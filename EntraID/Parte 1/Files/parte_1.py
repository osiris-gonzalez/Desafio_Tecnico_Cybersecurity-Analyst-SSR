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
def ejecutar_alta():
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # lee archivo csv
    df = pd.read_csv("data/empleados.csv")

    for index, fila in df.iterrows():
        nombre = fila['Nombre']
        apellido = fila['Apellido']
        puesto = fila['Puesto']
        depto = fila['Departamento']
        upn = f"{nombre.lower()}.{apellido.lower()}@{DOMAIN}"

        print(f"Procesando a: {nombre} {apellido}")

        # Datos del user
        payload_usuario = {
            # para crear la cuenta directamente habilitada
            "accountEnabled": True,
            "displayName": f"{nombre} {apellido}",
            "mailNickname": nombre.lower(),
            "userPrincipalName": upn,
            "jobTitle": puesto,
            "department": depto,
            #para forzar el cambio de password en el primer login
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": "Password2026!"
            }
        }

        # Crear el user en Azure
        url_usuarios = "https://graph.microsoft.com/v1.0/users"
        respuesta = requests.post(url_usuarios, headers=headers, json=payload_usuario)

        if respuesta.status_code == 201:
            user_id = respuesta.json().get('id')
            
            # Gestionar el grupo Rol-Puesto
            nombre_rol = f"Rol-{puesto}"
            id_grupo = gestionar_grupo(nombre_rol, headers)
            
            # Añadir user al grupo
            url_miembro = f"https://graph.microsoft.com/v1.0/groups/{id_grupo}/members/$ref"
            payload_miembro = {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"}
            requests.post(url_miembro, headers=headers, json=payload_miembro)
            
            print(f"Success: {nombre} creado y asignado a {nombre_rol}")
        else:
            print(f"Error con {nombre}: {respuesta.text}")

if __name__ == "__main__":
    ejecutar_alta()