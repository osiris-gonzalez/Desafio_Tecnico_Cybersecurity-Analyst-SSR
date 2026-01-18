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

# BAJA DE USERS
def ejecutar_bajas():
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # lee archivo csv. Crea lista de users vacia y va agregando los que encuentra
    df = pd.read_csv("Files/empleados_parte3.csv")
    users_en_csv = []
    for _, fila in df.iterrows():
        user_csv = f"{fila['Nombre'].lower()}.{fila['Apellido'].lower()}@{DOMAIN}"
        users_en_csv.append(user_csv)

    # Ver todos los users actualmente en EntraID
    url_azure = "https://graph.microsoft.com/v1.0/users"
    todos_los_users = requests.get(url_azure, headers=headers).json().get('value', [])

    for user in todos_los_users:
        user_azure = user.get('userPrincipalName')
        user_id = user.get('id')

        # Comparación: Si está en Azure pero NO en el CSV, es una BAJA
        if user_azure in users_en_csv:
            continue # Está todo ok, el usuario sigue en la empresa
        
        # Excluir cuentas admin
        if "admin" in user_azure or user_azure.startswith("osiris"):
            continue

        print(f"BAJA Detectada de: {user_azure}")

        # 1 ACCION: Deshabilitar cuenta
        url_modificar = f"https://graph.microsoft.com/v1.0/users/{user_id}"
        payload_baja = {"accountEnabled": False}
        requests.patch(url_modificar, headers=headers, json=payload_baja)
        print(f"Success - Cuenta deshabilitada con éxito.")

        # 2 ACCION: Revocar sesiones (Invalidar Refresh Tokens)
        url_revocar = f"https://graph.microsoft.com/v1.0/users/{user_id}/revokeSignInSessions"
        requests.post(url_revocar, headers=headers)
        print(f"Success - Sesiones revocadas. El usuario ya no tiene acceso.")

if __name__ == "__main__":
    ejecutar_bajas()