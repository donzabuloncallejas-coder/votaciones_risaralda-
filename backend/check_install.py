#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script de verificación de dependencias instaladas"""

import sys

DEPENDENCIAS_CRITICAS = [
    ('flask', 'Flask'),
    ('flask_cors', 'Flask-CORS'),
    ('gspread', 'GSpread'),
    ('google.auth', 'Google Auth'),
    ('google.oauth2', 'Google OAuth2'),
    ('googleapiclient', 'Google API Client'),
    ('dotenv', 'Python Dotenv'),
    ('requests', 'Requests'),
]

print("🔍 Verificando dependencias críticas...\n")
todas_ok = True

for modulo, nombre in DEPENDENCIAS_CRITICAS:
    try:
        __import__(modulo)
        print(f"✅ {nombre:25} - INSTALADO")
    except ImportError as e:
        print(f"❌ {nombre:25} - FALTA: {e}")
        todas_ok = False

print("\n" + "="*50)
if todas_ok:
    print("🎉 ¡Todas las dependencias están instaladas!")
    print("🚀 Puedes ejecutar: python app.py")
else:
    print("⚠️  Faltan dependencias. Ejecuta:")
    print("   pip install -r requirements.txt")
    sys.exit(1)