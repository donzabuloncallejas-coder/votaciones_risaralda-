from google_sheets import GoogleSheetsManager

print("🔍 VERIFICANDO NOMBRES DE COLUMNAS")
print("=" * 70)

sheets = GoogleSheetsManager()

# Verificar hoja VOTANTES
print("\n📋 Hoja 'votantes':")
worksheet_votantes = sheets.sheet.worksheet('votantes')
print(f"   Encabezados: {worksheet_votantes.row_values(1)}")

# Leer primera fila de datos
primer_fila = worksheet_votantes.row_values(2)
encabezados = worksheet_votantes.row_values(1)
print(f"   Primer registro:")
for i, (header, value) in enumerate(zip(encabezados, primer_fila), 1):
    print(f"     {i}. '{header}' = '{value}'")

# Verificar hoja CANDIDATOS
print("\n📋 Hoja 'candidatos':")
worksheet_candidatos = sheets.sheet.worksheet('candidatos')
print(f"   Encabezados: {worksheet_candidatos.row_values(1)}")

primer_fila_cand = worksheet_candidatos.row_values(2)
encabezados_cand = worksheet_candidatos.row_values(1)
print(f"   Primer registro:")
for i, (header, value) in enumerate(zip(encabezados_cand, primer_fila_cand), 1):
    print(f"     {i}. '{header}' = '{value}'")

print("\n" + "=" * 70)
print("💡 Copia los nombres EXACTOS de las columnas 'cedula' y 'ya_voto'")