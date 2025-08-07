#!/bin/bash
set -e  # Interrompe se houver erro

echo "🚀 Iniciando o dashboard..."

# Garante que estamos no diretório do projeto
cd /opt/render/project/src || cd $HOME/project/src

# Instala as dependências (caso o build tenha falhado em aplicar)
pip install -r requirements.txt

# Inicia o servidor
echo "✅ Dependências instaladas. Iniciando Gunicorn..."
exec gunicorn dashboard_expansao:server --bind 0.0.0.0:$PORT --workers 1 --timeout 120
