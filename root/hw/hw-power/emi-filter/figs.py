# -*- coding: utf-8 -*-
"""Фігури до теми «ЕМС-фільтр мережі живлення»."""
import sys, os, math

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

# ── 1. Джерела та шляхи завад: CM проти DM ──────────────────────────────────
def fig_cm_dm_noise_sources():
    W, H = 880, 460
    frags = []
    frags.append(text(W / 2, 26, "Генезис та контури поширення завад в імпульсному перетворювачі", size=16, bold=True))

    # Ліва панель: Диференціальна завада (DM)
    w_p = 405
    x1 = 25
    frags.append(rect(x1, 55, w_p, 385, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(x1 + w_p / 2, 80, "Диференціальна завада (DM): контур dI/dt", size=14, color=POS, bold=True))
    frags.append(text(x1 + w_p / 2, 100, "Струм тече в протилежних напрямках через L та N", size=11, color=MUTED))

    # Схема DM
    # Шини L і N
    frags.append(line(x1 + 30, 140, x1 + 375, 140, color=LINE, sw=2))
    frags.append(line(x1 + 30, 260, x1 + 375, 260, color=LINE, sw=2))
    frags.append(text(x1 + 20, 144, "L", size=13, bold=True))
    frags.append(text(x1 + 20, 264, "N", size=13, bold=True))

    # Вхідна ємність
    frags.append(line(x1 + 130, 140, x1 + 130, 190, color=LINE, sw=1.5))
    frags.append(line(x1 + 130, 210, x1 + 130, 260, color=LINE, sw=1.5))
    frags.append(line(x1 + 115, 190, x1 + 145, 190, color=LINE, sw=2.5))
    frags.append(line(x1 + 115, 210, x1 + 145, 210, color=LINE, sw=2.5))
    frags.append(text(x1 + 160, 204, "C_in", size=12, bold=True))

    # Силовий транзистор і діод
    frags.append(rect(x1 + 240, 125, 50, 30, fill="#f1f5f9", stroke=POS, sw=1.5))
    frags.append(text(x1 + 265, 145, "SW", size=11, bold=True, color=POS))

    frags.append(line(x1 + 330, 140, x1 + 330, 260, color=LINE, sw=1.5))
    frags.append(circle(x1 + 330, 200, 14, fill="#f1f5f9", stroke=LINE, sw=1.5))
    frags.append(text(x1 + 330, 204, "D", size=11, bold=True))

    # Червоний замкнений контур струму завади i_DM
    frags.append(arrow(x1 + 60, 125, x1 + 160, 125, color=POS, sw=2))
    frags.append(arrow(x1 + 200, 125, x1 + 290, 125, color=POS, sw=2))
    frags.append(arrow(x1 + 260, 275, x1 + 160, 275, color=POS, sw=2))
    frags.append(arrow(x1 + 130, 275, x1 + 60, 275, color=POS, sw=2))
    frags.append(text(x1 + 180, 115, "i_DM (прямий струм)", size=11, color=POS, bold=True))
    frags.append(text(x1 + 180, 295, "i_DM (зворотний струм)", size=11, color=POS, bold=True))

    box1, _, _ = textbox(x1 + w_p / 2, 365,
                         "Джерело: розривний струм комутації dI/dt\n"
                         "Шлях: шина L → ключ SW → навантаження → шина N\n"
                         "Пригнічення: X-конденсатори, індуктивність розсіювання",
                         size=11, pad=8, fill="#fff5f5", stroke=POS)
    frags.append(box1)

    # Права панель: Синфазна завада (CM)
    x2 = 450
    frags.append(rect(x2, 55, w_p, 385, fill="#fdfefe", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(x2 + w_p / 2, 80, "Синфазна завада (CM): струм зміщення dV/dt", size=14, color=NEG, bold=True))
    frags.append(text(x2 + w_p / 2, 100, "Струм тече синхронно через L та N у землю PE", size=11, color=MUTED))

    # Схема CM
    frags.append(line(x2 + 30, 140, x2 + 375, 140, color=LINE, sw=2))
    frags.append(line(x2 + 30, 220, x2 + 375, 220, color=LINE, sw=2))
    frags.append(text(x2 + 20, 144, "L", size=13, bold=True))
    frags.append(text(x2 + 20, 224, "N", size=13, bold=True))

    # Вузол комутації (SW node) з радіатором
    frags.append(rect(x2 + 220, 125, 60, 30, fill="#f1f5f9", stroke=NEG, sw=1.5))
    frags.append(text(x2 + 250, 145, "SW node", size=11, bold=True, color=NEG))

    # Паразитна ємність C_para до корпусу/землі
    frags.append(line(x2 + 250, 155, x2 + 250, 185, color=NEG, sw=1.5, dash="3,3"))
    frags.append(line(x2 + 235, 185, x2 + 265, 185, color=NEG, sw=2))
    frags.append(line(x2 + 235, 195, x2 + 265, 195, color=NEG, sw=2))
    frags.append(line(x2 + 250, 195, x2 + 250, 270, color=NEG, sw=1.5, dash="3,3"))
    frags.append(text(x2 + 305, 192, "C_para (радіатор)", size=11, color=NEG, bold=True))

    # Захисне заземлення PE (корпус)
    frags.append(line(x2 + 30, 270, x2 + 375, 270, color="#059669", sw=2.5))
    frags.append(text(x2 + 20, 274, "PE", size=13, bold=True, color="#059669"))

    # Сині стрілки синфазного струму i_CM
    frags.append(arrow(x2 + 180, 125, x2 + 60, 125, color=NEG, sw=2))
    frags.append(arrow(x2 + 180, 205, x2 + 60, 205, color=NEG, sw=2))
    frags.append(arrow(x2 + 100, 285, x2 + 220, 285, color=NEG, sw=2))
    frags.append(text(x2 + 120, 115, "i_CM / 2", size=11, color=NEG, bold=True))
    frags.append(text(x2 + 120, 195, "i_CM / 2", size=11, color=NEG, bold=True))
    frags.append(text(x2 + 160, 305, "i_CM (повернення через PE)", size=11, color=NEG, bold=True))

    box2, _, _ = textbox(x2 + w_p / 2, 365,
                         "Джерело: стрибки напруги dV/dt на комутаційному вузлі\n"
                         "Шлях: SW node → паразитне C_para → корпус PE → L & N\n"
                         "Пригнічення: синфазний дросель (CMC), Y-конденсатори",
                         size=11, pad=8, fill="#eff6ff", stroke=NEG)
    frags.append(box2)

    render(os.path.join(IMG, "cm-dm-noise-sources.svg"), W, H, *frags)

# ── 2. Анатомія повного вхідного ЕМС-фільтра ────────────────────────────────
def fig_filter_topology_breakdown():
    W, H = 920, 480
    frags = []
    frags.append(text(W / 2, 26, "Схемотехнічна анатомія дволанкового вхідного ЕМС-фільтра", size=16, bold=True))

    # Головні лінії L, N, PE
    y_l, y_n, y_pe = 90, 210, 330
    x_in, x_out = 60, 860

    frags.append(line(x_in, y_l, x_out, y_l, color=LINE, sw=2))
    frags.append(line(x_in, y_n, x_out, y_n, color=LINE, sw=2))
    frags.append(line(x_in, y_pe, x_out, y_pe, color="#059669", sw=2, dash="6,3"))

    frags.append(text(x_in - 20, y_l + 4, "L (вхід)", size=12, bold=True))
    frags.append(text(x_in - 20, y_n + 4, "N (вхід)", size=12, bold=True))
    frags.append(text(x_in - 20, y_pe + 4, "PE", size=12, bold=True, color="#059669"))

    frags.append(text(x_out + 25, y_l + 4, "L (вихід)", size=12, bold=True))
    frags.append(text(x_out + 25, y_n + 4, "N (вихід)", size=12, bold=True))
    frags.append(text(x_out + 25, y_pe + 4, "PE", size=12, bold=True, color="#059669"))

    # 1. Розрядний резистор (Bleeder) + X1-конденсатор
    x_c1 = 150
    frags.append(line(x_c1, y_l, x_c1, 130, color=LINE, sw=1.5))
    frags.append(rect(x_c1 - 10, 130, 20, 40, fill="#ffffff", stroke=MUTED, sw=1.5))
    frags.append(text(x_c1 + 22, 154, "R_bleed", size=11, color=MUTED))
    frags.append(line(x_c1, 170, x_c1, y_n, color=LINE, sw=1.5))

    x_x1 = 220
    frags.append(line(x_x1, y_l, x_x1, 140, color=LINE, sw=1.5))
    frags.append(line(x_x1 - 16, 140, x_x1 + 16, 140, color=POS, sw=2.5))
    frags.append(line(x_x1 - 16, 160, x_x1 + 16, 160, color=POS, sw=2.5))
    frags.append(line(x_x1, 160, x_x1, y_n, color=LINE, sw=1.5))
    frags.append(text(x_x1 + 22, 154, "C_X1", size=12, bold=True, color=POS))

    # 2. Синфазний дросель (Common-Mode Choke) з індуктивністю розсіювання L_leak
    x_cm = 370
    # Обмотка L
    frags.append(circle(x_cm - 20, y_l, 10, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(circle(x_cm, y_l, 10, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(circle(x_cm + 20, y_l, 10, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(circle(x_cm - 28, y_l - 12, 3, fill=NEG, stroke=NEG)) # точка фазування

    # Осердя (дві паралельні лінії)
    frags.append(line(x_cm - 35, 145, x_cm + 35, 145, color=LINE, sw=1.5))
    frags.append(line(x_cm - 35, 155, x_cm + 35, 155, color=LINE, sw=1.5))
    frags.append(text(x_cm, 153, "CMC (L_cm)", size=11, bold=True, color=NEG))

    # Обмотка N
    frags.append(circle(x_cm - 20, y_n, 10, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(circle(x_cm, y_n, 10, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(circle(x_cm + 20, y_n, 10, fill="#ffffff", stroke=NEG, sw=2))
    frags.append(circle(x_cm - 28, y_n - 12, 3, fill=NEG, stroke=NEG)) # точка фазування

    # Індуктивність розсіювання L_leak (пунктирний індуктор)
    x_lk = 460
    frags.append(circle(x_lk - 10, y_l, 8, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(circle(x_lk + 10, y_l, 8, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(text(x_lk, y_l - 16, "L_leak", size=11, bold=True, color=POS))

    frags.append(circle(x_lk - 10, y_n, 8, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(circle(x_lk + 10, y_n, 8, fill="#ffffff", stroke=POS, sw=1.5))
    frags.append(text(x_lk, y_n + 22, "L_leak", size=11, bold=True, color=POS))

    # 3. Y-конденсатори (C_Y1, C_Y2) до PE
    x_y = 570
    # Верхній C_Y1 (L -> PE)
    frags.append(line(x_y, y_l, x_y, 195, color=LINE, sw=1.5))
    frags.append(line(x_y - 14, 195, x_y + 14, 195, color=NEG, sw=2.5))
    frags.append(line(x_y - 14, 210, x_y + 14, 210, color=NEG, sw=2.5))
    frags.append(line(x_y, 210, x_y, y_pe, color=LINE, sw=1.5))
    frags.append(text(x_y + 22, 204, "C_Y1", size=12, bold=True, color=NEG))

    # Нижній C_Y2 (N -> PE)
    x_y2 = 630
    frags.append(line(x_y2, y_n, x_y2, 260, color=LINE, sw=1.5))
    frags.append(line(x_y2 - 14, 260, x_y2 + 14, 260, color=NEG, sw=2.5))
    frags.append(line(x_y2 - 14, 275, x_y2 + 14, 275, color=NEG, sw=2.5))
    frags.append(line(x_y2, 275, x_y2, y_pe, color=LINE, sw=1.5))
    frags.append(text(x_y2 + 22, 270, "C_Y2", size=12, bold=True, color=NEG))

    # 4. Демпфувальний ланцюжок Міддлбрука (R_d + C_d)
    x_d = 720
    frags.append(line(x_d, y_l, x_d, 130, color=LINE, sw=1.5))
    frags.append(rect(x_d - 10, 130, 20, 30, fill="#ffffff", stroke="#d97706", sw=1.5))
    frags.append(text(x_d + 20, 148, "R_d", size=11, color="#d97706", bold=True))
    frags.append(line(x_d, 160, x_d, 175, color=LINE, sw=1.5))
    frags.append(line(x_d - 14, 175, x_d + 14, 175, color="#d97706", sw=2.5))
    frags.append(line(x_d - 14, 188, x_d + 14, 188, color="#d97706", sw=2.5))
    frags.append(line(x_d, 188, x_d, y_n, color=LINE, sw=1.5))
    frags.append(text(x_d + 20, 184, "C_d", size=11, color="#d97706", bold=True))

    # 5. Другий X2-конденсатор
    x_x2 = 790
    frags.append(line(x_x2, y_l, x_x2, 140, color=LINE, sw=1.5))
    frags.append(line(x_x2 - 16, 140, x_x2 + 16, 140, color=POS, sw=2.5))
    frags.append(line(x_x2 - 16, 160, x_x2 + 16, 160, color=POS, sw=2.5))
    frags.append(line(x_x2, 160, x_x2, y_n, color=LINE, sw=1.5))
    frags.append(text(x_x2 + 22, 154, "C_X2", size=12, bold=True, color=POS))

    # Підсумкові виноски внизу
    b1, _, _ = textbox(210, 415, "X-ланка: C_X1, C_X2 + L_leak\nДавить диференційну заваду (DM)\nБезпека: самовідновлення плівки", size=11, pad=6, fill="#fff5f5", stroke=POS)
    b2, _, _ = textbox(500, 415, "CM-ланка: CMC + C_Y1, C_Y2\nДавить синфазну заваду (CM)\nБезпека: обмеження струму витоку PE", size=11, pad=6, fill="#eff6ff", stroke=NEG)
    b3, _, _ = textbox(770, 415, "Демпфування: R_d + C_d\nГасить пік імпедансу Міддлбрука\nЗапобігає розгойдуванню петлі", size=11, pad=6, fill="#fffbeb", stroke="#d97706")
    frags.extend([b1, b2, b3])

    render(os.path.join(IMG, "filter-topology-breakdown.svg"), W, H, *frags)

# ── 3. Критерій стійкості Міддлбрука ─────────────────────────────────────────
def fig_middlebrook_impedance_overlap():
    W, H = 880, 500
    frags = []
    frags.append(text(W / 2, 26, "Критерій стійкості Міддлбрука: імпеданс фільтра проти перетворювача", size=16, bold=True))

    x0, y0 = 90, 400
    w_ax, h_ax = 720, 320

    # Сітка та осі
    frags.append(rect(x0, y0 - h_ax, w_ax, h_ax, fill="none", stroke="#cbd5e1", sw=1))
    frags.append(line(x0, y0, x0 + w_ax, y0, color=LINE, sw=1.5))
    frags.append(line(x0, y0, x0, y0 - h_ax, color=LINE, sw=1.5))

    # Стрілки осей
    frags.append(arrow(x0 + w_ax, y0, x0 + w_ax + 25, y0, color=LINE, sw=1.5))
    frags.append(arrow(x0, y0 - h_ax, x0, y0 - h_ax - 20, color=LINE, sw=1.5))
    frags.append(text(x0 + w_ax + 30, y0 + 4, "f (Гц)", size=12, bold=True))
    frags.append(text(x0 - 15, y0 - h_ax - 10, "|Z| (дБОм)", size=12, bold=True))

    # Позначки частот на осі X (Log)
    freqs = [("100 Гц", 60), ("1 кГц", 180), ("10 кГц (f_0)", 320), ("50 кГц (f_c)", 480), ("500 кГц", 640)]
    for lbl, x_pos in freqs:
        frags.append(line(x0 + x_pos, y0, x0 + x_pos, y0 - h_ax, color="#f1f5f9", sw=1, dash="2,2"))
        frags.append(text(x0 + x_pos, y0 + 20, lbl, size=11, color=MUTED))

    # Крива 1: Вхідний імпеданс перетворювача |Z_in(f)|
    zin_pts = [
        (x0, y0 - 200), (x0 + 380, y0 - 200), (x0 + 480, y0 - 190),
        (x0 + 580, y0 - 110), (x0 + 700, y0 - 50)
    ]
    p_zin = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in zin_pts)
    frags.append(f'<path d="{p_zin}" fill="none" stroke="#2563eb" stroke-width="3"/>')
    b_zin, _, _ = textbox(x0 + 170, y0 - 230, "|Z_in,conv| = V_in² / P_out (від'ємний динамічний опір)", size=11, pad=5, fill="#eff6ff", stroke="#2563eb", color="#2563eb", bold=True)
    frags.append(b_zin)

    # Крива 2А: Недемпфований фільтр |Z_out,filter| з високим піком резонансу Q
    zout_undamped = [
        (x0, y0 - 20), (x0 + 160, y0 - 60), (x0 + 260, y0 - 120),
        (x0 + 320, y0 - 265), # високий гострий пік
        (x0 + 380, y0 - 120), (x0 + 480, y0 - 60), (x0 + 700, y0 - 20)
    ]
    p_undamped = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in zout_undamped)
    frags.append(f'<path d="{p_undamped}" fill="none" stroke="{POS}" stroke-width="2.5" stroke-dasharray="4,3"/>')

    # Виноска про нестійкість (вгорі над піком)
    b_warn, _, _ = textbox(x0 + 320, y0 - 295, "НЕСТІЙКІСТЬ! |Z_out| > |Z_in|\nПаразитні автоколивання", size=10, pad=4, fill="#fee2e2", stroke=POS, bold=True, color=POS)
    frags.append(b_warn)

    # Крива 2Б: Правильно демпфований фільтр (Middlebrook Damped)
    zout_damped = [
        (x0, y0 - 20), (x0 + 160, y0 - 60), (x0 + 260, y0 - 110),
        (x0 + 320, y0 - 135), # згладжений низький пік
        (x0 + 380, y0 - 110), (x0 + 480, y0 - 60), (x0 + 700, y0 - 20)
    ]
    p_damped = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in zout_damped)
    frags.append(f'<path d="{p_damped}" fill="none" stroke="{FIELD}" stroke-width="3"/>')
    b_zdamped, _, _ = textbox(x0 + 540, y0 - 260, "|Z_out,filter| з демпфуванням R_d + C_d", size=11, pad=5, fill="#f0fdf4", stroke=FIELD, color=FIELD, bold=True)
    frags.append(b_zdamped)

    # Запас стійкості (Delta M) між 135 і 200 на частоті f0
    frags.append(line(x0 + 320, y0 - 195, x0 + 320, y0 - 140, color="#d97706", sw=1.8))
    b_dm, _, _ = textbox(x0 + 250, y0 - 165, "Запас ΔM ≥ 6 дБ", size=10, pad=4, fill="#fffbeb", stroke="#d97706", color="#d97706", bold=True)
    frags.append(b_dm)

    box, _, _ = textbox(W / 2, 455,
                        "Критерій Міддлбрука: для стійкості замкненого перетворювача вихідний імпеданс\n"
                        "вхідного фільтра повинен бути значно меншим за вхідний імпеданс: |Z_out,filter(s)| << |Z_in,conv(s)|.\n"
                        "Паралельна RC-гілка (R_d, C_d ≈ 3..5·C_filt) зрізає резонансний пік добротності Q.",
                        size=11, pad=8, fill="#f8fafc", stroke=LINE)
    frags.append(box)

    render(os.path.join(IMG, "middlebrook-impedance-overlap.svg"), W, H, *frags)

# ── 4. Схема вимірювання з LISN ─────────────────────────────────────────────
def fig_lisn_measurement_setup():
    W, H = 900, 440
    frags = []
    frags.append(text(W / 2, 26, "Схема вимірювання кондуктивних завад з еквівалентом мережі (LISN / CISPR 16)", size=16, bold=True))

    # Блок 1: Мережа живлення (Grid)
    frags.append(rect(40, 90, 130, 240, fill="#f8fafc", stroke=MUTED, sw=1.5))
    frags.append(text(105, 120, "Мережа\nживлення\n(AC / DC Grid)", size=13, bold=True))
    frags.append(text(105, 270, "Невідомий\nімпеданс джерела\n1..100 Ом", size=10, color=MUTED))

    # Блок 2: LISN (Line Impedance Stabilization Network)
    frags.append(rect(220, 70, 280, 280, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    frags.append(text(360, 95, "LISN (Еквівалент мережі / 50 Ом)", size=14, bold=True, color=FIELD))

    # Схема всередині LISN
    # Лінія L
    frags.append(line(170, 140, 260, 140, color=LINE, sw=2))
    # Дросель LISN (50 мкГн)
    frags.append(circle(275, 140, 10, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(circle(295, 140, 10, fill="#ffffff", stroke=FIELD, sw=1.5))
    frags.append(text(285, 120, "50 мкГн", size=10, bold=True, color=FIELD))
    frags.append(line(305, 140, 500, 140, color=LINE, sw=2))

    # Конденсатор розв'язки на вимірювач (0.1 мкФ) + 50 Ом
    frags.append(line(380, 140, 380, 190, color=LINE, sw=1.5))
    frags.append(line(370, 190, 390, 190, color=LINE, sw=2))
    frags.append(line(370, 200, 390, 200, color=LINE, sw=2))
    frags.append(text(415, 195, "0.1 мкФ", size=10))
    frags.append(line(380, 200, 380, 230, color=LINE, sw=1.5))
    frags.append(rect(372, 230, 16, 26, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(405, 245, "50 Ом", size=10, bold=True))
    frags.append(line(380, 256, 380, 290, color="#059669", sw=2))

    # Лінія N
    frags.append(line(170, 290, 500, 290, color=LINE, sw=2))
    frags.append(text(240, 134, "L", size=12, bold=True))
    frags.append(text(240, 284, "N", size=12, bold=True))
    frags.append(text(380, 310, "PE (екран)", size=11, color="#059669", bold=True))

    # Блок 3: Вхідний ЕМС-фільтр
    frags.append(rect(540, 90, 140, 240, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(610, 120, "Вхідний\nЕМС-фільтр\n(DUT Filter)", size=13, bold=True, color=NEG))
    frags.append(text(610, 210, "CMC + X + Y\nдемпфування\nМіддлбрука", size=10, color=MUTED))

    # Блок 4: Досліджуваний перетворювач (EUT)
    frags.append(rect(720, 90, 140, 240, fill="#fdf2f8", stroke=POS, sw=1.8, rx=6))
    frags.append(text(790, 120, "Імпульсний\nперетворювач\n(EUT / SMPS)", size=13, bold=True, color=POS))
    frags.append(text(790, 210, "Джерело завад:\ndI/dt (DM)\ndV/dt (CM)", size=10, color=POS))

    # З'єднувальні лінії між блоками
    frags.append(line(500, 140, 540, 140, color=LINE, sw=2))
    frags.append(line(500, 290, 540, 290, color=LINE, sw=2))
    frags.append(line(680, 140, 720, 140, color=LINE, sw=2))
    frags.append(line(680, 290, 720, 290, color=LINE, sw=2))

    # Вихід на вимірювальний приймач
    frags.append(arrow(380, 256, 380, 370, color=FIELD, sw=2))
    box_rx, _, _ = textbox(380, 395, "До спектроаналізатора / приймача CISPR 16\nКалібрований порт: 50 Ом у смузі 150 кГц – 30 МГц", size=11, pad=6, fill="#f0fdf4", stroke=FIELD)
    frags.append(box_rx)

    # Підсумковий опис праворуч внизу
    box_desc, _, _ = textbox(700, 395, "LISN ізолює прилад від коливань мережі й задає\nстандартизований імпеданс 50 Ом для повторюваності вимірів.", size=11, pad=6, fill="#f8fafc", stroke=LINE)
    frags.append(box_desc)

    render(os.path.join(IMG, "lisn-measurement-setup.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_cm_dm_noise_sources()
    fig_filter_topology_breakdown()
    fig_middlebrook_impedance_overlap()
    fig_lisn_measurement_setup()
    print("Всі 4 фігури успішно згенеровано.")
