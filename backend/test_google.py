from google_sheets import GoogleSheetsManager

try:
    print("🔍 Intentando conectar con Google Sheets...")
    sheets = GoogleSheetsManager()
    print("✅ Conexión exitosa!")
    
    # Probar búsqueda
    print("\n📋 Probando búsqueda de votante...")
    resultado = sheets.buscar_votante_por_cedula("107084321")
    print(f"Resultado: {resultado}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    