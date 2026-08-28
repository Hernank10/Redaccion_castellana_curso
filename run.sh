#!/bin/bash
# 🚀 Iniciar el Archivo de Vector

echo ""
echo "⌛ ARCHIVO DE VECTOR"
echo "=================="
echo ""

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "🔧 Activando entorno virtual..."
    source venv/bin/activate
fi

# Verificar base de datos
if [ ! -f "db.sqlite3" ]; then
    echo "⚠️ Base de datos no encontrada. Ejecutando setup.py..."
    python setup.py
fi

# Iniciar servidor
echo ""
echo "🌐 Iniciando servidor en http://localhost:8000"
echo "🔑 Admin: http://localhost:8000/admin"
echo "👤 Usuario: admin"
echo "🔑 Contraseña: admin123"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

python manage.py runserver
