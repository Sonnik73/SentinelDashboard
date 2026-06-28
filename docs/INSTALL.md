Installation

Клонирование

git clone git@github.com:Sonnik73/SentinelDashboard.git
cd SentinelDashboard

Подготовка окружения

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Запуск

uvicorn app:app --host 0.0.0.0 --port 8000

После запуска открой:

http://IP_УСТРОЙСТВА:8000
