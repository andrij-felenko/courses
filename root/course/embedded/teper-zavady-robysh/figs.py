# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Тепер завади робиш ти: що саме випромінює твоя плата».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

COPPER = "#b9770e"   # мідь / земля — тепле
HOT    = "#c0392b"   # гаряча точка / високий dv/dt / di/dt
COLD   = "#2457d6"   # тихий сигнал / синфазний шум


# ── 1. Шляхи поширення: кондуктивні vs випромінювані завади ──────────────────
def fig_emi_mechanisms():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Шляхи поширення завад: кондуктивні та випромінювані", size=17, bold=True),
        text(W / 2, 50, "завада виникає всередині схеми і виходить назовні через спільні дроти (кондуктивно) або через ефір (випромінюванням)",
             size=11, color=MUTED, italic=True)
    ]

    # Ліва колонка: Кондуктивні завади (150 кГц – 30 МГц)
    x1, y1, w1, h1 = 50, 80, 400, 360
    f.append(rect(x1, y1, w1, h1, fill="#fcfcfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x1 + w1 / 2, y1 + 28, "КОНДУКТИВНІ ЗАВАДИ (150 кГц – 30 МГц)", size=12.5, color=INK, bold=True))
    f.append(text(x1 + w1 / 2, y1 + 46, "поширення провідниками, шинами живлення та кабелями", size=10, color=MUTED))

    # Джерело на платі
    f.append(rect(x1 + 30, y1 + 75, 110, 70, fill="#fdecea", stroke=HOT, sw=1.5, rx=6))
    f.append(text(x1 + 85, y1 + 105, "Джерело шуму", size=11, color=HOT, bold=True))
    f.append(text(x1 + 85, y1 + 125, "(DC-DC, ШІМ)", size=9.5, color=MUTED))

    # Лінії живлення
    f.append(line(x1 + 140, y1 + 95, x1 + 340, y1 + 95, color=POS, sw=2))
    f.append(text(x1 + 360, y1 + 99, "V+", size=10.5, color=POS, bold=True))

    f.append(line(x1 + 140, y1 + 130, x1 + 340, y1 + 130, color=COLD, sw=2))
    f.append(text(x1 + 360, y1 + 134, "GND", size=10.5, color=COLD, bold=True))

    # Диференціальний струм (стрілки в протилежні боки)
    f.append(arrow(x1 + 180, y1 + 85, x1 + 240, y1 + 85, color=POS, sw=1.8))
    f.append(arrow(x1 + 240, y1 + 140, x1 + 180, y1 + 140, color=COLD, sw=1.8))
    f.append(text(x1 + 210, y1 + 72, "Диференціальний шум (I_DM)", size=10, color=POS, bold=True))
    f.append(text(x1 + 210, y1 + 160, "струм тече по V+ і повертається по GND", size=9.5, color=MUTED))

    # Синфазний шум
    f.append(arrow(x1 + 180, y1 + 205, x1 + 260, y1 + 205, color=FIELD, sw=1.8))
    f.append(arrow(x1 + 180, y1 + 230, x1 + 260, y1 + 230, color=FIELD, sw=1.8))
    f.append(text(x1 + 210, y1 + 192, "Синфазний шум (I_CM)", size=10, color=FIELD, bold=True))
    f.append(text(x1 + 210, y1 + 252, "тече в один бік по обох провідниках", size=9.5, color=MUTED))
    f.append(text(x1 + 210, y1 + 268, "замикається через ємність до шасі / землі", size=9.5, color=MUTED))

    # Блок фільтрації внизу
    f.append(rect(x1 + 20, y1 + 295, w1 - 40, 50, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(x1 + w1 / 2, y1 + 314, "Лікування: LC-фільтри (DM) +", size=10.5, color=INK, bold=True))
    f.append(text(x1 + w1 / 2, y1 + 332, "синфазний дросель (CMC) та Y-конденсатори (CM)", size=10, color=MUTED))

    # Права колонка: Випромінювані завади (30 МГц – кілька ГГц)
    x2 = 490
    f.append(rect(x2, y1, w1, h1, fill="#fcfcfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x2 + w1 / 2, y1 + 28, "ВИПРОМІНЮВАНІ ЗАВАДИ (30 МГц – ГГц)", size=12.5, color=INK, bold=True))
    f.append(text(x2 + w1 / 2, y1 + 46, "поширення електромагнітними хвилями в ефір", size=10, color=MUTED))

    # Магнітна рамка (петля струму)
    f.append(rect(x2 + 30, y1 + 75, 150, 80, fill="#f6ecd6", stroke=COPPER, sw=1.8, rx=6))
    f.append(text(x2 + 105, y1 + 105, "Магнітна рамка", size=11, color=COPPER, bold=True))
    f.append(text(x2 + 105, y1 + 123, "петля з великим di/dt", size=9.5, color=INK))
    f.append(text(x2 + 105, y1 + 139, "випромінює H-поле", size=9.5, color=MUTED))

    # Хвилі H-поля
    for r in (20, 36, 52):
        f.append('<path d="M %d,%d A %d,%d 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="3,3"/>'
                 % (x2 + 195, y1 + 115 - r, r, r, x2 + 195, y1 + 115 + r, COPPER))
    f.append(text(x2 + 275, y1 + 118, "H-поле ~ f² · A · I", size=10.5, color=COPPER, bold=True))

    # Електричний диполь (кабель або switch node)
    f.append(rect(x2 + 30, y1 + 185, 150, 80, fill="#fdecea", stroke=HOT, sw=1.8, rx=6))
    f.append(text(x2 + 105, y1 + 215, "Електричний диполь", size=11, color=HOT, bold=True))
    f.append(text(x2 + 105, y1 + 233, "провідник з високим dv/dt", size=9.5, color=INK))
    f.append(text(x2 + 105, y1 + 249, "випромінює E-поле", size=9.5, color=MUTED))

    # Хвилі E-поля
    for r in (20, 36, 52):
        f.append('<path d="M %d,%d A %d,%d 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="1.5"/>'
                 % (x2 + 195, y1 + 225 - r, r, r, x2 + 195, y1 + 225 + r, HOT))
    f.append(text(x2 + 275, y1 + 228, "E-поле ~ f · L · I_cm", size=10.5, color=HOT, bold=True))

    # Блок лікування правої колонки
    f.append(rect(x2 + 20, y1 + 295, w1 - 40, 50, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(x2 + w1 / 2, y1 + 314, "Лікування: мінімізація площі петлі (A) +", size=10.5, color=INK, bold=True))
    f.append(text(x2 + w1 / 2, y1 + 332, "суцільна земля, ферити на кабелях, екранування", size=10, color=MUTED))

    return render(os.path.join(IMG, 'emi-mechanisms-overview.svg'), W, H, *f)


# ── 2. Анатомія DC-DC: високий dv/dt та високий di/dt ────────────────────────
def fig_dcdc_hot_loop():
    W, H = 940, 500
    f = [
        text(W / 2, 28, "Анатомія випромінювання DC-DC: де ховаються dv/dt та di/dt", size=17, bold=True),
        text(W / 2, 50, "два окремі джерела: комутаційний полігон випромінює електричне поле, а вхідна петля перемикання — магнітне",
             size=11, color=MUTED, italic=True)
    ]

    # Схема Buck-перетворювача
    # Вхідний конденсатор Cin
    cx, cy = 120, 240
    f.append(line(cx, cy - 80, cx, cy - 10, color=POS, sw=2))
    f.append(line(cx - 20, cy - 10, cx + 20, cy - 10, color=POS, sw=3))
    f.append(line(cx - 20, cy + 10, cx + 20, cy + 10, color=COLD, sw=3))
    f.append(line(cx, cy + 10, cx, cy + 80, color=COLD, sw=2))
    f.append(text(cx - 38, cy + 4, "C_in", size=12, color=INK, bold=True))

    # Верхній транзистор Q1
    q1x, q1y = 260, 160
    f.append(rect(q1x - 30, q1y - 25, 60, 50, fill="#fdecea", stroke=HOT, sw=2, rx=4))
    f.append(text(q1x, q1y + 4, "Q1 (Top)", size=10.5, color=HOT, bold=True))

    # Нижній транзистор Q2 (або діод)
    q2x, q2y = 260, 320
    f.append(rect(q2x - 30, q2y - 25, 60, 50, fill="#eaf0fd", stroke=COLD, sw=2, rx=4))
    f.append(text(q2x, q2y + 4, "Q2 (Bot)", size=10.5, color=COLD, bold=True))

    # З'єднання вхідної гарячої петлі (HOT LOOP)
    f.append(line(cx, cy - 80, q1x - 30, q1y, color=POS, sw=2.5))
    sw_x, sw_y = 370, 240
    f.append(line(q1x + 30, q1y, sw_x, sw_y, color=HOT, sw=2.5))
    f.append(line(sw_x, sw_y, q2x + 30, q2y, color=HOT, sw=2.5))
    f.append(line(q2x - 30, q2y, cx, cy + 80, color=COLD, sw=2.5))

    # Підсвітка гарячої петлі
    f.append('<polygon points="%d,%d %d,%d %d,%d %d,%d %d,%d" fill="#fdecea" opacity="0.45" stroke="%s" stroke-width="2" stroke-dasharray="4,4"/>'
             % (cx, cy - 80, q1x + 30, q1y, sw_x, sw_y, q2x + 30, q2y, cx, cy + 80, HOT))
    f.append(text(215, 235, "ГАРЯЧА ПЕТЛЯ (Hot Loop)", size=11, color=HOT, bold=True))
    f.append(text(215, 252, "розривний струм di/dt", size=10, color=HOT))
    f.append(text(215, 268, "МАЄ БУТИ МІНІМАЛЬНОЮ", size=9.5, color=INK, bold=True))

    # Дросель L1
    lx, ly = 490, 240
    f.append(line(sw_x, sw_y, lx - 40, ly, color=HOT, sw=2.5))
    f.append(rect(lx - 40, ly - 20, 80, 40, fill="#f6ecd6", stroke=COPPER, sw=2, rx=4))
    f.append(text(lx, ly + 4, "Дросель L1", size=11, color=COPPER, bold=True))

    # Вихідний конденсатор Cout і навантаження
    cout_x = 640
    f.append(line(lx + 40, ly, cout_x, ly, color=POS, sw=2))
    f.append(line(cout_x, ly, cout_x, cy - 60, color=POS, sw=2))
    f.append(line(cout_x - 20, cy - 60, cout_x + 20, cy - 60, color=POS, sw=3))
    f.append(line(cout_x - 20, cy - 40, cout_x + 20, cy - 40, color=COLD, sw=3))
    f.append(line(cout_x, cy - 40, cout_x, cy + 80, color=COLD, sw=2))
    f.append(line(cout_x, cy + 80, q2x - 30, q2y, color=COLD, sw=2))
    f.append(text(cout_x + 36, cy - 48, "C_out", size=11, color=INK, bold=True))

    # Вихід Vout
    f.append(line(cout_x, ly, cout_x + 100, ly, color=POS, sw=2))
    f.append(circle(cout_x + 100, ly, 4, fill=POS, stroke=POS, sw=0))
    f.append(text(cout_x + 115, ly + 4, "V_out (плавний струм)", size=10.5, color=POS, bold=True, anchor="start"))

    # Полігон Switch Node (високий dv/dt)
    f.append(circle(sw_x, sw_y, 6, fill=HOT, stroke=HOT, sw=0))
    f.append(rect(sw_x - 25, sw_y - 120, 150, 75, fill="#fff2f0", stroke=HOT, sw=1.5, rx=6))
    f.append(text(sw_x + 50, sw_y - 100, "Вузол SW (LX)", size=11, color=HOT, bold=True))
    f.append(text(sw_x + 50, sw_y - 82, "стрибки 0 В ↔ V_in за 1–3 нс", size=9.5, color=INK))
    f.append(text(sw_x + 50, sw_y - 66, "dv/dt = 10⁹ В/с (E-поле)", size=10, color=HOT, bold=True))
    f.append(arrow(sw_x + 50, sw_y - 45, sw_x + 10, sw_y - 10, color=HOT, sw=1.5))

    # Порівняльна плашка внизу
    f.append(rect(60, 410, 820, 65, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(240, 432, "1. Гаряча петля Cin-Q1-Q2 (di/dt)", size=11, color=HOT, bold=True))
    f.append(text(240, 455, "Розривний струм → петля як магнітна антена → стискати площу до нуля", size=9.5, color=MUTED))

    f.append(text(660, 432, "2. Комутаційний полігон SW (dv/dt)", size=11, color=HOT, bold=True))
    f.append(text(660, 455, "Стрибки напруги → ємнісна антена → мінімізувати площу міді SW-полігону", size=9.5, color=MUTED))

    return render(os.path.join(IMG, 'dcdc-hot-loop-dv-di.svg'), W, H, *f)


# ── 3. Спектр прямокутного імпульсу та кутова частота f_knee ─────────────────
def fig_fourier_spectrum():
    W, H = 940, 460
    f = [
        text(W / 2, 28, "Спектр цифрового сигналу: гармоніки та частота зламу f_knee", size=17, bold=True),
        text(W / 2, 50, "енергія гармонік спадає як -20 дБ/дек, а після частоти зламу f_knee = 1 / (π · t_r) — як -40 дБ/дек; крутий фронт тягне завади в гігагерци",
             size=11, color=MUTED, italic=True)
    ]

    ox, oy = 90, 380
    gw, gh = 780, 290

    # Осі графіка
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.8))
    f.append(text(ox + gw / 2, oy + 42, "Частота (логарифмічна шкала), Гц", size=11.5, color=INK, bold=True))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="11.5" fill="%s" font-weight="700" '
             'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">Амплітуда гармонік, дБ</text>'
             % (ox - 45, oy - gh / 2, FONT, INK, ox - 45, oy - gh / 2))

    f0_x = ox + 80
    f1_x = ox + 220
    fk_slow_x = ox + 420
    fk_fast_x = ox + 680

    f.append(line(f0_x, oy, f0_x, oy + 6, color=INK, sw=1.2))
    f.append(text(f0_x, oy + 22, "f₀ (10 МГц)", size=10, color=MUTED))

    f.append(line(f1_x, oy, f1_x, oy + 6, color=INK, sw=1.2))
    f.append(text(f1_x, oy + 22, "1/(π·t_w)", size=10, color=MUTED))

    f.append(line(fk_slow_x, oy, fk_slow_x, oy + 6, color=FIELD, sw=1.5))
    f.append(text(fk_slow_x, oy + 22, "f_knee (3 нс)", size=10, color=FIELD, bold=True))

    f.append(line(fk_fast_x, oy, fk_fast_x, oy + 6, color=HOT, sw=1.5))
    f.append(text(fk_fast_x, oy + 22, "f_knee (0.3 нс)", size=10, color=HOT, bold=True))

    # Спектральні лінії гармонік (дискретні палички)
    for x in range(f0_x, f1_x, 28):
        f.append(line(x, oy, x, oy - 240, color="#d0d5dd", sw=1.5))
    for x in range(f1_x, fk_slow_x - 50, 32):
        h_val = 240 - (x - f1_x) * 0.45
        f.append(line(x, oy, x, oy - h_val, color="#d0d5dd", sw=1.5))

    # Крива 1: Сповільнений фронт (t_r = 3 нс) -> спад -40 дБ/дек починається на 100 МГц (Зелена)
    p_slow = [
        (ox + 20, oy - 240),
        (f1_x, oy - 240),
        (fk_slow_x, oy - 150),
        (ox + gw - 40, oy - 15)
    ]
    pts1 = " ".join("%.1f,%.1f" % pt for pt in p_slow)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts1, FIELD))
    f.append(text(540, oy - 190, "Повільний фронт (3 нс): спад -40 дБ/дек", size=10.5, color=FIELD, bold=True, anchor="start"))

    # Крива 2: Крутий фронт (t_r = 0.3 нс) -> спад -40 дБ/дек починається аж на 1 ГГц (Червона)
    p_fast = [
        (ox + 20, oy - 240),
        (f1_x, oy - 240),
        (fk_slow_x, oy - 150),
        (fk_fast_x, oy - 50),
        (ox + gw - 10, oy - 10)
    ]
    pts2 = " ".join("%.1f,%.1f" % pt for pt in p_fast)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-dasharray="6,4"/>' % (pts2, HOT))
    f.append(text(620, oy - 130, "Крутий фронт (0.3 нс): шумить до ГГц", size=10.5, color=HOT, bold=True, anchor="start"))

    # Стрілка різниці (дельта завад)
    f.append(arrow(720, oy - 45, 720, oy - 95, color=HOT, sw=2))
    f.append(text(735, oy - 70, "Різниця 20–30 дБ!", size=10, color=HOT, bold=True, anchor="start"))

    # Пояснення нахилів у вільних місцях
    f.append(text(250, oy - 255, "поличка (f < f₁)", size=10, color=MUTED))
    f.append(text(420, oy - 110, "спад -20 дБ/дек (1/f)", size=10, color=MUTED))
    f.append(text(fk_slow_x + 130, oy - 25, "спад -40 дБ/дек (1/f²)", size=10, color=FIELD))

    return render(os.path.join(IMG, 'digital-signal-spectrum-fourier.svg'), W, H, *f)


# ── 4. Кабелі як дипольні антени (синфазне випромінювання) ────────────────────
def fig_cable_antenna():
    W, H = 940, 480
    f = [
        text(W / 2, 28, "Як дроти та шлейфи стають антенами: синфазний струм", size=17, bold=True),
        text(W / 2, 50, "падіння напруги на паразитному імпедансі землі плати виштовхує високочастотний струм на підключений кабель",
             size=11, color=MUTED, italic=True)
    ]

    # Друкована плата (PCB)
    pcb_x, pcb_y, pcb_w, pcb_h = 70, 110, 330, 280
    f.append(rect(pcb_x, pcb_y, pcb_w, pcb_h, fill="#fcfcfd", stroke=LINE, sw=2, rx=10))
    f.append(text(pcb_x + 20, pcb_y + 28, "ПЛАТА (PCB)", size=12, color=INK, bold=True, anchor="start"))

    # Шар землі плати з паразитною індуктивністю
    f.append(rect(pcb_x + 20, pcb_y + 200, pcb_w - 40, 45, fill="#f6ecd6", stroke=COPPER, sw=1.5, rx=4))
    f.append(text(pcb_x + 35, pcb_y + 228, "Опорна земля (GND plane)", size=10.5, color=COPPER, bold=True, anchor="start"))

    # Джерело швидкого перемикання на платі (МК або DC-DC)
    f.append(rect(pcb_x + 40, pcb_y + 60, 110, 60, fill="#fdecea", stroke=HOT, sw=1.5, rx=6))
    f.append(text(pcb_x + 95, pcb_y + 88, "Швидкий чіп", size=10.5, color=HOT, bold=True))
    f.append(text(pcb_x + 95, pcb_y + 104, "di/dt імпульси", size=9.5, color=INK))

    # Струм перемикання в землю
    f.append(arrow(pcb_x + 95, pcb_y + 120, pcb_x + 95, pcb_y + 195, color=HOT, sw=2))
    f.append(text(pcb_x + 105, pcb_y + 160, "i(t)", size=10, color=HOT, bold=True, anchor="start"))

    # Напруга Ground Bounce: V_cm = L * di/dt
    f.append(circle(pcb_x + 95, pcb_y + 222, 4, fill=HOT, stroke=HOT, sw=0))
    f.append(circle(pcb_x + pcb_w - 40, pcb_y + 222, 4, fill=HOT, stroke=HOT, sw=0))
    f.append(arrow(pcb_x + 105, pcb_y + 265, pcb_x + pcb_w - 50, pcb_y + 265, color=HOT, sw=1.8))
    f.append(text(pcb_x + 160, pcb_y + 285, "V_cm = L_gnd · (di/dt) (шум землі)", size=10, color=HOT, bold=True))

    # Роз'єм на краю плати (розміщений праворуч від контуру плати без накладання)
    conn_x = pcb_x + pcb_w
    conn_y = pcb_y + 160
    f.append(rect(conn_x, conn_y, 22, 70, fill="#333333", stroke=LINE, sw=1.5, rx=3))
    f.append(text(conn_x + 11, conn_y + 40, "Порт", size=9, color="#ffffff", bold=True))

    # Кабель, що йде від роз'єму назовні
    cable_x = conn_x + 22
    cable_len = 420
    f.append(line(cable_x, conn_y + 20, cable_x + cable_len, conn_y + 20, color=POS, sw=3))
    f.append(line(cable_x, conn_y + 50, cable_x + cable_len, conn_y + 50, color=COLD, sw=3))
    f.append(text(cable_x + cable_len / 2, conn_y + 8, "Кабель живлення / шлейф датчиків (~1 м)", size=11, color=INK, bold=True))

    # Синфазний струм по кабелю (I_cm)
    f.append(arrow(cable_x + 30, conn_y + 35, cable_x + 100, conn_y + 35, color=HOT, sw=2.5))
    f.append(arrow(cable_x + 120, conn_y + 35, cable_x + 190, conn_y + 35, color=HOT, sw=2.5))
    f.append(text(cable_x + 110, conn_y + 75, "Синфазний струм I_cm (достатньо 5–10 мкА!)", size=10, color=HOT, bold=True))

    # Випромінювання диполя вгору
    for r in (25, 45, 65):
        f.append('<path d="M %d,%d A %d,%d 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="1.8"/>'
                 % (cable_x + 270, conn_y + 20 - r, r, r, cable_x + 270 + 2 * r, conn_y + 20, HOT))
    f.append(text(cable_x + 310, conn_y - 65, "Випромінювання E-поля", size=10.5, color=HOT, bold=True))
    f.append(text(cable_x + 310, conn_y - 48, "(кабель діє як диполь)", size=9.5, color=MUTED))

    # Висновок внизу
    f.append(rect(70, 420, 800, 44, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    f.append(text(W / 2, 446, "Платі не треба бути великою: довгий зовнішній кабель стає ефективною антеною замість неї", size=11, color=INK, bold=True))

    return render(os.path.join(IMG, 'cable-common-mode-antenna.svg'), W, H, *f)


# ── 5. Інженерні правила розведення проти завад ───────────────────────────────
def fig_pcb_emi_rules():
    W, H = 940, 500
    f = [
        text(W / 2, 28, "Ключові топологічні правила мінімізації EMI на PCB", size=17, bold=True),
        text(W / 2, 50, "суцільний шар землі, мінімальні контури повернення струму та послідовне демпфування швидких ліній",
             size=11, color=MUTED, italic=True)
    ]

    col_w = 265
    col_h = 390
    y0 = 80

    # Правило 1: Суцільна земля без прорізів
    x1 = 45
    f.append(rect(x1, y0, col_w, col_h, fill="#fcfcfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x1 + col_w / 2, y0 + 26, "1. СУЦІЛЬНА ЗЕМЛЯ", size=12, color=INK, bold=True))
    f.append(text(x1 + col_w / 2, y0 + 44, "без щілин під швидкими лініями", size=10, color=MUTED))

    # Схема сигнальної доріжки над суцільною землею
    f.append(rect(x1 + 20, y0 + 75, col_w - 40, 85, fill="#f6ecd6", stroke=COPPER, sw=1.5, rx=4))
    f.append(text(x1 + col_w / 2, y0 + 95, "Суцільний Ground Plane", size=10, color=COPPER, bold=True))
    f.append(line(x1 + 35, y0 + 130, x1 + col_w - 35, y0 + 130, color=POS, sw=2.5))
    f.append(text(x1 + col_w / 2, y0 + 120, "Сигнал (прямий струм)", size=9.5, color=POS))
    f.append(line(x1 + 35, y0 + 145, x1 + col_w - 35, y0 + 145, color=COPPER, sw=2.5, dash="3,3"))
    f.append(text(x1 + col_w / 2, y0 + 155, "Зворотний струм прямо під ним", size=9.5, color=COPPER))

    f.append(text(x1 + col_w / 2, y0 + 185, "Чому це працює:", size=10.5, color=INK, bold=True))
    f.append(text(x1 + 20, y0 + 208, "• На високій частоті струм тече", size=9.5, color=INK, anchor="start"))
    f.append(text(x1 + 20, y0 + 226, "  шляхом найменшої індуктивності", size=9.5, color=INK, anchor="start"))
    f.append(text(x1 + 20, y0 + 248, "• Площа петлі A → 0", size=9.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(x1 + 20, y0 + 270, "• Щілина в землі змушує струм", size=9.5, color=HOT, anchor="start"))
    f.append(text(x1 + 20, y0 + 288, "  робити гак → створює рамку EMI!", size=9.5, color=HOT, bold=True, anchor="start"))

    f.append(rect(x1 + 15, y0 + 320, col_w - 30, 50, fill="#eaf6ec", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(x1 + col_w / 2, y0 + 342, "Правило:", size=10.5, color=FIELD, bold=True))
    f.append(text(x1 + col_w / 2, y0 + 358, "Жодних розрізів під сигналами", size=9.5, color=INK))

    # Правило 2: Компактна гаряча петля
    x2 = 335
    f.append(rect(x2, y0, col_w, col_h, fill="#fcfcfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x2 + col_w / 2, y0 + 26, "2. КОМПАКТНА ПЕТЛЯ", size=12, color=INK, bold=True))
    f.append(text(x2 + col_w / 2, y0 + 44, "вхідний конденсатор впритул до МС", size=10, color=MUTED))

    # Схема правильного розміщення Cin
    f.append(rect(x2 + 25, y0 + 75, 85, 80, fill="#fdecea", stroke=HOT, sw=1.5, rx=4))
    f.append(text(x2 + 67, y0 + 110, "DC-DC", size=10.5, color=HOT, bold=True))
    f.append(text(x2 + 67, y0 + 126, "чіп", size=9.5, color=HOT))

    f.append(rect(x2 + 140, y0 + 85, 45, 60, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=3))
    f.append(text(x2 + 162, y0 + 118, "C_in", size=10, color=INK, bold=True))

    f.append(line(x2 + 110, y0 + 95, x2 + 140, y0 + 95, color=POS, sw=3))
    f.append(line(x2 + 110, y0 + 135, x2 + 140, y0 + 135, color=COLD, sw=3))

    f.append(text(x2 + col_w / 2, y0 + 185, "Чому це працює:", size=10.5, color=INK, bold=True))
    f.append(text(x2 + 20, y0 + 208, "• Керамічний Cin на тому ж шарі", size=9.5, color=INK, anchor="start"))
    f.append(text(x2 + 20, y0 + 226, "• Прямий контакт без перехідних", size=9.5, color=INK, anchor="start"))
    f.append(text(x2 + 20, y0 + 248, "• Мінімізує індуктивність L_loop", size=9.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(x2 + 20, y0 + 270, "• Прибирає дзвін на ключах", size=9.5, color=INK, anchor="start"))
    f.append(text(x2 + 20, y0 + 288, "• Знижує випромінювання на 15 дБ", size=9.5, color=FIELD, bold=True, anchor="start"))

    f.append(rect(x2 + 15, y0 + 320, col_w - 30, 50, fill="#eaf6ec", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(x2 + col_w / 2, y0 + 342, "Правило:", size=10.5, color=FIELD, bold=True))
    f.append(text(x2 + col_w / 2, y0 + 358, "Cin за 1–2 мм від виводів чіпа", size=9.5, color=INK))

    # Правило 3: Демпфуючі резистори та фронти
    x3 = 625
    f.append(rect(x3, y0, col_w, col_h, fill="#fcfcfd", stroke=LINE, sw=1.5, rx=8))
    f.append(text(x3 + col_w / 2, y0 + 26, "3. ДЕМПФУВАННЯ ЛІНІЙ", size=12, color=INK, bold=True))
    f.append(text(x3 + col_w / 2, y0 + 44, "послідовні резистори 22–47 Ом", size=10, color=MUTED))

    # Схема драйвер -> R_series -> приймач
    f.append(rect(x3 + 20, y0 + 85, 55, 60, fill="#eaf0fd", stroke=COLD, sw=1.5, rx=4))
    f.append(text(x3 + 47, y0 + 118, "MCU", size=10, color=COLD, bold=True))

    f.append(rect(x3 + 95, y0 + 105, 45, 22, fill="#f6ecd6", stroke=COPPER, sw=1.5, rx=3))
    f.append(text(x3 + 117, y0 + 120, "22–33Ω", size=9.5, color=COPPER, bold=True))

    f.append(line(x3 + 75, y0 + 116, x3 + 95, y0 + 116, color=POS, sw=2))
    f.append(line(x3 + 140, y0 + 116, x3 + 200, y0 + 116, color=POS, sw=2))

    f.append(rect(x3 + 200, y0 + 85, 45, 60, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    f.append(text(x3 + 222, y0 + 118, "IC", size=10, color=INK, bold=True))

    f.append(text(x3 + col_w / 2, y0 + 185, "Чому це працює:", size=10.5, color=INK, bold=True))
    f.append(text(x3 + 20, y0 + 208, "• Збільшує час наростання t_r", size=9.5, color=INK, anchor="start"))
    f.append(text(x3 + 20, y0 + 226, "• Зсуває f_knee вліво по осі f", size=9.5, color=FIELD, bold=True, anchor="start"))
    f.append(text(x3 + 20, y0 + 248, "• Пригнічує високочастотний дзвін", size=9.5, color=INK, anchor="start"))
    f.append(text(x3 + 20, y0 + 270, "• Узгоджує вихід із лінією 50 Ом", size=9.5, color=INK, anchor="start"))
    f.append(text(x3 + 20, y0 + 288, "• Не впливає на логіку 10–50 МГц", size=9.5, color=FIELD, bold=True, anchor="start"))

    f.append(rect(x3 + 15, y0 + 320, col_w - 30, 50, fill="#eaf6ec", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(x3 + col_w / 2, y0 + 342, "Правило:", size=10.5, color=FIELD, bold=True))
    f.append(text(x3 + col_w / 2, y0 + 358, "R_series біля піна передавача", size=9.5, color=INK))

    return render(os.path.join(IMG, 'pcb-layout-emi-rules.svg'), W, H, *f)


if __name__ == '__main__':
    fig_emi_mechanisms()
    fig_dcdc_hot_loop()
    fig_fourier_spectrum()
    fig_cable_antenna()
    fig_pcb_emi_rules()
    print('OK: emi-mechanisms-overview, dcdc-hot-loop-dv-di, digital-signal-spectrum-fourier, cable-common-mode-antenna, pcb-layout-emi-rules')
