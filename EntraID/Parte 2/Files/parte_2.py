import requests
import pandas as pd

# datos de autenticación entraID
TENANT_ID = "c66b2c8d-874e-4712-839e-1210dfed7344"
CLIENT_ID = "31d2b2f4-1b4c-489f-8e53-a769f433308b"
CLIENT_SECRET = "xtn8Q~8HYZHnoAcXQU~DvJRGCTELqzfCUwBe0aHM"
DOMAIN = "osirisgonzalezprofgmail.onmicrosoft.com"

# obtener token
def obtener_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, data=data).json()
    return response.get("access_token")

# Busqueda y creación de grupos
def gestionar_grupo(nombre_grupo, headers):
    # Buscar si el grupo existe
    url_busqueda = f"https://graph.microsoft.com/v1.0/groups?$filter=displayName eq '{nombre_grupo}'"
    grupos = requests.get(url_busqueda, headers=headers).json()
    
    if grupos.get('value'):
        return grupos['value'][0]['id'] # Si existe, devuelve el ID del grupo
    
    # Si no existe, lo creo
    print(f"Creando grupo: {nombre_grupo}")
    payload_grupo = {
        "displayName": nombre_grupo,
        "mailEnabled": False,
        "mailNickname": nombre_grupo.replace(" ", ""),
        "securityEnabled": True
    }
    nuevo_grupo = requests.post("https://graph.microsoft.com/v1.0/groups", headers=headers, json=payload_grupo).json()
    return nuevo_grupo.get('id')

# ALTA DE USERS
def ejecutar_update():
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # lee archivo csv
    df = pd.read_csv("data/empleados_parte2.csv")

    for index, fila in df.iterrows():
        nombre = fila['Nombre']
        apellido = fila['Apellido']
        puesto = fila['Puesto']
        depto = fila['Departamento']
        puesto_nuevo = fila['Puesto']
        upn = f"{nombre.lower()}.{apellido.lower()}@{DOMAIN}"

        # Check el usuario actualmente en la nube
        url_usuario = f"https://graph.microsoft.com/v1.0/users/{upn}"
        respuesta_azure = requests.get(url_usuario, headers=headers)

        if respuesta_azure.status_code == 200:
            datos_usuario = respuesta_azure.json()
            puesto_actual_azure = datos_usuario.get('jobTitle')

            # Check puesto del CSV vs puesto de Azure
            if puesto_actual_azure != puesto_nuevo:
                print(f"[!] Cambio de puesto para {nombre}: de {puesto_actual_azure} a {puesto_nuevo}")
                
                # 1. Actualizar el puesto en el perfil (PATCH)
                requests.patch(url_usuario, headers=headers, json={"jobTitle": puesto_nuevo})
                
                # 2. Gestionar el nuevo grupo y añadir al usuario
                id_grupo = gestionar_grupo(f"Rol-{puesto_nuevo}", headers)
                url_miembros = f"https://graph.microsoft.com/v1.0/groups/{id_grupo}/members/$ref"
                payload_miembro = {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{datos_usuario['id']}"}
                
                requests.post(url_miembros, headers=headers, json=payload_miembro)
                print(f"    -> Success: Usuario actualizado y movido de grupo.")
            else:
                print(f"[Success:] {nombre} ya tiene el puesto correcto.")
        else:
            print(f"[Error:] No se encontró a {nombre}. Ejecuta primero el script de Alta (Parte 1).")

if __name__ == "__main__":
    ejecutar_update()