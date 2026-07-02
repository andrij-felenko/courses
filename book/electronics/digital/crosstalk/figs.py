# -*- coding: utf-8 -*-
"""Фігури до теми «Перехресна завада (crosstalk)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Два механізми зв'язку: ємнісний (dV/dt) і індуктивний (dI/dt) ──────────
def fig_mechanisms():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 26, "Дві доріжки поруч — паразитний конденсатор і трансформатор", size=17, bold=True))

    # ── ліва панель: ємнісний зв'язок ──
    xL = 60
    p.append(text(xL + 130, 60, "Ємнісний зв'язок (реагує на dV/dt)", size=13, bold=True, color=POS))
    # агресор (верхня доріжка) і жертва (нижня)
    ay = 110
    vy = 190
    p.append(line(xL, ay, xL + 260, ay, color=POS, sw=4))
    p.append(line(xL, vy, xL + 260, vy, color=INK, sw=4))
    p.append(text(xL - 6, ay + 4, "агресор", size=11, color=POS, anchor="end"))
    p.append(text(xL - 6, vy + 4, "жертва", size=11, color=INK, anchor="end"))
    # ємності між ними (кілька «конденсаторів»)
    for dx in (60, 130, 200):
        cx = xL + dx
        p.append(line(cx, ay, cx, ay + 22, color=MUTED, sw=1.5))
        p.append(line(cx - 10, ay + 22, cx + 10, ay + 22, color=MUTED, sw=2))
        p.append(line(cx - 10, ay + 34, cx + 10, ay + 34, color=MUTED, sw=2))
        p.append(line(cx, ay + 34, cx, vy, color=MUTED, sw=1.5))
    p.append(text(xL + 130, ay + 30, "Cм", size=12, color=MUTED, italic=True))
    # стрілка «інжектований струм» вниз у жертву
    p.append(arrow(xL + 130, vy + 8, xL + 130, vy + 40, color=POS, sw=2))
    p.append(text(xL + 130, vy + 55, "i = Cм · dV/dt", size=12, color=POS, bold=True))

    # ── права панель: індуктивний зв'язок ──
    xR = 400
    p.append(text(xR + 130, 60, "Індуктивний зв'язок (реагує на dI/dt)", size=13, bold=True, color=NEG))
    p.append(line(xR, ay, xR + 260, ay, color=NEG, sw=4))
    p.append(line(xR, vy, xR + 260, vy, color=INK, sw=4))
    p.append(text(xR - 6, ay + 4, "агресор", size=11, color=NEG, anchor="end"))
    p.append(text(xR - 6, vy + 4, "жертва", size=11, color=INK, anchor="end"))
    # струм в агресорі
    p.append(arrow(xR + 40, ay - 8, xR + 220, ay - 8, color=NEG, sw=2))
    p.append(text(xR + 130, ay - 16, "I (тече)", size=11, color=NEG))
    # магнітне поле — дуги над агресором, що охоплюють жертву
    for cx in (xR + 90, xR + 170):
        p.append('<path d="M %.1f %.1f A 30 42 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.5"/>'
                 % (cx - 26, ay + 6, cx + 26, ay + 6, MUTED))
    p.append(text(xR + 130, ay + 46, "Ø (спільний потік → M)", size=11, color=MUTED, italic=True))
    p.append(text(xR + 130, vy + 40, "наведена напруга", size=12, color=NEG, bold=True))
    p.append(text(xR + 130, vy + 55, "v = M · dI/dt", size=12, color=NEG, bold=True))

    # роздільник
    p.append(line(380, 70, 380, 300, color="#dddddd", sw=1.5, dash="4 4"))
    render(os.path.join(IMG, "mechanisms.svg"), W, H, *p)


# ── 2. Ближній і дальній кінець: різні імпульси на тій самій жертві ───────────
def edge_curve(x0, x1, y0, y1, n=20):
    pts = []
    for i in range(n + 1):
        t = i / n
        s = 0.5 * (1 - math.cos(math.pi * t))
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * s))
    return pts


def polyline(pts, color=INK, sw=2, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pth = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (pth, color, sw, d)


def fig_near_far():
    W, H = 720, 380
    p = []
    p.append(text(W / 2, 26, "Один фронт агресора — два різні сплески на кінцях жертви", size=17, bold=True))

    # верх: фронт агресора
    ax0, aw = 70, 560
    ay_hi, ay_lo = 70, 120
    p.append(text(ax0 - 10, (ay_hi + ay_lo) / 2, "агресор", size=11, color=POS, anchor="end"))
    a = [(ax0, ay_lo)]
    a += edge_curve(ax0 + 120, ax0 + 175, ay_lo, ay_hi)
    a += [(ax0 + aw, ay_hi)]
    p.append(polyline(a, color=POS, sw=3))
    p.append(text(ax0 + 147, ay_hi - 6, "крутий фронт", size=11, color=POS))

    # base line рівень жертви
    def victim_panel(y0, label, spikes):
        base = y0 + 60
        p.append(line(ax0, base, ax0 + aw, base, color="#cccccc", sw=1.2, dash="3 3"))
        p.append(text(ax0 - 10, base, label, size=11, color=INK, anchor="end"))
        p.append(polyline(spikes, color=NEG, sw=2.5))

    # ближній кінець: широкий однополярний горб (тримається весь час фронту й довше)
    b = base_near = 230
    near = [(ax0, b)]
    near += edge_curve(ax0 + 118, ax0 + 150, b, b - 55)      # швидкий підйом
    near += edge_curve(ax0 + 150, ax0 + 360, b - 55, b - 10)  # повільний спад (подвійний час пробігу)
    near += [(ax0 + aw, b)]
    victim_panel(170, "жертва: ближній кінець", near)
    p.append(text(ax0 + 250, b - 62, "широкий горб, той самий знак", size=11, color=NEG))

    # дальній кінець: вузький двополярний імпульс (тільки під час фронту)
    b2 = 330
    far = [(ax0, b2)]
    far += edge_curve(ax0 + 145, ax0 + 165, b2, b2 - 48)     # вузький пік
    far += edge_curve(ax0 + 165, ax0 + 185, b2 - 48, b2)
    far += [(ax0 + aw, b2)]
    victim_panel(270, "жертва: дальній кінець", far)
    p.append(text(ax0 + 300, b2 - 40, "вузький гострий пік лише на фронті", size=11, color=NEG))

    render(os.path.join(IMG, "near-far.svg"), W, H, *p)


# ── 3. Способи прибити заваду (короткий підсумок) ─────────────────────────────
def fig_mitigation():
    W, H = 720, 300
    p = []
    p.append(text(W / 2, 26, "Чотири важелі проти перехресної завади", size=17, bold=True))

    items = [
        ("Розсунути доріжки", "Cм і M\nпадають\nз відстанню.\nПравило 3W:\nпроміжок ≥ 2·ширини.", FIELD),
        ("Земля-щит", "Заземлена\nдоріжка\nчи шар землі\nперехоплює поле\nй веде зворотний\nструм поряд.", NEG),
        ("Тихший фронт", "Менший slew\n→ менший dV/dt\nі dI/dt\n→ слабший\nінжект у жертву.", POS),
        ("Диференційна пара", "Завада б'є\nв обидва\nпроводи рівно\n→ приймач\nбере різницю\nй викидає її.", INK),
    ]
    bw, bh, gap = 158, 190, 18
    x0 = (W - (bw * 4 + gap * 3)) / 2
    y0 = 66
    for i, (title, body, col) in enumerate(items):
        x = x0 + i * (bw + gap)
        p.append(rect(x, y0, bw, bh, fill="#fbfcfd", stroke=col, sw=2))
        p.append(text(x + bw / 2, y0 + 28, title, size=13, bold=True, color=col))
        p.append(line(x + 14, y0 + 40, x + bw - 14, y0 + 40, color=col, sw=1))
        p.append(fitbox(x + 10, y0 + 50, bw - 20, bh - 62, body, size=12,
                        fill="#ffffff", stroke="#ffffff", sw=0))
    p.append(text(W / 2, y0 + bh + 34,
                  "Найдешевше — фронт і відстань; найнадійніше на швидкості — земля-щит і диференціал.",
                  size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "mitigation.svg"), W, H, *p)


# ── 4. Розклад на хвилі: ємнісний струм — в обидва боки, індуктивний — зустрічно ─
def fig_wave_split():
    W, H = 700, 470
    p = []
    p.append(text(W / 2, 26, "Куди біжать наведені хвилі: чому на ближньому додаються, на дальньому гасяться", size=15, bold=True))

    x0, xw = 70, 560
    xmid = x0 + xw / 2
    xnear, xfar = x0, x0 + xw

    def victim_line(y, label):
        p.append(line(x0, y, x0 + xw, y, color=INK, sw=3))
        p.append(text(x0 - 12, y - 12, "ближній", size=10, color=MUTED, anchor="middle"))
        p.append(text(x0 + xw + 2, y - 12, "дальній", size=10, color=MUTED, anchor="middle"))
        p.append(text(xmid, y - 34, label, size=12, bold=True))

    # ── панель А: ємнісний струм у точці зв'язку ──
    yA = 90
    victim_line(yA, "Ємнісний струм  iC = Cм·dV/dt  (тече в точці зв'язку)")
    p.append(plus(xmid, yA - 4, r=7))
    # розтікається симетрично в обидва боки → на кінцях однаковий знак
    p.append(arrow(xmid - 12, yA + 16, xnear + 40, yA + 16, color=POS, sw=2.2))
    p.append(arrow(xmid + 12, yA + 16, xfar - 40, yA + 16, color=POS, sw=2.2))
    p.append(text((xmid + xnear) / 2, yA + 34, "назад  ½iC  (+)", size=11, color=POS))
    p.append(text((xmid + xfar) / 2, yA + 34, "вперед  ½iC  (+)", size=11, color=POS))

    # ── панель Б: індуктивна напруга у точці зв'язку ──
    yB = 210
    victim_line(yB, "Індуктивна е.р.с.  vL = M·dI/dt  (наводиться вздовж петлі)")
    # джерело напруги посередині, що жене струм жертвою у протилежні боки на кінцях
    p.append(minus(xmid - 16, yB - 4, r=7))
    p.append(plus(xmid + 16, yB - 4, r=7))
    p.append(arrow(xmid - 12, yB + 16, xnear + 40, yB + 16, color=POS, sw=2.2))
    p.append(arrow(xmid + 12, yB + 16, xfar - 40, yB + 16, color=NEG, sw=2.2))
    p.append(text((xmid + xnear) / 2, yB + 34, "назад  (+)", size=11, color=POS))
    p.append(text((xmid + xfar) / 2, yB + 34, "вперед  (−)", size=11, color=NEG))

    # ── панель В: сума на кожному кінці ──
    yC = 340
    victim_line(yC, "Сума на кінці = ємнісний ± індуктивний")
    # ближній: (+)+(+) = додаються
    p.append(fitbox(xnear - 6, yC + 12, 250, 60,
                    "БЛИЖНІЙ:  (+) + (+)  →  ДОДАЮТЬСЯ\nVбл ∝ (Cм/C + M/L)", size=12,
                    fill="#fdf0ee", stroke=POS, sw=2, color=POS, bold=True))
    # дальній: (+)+(−) = гасяться
    p.append(fitbox(xfar - 244, yC + 12, 250, 60,
                    "ДАЛЬНІЙ:  (+) + (−)  →  ГАСЯТЬСЯ\nVдл ∝ (Cм/C − M/L)", size=12,
                    fill="#eef2fd", stroke=NEG, sw=2, color=NEG, bold=True))

    p.append(text(W / 2, H - 14,
                  "Ємнісний внесок на обох кінцях однакового знаку; індуктивний — протилежного на дальньому. Звідси сума й різниця.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "wave-split.svg"), W, H, *p)


# ── 5. Насичення ближньої завади з довжиною зв'язку ───────────────────────────
def fig_next_saturation():
    W, H = 720, 360
    p = []
    p.append(text(W / 2, 26, "Ближня завада росте з довжиною зв'язку — і насичується", size=16, bold=True))

    # осі
    ox, oy = 90, 290
    axw, axh = 560, 210
    p.append(arrow(ox, oy, ox + axw + 10, oy, color=INK, sw=1.8))          # X: довжина
    p.append(arrow(ox, oy, ox, oy - axh - 10, color=INK, sw=1.8))          # Y: амплітуда
    p.append(text(ox + axw / 2, oy + 34, "довжина зв'язку  ℓ  (∝ час пробігу TD)", size=12))
    p.append(text(ox - 60, oy - axh / 2, "Vбл", size=12, italic=True))

    # крива насичення: лінійно росте до ℓsat, далі плато
    plateau = oy - axh + 30
    xsat = ox + axw * 0.42
    pts = [(ox, oy)]
    n = 24
    for i in range(n + 1):
        t = i / n
        xx = ox + (xsat - ox) * t
        pts.append((xx, oy + (plateau - oy) * t))
    pts.append((ox + axw, plateau))
    p.append(polyline(pts, color=NEG, sw=3))

    # рівень насичення Kb·Va
    p.append(line(ox, plateau, ox + axw, plateau, color=MUTED, sw=1, dash="4 4"))
    p.append(text(ox + axw - 4, plateau - 8, "Vбл = Kне·V  (насичення)", size=11, color=NEG, anchor="end"))
    # позначка ℓsat = tr·v/2
    p.append(line(xsat, oy, xsat, plateau, color=POS, sw=1.2, dash="3 3"))
    p.append(text(xsat, oy + 16, "ℓsat = tr·v/2", size=11, color=POS))
    # підписи зон (нижче кривої/плато, багаторядково через mtext)
    p.append(mtext((ox + xsat) / 2 + 30, oy - 60, "коротка лінія:\nросте лінійно", size=10, color=MUTED))
    p.append(mtext((xsat + ox + axw) / 2, plateau + 34, "довга лінія:\nплато, лише ширшає в часі", size=10, color=MUTED))

    render(os.path.join(IMG, "next-saturation.svg"), W, H, *p)


if __name__ == "__main__":
    fig_mechanisms()
    fig_near_far()
    fig_mitigation()
    fig_wave_split()
    fig_next_saturation()
    print("OK: 5 SVG ->", IMG)
