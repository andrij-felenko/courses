# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Форми осердь».
Генерує SVG-фігури у підтеку ./img/ за допомогою svgkit.
"""
import sys, os, math

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/electronics/components/core-geometry/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def rect_dash(x, y, w, h, fill="none", stroke=LINE, sw=1.5, rx=6, dash="4,3"):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>' %
            (x, y, w, h, rx, fill, stroke, sw, dash))


def circle_dash(cx, cy, r, fill="none", stroke=LINE, sw=1.5, dash="4,3"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))


# ── 1. Порівняння родин геометрій осердь ──────────────────────────────────────
def fig_geometries():
    W, H = 840, 400
    p = []
    p.append(text(W / 2, 28, "Порівняння основних геометрій магнітних осердь", size=16, bold=True))
    p.append(text(W / 2, 48, "Розподіл магнітопроводу, розміщення обмотки та ступінь екранування", size=12, color=MUTED, italic=True))

    cols = [
        {"name": "Тороїд (Toroid)", "sub": "Кільцеве осердя", "cx": 115, "emi": "Мінімальне EMI (360°)", "emi_col": FIELD},
        {"name": "Ш-подібне (E / ETD)", "sub": "Класичне каркасне", "cx": 325, "emi": "Помірне (відкриті боки)", "emi_col": "#d35400"},
        {"name": "Броньове (RM / PQ)", "sub": "Чашкове екрановане", "cx": 535, "emi": "Дуже низьке EMI", "emi_col": FIELD},
        {"name": "Планарне (Planar)", "sub": "Плоске під друк. плату", "cx": 735, "emi": "Низький профіль, мале EMI", "emi_col": FIELD},
    ]

    for col in cols:
        cx = col["cx"]
        # Рамка картки
        p.append(rect(cx - 95, 65, 190, 315, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
        p.append(text(cx, 88, col["name"], size=12.5, bold=True, color=INK))
        p.append(text(cx, 104, col["sub"], size=10.5, color=MUTED))

        # Нижня плашка EMI
        p.append(rect(cx - 85, 335, 170, 32, fill="#f0f4f8", stroke="#d0d7de", sw=1, rx=4))
        p.append(text(cx, 355, col["emi"], size=10, bold=True, color=col["emi_col"]))

    # 1.1 Малюнок тороїда (cx = 115)
    t_cx, t_cy = 115, 205
    p.append(circle(t_cx, t_cy, 52, fill="#e2e7ec", stroke="#5a626a", sw=2))
    p.append(circle(t_cx, t_cy, 28, fill="#fafbfc", stroke="#5a626a", sw=2))
    # Обмотка (витки навколо тороїда)
    for ang_deg in range(0, 360, 40):
        rad = math.radians(ang_deg)
        x1 = t_cx + 28 * math.cos(rad)
        y1 = t_cy + 28 * math.sin(rad)
        x2 = t_cx + 52 * math.cos(rad)
        y2 = t_cy + 52 * math.sin(rad)
        p.append(line(x1, y1, x2, y2, color="#c0392b", sw=3.5))
    # Магнітна лінія
    p.append(circle_dash(t_cx, t_cy, 40, fill="none", stroke=FIELD, sw=1.6, dash="4,3"))
    p.append(text(t_cx, 285, "Обмотка по кільцю", size=10.5, color=INK))
    p.append(text(t_cx, 300, "Немає стиків осердя", size=10, color=MUTED))

    # 1.2 Малюнок E-Core (cx = 325)
    e_cx, e_cy = 325, 205
    # Ліве E як єдиний замкнений контур path
    d_left = ("M %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d Z" %
              (e_cx - 55, e_cy - 48,
               e_cx - 3,  e_cy - 48,
               e_cx - 3,  e_cy - 32,
               e_cx - 39, e_cy - 32,
               e_cx - 39, e_cy - 10,
               e_cx - 3,  e_cy - 10,
               e_cx - 3,  e_cy + 10,
               e_cx - 39, e_cy + 10,
               e_cx - 39, e_cy + 32,
               e_cx - 3,  e_cy + 32,
               e_cx - 3,  e_cy + 48,
               e_cx - 55, e_cy + 48))
    p.append('<path d="%s" fill="#e2e7ec" stroke="#5a626a" stroke-width="1.8"/>' % d_left)

    # Праве E як єдиний замкнений контур path
    d_right = ("M %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d Z" %
               (e_cx + 55, e_cy - 48,
                e_cx + 3,  e_cy - 48,
                e_cx + 3,  e_cy - 32,
                e_cx + 39, e_cy - 32,
                e_cx + 39, e_cy - 10,
                e_cx + 3,  e_cy - 10,
                e_cx + 3,  e_cy + 10,
                e_cx + 39, e_cy + 10,
                e_cx + 39, e_cy + 32,
                e_cx + 3,  e_cy + 32,
                e_cx + 3,  e_cy + 48,
                e_cx + 55, e_cy + 48))
    p.append('<path d="%s" fill="#e2e7ec" stroke="#5a626a" stroke-width="1.8"/>' % d_right)

    # Каркас з обмоткою на центральному керні
    p.append(rect(e_cx - 28, e_cy - 28, 18, 56, fill="#fbecec", stroke="#c0392b", sw=1.5, rx=2))
    p.append(rect(e_cx + 10, e_cy - 28, 18, 56, fill="#fbecec", stroke="#c0392b", sw=1.5, rx=2))
    p.append(text(e_cx - 19, e_cy + 4, "Cu", size=10, color="#c0392b", bold=True))
    p.append(text(e_cx + 19, e_cy + 4, "Cu", size=10, color="#c0392b", bold=True))
    p.append(text(e_cx, 285, "Центральний каркас", size=10.5, color=INK))
    p.append(text(e_cx, 300, "Зручне намотування", size=10, color=MUTED))

    # 1.3 Малюнок RM / PQ (cx = 535)
    r_cx, r_cy = 535, 205
    # Броньовий корпус як контур
    d_rm = ("M %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d L %d,%d Z "
            "M %d,%d L %d,%d L %d,%d L %d,%d Z "
            "M %d,%d L %d,%d L %d,%d L %d,%d Z" %
            # Зовнішній контур
            (r_cx - 56, r_cy - 48,
             r_cx + 56, r_cy - 48,
             r_cx + 56, r_cy + 48,
             r_cx - 56, r_cy + 48,
             r_cx - 56, r_cy - 48,
             r_cx - 36, r_cy - 34,
             r_cx - 36, r_cy + 34,
             r_cx - 56, r_cy + 34,
             # Ліве вікно
             r_cx - 36, r_cy - 34,
             r_cx - 14, r_cy - 34,
             r_cx - 14, r_cy + 34,
             r_cx - 36, r_cy + 34,
             # Праве вікно
             r_cx + 14, r_cy - 34,
             r_cx + 36, r_cy - 34,
             r_cx + 36, r_cy + 34,
             r_cx + 14, r_cy + 34))
    # Броньовий корпус (зовнішній прямокутник)
    p.append(rect(r_cx - 56, r_cy - 48, 112, 96, fill="#e2e7ec", stroke="#5a626a", sw=1.8, rx=4))
    # Ліве вікно
    p.append(rect(r_cx - 36, r_cy - 34, 22, 68, fill="#fafbfc", stroke="#5a626a", sw=1.4, rx=2))
    # Праве вікно
    p.append(rect(r_cx + 14, r_cy - 34, 22, 68, fill="#fafbfc", stroke="#5a626a", sw=1.4, rx=2))
    # Обмотка всередині вікон
    p.append(rect(r_cx - 32, r_cy - 28, 14, 56, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=2))
    p.append(rect(r_cx + 18, r_cy - 28, 14, 56, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=2))
    p.append(text(r_cx - 25, r_cy + 4, "Cu", size=10, color="#c0392b", bold=True))
    p.append(text(r_cx + 25, r_cy + 4, "Cu", size=10, color="#c0392b", bold=True))
    p.append(text(r_cx, 285, "Повне охоплення міді", size=10.5, color=INK))
    p.append(text(r_cx, 300, "Мінімальне випромінювання", size=10, color=MUTED))

    # 1.4 Малюнок Planar (cx = 735)
    p_cx, p_cy = 735, 205
    # Планарне осердя: верхня й нижня пластини + керни
    # Верхня пластина
    p.append(rect(p_cx - 55, p_cy - 24, 110, 10, fill="#e2e7ec", stroke="#5a626a", sw=1.6, rx=2))
    # Нижня пластина
    p.append(rect(p_cx - 55, p_cy + 14, 110, 10, fill="#e2e7ec", stroke="#5a626a", sw=1.6, rx=2))
    # Лівий бічний керн
    p.append(rect(p_cx - 55, p_cy - 14, 12, 28, fill="#e2e7ec", stroke="#5a626a", sw=1.6, rx=0))
    # Правий бічний керн
    p.append(rect(p_cx + 43, p_cy - 14, 12, 28, fill="#e2e7ec", stroke="#5a626a", sw=1.6, rx=0))
    # Центральний керн
    p.append(rect(p_cx - 10, p_cy - 14, 20, 28, fill="#e2e7ec", stroke="#5a626a", sw=1.6, rx=0))

    # Планарна друкована плата (PCB) у вікнах (не перекриває керни)
    p.append(rect(p_cx - 43, p_cy - 5, 33, 10, fill="#d4edda", stroke="#28a745", sw=1.4, rx=1))
    p.append(rect(p_cx + 10, p_cy - 5, 33, 10, fill="#d4edda", stroke="#28a745", sw=1.4, rx=1))
    # Зовнішні крила PCB
    p.append(rect(p_cx - 78, p_cy - 5, 23, 10, fill="#d4edda", stroke="#28a745", sw=1.4, rx=1))
    p.append(rect(p_cx + 55, p_cy - 5, 23, 10, fill="#d4edda", stroke="#28a745", sw=1.4, rx=1))

    p.append(text(p_cx - 66, p_cy + 3.5, "PCB", size=10, color="#155724", bold=True))
    p.append(text(p_cx + 66, p_cy + 3.5, "PCB", size=10, color="#155724", bold=True))
    p.append(text(p_cx, 285, "Доріжки на платі", size=10.5, color=INK))
    p.append(text(p_cx, 300, "Надвисока повторюваність", size=10, color=MUTED))

    render(os.path.join(IMG, "core-geometries.svg"), W, H, *p)


# ── 2. Геометричні розрахункові параметри осердя ──────────────────────────────
def fig_parameters():
    W, H = 820, 430
    p = []
    p.append(text(W / 2, 28, "Розрахункові геометричні параметри осердя (IEC 60205)", size=16, bold=True))
    p.append(text(W / 2, 48, "Ефективна площа перерізу Ae, довжина магнітної лінії le та площа вікна Aw", size=12, color=MUTED, italic=True))

    # Схема осердя E-типу з розмірами
    ox, oy = 210, 240
    # Зовнішній контур EE
    p.append(rect(ox - 130, oy - 120, 260, 240, fill="#e8ecf0", stroke="#495057", sw=2, rx=4))
    # Ліве вікно
    p.append(rect(ox - 90, oy - 75, 55, 150, fill="#ffffff", stroke="#495057", sw=1.8, rx=2))
    # Праве вікно
    p.append(rect(ox + 35, oy - 75, 55, 150, fill="#ffffff", stroke="#495057", sw=1.8, rx=2))

    # Обмотка (мідні витки) всередині вікон
    p.append(rect(ox - 82, oy - 65, 40, 130, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=2))
    p.append(rect(ox + 42, oy - 65, 40, 130, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=2))
    p.append(text(ox - 62, oy + 4, "Обмотка", size=11, color="#c0392b", bold=True))
    p.append(text(ox + 62, oy + 4, "Обмотка", size=11, color="#c0392b", bold=True))

    # Середня магнітна лінія (le) — пунктир замкненого контуру
    # Лівий контур
    p.append(rect_dash(ox - 110, oy - 98, 110, 196, fill="none", stroke=FIELD, sw=2.2, rx=12, dash="6,4"))
    # Правий контур
    p.append(rect_dash(ox, oy - 98, 110, 196, fill="none", stroke=FIELD, sw=2.2, rx=12, dash="6,4"))

    # Позначення Ae (центральний керн)
    p.append(rect(ox - 30, oy - 75, 60, 150, fill="#d0d7de", stroke="#495057", sw=1.2, rx=1))
    p.append(text(ox, oy - 30, "Центральний", size=10.5, color=INK, bold=True))
    p.append(text(ox, oy - 15, "керн", size=10.5, color=INK, bold=True))
    p.append(text(ox, oy + 8, "Площа Ae", size=12, color=NEG, bold=True))

    # Стрілка розміру вікна Aw
    p.append(line(ox + 35, oy + 88, ox + 90, oy + 88, color=POS, sw=1.8))
    p.append(line(ox + 35, oy + 82, ox + 35, oy + 94, color=POS, sw=1.8))
    p.append(line(ox + 90, oy + 82, ox + 90, oy + 94, color=POS, sw=1.8))
    p.append(text(ox + 62, oy + 104, "Вікно Aw", size=11, color=POS, bold=True))

    # Права панель із формулами та поясненням
    rx = 450
    # Блок 1: Ae
    b1, _, _ = textbox(rx + 170, 105, "Ae (Effective Area) — площа перерізу керна\nВизначає максимальний магнітний потік: Φ = B · Ae\nБільша площа → менше витків N для заданої індукції B",
                       size=11, pad=10, fill="#f0f7ff", stroke="#3b82f6", min_w=340)
    p.append(b1)

    # Блок 2: le
    b2, _, _ = textbox(rx + 170, 190, "le (Magnetic Path) — середня магнітна лінія\nДовжина замкненого шляху магнітного потоку\nКоротша le → менший магнітний опір Rm = le / (μ · Ae)",
                       size=11, pad=10, fill="#f0fdf4", stroke=FIELD, min_w=340)
    p.append(b2)

    # Блок 3: Aw
    b3, _, _ = textbox(rx + 170, 275, "Aw (Window Area) — площа вікна намотки\nПростір для розміщення мідного дроту та ізоляції\nФактор заповнення: ku = S_міді / Aw ≈ 0.25...0.40",
                       size=11, pad=10, fill="#fef2f2", stroke=POS, min_w=340)
    p.append(b3)

    # Блок 4: Ap
    b4, _, _ = textbox(rx + 170, 365, "Area Product:  Ap = Aw · Ae  [см⁴]\nГоловний показник габаритної потужності P_габ ∝ Ap\nПов'язує втрати в магнетику та теплові втрати в міді",
                       size=11.5, pad=10, fill="#fffbeb", stroke="#d97706", bold=True, min_w=340)
    p.append(b4)

    render(os.path.join(IMG, "core-parameters.svg"), W, H, *p)


# ── 3. Локалізований зазор проти розподіленого ────────────────────────────────
def fig_air_gap():
    W, H = 840, 420
    p = []
    p.append(text(W / 2, 28, "Повітряний зазор: де накопичується магнітна енергія", size=16, bold=True))
    p.append(text(W / 2, 48, "Густина енергії w = B² / (2μ) у повітрі в μr разів вища, ніж у фериті", size=12, color=MUTED, italic=True))

    # Ліва колонка: Локалізований зазор у фериті
    lx = 220
    p.append(rect(lx - 190, 68, 380, 330, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(lx, 92, "Локалізований зазор (Gapped Ferrite)", size=13, bold=True, color=INK))
    p.append(text(lx, 108, "Дискретний зазор lg у центральному керні", size=10.5, color=MUTED))

    # Схема осердя з зазором
    cy = 200
    p.append(rect(lx - 90, cy - 65, 180, 130, fill="#e2e7ec", stroke="#5a626a", sw=1.8, rx=4))
    # Вікна
    p.append(rect(lx - 65, cy - 40, 40, 80, fill="#ffffff", stroke="#5a626a", sw=1.4, rx=2))
    p.append(rect(lx + 25, cy - 40, 40, 80, fill="#ffffff", stroke="#5a626a", sw=1.4, rx=2))
    # Зазор у центральному керні
    p.append(rect(lx - 20, cy - 6, 40, 12, fill="#fff3cd", stroke="#e67e22", sw=1.8, rx=1))
    p.append(text(lx, cy + 3, "lg", size=10, bold=True, color="#d35400"))

    # Пояснення густини енергії
    p.append(text(lx, cy + 85, "У зазорі (μr = 1):  w_gap = B² / (2·μ₀)", size=11, bold=True, color="#d35400"))
    p.append(text(lx, cy + 103, "У фериті (μr = 3000):  w_fe = B² / (2·μ₀·3000)", size=10.5, color=MUTED))
    p.append(rect(lx - 170, cy + 120, 340, 32, fill="#fef3c7", stroke="#f59e0b", sw=1, rx=4))
    p.append(text(lx, cy + 140, "👉 Понад 99% енергії запасається в зазорі lg!", size=10.5, bold=True, color="#92400e"))

    # Права колонка: Розподілений зазор у порошку
    rx = 620
    p.append(rect(rx - 190, 68, 380, 330, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(rx, 92, "Розподілений зазор (Powder Core)", size=13, bold=True, color=INK))
    p.append(text(rx, 108, "Мікроскопічні зазори між зернами металу", size=10.5, color=MUTED))

    # Малюнок структури порошку (зерна + діелектрик)
    py = 200
    p.append(rect(rx - 90, py - 65, 180, 130, fill="#fff9db", stroke="#f59e0b", sw=1.8, rx=4))
    # Сітка зерен
    for gx in range(int(rx - 75), int(rx + 80), 28):
        for gy in range(int(py - 50), int(py + 55), 24):
            p.append(circle(gx, gy, 10, fill="#495057", stroke="#212529", sw=1.2))

    p.append(text(rx, py + 85, "Мільйони мікрозазорів по всьому об'єму", size=11, bold=True, color=INK))
    p.append(text(rx, py + 103, "Плавне (м'яке) насичення під постійним струмом", size=10.5, color=MUTED))
    p.append(rect(rx - 170, py + 120, 340, 32, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    p.append(text(rx, py + 140, "👉 Немає точкового крайового потоку розсіювання", size=10.5, bold=True, color="#166534"))

    render(os.path.join(IMG, "air-gap-energy.svg"), W, H, *p)


# ── 4. Крайовий потік розсіювання (Fringing Flux) ─────────────────────────────
def fig_fringing_flux():
    W, H = 820, 410
    p = []
    p.append(text(W / 2, 28, "Крайовий потік (Fringing Flux) біля повітряного зазору", size=16, bold=True))
    p.append(text(W / 2, 48, "Випинання силових ліній у вікно обмотки спричиняє локальний перегрів міді", size=12, color=MUTED, italic=True))

    # Схема центрального керна з зазором
    cx, cy = 250, 220

    # Верхній полюс керна
    p.append(rect(cx - 50, cy - 130, 100, 95, fill="#e2e7ec", stroke="#495057", sw=2, rx=2))
    p.append(text(cx, cy - 80, "Центральний керн", size=11, color=INK, bold=True))
    p.append(text(cx, cy - 64, "(ферит, μr = 3000)", size=10, color=MUTED))

    # Нижній полюс керна
    p.append(rect(cx - 50, cy + 35, 100, 95, fill="#e2e7ec", stroke="#495057", sw=2, rx=2))
    p.append(text(cx, cy + 75, "Центральний керн", size=11, color=INK, bold=True))
    p.append(text(cx, cy + 91, "(ферит, μr = 3000)", size=10, color=MUTED))

    # Зазор lg
    p.append(rect_dash(cx - 50, cy - 35, 100, 70, fill="#fffdfa", stroke="#d0d7de", sw=1, rx=0, dash="3,3"))
    p.append(line(cx - 58, cy - 35, cx - 58, cy + 35, color=POS, sw=1.5))
    p.append(line(cx - 63, cy - 35, cx - 53, cy - 35, color=POS, sw=1.5))
    p.append(line(cx - 63, cy + 35, cx - 53, cy + 35, color=POS, sw=1.5))
    p.append(text(cx - 72, cy + 4, "lg", size=12, bold=True, color=POS))

    # Силові лінії в зазорі (прямі)
    for x_off in (-30, -10, 10, 30):
        p.append(line(cx + x_off, cy - 35, cx + x_off, cy + 35, color=FIELD, sw=1.8))

    # Крайові лінії (випинання / спучування праворуч у вікно)
    p.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,2"/>' %
             (cx + 45, cy - 35, cx + 80, cy, cx + 45, cy + 35, FIELD))
    p.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,2"/>' %
             (cx + 40, cy - 50, cx + 115, cy, cx + 40, cy + 50, FIELD))
    p.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,2"/>' %
             (cx + 35, cy - 65, cx + 150, cy, cx + 35, cy + 65, FIELD))

    # Витки обмотки, що потрапляють під крайовий потік
    wx = cx + 110
    for wy in (cy - 60, cy - 30, cy, cy + 30, cy + 60):
        is_hot = abs(wy - cy) <= 35
        fill_col = "#ffcdd2" if is_hot else "#fbecec"
        strk_col = "#b71c1c" if is_hot else "#c0392b"
        p.append(circle(wx, wy, 12, fill=fill_col, stroke=strk_col, sw=1.8))
        p.append(text(wx, wy + 4, "Cu", size=10, color=strk_col, bold=True))
        if is_hot:
            p.append(circle_dash(wx, wy, 7, fill="none", stroke="#d32f2f", sw=1.2, dash="2,2"))

    # Позначення гарячої зони
    p.append(arrow(wx + 22, cy, wx + 60, cy - 25, color=POS, sw=1.8))
    p.append(text(wx + 65, cy - 30, "Локальний перегрів!", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(wx + 65, cy - 14, "Вихрові струми в міді", size=10, color=POS, anchor="start"))

    # Права панель — причини та захист
    px = 590
    b1, _, _ = textbox(px, 125, "1. Фізична причина ефекту:\nМагнітні лінії випинаються назовні, бо повітря\nнавколо зазору має ту саму проникність μ₀.\nЕфективна площа зазору стає більшою: Agap > Ae.",
                       size=11, pad=10, fill="#f8fafc", stroke="#94a3b8", min_w=360)
    p.append(b1)

    b2, _, _ = textbox(px, 225, "2. Небезпека для обмотки:\nЗмінний потік перетинає провідники ПЕРПЕНДИКУЛЯРНО.\nЦе наводить потужні вихрові струми прямо в тілі міді\nта спричиняє катастрофічний локальний перегрів.",
                       size=11, pad=10, fill="#fff1f2", stroke="#f43f5e", min_w=360)
    p.append(b2)

    b3, _, _ = textbox(px, 325, "3. Конструктивні заходи захисту:\n• Залишати захисний проміжок (Keep-out) біля зазору\n• Робити зазор лише на центральному керні\n• Використовувати літцендрат замість товстого моноліту",
                       size=11, pad=10, fill="#f0fdf4", stroke=FIELD, min_w=360)
    p.append(b3)

    render(os.path.join(IMG, "fringing-flux.svg"), W, H, *p)


# ── 5. Електромагнітне екранування (EMI) ───────────────────────────────────────
def fig_emi_shielding():
    W, H = 840, 390
    p = []
    p.append(text(W / 2, 28, "Електромагнітне екранування: відкриті проти закритих осердь", size=16, bold=True))
    p.append(text(W / 2, 48, "Розподіл зовнішнього поля розсіювання та вплив на сусідні компоненти", size=12, color=MUTED, italic=True))

    # Ліворуч: Відкрите барабанне осердя (Drum Core / Unshielded)
    lx = 220
    p.append(rect(lx - 190, 68, 380, 300, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(lx, 92, "Відкрите барабанне осердя (Drum Core)", size=12.5, bold=True, color="#c0392b"))
    p.append(text(lx, 108, "Неекранований силовий індуктор", size=10.5, color=MUTED))

    # Схема гантелі
    dy = 195
    p.append(rect(lx - 40, dy - 45, 80, 16, fill="#7f8c8d", stroke="#34495e", sw=1.6, rx=2))
    p.append(rect(lx - 40, dy + 29, 80, 16, fill="#7f8c8d", stroke="#34495e", sw=1.6, rx=2))
    p.append(rect(lx - 16, dy - 29, 32, 58, fill="#7f8c8d", stroke="#34495e", sw=1.6, rx=0))
    # Обмотка
    p.append(rect(lx - 34, dy - 24, 18, 48, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=2))
    p.append(rect(lx + 16, dy - 24, 18, 48, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=2))

    # Сильні лінії розсіювання назовні
    for r_off in (65, 95, 125):
        p.append('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,3"/>' %
                 (lx, dy, r_off, r_off * 0.75, "#e74c3c"))

    p.append(rect(lx - 170, dy + 95, 340, 52, fill="#fef2f2", stroke="#ef4444", sw=1, rx=4))
    p.append(text(lx, dy + 115, "⚠️ Сильне випромінювання магнітного шуму (EMI)", size=10.5, bold=True, color="#991b1b"))
    p.append(text(lx, dy + 133, "Накладає наведення на чутливі аналогові кола", size=10, color="#991b1b"))

    # Праворуч: Броньове екрановане осердя (Pot / RM / PQ)
    rx = 620
    p.append(rect(rx - 190, 68, 380, 300, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(rx, 92, "Броньове закрите осердя (Pot / RM / PQ)", size=12.5, bold=True, color=FIELD))
    p.append(text(rx, 108, "Магнітно самозахищена конструкція", size=10.5, color=MUTED))

    # Схема закритого осердя
    p.append(rect(rx - 55, dy - 45, 110, 90, fill="#7f8c8d", stroke="#34495e", sw=1.8, rx=4))
    # Внутрішнє вікно
    p.append(rect(rx - 36, dy - 30, 72, 60, fill="#fafbfc", stroke="#34495e", sw=1.4, rx=2))
    # Центральний керн
    p.append(rect(rx - 12, dy - 30, 24, 60, fill="#7f8c8d", stroke="#34495e", sw=1.4, rx=0))
    # Обмотка всередині
    p.append(rect(rx - 32, dy - 24, 16, 48, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=2))
    p.append(rect(rx + 16, dy - 24, 16, 48, fill="#fbecec", stroke="#c0392b", sw=1.4, rx=2))

    # Замкнений потік у стінках (зелений пунктир)
    p.append(rect_dash(rx - 46, dy - 38, 92, 76, fill="none", stroke=FIELD, sw=2, rx=4, dash="4,3"))

    p.append(rect(rx - 170, dy + 95, 340, 52, fill="#f0fdf4", stroke=FIELD, sw=1, rx=4))
    p.append(text(rx, dy + 115, "✅ Магнітний потік повністю замкнений у стінках", size=10.5, bold=True, color="#166534"))
    p.append(text(rx, dy + 133, "Мінімальне випромінювання EMI, чудова ЕМС", size=10, color="#166534"))

    render(os.path.join(IMG, "core-emi-shielding.svg"), W, H, *p)


if __name__ == '__main__':
    fig_geometries()
    fig_parameters()
    fig_air_gap()
    fig_fringing_flux()
    fig_emi_shielding()
    print("All figures generated successfully.")
