#!/bin/sh
set -e

echo "🚀 Ejecutando script de inicialización de datos (superusuario)..."
python app/initial_data.py

echo "🌟 Arrancando servidor Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000