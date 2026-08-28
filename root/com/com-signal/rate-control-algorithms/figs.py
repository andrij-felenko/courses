# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. rate-distortion-curve: Крива R(D) та лагранжева оптимізація ────────────
def fig_rate_distortion_curve():
    W, H = 760, 380
    p = []
    ox, oy = 90, 310
    aw, ah = 580, 240

    # Сітка та осі
    p.append(rect(ox, oy - ah, aw, ah, fill="#fbfcfd", stroke="#e2e8f0", sw=1.0, rx=4))
    p.append(arrow(ox, oy, ox + aw + 25, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ah - 25, color=INK, sw=1.8))

    p.append(text(ox + aw + 25, oy + 22, "Бітрейт R (біт/піксель)", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 15, oy - ah - 15, "Спотворення D (MSE)", size=12, color=INK, bold=True, anchor="start"))

    # Теоретична R(D) крива Шеннона (опукла вниз гіперболічна форма)
    pts = []
    for i in range(101):
        t = i / 100.0
        x = ox + 30 + t * (aw - 70)
        val = 0.88 * math.exp(-3.2 * t) + 0.05
        y = oy - val * ah
        pts.append((x, y))

    d_path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    p.append(f'<path d="{d_path}" fill="none" stroke="{NEG}" stroke-width="2.8"/>')

    # Робочі точки A (високий QP, низький R) та B (низький QP, високий R)
    tA = 0.18
    xA = ox + 30 + tA * (aw - 70)
    yA = oy - (0.88 * math.exp(-3.2 * tA) + 0.05) * ah
    p.append(circle(xA, yA, 5.5, fill=POS, stroke=INK, sw=1.6))

    # Дотична в точці A (крутий нахил -> велика lambda_A)
    p.append(line(xA - 60, yA - 70, xA + 75, yA + 87, color=POS, sw=1.6, dash="4,3"))
    tb_a, _, _ = textbox(xA + 115, yA - 30, "Точка A (грубе квантування)\nВисокий QP, мала швидкість R\nКрутий нахил: нахил = −λ_A (велике λ)", size=10.5, pad=6, fill="#fdf2f2", stroke=POS, bold=False)
    p.append(tb_a)

    # Точка B: t = 0.65
    tB = 0.65
    xB = ox + 30 + tB * (aw - 70)
    yB = oy - (0.88 * math.exp(-3.2 * tB) + 0.05) * ah
    p.append(circle(xB, yB, 5.5, fill=FIELD, stroke=INK, sw=1.6))

    # Дотична в точці B (пологий нахил -> мала lambda_B)
    p.append(line(xB - 90, yB - 22, xB + 90, yB + 22, color=FIELD, sw=1.6, dash="4,3"))
    tb_b, _, _ = textbox(xB + 40, yB - 55, "Точка B (тонке квантування)\nНизький QP, висока якість\nПологий нахил: нахил = −λ_B (мале λ)", size=10.5, pad=6, fill="#f0f9f2", stroke=FIELD, bold=False)
    p.append(tb_b)

    # Лагранжева формула в рамці в центрі/вгорі
    tb_form, _, _ = textbox(ox + aw * 0.70, oy - ah * 0.82, "Критерій Лагранжа: min J = D + λ·R\nМінімум сумарної вартості:\nнахил кривої dD/dR = −λ", size=11, pad=8, fill="#eff6ff", stroke=NEG, bold=True)
    p.append(tb_form)

    # Зона недосяжності під кривою
    p.append(text(ox + 90, oy - 25, "Зона недосяжних компресій R(D)", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "rate-distortion-curve.svg"), W, H, *p,
           title="Крива швидкості-спотворення R(D) та оптимум Лагранжа")


# ── 2. hrd-leaky-bucket: Модель віртуального буфера VBV / HRD ─────────────────
def fig_hrd_leaky_bucket():
    W, H = 760, 360
    p = []
    ox, oy = 80, 290
    aw, ah = 620, 210

    # Фон графіку
    p.append(rect(ox, oy - ah, aw, ah, fill="#fbfcfd", stroke="#e2e8f0", sw=1.0, rx=4))

    # Межі буфера: Upper (Overflow) і Lower (Underflow)
    p.append(rect(ox, oy - ah, aw, 22, fill="#fef2f2", stroke="none"))
    p.append(line(ox, oy - ah + 22, ox + aw, oy - ah + 22, color=POS, sw=1.8, dash="5,4"))
    p.append(text(ox + aw - 10, oy - ah + 15, "Стеля буфера B_max (Ризик Buffer Overflow)", size=10, color=POS, bold=True, anchor="end"))

    p.append(rect(ox, oy - 22, aw, 22, fill="#fef2f2", stroke="none"))
    p.append(line(ox, oy - 22, ox + aw, oy - 22, color=POS, sw=1.8, dash="5,4"))
    p.append(text(ox + aw - 10, oy - 8, "Дно буфера 0 (Ризик Buffer Underflow — затихання відео)", size=10, color=POS, bold=True, anchor="end"))

    # Осі
    p.append(arrow(ox, oy, ox + aw + 25, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ah - 25, color=INK, sw=1.8))
    p.append(text(ox + aw + 25, oy + 20, "Час t (дискретні моменти DTS)", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 12, oy - ah - 12, "Наповнення буфера B(t) (біти)", size=11, color=INK, bold=True, anchor="start"))

    frames = [
        (0.00, 0.40, True),
        (0.14, 0.12, False),
        (0.28, 0.10, False),
        (0.42, 0.14, False),
        (0.56, 0.48, True),
        (0.70, 0.11, False),
        (0.84, 0.09, False),
        (0.98, 0.10, False)
    ]

    curr_b = 0.65
    t_prev = 0.0
    traj_pts = []

    x_start = ox + 15
    traj_pts.append((x_start, oy - curr_b * ah))

    for i, (t_frac, s_drop, is_i) in enumerate(frames):
        x_dts = ox + 15 + t_frac * (aw - 40)
        if i > 0:
            curr_b += (t_frac - t_prev) * 0.95
            traj_pts.append((x_dts, oy - curr_b * ah))

        curr_b -= s_drop
        traj_pts.append((x_dts, oy - curr_b * ah))
        t_prev = t_frac

        p.append(line(x_dts, oy - 4, x_dts, oy + 4, color=INK, sw=1.2))
        lbl = f"I{i+1}" if is_i else f"P{i}"
        col = POS if is_i else NEG
        p.append(text(x_dts, oy + 15, lbl, size=10, color=col, bold=True))

        if is_i:
            p.append(text(x_dts + 8, oy - (curr_b + s_drop/2) * ah, f"−S_I", size=9.5, color=POS, bold=True, anchor="start"))

    d_traj = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in traj_pts)
    p.append(f'<path d="{d_traj}" fill="none" stroke="{NEG}" stroke-width="2.4"/>')

    # Анотація нахилу каналу
    p.append(line(ox + 120, oy - 140, ox + 190, oy - 165, color=FIELD, sw=2.0))
    p.append(arrow(ox + 190, oy - 165, ox + 195, oy - 167, color=FIELD, sw=2.0))
    tb_chan, _, _ = textbox(ox + 250, oy - 170, "Приплив з каналу:\n+R_in · Δt (лінійне зростання)", size=9.5, pad=5, fill="#f0fdf4", stroke=FIELD)
    p.append(tb_chan)

    # Анотація поведінки регулятора після важкого кадру
    tb_rec, _, _ = textbox(ox + aw * 0.72, oy - ah * 0.70, "Після важкого кадру буфер падає;\nРегулятор збільшує QP наступних кадрів,\nщоб не допустити Underflow", size=9.5, pad=6, fill="#eff6ff", stroke=NEG)
    p.append(tb_rec)

    render(os.path.join(OUT, "hrd-leaky-bucket.svg"), W, H, *p,
           title="Модель віртуального буфера VBV / HRD: динаміка наповнення")


# ── 3. gop-bit-allocation: Розподіл бітів за типами кадрів і складністю ───────
def fig_gop_bit_allocation():
    W, H = 760, 390
    p = []
    ox, oy = 70, 335
    aw, ah = 630, 190

    # Інформаційні плашки вгорі
    tb1, _, _ = textbox(170, 55, "Опорний I-кадр (~5–8× ваги P)\nВисокий пріоритет: базове оновлення,\nпомилка впливає на всю групу", size=10, pad=6, fill="#fdf2f2", stroke=POS)
    p.append(tb1)

    tb2, _, _ = textbox(400, 55, "P-кадри (середня вага)\nНесуть вектори руху\nта залишок передбачення", size=10, pad=6, fill="#eef2ff", stroke=NEG)
    p.append(tb2)

    tb3, _, _ = textbox(610, 55, "B-кадри (найменша вага)\nДвонапрямлене усереднення,\nне є опорними в базі", size=10, pad=6, fill="#f8fafc", stroke="#475569")
    p.append(tb3)

    # Фон та осі
    p.append(rect(ox, oy - ah, aw, ah, fill="#fbfcfd", stroke="#e2e8f0", sw=1.0, rx=4))
    p.append(arrow(ox, oy, ox + aw + 25, oy, color=INK, sw=1.8))
    p.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=1.8))
    p.append(text(ox + aw + 25, oy + 20, "Порядок кадрів у GOP", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 10, oy - ah - 8, "Виділені біти", size=11, color=INK, bold=True, anchor="start"))

    gop = [
        ("I₀",  0.88, POS,   "#fde8e8"),
        ("B₁",  0.15, "#475569", "#f1f5f9"),
        ("B₂",  0.14, "#475569", "#f1f5f9"),
        ("P₃",  0.38, NEG,   "#e0e7ff"),
        ("B₄",  0.16, "#475569", "#f1f5f9"),
        ("B₅",  0.15, "#475569", "#f1f5f9"),
        ("P₆",  0.44, NEG,   "#e0e7ff"),
        ("B₇",  0.19, "#475569", "#f1f5f9"),
        ("B₈",  0.20, "#475569", "#f1f5f9"),
        ("I₉",  0.94, POS,   "#fde8e8"),
    ]

    n = len(gop)
    slot = aw / (n + 0.3)
    bw = slot * 0.65

    for i, (name, val, stroke_col, fill_col) in enumerate(gop):
        bx = ox + 18 + i * slot
        bh = ah * val * 0.85
        by = oy - bh

        p.append(rect(bx, by, bw, bh, fill=fill_col, stroke=stroke_col, sw=1.6, rx=3))
        p.append(text(bx + bw / 2, oy + 14, name, size=11, color=stroke_col, bold=True))

        pct_lbl = f"{int(val * 100)}%"
        p.append(text(bx + bw / 2, by - 6, pct_lbl, size=9.5, color=stroke_col, bold=True))

    satd_pts = []
    for i in range(n):
        bx = ox + 18 + i * slot + bw / 2
        c_val = 0.42 + 0.38 * (i / float(n-1)) ** 1.5
        cy = oy - ah * (c_val * 0.82)
        satd_pts.append((bx, cy))

    d_satd = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in satd_pts)
    p.append(f'<path d="{d_satd}" fill="none" stroke="{FIELD}" stroke-width="2.2" stroke-dasharray="4,3"/>')
    p.append(text(ox + aw - 10, oy - ah + 16, "Складність сцени (SATD)", size=10, color=FIELD, bold=True, anchor="end"))

    render(os.path.join(OUT, "gop-bit-allocation.svg"), W, H, *p,
           title="Адаптивний розподіл бюджету бітів у структурі GOP")


# ── 4. vbv-feedback-loop: Контур зворотного зв'язку VBV-керування ──────────────
def fig_vbv_feedback_loop():
    W, H = 760, 360
    p = []

    y_mid = 100

    # Блок 1: Вхід
    tb1, w1, h1 = textbox(80, y_mid, "Вхідний кадр\n(Raw Frame)", size=11, pad=8, fill="#f8fafc", stroke="#64748b", bold=True)
    p.append(tb1)

    p.append(arrow(135, y_mid, 165, y_mid, color=INK, sw=1.6))

    # Блок 2: Оцінка складності
    tb2, w2, h2 = textbox(225, y_mid, "Оцінка складності\n(SATD / MAD)", size=11, pad=8, fill="#f0fdf4", stroke=FIELD, bold=True)
    p.append(tb2)

    p.append(arrow(285, y_mid, 315, y_mid, color=INK, sw=1.6))

    # Блок 3: Розподіл цільових бітів
    tb3, w3, h3 = textbox(380, y_mid, "Цільовий бюджет\nT_frame (GOP level)", size=11, pad=8, fill="#eff6ff", stroke=NEG, bold=True)
    p.append(tb3)

    p.append(arrow(445, y_mid, 475, y_mid, color=INK, sw=1.6))

    # Блок 4: Обчислення QP з VBV обмеженням
    tb4, w4, h4 = textbox(545, y_mid, "Розрахунок QP\nта λ = f(QP, VBV)", size=11, pad=8, fill="#fef3c7", stroke="#d97706", bold=True)
    p.append(tb4)

    p.append(arrow(615, y_mid, 645, y_mid, color=INK, sw=1.6))

    # Блок 5: Квантування / RDO / Кодування
    tb5, w5, h5 = textbox(700, y_mid, "RDO кодер\n(DCT + CABAC)", size=11, pad=8, fill="#fdf2f2", stroke=POS, bold=True)
    p.append(tb5)

    # Вихідний потік праворуч
    p.append(arrow(700, y_mid + 30, 700, 200, color=INK, sw=1.6))

    # Блок 6 (внизу праворуч): Реально витрачені біти S_actual
    tb6, w6, h6 = textbox(660, 230, "Вимірювання факту:\nS_actual бітів", size=11, pad=8, fill="#f8fafc", stroke=INK, bold=True)
    p.append(tb6)

    # Зворотний зв'язок: оновлення віртуального буфера VBV
    p.append(arrow(595, 230, 485, 230, color=POS, sw=1.8))

    # Блок 7 (внизу по центру): Модель віртуального буфера VBV
    tb7, w7, h7 = textbox(380, 230, "Віртуальний буфер VBV / HRD\nB(t) = B(t-1) + R_in·Δt − S_actual\nКонтроль Overflow / Underflow", size=10.5, pad=8, fill="#fef2f2", stroke=POS, bold=True)
    p.append(tb7)

    # Стрілка корекції вгору до Блоку 4 (Розрахунок QP)
    p.append(line(380, 195, 380, 160, color=POS, sw=1.8))
    p.append(line(380, 160, 545, 160, color=POS, sw=1.8))
    p.append(arrow(545, 160, 545, 135, color=POS, sw=1.8))
    p.append(text(465, 150, "Поправка QP (зворотний зв'язок)", size=10, color=POS, bold=True))

    # Стрілка зворотного зв'язку до оновлення моделі складності X = S * Qstep
    p.append(line(270, 230, 225, 230, color=FIELD, sw=1.6))
    p.append(arrow(225, 230, 225, 135, color=FIELD, sw=1.6))
    p.append(text(175, 190, "Оновлення X = S·Q", size=9.5, color=FIELD, bold=True))

    # Підсумкова рамка знизу
    tb_bot, _, _ = textbox(380, 320, "Замкнений контур регулювання: складність сцени задає стартовий прогноз, "
                                    "а буфер VBV жорстко коригує QP,\nзапобігаючи як зриву трансляції (спустошенню), так і перевищенню каналу.",
                           size=10, pad=6, fill="#f1f5f9", stroke="#94a3b8")
    p.append(tb_bot)

    render(os.path.join(OUT, "vbv-feedback-loop.svg"), W, H, *p,
           title="Контур зворотного зв'язку VBV-керування бітрейтом")


if __name__ == "__main__":
    fig_rate_distortion_curve()
    fig_hrd_leaky_bucket()
    fig_gop_bit_allocation()
    fig_vbv_feedback_loop()
    print("All figures generated successfully.")
