# -*- coding: utf-8 -*-
"""Фігури до теми «Вирівнювання навантаження чергою (Queue-Based Load Leveling)»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # небезпека / збій / перевантаження
COOL = "#eaf0fd"   # нейтральне / структури / компоненти
GOOD = "#e8f6ee"   # успіх / захищений бекенд / стабільність
WARN = "#fef9e7"   # черга / буфер / очікування / застереження


# ── 1. Динаміка амортизації сплеску: вхідний потік, глибина черги та злив ──────
def queue_load_leveling_dynamics():
    W, H = 1120, 520
    f = []

    # Загальне тло
    f.append(rect(20, 20, 1080, 480, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=8))
    f.append(text(560, 45, "Гідродинаміка демпфування: вхідний сплеск, буферизація та контрольований злив", size=14, bold=True, color="#1e293b"))

    # Графік 1: Вхідний потік λ(t) та ліміт бекенду μ
    f.append(rect(40, 70, 500, 190, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(290, 92, "1. Швидкість надходження λ(t) проти ємності бекенду μ", size=12, bold=True, color=INK))

    # Осі графіка 1
    f.append(line(80, 230, 510, 230, color=LINE, sw=1.5))
    f.append(arrow(80, 230, 80, 110, color=LINE, sw=1.5))
    f.append(text(75, 105, "RPS", size=11, color=MUTED, anchor="end", bold=True))
    f.append(text(515, 235, "Час t", size=11, color=MUTED, anchor="start"))

    # Полігон сплеску трафіку λ(t)
    f.append('<polygon points="90,215 150,215 220,125 270,125 340,215 500,215 500,230 90,230" fill="#fee2e2" stroke="#ef4444" stroke-width="1.8"/>')
    f.append(text(245, 145, "Піковий сплеск λ(t) = 10 000 RPS", size=10, bold=True, color=POS))

    # Лінія безпечної пропускної здатності μ_safe (y=185 -> 400 RPS)
    f.append(line(80, 185, 510, 185, color=FIELD, sw=2, dash="5,4"))
    f.append(text(420, 175, "Ємність бекенду μ = 400 RPS", size=10, bold=True, color=FIELD))

    # Зона надлишку енергії сплеску
    f.append(fitbox(155, 160, 180, 36, "Надлишковий обсяг (Backlog)\nАкумулюється в черзі", size=10, fill="#fef3c7", stroke="#d97706", sw=1))

    # Графік 2: Глибина черги Q(t)
    f.append(rect(570, 70, 510, 190, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(825, 92, "2. Динаміка наповнення та зливу черги Q(t)", size=12, bold=True, color=INK))

    # Осі графіка 2
    f.append(line(610, 230, 1050, 230, color=LINE, sw=1.5))
    f.append(arrow(610, 230, 610, 110, color=LINE, sw=1.5))
    f.append(text(605, 105, "Повідомлень", size=11, color=MUTED, anchor="end", bold=True))
    f.append(text(1055, 235, "Час t", size=11, color=MUTED, anchor="start"))

    # Трапеція зростання і спадання черги
    f.append('<polygon points="620,230 670,230 790,130 810,130 1010,230 620,230" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>')
    f.append(text(800, 120, "Q_max (Пікова глибина)", size=10, bold=True, color="#b45309"))

    # Позначення фаз: Сплеск і Злив
    f.append(line(670, 235, 800, 235, color=POS, sw=1.5))
    f.append(text(735, 250, "Фаза накопичення (λ > μ)", size=9, bold=True, color=POS))

    f.append(line(810, 235, 1010, 235, color=FIELD, sw=1.5))
    f.append(text(910, 250, "Фаза зливу T_drain (λ < μ)", size=9, bold=True, color=FIELD))

    # Нижня панель: Стан бекенду і результат
    f.append(rect(40, 280, 1040, 200, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(560, 305, "3. Режим роботи захищеного бекенду (База даних / Зовнішній API)", size=13, bold=True, color="#166534"))

    # Три ключові показники
    f.append(fitbox(60, 325, 300, 135,
                     "Навантаження на CPU та I/O:\nСтабільне 75-80%\n\n• Пул з'єднань БД: фіксований (50)\n• Немає вичерпання пам'яті (OOM)\n• Відсутня деградація дискового WAL",
                     size=11, fill="#ffffff", stroke=FIELD, sw=1.2))

    f.append(fitbox(410, 325, 300, 135,
                     "Пропускна здатність вичитування:\nКонтрольовані 400 req/s\n\n• Рівномірний темп обробки\n• Відсутність збоїв через сплеск\n• 100% збереження транзакцій",
                     size=11, fill="#ffffff", stroke=FIELD, sw=1.2))

    f.append(fitbox(760, 325, 300, 135,
                     "Компроміс затримки (Trade-off):\nЛатентність зростає контрольовано\n\n• T_wait = Q(t) / μ\n• Клієнт отримує 202 Accepted\n• Результат через опитування або Webhook",
                     size=11, fill="#ffffff", stroke=FIELD, sw=1.2))

    render(os.path.join(OUT, 'queue-load-leveling-dynamics.svg'), W, H, *f)


# ── 2. Повна архітектура системи з демпфуванням навантаження ──────────────────
def queue_load_leveling_architecture():
    W, H = 1140, 520
    f = []

    # Тло
    f.append(rect(20, 20, 1100, 480, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=8))
    f.append(text(570, 45, "Архітектура патерну Queue-Based Load Leveling", size=14, bold=True, color="#0f172a"))

    # 1. Клієнти ліворуч
    f.append(rect(35, 80, 170, 380, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    f.append(text(120, 105, "Клієнти / Джерела", size=12, bold=True, color=INK))
    f.append(fitbox(50, 125, 140, 55, "Мобільні клієнти\n(HTTP POST)", size=10, fill=COOL))
    f.append(fitbox(50, 195, 140, 55, "Веб-фронтенди\n(Сплеск замовлень)", size=10, fill=COOL))
    f.append(fitbox(50, 265, 140, 55, "IoT / Сенсори\n(Телеметрія)", size=10, fill=COOL))
    f.append(fitbox(50, 335, 140, 55, "Партнерські Webhooks\n(Масовий імпорт)", size=10, fill=COOL))
    f.append(text(120, 425, "Сплески до 10 000 RPS", size=10, bold=True, color=POS))

    # Стрілка від клієнтів до шлюзу
    f.append(arrow(205, 230, 250, 230, color=POS, sw=2))
    f.append(text(228, 220, "Сплеск", size=9, bold=True, color=POS))

    # 2. Шлюз прийому (Ingress API)
    f.append(rect(250, 80, 190, 380, fill="#f1f5f9", stroke=LINE, sw=1.3, rx=6))
    f.append(text(345, 105, "Шлюз прийому (Ingress)", size=12, bold=True, color=INK))
    f.append(fitbox(265, 125, 160, 60, "Валідація схеми\nГенерація job_id\nАутентифікація", size=10, fill="#ffffff"))
    f.append(fitbox(265, 200, 160, 65, "Асинхронна публікація\n(Запис у чергу < 2 мс)\nO(1) Append", size=10, fill="#ffffff", stroke=FIELD))
    f.append(fitbox(265, 280, 160, 65, "Миттєва відповідь:\n202 Accepted\nLocation: /jobs/{id}", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(265, 360, 160, 85, "Захист переповнення:\nЯкщо черга повна (HWM)\n→ 429 Too Many Requests\n(Retry-After: 30s)", size=10, fill=WARM, stroke=POS))

    # Стрілка від шлюзу до черги
    f.append(arrow(440, 230, 485, 230, color=FIELD, sw=2))
    f.append(text(462, 220, "Enqueue", size=9, bold=True, color=FIELD))

    # 3. Брокер повідомлень / Буфер черги
    f.append(rect(485, 80, 240, 380, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    f.append(text(605, 105, "Буфер черги (Queue Buffer)", size=12, bold=True, color="#92400e"))

    # Елементи черги всередині
    msgs = [("M6", 500), ("M5", 540), ("M4", 580), ("M3", 620), ("M2", 660)]
    for lbl, mx in msgs:
        f.append(rect(mx, 130, 35, 45, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
        f.append(text(mx + 17, 157, lbl, size=10, bold=True, color="#92400e"))

    f.append(text(605, 195, "FIFO Буфер / Журнал партицій", size=10, bold=True, color=INK))
    f.append(fitbox(500, 215, 210, 60, "Надійне збереження (Disk WAL)\nЛізи видимості (Visibility Lease)\nКонтроль розміру (Max Depth)", size=10, fill="#ffffff", stroke="#d97706"))

    # Мертва черга DLQ
    f.append(rect(500, 290, 210, 75, fill="#fee2e2", stroke=POS, sw=1.2, rx=5))
    f.append(text(605, 310, "Мертва черга (DLQ)", size=10, bold=True, color=POS))
    f.append(text(605, 335, "Отруйні задачі / Вичерпано TTL", size=9, color=INK))
    f.append(text(605, 352, "Ізоляція від робочого потоку", size=9, color=MUTED, italic=True))

    f.append(fitbox(500, 380, 210, 65, "Метрики для автоскейлінгу:\n• Queue Depth / Lag\n• Backlog Drain Estimate\n• KEDA / HPA тригери", size=10, fill="#ffffff", stroke=MUTED))

    # Стрілка від черги до воркерів
    f.append(arrow(725, 230, 770, 230, color=FIELD, sw=2))
    f.append(text(747, 220, "Dequeue", size=9, bold=True, color=FIELD))

    # 4. Пул споживачів (Worker Pool)
    f.append(rect(770, 80, 170, 380, fill="#f1f5f9", stroke=LINE, sw=1.3, rx=6))
    f.append(text(855, 105, "Пул воркерів", size=12, bold=True, color=INK))
    f.append(fitbox(785, 125, 140, 50, "Воркер #1 ⚡\n[Rate: 100 req/s]", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(785, 185, 140, 50, "Воркер #2 ⚡\n[Rate: 100 req/s]", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(785, 245, 140, 50, "Воркер #3 ⚡\n[Rate: 100 req/s]", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(785, 305, 140, 50, "Воркер #4 ⚡\n[Rate: 100 req/s]", size=10, fill=GOOD, stroke=FIELD))
    f.append(fitbox(785, 365, 140, 80, "Обмеження темпу:\nToken Bucket / Ліміт\nСумарно: ≤ 400 req/s\nФіксований пул потоків", size=10, fill="#ffffff", stroke=FIELD))

    # Стрілка від воркерів до бекенду
    f.append(arrow(940, 230, 985, 230, color=FIELD, sw=2))
    f.append(text(962, 220, "Write", size=9, bold=True, color=FIELD))

    # 5. Захищений бекенд (Database / API)
    f.append(rect(985, 80, 125, 380, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(1047, 105, "Бекенд", size=12, bold=True, color="#166534"))
    f.append(fitbox(995, 130, 105, 75, "Транзакційна БД\n(PostgreSQL / MySQL)", size=10, fill="#ffffff", stroke=FIELD))
    f.append(fitbox(995, 220, 105, 75, "Пул з'єднань:\n50 конектів\n(Безпечний)", size=10, fill="#ffffff", stroke=FIELD))
    f.append(fitbox(995, 310, 105, 75, "Зовнішні API\n(Платіжні шлюзи)\nСуворі квоти", size=10, fill="#ffffff", stroke=FIELD))
    f.append(text(1047, 415, "Навантаження: 80%", size=10, bold=True, color=FIELD))
    f.append(text(1047, 435, "Нуль падінь!", size=10, bold=True, color="#166534"))

    render(os.path.join(OUT, 'queue-load-leveling-architecture.svg'), W, H, *f)


# ── 3. Порівняння відмови: Прямий RPC проти Демпфування чергою ─────────────────
def direct_vs_leveled_failure():
    W, H = 1140, 480
    f = []

    # Тло
    f.append(rect(20, 20, 1100, 440, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=8))
    f.append(text(570, 45, "Сценарій сплеску 10 000 RPS: Прямий синхронний виклик проти Демпфування чергою", size=14, bold=True, color="#0f172a"))

    # Ліва колонка: Прямий синхронний виклик (Катастрофа)
    f.append(rect(40, 70, 510, 370, fill="#fef2f2", stroke=POS, sw=1.4, rx=6))
    f.append(text(295, 95, "❌ Прямий синхронний виклик (Direct RPC / REST)", size=12, bold=True, color=POS))

    f.append(fitbox(60, 115, 470, 45, "1. Сплеск 10 000 RPS надходить на API Gateway", size=11, fill="#ffffff", stroke=POS))
    f.append(arrow(295, 160, 295, 180, color=POS, sw=1.5))

    f.append(fitbox(60, 180, 470, 55, "2. API Gateway відкриває 10 000 паралельних з'єднань до БД\nВичерпання пулу потоків веб-сервера, сплеск споживання RAM", size=11, fill="#ffffff", stroke=POS))
    f.append(arrow(295, 235, 295, 255, color=POS, sw=1.5))

    f.append(fitbox(60, 255, 470, 60, "3. База даних зазнає блокувань дискового I/O та вичерпання пам'яті\nЛатентність зростає від 10 мс до 60 с → Масові 504 Gateway Timeout", size=11, fill="#ffffff", stroke=POS))
    f.append(arrow(295, 315, 295, 335, color=POS, sw=1.5))

    f.append(fitbox(60, 335, 470, 85, "4. Клієнти повторюють спроби (Retry Storm)\nКрах системи: Out Of Memory Killer аварійно вбиває процес БД,\nвсі користувачі втрачають доступ (Повний блекаут)", size=11, fill="#fee2e2", stroke=POS, bold=True))

    # Права колонка: Демпфування чергою (Стабільність)
    f.append(rect(590, 70, 510, 370, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(845, 95, "✅ Вирівнювання навантаження чергою (Load Leveling)", size=12, bold=True, color="#166534"))

    f.append(fitbox(610, 115, 470, 45, "1. Сплеск 10 000 RPS надходить на API Gateway", size=11, fill="#ffffff", stroke=FIELD))
    f.append(arrow(845, 160, 845, 180, color=FIELD, sw=1.5))

    f.append(fitbox(610, 180, 470, 55, "2. Шлюз записує задачі в чергу (< 2 мс) і повертає 202 Accepted\nЗ'єднання з клієнтами закриваються негайно, ресурси вільні", size=11, fill="#ffffff", stroke=FIELD))
    f.append(arrow(845, 235, 845, 255, color=FIELD, sw=1.5))

    f.append(fitbox(610, 255, 470, 60, "3. Буфер черги тимчасово зростає (Backlog), поглинаючи надлишок\nВоркери вичитують задачі з фіксованим темпом 400 req/s", size=11, fill="#ffffff", stroke=FIELD))
    f.append(arrow(845, 315, 845, 335, color=FIELD, sw=1.5))

    f.append(fitbox(610, 335, 470, 85, "4. База даних працює в штатному лінійному режимі (80% CPU)\nЖодної втраченої транзакції; черга плавно розвантажується;\nсистема зберігає 100% працездатність", size=11, fill="#dcfce7", stroke=FIELD, bold=True))

    render(os.path.join(OUT, 'direct-vs-leveled-failure.svg'), W, H, *f)


# ── 4. Крива Кінгмана: Експоненційний стрибок затримки при ρ → 1.0 ──────────────
def kingman_utilization_curve():
    W, H = 1120, 540
    f = []

    # Тло
    f.append(rect(20, 20, 1080, 500, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=8))
    f.append(text(560, 45, "Залежність часу очікування від утилізації ρ (Формула Кінгмана)", size=14, bold=True, color="#0f172a"))

    # Осі графіка
    f.append(line(100, 400, 1020, 400, color=LINE, sw=1.8))
    f.append(arrow(100, 400, 100, 70, color=LINE, sw=1.8))
    f.append(text(95, 75, "Середній час очікування в черзі W_q", size=11, color=MUTED, anchor="end", bold=True))
    f.append(text(1025, 415, "Коефіцієнт утилізації ресурсу ρ = λ / μ", size=11, color=MUTED, anchor="start", bold=True))

    # Зони стабільності та колапсу (написи вгорі)
    f.append(text(380, 105, "Зона стабільної роботи (Safe Zone: ρ ≤ 0.75)", size=11, bold=True, color="#166534"))
    f.append(text(380, 125, "Передбачувана затримка, лінійний відгук бекенду", size=10, color="#166534"))

    f.append(text(820, 105, "Зона колапсу (Danger Zone)", size=11, bold=True, color=POS))
    f.append(text(820, 125, "Експоненційний вибух затримки", size=10, color=POS))

    # Сітка утилізації
    for rho_val, x_pos in [("0.0", 100), ("0.2", 260), ("0.4", 420), ("0.6", 580), ("0.75", 700), ("1.0", 940)]:
        f.append(line(x_pos, 400, x_pos, 406, color=LINE, sw=1.5))
        f.append(text(x_pos, 420, rho_val, size=11, color=INK))

    # Асимптота при rho = 1.0
    f.append(line(940, 400, 940, 75, color=POS, sw=1.8, dash="5,4"))
    f.append(text(945, 90, "Асимптота ρ = 1.0 (W_q → ∞)", size=11, color=POS, bold=True, anchor="start"))

    # Межа безпеки при rho = 0.75
    f.append(line(700, 400, 700, 75, color=FIELD, sw=1.5, dash="4,4"))
    f.append(text(700, 70, "Межа ρ_safe = 0.75", size=10, color=FIELD, bold=True))

    # Крива Кінгмана W_q = (rho / (1 - rho)) * C
    curve_points = "100,400 180,398 260,392 340,384 420,372 500,355 580,330 660,290 700,250 760,195 820,130 870,80"
    f.append('<polyline points="' + curve_points + '" fill="none" stroke="#2563eb" stroke-width="3"/>')

    # Точка робочого режиму бекенду при демпфуванні (700, 250)
    f.append(circle(700, 250, 6, fill=FIELD, stroke="#ffffff", sw=2))
    f.append(fitbox(440, 215, 240, 52, "Робоча точка бекенду:\nρ = 0.75 (μ = 400 RPS)\nW_q бекенду суворо обмежений", size=10, fill="#ffffff", stroke=FIELD, bold=True))

    # Точка прямого сплеску без демпфування (870, 80)
    f.append(circle(870, 80, 6, fill=POS, stroke="#ffffff", sw=2))
    f.append(fitbox(730, 150, 250, 60, "Прямий сплеск без черги:\nρ > 1.0 → Переповнення пам'яті,\nпадіння сокетів, тайм-аути 504", size=10, fill="#ffffff", stroke=POS, bold=True))

    # Пояснення формули Кінгмана внизу
    f.append(fitbox(100, 445, 920, 45,
                     "Формула Кінгмана: W_q ≈ [ρ / (1 − ρ)] · [(c_a² + c_s²) / 2] · (1 / μ). "
                     "Демпфер черги ізолює бекенд, утримуючи ρ в безпечній зоні, та переносить очікування в еластичний буфер.",
                     size=10, fill="#f8fafc", stroke=LINE, sw=1))

    render(os.path.join(OUT, 'kingman-utilization-curve.svg'), W, H, *f)


if __name__ == '__main__':
    queue_load_leveling_dynamics()
    queue_load_leveling_architecture()
    direct_vs_leveled_failure()
    kingman_utilization_curve()
    print("Всі 4 фігури успішно згенеровано.")
