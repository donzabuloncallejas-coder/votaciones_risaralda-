
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()

class GoogleSheetsManager:
    def __init__(self):
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
        # Intentar cargar desde credentials.json primero
        json_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        
        try:
            if os.path.exists(json_path):
                print("📄 Cargando credenciales desde credentials.json...")
                with open(json_path, 'r', encoding='utf-8') as f:
                    creds_info = json.load(f)
                
                # Limpiar URLs con espacios en blanco
                for key in ['auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url']:
                    if key in creds_info and creds_info[key]:
                        creds_info[key] = creds_info[key].strip()
                
                self.creds = Credentials.from_service_account_info(
                    creds_info,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
                print("✅ Credenciales cargadas desde JSON")
            else:
                print("📄 Cargando credenciales desde .env...")
                private_key = os.getenv('GOOGLE_PRIVATE_KEY', '')
                if private_key:
                    private_key = private_key.replace('\\n', '\n')
                
                self.creds = Credentials.from_service_account_info({
                    'type': 'service_account',
                    'client_email': os.getenv('GOOGLE_CLIENT_EMAIL'),
                    'private_key': private_key,
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'scopes': [
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                })
                print("✅ Credenciales cargadas desde .env")
            
            print(f"📧 Service Account: {os.getenv('GOOGLE_CLIENT_EMAIL', 'N/A')}")
            print(f"📄 Sheet ID: {self.spreadsheet_id}")
            
            # Autorizar cliente
            print("🔐 Autorizando cliente...")
            self.client = gspread.authorize(self.creds)
            print("✅ Cliente autorizado correctamente")
            
            # Listar sheets accesibles (debug)
            try:
                files = self.client.list_spreadsheet_files()
                print(f"📋 Sheets accesibles: {len(files)} encontrados")
                
                # Buscar el sheet específico
                sheet_found = False
                for f in files:
                    if f['id'] == self.spreadsheet_id:
                        print(f"✅ Sheet encontrado: {f['name']}")
                        sheet_found = True
                        break
                
                if not sheet_found:
                    print(f"⚠️  Sheet ID {self.spreadsheet_id} no encontrado en la lista")
                    print("   Sheets disponibles:")
                    for f in files[:5]:
                        print(f"     - {f['name']} ({f['id']})")
            except Exception as e:
                print(f"⚠️  No se pudieron listar sheets: {e}")
            
            # Abrir el sheet específico
            print(f"🔓 Abriendo sheet: {self.spreadsheet_id}...")
            self.sheet = self.client.open_by_key(self.spreadsheet_id)
            print("✅ Google Sheet abierto exitosamente")
            
            # Verificar hojas
            worksheets = self.sheet.worksheets()
            worksheet_names = [w.title for w in worksheets]
            print(f"📑 Hojas encontradas: {worksheet_names}")
            
            if 'votantes' not in worksheet_names:
                print("⚠️  ADVERTENCIA: No se encontró la hoja 'votantes'")
            if 'candidatos' not in worksheet_names:
                print("⚠️  ADVERTENCIA: No se encontró la hoja 'candidatos'")
            
            print("=" * 60)
            print("✅ CONEXIÓN CON GOOGLE SHEETS EXITOSA")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO AL CONECTAR: {type(e).__name__}")
            print(f"📄 Detalle: {e}")
            print("\n🔍 POSIBLES CAUSAS:")
            print("   1. El Google Sheet NO está compartido con la service account")
            print("   2. La Google Drive API NO está habilitada")
            print("   3. Las credenciales son inválidas o están revocadas")
            print("   4. El Sheet ID es incorrecto")
            print("\n🔧 SOLUCIONES:")
            print(f"   - Comparte el sheet con: {os.getenv('GOOGLE_CLIENT_EMAIL', 'N/A')}")
            print("   - Habilita Google Drive API en: https://console.cloud.google.com/apis/library/drive.googleapis.com")
            print("   - Verifica que el Sheet ID sea correcto")
            print("   - Regenera las credenciales si es necesario")
            raise
    
    def buscar_votante_por_cedula(self, cedula):
        """Busca un votante por su número de cédula"""
        try:
            worksheet = self.sheet.worksheet('votantes')
            all_records = worksheet.get_all_records()
            
            for i, record in enumerate(all_records):
                # Probar ambos nombres de columna (con y sin espacio)
                valor_cedula = str(record.get('cedula', record.get('cedula ', ''))).strip()
                
                if valor_cedula == str(cedula).strip():
                    return {
                        'encontrado': True,
                        'datos': record,
                        'fila': i + 2  # +2 porque fila 1 es header
                    }
            
            return {'encontrado': False}
        except Exception as e:
            print(f"❌ Error buscando votante {cedula}: {e}")
            return {'error': str(e)}
    
    def verificar_ya_voto(self, cedula):
        """Verifica si el votante ya ejerció su derecho al voto"""
        votante = self.buscar_votante_por_cedula(cedula)
        
        if not votante['encontrado']:
            return {'error': 'Votante no encontrado'}
        
        # Probar ambos nombres de columna
        ya_voto = str(votante['datos'].get('ya_voto', votante['datos'].get('ya_voto ', ''))).lower().strip()
        
        return {
            'ya_voto': ya_voto == 'si',
            'mensaje': 'El votante ya ha ejercido su derecho al voto' if ya_voto == 'si' else 'Votante habilitado para votar'
        }
    
    def obtener_municipios_unicos(self):
        """Obtiene la lista de municipios únicos de los candidatos"""
        try:
            worksheet = self.sheet.worksheet('candidatos')
            all_records = worksheet.get_all_records()
            
            municipios = set()
            for record in all_records:
                municipio = str(record.get('municipio', '')).strip()
                if municipio:
                    municipios.add(municipio)
            
            return sorted(list(municipios))
        except Exception as e:
            print(f"❌ Error obteniendo municipios: {e}")
            return {'error': str(e)}
    
    def obtener_candidatos_por_municipio(self, municipio):
        """Obtiene todos los candidatos de un municipio específico"""
        try:
            worksheet = self.sheet.worksheet('candidatos')
            all_records = worksheet.get_all_records()
            
            candidatos = []
            for i, record in enumerate(all_records):
                if str(record.get('municipio', '')).strip().lower() == municipio.lower():
                    candidatos.append({
                        'id': str(record.get('id', '')),
                        'nombre': record.get('nombre_completo'),
                        'tipo_discapacidad': record.get('tipo_discapacidad'),
                        'municipio': record.get('municipio'),
                        'votos': int(record.get('votos', 0)) if record.get('votos') else 0,
                        'fila': i + 2
                    })
            
            print(f"📋 Candidatos en {municipio}: {len(candidatos)} encontrados")
            return candidatos
        except Exception as e:
            print(f"❌ Error obteniendo candidatos de {municipio}: {e}")
            return {'error': str(e)}
    
    def registrar_voto(self, cedula, candidato_id):
        """Registra el voto y actualiza el estado del votante"""
        try:
            # 1. Buscar el votante
            votante = self.buscar_votante_por_cedula(cedula)
            if not votante['encontrado']:
                return {'success': False, 'error': 'Votante no encontrado'}
            
            # 2. Verificar si ya votó
            ya_voto_valor = str(votante['datos'].get('ya_voto', votante['datos'].get('ya_voto ', ''))).lower().strip()
            if ya_voto_valor == 'si':
                return {'success': False, 'error': 'Este votante ya ha ejercido su derecho al voto'}
            
            # 3. Buscar el candidato
            worksheet_candidatos = self.sheet.worksheet('candidatos')
            all_candidatos = worksheet_candidatos.get_all_records()
            
            candidato_fila = None
            votos_actuales = 0
            candidato_nombre = None
            
            for i, cand in enumerate(all_candidatos):
                if str(cand.get('id', '')).strip() == str(candidato_id).strip():
                    candidato_fila = i + 2
                    votos_actuales = int(cand.get('votos', 0)) if cand.get('votos') else 0
                    candidato_nombre = cand.get('nombre_completo')
                    break
            
            if candidato_fila is None:
                return {'success': False, 'error': 'Candidato no encontrado'}
            
            # 4. Actualizar votos del candidato (columna E = 5)
            print(f"📊 Actualizando votos: {candidato_nombre} ({votos_actuales} → {votos_actuales + 1})")
            worksheet_candidatos.update_cell(candidato_fila, 5, votos_actuales + 1)
            
            # 5. Actualizar ya_voto del votante (columna H = 8)
            worksheet_votantes = self.sheet.worksheet('votantes')
            worksheet_votantes.update_cell(votante['fila'], 8, 'si')
            
            # 6. Registrar fecha y hora (columna I = 9)
            fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            worksheet_votantes.update_cell(votante['fila'], 9, fecha_hora)
            
            # Obtener nombre del votante
            nombre_votante = votante['datos'].get('nombre_completo', 'Desconocido')
            print(f"✅ Voto registrado: {nombre_votante} → {candidato_nombre}")
            
            return {
                'success': True,
                'mensaje': 'Voto registrado exitosamente',
                'votante': nombre_votante,
                'candidato_id': candidato_id,
                'candidato_nombre': candidato_nombre
            }
            
        except Exception as e:
            print(f"❌ Error registrando voto: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': f'Error al registrar voto: {str(e)}'}
    
    def obtener_todos_candidatos(self):
        """Obtiene todos los candidatos con sus votos"""
        try:
            worksheet = self.sheet.worksheet('candidatos')
            return worksheet.get_all_records()
        except Exception as e:
            print(f"❌ Error obteniendo todos los candidatos: {e}")
            return {'error': str(e)}