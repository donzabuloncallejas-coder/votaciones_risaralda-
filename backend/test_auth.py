import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 DIAGNÓSTICO DE AUTENTICACIÓN")
print("=" * 60)

# 1. Verificar variables de entorno
print("\n1️⃣ Variables de entorno:")
print(f"   GOOGLE_SHEETS_ID: {os.getenv('GOOGLE_SHEETS_ID')}")
print(f"   GOOGLE_CLIENT_EMAIL: {os.getenv('GOOGLE_CLIENT_EMAIL')}")
private_key = os.getenv('GOOGLE_PRIVATE_KEY')
print(f"   GOOGLE_PRIVATE_KEY: {len(private_key) if private_key else 'NO DEFINIDA'} caracteres")
print(f"   Primeros 50 chars: {private_key[:50] if private_key else 'N/A'}...")

# 2. Verificar formato de private key
if private_key:
    if '\\n' in private_key:
        print("   ⚠️  Private key tiene \\n escapados (esto es normal)")
    if '-----BEGIN PRIVATE KEY-----' in private_key:
        print("   ✅ Private key tiene formato válido")
    else:
        print("   ❌ Private key NO tiene formato válido")

# 3. Intentar autenticación mínima
print("\n2️⃣ Probando autenticación mínima...")
try:
    from google.oauth2.service_account import Credentials
    
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = Credentials.from_service_account_info({
        'type': 'service_account',
        'client_email': os.getenv('GOOGLE_CLIENT_EMAIL'),
        'private_key': private_key.replace('\\n', '\n') if private_key else None,
        'token_uri': 'https://oauth2.googleapis.com/token',
        'scopes': scopes
    })
    
    print("   ✅ Credenciales cargadas correctamente")
    
    # Intentar obtener token (esto falla si los scopes son inválidos)
    print("   🔐 Intentando obtener token de acceso...")
    import google.auth.transport.requests
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    print(f"   ✅ Token obtenido: {creds.token[:30]}...")
    
except Exception as e:
    print(f"   ❌ Error en autenticación: {type(e).__name__}")
    print(f"   📄 Detalle: {e}")

print("\n" + "=" * 60)
print("💡 Si falla en 'Token obtenido', revisa:")
print("   1. Google Drive API habilitada en Cloud Console")
print("   2. Sheet compartido con la service account")
print("   3. Credenciales regeneradas (la key puede estar revocada)")