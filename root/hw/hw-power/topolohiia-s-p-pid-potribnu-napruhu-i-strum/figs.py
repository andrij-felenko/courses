# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HOT   = "#c0392b"
WARM  = "#e67e22"
COOL  = "#2457d6"
GREEN = "#27ae60"
GREY  = "#d8dee5"
DARK  = "#2c3e50"


# ── 1. Порівняння архітектур xSyP та xPyS ───────────────────────────────────
def fig_xsyp_vs_xpys():
    W, H = 760, 430
    frags = []

    # Заголовок фігури
    frags.append(text(W / 2, 28, "Порівняння архітектур: xSyP (послідовні групи) проти xPyS (паралельні гілки)", size=15, bold=True))

    # ── Ліва колонка: xSyP (3S2P) ──
    lx = 190
    frags.append(rect(25, 48, 335, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(lx, 72, "xSyP: Послідовно з паралелей (3S2P)", size=14, bold=True, color=GREEN))
    frags.append(text(lx, 90, "Стандарт індустрії: самобаланс у групі, 1 BMS", size=11, color=MUTED))

    # 3 паралельні групи (кожна по 2 комірки)
    group_y = [115, 195, 275]
    for i, gy in enumerate(group_y):
        # Рамка 2P-групи
        frags.append(rect(45, gy, 295, 62, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=5))
        frags.append(text(55, gy + 16, "Група %d (1S2P)" % (i + 1), size=10, bold=True, color=MUTED, anchor="start"))
        
        # Дві комірки в групі
        for c, cx in enumerate([135, 235]):
            frags.append(rect(cx, gy + 8, 70, 46, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
            frags.append(rect(cx + 64, gy + 22, 6, 18, fill="#94a3b8", stroke=LINE, sw=1.0, rx=1))
            frags.append(text(cx + 35, gy + 32, "3.6 В", size=11, bold=True))
            frags.append(text(cx + 35, gy + 45, "комірка", size=9, color=MUTED))

        # Спільна шина паралелі (з'єднує 2 комірки)
        frags.append(line(125, gy + 31, 135, gy + 31, color=COOL, sw=2.5))
        frags.append(line(205, gy + 31, 235, gy + 31, color=COOL, sw=2.5))
        frags.append(line(305, gy + 31, 315, gy + 31, color=HOT, sw=2.5))

    # Послідовні перемички між групами
    frags.append(line(315, 146, 315, 175, color=LINE, sw=2.0))
    frags.append(line(315, 175, 45, 175, color=LINE, sw=2.0))
    frags.append(line(45, 175, 45, 226, color=LINE, sw=2.0))
    frags.append(line(45, 226, 125, 226, color=LINE, sw=2.0))

    frags.append(line(315, 226, 315, 255, color=LINE, sw=2.0))
    frags.append(line(315, 255, 45, 255, color=LINE, sw=2.0))
    frags.append(line(45, 255, 45, 306, color=LINE, sw=2.0))
    frags.append(line(45, 306, 125, 306, color=LINE, sw=2.0))

    # Виводи BMS (всього 4 точки)
    frags.append(text(lx, 360, "Лінії BMS: всього 4 дроти (S + 1 = 4)", size=11, bold=True, color=DARK))
    frags.append(text(lx, 378, "При відмові 1 банки ємність падає на 1/P", size=10, color=MUTED))
    frags.append(text(lx, 394, "Комірки в паралелі зрівнюють напругу самі", size=10, color=GREEN))

    # ── Роздільник ──
    frags.append(line(380, 50, 380, 410, color="#e2e8f0", sw=1.5, dash="5 5"))

    # ── Права колонка: xPyS (2P3S) ──
    rx = 570
    frags.append(rect(400, 48, 335, 365, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(rx, 72, "xPyS: Паралельно з ланцюгів (2P3S)", size=14, bold=True, color=HOT))
    frags.append(text(rx, 90, "Рідкісна схема: ризик кільцевих струмів", size=11, color=MUTED))

    # Дві незалежні послідовні гілки
    for b, bx in enumerate([420, 575]):
        frags.append(rect(bx, 115, 140, 222, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=5))
        frags.append(text(bx + 70, 132, "Гілка %d (3S)" % (b + 1), size=10, bold=True, color=MUTED))

        # 3 комірки послідовно в гілці
        for s, sy in enumerate([145, 205, 265]):
            frags.append(rect(bx + 35, sy, 70, 46, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
            frags.append(rect(bx + 99, sy + 14, 6, 18, fill="#94a3b8", stroke=LINE, sw=1.0, rx=1))
            frags.append(text(bx + 70, sy + 24, "3.6 В", size=11, bold=True))
            frags.append(text(bx + 70, sy + 37, "комірка", size=9, color=MUTED))
            if s > 0:
                frags.append(line(bx + 70, sy - 14, bx + 70, sy, color=LINE, sw=1.8))

    # Замикання кінців гілок у паралель зверху й знизу
    frags.append(line(490, 115, 490, 105, color=COOL, sw=2.0))
    frags.append(line(645, 115, 645, 105, color=COOL, sw=2.0))
    frags.append(line(490, 105, 645, 105, color=COOL, sw=2.5))
    frags.append(circle(567, 105, 4, fill=COOL))
    frags.append(text(567, 98, "− Bat", size=10, bold=True, color=COOL))

    frags.append(line(490, 337, 490, 347, color=HOT, sw=2.0))
    frags.append(line(645, 337, 645, 347, color=HOT, sw=2.0))
    frags.append(line(490, 347, 645, 347, color=HOT, sw=2.5))
    frags.append(circle(567, 347, 4, fill=HOT))
    frags.append(text(567, 360, "+ Bat", size=10, bold=True, color=HOT))

    frags.append(text(rx, 378, "Потрібно 2 незалежні BMS або 8 дротів контролю", size=10, color=HOT))
    frags.append(text(rx, 394, "При просадці однієї гілки — неконтрольований струм", size=10, color=MUTED))

    render(os.path.join(OUT, 'sp-topologies-xsyp-vs-xpys.svg'), W, H, *frags)


# ── 2. Геометрія підключення шин: U-схема проти Z-схеми ────────────────────
def fig_busbar_geometry():
    W, H = 760, 420
    frags = []

    frags.append(text(W / 2, 26, "Розподіл струму по шині: однобічне (U) проти діагонального (Z) підключення", size=15, bold=True))

    # ── Верхній блок: Однобічне підключення (U-схема, нерівномірне) ──
    frags.append(rect(25, 46, 710, 168, fill="#fff5f5", stroke="#fca5a5", sw=1.2, rx=6))
    frags.append(text(45, 68, "Однобічне підключення (U-потік) — перекіс струмів", size=13, bold=True, color=HOT, anchor="start"))
    frags.append(text(45, 84, "Перша банка має найкоротший шлях і перевантажується на 35–40%", size=11, color=MUTED, anchor="start"))

    # 4 комірки в паралелі
    cell_x = [200, 330, 460, 590]
    cell_currents_u = ["11.8 А", "8.2 А", "5.8 А", "4.2 А"]
    cell_colors_u = [HOT, WARM, DARK, COOL]

    # Верхня шина (+)
    frags.append(rect(140, 100, 520, 12, fill="#f97316", stroke=LINE, sw=1.0, rx=2))
    frags.append(text(125, 109, "+ Вихід (30 А)", size=10, bold=True, color=HOT, anchor="end"))
    frags.append(circle(140, 106, 5, fill=HOT))

    # Нижня шина (-)
    frags.append(rect(140, 166, 520, 12, fill="#3b82f6", stroke=LINE, sw=1.0, rx=2))
    frags.append(text(125, 175, "− Вихід (30 А)", size=10, bold=True, color=COOL, anchor="end"))
    frags.append(circle(140, 172, 5, fill=COOL))

    for i, cx in enumerate(cell_x):
        frags.append(rect(cx - 28, 116, 56, 46, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        frags.append(text(cx, 134, "Банка %d" % (i + 1), size=10, bold=True))
        frags.append(text(cx, 150, cell_currents_u[i], size=11, bold=True, color=cell_colors_u[i]))
        # з'єднання з шинами
        frags.append(line(cx, 112, cx, 116, color=LINE, sw=2.0))
        frags.append(line(cx, 162, cx, 166, color=LINE, sw=2.0))

    frags.append(text(665, 140, "Дальня банка недовантажена", size=10, color=MUTED, anchor="start"))

    # ── Нижній блок: Діагональне підключення (Z-схема / Reverse-Return) ──
    frags.append(rect(25, 230, 710, 168, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=6))
    frags.append(text(45, 252, "Діагональне підключення (Z-потік / Reverse-Return) — ідеальний баланс", size=13, bold=True, color=GREEN, anchor="start"))
    frags.append(text(45, 268, "Сумарна довжина шини (верх + низ) однакова для кожної банки: L_top + L_bot = const", size=11, color=MUTED, anchor="start"))

    # Верхня шина (+) з клемою зліва
    frags.append(rect(140, 284, 520, 12, fill="#f97316", stroke=LINE, sw=1.0, rx=2))
    frags.append(text(125, 293, "+ Вихід (30 А)", size=10, bold=True, color=HOT, anchor="end"))
    frags.append(circle(140, 290, 5, fill=HOT))

    # Нижня шина (-) з клемою СПРАВА
    frags.append(rect(140, 350, 520, 12, fill="#3b82f6", stroke=LINE, sw=1.0, rx=2))
    frags.append(text(675, 359, "− Вихід (30 А)", size=10, bold=True, color=COOL, anchor="start"))
    frags.append(circle(660, 356, 5, fill=COOL))

    for i, cx in enumerate(cell_x):
        frags.append(rect(cx - 28, 300, 56, 46, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        frags.append(text(cx, 318, "Банка %d" % (i + 1), size=10, bold=True))
        frags.append(text(cx, 334, "7.5 А", size=11, bold=True, color=GREEN))
        # з'єднання з шинами
        frags.append(line(cx, 296, cx, 300, color=LINE, sw=2.0))
        frags.append(line(cx, 346, cx, 350, color=LINE, sw=2.0))

    render(os.path.join(OUT, 'diagonal-vs-same-side-busbar.svg'), W, H, *frags)


# ── 3. Нерівномірність струмів при розкиді внутрішнього опору ΔIR ────────────
def fig_cell_mismatch_ir():
    W, H = 760, 380
    frags = []

    frags.append(text(W / 2, 26, "Розподіл струму в 1S3P групі при розкиді внутрішнього опору (ΔIR)", size=15, bold=True))

    # Загальна рамка схеми
    frags.append(rect(30, 48, 700, 312, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))

    # Верхня рейка (+)
    frags.append(line(80, 85, 680, 85, color=HOT, sw=3.0))
    frags.append(circle(80, 85, 5, fill=HOT))
    frags.append(text(75, 75, "+ Клема (30 А)", size=11, bold=True, color=HOT, anchor="start"))

    # Нижня рейка (-)
    frags.append(line(80, 275, 680, 275, color=COOL, sw=3.0))
    frags.append(circle(80, 275, 5, fill=COOL))
    frags.append(text(75, 295, "− Клема (30 А)", size=11, bold=True, color=COOL, anchor="start"))

    # 3 паралельні гілки
    branches = [
        {"x": 190, "r": "15 мОм", "i": "14.5 А", "p": "3.15 Вт", "color": HOT, "sub": "Низький R → Перегрів!"},
        {"x": 380, "r": "25 мОм", "i": "8.7 А",  "p": "1.89 Вт", "color": WARM, "sub": "Номінальний стан"},
        {"x": 570, "r": "40 мОм", "i": "5.4 А",  "p": "1.17 Вт", "color": COOL, "sub": "Високий R → Ледарює"}
    ]

    for b in branches:
        bx = b["x"]
        # Дроти до гілки
        frags.append(line(bx, 85, bx, 110, color=LINE, sw=1.8))
        frags.append(line(bx, 250, bx, 275, color=LINE, sw=1.8))

        # Блок моделі комірки (ЕРС + R_внутр)
        frags.append(rect(bx - 65, 110, 130, 140, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
        
        # ЕРС
        frags.append(rect(bx - 35, 122, 70, 28, fill="#e2e8f0", stroke=LINE, sw=1.0, rx=3))
        frags.append(text(bx, 140, "E = 3.6 В", size=10, bold=True))

        # Внутрішній опір
        frags.append(rect(bx - 45, 160, 90, 26, fill="#fef3c7", stroke="#d97706", sw=1.0, rx=3))
        frags.append(text(bx, 177, "R = " + b["r"], size=10, bold=True, color="#b45309"))

        # Струм та тепловиділення
        frags.append(text(bx, 204, "I = " + b["i"], size=12, bold=True, color=b["color"]))
        frags.append(text(bx, 222, "P = I²R = " + b["p"], size=10, bold=True, color=b["color"]))
        frags.append(text(bx, 240, b["sub"], size=9, color=MUTED))

    # Висновок внизу фігури
    frags.append(text(W / 2, 330, "При розкиді опору в 2.6 раза: банка з R = 15 мОм виділяє майже втричі більше тепла (3.15 Вт vs 1.17 Вт),", size=11, bold=True, color=DARK))
    frags.append(text(W / 2, 348, "що спричиняє її прискорене старіння та деградацію всієї паралельної групи.", size=11, color=MUTED))

    render(os.path.join(OUT, 'cell-mismatch-current-sharing.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_xsyp_vs_xpys()
    fig_busbar_geometry()
    fig_cell_mismatch_ir()
    print("All figures generated successfully.")
