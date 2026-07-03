# -*- coding: utf-8 -*-
"""Фігури до статті «Bootstrap-конденсатор у драйвері затвора».
Запуск: python figs.py  → пише .svg у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: чотири споживачі, що спорожняють Cbs за один період ────────────
def fig_drains():
    W, H = 760, 470
    els = []
    # центральний конденсатор — «відерце»
    cx, cy = 210, 250
    els.append(rect(cx - 55, cy - 70, 110, 140, fill="#eef4ff", stroke=NEG, sw=2, rx=8))
    els.append(text(cx, cy - 44, "Cbs", size=20, color=NEG, bold=True))
    els.append(text(cx, cy - 22, "«відерце»", size=13, color=MUTED))
    # рівень заряду
    els.append(line(cx - 45, cy + 8, cx + 45, cy + 8, color=NEG, sw=3))
    els.append(text(cx, cy + 34, "запас", size=12, color=MUTED))
    els.append(text(cx, cy + 50, "заряду", size=12, color=MUTED))
    # заголовок
    els.append(text(W / 2, 30, "Що вип'є Cbs за один період відкритого верхнього ключа",
                    size=16, bold=True))
    # чотири споживачі праворуч
    items = [
        ("Qg", "заряд затвора верхнього ключа", "— головний ковток, ~30–100 нКл", POS, 95),
        ("Qls", "заряд зсуву рівня за такт", "— внутрішня схема драйвера, ~5 нКл", INK, 185),
        ("Iqbs·t", "струм спокою верхнього драйвера", "— тече весь час, поки ключ ON", INK, 275),
        ("Iвитік·t", "витік діода Dbs + затвора", "— малий, але при 100% ON вирішує", MUTED, 365),
    ]
    bx = 430
    for sym, name, note, col, y in items:
        # стрілка від конденсатора до споживача
        els.append(arrow(cx + 58, cy - 30 + (y - 95) * 0.42, bx - 8, y, color=col, sw=2))
        frag, w, h = textbox(bx + 150, y, sym + "  " + name, size=13, bold=True,
                             stroke=col, fill="#fbfbfb", min_w=300)
        els.append(frag)
        els.append(text(bx + 150, y + 22, note, size=11, color=MUTED))
    render(os.path.join(IMG, "drains.svg"), W, H, *els)


# ── Фігура 2: просідання напруги — компроміс розміру ─────────────────────────
def fig_droop():
    W, H = 720, 430
    els = []
    els.append(text(W / 2, 28, "Просідання ΔV задає нижню межу ємності", size=16, bold=True))
    # осі
    ox, oy = 90, 330
    els.append(arrow(ox, oy, ox, 70, color=INK, sw=1.6))       # V
    els.append(arrow(ox, oy, 660, oy, color=INK, sw=1.6))      # t
    els.append(text(ox - 12, 78, "VB−VS", size=13, anchor="end", color=INK))
    els.append(text(650, oy + 24, "час", size=13, color=INK))
    # лінія повного заряду (12 В)
    yfull = 110
    els.append(line(ox, yfull, 640, yfull, color=MUTED, sw=1, dash="5,5"))
    els.append(text(645, yfull + 4, "Vdrv (12 В)", size=12, anchor="start", color=MUTED))
    # поріг UVLO
    ythr = 250
    els.append(line(ox, ythr, 640, ythr, color=POS, sw=1.4, dash="6,4"))
    els.append(text(645, ythr + 4, "UVLO", size=12, anchor="start", color=POS))
    # велика ємність — тихе просідання (зелена)
    import math
    pts_big = []
    for i in range(0, 220):
        t = i / 219.0
        x = ox + 40 + t * 250
        y = yfull + (140 * 0.28) * t  # спад на 0.28·140
        pts_big.append("%.1f,%.1f" % (x, y))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
               % (" ".join(pts_big), FIELD))
    els.append(text(ox + 165, yfull - 10, "велика Cbs: мале ΔV", size=12, color=FIELD, bold=True))
    # мала ємність — глибоке просідання нижче порога (червона)
    pts_sm = []
    for i in range(0, 220):
        t = i / 219.0
        x = ox + 340 + t * 250
        y = yfull + (170) * t
        pts_sm.append("%.1f,%.1f" % (x, y))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>'
               % (" ".join(pts_sm), POS))
    els.append(text(ox + 470, yfull - 10, "мала Cbs: провал", size=12, color=POS, bold=True))
    # позначка ΔV
    els.append(line(ox + 300, yfull, ox + 300, yfull + 39, color=FIELD, sw=1.2))
    els.append(text(ox + 312, yfull + 24, "ΔV", size=12, anchor="start", color=FIELD, bold=True))
    # підпис зон
    els.append(text(ox + 465, ythr + 40, "нижче UVLO → верхній ключ гасне",
                    size=12, color=POS))
    render(os.path.join(IMG, "droop.svg"), W, H, *els)


# ── Фігура 3: діод Dbs — воротар «відерця» ──────────────────────────────────
def fig_diode():
    W, H = 720, 360
    els = []
    els.append(text(W / 2, 28, "Діод Dbs: наливає у фазі заряду, замикає у фазі роботи",
                    size=15, bold=True))
    # ── ліва панель: фаза заряду ──
    els.append(fitbox(40, 60, 300, 40, "ФАЗА ЗАРЯДУ  (нижній ключ ON, SW ≈ 0)",
                      size=13, bold=True, fill="#eef7ee", stroke=FIELD))
    # Vdrv
    els.append(text(60, 150, "Vdrv", size=13, color=INK, anchor="start"))
    els.append(text(60, 166, "12 В", size=11, color=MUTED, anchor="start"))
    els.append(circle(120, 150, 6, fill=INK, stroke=INK))
    # діод відкритий
    els.append(line(120, 150, 180, 150, color=FIELD, sw=2))
    els.append('<path d="M180 138 L180 162 L206 150 Z" fill="#eef7ee" stroke="%s" stroke-width="2"/>' % FIELD)
    els.append(line(206, 138, 206, 162, color=FIELD, sw=2.5))
    els.append(line(206, 150, 260, 150, color=FIELD, sw=2))
    els.append(text(163, 128, "Dbs ▶ тече", size=12, color=FIELD, bold=True))
    # конденсатор
    els.append(line(260, 120, 260, 180, color=INK, sw=2))
    els.append(line(275, 120, 275, 180, color=INK, sw=2))
    els.append(text(300, 145, "Cbs", size=13, color=NEG, anchor="start", bold=True))
    els.append(text(300, 162, "набирає 12 В", size=11, color=MUTED, anchor="start"))
    els.append(line(275, 150, 300, 150, color=INK, sw=1.5))
    # SW ≈ 0
    els.append(line(260, 210, 260, 230, color=INK, sw=1.5))
    els.append(line(260, 230, 320, 230, color=INK, sw=1.5))
    els.append(text(325, 234, "SW ≈ 0", size=12, color=MUTED, anchor="start"))
    els.append(line(260, 180, 260, 210, color=INK, sw=1.5))

    # ── права панель: фаза роботи ──
    els.append(fitbox(400, 60, 300, 40, "ФАЗА РОБОТИ  (верхній ключ ON, SW ↑ Vbus)",
                      size=13, bold=True, fill="#fdeeee", stroke=POS))
    els.append(text(410, 150, "Vdrv", size=13, color=INK, anchor="start"))
    els.append(circle(470, 150, 6, fill=INK, stroke=INK))
    # діод замкнений (перекреслений)
    els.append(line(470, 150, 530, 150, color=MUTED, sw=2))
    els.append('<path d="M530 138 L530 162 L556 150 Z" fill="#f0f0f0" stroke="%s" stroke-width="2"/>' % MUTED)
    els.append(line(556, 138, 556, 162, color=MUTED, sw=2.5))
    els.append(line(556, 150, 610, 150, color=MUTED, sw=2))
    els.append(line(586, 132, 574, 168, color=POS, sw=2.5))  # риска «×»
    els.append(text(520, 128, "Dbs ✕ замкнено", size=12, color=POS, bold=True))
    # конденсатор — поїхав угору (VB = Vbus+12)
    els.append(line(610, 120, 610, 180, color=INK, sw=2))
    els.append(line(625, 120, 625, 180, color=INK, sw=2))
    els.append(text(648, 138, "Cbs", size=13, color=NEG, anchor="start", bold=True))
    els.append(text(648, 155, "тримає", size=11, color=MUTED, anchor="start"))
    els.append(text(648, 170, "12 В", size=11, color=MUTED, anchor="start"))
    els.append(line(625, 150, 648, 150, color=INK, sw=1.5))
    # SW ↑
    els.append(line(610, 180, 610, 230, color=POS, sw=1.5))
    els.append(arrow(610, 226, 610, 200, color=POS, sw=1.8))
    els.append(text(560, 250, "SW злітає до Vbus, VB = Vbus+12",
                    size=12, color=POS, anchor="start"))
    render(os.path.join(IMG, "diode.svg"), W, H, *els)


# ── Фігура 4 (вставка math): повний баланс заряду «прихід ↔ витрата» ─────────
def fig_charge_ledger():
    W, H = 880, 560
    els = []
    els.append(text(W / 2, 34, "Баланс заряду за один найдовший такт: усе, що вип'є Cbs",
                    size=17, bold=True))
    els.append(text(W / 2, 56, "напруга просяде на ΔV = Qвитрат / Cbs — тримаємо ΔV меншим за запас над UVLO",
                    size=12, color=MUTED))

    # ── ліва колонка: разові порції (заряд) ──
    lx = 60
    els.append(fitbox(lx, 90, 320, 34, "РАЗОВІ ПОРЦІЇ (нКл за такт)",
                      size=13, bold=True, fill="#fdeeee", stroke=POS))
    rows_once = [
        ("Qg", "заряд затвора верхнього ключа", "весь Qg від 0 до Vgs — головний ковток"),
        ("Qls", "заряд зсуву рівня", "команда «відкрий» крізь межу напруги"),
        ("Qrr", "зворотне відновлення діода", "заряд, злитий назад, поки діод гасне"),
    ]
    y = 150
    for sym, name, note in rows_once:
        frag, w, h = textbox(lx + 40, y, sym, size=15, bold=True, stroke=POS,
                             fill="#fff", min_w=64, color=POS)
        els.append(frag)
        els.append(text(lx + 86, y - 4, name, size=12.5, color=INK, anchor="start", bold=True))
        els.append(text(lx + 86, y + 14, note, size=11, color=MUTED, anchor="start"))
        y += 66

    # ── ліва колонка нижче: цівки (струм × час) ──
    els.append(fitbox(lx, 350, 320, 34, "ЦІВКИ × t(ON,max)  (струм · час)",
                      size=13, bold=True, fill="#eef4ff", stroke=NEG))
    rows_flow = [
        ("Iqbs", "струм спокою верхнього драйвера"),
        ("Icbs,leak", "витік самого конденсатора"),
        ("Ig,leak", "витік затвора + зсуву рівня"),
    ]
    y = 408
    for sym, name in rows_flow:
        frag, w, h = textbox(lx + 52, y, sym, size=13.5, bold=True, stroke=NEG,
                             fill="#fff", min_w=88, color=NEG)
        els.append(frag)
        els.append(text(lx + 108, y + 4, name, size=12, color=INK, anchor="start"))
        y += 52

    # знак множення на час
    els.append(text(lx + 150, 540, "усі три × найдовший t(ON,max)", size=11.5,
                    color=NEG, anchor="middle", italic=True))

    # ── права частина: сума → ємність (вертикальний ланцюг; стрілки в проміжках) ──
    cxr = 625
    frag, w, h = textbox(cxr, 195, "Qвитрат =\nQg + Qls + Qrr\n+ (Iqbs + Icbs,leak\n   + Ig,leak)·t(ON,max)",
                         size=13.5, bold=True, stroke=INK, fill=FILL, min_w=300)
    els.append(frag)
    # стрілка в проміжку між сумою (низ ≈ 258) і рамкою Cbs (верх ≈ 335)
    els.append(arrow(cxr, 262, cxr, 328, color=INK, sw=2.2))
    els.append(text(cxr + 96, 288, "÷ дозволене ΔV", size=11.5, color=MUTED, anchor="start"))
    frag, w, h = textbox(cxr, 360, "Cbs ≥ Qвитрат / ΔV", size=15, bold=True,
                         stroke=FIELD, fill="#eef7ee", min_w=290, color=FIELD)
    els.append(frag)
    # стрілка в проміжку між рамкою Cbs (низ ≈ 386) і рамкою номіналу (верх ≈ 470)
    els.append(arrow(cxr, 390, cxr, 466, color=FIELD, sw=1.9))
    els.append(text(cxr + 96, 420, "× 10–20", size=12.5, color=INK, anchor="start", bold=True))
    els.append(text(cxr + 96, 438, "запас на DC-bias,", size=11, color=MUTED, anchor="start"))
    els.append(text(cxr + 96, 452, "пуск, розкид", size=11, color=MUTED, anchor="start"))
    frag, w, h = textbox(cxr, 498, "номінал, який ставимо", size=13, bold=True,
                         stroke=NEG, fill="#fff", min_w=260, color=NEG)
    els.append(frag)

    render(os.path.join(IMG, "charge-ledger.svg"), W, H, *els)


# ── Фігура 5 (вставка math): DC-bias — чому «1 мкФ» це не 1 мкФ ──────────────
def fig_dcbias():
    import math
    W, H = 780, 470
    els = []
    els.append(text(W / 2, 30, "DC-bias: керамічний «1 мкФ» під напругою — уже не 1 мкФ",
                    size=16, bold=True))
    ox, oy = 90, 380          # початок осей
    top = 80                  # верх графіка (100 %)
    els.append(arrow(ox, oy, ox, top - 6, color=INK, sw=1.6))   # вісь C
    els.append(arrow(ox, oy, 700, oy, color=INK, sw=1.6))       # вісь U
    els.append(text(ox - 14, top + 6, "ефективна", size=12, anchor="end", color=INK))
    els.append(text(ox - 14, top + 22, "ємність", size=12, anchor="end", color=INK))
    els.append(text(690, oy + 26, "прикладена напруга / номінал ролі", size=12, anchor="end", color=INK))

    # горизонталь 100 %
    y100 = top + 10
    els.append(line(ox, y100, 660, y100, color=MUTED, sw=1, dash="5,5"))
    els.append(text(ox - 10, y100 + 4, "100 %", size=11, anchor="end", color=MUTED))
    # горизонталь 50 %
    y50 = oy - (oy - y100) * 0.5
    els.append(line(ox, y50, 660, y50, color=MUTED, sw=1, dash="4,4"))
    els.append(text(ox - 10, y50 + 4, "50 %", size=11, anchor="end", color=MUTED))

    def X(frac):  # частка робочої напруги від номіналу (0..1)
        return ox + frac * 560
    def Y(pct):   # ємність у % (0..100)
        return oy - (oy - y100) * (pct / 100.0)

    # крива X7R (спад до ~55 % на номіналі)
    ptx = []
    for i in range(0, 141):
        f = i / 140.0
        pct = 100 - 48 * (f ** 1.15)   # ~52 % на f=1
        ptx.append("%.1f,%.1f" % (X(f), Y(pct)))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
               % (" ".join(ptx), NEG))
    els.append(text(X(1.0) + 8, Y(52) + 4, "X7R", size=13, color=NEG, bold=True, anchor="start"))

    # крива X5R / гірший діелектрик (спад до ~35 %)
    pts5 = []
    for i in range(0, 141):
        f = i / 140.0
        pct = 100 - 66 * (f ** 1.05)   # ~34 % на f=1
        pts5.append("%.1f,%.1f" % (X(f), Y(pct)))
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-dasharray="7,4"/>'
               % (" ".join(pts5), POS))
    els.append(text(X(1.0) + 8, Y(34) + 4, "X5R", size=13, color=POS, bold=True, anchor="start"))

    # вертикаль «робоча точка ~50 % номіналу»
    els.append(line(X(0.5), y100, X(0.5), oy, color=FIELD, sw=1.4, dash="3,3"))
    els.append(text(X(0.5), oy + 18, "робоча точка", size=11, color=FIELD, anchor="middle"))
    els.append(text(X(0.5), oy + 33, "(~½ номіналу)", size=11, color=FIELD, anchor="middle"))
    # відмітка втрати
    els.append(circle(X(0.5), Y(100 - 48 * (0.5 ** 1.15)), 4, fill=NEG, stroke=NEG))
    els.append(text(X(0.5) + 10, Y(100 - 48 * (0.5 ** 1.15)) - 8,
                    "лишилось ~65 %", size=11, color=NEG, anchor="start"))

    # висновок-рамка
    frag, w, h = textbox(560, 130,
                         "тому «1 мкФ» беруть\nіз запасом 10–20×:\nреальна ємність під\nнапругою удвічі менша",
                         size=12, bold=False, stroke=INK, fill="#fff", min_w=250, color=INK)
    els.append(frag)

    render(os.path.join(IMG, "dcbias.svg"), W, H, *els)


if __name__ == "__main__":
    fig_drains()
    fig_droop()
    fig_diode()
    fig_charge_ledger()
    fig_dcbias()
    print("done")
