SentinelDashboard

«Modular information dashboard for Raspberry Pi and Linux servers»

SentinelDashboard — это лёгкая модульная информационная панель, предназначенная для постоянного отображения важных данных на отдельном экране или планшете.

Проект разрабатывается с приоритетом стабильности, простоты настройки и расширяемой архитектуры.

---

Основные возможности

- 🖥 Мониторинг состояния системы
  
  - загрузка CPU
  - использование памяти
  - дисковое пространство
  - температура
  - время работы
  - имя хоста

- 🌤 Погодный модуль

- 📰 RSS-новости

- 🌐 Мониторинг сети

- ⚙️ Редактор представлений (Views Editor)

- 👁 Live Preview без перезагрузки страницы

- 🔗 Представления, которыми можно делиться через URL

---

Архитектура проекта

core/
    Базовая инфраструктура

modules/
    Независимые функциональные модули

routes/
    FastAPI endpoints

config/
    Конфигурация проекта

templates/
    HTML

static/
    JavaScript / CSS

tools/
    Инструменты разработки

---

Быстрый запуск

git clone git@github.com:Sonnik73/SentinelDashboard.git
cd SentinelDashboard

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app:app --host 0.0.0.0 --port 8000

После запуска открой:

http://<IP Raspberry Pi>:8000

Например:

http://192.168.88.107:8000

---

Представления (Views)

Каждое представление описывается отдельным JSON-файлом.

config/views/

Пример:

{
    "title": "Server",
    "widgets": [
        "system",
        "network"
    ]
}

Поддерживаемые представления:

/?view=default
/?view=home
/?view=server
/?view=wall

---

Разработка

Перед каждым коммитом рекомендуется выполнить:

python tools/check.py

После успешной проверки:

git add .
git commit -m "<message>"
git push

---

Road to Stability

Проект развивается небольшими инженерными спринтами.

Основные принципы:

- один законченный спринт — один коммит;
- небольшие безопасные изменения;
- сначала архитектура, затем код;
- минимум технического долга;
- обратная совместимость.

---

Статус проекта

Текущая стадия разработки:

Road to Stability

Следующая цель:

v1.0.0 — First Stable
