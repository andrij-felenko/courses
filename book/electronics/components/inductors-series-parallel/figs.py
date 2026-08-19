# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def coil_symbol(cx, cy, length=80, loops=4, r=10, color=LINE, sw=2.0):
    """Малює котушку індуктивності з півокружностей вздовж осі X."""
    parts = []
    step = length / loops
    x_start = cx - length / 2
    # Початковий дріт
    parts.append(line(x_start - 15, cy, x_start, cy, color=color, sw=sw))
    for i in range(loops):
        x0 = x_start + i * step
        x1 = x0 + step
        xm = (x0 + x1) / 2
        # Верхня арка (виток)
        path_str = ('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
                    'stroke="%s" stroke-width="%.1f"/>' % (x0, cy, step / 2, r, x1, cy, color, sw))
        parts.append(path_str)
    # Кінцевий дріт
    parts.append(line(x_start + length, cy, x_start + length + 15, cy, color=color, sw=sw))
    return "".join(parts)


def resistor_symbol(cx, cy, w=40, h=16, color=LINE, sw=1.8):
    """Малює символ резистора (прямокутник за стандартом)."""
    parts = []
    parts.append(line(cx - w / 2 - 12, cy, cx - w / 2, cy, color=color, sw=sw))
    parts.append(rect(cx - w / 2, cy - h / 2, w, h, fill="#ffffff", stroke=color, sw=sw, rx=1))
    parts.append(line(cx + w / 2, cy, cx + w / 2 + 12, cy, color=color, sw=sw))
    return "".join(parts)


# ── 1. Послідовне з'єднання незв'язаних котушок ─────────────────────────────
def fig_series_uncoupled():
    W, H = 760, 320
    parts = []
    cy = 130

    # Загальні виводи
    x_in = 50
    x_out = 710

    # Котушка 1 + DCR1
    cx_l1 = 170
    cx_r1 = 280
    # Котушка 2 + DCR2
    cx_l2 = 480
    cx_r2 = 590

    # Вхідний дріт
    parts.append(line(x_in, cy, cx_l1 - 55, cy, color=LINE, sw=2))
    parts.append(circle(x_in, cy, 4, fill=INK, stroke=INK))
    parts.append(text(x_in, cy - 14, "A", size=14, bold=True))

    # Секція 1 (L1 + DCR1)
    parts.append(coil_symbol(cx_l1, cy, length=70, loops=4, r=14, color=POS, sw=2.2))
    parts.append(text(cx_l1, cy - 26, "L₁", size=15, color=POS, bold=True))
    parts.append(line(cx_l1 + 50, cy, cx_r1 - 32, cy, color=LINE, sw=2))
    parts.append(resistor_symbol(cx_r1, cy, w=36, h=16, color=MUTED, sw=1.8))
    parts.append(text(cx_r1, cy - 20, "DCR₁", size=12, color=MUTED, bold=True))

    # З'єднувальний провід між 1 і 2
    parts.append(line(cx_r1 + 30, cy, cx_l2 - 55, cy, color=LINE, sw=2))
    parts.append(circle((cx_r1 + cx_l2) / 2 - 10, cy, 3, fill=MUTED, stroke=MUTED))

    # Секція 2 (L2 + DCR2)
    parts.append(coil_symbol(cx_l2, cy, length=70, loops=4, r=14, color=NEG, sw=2.2))
    parts.append(text(cx_l2, cy - 26, "L₂", size=15, color=NEG, bold=True))
    parts.append(line(cx_l2 + 50, cy, cx_r2 - 32, cy, color=LINE, sw=2))
    parts.append(resistor_symbol(cx_r2, cy, w=36, h=16, color=MUTED, sw=1.8))
    parts.append(text(cx_r2, cy - 20, "DCR₂", size=12, color=MUTED, bold=True))

    # Вихідний дріт
    parts.append(line(cx_r2 + 30, cy, x_out, cy, color=LINE, sw=2))
    parts.append(circle(x_out, cy, 4, fill=INK, stroke=INK))
    parts.append(text(x_out, cy - 14, "B", size=14, bold=True))

    # Струм i(t)
    parts.append(arrow(80, cy - 25, 140, cy - 25, color=POS, sw=2.4))
    parts.append(text(110, cy - 36, "i(t) спільний", size=12, color=POS, bold=True))

    # Спади напруг v1(t), v2(t)
    parts.append(line(cx_l1 - 50, cy + 40, cx_r1 + 25, cy + 40, color=POS, sw=1.5))
    parts.append(line(cx_l1 - 50, cy + 32, cx_l1 - 50, cy + 48, color=POS, sw=1.5))
    parts.append(line(cx_r1 + 25, cy + 32, cx_r1 + 25, cy + 48, color=POS, sw=1.5))
    parts.append(text((cx_l1 + cx_r1) / 2 - 10, cy + 56, "v₁(t) = L₁·(di/dt) + DCR₁·i", size=12, color=POS, bold=True))

    parts.append(line(cx_l2 - 50, cy + 40, cx_r2 + 25, cy + 40, color=NEG, sw=1.5))
    parts.append(line(cx_l2 - 50, cy + 32, cx_l2 - 50, cy + 48, color=NEG, sw=1.5))
    parts.append(line(cx_r2 + 25, cy + 32, cx_r2 + 25, cy + 48, color=NEG, sw=1.5))
    parts.append(text((cx_l2 + cx_r2) / 2 - 10, cy + 56, "v₂(t) = L₂·(di/dt) + DCR₂·i", size=12, color=NEG, bold=True))

    # Підсумковий блок
    parts.append(fitbox(140, 240, 480, 52,
                         "Незв'язані котушки (k = 0):\nL_eq = L₁ + L₂ + … + L_n        DCR_eq = DCR₁ + DCR₂ + … + DCR_n",
                         size=13, fill="#f4fbf7", stroke=FIELD, color=FIELD, bold=True))

    return render(os.path.join(OUT, 'series-uncoupled.svg'), W, H, *parts,
                  title="Послідовне з'єднання незв'язаних котушок (k = 0)")


# ── 2. Послідовне з'єднання магнітозв'язаних котушок ────────────────────────
def fig_series_coupled():
    W, H = 820, 440
    parts = []

    # Розділ на дві панелі: Ліва = Згідне ввімкнення, Права = Зустрічне ввімкнення
    p1_x = 210
    p2_x = 610
    cy = 150

    # ── Ліва панель: Згідне (Flux Aiding) ──
    parts.append(rect(20, 50, 375, 360, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    parts.append(text(p1_x, 75, "Згідне ввімкнення (Flux Aiding)", size=15, color=POS, bold=True))

    # Спільне магнітне осердя
    parts.append(rect(p1_x - 140, cy - 45, 280, 16, fill="#e1e4e8", stroke=MUTED, sw=1.5, rx=3))
    parts.append(text(p1_x, cy - 52, "Спільне магнітне осердя (k > 0)", size=11, color=MUTED, italic=True))

    # Котушка 1
    l1_x = p1_x - 70
    parts.append(coil_symbol(l1_x, cy, length=60, loops=3, r=13, color=POS, sw=2.2))
    parts.append(text(l1_x, cy - 18, "L₁", size=14, color=POS, bold=True))
    # Крапка L1 (початок зліва)
    parts.append(circle(l1_x - 40, cy - 18, 4.5, fill=POS, stroke=POS))

    # Котушка 2
    l2_x = p1_x + 70
    parts.append(coil_symbol(l2_x, cy, length=60, loops=3, r=13, color=POS, sw=2.2))
    parts.append(text(l2_x, cy - 18, "L₂", size=14, color=POS, bold=True))
    # Крапка L2 (початок зліва)
    parts.append(circle(l2_x - 40, cy - 18, 4.5, fill=POS, stroke=POS))

    # З'єднання між L1 і L2
    parts.append(line(l1_x + 45, cy, l2_x - 45, cy, color=LINE, sw=2))
    # Зовнішні проводи
    parts.append(line(40, cy, l1_x - 45, cy, color=LINE, sw=2))
    parts.append(line(l2_x + 45, cy, 375, cy, color=LINE, sw=2))
    parts.append(circle(40, cy, 4, fill=INK, stroke=INK))
    parts.append(circle(375, cy, 4, fill=INK, stroke=INK))

    # Стрілки струму
    parts.append(arrow(55, cy - 16, 95, cy - 16, color=POS, sw=2.0))
    parts.append(text(75, cy - 24, "i(t)", size=11, color=POS, bold=True))

    # Магнітні потоки (співнапрямлені)
    parts.append(arrow(l1_x - 30, cy + 30, l1_x + 30, cy + 30, color=FIELD, sw=2.2))
    parts.append(text(l1_x, cy + 46, "Φ₁ →", size=12, color=FIELD, bold=True))
    parts.append(arrow(l2_x - 30, cy + 30, l2_x + 30, cy + 30, color=FIELD, sw=2.2))
    parts.append(text(l2_x, cy + 46, "Φ₂ →", size=12, color=FIELD, bold=True))
    parts.append(text(p1_x, cy + 70, "Потоки складаються: Φ_сум = Φ₁ + Φ₂", size=12, color=FIELD, bold=True))

    # Формула згідного
    parts.append(fitbox(35, 260, 345, 135,
                         "Струм входить в обидві крапки:\nv = (L₁ + M)·(di/dt) + (L₂ + M)·(di/dt)\n\nL_eq = L₁ + L₂ + 2·M\nде M = k·√(L₁·L₂)",
                         size=12, fill="#fdf2f0", stroke=POS, color=POS, bold=True))

    # ── Права панель: Зустрічне (Flux Opposing) ──
    parts.append(rect(425, 50, 375, 360, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    parts.append(text(p2_x, 75, "Зустрічне ввімкнення (Flux Opposing)", size=15, color=NEG, bold=True))

    # Спільне магнітне осердя
    parts.append(rect(p2_x - 140, cy - 45, 280, 16, fill="#e1e4e8", stroke=MUTED, sw=1.5, rx=3))
    parts.append(text(p2_x, cy - 52, "Спільне магнітне осердя (k > 0)", size=11, color=MUTED, italic=True))

    # Котушка 1
    parts.append(coil_symbol(p2_x - 70, cy, length=60, loops=3, r=13, color=NEG, sw=2.2))
    parts.append(text(p2_x - 70, cy - 18, "L₁", size=14, color=NEG, bold=True))
    # Крапка L1 (зліва)
    parts.append(circle(p2_x - 110, cy - 18, 4.5, fill=NEG, stroke=NEG))

    # Котушка 2
    parts.append(coil_symbol(p2_x + 70, cy, length=60, loops=3, r=13, color=NEG, sw=2.2))
    parts.append(text(p2_x + 70, cy - 18, "L₂", size=14, color=NEG, bold=True))
    # Крапка L2 (справа — вихід)
    parts.append(circle(p2_x + 110, cy - 18, 4.5, fill=NEG, stroke=NEG))

    # З'єднання між L1 і L2
    parts.append(line(p2_x - 25, cy, p2_x + 25, cy, color=LINE, sw=2))
    # Зовнішні проводи
    parts.append(line(445, cy, p2_x - 115, cy, color=LINE, sw=2))
    parts.append(line(p2_x + 115, cy, 780, cy, color=LINE, sw=2))
    parts.append(circle(445, cy, 4, fill=INK, stroke=INK))
    parts.append(circle(780, cy, 4, fill=INK, stroke=INK))

    # Стрілки струму
    parts.append(arrow(460, cy - 16, 500, cy - 16, color=NEG, sw=2.0))
    parts.append(text(480, cy - 24, "i(t)", size=11, color=NEG, bold=True))

    # Магнітні потоки (протинапрямлені)
    parts.append(arrow(p2_x - 100, cy + 30, p2_x - 40, cy + 30, color=FIELD, sw=2.2))
    parts.append(text(p2_x - 70, cy + 46, "Φ₁ →", size=12, color=FIELD, bold=True))
    parts.append(arrow(p2_x + 100, cy + 30, p2_x + 40, cy + 30, color=POS, sw=2.2))
    parts.append(text(p2_x + 70, cy + 46, "← Φ₂", size=12, color=POS, bold=True))
    parts.append(text(p2_x, cy + 70, "Потоки віднімаються: Φ_сум = Φ₁ − Φ₂", size=12, color=POS, bold=True))

    # Формула зустрічного
    parts.append(fitbox(440, 260, 345, 135,
                         "Входить у крапку L₁, виходить з L₂:\nv = (L₁ − M)·(di/dt) + (L₂ − M)·(di/dt)\n\nL_eq = L₁ + L₂ − 2·M\n(при L₁=L₂, k=1: L_eq = 0)",
                         size=12, fill="#eef3fd", stroke=NEG, color=NEG, bold=True))

    return render(os.path.join(OUT, 'series-coupled-flux.svg'), W, H, *parts,
                  title="Послідовне з'єднання магнітозв'язаних котушок")


# ── 3. Паралельне з'єднання незв'язаних котушок ─────────────────────────────
def fig_parallel_uncoupled():
    W, H = 780, 400
    parts = []

    # Вузол входу/виходу
    nx_in = 160
    nx_out = 600
    top_y = 100
    bot_y = 230
    mid_y = 165

    # Вхідна лінія
    parts.append(line(40, mid_y, nx_in, mid_y, color=LINE, sw=2))
    parts.append(circle(40, mid_y, 4, fill=INK, stroke=INK))
    parts.append(text(40, mid_y - 14, "A (+)", size=14, bold=True, color=POS))
    parts.append(arrow(60, mid_y - 15, 120, mid_y - 15, color=POS, sw=2.5))
    parts.append(text(90, mid_y - 25, "i_total(t)", size=13, color=POS, bold=True))

    # Розгалуження входу
    parts.append(line(nx_in, top_y, nx_in, bot_y, color=LINE, sw=2.2))
    parts.append(circle(nx_in, mid_y, 5, fill=INK, stroke=INK))
    parts.append(circle(nx_in, top_y, 4, fill=INK, stroke=INK))
    parts.append(circle(nx_in, bot_y, 4, fill=INK, stroke=INK))

    # Верхня гілка (L1)
    parts.append(line(nx_in, top_y, 330, top_y, color=LINE, sw=2))
    parts.append(coil_symbol(380, top_y, length=70, loops=4, r=13, color=POS, sw=2.2))
    parts.append(text(380, top_y - 24, "L₁ (менша)", size=14, color=POS, bold=True))
    parts.append(line(430, top_y, nx_out, top_y, color=LINE, sw=2))
    parts.append(arrow(210, top_y - 12, 270, top_y - 12, color=POS, sw=2.8))
    parts.append(text(240, top_y - 22, "i₁(t) БІЛЬШИЙ", size=12, color=POS, bold=True))

    # Нижня гілка (L2)
    parts.append(line(nx_in, bot_y, 330, bot_y, color=LINE, sw=2))
    parts.append(coil_symbol(380, bot_y, length=70, loops=4, r=13, color=NEG, sw=2.2))
    parts.append(text(380, bot_y + 34, "L₂ (більша)", size=14, color=NEG, bold=True))
    parts.append(line(430, bot_y, nx_out, bot_y, color=LINE, sw=2))
    parts.append(arrow(210, bot_y - 12, 270, bot_y - 12, color=NEG, sw=1.8))
    parts.append(text(240, bot_y - 22, "i₂(t) менший", size=12, color=NEG, bold=True))

    # Зведення виходу
    parts.append(line(nx_out, top_y, nx_out, bot_y, color=LINE, sw=2.2))
    parts.append(circle(nx_out, mid_y, 5, fill=INK, stroke=INK))
    parts.append(circle(nx_out, top_y, 4, fill=INK, stroke=INK))
    parts.append(circle(nx_out, bot_y, 4, fill=INK, stroke=INK))

    # Вихідна лінія
    parts.append(line(nx_out, mid_y, 730, mid_y, color=LINE, sw=2))
    parts.append(circle(730, mid_y, 4, fill=INK, stroke=INK))
    parts.append(text(730, mid_y - 14, "B (−)", size=14, bold=True, color=NEG))

    # Напруга v(t) спільна
    parts.append(text(nx_in + 45, mid_y + 4, "v(t) спільна", size=11, color=MUTED, bold=True, anchor="start"))

    # Блок формули внизу
    parts.append(fitbox(150, 290, 480, 80,
                         "1/L_eq = 1/L₁ + 1/L₂   →   L_eq = (L₁·L₂)/(L₁ + L₂)\n\nРозподіл змінного струму: di₁/dt / di₂/dt = L₂/L₁ (обернено до L)",
                         size=12, fill="#f4fbf7", stroke=FIELD, color=FIELD, bold=True))

    return render(os.path.join(OUT, 'parallel-uncoupled.svg'), W, H, *parts,
                  title="Паралельне з'єднання незв'язаних котушок (розподіл струмів обернено до L)")


# ── 4. Паралельне з'єднання зв'язаних котушок та циркулюючий струм ──────────
def fig_parallel_coupled():
    W, H = 840, 420
    parts = []

    nx_in = 130
    nx_out = 500
    top_y = 110
    bot_y = 270
    mid_y = 190

    # Магнітне осердя
    parts.append(rect(220, mid_y - 8, 200, 16, fill="#e1e4e8", stroke=MUTED, sw=1.5, rx=3))
    parts.append(text(320, mid_y + 4, "Магнітний зв'язок M = k·√(L₁·L₂)", size=11, color=MUTED, bold=True))

    # Вхідний вузол
    parts.append(line(30, mid_y, nx_in, mid_y, color=LINE, sw=2))
    parts.append(circle(30, mid_y, 4, fill=INK, stroke=INK))
    parts.append(text(30, mid_y - 14, "Вхід", size=13, bold=True))
    parts.append(circle(nx_in, mid_y, 5, fill=INK, stroke=INK))
    parts.append(line(nx_in, top_y, nx_in, bot_y, color=LINE, sw=2))

    # Верхня котушка L1
    parts.append(line(nx_in, top_y, 280, top_y, color=LINE, sw=2))
    parts.append(coil_symbol(320, top_y, length=60, loops=3, r=13, color=POS, sw=2.2))
    parts.append(text(320, top_y - 20, "L₁", size=14, color=POS, bold=True))
    parts.append(circle(280, top_y - 18, 4.5, fill=POS, stroke=POS)) # Крапка зліва
    parts.append(line(360, top_y, nx_out, top_y, color=LINE, sw=2))

    # Нижня котушка L2
    parts.append(line(nx_in, bot_y, 280, bot_y, color=LINE, sw=2))
    parts.append(coil_symbol(320, bot_y, length=60, loops=3, r=13, color=NEG, sw=2.2))
    parts.append(text(320, bot_y + 30, "L₂", size=14, color=NEG, bold=True))
    parts.append(circle(280, bot_y - 18, 4.5, fill=NEG, stroke=NEG)) # Крапка зліва
    parts.append(line(360, bot_y, nx_out, bot_y, color=LINE, sw=2))

    # Вихідний вузол
    parts.append(line(nx_out, top_y, nx_out, bot_y, color=LINE, sw=2))
    parts.append(circle(nx_out, mid_y, 5, fill=INK, stroke=INK))
    parts.append(line(nx_out, mid_y, 550, mid_y, color=LINE, sw=2))
    parts.append(circle(550, mid_y, 4, fill=INK, stroke=INK))
    parts.append(text(550, mid_y - 14, "Вихід", size=13, bold=True))

    # Контурний циркулюючий струм
    parts.append(arrow(390, top_y + 15, 390, bot_y - 15, color=POS, sw=2.5))
    parts.append(arrow(200, bot_y - 15, 200, top_y + 15, color=POS, sw=2.5))
    parts.append(text(320, mid_y - 25, "i_циркуляційний (при асиметрії)", size=11, color=POS, bold=True))

    # Інформаційна панель праворуч
    parts.append(fitbox(570, 50, 250, 320,
                         "Еквівалентна індуктивність:\n\nL_eq = (L₁·L₂ − M²)\n       ————————————\n       L₁ + L₂ ∓ 2·M\n\nЗнак «−» у знаменнику:\nзгідне ввімкнення\n\nЗнак «+» у знаменнику:\nзустрічне ввімкнення\n\nНебезпека:\nПри L₁ = L₂ і k → 1:\nчисельник прямує до 0;\nбудь-яка асиметрія викликає\nнебезпечний циркулюючий струм!",
                         size=12, fill="#fdf2f0", stroke=POS, color=POS, bold=True))

    return render(os.path.join(OUT, 'parallel-coupled.svg'), W, H, *parts,
                  title="Паралельне з'єднання зв'язаних котушок і циркулюючі струми")


# ── 5. Застосування: багатофазний DC-DC зі зв'язаними дроселями ───────────────
def fig_multiphase_coupled():
    W, H = 860, 420
    parts = []

    sw1_x = 90
    sw2_x = 90
    l_x = 290
    out_x = 490

    top_y = 110
    bot_y = 270
    mid_y = 190

    # Блок Фаза 1 (комутатор SW1)
    parts.append(rect(sw1_x - 55, top_y - 35, 110, 70, fill="#fdf2f0", stroke=POS, sw=1.8, rx=6))
    parts.append(text(sw1_x, top_y - 12, "Phase 1 (SW₁)", size=13, color=POS, bold=True))
    parts.append(text(sw1_x, top_y + 12, "0° фазовий зсув", size=11, color=MUTED))

    # Блок Фаза 2 (комутатор SW2)
    parts.append(rect(sw2_x - 55, bot_y - 35, 110, 70, fill="#eef3fd", stroke=NEG, sw=1.8, rx=6))
    parts.append(text(sw2_x, bot_y - 12, "Phase 2 (SW₂)", size=13, color=NEG, bold=True))
    parts.append(text(sw2_x, bot_y + 12, "180° фазовий зсув", size=11, color=MUTED))

    # Спільний сердечник зв'язаного дроселя (Coupled Choke)
    parts.append(rect(l_x - 70, mid_y - 100, 140, 200, fill="#f6f8fa", stroke=MUTED, sw=2, rx=8))
    parts.append(text(l_x, mid_y - 80, "Coupled Core", size=12, color=INK, bold=True))
    parts.append(text(l_x, mid_y, "Зустрічний зв'язок\n(k < 0, компенсація\nпостійного потоку)", size=11, color=FIELD, bold=True))

    # Обмотка 1
    parts.append(line(sw1_x + 55, top_y, l_x - 40, top_y, color=LINE, sw=2))
    parts.append(coil_symbol(l_x, top_y, length=50, loops=3, r=12, color=POS, sw=2.2))
    parts.append(circle(l_x - 30, top_y - 16, 4.5, fill=POS, stroke=POS)) # Крапка входу
    parts.append(line(l_x + 40, top_y, out_x, top_y, color=LINE, sw=2))

    # Обмотка 2
    parts.append(line(sw2_x + 55, bot_y, l_x - 40, bot_y, color=LINE, sw=2))
    parts.append(coil_symbol(l_x, bot_y, length=50, loops=3, r=12, color=NEG, sw=2.2))
    parts.append(circle(l_x + 30, bot_y - 16, 4.5, fill=NEG, stroke=NEG)) # Крапка виходу (інверсна полярність)
    parts.append(line(l_x + 40, bot_y, out_x, bot_y, color=LINE, sw=2))

    # Зведення у вихідний вузол Vout
    parts.append(line(out_x, top_y, out_x, bot_y, color=LINE, sw=2.5))
    parts.append(circle(out_x, mid_y, 5, fill=INK, stroke=INK))
    parts.append(line(out_x, mid_y, out_x + 40, mid_y, color=LINE, sw=2.5))

    # Вихідний конденсатор Cout + навантаження
    parts.append(rect(out_x + 40, mid_y - 45, 75, 90, fill="#f4fbf7", stroke=FIELD, sw=2, rx=6))
    parts.append(text(out_x + 77, mid_y - 16, "V_out", size=14, color=FIELD, bold=True))
    parts.append(text(out_x + 77, mid_y + 4, "C_out +", size=11, color=MUTED))
    parts.append(text(out_x + 77, mid_y + 22, "CPU / GPU", size=11, color=INK, bold=True))

    # Панель переваг
    parts.append(fitbox(620, 50, 220, 140,
                         "Перевага 1: Пульсації фаз\n\nЗниження ΔI_L у 2–4 рази\nзавдяки взаємному\nнаведенню ЕРС",
                         size=12, fill="#f4fbf7", stroke=FIELD, color=FIELD, bold=True))

    parts.append(fitbox(620, 220, 220, 150,
                         "Перевага 2: Динамічний відгук\n\nПри стрибку навантаження\nфази перемикаються синфазно:\nпрацює мала індуктивність\nрозсіювання L_lk",
                         size=12, fill="#eef3fd", stroke=NEG, color=NEG, bold=True))

    return render(os.path.join(OUT, 'multiphase-coupled.svg'), W, H, *parts,
                  title="Багатофазний перетворювач зі зв'язаними дроселями (Coupled Inductors)")


if __name__ == '__main__':
    fig_series_uncoupled()
    fig_series_coupled()
    fig_parallel_uncoupled()
    fig_parallel_coupled()
    fig_multiphase_coupled()
    print("Всі фігури згенеровано успішно.")
