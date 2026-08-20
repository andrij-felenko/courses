# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=11, pad=8, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Бінарний таймаут проти накопичувальної шкали Phi Accrual ───────
def fig_binary_vs_accrual():
    W, H = 1000, 480
    frags = []

    frags.append(text(500, 26, "Бінарний таймаут проти шкали підозри Phi Accrual", size=15, bold=True))

    # Ліва колонка: Традиційний бінарний таймаут
    frags.append(rect(25, 50, 455, 410, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(252, 76, "Традиційний бінарний детектор (Hard Timeout)", size=12, bold=True, color=POS))

    frags.append(box(252, 130, "Вхідний потік сигналів пульсу (Heartbeat)\nПеріод T = 1.0 с, випадковий джиттер мережі", size=10, fill="#ffffff", stroke=MUTED, min_w=390))
    frags.append(arrow(252, 165, 252, 195, color=MUTED, sw=1.5))

    frags.append(box(252, 230, "Жорсткий таймаут: t_diff > 3.0 c ?\nБінарний поріг «Все або нічого»\nНе враховує історію дисперсії затримок", size=10, bold=True, fill="#fff5f5", stroke=POS, min_w=390))
    
    frags.append(arrow(160, 275, 120, 315, color=FIELD, sw=1.5))
    frags.append(text(120, 295, "t_diff ≤ 3.0 c", size=9, color=FIELD, bold=True))
    frags.append(box(120, 355, "Статус: UP\nВузол здоровий\n(100% трафіку)", size=9, fill="#eafaf0", stroke=FIELD, min_w=160))

    frags.append(arrow(340, 275, 380, 315, color=POS, sw=1.5))
    frags.append(text(380, 295, "t_diff > 3.0 c", size=9, color=POS, bold=True))
    frags.append(box(380, 355, "Статус: DEAD\nПримусовий Failover\nПеревибори лідера", size=9, fill="#fdecea", stroke=POS, min_w=180))

    frags.append(rect(35, 410, 435, 40, fill="#fff8e1", stroke="#e67e22", sw=1, rx=4))
    frags.append(text(252, 434, "Хибна тривога під час сплеску GC → каскадний колапс кластера", size=9, color="#b7791f", bold=True))

    # Права колонка: Детектор Phi Accrual
    frags.append(rect(515, 50, 460, 410, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(745, 76, "Адаптивний детектор Phi Accrual (Hayashibara)", size=12, bold=True, color=FIELD))

    frags.append(box(745, 120, "Ковзне вікно інтервалів Δt (W = 1000)\nДинамічний розрахунок середнього μ та дисперсії σ²", size=9, fill="#ffffff", stroke=MUTED, min_w=410))
    frags.append(arrow(745, 150, 745, 175, color=MUTED, sw=1.5))

    frags.append(box(745, 205, "Неперервна шкала підозри:\nΦ = −log10(P_later(t_diff))\nВідокремлення оцінки від реакції системи", size=9, bold=True, fill="#e8f0ff", stroke=NEG, min_w=410))

    frags.append(arrow(745, 240, 745, 265, color=FIELD, sw=1.5))

    # Градація реакцій
    frags.append(box(745, 285, "Φ ≥ 2..3 (P ≤ 10⁻³): Хеджування запитів / резервний маршрут", size=9, fill="#eafaf0", stroke=FIELD, min_w=410))
    frags.append(box(745, 330, "Φ ≥ 8 (P ≤ 10⁻⁸): Gossip-підозра / накопичення Hinted Handoff", size=9, fill="#fff8e1", stroke="#e67e22", min_w=410))
    frags.append(box(745, 375, "Φ ≥ 12 (P ≤ 10⁻¹²): Виключення з кільця реплікації / рестарт", size=9, fill="#fdecea", stroke=POS, min_w=410))

    frags.append(rect(525, 410, 440, 40, fill="#eafaf0", stroke=FIELD, sw=1, rx=4))
    frags.append(text(745, 434, "Гнучкі багаторівневі дії залежно від ціни та зворотності помилки", size=9, color=FIELD, bold=True))

    return render(os.path.join(IMG, 'binary-vs-accrual-concept.svg'), W, H, *frags)


# ── Фігура 2: Гаусовий розподіл затримок, хвіст і метрика Phi ───────────────
def fig_gaussian_tail_phi():
    W, H = 960, 460
    frags = []

    frags.append(text(480, 26, "Статистична модель: інтеграл хвоста затримок та логарифмічна шкала Phi", size=15, bold=True))

    # Координатна сітка для дзвона Гауса
    ox, oy = 80, 340
    gw, gh = 420, 240

    # Вісь X та Y
    frags.append(arrow(ox, oy, ox + gw + 40, oy, color=LINE, sw=1.5))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.5))
    frags.append(text(ox + gw + 20, oy + 22, "Час очікування t_diff (с)", size=10, bold=True))
    frags.append(text(ox - 30, oy - gh, "Густина f(t)", size=10, bold=True, anchor="start"))

    # Крива Гауса: вершина в mu = 220, sigma = 50
    # y = oy - A * exp(-(x - mu)^2 / (2 * sigma^2))
    mu_x = 220
    sigma_px = 55
    peak_h = 200

    import math
    points = []
    for x_val in range(80, 480, 5):
        z = (x_val - mu_x) / sigma_px
        y_val = oy - peak_h * math.exp(-0.5 * z * z)
        points.append((x_val, y_val))

    path_d = ["M %.1f %.1f" % points[0]]
    for pt in points[1:]:
        path_d.append("L %.1f %.1f" % pt)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_d), NEG))

    # Зафарбований хвіст для t_diff = 330 (приблизно mu + 2*sigma)
    t_diff_x = 330
    tail_pts = [(t_diff_x, oy)]
    for pt in points:
        if pt[0] >= t_diff_x:
            tail_pts.append(pt)
    tail_pts.append((points[-1][0], oy))
    tail_d = ["M %.1f %.1f" % tail_pts[0]]
    for pt in tail_pts[1:]:
        tail_d.append("L %.1f %.1f" % pt)
    tail_d.append("Z")
    frags.append('<path d="%s" fill="#fdecea" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>' % (" ".join(tail_d), POS))

    # Позначки математичного сподівання mu
    frags.append(line(mu_x, oy, mu_x, oy - peak_h, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(circle(mu_x, oy, 3, fill=INK, stroke=INK))
    frags.append(text(mu_x, oy + 18, "μ (1.0 с)", size=10, bold=True))

    # Позначка mu + sigma
    frags.append(line(mu_x + sigma_px, oy, mu_x + sigma_px, oy - 120, color=MUTED, sw=1, dash="2,2"))
    frags.append(text(mu_x + sigma_px, oy + 18, "μ+σ", size=9, color=MUTED))

    # Позначка t_diff
    frags.append(line(t_diff_x, oy, t_diff_x, oy - 55, color=POS, sw=1.5))
    frags.append(circle(t_diff_x, oy, 4, fill=POS, stroke=POS))
    frags.append(text(t_diff_x, oy + 18, "t_diff", size=10, bold=True, color=POS))

    # Підпис площі хвоста
    frags.append(arrow(390, oy - 90, 360, oy - 25, color=POS, sw=1.2))
    frags.append(box(400, oy - 110, "P_later(t_diff) = ∫ f(t) dt\nЙмовірність того, що сигнал\nзатримається на час ≥ t_diff", size=9, fill="#ffffff", stroke=POS, min_w=170))

    # Права панель: Формула та співвідношення Phi
    frags.append(rect(560, 50, 375, 380, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(747, 76, "Логарифмічна інтерпретація шкали Φ", size=12, bold=True, color=NEG))

    frags.append(box(747, 130, "Формула Хаясібари:\nΦ = −log10(P_later(t_diff))\nде P_later = (1/2) · erfc((t_diff − μ) / (σ√2))", size=9, bold=True, fill="#e8f0ff", stroke=NEG, min_w=340))

    # Таблиця значень Phi
    frags.append(rect(575, 185, 345, 175, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    
    frags.append(text(620, 205, "Рівень Φ", size=9, bold=True, color=INK))
    frags.append(text(700, 205, "P_later", size=9, bold=True, color=INK))
    frags.append(text(810, 205, "Частота помилок (при T=1с)", size=9, bold=True, color=INK))
    frags.append(line(575, 215, 920, 215, color=MUTED, sw=1))

    rows = [
        ("Φ = 1", "10⁻¹ (10%)", "1 раз на 10 секунд"),
        ("Φ = 2", "10⁻² (1%)", "1 раз на 1.6 хвилини"),
        ("Φ = 4", "10⁻⁴ (0.01%)", "1 раз на 2.7 години"),
        ("Φ = 8", "10⁻⁸ (10⁻⁶ %)", "1 раз на 3.17 року (Cassandra)"),
        ("Φ = 12", "10⁻¹²", "1 раз на 31 000 років (Akka)"),
    ]
    for i, (r_phi, r_p, r_err) in enumerate(rows):
        ry = 235 + i * 24
        frags.append(text(620, ry, r_phi, size=9, bold=True, color=POS if i >= 3 else INK))
        frags.append(text(700, ry, r_p, size=9, color=INK))
        frags.append(text(810, ry, r_err, size=9, color=MUTED))

    frags.append(rect(575, 375, 345, 45, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    frags.append(text(747, 400, "Кожна одиниця збільшення Φ зменшує помилки в 10 разів", size=9, bold=True, color=FIELD))

    return render(os.path.join(IMG, 'gaussian-tail-phi-curve.svg'), W, H, *frags)


# ── Фігура 3: Архітектура Phi Accrual у розподіленому кластері ──────────────
def fig_cassandra_gossip_phi():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 26, "Архітектура Phi Accrual у вузлі кластера (Cassandra / Akka)", size=15, bold=True))

    # Секція 1: Джерело сигналів (Віддалений вузол)
    frags.append(rect(25, 55, 230, 420, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(140, 82, "Віддалений вузол (Node B)", size=12, bold=True, color=NEG))

    frags.append(box(140, 140, "Періодичний генератор пульсу\nGossip Heartbeat / UDP / TCP\nІнтервал відправки: T = 1.0 с", size=9, fill="#ffffff", stroke=MUTED, min_w=200))
    frags.append(arrow(140, 185, 140, 225, color=MUTED, sw=1.5))
    frags.append(box(140, 270, "Ненадійна мережа WAN / LAN\nЗмінні черги комутаторів\nДжиттер затримок: 1..250 мс\nВтрати та дублювання пакетів", size=9, fill="#fff8e1", stroke="#e67e22", min_w=200))

    frags.append(arrow(240, 270, 310, 270, color=NEG, sw=2))

    # Секція 2: Локальний детектор відмов (Node A)
    frags.append(rect(295, 55, 395, 420, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(492, 82, "Детектор відмов на вузлі-спостерігачі (Node A)", size=12, bold=True, color=FIELD))

    frags.append(box(492, 135, "Отримання Heartbeat-пакета:\nФіксація точного локального часу t_now\nРозрахунок інтервалу: Δt = t_now − t_last", size=9, fill="#eafaf0", stroke=FIELD, min_w=350))

    frags.append(arrow(492, 175, 492, 205, color=FIELD, sw=1.5))

    frags.append(box(492, 250, "Ковзне вікно інтервалів (ArrivalWindow)\nРозмір: W = 1000 елементів\nІтеративне оновлення: сума Δt та сума (Δt)²\nВибіркове середнє μ та дисперсія σ²", size=9, fill="#ffffff", stroke=MUTED, min_w=350))

    frags.append(arrow(492, 295, 492, 325, color=FIELD, sw=1.5))

    frags.append(box(492, 375, "Калькулятор підозри Phi:\nВхід: t_diff = t_now − t_last\nЙмовірність: P_later(t_diff) через erfc()\nВихід: значення Φ у просторі [0, +∞)", size=9, bold=True, fill="#e8f0ff", stroke=NEG, min_w=350))

    frags.append(arrow(675, 375, 735, 375, color=POS, sw=2))

    # Секція 3: Прикладні підсистеми та диференційована реакція
    frags.append(rect(720, 55, 255, 420, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(847, 82, "Прикладні дії підсистем", size=12, bold=True, color=POS))

    frags.append(box(847, 140, "Динамічний маршрутизатор:\nПри Φ > 3 надсилати запити\nчитання до інших реплік", size=9, fill="#eafaf0", stroke=FIELD, min_w=225))
    
    frags.append(box(847, 230, "Менеджер мутацій Cassandra:\nПри Φ > 8 зберігати локальні\nHinted Handoff замість помилок", size=9, fill="#fff8e1", stroke="#e67e22", min_w=225))

    frags.append(box(847, 320, "Gossip & Membership:\nПри Φ > 12 оголосити DOWN,\nініціювати вибори координатора", size=9, fill="#fdecea", stroke=POS, min_w=225))

    frags.append(rect(730, 390, 235, 65, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(847, 415, [
        "Кожна підсистема обирає",
        "власний поріг Φ залежно",
        "від ціни хибного рішення."
    ], size=9, color=INK))

    return render(os.path.join(IMG, 'cassandra-gossip-phi-architecture.svg'), W, H, *frags)


# ── Фігура 4: Динамічна адаптація вікна до зміни джиттеру мережі ────────────
def fig_adaptive_variance_shift():
    W, H = 980, 460
    frags = []

    frags.append(text(490, 26, "Динамічна самоадаптація: реакція детектора на зміну мережевого джиттеру", size=15, bold=True))

    # Графік 1: Спокійний режим (LAN / низький джиттер)
    frags.append(rect(25, 55, 450, 390, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(250, 82, "1. Стабільна мережа LAN (Низький джиттер)", size=12, bold=True, color=FIELD))

    # Маленький графік нормального розподілу (вузький дзвін)
    ox1, oy1 = 65, 270
    frags.append(arrow(ox1, oy1, ox1 + 370, oy1, color=LINE, sw=1.2))
    frags.append(arrow(ox1, oy1, ox1, oy1 - 160, color=LINE, sw=1.2))
    frags.append(text(ox1 + 350, oy1 + 18, "t_diff (с)", size=9))
    frags.append(text(ox1 - 15, oy1 - 145, "f(t)", size=9, anchor="start"))

    # Вузький дзвін: mu = 180, sigma = 25
    mu1 = 180
    sig1 = 25
    import math
    pts1 = []
    for x in range(ox1 + 10, ox1 + 360, 4):
        z = (x - mu1) / sig1
        y = oy1 - 140 * math.exp(-0.5 * z * z)
        pts1.append((x, y))
    d1 = ["M %.1f %.1f" % pts1[0]] + ["L %.1f %.1f" % p for p in pts1[1:]]
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(d1), FIELD))

    # Позначка mu та порогу Phi=8
    frags.append(line(mu1, oy1, mu1, oy1 - 140, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(mu1, oy1 + 16, "μ = 1.0 с", size=9, bold=True))

    th1_x = mu1 + int(sig1 * 3.5)
    frags.append(line(th1_x, oy1, th1_x, oy1 - 40, color=POS, sw=1.5))
    frags.append(text(th1_x + 30, oy1 - 45, "Поріг Φ=8 (1.4 с)", size=9, bold=True, color=POS))

    frags.append(rect(40, 305, 420, 125, fill="#f0fff4", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(250, 325, [
        "Параметри: μ = 1.0 с, σ = 0.05 с (джиттер мінімальний)",
        "Поріг Φ = 8 досягається вже через 1.4 секунди затримки.",
        "Результат: надшвидке виявлення реальної аварії вузла",
        "без будь-якого ризику помилкових спрацьовувань."
    ], size=9, color=INK))

    # Графік 2: Навантажена мережа WAN (Високий джиттер)
    frags.append(rect(505, 55, 450, 390, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(730, 82, "2. Хмарне перевантаження WAN (Високий джиттер)", size=12, bold=True, color=POS))

    # Широкий дзвін: mu = 660, sigma = 60
    ox2, oy2 = 545, 270
    frags.append(arrow(ox2, oy2, ox2 + 370, oy2, color=LINE, sw=1.2))
    frags.append(arrow(ox2, oy2, ox2, oy2 - 160, color=LINE, sw=1.2))
    frags.append(text(ox2 + 350, oy2 + 18, "t_diff (с)", size=9))
    frags.append(text(ox2 - 15, oy2 - 145, "f(t)", size=9, anchor="start"))

    mu2 = 660
    sig2 = 55
    pts2 = []
    for x in range(ox2 + 10, ox2 + 360, 4):
        z = (x - mu2) / sig2
        y = oy2 - 80 * math.exp(-0.5 * z * z)
        pts2.append((x, y))
    d2 = ["M %.1f %.1f" % pts2[0]] + ["L %.1f %.1f" % p for p in pts2[1:]]
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(d2), POS))

    # Позначка mu та порогу Phi=8
    frags.append(line(mu2, oy2, mu2, oy2 - 80, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(mu2, oy2 + 16, "μ = 1.0 с", size=9, bold=True))

    th2_x = mu2 + int(sig2 * 3.5)
    frags.append(line(th2_x, oy2, th2_x, oy2 - 40, color=POS, sw=1.5))
    frags.append(text(th2_x + 15, oy2 - 45, "Поріг Φ=8 (3.8 с)", size=9, bold=True, color=POS))

    frags.append(rect(520, 305, 420, 125, fill="#fff5f5", stroke=POS, sw=1, rx=4))
    frags.append(mtext(730, 325, [
        "Параметри: μ = 1.0 с, σ = 0.45 с (мережевий шторм / GC)",
        "Дисперсія σ зросла → вікно очікування автоматично розширилося.",
        "Поріг Φ = 8 автоматично зсунувся до 3.8 секунди.",
        "Результат: нуль хибних відключень здорових серверів під навантаженням."
    ], size=9, color=INK))

    return render(os.path.join(IMG, 'adaptive-variance-shift.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_binary_vs_accrual()
    fig_gaussian_tail_phi()
    fig_cassandra_gossip_phi()
    fig_adaptive_variance_shift()
    print("All figures generated successfully.")
