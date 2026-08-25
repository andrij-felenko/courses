# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Ферит і втрати в осерді».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/.
Три матеріальні фігури: петля гістерезису, вихрові струми (ферит vs залізо),
робочі діапазони родин MnZn/NiZn."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: петля гістерезису — площа = тепло за цикл ───────────────────────
# Головна ідея: намагніченість відстає від поля, крива за цикл описує петлю,
# і площа цієї петлі = енергія, з'їдена осердям за один цикл.
def fig_hysteresis():
    W, H = 740, 430
    p = []
    p.append(text(W / 2, 30, "Петля гістерезису: площа = тепло за цикл", size=17, bold=True))

    # центр координат
    ox, oy = 300, 250
    ax = 130   # піврозмах по горизонталі (поле)
    ay = 120   # піврозмах по вертикалі (намагніченість)

    # осі
    p.append(line(ox - ax - 30, oy, ox + ax + 36, oy, color=INK, sw=1.8))   # поле H
    p.append(line(ox, oy + ay + 36, ox, oy - ay - 30, color=INK, sw=1.8))   # намагніченість B
    p.append(text(ox + ax + 40, oy + 4, "поле H", size=12, color=INK, anchor="start", bold=True))
    p.append(text(ox, oy - ay - 36, "намагніченість B", size=12, color=INK, bold=True))

    # петля гістерезису — параметрично, як зміщені вгору/вниз гілки tanh
    def branch(direction, n=80):
        pts = []
        for i in range(n + 1):
            t = -1.0 + 2.0 * i / n                       # від -1 до +1
            hx = t * ax
            shift = 0.32 * direction                     # коерцитивне зміщення
            by = math.tanh(3.0 * (t - shift)) * ay
            pts.append((ox + hx, oy - by))
        return pts

    up = branch(+1)              # зростання поля
    down = branch(-1)[::-1]      # спадання поля
    poly = up + down
    d = "M %.1f,%.1f " % poly[0] + " ".join("L %.1f,%.1f" % q for q in poly[1:]) + " Z"
    p.append('<path d="%s" fill="#fbecec" stroke="%s" stroke-width="2.4"/>' % (d, POS))

    # стрілки напрямку обходу петлі
    p.append(arrow(ox - 6, oy - 96, ox + 20, oy - 104, color=POS, sw=2))
    p.append(arrow(ox + 6, oy + 96, ox - 20, oy + 104, color=POS, sw=2))

    # підпис площі — у центрі петлі
    p.append(text(ox, oy - 6, "площа =", size=12.5, color="#9a2b22", bold=True))
    p.append(text(ox, oy + 12, "тепло за цикл", size=12.5, color="#9a2b22", bold=True))

    # права колонка пояснень
    tx = 500
    p.append(text(tx, 120, "домени перевертаються", size=12, color=INK, anchor="start", bold=True))
    p.append(text(tx, 138, "не задарма — «з тертям»", size=12, color=INK, anchor="start"))
    p.append(text(tx, 176, "f циклів за секунду →", size=12, color=INK, anchor="start", bold=True))
    p.append(text(tx, 194, "потужність втрат росте", size=12, color=INK, anchor="start"))
    p.append(text(tx, 212, "разом із частотою", size=12, color=INK, anchor="start"))
    p.append(text(tx, 250, "ширша петля —", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(tx, 268, "більше тепла за цикл", size=12, color=FIELD, anchor="start", bold=True))

    render(os.path.join(IMG, "hysteresis.svg"), W, H, *p)


# ── Фігура 2: вихрові струми — суцільний метал vs ферит-ізолятор ──────────────
# Головна ідея: у провідному осерді змінне поле наводить вихрові струми (гріють,
# виштовхують поле); ферит — кераміка-ізолятор, вихорам нема де текти.
def fig_eddy():
    W, H = 800, 440
    p = []
    p.append(text(W / 2, 30, "Чому не залізо: вихрові струми в провідному осерді", size=17, bold=True))
    p.append(text(W / 2, 52, "змінне поле наводить струм у будь-якому провіднику — і в самому осерді теж",
                  size=12, color=MUTED, italic=True))

    # ── ЛІВОРУЧ: суцільний метал ─────────────────────────────────────────────
    lx = 165
    # стрілки «змінне поле» згори
    for dx in (-45, 0, 45):
        p.append(arrow(lx + dx, 78, lx + dx, 100, color=FIELD, sw=2))
    p.append(text(lx, 72, "змінне поле", size=11, color=FIELD, bold=True))

    p.append(rect(lx - 75, 102, 150, 220, fill="#9aa0a6", stroke="#4a4e54", sw=2))
    # вихрові кружки
    p.append('<ellipse cx="%.1f" cy="212" rx="44" ry="27" fill="none" stroke="%s" stroke-width="2.6"/>' % (lx, POS))
    p.append('<ellipse cx="%.1f" cy="212" rx="26" ry="16" fill="none" stroke="%s" stroke-width="2"/>' % (lx, POS))
    p.append(arrow(lx + 44, 208, lx + 44, 220, color=POS, sw=2.2))
    p.append(text(lx, 344, "суцільний метал:", size=12.5, color=INK, bold=True))
    p.append(text(lx, 362, "вихрові струми гріють осердя", size=11.5, color="#9a2b22"))
    p.append(text(lx, 380, "й виштовхують поле — на ВЧ «глухе»", size=11.5, color="#9a2b22"))

    # ── ПРАВОРУЧ: ферит-ізолятор ─────────────────────────────────────────────
    rx = 545
    for dx in (-45, 0, 45):
        p.append(arrow(rx + dx, 78, rx + dx, 100, color=FIELD, sw=2))
    p.append(text(rx, 72, "змінне поле", size=11, color=FIELD, bold=True))

    p.append(rect(rx - 75, 102, 150, 220, fill="#6a6f76", stroke="#4a4e54", sw=2))
    # зерна кераміки — крапки
    dots = []
    for gx in range(int(rx - 61), int(rx + 62), 22):
        for gy in range(116, 314, 24):
            dots.append('<circle cx="%.1f" cy="%.1f" r="1.6" fill="#4a4e54"/>' % (gx, gy))
    p.extend(dots)
    p.append(text(rx, 218, "∅", size=26, color="#dddddd", bold=True))
    p.append(text(rx, 344, "ферит — магнітна КЕРАМІКА:", size=12.5, color=INK, bold=True))
    p.append(text(rx, 362, "ізолятор, вихровим струмам", size=11.5, color="#1f6e33"))
    p.append(text(rx, 380, "нема де текти — працює до сотень МГц", size=11.5, color="#1f6e33"))

    p.append(text(W / 2, 414, "та сама причина, чому трансформатори складають із тонких ізольованих пластин",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "eddy.svg"), W, H, *p)


# ── Фігура 3: робочі діапазони родин MnZn / NiZn ─────────────────────────────
# Головна ідея: MnZn — велика проникність, але глухне ~1–2 МГц (власна провідність);
# NiZn — менша проникність, зате ізолятор, тягне до сотень МГц. Межа = вихрові струми.
def fig_families():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 30, "Дві родини фериту: де кожна працює", size=17, bold=True))

    # горизонтальна вісь частоти (логарифмічна), мітки 10к…1Г
    x0, x1 = 110, 690
    axisY = 300
    p.append(line(x0 - 10, axisY, x1 + 20, axisY, color=INK, sw=1.8))
    p.append(text(x1 + 24, axisY + 4, "f", size=13, color=INK, anchor="start", bold=True, italic=True))

    decades = [("10 кГц", 1e4), ("100 кГц", 1e5), ("1 МГц", 1e6),
               ("10 МГц", 1e7), ("100 МГц", 1e8), ("1 ГГц", 1e9)]
    lo, hi = math.log10(1e4), math.log10(1e9)

    def fx(freq):
        return x0 + (math.log10(freq) - lo) / (hi - lo) * (x1 - x0)

    for label, f in decades:
        x = fx(f)
        p.append(line(x, axisY - 5, x, axisY + 5, color=INK, sw=1.4))
        p.append(text(x, axisY + 22, label, size=11, color=MUTED))

    # смуга MnZn
    my = 120
    mx0, mx1 = fx(2e4), fx(2e6)
    p.append(rect(mx0, my, mx1 - mx0, 40, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text((mx0 + mx1) / 2, my + 25, "MnZn-ферит", size=14, color=NEG, bold=True))
    p.append(text(mx0, my - 12, "велика проникність → силові осердя", size=11.5, color=INK, anchor="start"))
    # «глухне» — згасання справа
    p.append(text(mx1 + 8, my + 25, "глухне", size=11, color="#9a2b22", anchor="start", bold=True))

    # смуга NiZn
    ny = 200
    nx0, nx1 = fx(1e6), fx(9e8)
    p.append(rect(nx0, ny, nx1 - nx0, 40, fill="#eef6ef", stroke=FIELD, sw=2, rx=8))
    p.append(text((nx0 + nx1) / 2, ny + 25, "NiZn-ферит", size=14, color=FIELD, bold=True))
    p.append(text(nx1, ny - 12, "ізолятор → ВЧ, антени, кільця, бусини", size=11.5, color=INK, anchor="end"))

    # вертикальна межа ~1–2 МГц
    bx = fx(1.5e6)
    p.append(line(bx, 95, bx, axisY, color=MUTED, sw=1.4, dash="5,4"))
    p.append(text(bx, 88, "межа вихрових струмів", size=11, color=MUTED, bold=True))

    render(os.path.join(IMG, "ferrite-families.svg"), W, H, *p)


if __name__ == "__main__":
    fig_hysteresis()
    fig_eddy()
    fig_families()
    print("OK: hysteresis.svg, eddy.svg, ferrite-families.svg")
