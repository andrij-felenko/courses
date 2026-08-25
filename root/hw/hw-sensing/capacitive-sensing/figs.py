# -*- coding: utf-8 -*-
"""Фігури до статті «Ємнісне зондування» (book/electronics/analog/capacitive-sensing).
Три фігури:
  finger.svg   — палець як друга обкладка: ємність електрода на землю зростає
  methods.svg  — три способи зчитати ємність: RC-час, перенос заряду, ємнісний дільник
  baseline.svg — сирий відлік пливе, дотик — стрибок над повільним базовим рівнем
  lineage.svg  — родовід ідеї «заземлене тіло змінює ємність» (вставка hist-theremin-to-touch)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def pad(cx, cy, w=70, h=12, fill="#fff3e0", stroke=POS):
    """Прямокутна сенсорна площадка (електрод) з центром."""
    return rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, sw=2, rx=3)


def gnd(cx, y):
    out = [line(cx, y, cx, y + 8, color=INK, sw=1.6)]
    w = 16
    for i, ww in enumerate((w, w * 0.62, w * 0.28)):
        yy = y + 8 + i * 4
        out.append(line(cx - ww / 2, yy, cx + ww / 2, yy, color=INK, sw=1.6))
    return "".join(out)


# ── 1. Палець як друга обкладка ─────────────────────────────────────────────
def fig_finger():
    W, H = 640, 300
    out = []
    out.append(text(W / 2, 26, "Палець добудовує конденсатор до землі", size=17, bold=True))

    # Ліворуч: без пальця
    cx1 = 170
    out.append(text(cx1, 62, "немає пальця", size=13, color=MUTED, bold=True))
    out.append(pad(cx1, 150))
    out.append(text(cx1, 154, "електрод", size=11, color=INK))
    out.append(gnd(cx1, 235))
    out.append(line(cx1, 162, cx1, 235, color=INK, sw=1.6))
    # власна ємність електрода на землю — мала
    out.append(text(cx1, 205, "Cₒ", size=15, color=NEG, bold=True, anchor="end"))
    out.append(line(cx1 - 22, 188, cx1 - 22, 196, color=NEG, sw=2.4))
    out.append(line(cx1 - 22, 200, cx1 - 22, 208, color=NEG, sw=2.4))
    out.append(line(cx1 - 22, 162, cx1 - 22, 188, color=NEG, sw=1.4))
    out.append(line(cx1 - 22, 208, cx1 - 22, 235, color=NEG, sw=1.4))
    out.append(line(cx1, 162, cx1 - 22, 162, color=NEG, sw=1.4))
    out.append(line(cx1 - 22, 235, cx1, 235, color=NEG, sw=1.4))

    # Стрілка
    out.append(arrow(290, 150, 360, 150, color=INK, sw=2))

    # Праворуч: з пальцем
    cx2 = 470
    out.append(text(cx2, 62, "палець над електродом", size=13, color=POS, bold=True))
    # палець — заокруглений прямокутник зверху
    out.append(rect(cx2 - 16, 78, 32, 34, fill="#fdecea", stroke=POS, sw=2, rx=14))
    out.append(text(cx2, 100, "🖐", size=15))
    out.append(pad(cx2, 150))
    out.append(text(cx2, 154, "електрод", size=11, color=INK))
    out.append(gnd(cx2, 235))
    out.append(line(cx2, 162, cx2, 235, color=INK, sw=1.6))
    # додана ємність пальця Cf — паралельно, через тіло на землю
    out.append(text(cx2, 132, "Cբ", size=14, color=POS, bold=True))
    out.append(text(cx2 + 60, 100, "тіло →\nземля", size=11, color=MUTED, anchor="start"))
    out.append(line(cx2, 114, cx2, 122, color=POS, sw=2.4))   # верхня обкладка (палець)
    out.append(line(cx2, 138, cx2, 144, color=POS, sw=2.4))   # нижня (електрод)
    # стара ємність лишається
    out.append(text(cx2 - 22, 205, "Cₒ", size=13, color=NEG, anchor="end"))
    out.append(line(cx2 - 22, 188, cx2 - 22, 196, color=NEG, sw=2.2))
    out.append(line(cx2 - 22, 200, cx2 - 22, 208, color=NEG, sw=2.2))
    out.append(line(cx2 - 22, 162, cx2 - 22, 188, color=NEG, sw=1.3))
    out.append(line(cx2 - 22, 208, cx2 - 22, 235, color=NEG, sw=1.3))
    out.append(line(cx2, 162, cx2 - 22, 162, color=NEG, sw=1.3))
    out.append(line(cx2 - 22, 235, cx2, 235, color=NEG, sw=1.3))

    b, _, _ = textbox(W / 2, 278, "Сумарна ємність електрода на землю росте з Cₒ до Cₒ + Cբ — це і є сигнал",
                      size=12, color=INK, fill=FILL)
    out.append(b)
    render(os.path.join(IMG, "finger.svg"), W, H, *out)


# ── 2. Три способи зчитати ємність ──────────────────────────────────────────
def fig_methods():
    W, H = 720, 350
    out = []
    out.append(text(W / 2, 26, "Три способи перетворити ємність на число", size=17, bold=True))

    col = [130, 360, 590]
    titles = ["RC-час / частота", "перенос заряду", "ємнісний дільник"]
    for cx, t in zip(col, titles):
        out.append(text(cx, 58, t, size=13, bold=True, color=FIELD))

    # 1) RC: резистор + Cx, поріг → коливання
    cx = col[0]
    out.append(rect(cx - 70, 78, 140, 150, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    out.append(text(cx, 100, "R", size=13, color=INK))
    out.append(line(cx - 40, 110, cx + 40, 110, color=INK, sw=1.6))
    out.append(text(cx, 140, "Cₓ", size=14, color=POS, bold=True))
    out.append(line(cx - 12, 124, cx + 12, 124, color=POS, sw=2.4))
    out.append(line(cx - 12, 132, cx + 12, 132, color=POS, sw=2.4))
    # хвиля
    pts = []
    for i in range(0, 80):
        x = cx - 40 + i
        y = 185 + (10 if (i // 10) % 2 == 0 else -10)
        pts.append("%.0f,%.0f" % (x, y))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (" ".join(pts), INK))
    out.append(text(cx, 218, "більша Cₓ → нижча f", size=10, color=MUTED))

    # 2) перенос заряду: Cx наповнює Cref порціями, лічимо такти
    cx = col[1]
    out.append(rect(cx - 70, 78, 140, 150, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    out.append(text(cx - 38, 104, "Cₓ", size=13, color=POS, bold=True))
    out.append(line(cx - 50, 112, cx - 26, 112, color=POS, sw=2.2))
    out.append(line(cx - 50, 120, cx - 26, 120, color=POS, sw=2.2))
    out.append(arrow(cx - 18, 116, cx + 14, 116, color=INK, sw=1.8))
    out.append(text(cx + 40, 104, "C_оп", size=12, color=NEG, bold=True))
    out.append(line(cx + 26, 112, cx + 54, 112, color=NEG, sw=2.2))
    out.append(line(cx + 26, 120, cx + 54, 120, color=NEG, sw=2.2))
    # сходинки наповнення
    sx, sy = cx - 45, 200
    px = [sx]; py = [sy]
    for i in range(6):
        px += [sx + i * 14 + 14, sx + i * 14 + 14]
        py += [sy - i * 6, sy - i * 6 - 6]
    pts = " ".join("%.0f,%.0f" % (a, b) for a, b in zip(px, py))
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (pts, INK))
    out.append(text(cx, 220, "більша Cₓ → менше тактів", size=10, color=MUTED))

    # 3) ємнісний дільник: AC у Cx над Cref, міряємо амплітуду
    cx = col[2]
    out.append(rect(cx - 70, 78, 140, 150, fill=BG, stroke=MUTED, sw=1.2, rx=8))
    out.append(text(cx, 98, "~", size=20, color=INK, bold=True))
    out.append(text(cx - 28, 98, "AC", size=11, color=MUTED, anchor="end"))
    out.append(text(cx + 36, 128, "Cₓ", size=13, color=POS, bold=True))
    out.append(line(cx + 22, 136, cx + 50, 136, color=POS, sw=2.2))
    out.append(line(cx + 22, 144, cx + 50, 144, color=POS, sw=2.2))
    out.append(text(cx + 36, 178, "C_оп", size=11, color=NEG, bold=True))
    out.append(line(cx + 22, 186, cx + 50, 186, color=NEG, sw=2.2))
    out.append(line(cx + 22, 194, cx + 50, 194, color=NEG, sw=2.2))
    out.append(line(cx + 36, 108, cx + 36, 136, color=INK, sw=1.4))
    out.append(line(cx + 36, 144, cx + 36, 186, color=INK, sw=1.4))
    out.append(line(cx + 36, 194, cx + 36, 216, color=INK, sw=1.4))
    out.append(gnd(cx + 36, 216))
    out.append(arrow(cx - 6, 160, cx + 18, 160, color=INK, sw=1.6))
    out.append(text(cx - 26, 178, "амплі-\nтуда", size=10, color=MUTED))
    out.append(text(cx, 232, "більша Cₓ → менший рівень", size=10, color=MUTED))

    b, _, _ = textbox(W / 2, 302, "Спільне: крихітну зміну ємності переводимо в час, кількість тактів або напругу —\nте, що цифрова частина вміє безпосередньо виміряти",
                      size=11, color=INK, fill=FILL)
    out.append(b)
    render(os.path.join(IMG, "methods.svg"), W, H, *out)


# ── 3. Базовий рівень пливе, дотик — різкий стрибок ─────────────────────────
def fig_baseline():
    W, H = 640, 300
    out = []
    out.append(text(W / 2, 26, "Дотик — це стрибок над повільним базовим рівнем", size=16, bold=True))

    x0, y0, w, h = 60, 60, 520, 180
    out.append(line(x0, y0 + h, x0 + w, y0 + h, color=INK, sw=1.6))   # вісь часу
    out.append(line(x0, y0, x0, y0 + h, color=INK, sw=1.6))           # вісь відліку
    out.append(text(x0 + w, y0 + h + 18, "час", size=12, color=MUTED, anchor="end"))
    out.append(text(x0 - 8, y0 + 6, "відлік", size=12, color=MUTED, anchor="end"))

    # повільний дрейф базового рівня (наприклад, нагрів/вологість)
    import math
    base = []
    for i in range(0, w + 1, 4):
        t = i / w
        b = y0 + h - 40 - 18 * math.sin(t * 2.2)
        base.append((x0 + i, b))
    pts = " ".join("%.0f,%.0f" % p for p in base)
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="5 4"/>' % (pts, NEG))
    out.append(text(x0 + 96, base[24][1] - 12, "базовий рівень (повзе)", size=11, color=NEG, anchor="start"))

    # сирий сигнал = база + два дотики (різкі плато)
    raw = []
    for i in range(0, w + 1, 2):
        t = i / w
        b = y0 + h - 40 - 18 * math.sin(t * 2.2)
        bump = 0
        if 0.30 < t < 0.42:
            bump = 70
        if 0.62 < t < 0.78:
            bump = 70
        raw.append((x0 + i, b - bump))
    pts = " ".join("%.0f,%.0f" % p for p in raw)
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (pts, POS))

    # поріг над поточним базовим рівнем
    thr = []
    for i in range(0, w + 1, 4):
        t = i / w
        b = y0 + h - 40 - 18 * math.sin(t * 2.2)
        thr.append((x0 + i, b - 35))
    pts = " ".join("%.0f,%.0f" % p for p in thr)
    out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="2 4"/>' % (pts, FIELD))
    out.append(text(x0 + w - 4, thr[-1][1] - 6, "поріг = база − Δ", size=11, color=FIELD, anchor="end"))

    out.append(text(x0 + int(w * 0.36), y0 + 18, "дотик", size=11, color=POS, bold=True))
    out.append(text(x0 + int(w * 0.70), y0 + 18, "дотик", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "baseline.svg"), W, H, *out)


# ── 4. Родовід ідеї: від руки над антеною до скла в кишені (вставка hist) ────
def fig_lineage():
    W, H = 720, 330
    out = []
    out.append(text(W / 2, 26, "Один механізм крізь століття: заземлене тіло змінює ємність електрода",
                    size=15, bold=True))

    # Горизонтальна вісь часу
    x0, x1, y = 70, 650, 120
    out.append(line(x0, y, x1, y, color=INK, sw=2))
    out.append(arrow(x1 - 2, y, x1 + 14, y, color=INK, sw=2))
    out.append(text(x1 + 16, y + 4, "час", size=11, color=MUTED, anchor="start"))

    # Чотири віхи: рік, підпис, що саме сталося
    marks = [
        (0.02, "1920", "терменвокс", "рука над антеною\nведе висоту тону", POS),
        (0.40, "1965", "стаття Джонсона", "перший ємнісний\nтачскрин (ідея)", FIELD),
        (0.62, "1969", "патент US 3 482 241", "система для\nдиспетчера", NEG),
        (0.92, "наші дні", "скло смартфона", "мультитач\nкрізь скло", INK),
    ]
    for t, yr, title, what, col in marks:
        x = x0 + t * (x1 - x0)
        out.append(circle(x, y, 6, fill=col, stroke=col, sw=1))
        out.append(line(x, y - 6, x, y - 30, color=col, sw=1.4))
        out.append(text(x, y - 36, yr, size=13, color=col, bold=True))
        out.append(line(x, y + 6, x, y + 30, color=col, sw=1.4))
        out.append(text(x, y + 44, title, size=11, color=INK, bold=True))
        out.append(mtext(x, y + 60, what, size=10, color=MUTED, lh=1.2))

    b, _, _ = textbox(W / 2, 300,
                      "Ідея → реалізація → система → щоденна річ: між «рука змінює ємність» і склом у кишені —\nне стрибок, а той самий фізичний механізм, доведений до зрілості за століття",
                      size=11, color=INK, fill=FILL)
    out.append(b)
    render(os.path.join(IMG, "lineage.svg"), W, H, *out)


if __name__ == "__main__":
    fig_finger()
    fig_methods()
    fig_baseline()
    fig_lineage()
    print("OK: finger.svg, methods.svg, baseline.svg, lineage.svg")
