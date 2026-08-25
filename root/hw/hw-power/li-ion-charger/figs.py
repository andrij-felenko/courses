# -*- coding: utf-8 -*-
"""Фігури до теми «Зарядка Li-ion».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── CC/CV: дві фази — крива струму й крива напруги ────────────────────────────
def fig_ccv():
    W, H = 760, 430
    f = [text(W / 2, 28, "CC/CV: спершу сталий струм, тоді стала напруга",
              size=16, bold=True)]
    ox, oy = 80, 330          # початок осей
    span_x = 600
    top = 70
    # осі
    f.append(line(ox, oy, ox + span_x, oy, color=MUTED, sw=1.4))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.4))
    f.append(text(ox + span_x, oy + 24, "час →", size=11, color=MUTED, anchor="end"))
    # межа фаз CC|CV (момент, коли напруга дійшла 4.2 В)
    xcc = ox + span_x * 0.45
    f.append(line(xcc, top, xcc, oy, color=MUTED, sw=1.0, dash="4,4"))
    f.append(text((ox + xcc) / 2, top - 6, "CC", size=13, bold=True, color=NEG))
    f.append(text((xcc + ox + span_x) / 2, top - 6, "CV", size=13, bold=True, color=POS))

    # рівень 4.2 В
    v42 = top + 24
    f.append(line(ox, v42, ox + span_x, v42, color=MUTED, sw=1.0, dash="2,4"))
    f.append(text(ox - 8, v42 + 4, "4.2 В", size=10.5, color=NEG, anchor="end"))

    # крива напруги (синя): росте в CC, плато в CV
    vpts = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ox + t * span_x
        if xx <= xcc:
            tt = (xx - ox) / (xcc - ox)
            yy = oy - (oy - v42) * (1 - math.exp(-2.6 * tt)) / (1 - math.exp(-2.6))
        else:
            yy = v42
        vpts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join("%.1f,%.1f" % p for p in vpts), NEG))

    # крива струму (червона): плато в CC, спад у CV до C/10
    i_full = oy - 150          # рівень повного струму
    i_c10 = oy - 30            # рівень C/10
    ipts = []
    for i in range(0, 201):
        t = i / 200.0
        xx = ox + t * span_x
        if xx <= xcc:
            yy = i_full
        else:
            tt = (xx - xcc) / (ox + span_x - xcc)
            yy = i_c10 + (i_full - i_c10) * math.exp(-3.2 * tt)
        ipts.append((xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" stroke-dasharray="7,4"/>'
             % (" ".join("%.1f,%.1f" % p for p in ipts), POS))
    f.append(line(ox - 4, i_c10, ox + 4, i_c10, color=POS, sw=1.2))
    f.append(text(ox - 8, i_c10 + 4, "C/10", size=10.5, color=POS, anchor="end"))

    # легенда
    lx, ly = xcc + 120, 110
    f.append(line(lx, ly, lx + 30, ly, color=NEG, sw=2.8))
    f.append(text(lx + 38, ly + 4, "напруга", size=11.5, color=INK, anchor="start"))
    f.append(line(lx, ly + 22, lx + 30, ly + 22, color=POS, sw=2.8, dash="7,4"))
    f.append(text(lx + 38, ly + 26, "струм", size=11.5, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, 405,
                      "у CC струм сталий, напруга росте до 4.2 В · у CV напруга тримається, струм спадає · стоп, коли струм < C/10",
                      size=11, fill="#eef3fb", stroke=NEG)
    f.append(b)
    render(os.path.join(IMG, "ccv.svg"), W, H, *f)


# ── Повний цикл по фазах: precharge → CC → CV → стоп ──────────────────────────
def fig_phases():
    W, H = 780, 360
    f = [text(W / 2, 28, "Повний цикл заряду: від глибокого розряду до стопу",
              size=16, bold=True)]
    boxes = [
        ("глибокий\nрозряд", "< 3 В", FILL, INK),
        ("ПЕРЕДЗАРЯД", "крихітний струм\nпідняти напругу", "#eef3fb", NEG),
        ("CC", "повний струм\nнапруга росте", "#eef3fb", NEG),
        ("CV", "тримаємо 4.2 В\nструм спадає", "#fbeee6", POS),
        ("СТОП", "струм < C/10\nкомірка повна", "#e9f7ef", FIELD),
    ]
    n = len(boxes)
    bw, bh, gap = 118, 92, 22
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    cy = 175
    for i, (title_, sub, fill, col) in enumerate(boxes):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        f.append(mtext(x + bw / 2, cy - 14, title_, size=13, bold=True, color=col))
        f.append(mtext(x + bw / 2, cy + 20, sub, size=10, color=MUTED))
        if i < n - 1:
            ax = x + bw
            f.append(arrow(ax + 2, cy, ax + gap - 2, cy, color=LINE, sw=1.8))
    b, _, _ = textbox(W / 2, 320,
                      "у нормі комірка стартує одразу з CC; передзаряд — лише коли вона сіла глибоко",
                      size=11, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "phases.svg"), W, H, *f)


# ── Точність напруги: 4.10 / 4.20 / 4.25 — ємність проти життя ────────────────
def fig_voltage():
    W, H = 760, 380
    f = [text(W / 2, 28, "Верхня напруга: вище — ємніше, нижче — довговічніше",
              size=16, bold=True)]
    cols = [
        ("4.10 В", "недозаряд", "−кілька % ємності\nжиття × у рази", FIELD, "#e9f7ef"),
        ("4.20 В", "стандарт", "повна ємність\nточність ±1%", NEG, "#eef3fb"),
        ("4.25 В", "так НЕ можна", "стрес, нагрів\nризик розгону", POS, "#fbeee6"),
    ]
    bw, bh, gap = 200, 150, 26
    total = len(cols) * bw + (len(cols) - 1) * gap
    x0 = (W - total) / 2
    cy = 190
    for i, (volt, tag, body, col, fill) in enumerate(cols):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=2))
        f.append(text(x + bw / 2, cy - 42, volt, size=22, bold=True, color=col))
        f.append(text(x + bw / 2, cy - 16, tag, size=12, bold=True, color=col))
        f.append(mtext(x + bw / 2, cy + 16, body, size=11.5, color=INK))
    # стрілка-шкала «ємніше ↔ довговічніше»
    f.append(text(x0, cy + bh / 2 + 32, "← довговічніше", size=11.5, color=FIELD, anchor="start"))
    f.append(text(x0 + total, cy + bh / 2 + 32, "ємніше / небезпечніше →", size=11.5, color=POS, anchor="end"))
    render(os.path.join(IMG, "voltage.svg"), W, H, *f)


# ── Температурне вікно (стиль JEITA) ──────────────────────────────────────────
def fig_jeita():
    W, H = 780, 360
    f = [text(W / 2, 28, "Температурне вікно заряду (логіка JEITA)",
              size=16, bold=True)]
    zones = [
        ("< 0 °C", "ЗАБОРОНЕНО", "осідання літію\nметалом", POS, "#fbeee6"),
        ("0–10 °C", "знижений струм", "напр., половинний", NEG, "#eef3fb"),
        ("10–45 °C", "повний заряд", "штатний CC/CV", FIELD, "#e9f7ef"),
        ("> 45 °C", "знижена U / стоп", "гарячий заряд\nстарить", POS, "#fbeee6"),
    ]
    n = len(zones)
    bw, bh, gap = 162, 110, 16
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    cy = 175
    for i, (rng, tag, body, col, fill) in enumerate(zones):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.8))
        f.append(text(x + bw / 2, cy - 30, rng, size=15, bold=True, color=INK))
        f.append(text(x + bw / 2, cy - 6, tag, size=12, bold=True, color=col))
        f.append(mtext(x + bw / 2, cy + 22, body, size=10.5, color=MUTED))
    b, _, _ = textbox(W / 2, 318,
                      "усім керує давач температури комірки (TS); межі — за температурою САМОЇ комірки, не повітря",
                      size=11, fill=FILL, stroke=MUTED)
    f.append(b)
    render(os.path.join(IMG, "jeita.svg"), W, H, *f)


# ── Кожна хімія по-своєму ─────────────────────────────────────────────────────
def fig_targets():
    W, H = 760, 360
    f = [text(W / 2, 28, "Алгоритм заряду — частина хімії", size=16, bold=True)]
    rows = [
        ("Li-ion", "CC/CV до 4.20 В", "стоп за струмом < C/10", NEG),
        ("LiFePO4", "CC/CV до 3.65 В", "стоп за струмом < C/10", FIELD),
        ("Свинець", "CC/CV до ~2.4 В/елем.", "далі float ~2.3 В", MUTED),
        ("NiMH", "сталий СТРУМ", "стоп за −ΔV або dT/dt", POS),
    ]
    rh, gap = 56, 14
    bw = 600
    x0 = (W - bw) / 2
    y0 = 70
    for i, (chem, how, stop, col) in enumerate(rows):
        y = y0 + i * (rh + gap)
        f.append(rect(x0, y, bw, rh, fill=FILL, stroke=col, sw=1.8))
        f.append(rect(x0, y, 150, rh, fill="#ffffff", stroke=col, sw=1.8))
        f.append(text(x0 + 75, y + rh / 2 + 5, chem, size=15, bold=True, color=col))
        f.append(text(x0 + 168, y + rh / 2 - 4, how, size=12.5, color=INK, anchor="start"))
        f.append(text(x0 + 168, y + rh / 2 + 15, stop, size=11, color=MUTED, anchor="start"))
    f.append(text(W / 2, H - 14,
                  "однакова буква «CC/CV» — різні цілі; плутати алгоритми не можна",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "targets.svg"), W, H, *f)


# ── Зарядний вузол на практиці ────────────────────────────────────────────────
def fig_node():
    W, H = 780, 360
    f = [text(W / 2, 28, "Зарядний вузол: чип робить важке, розробник — кілька рішень",
              size=16, bold=True)]
    cy = 165
    # вхід
    bx, _, _ = textbox(95, cy, "вхід 5 В\n(USB)", size=12, fill="#eef3fb", stroke=NEG, min_w=110)
    f.append(bx)
    # чип
    chip = rect(250, cy - 55, 180, 110, fill=FILL, stroke=INK, sw=2)
    f.append(chip)
    f.append(text(340, cy - 30, "зарядний чип", size=14, bold=True))
    f.append(mtext(340, cy - 4, "CC/CV · опорна 4.2 В\nтермінація C/10 · JEITA",
                   size=10.5, color=MUTED))
    # комірка
    cl, _, _ = textbox(630, cy, "комірка\nLi-ion", size=12, fill="#e9f7ef", stroke=FIELD, min_w=110)
    f.append(cl)
    # стрілки силового тракту
    f.append(arrow(152, cy, 248, cy, color=LINE, sw=2))
    f.append(arrow(432, cy, 572, cy, color=LINE, sw=2))

    # ISET знизу до чипа
    f.append(arrow(300, cy + 95, 300, cy + 57, color=NEG, sw=1.6))
    f.append(text(300, cy + 112, "ISET — задає струм CC", size=11, color=NEG))
    # TS від комірки
    f.append(arrow(630, cy + 95, 380, cy + 57, color=POS, sw=1.6))
    f.append(text(630, cy + 112, "TS — термістор на комірці", size=11, color=POS, anchor="middle"))
    # STAT вгору
    f.append(arrow(340, cy - 57, 340, cy - 95, color=FIELD, sw=1.6))
    f.append(text(340, cy - 102, "STAT → МК / світлодіод", size=11, color=FIELD))

    render(os.path.join(IMG, "node.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ccv()
    fig_phases()
    fig_voltage()
    fig_jeita()
    fig_targets()
    fig_node()
    print("OK: 6 figures ->", IMG)
