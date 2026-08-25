# -*- coding: utf-8 -*-
"""Генератор фігур для теми 'Гримуча отара на масштабі'."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / перевантаження / синхронізована лавина
COOL = "#eaf0fd"   # клієнти / нормальний потік / мережа
GOOD = "#e8f6ee"   # стабільність / десинхронізація / захист
ACCENT = "#fef9e7" # координація / черги / проміжний стан


# ── 1. Анатомія гримучої отари на масштабі ─────────────────────────────────
def fig_herd_anatomy_scale():
    W, H = 1180, 580
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "Анатомія гримучої отари: фазова синхронізація та резонансний колапс системи",
                    size=13, bold=True, fill=COOL))

    # Колонка 1: Тригер та масове скидання стану
    f.append(rect(40, 80, 330, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 95, 300, 34, "1. Тригер та скидання сесій", size=11, bold=True, fill=COOL, stroke=LINE))
    
    f.append(fitbox(55, 140, 300, 45, "Подія в системі:\n• Перезапуск шлюзу / BGP-флап\n• Одночасне скидання 2 000 000 з'єднань", size=10, fill=FILL, stroke=MUTED))
    f.append(fitbox(55, 195, 300, 60, "Детермінована поведінка клієнтів:\nКод клієнта: sleep(1.0) -> connect()\nУсі 2 млн таймерів завершуються в мить\nt = 03:00:01.000 (точність до мс)", size=9.5, fill=WARM, stroke=POS))
    
    f.append(arrow(205, 265, 205, 295, color=POS, sw=2.0))
    f.append(fitbox(55, 300, 300, 105, "Синхронізований імпульс (Herd Surge):\nВхідний пік: 2 000 000 запитів/с\n(нормальна пропускна здатність 50 000 RPS)\nСтрибок навантаження у 40 разів\nза інтервал часу < 50 мілісекунд", size=10, fill=WARM, stroke=POS))
    
    f.append(fitbox(55, 415, 300, 115, "Фазова узгодженість (Phase Coherence):\nКлієнти діють як єдиний когерентний осцилятор:\nвсі сплять одночасно і б'ють одночасно,\nутворюючи резонансний шторм", size=9.5, fill=WARM, stroke=POS))

    # Колонка 2: Колапс вузького місця
    f.append(rect(390, 80, 380, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(405, 95, 350, 34, "2. Колапс вузького місця (Шлюз)", size=11, bold=True, fill=WARM, stroke=POS))

    f.append(fitbox(405, 140, 350, 60, "Виснаження черг сокетів:\n• Черга listen queue (somaxconn) переповнена\n• Ядро дропає 98% вхідних TCP SYN пакетів\n• CPU витрачається на softirq та handshake", size=9.5, fill=WARM, stroke=POS))
    
    f.append(fitbox(405, 210, 350, 60, "TLS Handshake & Обчислювальний тупик:\n• 2.5 мс CPU на повний TLS 1.3 ECDH обмін\n• 128 ядр здатні виконати лише 51k TLS/s\n• 100% CPU зайнято криптографією", size=9.5, fill=WARM, stroke=POS))

    f.append(fitbox(405, 280, 350, 60, "Деградація затримки та таймаути:\n• Затримка підключення: 10 мс -> 30 000 мс\n• Спрацьовує клієнтський таймаут 3.0 с\n• Сервер витратив ресурси даремно", size=9.5, fill=WARM, stroke=POS))

    f.append(fitbox(405, 350, 350, 180, "Метастабільний резонанс (Metastability):\n1. Мільйони відхилених клієнтів знову сплять\n   однаковий час (наприклад, ще 3 секунди).\n2. О 03:00:04.000 приходить Друга Хвиля.\n3. О 03:00:07.000 приходить Третя Хвиля.\n4. Корисна робота (goodput) = 0%.\n5. Система ніколи не відновлюється сама!", size=10, fill=WARM, stroke=POS))

    # Колонка 3: Архітектурний захист
    f.append(rect(790, 80, 350, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(805, 95, 320, 34, "3. Десинхронізація та бар'єри", size=11, bold=True, fill=GOOD, stroke=FIELD))

    f.append(fitbox(805, 140, 320, 75, "А. Клієнтський джитер (Decorrelated Jitter):\nРозмазування повторних спроб у часі:\nt = min(cap, uniform(base, prev * 3))\nРуйнує фазову когерентність імпульсу.", size=9.5, fill=GOOD, stroke=FIELD))

    f.append(fitbox(805, 225, 320, 75, "Б. Вхідний контроль (Admission / Token Bucket):\nШлюз миттєво відсікає надлишок SYN/TCP,\nпропускаючи лише гарантовані 50k conn/s.\nЗахищає CPU від перевантаження.", size=9.5, fill=GOOD, stroke=FIELD))

    f.append(fitbox(805, 310, 320, 75, "В. TLS Session Tickets (RFC 8446):\nСкорочення часу хендшейку з 2.5 мс до 0.1 мс.\nПропускна здатність TLS зростає у 25 разів\nпри масових повторних підключеннях.", size=9.5, fill=GOOD, stroke=FIELD))

    f.append(fitbox(805, 395, 320, 135, "Г. Ступінчастий плавний старт (Slow-Start):\nВідновлений вузол нарощує ліміт трафіку\nпоступово: 10% -> 25% -> 50% -> 100%,\nне провокуючи миттєвий прорив дамби\nі не захоплюючи весь трафік отари.", size=9.5, fill=GOOD, stroke=FIELD))

    # З'єднувальні стрілки
    f.append(arrow(370, 220, 390, 220, color=POS, sw=2.0))
    f.append(arrow(770, 220, 790, 220, color=FIELD, sw=2.0))

    render(os.path.join(OUT, "herd-anatomy-scale.svg"), W, H, *f)


# ── 2. Порівняння хвиль синхронізації: детермінізм проти джитеру ──────────
def fig_synchronization_waves():
    W, H = 1180, 540
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "Динаміка навантаження: синхронізований резонанс проти експоненційного розсіювання",
                    size=13, bold=True, fill=COOL))

    # Ліва панель: Без джитеру (Синхронізація отари)
    f.append(rect(40, 80, 535, 435, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 95, 505, 32, "А. Без джитеру: синхронізовані резонансні піки (Collapse)", size=11, bold=True, fill=WARM, stroke=POS))

    # Вісь та графік ліворуч
    # Базова лінія (час t)
    f.append(line(75, 340, 545, 340, color=LINE, sw=1.5))
    # Вісь Y (RPS)
    f.append(line(75, 340, 75, 140, color=LINE, sw=1.5))
    f.append(text(75, 135, "RPS (Навантаження)", size=10, color=INK, anchor="start", bold=True))
    f.append(text(545, 355, "Час (с)", size=10, color=INK, anchor="end"))

    # Лінія ліміту місткості сервера
    f.append(line(75, 260, 545, 260, color=POS, sw=1.5, dash="4,4"))
    f.append(text(460, 252, "Ліміт місткості сервера", size=9.5, color=POS, bold=True))

    # Хвилі-піки без джитеру
    # Пік 1 (t=1c)
    f.append(rect(130, 150, 40, 190, fill="#f9d5d5", stroke=POS, sw=1.5))
    f.append(text(150, 142, "2.0M", size=9, color=POS, bold=True))
    f.append(text(150, 355, "t = 1s", size=9, color=INK))

    # Пік 2 (t=3c)
    f.append(rect(240, 160, 40, 180, fill="#f9d5d5", stroke=POS, sw=1.5))
    f.append(text(260, 152, "1.8M", size=9, color=POS, bold=True))
    f.append(text(260, 355, "t = 3s", size=9, color=INK))

    # Пік 3 (t=7c)
    f.append(rect(370, 175, 40, 165, fill="#f9d5d5", stroke=POS, sw=1.5))
    f.append(text(390, 167, "1.5M", size=9, color=POS, bold=True))
    f.append(text(390, 355, "t = 7s", size=9, color=INK))

    # Пік 4 (t=15c)
    f.append(rect(480, 190, 40, 150, fill="#f9d5d5", stroke=POS, sw=1.5))
    f.append(text(500, 182, "1.3M", size=9, color=POS, bold=True))
    f.append(text(500, 355, "t = 15s", size=9, color=INK))

    f.append(fitbox(55, 380, 505, 115, "Характеристики некерованої отари:\n• Кожен пік значно перевищує фізичну місткість вузла.\n• 100% запитів під час піку зазнають відмови через черги та таймаути.\n• Періоди між піками мають нульове завантаження (CPU простоює).\n• Клієнти зберігають синхронність фази через фіксовані множники 2^i.", size=9.5, fill=WARM, stroke=POS))

    # Права панель: З Decorrelated Jitter
    f.append(rect(605, 80, 535, 435, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(620, 95, 505, 32, "Б. З Decorrelated Jitter: рівномірне розсіювання потоку (Stable)", size=11, bold=True, fill=GOOD, stroke=FIELD))

    # Вісь та графік праворуч
    f.append(line(640, 340, 1110, 340, color=LINE, sw=1.5))
    f.append(line(640, 340, 640, 140, color=LINE, sw=1.5))
    f.append(text(640, 135, "RPS (Навантаження)", size=10, color=INK, anchor="start", bold=True))
    f.append(text(1110, 355, "Час (с)", size=10, color=INK, anchor="end"))

    # Лінія ліміту місткості сервера
    f.append(line(640, 260, 1110, 260, color=POS, sw=1.5, dash="4,4"))
    f.append(text(1025, 252, "Ліміт місткості сервера", size=9.5, color=POS, bold=True))

    # Плавне розсіяне навантаження під лінією місткості
    # Початковий зрізаний пік (в межах норми)
    f.append(rect(660, 270, 50, 70, fill="#d4edda", stroke=FIELD, sw=1.5))
    f.append(rect(710, 280, 70, 60, fill="#d4edda", stroke=FIELD, sw=1.5))
    f.append(rect(780, 295, 90, 45, fill="#d4edda", stroke=FIELD, sw=1.5))
    f.append(rect(870, 310, 110, 30, fill="#d4edda", stroke=FIELD, sw=1.5))
    f.append(rect(980, 325, 110, 15, fill="#d4edda", stroke=FIELD, sw=1.5))

    f.append(text(685, 262, "45k RPS", size=9, color=FIELD, bold=True))
    f.append(text(745, 272, "38k RPS", size=9, color=FIELD))
    f.append(text(825, 287, "25k RPS", size=9, color=FIELD))
    f.append(text(925, 302, "12k RPS", size=9, color=FIELD))

    f.append(fitbox(620, 380, 505, 115, "Характеристики десинхронізованого потоку:\n• Випадковий шум руйнує фазову когерентність клієнтських циклів.\n• Навантаження розмазується тонким шаром, не перевищуючи ліміт.\n• Goodput наближається до 100%: кожен запит отримує відповідь.\n• Сервер стабільно перетравлює отару за передбачуваний час.", size=9.5, fill=GOOD, stroke=FIELD))

    render(os.path.join(OUT, "synchronization-waves.svg"), W, H, *f)


# ── 3. Багаторівнева матриця захисту від гримучої отари ────────────────────
def fig_defense_layers():
    W, H = 1180, 580
    f = []

    f.append(fitbox(40, 20, 1100, 44,
                    "Багаторівневий захист від штормів пробудження у розподілених архітектурах",
                    size=13, bold=True, fill=COOL))

    # 4 рівні захисту (шари від ядра до клієнта)
    # Рівень 1: Транспорт та Ядро ОС
    f.append(rect(40, 80, 260, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(55, 95, 230, 34, "1. Транспорт та Ядро", size=11, bold=True, fill=COOL, stroke=LINE))
    f.append(fitbox(55, 140, 230, 75, "SO_REUSEPORT:\nШардинг черг слухання між\nпотоками ядра без конкуренції\nза єдиний accept-мутекс.", size=9.5, fill=FILL, stroke=MUTED))
    f.append(fitbox(55, 225, 230, 75, "EPOLLEXCLUSIVE:\nПробудження строго одного\nворкера на подію замість\nусіх N сплячих потоків.", size=9.5, fill=FILL, stroke=MUTED))
    f.append(fitbox(55, 310, 230, 95, "SYN Cookies & Backlog:\nЗахист від переповнення\nчерги TCP без виділення\nструктур стану в ядрі\nпри зливних сплесках SYN.", size=9.5, fill=FILL, stroke=MUTED))
    f.append(fitbox(55, 415, 230, 115, "TLS Session Resumption:\nЗменшення витрат CPU\nна повторне встановлення\nзахищеного каналу завдяки\nквиткам сесій (Session Tickets).", size=9.5, fill=GOOD, stroke=FIELD))

    # Рівень 2: Вхідний шлюз та Admission Control
    f.append(rect(320, 80, 260, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(335, 95, 230, 34, "2. Шлюз та Вхідний бар'єр", size=11, bold=True, fill=ACCENT, stroke=LINE))
    f.append(fitbox(335, 140, 230, 75, "Token Bucket Limiting:\nЖорстке відсікання сплесків\nз'єднань на вході з поверненням\nшвидкої помилки (429 / RST).", size=9.5, fill=FILL, stroke=MUTED))
    f.append(fitbox(335, 225, 230, 75, "Staggered Staged Warm-up:\nПоступове відкриття шлюзу\nпісля старту для уникнення\nхолодного удару по бекендах.", size=9.5, fill=FILL, stroke=MUTED))
    f.append(fitbox(335, 310, 230, 95, "Jittered Retry-After:\nHTTP 429 з динамічним\nзаголовком Retry-After:\nHeader = base + random()\nдля розсіювання клієнтів.", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(335, 415, 230, 115, "Load Shedding:\nСкидання низькопріоритетних\nфонових запитів на користь\nкритичних операцій користувача\nпід час пікового навантаження.", size=9.5, fill=GOOD, stroke=FIELD))

    # Рівень 3: Розподілена координація
    f.append(rect(600, 80, 260, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(615, 95, 230, 34, "3. Координація та Замки", size=11, bold=True, fill=WARM, stroke=POS))
    f.append(fitbox(615, 140, 230, 75, "Послідовні вотчі (ZNode):\nКлієнт чекає ТІЛЬКИ на свій\nпопередник (i - 1), запобігаючи\nшторму пробудження O(N^2).", size=9.5, fill=FILL, stroke=MUTED))
    f.append(fitbox(615, 225, 230, 75, "Raft Randomized Election:\nВипадковий інтервал виборів\n(150-300 мс) гарантує швидке\nобрання лідера без колізій.", size=9.5, fill=FILL, stroke=MUTED))
    f.append(fitbox(615, 310, 230, 95, "Staggered Lease Renewals:\nПеріодичне оновлення лізів\nу Soft-State реєстрах з\nіндивідуальним зміщенням фази\n(Hash(ID) mod Interval).", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(615, 415, 230, 115, "Hierarchical Single-Flight:\nЛокальне злиття однакових\nзапитів на рівні екземплярів\nперед зверненням до загального\nкластера координації.", size=9.5, fill=GOOD, stroke=FIELD))

    # Рівень 4: Клієнтська дисципліна
    f.append(rect(880, 80, 260, 470, fill=FILL, stroke=MUTED, sw=1.2))
    f.append(fitbox(895, 95, 230, 34, "4. Клієнтська дисципліна", size=11, bold=True, fill=GOOD, stroke=FIELD))
    f.append(fitbox(895, 140, 230, 75, "Decorrelated Jitter:\nНелінійне розмивання пауз\nміж спробами з урахуванням\nпопереднього інтервалу сну.", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(895, 225, 230, 75, "Retry Budgets:\nОбмеження повторів часткою\nвід успішних запитів (<= 10%),\nщо вимикає лавиноподібні шторми.", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(895, 310, 230, 95, "Client-Side Circuit Breaker:\nАвтономне розмикання кола\nна пристрої користувача при\nдетекції серійних збоїв мережі.", size=9.5, fill=GOOD, stroke=FIELD))
    f.append(fitbox(895, 415, 230, 115, "Poller Phase Offsets:\nПримусовий розкид періодичних\nтаймерів фонових завдань замість\nзапуску рівно на початку хвилини\n(00.000 секунд).", size=9.5, fill=GOOD, stroke=FIELD))

    render(os.path.join(OUT, "defense-layers.svg"), W, H, *f)


if __name__ == '__main__':
    fig_herd_anatomy_scale()
    fig_synchronization_waves()
    fig_defense_layers()
    print("All figures successfully generated in", OUT)
