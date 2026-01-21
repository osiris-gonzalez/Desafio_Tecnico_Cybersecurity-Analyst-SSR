import datetime
from datetime import timezone, timedelta
import pandas as pd

# OBTENER LOS DATOS DE LA CONSOLA AWS 

# Esta función la usaría con AWS real - implementando BOTO3
"""
import boto3
def obtener_datos_reales_aws():
    iam = boto3.client('iam')
    usuarios_reales = []
    paginator = iam.get_paginator("list_users")
    
    for page in paginator.paginate():
        for user in page["Users"]:
            nombre = user["UserName"]
            # Listamos llaves y obtenemos su último uso
            keys = iam.list_access_keys(UserName=nombre)["AccessKeyMetadata"]
            for key in keys:
                uso_req = iam.get_access_key_last_used(AccessKeyId=key["AccessKeyId"])
                usuarios_reales.append({
                    'UserName': nombre,
                    'AccessKeyId': key["AccessKeyId"],
                    'CreateDate': key["CreateDate"],
                    'LastUsedDate': uso_req.get("AccessKeyLastUsed", {}).get("LastUsedDate")
                })
    return usuarios_reales
"""

# SIMULACIÓN DE DATOS PARA RESULTADO DE LA FUNCION SOLO PARA EL ASSESSMENT
def obtener_datos_simulados():
    ahora = datetime.datetime.now(timezone.utc)
    return [
        {
            'UserName': 'admin.osiris',
            'AccessKeyId': 'AKIA_OLD_123',
            'CreateDate': ahora - timedelta(days=120), # CUENTA DE +90 días
            'LastUsedDate': ahora - timedelta(days=5)
        },
        {
            'UserName': 'dev.laura',
            'AccessKeyId': 'AKIA_NEW_456',
            'CreateDate': ahora - timedelta(days=10),  # CUENTA OK
            'LastUsedDate': ahora - timedelta(days=1)
        },
        {
            'UserName': 'test.user',
            'AccessKeyId': 'AKIA_IDLE_789',
            'CreateDate': ahora - timedelta(days=45), 
            'LastUsedDate': ahora - timedelta(days=100) # CUENTA SIN USO POR +90 días
        }
    ]

# AUDITORIA E HIGIENE

def ejecutar_auditoria():
    print("====================================================")
    print("INICIANDO AUDITORÍA DE SEGURIDAD AWS")
    print("====================================================\n")
    
    ahora = datetime.datetime.now(timezone.utc)
    threshold = timedelta(days=90)
    
    # ACÁ SE USARÍA LA FUNCIÓN REAL
    usuarios = obtener_datos_simulados()
    reporte_final = []

    for user in usuarios:
        motivos = []
        antiguedad = ahora - user['CreateDate']
        
        # Regla 1: Antigüedad
        if antiguedad > threshold:
            motivos.append(f"Llave con {antiguedad.days} días de antigüedad")
            
        # Regla 2: Uso
        if user['LastUsedDate']:
            dias_sin_uso = (ahora - user['LastUsedDate']).days
            if dias_sin_uso > 90:
                motivos.append(f"Sin uso hace {dias_sin_uso} días")
        else:
            motivos.append("Llave nunca utilizada")

        # Determinar estado
        estado = "RIESGO" if motivos else "OK"
        
        # Guardar para Excel
        reporte_final.append({
            "Usuario": user['UserName'],
            "AccessKey": user['AccessKeyId'],
            "Antigüedad (Días)": antiguedad.days,
            "Estado": estado,
            "Hallazgos": " | ".join(motivos) if motivos else "Llave ok"
        })

        # Mostrar en pantalla
        if estado == "RIESGO":
            print(f"[WARN] {user['UserName']} requiere atención:")
            for m in motivos: print(f"  - {m}")
        else:
            print(f"[OK] {user['UserName']} cumple políticas.")

    # --- 3. EXPORTAR A EXCEL ---
    df = pd.DataFrame(reporte_final)
    df.to_excel("reporte_auditoria_aws.xlsx", index=False)
    print(f"\n====================================================")
    print("REPORTE EXCEL GENERADO: reporte_auditoria_aws.xlsx")
    print("====================================================")

if __name__ == "__main__":
    ejecutar_auditoria()