from google_sheets import GoogleSheetsManager

print("📋 LISTADO DE VOTANTES DISPONIBLES")
print("=" * 70)

sheets = GoogleSheetsManager()
worksheet = sheets.sheet.worksheet('votantes')
records = worksheet.get_all_records()

print(f"Total votantes: {len(records)}\n")

disponibles = []
for i, r in enumerate(records[:20], 1):  # Mostrar primeros 20
    cedula = r.get('cedula', '')
    nombre = r.get('nombre_completo', '')
    municipio = r.get('municipio', '')
    ya_voto = str(r.get('ya_voto', '')).lower().strip()
    
    estado = "✅ DISPONIBLE" if ya_voto == 'no' else "❌ YA VOTÓ"
    print(f"{i}. {cedula} - {nombre} ({municipio}) [{estado}]")
    
    if ya_voto == 'no':
        disponibles.append(cedula)

print("\n" + "=" * 70)
if disponibles:
    print(f"🎯 Cédulas disponibles para probar: {disponibles[:5]}")
else:
    print("⚠️  No hay votantes disponibles (todos ya votaron)")