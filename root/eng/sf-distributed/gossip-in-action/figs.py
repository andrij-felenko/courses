# -*- coding: utf-8 -*-
import sys
import os

# Додаємо scripts до шляху імпорту (4 рівні вгору від теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_scuttlebutt():
    """3-фазний протокол Scuttlebutt (Syn-Ack-Ack2) між двома вузлами."""
    w, h = 840, 480
    frags = []

    # Колонка Вузол A і Вузол B
    frags.append(fitbox(70, 30, 180, 50, "Вузол A\n(Ініціатор раунду)", size=13, bold=True, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(590, 30, 180, 50, "Вузол B\n(Випадковий партнер)", size=13, bold=True, fill="#f4f6f8", stroke=LINE))

    # Вертикальні лінії життя (розміщені поза бічними боксами)
    frags.append(line(160, 85, 160, 410, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(680, 85, 680, 410, color=MUTED, sw=1.5, dash="4,4"))

    # Фаза 1: SYN
    frags.append(arrow(160, 140, 675, 140, color=NEG, sw=2))
    frags.append(textbox(420, 120, "1. GossipDigestSyn [Вузол: (Generation, MaxVersion)]", size=12, bold=True, fill="#ffffff", stroke=NEG)[0])
    frags.append(fitbox(15, 115, 135, 55, "Генерація дайджесту:\nверсії всіх відомих\nвузлів у пам'яті", size=10, fill="#ffffff", stroke=LINE))

    # Фаза 2: ACK
    frags.append(arrow(680, 230, 165, 230, color=POS, sw=2))
    frags.append(textbox(420, 210, "2. GossipDigestAck (нові стани для A + запит дельти для B)", size=12, bold=True, fill="#ffffff", stroke=POS)[0])
    frags.append(fitbox(695, 205, 135, 60, "Обчислення різниці:\nновіші стани → у дельту,\nстаріші → у запит", size=10, fill="#ffffff", stroke=LINE))

    # Фаза 3: ACK2
    frags.append(arrow(160, 320, 675, 320, color=FIELD, sw=2))
    frags.append(textbox(420, 300, "3. GossipDigestAck2 (залишкова дельта станів для B)", size=12, bold=True, fill="#ffffff", stroke=FIELD)[0])
    frags.append(fitbox(15, 295, 135, 60, "Оновлення станів A\nВідправка залишку\nдельти до вузла B", size=10, fill="#ffffff", stroke=LINE))

    # Підсумок
    frags.append(fitbox(695, 305, 135, 50, "Оновлення станів B\nПовна збіжність", size=10, fill="#ffffff", stroke=LINE))
    frags.append(fitbox(200, 420, 440, 40, "Результат: обидва вузли повністю узгодили стан за 1.5 RTT (3 кроки)", size=12, bold=True, fill="#e8f8f0", stroke=FIELD))

    render(os.path.join(IMG_DIR, "scuttlebutt-syn-ack2.svg"), w, h, *frags)


def fig_phi_accrual():
    """Крива Phi Accrual Failure Detector та порогові значення."""
    w, h = 820, 420
    frags = []

    # Осі координат
    frags.append(line(80, 340, 760, 340, color=LINE, sw=2))
    frags.append(line(80, 340, 80, 50, color=LINE, sw=2))
    frags.append(arrow(750, 340, 765, 340, color=LINE, sw=2))
    frags.append(arrow(80, 60, 80, 40, color=LINE, sw=2))

    # Підписи осей
    frags.append(text(720, 365, "Час від останнього пульсу t - t_last (с)", size=12, bold=True, anchor="end"))
    frags.append(text(75, 35, "Рівень підозри Φ", size=12, bold=True, anchor="start"))

    # Поділки на осі Y (Phi)
    for y_val, label in [(280, "Φ = 4"), (210, "Φ = 8"), (140, "Φ = 12"), (70, "Φ = 16")]:
        frags.append(line(75, y_val, 80, y_val, color=LINE, sw=1.5))
        frags.append(text(70, y_val + 4, label, size=11, anchor="end", color=MUTED))
        frags.append(line(80, y_val, 740, y_val, color="#e5e7eb", sw=1, dash="3,3"))

    # Поділки на осі X (Час)
    for x_val, label in [(160, "1с"), (260, "2с (μ)"), (380, "4с"), (500, "8с"), (640, "12с")]:
        frags.append(line(x_val, 340, x_val, 345, color=LINE, sw=1.5))
        frags.append(text(x_val, 360, label, size=11, anchor="middle", color=MUTED))

    # Порогова лінія Phi = 8
    frags.append(line(80, 210, 740, 210, color=POS, sw=1.8, dash="5,3"))
    frags.append(fitbox(530, 185, 220, 40, "Поріг за замовчуванням (Φ = 8)\nПомилка: 1 на 10⁸ випадків", size=10, bold=True, fill="#fff1f2", stroke=POS))

    # Порогова лінія Phi = 12
    frags.append(line(80, 140, 740, 140, color=NEG, sw=1.8, dash="5,3"))
    frags.append(fitbox(530, 115, 220, 40, "Рекомендовано для WAN (Φ = 12)\nПомилка: 1 на 10¹² випадків", size=10, bold=True, fill="#eff6ff", stroke=NEG))

    # Крива зростання Phi
    curve_path = (
        '<path d="M 120 338 Q 240 335 320 310 T 450 230 T 560 150 T 700 70" '
        'fill="none" stroke="#1e293b" stroke-width="3"/>'
    )
    frags.append(curve_path)

    frags.append(textbox(320, 260, "Φ = -log₁₀(P_later(t - t_last))", size=12, bold=True, fill="#ffffff", stroke=LINE)[0])

    render(os.path.join(IMG_DIR, "phi-accrual-curve.svg"), w, h, *frags)


def fig_consul_lifeguard():
    """Автомат станів Memberlist (Lifeguard SWIM) та непряме зондування."""
    w, h = 820, 420
    frags = []

    # Вузли станів
    frags.append(fitbox(70, 70, 160, 60, "Живий (Alive)\nIncarnation: i\nСтатус: Online", size=12, bold=True, fill="#f0fdf4", stroke=FIELD))
    frags.append(fitbox(430, 70, 180, 60, "Підозрюваний (Suspect)\nIncarnation: i\nТаймер: T_suspect(LWL)", size=12, bold=True, fill="#fefce8", stroke="#ca8a04"))
    frags.append(fitbox(650, 270, 140, 60, "Мертвий (Dead)\nTombstone період\nВидалення з кільця", size=12, bold=True, fill="#fef2f2", stroke=POS))
    frags.append(fitbox(70, 270, 160, 60, "Вибув (Left)\nПлановий вихід\nIncarnation: i + 1", size=12, bold=True, fill="#f8fafc", stroke=MUTED))

    # Переходи
    # Alive -> Suspect (Провал прямого пінгу + k непрямих ping-req)
    frags.append(arrow(230, 100, 425, 100, color=POS, sw=2))
    frags.append(textbox(330, 75, "Провал Direct Ping +\nk непрямих Ping-Req", size=10, bold=True, fill="#ffffff", stroke=POS)[0])

    # Suspect -> Dead (Таймер підозри вичерпано)
    frags.append(arrow(550, 130, 680, 265, color=POS, sw=2))
    frags.append(textbox(655, 185, "Таймер підозри сплив\n(без спростування)", size=10, bold=True, fill="#ffffff", stroke=POS)[0])

    # Suspect -> Alive (Спростування через Incarnation Number)
    frags.append(arrow(450, 130, 210, 130, color=FIELD, sw=2))
    frags.append(textbox(330, 155, "Спростування живим вузлом:\nAlive(Incarnation = i + 1)", size=10, bold=True, fill="#ffffff", stroke=FIELD)[0])

    # Alive -> Left (Graceful Leave)
    frags.append(arrow(150, 130, 150, 265, color=MUTED, sw=2))
    frags.append(textbox(205, 200, "Плановий вихід\n(Graceful Leave)", size=10, bold=True, fill="#ffffff", stroke=MUTED)[0])

    # Блок зворотного зв'язку Lifeguard (LWL)
    frags.append(fitbox(290, 250, 300, 130, "Розширення Lifeguard (LWL):\n• Моніторинг затримок планувальника ОС\n• Рахунок здоров'я H (Local Health Score)\n• Адаптивне збільшення T_suspect у H разів\n• Відкидання хибних підозр при GC-паузах", size=11, fill="#eff6ff", stroke=NEG))

    render(os.path.join(IMG_DIR, "consul-lifeguard-swim.svg"), w, h, *frags)


def fig_cassandra_targets():
    """Вибір цілей для раунду пліткування в Apache Cassandra."""
    w, h = 820, 440
    frags = []

    # Центральний вузол
    frags.append(fitbox(300, 30, 220, 50, "Вузол A (Gossiper раунд 1с)\nВибір партнерів для обміну", size=12, bold=True, fill="#eaf0fd", stroke=NEG))

    # Три гілки вибору
    # Гілка 1: Живий вузол
    frags.append(arrow(350, 80, 140, 175, color=FIELD, sw=2))
    frags.append(fitbox(40, 180, 200, 70, "1. Випадковий живий вузол\n(Ймовірність = 1.0)\nРівномірний вибір серед\nусіх активних учасників", size=11, fill="#f0fdf4", stroke=FIELD))

    # Гілка 2: Недоступний вузол
    frags.append(arrow(410, 80, 410, 175, color="#ca8a04", sw=2))
    frags.append(fitbox(310, 180, 200, 70, "2. Недоступний вузол\nЙмовірність P = unreach / (live + 1)\nСпроба виявити відновлення\nпісля збою", size=11, fill="#fefce8", stroke="#ca8a04"))

    # Гілка 3: Seed-вузол
    frags.append(arrow(470, 80, 680, 175, color=POS, sw=2))
    frags.append(fitbox(580, 180, 200, 70, "3. Seed-вузол (Якір)\nЙмовірність P = seeds / (live + unreach)\nАбо якщо A не бачить живих\nЗапобігання розколу кластера", size=11, fill="#fef2f2", stroke=POS))

    # Підсумковий блок: подолання ізоляції
    frags.append(fitbox(120, 310, 580, 95, "Гарантії архітектури вибору цілей:\n• Живі вузли поширюють метадані за O(log N) раундів\n• Недоступні вузли автоматично повертаються в кільце без ручного втручання\n• Seed-вузли зшивають ізольовані підмножини («острови пліток») після збоїв мережі", size=12, bold=True, fill="#f8fafc", stroke=LINE))

    render(os.path.join(IMG_DIR, "cassandra-target-selection.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_scuttlebutt()
    fig_phi_accrual()
    fig_consul_lifeguard()
    fig_cassandra_targets()
    print("Усі 4 фігури успішно згенеровано.")
