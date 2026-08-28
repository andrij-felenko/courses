# -*- coding: utf-8 -*-
"""Фігури до теми «Струм і тензодавач як дотик».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG


def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.2f,%.2f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def gnd(x, y):
    return (line(x, y, x, y + 6, color=LINE, sw=2)
            + line(x - 12, y + 6, x + 12, y + 6, color=LINE, sw=2.4)
            + line(x - 7, y + 11, x + 7, y + 11, color=LINE, sw=2)
            + line(x - 3, y + 16, x + 3, y + 16, color=LINE, sw=2))


# ── 1. Оцінка сили за струмом та бар'єр тертя в редукторі ───────────────────
def fig_motor_current_friction():
    W, H = 760, 420
    f = []

    # Графік: вісь X — зовнішній момент, вісь Y — виміряний струм мотора
    x0, y0 = 130, 240
    xr, yt = 700, 75
    xl, yb = 60, 390

    # Осі
    f.append(arrow(xl, y0, xr, y0, color=LINE, sw=1.8))
    f.append(arrow(x0, yb, x0, yt, color=LINE, sw=1.8))

    f.append(text(xr - 20, y0 + 22, "Зовнішній момент на валу τ_ext  →", size=11.5, color=INK, anchor="end"))
    f.append('<text x="32" y="%.1f" font-family="%s" font-size="11.5" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 32 %.1f)">Струм двигуна I_q  →</text>'
             % ((y0 + yt) / 2, FONT, INK, (y0 + yt) / 2))

    # Зона сухого тертя (мертва зона) навколо нуля
    coulomb_w = 75
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
             'stroke="#c0392b" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.75" rx="4"/>'
             % (x0 - coulomb_w, yt + 20, 2 * coulomb_w, (yb - yt - 40)))

    f.append(text(x0, y0 - 100, "Зона нечутливості (сухе тертя Кулона)", size=11, color=RED, bold=True))
    f.append(text(x0, y0 - 84, "струм не реагує на слабкий контакт", size=10, color=MUTED))

    # Ідеальна пряма без тертя (пунктир)
    f.append(line(x0 - 150, y0 + 100, x0 + 150, y0 - 100, color=MUTED, sw=1.5, dash="5 4"))
    f.append(text(x0 + 155, y0 - 105, "Ідеал без тертя: I = τ / (N · K_t)", size=10.5, color=MUTED, anchor="start"))

    # Реальна крива з гістерезисом та тертям (прямий хід і зворотний)
    pts_fwd = [
        (x0 - 200, y0 + 150),
        (x0 - coulomb_w, y0 + 45),
        (x0 - coulomb_w, y0),
        (x0 + coulomb_w, y0),
        (x0 + coulomb_w, y0 - 45),
        (x0 + 200, y0 - 150)
    ]
    f.append(polyline(pts_fwd, color=NEG, sw=2.6))
    f.append(text(x0 + 180, y0 - 125, "Реальний відгук струму", size=11, color=NEG, bold=True, anchor="start"))

    # Позначення редуктора та передавального числа
    bx = fitbox(550, 310, 180, 60,
                "Редуктор N:1\nТертя росте з N\nІнерція росте як N²",
                size=11, fill="#eaf0fd", stroke=NEG, color=INK)
    f.append(bx)

    return render(os.path.join(IMG, "motor-current-friction.svg"), W, H, *f,
                  title="Оцінка сили за струмом: вплив сухого тертя та мертвої зони редуктора")


# ── 2. Тензоміст Вітстона на балці вигину ─────────────────────────────────────
def fig_wheatstone_bridge_strain():
    W, H = 760, 440
    f = []

    # Ліва частина: балка із закріпленням
    bx0, by0 = 60, 110
    bw, bh = 220, 60

    # Затискач (опора)
    f.append(rect(bx0, by0 - 20, 30, bh + 40, fill="#dcdfe4", stroke=LINE, sw=2, rx=2))
    for i in range(5):
        f.append(line(bx0 - 10, by0 - 15 + i * 20, bx0, by0 - 5 + i * 20, color=LINE, sw=1.5))

    # Сама балка
    f.append(rect(bx0 + 30, by0, bw, bh, fill="#f4f6f8", stroke=LINE, sw=2, rx=4))
    f.append(text(bx0 + 30 + bw / 2, by0 + bh / 2 + 5, "Пружна балка (алюміній/сталь)", size=11, color=MUTED))

    # Сила F на кінці балки
    fx = bx0 + 30 + bw - 15
    f.append(arrow(fx, by0 - 45, fx, by0 - 5, color=RED, sw=2.8))
    f.append(text(fx, by0 - 52, "Сила F", size=12, color=RED, bold=True))

    # Тензорезистори на верхній поверхні (розтяг: R1, R3)
    f.append(rect(bx0 + 65, by0 - 8, 45, 8, fill="#fdecea", stroke=RED, sw=1.6, rx=2))
    f.append(text(bx0 + 87, by0 - 14, "R1 (+ε)", size=10, color=RED, bold=True))

    f.append(rect(bx0 + 135, by0 - 8, 45, 8, fill="#fdecea", stroke=RED, sw=1.6, rx=2))
    f.append(text(bx0 + 157, by0 - 14, "R3 (+ε)", size=10, color=RED, bold=True))

    # Тензорезистори на нижній поверхні (стиск: R2, R4)
    f.append(rect(bx0 + 65, by0 + bh, 45, 8, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=2))
    f.append(text(bx0 + 87, by0 + bh + 20, "R2 (−ε)", size=10, color=NEG, bold=True))

    f.append(rect(bx0 + 135, by0 + bh, 45, 8, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=2))
    f.append(text(bx0 + 157, by0 + bh + 20, "R4 (−ε)", size=10, color=NEG, bold=True))

    # Пояснення деформації
    f.append(text(bx0 + 30 + bw / 2, by0 + bh + 50, "Верхні волокна розтягуються (+ΔR),\nнижні — стискаються (−ΔR)", size=11, color=INK))

    # Права частина: ромб моста Вітстона
    mx0, my0 = 530, 230
    mr = 95

    top_node = (mx0, my0 - mr)
    bot_node = (mx0, my0 + mr)
    left_node = (mx0 - mr, my0)
    right_node = (mx0 + mr, my0)

    # Живлення V_EXC
    f.append(line(top_node[0], top_node[1], top_node[0], top_node[1] - 30, color=RED, sw=2))
    f.append(text(top_node[0], top_node[1] - 36, "+V_EXC (збудження)", size=11, color=RED, bold=True))

    f.append(line(bot_node[0], bot_node[1], bot_node[0], bot_node[1] + 30, color=LINE, sw=2))
    f.append(gnd(bot_node[0], bot_node[1] + 30))

    # Плечі моста: резистори R1, R2, R4, R3
    # Top-Left: R1 (+ε)
    f.append(line(top_node[0], top_node[1], left_node[0], left_node[1], color=LINE, sw=1.8))
    f.append(rect(mx0 - mr / 2 - 18, my0 - mr / 2 - 10, 36, 20, fill="#fdecea", stroke=RED, sw=1.8, rx=3))
    f.append(text(mx0 - mr / 2, my0 - mr / 2 + 5, "R1", size=11, color=RED, bold=True))

    # Bottom-Left: R2 (−ε)
    f.append(line(left_node[0], left_node[1], bot_node[0], bot_node[1], color=LINE, sw=1.8))
    f.append(rect(mx0 - mr / 2 - 18, my0 + mr / 2 - 10, 36, 20, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    f.append(text(mx0 - mr / 2, my0 + mr / 2 + 5, "R2", size=11, color=NEG, bold=True))

    # Top-Right: R4 (−ε)
    f.append(line(top_node[0], top_node[1], right_node[0], right_node[1], color=LINE, sw=1.8))
    f.append(rect(mx0 + mr / 2 - 18, my0 - mr / 2 - 10, 36, 20, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=3))
    f.append(text(mx0 + mr / 2, my0 - mr / 2 + 5, "R4", size=11, color=NEG, bold=True))

    # Bottom-Right: R3 (+ε)
    f.append(line(right_node[0], right_node[1], bot_node[0], bot_node[1], color=LINE, sw=1.8))
    f.append(rect(mx0 + mr / 2 - 18, my0 + mr / 2 - 10, 36, 20, fill="#fdecea", stroke=RED, sw=1.8, rx=3))
    f.append(text(mx0 + mr / 2, my0 + mr / 2 + 5, "R3", size=11, color=RED, bold=True))

    # Вимірювальна діагональ: V_SIG+ та V_SIG-
    f.append(circle(left_node[0], left_node[1], 4, fill=LINE, stroke=LINE))
    f.append(circle(right_node[0], right_node[1], 4, fill=LINE, stroke=LINE))

    f.append(line(left_node[0], left_node[1], left_node[0] - 25, left_node[1], color=FIELD, sw=2))
    f.append(text(left_node[0] - 30, left_node[1] + 4, "V_SIG+", size=11, color=FIELD, bold=True, anchor="end"))

    f.append(line(right_node[0], right_node[1], right_node[0] + 25, right_node[1], color=FIELD, sw=2))
    f.append(text(right_node[0] + 30, right_node[1] + 4, "V_SIG−", size=11, color=FIELD, bold=True, anchor="start"))

    # Підсумкова формула в рамці
    f.append(rect(mx0 - 130, my0 + mr + 45, 260, 32, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(mx0, my0 + mr + 66, "V_out = V_EXC · GF · ε   (4× чутливість)", size=11.5, color=FIELD, bold=True))

    return render(os.path.join(IMG, "wheatstone-bridge-strain.svg"), W, H, *f,
                  title="Тензоміст Вітстона: мостова схема на згинальній балці")


# ── 3. Бінокулярна зсувна балка тензодавача ──────────────────────────────────
def fig_binocular_load_cell_mechanics():
    W, H = 760, 400
    f = []

    x0, y0 = 90, 80
    lw, lh = 580, 200

    # Основний контур металевого бруска (алюміній)
    f.append(rect(x0, y0, lw, lh, fill="#f4f6f8", stroke=LINE, sw=2.4, rx=6))

    # Жорстке ліве кріплення (база)
    f.append(rect(x0, y0, 90, lh, fill="#e5e7eb", stroke=LINE, sw=2, rx=4))
    f.append(circle(x0 + 45, y0 + 50, 10, fill="#ffffff", stroke=LINE, sw=2))
    f.append(circle(x0 + 45, y0 + 150, 10, fill="#ffffff", stroke=LINE, sw=2))
    f.append(text(x0 + 45, y0 + lh / 2 + 5, "Нерухома база", size=11, color=INK, bold=True))

    # Рухомий правий фланець (прикладання навантаження)
    f.append(rect(x0 + lw - 90, y0, 90, lh, fill="#e5e7eb", stroke=LINE, sw=2, rx=4))
    f.append(circle(x0 + lw - 45, y0 + 50, 10, fill="#ffffff", stroke=LINE, sw=2))
    f.append(circle(x0 + lw - 45, y0 + 150, 10, fill="#ffffff", stroke=LINE, sw=2))
    f.append(text(x0 + lw - 45, y0 + lh / 2 + 5, "Рухомий фланець", size=11, color=INK, bold=True))

    # Внутрішній виріз: два отвори (бінокуляр) з центральним прорізом
    hole1_cx = x0 + 200
    hole2_cx = x0 + 380
    hole_cy = y0 + lh / 2
    hole_r = 45

    # Центральний паз
    f.append(rect(hole1_cx, hole_cy - 12, hole2_cx - hole1_cx, 24, fill="#ffffff", stroke=LINE, sw=2))
    # Два круглі отвори
    f.append(circle(hole1_cx, hole_cy, hole_r, fill="#ffffff", stroke=LINE, sw=2))
    f.append(circle(hole2_cx, hole_cy, hole_r, fill="#ffffff", stroke=LINE, sw=2))

    # Тонкі пружні перемички (flexure hinges)
    # Зони деформації — над і під отворами
    f.append(rect(hole1_cx - 20, y0 + 4, 40, 10, fill="#fdecea", stroke=RED, sw=1.5, rx=2))
    f.append(text(hole1_cx, y0 - 8, "R1 (розтяг)", size=10, color=RED, bold=True))

    f.append(rect(hole2_cx - 20, y0 + 4, 40, 10, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=2))
    f.append(text(hole2_cx, y0 - 8, "R2 (стиск)", size=10, color=NEG, bold=True))

    f.append(rect(hole1_cx - 20, y0 + lh - 14, 40, 10, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=2))
    f.append(text(hole1_cx, y0 + lh + 22, "R4 (стиск)", size=10, color=NEG, bold=True))

    f.append(rect(hole2_cx - 20, y0 + lh - 14, 40, 10, fill="#fdecea", stroke=RED, sw=1.5, rx=2))
    f.append(text(hole2_cx, y0 + lh + 22, "R3 (розтяг)", size=10, color=RED, bold=True))

    # Стрілка навантаження F
    f.append(arrow(x0 + lw - 45, y0 - 55, x0 + lw - 45, y0 - 10, color=RED, sw=3))
    f.append(text(x0 + lw - 45, y0 - 62, "Сила F", size=13, color=RED, bold=True))

    # Пояснення 4-ланкового паралелограма
    f.append(text(W / 2, y0 + lh + 65,
                  "Паралелограмний механізм усуває вплив плеча прикладання сили:\n"
                  "вимірюється суто вертикальний зсув без чутливості до моменту перекидання",
                  size=11.5, color="#1e3a8a"))

    return render(os.path.join(IMG, "binocular-load-cell-mechanics.svg"), W, H, *f,
                  title="Механіка бінокулярної балки: паралелограмний механізм компенсації плеча сили")


# ── 4. Шестиосьовий силомоментний давач і матриця декуплінгу ───────────────────
def fig_six_axis_ft_sensor():
    W, H = 760, 430
    f = []

    # Ліва частина: структурна схема хрестовини Мальтійського хреста
    cx, cy = 190, 225
    cr_outer = 125
    cr_inner = 38

    # Зовнішнє кільце
    f.append(circle(cx, cy, cr_outer, fill="#f8fafc", stroke=LINE, sw=2))
    # Внутрішня втулка (центр)
    f.append(circle(cx, cy, cr_inner, fill="#e2e8f0", stroke=LINE, sw=2))
    f.append(text(cx, cy + 4, "Втулка", size=10.5, color=INK, bold=True))

    # 4 пружні промені (радіальні балки)
    beam_w = 22
    # Північ (Y+)
    f.append(rect(cx - beam_w / 2, cy - cr_outer, beam_w, cr_outer - cr_inner, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(rect(cx - beam_w / 2 + 2, cy - cr_outer + 25, beam_w - 4, 18, fill="#fdecea", stroke=RED, sw=1.2))
    f.append(text(cx, cy - cr_outer - 10, "+Y (Міст 1)", size=10, color=RED, bold=True))

    # Південь (Y−)
    f.append(rect(cx - beam_w / 2, cy + cr_inner, beam_w, cr_outer - cr_inner, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(rect(cx - beam_w / 2 + 2, cy + cr_inner + 30, beam_w - 4, 18, fill="#fdecea", stroke=RED, sw=1.2))
    f.append(text(cx, cy + cr_outer + 18, "−Y (Міст 2)", size=10, color=RED, bold=True))

    # Схід (X+)
    f.append(rect(cx + cr_inner, cy - beam_w / 2, cr_outer - cr_inner, beam_w, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(rect(cx + cr_inner + 30, cy - beam_w / 2 + 2, 18, beam_w - 4, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(cx + cr_outer + 35, cy + 4, "+X (Міст 3)", size=10, color=NEG, bold=True))

    # Захід (X−)
    f.append(rect(cx - cr_outer, cy - beam_w / 2, cr_outer - cr_inner, beam_w, fill="#ffffff", stroke=LINE, sw=1.8))
    f.append(rect(cx - cr_outer + 25, cy - beam_w / 2 + 2, 18, beam_w - 4, fill="#eaf0fd", stroke=NEG, sw=1.2))
    f.append(text(cx - cr_outer - 35, cy + 4, "−X (Міст 4)", size=10, color=NEG, bold=True))

    # Центральні осі Z
    f.append(circle(cx, cy, 8, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(cx + 16, cy - 14, "Z, Mz", size=10, color=POS, bold=True))

    # Права частина: калібрувальна матриця перетворення сигналів у вектор сил і моментів
    mx0, my0 = 540, 225

    f.append(rect(mx0 - 150, my0 - 130, 310, 260, fill="#ffffff", stroke=LINE, sw=2, rx=8))
    f.append(text(mx0 + 5, my0 - 105, "Матриця розділення каналів (6×6)", size=12, color=INK, bold=True))

    f.append(text(mx0 - 110, my0 - 60, "⎡ Fx ⎤", size=11, color=NEG, bold=True))
    f.append(text(mx0 - 110, my0 - 38, "⎢ Fy ⎥", size=11, color=NEG, bold=True))
    f.append(text(mx0 - 110, my0 - 16, "⎢ Fz ⎥", size=11, color=NEG, bold=True))
    f.append(text(mx0 - 110, my0 + 6, "⎢ Mx ⎥", size=11, color=RED, bold=True))
    f.append(text(mx0 - 110, my0 + 28, "⎢ My ⎥", size=11, color=RED, bold=True))
    f.append(text(mx0 - 110, my0 + 50, "⎣ Mz ⎦", size=11, color=RED, bold=True))

    f.append(text(mx0 - 75, my0 - 5, "=", size=16, color=INK, bold=True))

    f.append(rect(mx0 - 60, my0 - 75, 120, 140, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    f.append(text(mx0, my0 - 10, "Калібрувальна\nматриця\nC (6×6)", size=11, color=NEG, bold=True))

    f.append(text(mx0 + 72, my0 - 5, "·", size=18, color=INK, bold=True))

    f.append(text(mx0 + 105, my0 - 60, "⎡ V₁ − V₁₀ ⎤", size=10.5, color=FIELD, bold=True))
    f.append(text(mx0 + 105, my0 - 38, "⎢ V₂ − V₂₀ ⎥", size=10.5, color=FIELD, bold=True))
    f.append(text(mx0 + 105, my0 - 16, "⎢ V₃ − V₃₀ ⎥", size=10.5, color=FIELD, bold=True))
    f.append(text(mx0 + 105, my0 + 6, "⎢ V₄ − V₄₀ ⎥", size=10.5, color=FIELD, bold=True))
    f.append(text(mx0 + 105, my0 + 28, "⎢ V₅ − V₅₀ ⎥", size=10.5, color=FIELD, bold=True))
    f.append(text(mx0 + 105, my0 + 50, "⎣ V₆ − V₆₀ ⎦", size=10.5, color=FIELD, bold=True))

    f.append(text(W / 2, H - 15, "Матриця C усуває взаємний вплив осей (Cross-talk) та перетворює вольти в ньютони й ньютон-метри", size=11, color="#374151"))

    return render(os.path.join(IMG, "six-axis-ft-sensor.svg"), W, H, *f,
                  title="6-осьовий силомоментний давач: структура хрестовини та калібрувальна матриця")


# ── 5. Спостерігач узагальненого імпульсу та детектування зіткнень ────────────
def fig_momentum_observer_collision():
    W, H = 760, 420
    f = []

    # Верхня частина: блок-схема спостерігача
    bx0, by0 = 60, 65

    # Блок: Вхідні сигнали q, dq, tau
    b1, w1, h1 = textbox(120, by0 + 35, "Датчики приводу:\nПоложення q, швидкість q̇\nКерівний момент τ", size=10.5, fill="#f4f6f8", stroke=LINE)
    f.append(b1)

    # Блок: Модель динаміки
    b2, w2, h2 = textbox(360, by0 + 35, "Модель динаміки робота:\np(t) = M(q)q̇ (імпульс)\nКориоліс Cᵀ(q,q̇)q̇ + Гравітація g(q)", size=10.5, fill="#eaf0fd", stroke=NEG)
    f.append(b2)

    # Блок: Інтегратор нев'язки
    b3, w3, h3 = textbox(620, by0 + 35, "Фільтр нев'язки r(t):\nṙ = K_I · [τ_ext - r]\nБез обчислення q̈!", size=10.5, fill="#fdecea", stroke=RED)
    f.append(b3)

    # Стрілки між блоками
    f.append(arrow(120 + w1 / 2, by0 + 35, 360 - w2 / 2, by0 + 35, color=LINE, sw=1.8))
    f.append(arrow(360 + w2 / 2, by0 + 35, 620 - w3 / 2, by0 + 35, color=LINE, sw=1.8))

    # Нижня частина: часові діаграми удару/зіткнення
    gx0, gy0 = 90, 365
    gxr, gyt = 680, 205

    f.append(arrow(gx0, gy0, gxr, gy0, color=LINE, sw=1.8))
    f.append(arrow(gx0, gy0, gx0, gyt, color=LINE, sw=1.8))

    f.append(text(gxr - 10, gy0 + 22, "Час t  →", size=11, color=INK, anchor="end"))
    f.append('<text x="32" y="%.1f" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 32 %.1f)">Нев\'язка r(t) / Момент  →</text>'
             % ((gy0 + gyt) / 2, FONT, INK, (gy0 + gyt) / 2))

    # Динамічний поріг (пунктир червоний)
    thr_y = gy0 - 75
    f.append(line(gx0, thr_y, gxr - 30, thr_y, color=RED, sw=1.5, dash="6 4"))
    f.append(text(gxr - 35, thr_y - 8, "Динамічний поріг спрацювання τ_thresh", size=10.5, color=RED, bold=True, anchor="end"))

    # Сигнал нев'язки r(t)
    impact_t = gx0 + 260
    n = 100
    pts_r = [(gx0, gy0 - 10)]

    for i in range(1, n):
        x = gx0 + i * (gxr - gx0 - 50) / n
        if x < impact_t:
            # Шуми моделі / спокій
            y = gy0 - 12 + 4 * math.sin(i * 0.8)
        elif x < impact_t + 60:
            # Різкий стрибок від контакту
            progress = (x - impact_t) / 60.0
            y = gy0 - 12 - (gy0 - gyt - 30) * math.sin(progress * math.pi / 2)
        else:
            # Спад після аварійної зупинки
            y = gyt + 30 + 15 * math.exp(-(x - impact_t - 60) * 0.03)
        pts_r.append((x, y))

    f.append(polyline(pts_r, color=NEG, sw=2.6))
    f.append(text(impact_t + 130, gyt + 45, "Нев'язка r(t) ≈ τ_ext", size=11, color=NEG, bold=True))

    # Точка спрацювання аварійного захисту
    f.append(circle(impact_t + 25, thr_y, 5, fill=RED, stroke=LINE, sw=1.5))
    f.append(line(impact_t + 25, thr_y, impact_t + 25, gy0, color=RED, sw=1.2, dash="3 3"))
    f.append(text(impact_t + 25, gy0 + 18, "Зіткнення! (t_det < 5 мс)", size=10.5, color=RED, bold=True))

    return render(os.path.join(IMG, "momentum-observer-collision.svg"), W, H, *f,
                  title="Спостерігач імпульсу: детектування зіткнення за стрибком нев'язки без подвійного диференціювання")


if __name__ == "__main__":
    fig_motor_current_friction()
    fig_wheatstone_bridge_strain()
    fig_binocular_load_cell_mechanics()
    fig_six_axis_ft_sensor()
    fig_momentum_observer_collision()
    print("OK: 5 фігур у", IMG)
