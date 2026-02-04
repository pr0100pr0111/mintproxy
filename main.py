from flask import Flask, render_template_string, request, redirect, session
from functools import wraps
import random
import json
import os
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


# ============================================================================
# CONFIG
# ============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32).hex())

BANK_CARD = os.environ.get('BANK_CARD', "5599 0021 1503 7915")
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', "admin")
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get('ADMIN_PASSWORD', "admin"))


# ============================================================================
# DATABASE
# ============================================================================

def init_db():
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            region_id TEXT NOT NULL,
            country_id TEXT NOT NULL,
            amount REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'pending',
            proxy_data TEXT,
            timestamp DATETIME NOT NULL
        )
    ''')

    c.execute("PRAGMA table_info(payments)")
    columns = [column[1] for column in c.fetchall()]

    if 'quantity' not in columns:
        try:
            c.execute("ALTER TABLE payments ADD COLUMN quantity INTEGER NOT NULL DEFAULT 1")
        except sqlite3.Error:
            pass

    try:
        c.execute('CREATE INDEX IF NOT EXISTS idx_payments_status ON payments (status)')
    except sqlite3.Error:
        pass

    conn.commit()
    conn.close()


# ============================================================================
# DECORATORS & HELPERS
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function


def _validate_region_country(region_id, country_id):
    return region_id in PROXIES and country_id in PROXIES[region_id]["countries"]


def _get_country_name(region_id, country_id):
    if _validate_region_country(region_id, country_id):
        return PROXIES[region_id]["countries"][country_id]["name"]
    return "Неизвестная страна"


def _generate_proxy_data(quantity):
    return [
        {
            "ip": ".".join(str(random.randint(0, 255)) for _ in range(4)),
            "port": random.randint(1000, 9999),
            "login": f"user{random.randint(1000, 9999)}",
            "password": f"pass{random.randint(10000, 99999)}"
        }
        for _ in range(quantity)
    ]


# ============================================================================
# PROXIES DATA
# ============================================================================

PROXIES = {
    "europe": {
        "name": "Европа",
        "countries": {
            "austria": {"name": "Австрия", "price": 249, "color": "#4AA896"},
            "bosnia": {"name": "Босния и Герцеговина", "price": 249, "color": "#4AA896"},
            "uk": {"name": "Великобритания", "price": 299, "color": "#4AA896"},
            "hungary": {"name": "Венгрия", "price": 249, "color": "#4AA896"},
            "germany": {"name": "Германия", "price": 299, "color": "#4AA896"},
            "greece": {"name": "Греция", "price": 199, "color": "#4AA896"},
            "denmark": {"name": "Дания", "price": 249, "color": "#4AA896"},
            "ireland": {"name": "Ирландия", "price": 299, "color": "#4AA896"},
            "iceland": {"name": "Исландия", "price": 249, "color": "#4AA896"},
            "spain": {"name": "Испания", "price": 299, "color": "#4AA896"},
            "italy": {"name": "Италия", "price": 299, "color": "#4AA896"},
            "latvia": {"name": "Латвия", "price": 299, "color": "#4AA896"},
            "netherlands": {"name": "Нидерланды", "price": 149, "color": "#4AA896"},
            "norway": {"name": "Норвегия", "price": 249, "color": "#4AA896"},
            "poland": {"name": "Польша", "price": 149, "color": "#4AA896"},
            "portugal": {"name": "Португалия", "price": 299, "color": "#4AA896"},
            "russia": {"name": "Россия", "price": 99, "color": "#4AA896"},
            "serbia": {"name": "Сербия", "price": 199, "color": "#4AA896"},
            "slovakia": {"name": "Словакия", "price": 199, "color": "#4AA896"},
            "slovenia": {"name": "Словения", "price": 199, "color": "#4AA896"},
            "finland": {"name": "Финляндия", "price": 199, "color": "#4AA896"},
            "france": {"name": "Франция", "price": 299, "color": "#4AA896"},
            "croatia": {"name": "Хорватия", "price": 249, "color": "#4AA896"},
            "czech": {"name": "Чехия", "price": 249, "color": "#4AA896"},
            "switzerland": {"name": "Швейцария", "price": 249, "color": "#4AA896"},
            "sweden": {"name": "Швеция", "price": 249, "color": "#4AA896"},
            "estonia": {"name": "Эстония", "price": 199, "color": "#4AA896"},
        }
    },
    "asia": {
        "name": "Азия",
        "countries": {
            "azerbaijan": {"name": "Азербайджан", "price": 149, "color": "#4AA896"},
            "vietnam": {"name": "Вьетнам", "price": 149, "color": "#4AA896"},
            "hongkong": {"name": "Гонконг", "price": 199, "color": "#4AA896"},
            "georgia": {"name": "Грузия", "price": 199, "color": "#4AA896"},
            "israel": {"name": "Израиль", "price": 249, "color": "#4AA896"},
            "india": {"name": "Индия", "price": 249, "color": "#4AA896"},
            "indonesia": {"name": "Индонезия", "price": 199, "color": "#4AA896"},
            "kazakhstan": {"name": "Казахстан", "price": 149, "color": "#4AA896"},
            "qatar": {"name": "Катар", "price": 199, "color": "#4AA896"},
            "china": {"name": "Китай", "price": 149, "color": "#4AA896"},
            "kuwait": {"name": "Кувейт", "price": 299, "color": "#4AA896"},
            "malaysia": {"name": "Малайзия", "price": 249, "color": "#4AA896"},
            "uae": {"name": "ОАЭ", "price": 249, "color": "#4AA896"},
            "korea": {"name": "Республика Корея", "price": 299, "color": "#4AA896"},
            "thailand": {"name": "Таиланд", "price": 299, "color": "#4AA896"},
            "turkey": {"name": "Турция", "price": 149, "color": "#4AA896"},
            "philippines": {"name": "Филиппины", "price": 299, "color": "#4AA896"},
            "japan": {"name": "Япония", "price": 299, "color": "#4AA896"},
        }
    },
    "america": {
        "name": "Америка",
        "countries": {
            "argentina": {"name": "Аргентина", "price": 299, "color": "#4AA896"},
            "brazil": {"name": "Бразилия", "price": 199, "color": "#4AA896"},
            "canada": {"name": "Канада", "price": 149, "color": "#4AA896"},
            "cuba": {"name": "Куба", "price": 249, "color": "#4AA896"},
            "mexico": {"name": "Мексика", "price": 199, "color": "#4AA896"},
            "usa": {"name": "США", "price": 149, "color": "#4AA896"},
        }
    },
    "africa": {
        "name": "Африка",
        "countries": {
            "egypt": {"name": "Египет", "price": 149, "color": "#4AA896"},
            "morocco": {"name": "Марокко", "price": 199, "color": "#4AA896"},
            "southafrica": {"name": "ЮАР", "price": 249, "color": "#4AA896"},
        }
    },
    "oceania": {
        "name": "Океания",
        "countries": {
            "australia": {"name": "Австралия", "price": 249, "color": "#4AA896"},
            "newzealand": {"name": "Новая Зеландия", "price": 199, "color": "#4AA896"},
            "samoa": {"name": "Самоа", "price": 199, "color": "#4AA896"},
        }
    }
}

BASE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | MintProxy</title>
    <style>
        @keyframes slideUp {{
            0% {{ transform: translateY(50px); opacity: 0; }}
            100% {{ transform: translateY(0); opacity: 1; }}
        }}

        :root {{
            --mint-dark: #4AA896;
            --mint-medium: #6DC0B8;
            --mint-light: #A7D7C5;
            --mint-extra-light: #C4E3D1;
            --mint-super-light: #E8F4F0;
            --text-dark: #2E3E4C;
            --text-light: #FFFFFF;
            --gray: #F5F7FA;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        body {{
            color: var(--text-dark);
            line-height: 1.6;
            background-color: var(--gray);
        }}

        .navbar {{
            background-color: var(--text-light);
            box-shadow: 0 2px 10px rgba(46, 62, 76, 0.1);
            padding: 15px 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }}

        .nav-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        .logo {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--mint-dark);
            text-decoration: none;
        }}

        .nav-links {{
            display: flex;
            gap: 25px;
        }}

        .nav-link {{
            color: var(--text-dark);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
            position: relative;
        }}

        .nav-link:hover {{
            color: var(--mint-dark);
        }}

        .contacts-dropdown {{
            position: relative;
            display: inline-block;
        }}

        .contacts-dropdown-content {{
            display: none;
            position: absolute;
            background-color: var(--text-light);
            min-width: 200px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            border-radius: 8px;
            padding: 15px;
            z-index: 1;
            right: 0;
            top: 100%;
            opacity: 0;
            transition: opacity 0.3s;
        }}

        .contacts-dropdown:hover .contacts-dropdown-content {{
            display: block;
            opacity: 1;
        }}

        .contacts-dropdown-content p {{
            margin: 8px 0;
            color: var(--text-dark);
        }}

        .contacts-dropdown > .nav-link {{
            background-color: transparent !important;
            padding: 0 !important;
        }}

        .btn {{
            display: inline-block;
            background-color: var(--mint-dark);
            color: var(--text-light);
            padding: 12px 28px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            box-shadow: 0 4px 6px rgba(74, 168, 150, 0.2);
        }}

        .btn:hover {{
            background-color: var(--mint-medium);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(74, 168, 150, 0.25);
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        footer {{
            background-color: var(--text-dark);
            color: var(--text-light);
            padding: 40px 0;
            text-align: center;
            margin-top: 80px;
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="/" class="logo">MintProxy</a>
            <div class="nav-links">
                <a href="/proxies" class="nav-link">Прокси</a>
                <div class="contacts-dropdown">
                    <a href="#" class="nav-link" onclick="return false;">Контакты</a>
                    <div class="contacts-dropdown-content">
                        <p><strong>Email:</strong> mintproxy@tutamail.com</p>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    {content}

    <footer id="contacts">
        <div class="container">
            <p>&copy; {year} MintProxy. Все права защищены.</p>
        </div>
    </footer>
</body>
</html>
"""

LANDING_HTML = """
<section style="background: linear-gradient(to bottom, var(--mint-super-light) 0%, var(--gray) 100%); padding: 120px 0 180px; text-align: center; overflow: hidden;">
    <div class="container" style="animation: slideUp 1s ease-out forwards;">
        <h1 style="font-size: 3rem; margin-bottom: 20px; color: var(--text-dark); opacity: 0; animation: slideUp 0.8s ease-out 0.2s forwards;">Премиум резидентские прокси</h1>
        <p style="font-size: 1.3rem; margin-bottom: 40px; color: var(--text-dark); opacity: 0; animation: slideUp 0.8s ease-out 0.4s forwards;">Высокоскоростные анонимные прокси с гарантией работоспособности</p>
        <a href="/proxies" class="btn" style="opacity: 0; animation: slideUp 0.8s ease-out 0.6s forwards;">Получить прокси</a>
    </div>
</section>

<section id="features" style="padding: 80px 0; background-color: var(--text-light);">
    <div class="container">
        <h2 style="text-align: center; font-size: 2.2rem; margin-bottom: 60px; color: var(--text-dark);">Наши преимущества</h2>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px;">
            <div style="background: var(--gray); padding: 30px; border-radius: 12px; text-align: center; transition: transform 0.3s;">
                <div style="background-color: var(--mint-light); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <span style="font-size: 1.8rem;">🌐</span>
                </div>
                <h3 style="font-size: 1.5rem; margin-bottom: 15px; color: var(--text-dark);">Глобальное покрытие</h3>
                <p style="color: var(--text-dark);">Большой выбор прокси-серверов со всего мира</p>
            </div>

            <div style="background: var(--gray); padding: 30px; border-radius: 12px; text-align: center; transition: transform 0.3s;">
                <div style="background-color: var(--mint-light); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <span style="font-size: 1.8rem;">⚡</span>
                </div>
                <h3 style="font-size: 1.5rem; margin-bottom: 15px; color: var(--text-dark);">Высокая скорость</h3>
                <p style="color: var(--text-dark);">Средняя задержка менее 50 мс, пропускная способность 1 Гбит/с</p>
            </div>

            <div style="background: var(--gray); padding: 30px; border-radius: 12px; text-align: center; transition: transform 0.3s;">
                <div style="background-color: var(--mint-light); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <span style="font-size: 1.8rem;">🔒</span>
                </div>
                <h3 style="font-size: 1.5rem; margin-bottom: 15px; color: var(--text-dark);">Анонимность</h3>
                <p style="color: var(--text-dark);">Полная защита ваших данных и реального IP-адреса</p>
            </div>
        </div>
    </div>
</section>
"""

PROXIES_HTML = """
<section style="padding: 40px 0;">
    <div class="container">
        <h2 style="text-align: center; font-size: 2.2rem; margin-bottom: 20px; color: var(--text-dark);">Выберите прокси по региону</h2>
        
        <div style="display: flex; justify-content: center; gap: 15px; margin-bottom: 30px; flex-wrap: wrap;">
            {% for region_id, region in proxies.items() %}
            <a href="#{{ region_id }}" 
               onclick="smoothScroll(event, '{{ region_id }}')"
               style="padding: 10px 20px; 
                      background-color: var(--mint-light); 
                      color: var(--text-dark); 
                      border-radius: 50px; 
                      text-decoration: none; 
                      font-weight: 600;
                      transition: all 0.3s;
                      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                      cursor: pointer;">
                {{ region.name }}
            </a>
            {% endfor %}
        </div>

        {% for region_id, region in proxies.items() %}
        <div style="margin-bottom: 50px;" id="{{ region_id }}">
            <h3 style="font-size: 1.5rem; margin-bottom: 20px; color: var(--mint-dark); border-bottom: 2px solid var(--mint-light); padding-bottom: 10px;">
                {{ region.name }}
            </h3>

            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px;">
                {% for country_id, proxy in region.countries.items() %}
                <div style="background: var(--text-light); border-radius: 12px; overflow: hidden; box-shadow: 0 5px 15px rgba(46, 62, 76, 0.1); transition: transform 0.3s;">
                    <div style="background-color: {{ proxy.color }}; padding: 25px; text-align: center; color: var(--text-light);">
                        <h3 style="font-size: 1.5rem; margin-bottom: 5px;">{{ proxy.name }}</h3>
                        <p style="font-size: 1.2rem;">{{ proxy.price }}₽ / месяц</p>
                    </div>
                    <div style="padding: 25px; text-align: center;">
                        <a href="/proxy/{{ region_id }}/{{ country_id }}" class="btn" style="width: 100%; background-color: {{ proxy.color }};">Выбрать</a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
</section>

<script>
function smoothScroll(event, targetId) {
    event.preventDefault();
    const targetElement = document.getElementById(targetId);
    if (targetElement) {
        window.scrollTo({
            top: targetElement.offsetTop - 100, // Отступ сверху для компенсации фиксированного меню
            behavior: 'smooth'
        });
        
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.style.backgroundColor = 'var(--mint-light)';
        });
        event.currentTarget.style.backgroundColor = 'var(--mint-medium)';
    }
}
</script>
"""

PROXY_DETAIL_HTML = """
<section style="padding: 80px 0; background-color: var(--gray);">
    <div class="container" style="max-width: 800px;">
        <div style="background: var(--text-light); border-radius: 12px; padding: 40px; box-shadow: 0 5px 25px rgba(46, 62, 76, 0.1); text-align: center;">
            <h2 style="font-size: 1.8rem; color: var(--mint-dark); margin-bottom: 30px;">Благодарим за покупку!</h2>

            <div style="margin-bottom: 30px; padding: 20px; background-color: var(--mint-super-light); border-radius: 8px;">
                <p style="color: var(--mint-dark); font-weight: 600; margin-bottom: 15px; text-align: center;">
                    Не забудьте скопировать и сохранить данные ваших прокси
                </p>
            </div>

            {% for proxy in proxies_data %}
            <div style="margin-bottom: 40px; padding: 20px; background-color: var(--mint-super-light); border-radius: 8px;">
                <h3 style="font-size: 1.4rem; margin-bottom: 20px; color: var(--mint-dark);">Прокси #{{ loop.index }}</h3>

                <div style="text-align: left; margin-bottom: 15px;">
                    <p style="font-weight: 600; margin-bottom: 5px;">Страна:</p>
                    <p style="font-size: 1.1rem;">{{ country_name }}</p>
                </div>

                <div style="text-align: left; margin-bottom: 15px;">
                    <p style="font-weight: 600; margin-bottom: 5px;">IP-адрес и порт:</p>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <code style="background: var(--text-dark); color: var(--text-light); padding: 8px 15px; border-radius: 6px; font-size: 1.1rem; word-break: break-all; flex-grow: 1;">
                            {{ proxy.ip }}:{{ proxy.port }}
                        </code>
                        <button onclick="copyToClipboard('{{ proxy.ip }}:{{ proxy.port }}', this)" 
                                style="background: var(--mint-dark); color: white; border: none; border-radius: 6px; padding: 8px 12px; cursor: pointer; transition: background 0.3s;">
                            Копировать
                        </button>
                    </div>
                </div>

                <div style="text-align: left; margin-bottom: 15px;">
                    <p style="font-weight: 600; margin-bottom: 5px;">Логин:</p>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <code style="background: var(--text-dark); color: var(--text-light); padding: 8px 15px; border-radius: 6px; font-size: 1.1rem; flex-grow: 1;">{{ proxy.login }}</code>
                        <button onclick="copyToClipboard('{{ proxy.login }}', this)" 
                                style="background: var(--mint-dark); color: white; border: none; border-radius: 6px; padding: 8px 12px; cursor: pointer; transition: background 0.3s;">
                            Копировать
                        </button>
                    </div>
                </div>

                <div style="text-align: left;">
                    <p style="font-weight: 600; margin-bottom: 5px;">Пароль:</p>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <code style="background: var(--text-dark); color: var(--text-light); padding: 8px 15px; border-radius: 6px; font-size: 1.1rem; flex-grow: 1;">{{ proxy.password }}</code>
                        <button onclick="copyToClipboard('{{ proxy.password }}', this)" 
                                style="background: var(--mint-dark); color: white; border: none; border-radius: 6px; padding: 8px 12px; cursor: pointer; transition: background 0.3s;">
                            Копировать
                        </button>
                    </div>
                </div>
            </div>
            {% endfor %}

            <div style="margin-bottom: 30px; padding: 20px; background-color: var(--mint-super-light); border-radius: 8px;">
                <p style="margin-bottom: 10px;"><strong>Количество прокси:</strong> {{ quantity }}</p>
                <p style="margin-bottom: 10px;"><strong>Срок действия:</strong> 30 дней</p>
                <p><strong>Общая цена:</strong> {{ total_amount }}₽</p>
            </div>

            <a href="/" class="btn" style="background-color: var(--mint-dark); display: inline-flex; align-items: center; justify-content: center;">
                Вернуться на главную
            </a>
        </div>
    </div>

    <script>
    function copyToClipboard(text, button) {
        navigator.clipboard.writeText(text).then(function() {
            const originalText = button.textContent;
            button.textContent = 'Скопировано!';
            button.style.background = '#4CAF50';

            setTimeout(function() {
                button.textContent = originalText;
                button.style.background = '#4AA896';
            }, 2000);
        }).catch(function(err) {
            console.error('Не удалось скопировать текст: ', err);
            button.textContent = 'Ошибка!';
            button.style.background = '#F44336';
        });
    }
    </script>
</section>
"""


# ============================================================================
# ROUTES: PUBLIC
# ============================================================================

@app.route('/')
def home():
    return render_template_string(
        BASE_HTML.format(
            title="Премиум прокси",
            content=LANDING_HTML,
            year=datetime.now().year
        )
    )
@app.route('/proxies')
def proxies():
    return render_template_string(
        BASE_HTML.format(
            title="Выбор прокси",
            content=PROXIES_HTML,
            year=datetime.now().year
        ),
        proxies=PROXIES
    )

@app.route('/proxy/<region_id>/<country_id>')
def proxy_detail(region_id, country_id):
    if not _validate_region_country(region_id, country_id):
        return redirect('/proxies')

    proxy = PROXIES[region_id]["countries"][country_id]
    quantity_options = [
        (1, proxy['price']),
        (2, proxy['price'] * 2),
        (5, proxy['price'] * 5),
        (10, proxy['price'] * 10),
        (20, proxy['price'] * 20)
    ]

    return render_template_string(
        BASE_HTML.format(
            title=f"{proxy['name']} прокси",
            content=f'''
            <section style="padding: 80px 0; text-align: center; min-height: calc(100vh - 200px);">
                <div class="container">
                    <h2 style="font-size: 2rem; margin-bottom: 20px;">{proxy['name']} прокси</h2>
                    <div style="max-width: 500px; margin: 0 auto; background: var(--text-light); 
                         padding: 30px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                        <p style="font-size: 1.2rem; margin-bottom: 15px;">Цена: <strong>{proxy['price']}₽</strong> за 1 прокси</p>

                        <form action="/create_payment/{region_id}/{country_id}" method="GET">
                            <div style="margin-bottom: 25px; text-align: left;">
                                <label for="quantity" style="display: block; margin-bottom: 8px; font-weight: 600;">Количество прокси:</label>
                                <select id="quantity" name="quantity" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                                    {chr(10).join(f'<option value="{qty}">{qty} прокси - {price}₽</option>' for qty, price in quantity_options)}
                                </select>
                            </div>

                            <button type="submit" class="btn" style="width: 100%;">
                                Оплатить
                            </button>
                        </form>
                    </div>
                </div>
            </section>
            ''',
            year=datetime.now().year
        )
    )

@app.route('/create_payment/<region_id>/<country_id>')
def create_payment(region_id, country_id):
    if not _validate_region_country(region_id, country_id):
        return redirect('/proxies')

    try:
        quantity = max(1, min(20, int(request.args.get('quantity', '1'))))
    except (ValueError, TypeError):
        quantity = 1

    proxy = PROXIES[region_id]["countries"][country_id]
    total_amount = proxy["price"] * quantity
    payment_id = f"proxy_{random.randint(10000, 99999)}"

    session.update({
        "payment_id": payment_id,
        "region_id": region_id,
        "country_id": country_id,
        "amount": total_amount,
        "quantity": quantity
    })

    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO payments 
            (payment_id, region_id, country_id, amount, quantity, status, proxy_data, timestamp) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (payment_id, region_id, country_id, total_amount, quantity, 'pending', '', datetime.now()))
        conn.commit()
    except sqlite3.Error:
        return redirect('/proxies')
    finally:
        conn.close()

    return render_template_string(
        BASE_HTML.format(
            title="Оплата на карту",
            content=f'''
            <section style="padding: 40px 0; text-align: center;">
                <div class="container" style="max-width: 600px;">
                    <h2 style="margin-bottom: 30px;">Оплата {total_amount}₽ ({quantity} прокси)</h2>
                    <div style="background: var(--text-light); padding: 25px; border-radius: 12px; margin-bottom: 30px; text-align: left;">
                        <h3 style="color: var(--mint-dark); margin-bottom: 20px; text-align: center;">Реквизиты для перевода</h3>
                        <div style="margin-bottom: 20px;">
                            <p style="font-weight: bold; margin-bottom: 5px;">Номер карты:</p>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="background: var(--gray); padding: 10px 15px; border-radius: 6px; flex-grow: 1;">
                                    {BANK_CARD}
                                </div>
                                <button onclick="copyToClipboard('{BANK_CARD}')" 
                                        style="background: var(--mint-dark); color: white; border: none; border-radius: 6px; padding: 10px 15px; cursor: pointer;">
                                    Копировать
                                </button>
                            </div>
                        </div>
                        <div style="margin-bottom: 25px;">
                            <p style="font-weight: bold; margin-bottom: 5px;">Комментарий к платежу:</p>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="background: var(--gray); padding: 10px 15px; border-radius: 6px; flex-grow: 1;">
                                    {payment_id}
                                </div>
                                <button onclick="copyToClipboard('{payment_id}')" 
                                        style="background: var(--mint-dark); color: white; border: none; border-radius: 6px; padding: 10px 15px; cursor: pointer;">
                                    Копировать
                                </button>
                            </div>
                            <p style="font-size: 0.9rem; color: #e74c3c; margin-top: 5px;">Обязательно укажите этот комментарий!</p>
                        </div>
                        <div style="background: var(--mint-super-light); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                            <p style="font-weight: bold; margin-bottom: 10px;">Инструкция:</p>
                            <ol style="padding-left: 20px; margin: 0;">
                                <li>Скопируйте номер карты</li>
                                <li>Скопируйте комментарий</li>
                                <li>Сделайте перевод через ваш банк</li>
                                <li>Нажмите "Я оплатил"</li>
                            </ol>
                        </div>
                        <a href="/check_payment" class="btn" style="width: 100%; text-align: center;">
                            Я оплатил
                        </a>
                    </div>
                    <p style="color: #666;">Обычно проверка занимает до 15 минут</p>
                </div>
            </section>
            <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text);
                alert('Скопировано: ' + text);
            }}
            </script>
            ''',
            year=datetime.now().year
        )
    )

@app.route('/check_payment')
def check_payment():
    payment_id = session.get("payment_id")
    if not payment_id:
        return redirect('/proxies')

    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute("SELECT status, proxy_data, amount, quantity FROM payments WHERE payment_id=?", (payment_id,))
    payment = c.fetchone()
    conn.close()

    if not payment:
        if 'proxies_data' in session:
            proxies_data = session['proxies_data']
            region_id = session.get("region_id")
            country_id = session.get("country_id")
            amount = session.get("amount")
            quantity = session.get("quantity")
            country_name = _get_country_name(region_id, country_id)

            return render_template_string(
                BASE_HTML.format(
                    title=f"{country_name} прокси",
                    content=PROXY_DETAIL_HTML,
                    year=datetime.now().year
                ),
                proxies_data=proxies_data,
                country_name=country_name,
                quantity=quantity,
                total_amount=amount
            )
        return redirect('/proxies')

    status, proxy_data, amount, quantity = payment

    if status == 'success':
        try:
            proxies_data = json.loads(proxy_data) if proxy_data else []
            session['proxies_data'] = proxies_data
            session['amount'] = amount
            session['quantity'] = quantity
        except (json.JSONDecodeError, ValueError):
            proxies_data = []

        region_id = session.get("region_id")
        country_id = session.get("country_id")
        country_name = _get_country_name(region_id, country_id)

        return render_template_string(
            BASE_HTML.format(
                title=f"{country_name} прокси",
                content=PROXY_DETAIL_HTML,
                year=datetime.now().year
            ),
            proxies_data=proxies_data,
            country_name=country_name,
            quantity=quantity,
            total_amount=amount
        )

    return render_template_string(
        BASE_HTML.format(
            title="Ожидание оплаты",
            content=f'''
            <section style="padding: 80px 0; text-align: center; min-height: calc(100vh - 200px);">
                <div class="container" style="max-width: 600px;">
                    <div style="background: var(--text-light); padding: 30px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                        <h2 style="margin-bottom: 20px;">Платеж проверяется</h2>
                        <div style="margin-bottom: 30px;">
                            <p style="margin-bottom: 15px;">
                                Мы получили ваш платеж и проверяем его.<br>
                                Обычно это занимает до 15 минут.
                            </p>
                            <div style="background: var(--mint-super-light); padding: 15px; border-radius: 8px;">
                                <p>Номер вашего платежа: <strong>{payment_id}</strong></p>
                                <p>Сумма: <strong>{amount}₽</strong></p>
                                <p>Количество прокси: <strong>{quantity}</strong></p>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: center; gap: 15px;">
                            <a href="/check_payment" class="btn">Проверить снова</a>
                            <a href="/" class="btn" style="background: var(--gray); color: var(--text-dark);">На главную</a>
                        </div>
                    </div>
                </div>
            </section>
            ''',
            year=datetime.now().year
        )
    )


# ============================================================================
# ROUTES: ADMIN
# ============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            return redirect('/admin')

    return render_template_string(BASE_HTML.format(
        title="Вход в админку",
        content='''
        <section style="padding: 80px 0; text-align: center; min-height: calc(100vh - 200px);">
            <div class="container" style="max-width: 400px;">
                <h2 style="margin-bottom: 30px;">Вход в админ-панель</h2>
                <form method="POST" style="background: var(--text-light); padding: 25px; border-radius: 12px;">
                    <div style="margin-bottom: 20px;">
                        <input type="text" name="username" placeholder="Логин" required 
                               style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                    </div>
                    <div style="margin-bottom: 25px;">
                        <input type="password" name="password" placeholder="Пароль" required
                               style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                    </div>
                    <button type="submit" class="btn" style="width: 100%;">Войти</button>
                </form>
            </div>
        </section>
        ''',
        year=datetime.now().year
    ))

@app.route('/admin')
@login_required
def admin_panel():
    message = session.pop('admin_message', None)
    message_html = ""
    if message:
        text, category = message
        color = "#4CAF50" if category == "success" else "#F44336"
        message_html = f'''<div style="margin-bottom: 20px; padding: 15px; background-color: {color}20; border-left: 4px solid {color}; color: {color};">{text}</div>'''

    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute("SELECT payment_id, region_id, country_id, amount, quantity, status, timestamp FROM payments ORDER BY timestamp DESC")
    payments = c.fetchall()
    conn.close()

    payment_rows = ""
    for payment_id, region_id, country_id, amount, quantity, status, timestamp in payments:
        status_color = "#2ecc71" if status == "success" else "#e74c3c"
        country_name = _get_country_name(region_id, country_id)
        
        action_btn = f'<a href="/admin/confirm/{payment_id}" class="btn" style="padding: 5px 10px; font-size: 0.9rem; margin-right: 5px;">Подтвердить</a>' if status != "success" else '✅'
        
        payment_rows += f'''<tr>
            <td>{payment_id}</td>
            <td>{country_name}</td>
            <td>{amount}₽</td>
            <td>{quantity}</td>
            <td style="color: {status_color}">{status}</td>
            <td>{timestamp}</td>
            <td style="white-space: nowrap;">
                {action_btn}
                <a href="/admin/delete/{payment_id}" class="btn" style="padding: 5px 10px; font-size: 0.9rem; background-color: #e74c3c;">Удалить</a>
            </td>
        </tr>'''

    return render_template_string(BASE_HTML.format(
        title="Админ-панель",
        content=f'''
        <section style="padding: 40px 0; min-height: calc(100vh - 200px);">
            <div class="container">
                <h2 style="margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center;">
                    <span>Ожидающие платежи</span>
                    <a href="/admin/logout" class="btn" style="padding: 5px 15px; font-size: 0.9rem;">Выйти</a>
                </h2>

                {message_html}

                <div style="overflow-x: auto; margin-bottom: 30px;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: var(--mint-dark); color: white;">
                                <th style="padding: 12px; text-align: left;">ID платежа</th>
                                <th style="padding: 12px; text-align: left;">Страна</th>
                                <th style="padding: 12px; text-align: left;">Сумма</th>
                                <th style="padding: 12px; text-align: left;">Кол-во</th>
                                <th style="padding: 12px; text-align: left;">Статус</th>
                                <th style="padding: 12px; text-align: left;">Дата</th>
                                <th style="padding: 12px; text-align: left;">Действия</th>
                            </tr>
                        </thead>
                        <tbody>
                            {payment_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
        ''',
        year=datetime.now().year
    ))

@app.route('/admin/delete/<payment_id>')
@login_required
def delete_payment(payment_id):
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()
    c.execute("DELETE FROM payments WHERE payment_id=?", (payment_id,))
    conn.commit()
    conn.close()

    session['admin_message'] = ('Платеж удален', 'success')
    return redirect('/admin')


@app.route('/admin/confirm/<payment_id>')
@login_required
def confirm_payment(payment_id):
    conn = sqlite3.connect('payments.db')
    c = conn.cursor()

    try:
        c.execute("SELECT region_id, country_id, quantity FROM payments WHERE payment_id=?", (payment_id,))
        payment_info = c.fetchone()

        if not payment_info:
            session['admin_message'] = ('Платеж не найден', 'error')
            return redirect('/admin')

        region_id, country_id, quantity = payment_info
        proxies_data = _generate_proxy_data(quantity)

        c.execute("UPDATE payments SET status=?, proxy_data=? WHERE payment_id=?",
                 ('success', json.dumps(proxies_data), payment_id))
        conn.commit()

        session['admin_message'] = ('Платеж подтвержден! Данные прокси сгенерированы.', 'success')

    except sqlite3.Error:
        session['admin_message'] = ('Ошибка при подтверждении платежа', 'error')
    finally:
        conn.close()

    return redirect('/admin')


@app.route('/admin/logout')
@login_required
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template_string(BASE_HTML.format(
        title="Страница не найдена",
        content='''
        <section style="padding: 80px 0; text-align: center; min-height: calc(100vh - 200px);">
            <div class="container">
                <h1 style="font-size: 3rem; margin-bottom: 20px;">404</h1>
                <p style="font-size: 1.3rem; margin-bottom: 30px;">Страница не найдена</p>
                <a href="/" class="btn">Вернуться на главную</a>
            </div>
        </section>
        ''',
        year=datetime.now().year
    )), 404


@app.errorhandler(500)
def server_error(error):
    return render_template_string(BASE_HTML.format(
        title="Ошибка сервера",
        content='''
        <section style="padding: 80px 0; text-align: center; min-height: calc(100vh - 200px);">
            <div class="container">
                <h1 style="font-size: 3rem; margin-bottom: 20px;">500</h1>
                <p style="font-size: 1.3rem; margin-bottom: 30px;">Внутренняя ошибка сервера</p>
                <a href="/" class="btn">Вернуться на главную</a>
            </div>
        </section>
        ''',
        year=datetime.now().year
    )), 500


# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)