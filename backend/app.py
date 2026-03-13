from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google_sheets import GoogleSheetsManager
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Inicializar Google Sheets Manager
try:
    sheets_manager = GoogleSheetsManager()
except Exception as e:
    print(f"⚠️  Advertencia: {e}")
    sheets_manager = None

# ==================== RUTAS DEL FRONTEND ====================

@app.route('/')
def index():
    """Sirve la página principal"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/votacion.html')
def votacion():
    """Sirve la página de votación"""
    return send_from_directory(app.static_folder, 'votacion.html')

# ==================== RUTAS DE LA API ====================

@app.route('/api/validar-votante', methods=['POST'])
def validar_votante():
    """
    Valida si un votante existe y puede votar
    Request: {"cedula": "123456789"}
    """
    if sheets_manager is None:
        return jsonify({
            'success': False,
            'error': 'Error de conexión con la base de datos'
        }), 500
    
    data = request.get_json()
    cedula = data.get('cedula')
    
    if not cedula:
        return jsonify({
            'success': False,
            'error': 'Cédula requerida'
        }), 400
    
    print(f"🔍 Validando votante: {cedula}")
    
    # Buscar votante
    votante = sheets_manager.buscar_votante_por_cedula(cedula)
    
    if not votante['encontrado']:
        print(f"❌ Votante {cedula} NO encontrado")
        return jsonify({
            'success': False,
            'error': 'Votante no registrado en el sistema'
        }), 404
    
    # Verificar si ya votó
    if str(votante['datos'].get('ya_voto', '')).lower().strip() == 'si':
        print(f"⚠️  Votante {cedula} YA VOTÓ")
        return jsonify({
            'success': False,
            'ya_voto': True,
            'error': 'Usted ya ha ejercido su derecho al voto. No puede votar nuevamente.'
        }), 403
    
    # Votante válido y puede votar
    print(f"✅ Votante {cedula} validado correctamente")
    return jsonify({
        'success': True,
        'mensaje': 'Votante validado correctamente',
        'votante': {
            'cedula': votante['datos'].get('cedula'),
            'nombre': votante['datos'].get('nombre_completo'),
            'municipio': votante['datos'].get('municipio')
        }
    }), 200

@app.route('/api/municipios', methods=['GET'])
def obtener_municipios():
    """Obtiene la lista de municipios disponibles"""
    if sheets_manager is None:
        return jsonify({
            'success': False,
            'error': 'Error de conexión con la base de datos'
        }), 500
    
    municipios = sheets_manager.obtener_municipios_unicos()
    
    if isinstance(municipios, dict) and 'error' in municipios:
        return jsonify({
            'success': False,
            'error': municipios['error']
        }), 500
    
    return jsonify({
        'success': True,
        'municipios': municipios
    }), 200

@app.route('/api/candidatos/<municipio>', methods=['GET'])
def obtener_candidatos(municipio):
    """Obtiene los candidatos de un municipio específico"""
    if sheets_manager is None:
        return jsonify({
            'success': False,
            'error': 'Error de conexión con la base de datos'
        }), 500
    
    candidatos = sheets_manager.obtener_candidatos_por_municipio(municipio)
    
    if isinstance(candidatos, dict) and 'error' in candidatos:
        return jsonify({
            'success': False,
            'error': candidatos['error']
        }), 500
    
    return jsonify({
        'success': True,
        'municipio': municipio,
        'candidatos': candidatos
    }), 200

@app.route('/api/votar', methods=['POST'])
def votar():
    """
    Registra un voto
    Request: {"cedula": "123456789", "candidato_id": "5"}
    """
    if sheets_manager is None:
        return jsonify({
            'success': False,
            'error': 'Error de conexión con la base de datos'
        }), 500
    
    data = request.get_json()
    cedula = data.get('cedula')
    candidato_id = data.get('candidato_id')
    
    if not cedula or not candidato_id:
        return jsonify({
            'success': False,
            'error': 'Cédula y candidato son requeridos'
        }), 400
    
    print(f"🗳️  Registrando voto - Cédula: {cedula}, Candidato: {candidato_id}")
    
    resultado = sheets_manager.registrar_voto(cedula, candidato_id)
    
    if resultado['success']:
        return jsonify(resultado), 200
    else:
        status_code = 400 if 'ya ha ejercido' in resultado.get('error', '') else 500
        return jsonify(resultado), status_code

@app.route('/api/resultado-votacion', methods=['GET'])
def resultado_votacion():
    """Obtiene los resultados completos de la votación"""
    if sheets_manager is None:
        return jsonify({
            'success': False,
            'error': 'Error de conexión con la base de datos'
        }), 500
    
    candidatos = sheets_manager.obtener_todos_candidatos()
    
    if isinstance(candidatos, dict) and 'error' in candidatos:
        return jsonify({
            'success': False,
            'error': candidatos['error']
        }), 500
    
    # Ordenar por número de votos (descendente)
    candidatos_ordenados = sorted(
        candidatos,
        key=lambda x: int(x.get('votos', 0)) if x.get('votos') else 0,
        reverse=True
    )
    
    return jsonify({
        'success': True,
        'resultados': candidatos_ordenados
    }), 200

# ==================== INICIAR SERVIDOR ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print("=" * 70)
    print("🗳️  SISTEMA DE VOTACIÓN RISARALDA 2026")
    print("=" * 70)
    print(f"📡 Servidor: http://localhost:{port}")
    print(f"🔧 Modo debug: {debug}")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=port, debug=debug)