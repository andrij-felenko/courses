# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Людина в контурі: чому затримка руйнує керування».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
"""
import sys, os
TOPIC_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(TOPIC_DIR, '..', '..', '..', '..', 'scripts'))
sys.path.insert(0, SCRIPTS_DIR)
from svgkit import *

IMG_DIR = os.path.join(TOPIC_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)


# ── Фігура 1: Повний замкнений контур «людина-машина» ─────────────────────────
def fig_human_machine_loop():
    W, H = 1040, 520
    P = []
    P.append(text(W / 2, 28, "Замкнений контур керування «людина-машина» та наскрізна затримка",
                  size=16, bold=True))

    # Зона оператора (ліва колонка) та зона апарата (права колонка)
    op_box_w = 320
    rv_box_w = 320
    op_x0 = 30
    rv_x0 = W - 30 - rv_box_w  # 1040 - 350 = 690

    P.append(rect(op_x0, 55, op_box_w, 415, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    P.append(text(op_x0 + op_box_w / 2, 80, "ЛЮДИНА-ОПЕРАТОР (модель Макруера)", size=12.5, bold=True, color="#1e293b"))

    P.append(rect(rv_x0, 55, rv_box_w, 415, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=8))
    P.append(text(rv_x0 + rv_box_w / 2, 80, "БОРТ АПАРАТА ТА ДИНАМІКА", size=12.5, bold=True, color="#1e293b"))

    # Вхідний сигнал: Уставка r(t)
    P.append(arrow(op_x0 - 20, 140, op_x0 + 25, 140, color=INK, sw=2.0))
    P.append(text(op_x0 - 5, 128, "r(t)", size=11, bold=True, color=INK))

    # Суматор похибки e(t) = r(t) - y_fb(t)
    sum_cx, sum_cy = op_x0 + 35, 140
    P.append(circle(sum_cx, sum_cy, 10, fill="#ffffff", stroke=INK, sw=1.8))
    P.append(text(sum_cx, sum_cy + 4, "+", size=12, bold=True, color=POS))
    P.append(text(sum_cx - 8, sum_cy + 20, "−", size=14, bold=True, color=NEG))
    P.append(text(sum_cx + 16, sum_cy - 10, "e(t)", size=10.5, bold=True, color=MUTED))

    # Блок 1: Зорове сприйняття й когнітивна реакція
    op_cx = op_x0 + 185
    fr, w, h = textbox(op_cx, 140,
                       "Зоровий тракт і мозок\nτ_p ≈ 150–220 мс\nLead/Lag: (T_L·s+1)/(T_I·s+1)",
                       size=10.5, bold=True, fill="#eef2f7", stroke=NEG, min_w=190)
    P.append(arrow(sum_cx + 10, 140, op_cx - w / 2, 140, color=INK, sw=1.8))
    P.append(fr)

    # Блок 2: Нервово-м'язовий фільтр
    fr2, w2, h2 = textbox(op_cx, 240,
                          "Нервово-м'язова ланка\n1 / (T_N·s + 1), T_N ≈ 0.1 с\nМ'язи рук і стік пульта",
                          size=10.5, bold=True, fill="#eef2f7", stroke=NEG, min_w=190)
    P.append(arrow(op_cx, 140 + h / 2, op_cx, 240 - h2 / 2, color=INK, sw=1.8))
    P.append(fr2)

    # Лінія зв'язку: RC-лінк (команди вгору)
    mid_cx = W / 2  # 520
    P.append(arrow(op_cx + w2 / 2, 240, rv_x0 + 20, 240, color=POS, sw=2.2))
    fr_rc, w_rc, h_rc = textbox(mid_cx, 215,
                                "RC-ЛІНК ↑\nτ_rc ≈ 10–30 мс\n(пакет, ефір, черга)",
                                size=10, bold=True, fill="#fdecea", stroke=POS)
    P.append(fr_rc)

    # Блок 3: Політний контролер
    rv_cx = rv_x0 + rv_box_w / 2
    fr3, w3, h3 = textbox(rv_cx, 240,
                          "Політний контролер (FC)\nВнутрішній PID (1–8 кГц)\nRate / Angle / Position",
                          size=10.5, bold=True, fill="#e9f7ef", stroke=FIELD, min_w=200)
    P.append(fr3)

    # Блок 4: Фізика апарата
    fr4, w4, h4 = textbox(rv_cx, 350,
                          "Фізика апарата й мотори\nІнерція, тяга, ESC\nСтан / кут y(t)",
                          size=10.5, bold=True, fill="#e9f7ef", stroke=FIELD, min_w=200)
    P.append(arrow(rv_cx, 240 + h3 / 2, rv_cx, 350 - h4 / 2, color=INK, sw=1.8))
    P.append(fr4)

    # Зворотний зв'язок: Відеотракт і дисплей
    P.append(line(rv_cx - w4 / 2, 350, mid_cx + 120, 350, color=NEG, sw=2.2))
    P.append(line(mid_cx - 120, 350, sum_cx, 350, color=NEG, sw=2.2))
    P.append(arrow(sum_cx, 350, sum_cx, sum_cy + 10, color=NEG, sw=2.2))

    fr_vid, w_vid, h_vid = textbox(mid_cx, 350,
                                   "ВІДЕОЛІНК ТА ДИСПЛЕЙ ↓\nτ_video ≈ 40–180 мс\n(камера + кодек + RF + екран)",
                                   size=10, bold=True, fill="#eaf0fd", stroke=NEG)
    P.append(fr_vid)

    # Підсумок у рамці внизу
    fr_bot, w_bot, h_bot = textbox(W / 2, 492,
                                   "Повна затримка контуру:  τ_total = τ_video + τ_людина + τ_rc + τ_борт ≈ 250–450 мс.  "
                                   "Фазовий набіг:  Δφ = −ω · τ_total.",
                                   size=11.5, bold=True, fill="#ffffff", stroke=INK)
    P.append(fr_bot)

    render(os.path.join(IMG_DIR, "human-machine-loop.svg"), W, H, *P)


# ── Фігура 2: З'їдання фазового запасу затримкою (діаграма Боде) ───────────────
def fig_bode_phase_erosion():
    W, H = 960, 500
    P = []
    P.append(text(W / 2, 28, "Як чиста затримка з'їдає запас стійкості по фазі (Діаграма Боде)",
                  size=16, bold=True))

    gx0, gx1 = 120, W - 60
    # Верхній графік: Амплітуда (дБ)
    gy_mag = 130
    gh_mag = 100

    # Нижній графік: Фаза (градуси)
    gy_pha = 310
    gh_pha = 120

    # Сітка та осі для Амплітуди
    P.append(rect(gx0, gy_mag - gh_mag / 2, gx1 - gx0, gh_mag, fill="#fafafa", stroke="#d1d5db", sw=1.0))
    P.append(line(gx0, gy_mag, gx1, gy_mag, color="#9ca3af", sw=1.2, dash="4,4")) # 0 dB line
    P.append(text(gx0 - 12, gy_mag + 4, "0 дБ", size=11, bold=True, anchor="end", color=INK))
    P.append(text(gx0 - 12, gy_mag - gh_mag / 2 + 12, "+20 дБ", size=10, anchor="end", color=MUTED))
    P.append(text(gx0 - 12, gy_mag + gh_mag / 2 - 4, "−20 дБ", size=10, anchor="end", color=MUTED))
    P.append(text(gx0 + 15, gy_mag - gh_mag / 2 + 15, "Амплітуда |Y_ol(jω)|", size=11.5, bold=True, color=INK, anchor="start"))

    # Крива амплітуди: спад -20 дБ/дек, перетин 0 дБ на частоті зрізу w_c
    wc_x = gx0 + (gx1 - gx0) * 0.48
    mag_pts = [(gx0 + 20, gy_mag - 38), (wc_x, gy_mag), (gx1 - 30, gy_mag + 38)]
    for i in range(len(mag_pts) - 1):
        P.append(line(mag_pts[i][0], mag_pts[i][1], mag_pts[i + 1][0], mag_pts[i + 1][1], color=INK, sw=2.4))
    P.append(circle(wc_x, gy_mag, 4, fill=POS, stroke=POS))
    P.append(text(wc_x, gy_mag - 12, "Частота зрізу ω_c", size=11, bold=True, color=POS))

    # Сітка та осі для Фази
    P.append(rect(gx0, gy_pha - gh_pha / 2, gx1 - gx0, gh_pha, fill="#fafafa", stroke="#d1d5db", sw=1.0))
    p0_y = gy_pha - gh_pha / 2 + 15    # -90 deg
    p180_y = gy_pha + gh_pha / 2 - 15  # -180 deg
    p135_y = (p0_y + p180_y) / 2       # -135 deg

    P.append(line(gx0, p0_y, gx1, p0_y, color="#9ca3af", sw=1.0, dash="3,3"))
    P.append(text(gx0 - 12, p0_y + 4, "−90°", size=10, anchor="end", color=MUTED))

    P.append(line(gx0, p135_y, gx1, p135_y, color="#9ca3af", sw=1.0, dash="3,3"))
    P.append(text(gx0 - 12, p135_y + 4, "−135°", size=10, anchor="end", color=MUTED))

    P.append(line(gx0, p180_y, gx1, p180_y, color=POS, sw=1.5, dash="5,3"))
    P.append(text(gx0 - 12, p180_y + 4, "−180°", size=11, bold=True, anchor="end", color=POS))
    P.append(text(gx0 + 15, gy_pha - gh_pha / 2 + 15, "Фаза ∠Y_ol(jω)", size=11.5, bold=True, color=INK, anchor="start"))

    # Вертикальна лінія частоти зрізу крізь обидва графіки
    P.append(line(wc_x, gy_mag - 40, wc_x, p180_y + 15, color="#6b7280", sw=1.2, dash="3,3"))

    # Фазова крива 1: Без затримки (ідеальний інтегратор: стала фаза -90 deg)
    P.append(line(gx0 + 20, p0_y, gx1 - 20, p0_y, color=FIELD, sw=2.2))
    P.append(text(gx1 - 25, p0_y - 8, "Без затримки (τ=0): Запас PM = 90°", size=10.5, bold=True, color=FIELD, anchor="end"))

    # Фазова крива 2: Мала затримка (τ = 80 мс)
    p_tau1 = [(gx0 + 20, p0_y + 2), (wc_x * 0.7, p0_y + 12), (wc_x, p135_y - 8), (gx1 - 40, p180_y + 8)]
    for i in range(len(p_tau1) - 1):
        P.append(line(p_tau1[i][0], p_tau1[i][1], p_tau1[i + 1][0], p_tau1[i + 1][1], color=NEG, sw=2.0))
    P.append(circle(wc_x, p135_y - 8, 4, fill=NEG, stroke=NEG))
    P.append(text(gx1 - 25, p135_y - 12, "Помірна затримка (τ=80 мс): PM ≈ 50° (стійко)", size=10.5, bold=True, color=NEG, anchor="end"))

    # Фазова крива 3: Критична затримка (τ = 250 мс) -> перетинає -180 саме на wc!
    p_tau2 = [(gx0 + 20, p0_y + 6), (wc_x * 0.6, p0_y + 30), (wc_x, p180_y), (gx1 - 100, p180_y + 28)]
    for i in range(len(p_tau2) - 1):
        P.append(line(p_tau2[i][0], p_tau2[i][1], p_tau2[i + 1][0], p_tau2[i + 1][1], color=POS, sw=2.5))
    P.append(circle(wc_x, p180_y, 5, fill=POS, stroke=POS))
    P.append(text(gx1 - 25, p180_y + 15, "Критична затримка (τ=250 мс): PM = 0° (МЕЖА РОЗКАЧКИ / PIO)", size=10.5, bold=True, color=POS, anchor="end"))

    # Стрілка запасу по фазі
    P.append(arrow(wc_x + 15, p180_y, wc_x + 15, p135_y - 8, color=NEG, sw=1.6))
    P.append(text(wc_x + 22, (p180_y + p135_y) / 2, "Запас по фазі (PM)", size=10, bold=True, color=NEG, anchor="start"))

    # Нижня рамка з висновком
    fr_b, w_b, h_b = textbox(W / 2, 475,
                             "Затримка τ валить фазу за формулою  Δφ = −ω·τ.  "
                             "Коли фаза досягає −180° на частоті зрізу (де підсилення = 1), контур перетворюється на автогенератор.",
                             size=11, bold=True, fill="#fdecea", stroke=POS)
    P.append(fr_b)

    render(os.path.join(IMG_DIR, "bode-phase-erosion.svg"), W, H, *P)


# ── Фігура 3: Хвильова форма розкачки оператором (PIO) ────────────────────────
def fig_pio_waveform():
    W, H = 960, 480
    P = []
    P.append(text(W / 2, 28, "Розвиток розкачки оператором (PIO) при виникненні затримки",
                  size=16, bold=True))

    # Два часові сценарії: ліворуч — стійке керування (τ=40 мс), праворуч — PIO (τ=250 мс)
    w_half = 410
    h_box = 370

    # Ліва панель: Норма
    x_left = 60
    P.append(rect(x_left, 60, w_half, h_box, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=6))
    P.append(text(x_left + w_half / 2, 85, "А. Мала затримка (τ = 40 мс): Стійке парирування", size=12, bold=True, color=FIELD))

    # Осі лівої панелі
    y_zero_l = 210
    P.append(line(x_left + 30, y_zero_l, x_left + w_half - 20, y_zero_l, color="#94a3b8", sw=1.2, dash="3,3"))
    P.append(line(x_left + 30, 110, x_left + 30, 390, color="#64748b", sw=1.4))
    P.append(text(x_left + 25, 115, "Кут / Стік", size=10, color=MUTED, anchor="end"))
    P.append(text(x_left + w_half - 15, y_zero_l + 15, "Час t", size=10, color=MUTED, anchor="end"))

    # Графік ліворуч: Збурення кута (зелена лінія) швидко затухає
    pts_l_angle = [
        (x_left + 30, y_zero_l),
        (x_left + 60, y_zero_l - 45),   # порив вітру
        (x_left + 100, y_zero_l - 20),
        (x_left + 150, y_zero_l + 8),
        (x_left + 200, y_zero_l - 2),
        (x_left + 260, y_zero_l),
        (x_left + w_half - 30, y_zero_l)
    ]
    for i in range(len(pts_l_angle) - 1):
        P.append(line(pts_l_angle[i][0], pts_l_angle[i][1], pts_l_angle[i + 1][0], pts_l_angle[i + 1][1], color=FIELD, sw=2.4))

    # Стік оператора (пунктир) — адекватно компенсує
    pts_l_stick = [
        (x_left + 30, y_zero_l),
        (x_left + 60, y_zero_l),
        (x_left + 90, y_zero_l + 40),  # реакція з малим лагом
        (x_left + 140, y_zero_l - 10),
        (x_left + 200, y_zero_l),
        (x_left + w_half - 30, y_zero_l)
    ]
    for i in range(len(pts_l_stick) - 1):
        P.append(line(pts_l_stick[i][0], pts_l_stick[i][1], pts_l_stick[i + 1][0], pts_l_stick[i + 1][1], color=NEG, sw=1.8, dash="4,2"))

    P.append(text(x_left + w_half / 2, 415, "Похибка зникає за 1.5 с. Контур стійкий.", size=10.5, color=FIELD, bold=True))

    # Права панель: PIO
    x_right = 500
    P.append(rect(x_right, 60, w_half, h_box, fill="#fffbfb", stroke=POS, sw=1.5, rx=6))
    P.append(text(x_right + w_half / 2, 85, "Б. Затримка (τ = 250 мс): Розгойдування (PIO)", size=12, bold=True, color=POS))

    # Осі правої панелі
    y_zero_r = 210
    P.append(line(x_right + 30, y_zero_r, x_right + w_half - 20, y_zero_r, color="#94a3b8", sw=1.2, dash="3,3"))
    P.append(line(x_right + 30, 110, x_right + 30, 390, color="#64748b", sw=1.4))
    P.append(text(x_right + w_half - 15, y_zero_r + 15, "Час t", size=10, color=MUTED, anchor="end"))

    # Графік праворуч: Розгойдування кута (червона лінія з наростанням)
    pts_r_angle = [
        (x_right + 30, y_zero_r),
        (x_right + 60, y_zero_r - 25),
        (x_right + 110, y_zero_r + 40),
        (x_right + 170, y_zero_r - 65),
        (x_right + 230, y_zero_r + 85),
        (x_right + 290, y_zero_r - 110),
        (x_right + 350, y_zero_r + 130)
    ]
    for i in range(len(pts_r_angle) - 1):
        P.append(line(pts_r_angle[i][0], pts_r_angle[i][1], pts_r_angle[i + 1][0], pts_r_angle[i + 1][1], color=POS, sw=2.4))

    # Стік оператора (синій пунктир) — запізнюється рівно на півперіоду (фаза 180 deg) і розгойдує сильніше
    pts_r_stick = [
        (x_right + 30, y_zero_r),
        (x_right + 75, y_zero_r),
        (x_right + 110, y_zero_r - 35),  # штовхає в той самий бік, куди летить апарат!
        (x_right + 170, y_zero_r + 55),
        (x_right + 230, y_zero_r - 80),
        (x_right + 290, y_zero_r + 105),
        (x_right + 350, y_zero_r - 125)
    ]
    for i in range(len(pts_r_stick) - 1):
        P.append(line(pts_r_stick[i][0], pts_r_stick[i][1], pts_r_stick[i + 1][0], pts_r_stick[i + 1][1], color=NEG, sw=1.8, dash="4,2"))

    P.append(text(x_right + w_half / 2, 415, "Стік синфазний з рухом → самозбудження й аварія!", size=10.5, color=POS, bold=True))

    # Загальна легенда
    P.append(line(W / 2 - 120, 455, W / 2 - 80, 455, color=POS, sw=2.5))
    P.append(text(W / 2 - 70, 459, "Кут апарата", size=11, bold=True, anchor="start"))
    P.append(line(W / 2 + 40, 455, W / 2 + 80, 455, color=NEG, sw=2.0, dash="4,2"))
    P.append(text(W / 2 + 90, 459, "Стік оператора u(t)", size=11, bold=True, anchor="start"))

    render(os.path.join(IMG_DIR, "pio-waveform.svg"), W, H, *P)


# ── Фігура 4: Ієрархія режимів керування та допустима затримка ────────────────
def fig_control_levels_latency():
    W, H = 980, 440
    P = []
    P.append(text(W / 2, 28, "Ієрархія рівнів абстракції керування та допустима затримка",
                  size=16, bold=True))

    # Чотири сходинки абстракції (зліва направо: від ручного до автономного)
    levels = [
        ("RATE / ACRO\n(кутова швидкість)",
         "τ_max < 60–80 мс",
         "Пряме керування моментом/швидкістю.\nІнтегратор 1/s у контурі.\nНайвища чутливість до затримок.",
         "#fdecea", POS),

        ("ANGLE / STABILIZE\n(кутова орієнтація)",
         "τ_max ≈ 200–300 мс",
         "Бортовий PID тримає кут нахилу.\nСтік задає нахил (Pitch/Roll).\nПри відпусканні — автогоризонт.",
         "#fef9c3", "#ca8a04"),

        ("POSITION HOLD\n(утримання точки)",
         "τ_max ≈ 0.8–2.0 с",
         "Борт тримає швидкість і координати.\nСтік задає вектор швидкості v_x, v_y.\nБез команд — зависання в точці.",
         "#e9f7ef", FIELD),

        ("SUPERVISORY / MISSION\n(маршрутні точки)",
         "τ_max > 5–30 с",
         "Високорівневі цілі (Waypoints/Go-To).\nУся фізика й навігація — на борту.\nСтійкий до супутникових лагів.",
         "#eaf0fd", NEG)
    ]

    card_w = 210
    card_gap = 18
    start_x = (W - (4 * card_w + 3 * card_gap)) / 2

    for i, (title, lat, desc, fill_col, stroke_col) in enumerate(levels):
        cx = start_x + i * (card_w + card_gap) + card_w / 2
        cy = 220

        # Рамка картки
        fr, w, h = textbox(cx, cy,
                           "%s\n\nДОПУСТИМА ЗАТРИМКА:\n%s\n\n%s" % (title, lat, desc),
                           size=11, bold=False, fill=fill_col, stroke=stroke_col, sw=1.8, min_w=card_w)
        P.append(fr)

        # Стрілка переходу між рівнями
        if i < len(levels) - 1:
            P.append(arrow(cx + card_w / 2 + 2, cy, cx + card_w / 2 + card_gap - 2, cy, color=MUTED, sw=1.6))

    # Стрілка знизу: рівень автономії зростає
    P.append(arrow(start_x, 380, W - start_x, 380, color=INK, sw=2.0))
    P.append(text(W / 2, 405, "Рівень автономності бортового контролера зростає  ⟶  Стійкість до затримок каналу зростає",
                  size=11.5, bold=True, color=INK))

    render(os.path.join(IMG_DIR, "control-levels-latency.svg"), W, H, *P)


if __name__ == "__main__":
    fig_human_machine_loop()
    fig_bode_phase_erosion()
    fig_pio_waveform()
    fig_control_levels_latency()
    print("OK: 4 figures generated into img/")
