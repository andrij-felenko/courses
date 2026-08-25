# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Порівняння топологій: Двообмотковий трансформатор проти Автотрансформатора ──
def fig_topology_comparison():
    W, H = 820, 390
    els = []

    # Тло блоків
    els.append(rect(15, 15, 385, 360, fill="#fbfcfd", stroke="#d0d7de", sw=1.2, rx=8))
    els.append(rect(420, 15, 385, 360, fill="#fbfcfd", stroke="#d0d7de", sw=1.2, rx=8))

    # Заголовки блоків
    els.append(text(207, 44, "Двообмотковий трансформатор", size=15, bold=True, color=INK))
    els.append(text(207, 63, "Повна гальванічна розв'язка", size=12, color=MUTED))

    els.append(text(612, 44, "Автотрансформатор (знижувальний)", size=15, bold=True, color=INK))
    els.append(text(612, 63, "Спільна обмотка без розв'язки", size=12, color=MUTED))

    # --- Лівий блок: Двообмотковий ---
    # Осердя
    els.append(rect(185, 100, 44, 180, fill="#e1e4e8", stroke=LINE, sw=1.5, rx=4))
    els.append(text(207, 195, "Осердя", size=12, bold=True, color=LINE))

    # Первинна обмотка
    els.append(line(50, 120, 160, 120, color=POS, sw=2.2))
    els.append(line(50, 260, 160, 260, color=LINE, sw=2.2))
    for i in range(4):
        y = 135 + i * 32
        els.append(rect(145, y, 32, 22, fill="#fff5f5", stroke=POS, sw=1.8, rx=3))
    els.append(line(160, 120, 160, 135, color=POS, sw=1.8))
    els.append(line(160, 247, 160, 260, color=LINE, sw=1.8))

    # Вторинна обмотка
    els.append(line(254, 140, 360, 140, color=NEG, sw=2.2))
    els.append(line(254, 240, 360, 240, color=LINE, sw=2.2))
    for i in range(3):
        y = 155 + i * 28
        els.append(rect(238, y, 32, 20, fill="#f0f7ff", stroke=NEG, sw=1.8, rx=3))
    els.append(line(254, 140, 254, 155, color=NEG, sw=1.8))
    els.append(line(254, 225, 254, 240, color=LINE, sw=1.8))

    # Підписи напруг і струмів ліворуч
    els.append(arrow(65, 110, 115, 110, color=POS, sw=1.8))
    els.append(text(90, 102, "I₁", size=13, bold=True, color=POS))
    els.append(arrow(300, 130, 350, 130, color=NEG, sw=1.8))
    els.append(text(325, 122, "I₂", size=13, bold=True, color=NEG))

    els.append(text(80, 195, "V₁ (N₁)", size=14, bold=True, color=POS))
    els.append(text(335, 195, "V₂ (N₂)", size=14, bold=True, color=NEG))

    # Бар'єр ізоляції
    els.append(line(207, 85, 207, 98, color="#27ae60", sw=1.5, dash="4 3"))
    els.append(line(207, 282, 207, 295, color="#27ae60", sw=1.5, dash="4 3"))

    # Плашка потужності ліворуч
    b1, _, _ = textbox(207, 325, "Трансформаторна потужність: P_tr = P_out\nУся енергія (100 %) йде через магнітне осердя", size=12, pad=6, fill="#f6f8fa", stroke="#d0d7de")
    els.append(b1)

    # --- Правий блок: Автотрансформатор ---
    # Осердя
    els.append(rect(590, 100, 44, 180, fill="#e1e4e8", stroke=LINE, sw=1.5, rx=4))
    els.append(text(612, 195, "Осердя", size=12, bold=True, color=LINE))

    # Спільна неперервна обмотка праворуч
    # Верхня частина: послідовна (N1 - N2)
    els.append(line(455, 120, 565, 120, color=POS, sw=2.2))
    for i in range(2):
        y = 130 + i * 26
        els.append(rect(550, y, 30, 18, fill="#fff5f5", stroke=POS, sw=1.8, rx=3))

    # Вузол відгалуження (відвід)
    els.append(circle(565, 185, 4, fill=LINE, stroke=LINE, sw=1))
    els.append(line(565, 185, 765, 185, color=NEG, sw=2.2))

    # Нижня частина: спільна (N2)
    for i in range(3):
        y = 195 + i * 24
        els.append(rect(550, y, 30, 18, fill="#e8f8f0", stroke=FIELD, sw=1.8, rx=3))

    els.append(line(565, 120, 565, 130, color=POS, sw=1.8))
    els.append(line(565, 170, 565, 195, color=LINE, sw=1.8))
    els.append(line(565, 255, 565, 270, color=LINE, sw=1.8))

    # Спільна нижня лінія (земля/нуль)
    els.append(line(455, 270, 765, 270, color=LINE, sw=2.2))

    # Стрілки струмів
    els.append(arrow(470, 110, 520, 110, color=POS, sw=1.8))
    els.append(text(495, 102, "I₁", size=13, bold=True, color=POS))

    els.append(arrow(700, 175, 750, 175, color=NEG, sw=1.8))
    els.append(text(725, 167, "I₂", size=13, bold=True, color=NEG))

    # Струм у спільній секції (різниця I2 - I1)
    els.append(arrow(535, 245, 535, 215, color=FIELD, sw=1.8))
    els.append(text(510, 232, "I₂ − I₁", size=11, bold=True, color=FIELD))

    els.append(text(485, 155, "V₁ (N₁)", size=13, bold=True, color=POS))
    els.append(text(735, 230, "V₂ (N₂)", size=13, bold=True, color=NEG))

    # Позначення секцій
    els.append(text(655, 150, "Послідовна: N₁−N₂", size=11, color=POS))
    els.append(text(655, 230, "Спільна: N₂", size=11, color=FIELD))

    # Плашка потужності праворуч
    b2, _, _ = textbox(612, 325, "P_tr = P_out · (1 − 1/n)  [магнітна частка]\nP_cond = P_out / n        [гальванічна частка]", size=12, pad=6, fill="#f6f8fa", stroke="#d0d7de")
    els.append(b2)

    render(os.path.join(OUT, "topology-comparison.svg"), W, H, *els)


# ── 2. Вузловий баланс і компенсація струмів у спільній обмотці ───────────
def fig_current_cancellation():
    W, H = 780, 360
    els = []

    # Головна схема вузла
    els.append(rect(20, 20, 420, 320, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    els.append(text(230, 48, "Розподіл струмів у витках", size=15, bold=True, color=INK))

    # Вхідний провід
    els.append(line(60, 90, 210, 90, color=POS, sw=2.5))
    els.append(arrow(90, 80, 150, 80, color=POS, sw=2.0))
    els.append(text(120, 70, "Вхід I₁ = 10 А", size=12, bold=True, color=POS))

    # Послідовна обмотка
    els.append(line(210, 90, 210, 115, color=POS, sw=2.2))
    for i in range(2):
        y = 115 + i * 26
        els.append(rect(195, y, 30, 18, fill="#fff5f5", stroke=POS, sw=1.8, rx=3))
    els.append(text(255, 138, "N_ser = 20 вит.", size=11, color=POS))
    els.append(arrow(185, 115, 185, 155, color=POS, sw=1.8))
    els.append(text(168, 140, "I₁", size=11, bold=True, color=POS))

    # Вузол відводу
    els.append(circle(210, 175, 5, fill=LINE, stroke=LINE, sw=1))
    els.append(text(210, 165, "Вузол A", size=11, bold=True, color=LINE, anchor="end"))

    # Вихідний провід до навантаження
    els.append(line(210, 175, 380, 175, color=NEG, sw=2.5))
    els.append(arrow(260, 165, 330, 165, color=NEG, sw=2.0))
    els.append(text(295, 155, "Вихід I₂ = 12 А", size=12, bold=True, color=NEG))

    # Спільна обмотка
    for i in range(3):
        y = 190 + i * 26
        els.append(rect(195, y, 30, 18, fill="#e8f8f0", stroke=FIELD, sw=1.8, rx=3))
    els.append(text(255, 225, "N_com = 100 вит.", size=11, color=FIELD))

    # Струм у спільній обмотці — вгору до вузла A
    els.append(arrow(185, 260, 185, 200, color=FIELD, sw=2.2))
    els.append(text(152, 235, "I_com", size=12, bold=True, color=FIELD))

    # Нижня шина
    els.append(line(210, 256, 210, 285, color=LINE, sw=2.2))
    els.append(line(60, 285, 380, 285, color=LINE, sw=2.5))
    els.append(text(110, 305, "Спільний нуль (N)", size=12, color=MUTED))

    # Правий блок: Розрахунок і фізичний висновок
    els.append(rect(460, 20, 300, 320, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    els.append(text(610, 48, "Числовий баланс (n = 1.2)", size=14, bold=True, color=INK))

    info = [
        "V₁ = 240 В,  V₂ = 200 В",
        "P_out = 200 В · 12 А = 2400 Вт",
        "────────────────────────",
        "За 1-м законом Кірхгофа у вузлі A:",
        "I₂ = I₁ + I_com",
        "I_com = I₂ − I₁",
        "I_com = 12 А − 10 А = 2 А",
        "────────────────────────",
        "Струм у спільних витках в 6 разів",
        "менший за струм навантаження!",
        "Втрати I²·R скорочено в 36 разів."
    ]
    for idx, line_text in enumerate(info):
        is_bold = "I_com" in line_text or "скорочено" in line_text
        col = FIELD if "I_com =" in line_text else INK
        els.append(text(480, 80 + idx * 22, line_text, size=11, color=col, anchor="start", bold=is_bold))

    render(os.path.join(OUT, "current-cancellation.svg"), W, H, *els)


# ── 3. Графік розподілу потужності: P_tr vs P_cond ────────────────────────
def fig_power_split_curve():
    W, H = 760, 380
    els = []

    # Осі координат
    x0, y0 = 90, 300
    w_ax, h_ax = 600, 230

    # Тло графіка
    els.append(rect(x0, y0 - h_ax, w_ax, h_ax, fill="#fbfcfd", stroke="#e2e8f0", sw=1.0, rx=4))

    # Виділення зони високої ефективності (n від 1 до 2)
    x_n2 = x0 + (2.0 - 1.0) / (6.0 - 1.0) * w_ax
    els.append(rect(x0, y0 - h_ax, x_n2 - x0, h_ax, fill="#ecfdf5", stroke="none"))
    els.append(text((x0 + x_n2) / 2, y0 - h_ax + 20, "Зона найбільшого виграшу (n < 2)", size=11, bold=True, color=FIELD))

    # Сітка по Y (від 0% до 100%)
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = y0 - p * h_ax
        els.append(line(x0, y, x0 + w_ax, y, color="#e2e8f0", sw=1.0, dash="3 3"))
        els.append(text(x0 - 12, y + 4, "%d %%" % int(p * 100), size=11, color=MUTED, anchor="end"))

    # Сітка по X (n від 1.0 до 6.0)
    for n_val in range(1, 7):
        x = x0 + (n_val - 1.0) / (6.0 - 1.0) * w_ax
        els.append(line(x, y0, x, y0 - h_ax, color="#e2e8f0", sw=1.0, dash="3 3"))
        els.append(text(x, y0 + 18, "%.1f" % n_val, size=11, color=MUTED))

    # Криві
    pts_tr = []
    pts_cond = []
    steps = 100
    for i in range(steps + 1):
        n_val = 1.0 + (i / steps) * 5.0
        x = x0 + (n_val - 1.0) / 5.0 * w_ax
        p_tr = 1.0 - 1.0 / n_val
        p_cond = 1.0 / n_val
        y_tr = y0 - p_tr * h_ax
        y_cond = y0 - p_cond * h_ax
        pts_tr.append("%.1f,%.1f" % (x, y_tr))
        pts_cond.append("%.1f,%.1f" % (x, y_cond))

    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts_tr), POS))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts_cond), NEG))

    # Підписи кривих
    els.append(text(x0 + 380, y0 - 0.72 * h_ax, "P_tr = P_out · (1 − 1/n)  [Трансформаторна]", size=12, bold=True, color=POS, anchor="start"))
    els.append(text(x0 + 380, y0 - 0.28 * h_ax, "P_cond = P_out / n  [Прохідна]", size=12, bold=True, color=NEG, anchor="start"))

    # Точка перетину при n = 2.0 (50 / 50)
    els.append(circle(x_n2, y0 - 0.5 * h_ax, 5, fill="#ffffff", stroke=LINE, sw=2))
    els.append(text(x_n2 + 8, y0 - 0.5 * h_ax + 18, "n = 2.0 (50% / 50%)", size=11, bold=True, color=LINE, anchor="start"))

    # Підписи осей
    els.append(text(x0 + w_ax / 2, y0 + 42, "Коефіцієнт трансформації n = V₁ / V₂", size=13, bold=True, color=INK))
    els.append(text(x0 - 50, y0 - h_ax / 2, "Частка потужності", size=13, bold=True, color=INK, anchor="middle"))

    # Заголовок графіка
    els.append(text(W / 2, 28, "Баланс потужностей автотрансформатора від коефіцієнта n", size=15, bold=True, color=INK))

    render(os.path.join(OUT, "power-split-curve.svg"), W, H, *els)


# ── 4. Будова лабораторного автотрансформатора (ЛАТР) ──────────────────────
def fig_variac_construction():
    W, H = 800, 390
    els = []

    # Тло
    els.append(rect(15, 15, 770, 360, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    els.append(text(W / 2, 42, "Конструкція ЛАТР та механізм вугільної щітки", size=15, bold=True, color=INK))

    # Ліва частина: Тороїдальне осердя та обмотка
    cx, cy = 220, 210
    r_out, r_in = 110, 60

    # Тороїд осердя
    els.append(circle(cx, cy, r_out, fill="#e2e8f0", stroke=LINE, sw=2.0))
    els.append(circle(cx, cy, r_in, fill="#ffffff", stroke=LINE, sw=2.0))
    els.append(text(cx, cy, "Тороїд", size=12, bold=True, color=MUTED))

    # Витки обмотки по колу
    n_turns = 24
    for i in range(n_turns):
        angle = i * (2 * math.pi / n_turns)
        x1 = cx + (r_in + 2) * math.cos(angle)
        y1 = cy + (r_in + 2) * math.sin(angle)
        x2 = cx + (r_out - 2) * math.cos(angle)
        y2 = cy + (r_out - 2) * math.sin(angle)
        els.append(line(x1, y1, x2, y2, color=POS, sw=2.2))

    # Зачищена контактна доріжка (верхнє півколо)
    els.append('<path d="M %f %f A %f %f 0 0 1 %f %f" fill="none" stroke="%s" stroke-width="8" stroke-opacity="0.4"/>'
               % (cx - 85, cy, 85, 85, cx + 85, cy, "#f59e0b"))

    # Поворотний важіль зі щіткою
    ang_brush = -math.pi / 3  # ~60 градусів угору-вправо
    bx = cx + 85 * math.cos(ang_brush)
    by = cy + 85 * math.sin(ang_brush)
    els.append(line(cx, cy, bx, by, color=LINE, sw=3.5))
    els.append(circle(cx, cy, 8, fill=LINE, stroke=LINE, sw=1))
    els.append(rect(bx - 8, by - 8, 16, 16, fill="#334155", stroke=LINE, sw=1.5, rx=2))
    els.append(text(bx + 16, by - 12, "Графітовий ролик / щітка", size=11, bold=True, color=INK, anchor="start"))

    # Виводи
    els.append(line(cx - r_out, cy + 30, cx - r_out - 40, cy + 30, color=LINE, sw=2))
    els.append(text(cx - r_out - 45, cy + 35, "0 В (N)", size=11, color=MUTED, anchor="end"))
    els.append(line(cx + r_out, cy + 30, cx + r_out + 40, cy + 30, color=POS, sw=2))
    els.append(text(cx + r_out + 45, cy + 35, "230 В (L)", size=11, color=POS, anchor="start"))

    els.append(line(cx, cy, cx, cy + r_out + 40, color=NEG, sw=2.2))
    els.append(text(cx, cy + r_out + 55, "Вихід (0…250 В)", size=12, bold=True, color=NEG))

    # Права частина: Збільшений розріз замикання сусідніх витків
    els.append(rect(460, 75, 305, 275, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    els.append(text(612, 100, "Вузол контакту: розв'язання дилеми", size=13, bold=True, color=INK))

    # Два сусідніх витки
    els.append(rect(510, 165, 32, 70, fill="#fed7aa", stroke="#ea580c", sw=1.8, rx=4))
    els.append(rect(560, 165, 32, 70, fill="#fed7aa", stroke="#ea580c", sw=1.8, rx=4))
    els.append(text(526, 205, "N_k", size=11, bold=True, color="#c2410c"))
    els.append(text(576, 205, "N_k+1", size=11, bold=True, color="#c2410c"))

    # Графітова щітка, що накриває обидва витки
    els.append(rect(500, 135, 102, 24, fill="#475569", stroke=LINE, sw=2.0, rx=3))
    els.append(text(551, 151, "Графітова щітка (R_brush)", size=10, bold=True, color="#ffffff"))

    # Напруга між витками
    els.append(arrow(526, 245, 576, 245, color=POS, sw=1.5))
    els.append(text(551, 262, "e_витка ≈ 0.7 В", size=11, color=POS))

    # Пояснення фізики
    info_latr = [
        "1. Щітка одночасно торкається 2 витків.",
        "2. Мідний контакт дав би I_кз = 0.7В/1мОм = 700 А!",
        "3. Графіт має високий поперечний опір R_щ,",
        "   що обмежує паразитичний струм I_кз < 1.5 А,",
        "   не даючи виткам перегрітися й зваритися."
    ]
    for idx, txt in enumerate(info_latr):
        col = POS if "700 А" in txt else INK
        els.append(text(475, 280 + idx * 14, txt, size=10, color=col, anchor="start"))

    render(os.path.join(OUT, "variac-construction.svg"), W, H, *els)


# ── 5. Небезпека ураження при обриві нейтралі ──────────────────────────────
def fig_broken_neutral_hazard():
    W, H = 820, 380
    els = []

    # Дві панелі: Нормальний режим проти Обриву нейтралі
    els.append(rect(15, 15, 385, 350, fill="#f0fdf4", stroke="#86efac", sw=1.2, rx=8))
    els.append(rect(420, 15, 385, 350, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=8))

    # Заголовки
    els.append(text(207, 44, "Нормальний режим (N заземлено)", size=14, bold=True, color=FIELD))
    els.append(text(612, 44, "Аварія: обрив нейтралі (N розірвано)", size=14, bold=True, color=POS))

    # --- Ліва панель: Норма ---
    # Вхідна фаза L (230 В) і нуль N (0 В)
    els.append(line(45, 90, 140, 90, color=POS, sw=2.2))
    els.append(text(40, 94, "L (230 В)", size=11, bold=True, color=POS, anchor="end"))

    els.append(line(45, 250, 360, 250, color=NEG, sw=2.2))
    els.append(text(40, 254, "N (0 В)", size=11, bold=True, color=NEG, anchor="end"))
    # Заземлення нейтралі
    els.append(line(100, 250, 100, 275, color=LINE, sw=1.5))
    els.append(line(85, 275, 115, 275, color=LINE, sw=1.5))
    els.append(line(90, 280, 110, 280, color=LINE, sw=1.5))
    els.append(line(95, 285, 105, 285, color=LINE, sw=1.5))
    els.append(text(100, 302, "PE (Земля)", size=10, color=MUTED))

    # Обмотка автотрансформатора
    els.append(line(140, 90, 140, 110, color=POS, sw=2))
    for i in range(4):
        y = 110 + i * 28
        els.append(rect(125, y, 30, 20, fill="#ffffff", stroke=LINE, sw=1.6, rx=2))
    els.append(line(140, 222, 140, 250, color=NEG, sw=2))

    # Відвід V2 = 110 В
    els.append(line(140, 166, 260, 166, color=NEG, sw=2.2))
    els.append(text(200, 155, "V_вих = 110 В", size=11, bold=True, color=NEG))

    # Навантаження
    els.append(rect(260, 150, 50, 115, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    els.append(text(285, 210, "R_нав", size=12, bold=True, color=LINE))
    els.append(line(285, 166, 285, 150, color=NEG, sw=1.5))
    els.append(line(285, 250, 285, 265, color=NEG, sw=1.5))

    # Потенціал корпусу
    b_norm, _, _ = textbox(207, 330, "Потенціал навантаження відносно землі:\nV = 110 В  (розрахунковий рівень)", size=11, pad=5, fill="#ffffff", stroke="#86efac")
    els.append(b_norm)

    # --- Права панель: Аварія ---
    els.append(line(450, 90, 545, 90, color=POS, sw=2.2))
    els.append(text(445, 94, "L (230 В)", size=11, bold=True, color=POS, anchor="end"))

    # Обрив нейтралі (хрестик)
    els.append(line(450, 250, 490, 250, color=NEG, sw=2.2))
    els.append(line(495, 243, 515, 257, color=POS, sw=2.5))
    els.append(line(495, 257, 515, 243, color=POS, sw=2.5))
    els.append(text(505, 235, "ОБРИВ", size=10, bold=True, color=POS))
    els.append(line(520, 250, 765, 250, color=POS, sw=2.2, dash="4 3"))

    # Обмотка під фазою
    els.append(line(545, 90, 545, 110, color=POS, sw=2))
    for i in range(4):
        y = 110 + i * 28
        els.append(rect(530, y, 30, 20, fill="#fee2e2", stroke=POS, sw=1.6, rx=2))
    els.append(line(545, 222, 545, 250, color=POS, sw=2))

    # Відвід під повною фазою 230 В
    els.append(line(545, 166, 665, 166, color=POS, sw=2.2))

    # Навантаження та людина
    els.append(rect(665, 150, 50, 115, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    els.append(text(690, 210, "R_нав", size=12, bold=True, color=POS))

    # Знак небезпеки
    els.append(circle(745, 166, 14, fill="#fef08a", stroke="#ca8a04", sw=2))
    els.append(text(745, 172, "⚡", size=15, bold=True, color="#854d0e"))

    # Стрілка ураження струмом
    els.append(text(730, 205, "Фаза 230 В на", size=11, bold=True, color=POS, anchor="start"))
    els.append(text(730, 220, "всіх клемах!", size=11, bold=True, color=POS, anchor="start"))

    b_dang, _, _ = textbox(612, 330, "НЕБЕЗПЕКА: при розриві нуля весь автотрансформатор\nі прилади на виході опиняються під фазою 230 В!", size=11, pad=5, fill="#ffffff", stroke="#fca5a5")
    els.append(b_dang)

    render(os.path.join(OUT, "broken-neutral-hazard.svg"), W, H, *els)


if __name__ == '__main__':
    fig_topology_comparison()
    fig_current_cancellation()
    fig_power_split_curve()
    fig_variac_construction()
    fig_broken_neutral_hazard()
    print("All 5 figures generated successfully.")
