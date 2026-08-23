# -*- coding: utf-8 -*-
"""Фігури до кроку «Практикум даташитів: мікроконтролер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RED, GRN, BLU = POS, FIELD, NEG


# ── 1. Документ-родина: не один PDF, а полиця ────────────────────────────────
def fig_docfamily():
    W, H = 720, 330
    f = [text(W / 2, 28, "МК — не один PDF, а полиця документів", size=16, bold=True)]
    docs = [
        ("Datasheet", "паспорт: межі, живлення, такти, перелік периферії",
         "відповідає: чи годиться й чи виживе", "#eaf0fd", BLU),
        ("Reference manual", "як кожен блок працює: регістри, біти, режими",
         "відповідає: як це запрограмувати", "#eafaf1", GRN),
        ("Errata", "підтверджені баги кремнію й обхідні шляхи",
         "відповідає: чого НЕ робити на цій ревізії", "#fdecea", RED),
        ("Hardware design", "як розвести плату: живлення, кварц, землі",
         "відповідає: як завести його на платі", "#fdf1dc", "#b8860b"),
    ]
    x, y0, bh, gap = 44, 56, 58, 12
    for i, (name, what, ans, fill, col) in enumerate(docs):
        y = y0 + i * (bh + gap)
        f.append(rect(x, y, 632, bh, fill=fill, stroke=col, sw=1.6, rx=8))
        f.append(text(x + 16, y + 24, name, size=13.5, color=col, bold=True, anchor="start"))
        fs = fit_font(what, 470, 11)
        f.append(text(x + 150, y + 22, what, size=fs, color=INK, anchor="start"))
        fa = fit_font(ans, 470, 10.5)
        f.append(text(x + 150, y + 42, ans, size=fa, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "docfamily.svg"), W, H, *f)


# ── 2. Живлення: середній струм проти пікового ──────────────────────────────
def fig_power_burst():
    W, H = 720, 320
    f = [text(W / 2, 28, "Живлення МК: вирішує не середній струм, а пік", size=16, bold=True)]

    # осі
    ox, oy, pw, ph = 70, 250, 560, 170
    f.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))           # час
    f.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))           # струм
    f.append(text(ox + pw, oy + 20, "час", size=11, color=MUTED, anchor="end"))
    f.append(text(ox - 8, oy - ph + 4, "струм", size=11, color=MUTED, anchor="end"))

    base = oy - 26          # рівень «сну/обробки», ~тонка лінія
    peak = oy - 150         # рівень піку передавання

    # рівні-пунктири
    f.append(line(ox, base, ox + pw, base, color=GRN, sw=1.3, dash="5 4"))
    f.append(line(ox, peak, ox + pw, peak, color=RED, sw=1.3, dash="5 4"))
    f.append(text(ox + pw + 4, base + 4, "середній", size=10.5, color=GRN, anchor="start"))
    f.append(text(ox + pw + 4, peak + 4, "пік TX", size=10.5, color=RED, anchor="start"))

    # профіль струму: фон низький, із короткими сплесками радіо
    pts = [(ox, base)]
    x = ox
    seg = pw / 12.0
    spikes = [2, 6, 9]      # де радіо «стріляє»
    for i in range(12):
        x0 = ox + i * seg
        if i in spikes:
            pts += [(x0 + seg * 0.30, base), (x0 + seg * 0.34, peak),
                    (x0 + seg * 0.55, peak), (x0 + seg * 0.59, base)]
        else:
            pts += [(x0 + seg, base)]
    pts.append((ox + pw, base))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (poly, INK))

    # підписи-винесення
    b1, _, _ = textbox(ox + 150, oy - ph - 4, "фоновий струм ~десятки мА", size=10.5,
                       fill="#eafaf1", stroke=GRN, color=GRN)
    f.append(b1)
    b2, _, _ = textbox(ox + 430, oy - ph - 4, "сплеск радіо ~240 мА", size=10.5,
                       fill="#fdecea", stroke=RED, color=RED)
    f.append(b2)
    f.append(text(W / 2, H - 10,
                  "Джерело беруть під ПІК (≥ 0.5 А), а конденсатор — щоб витримати сплеск; інакше brown-out і перезавантаження",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "power-burst.svg"), W, H, *f)


# ── 3. Той самий маршрут — тепер по підсистемах ─────────────────────────────
def fig_subsystem_route():
    W, H = 720, 340
    f = [text(W / 2, 26, "Один даташит МК = маршрут практикуму, повторений по блоках", size=15.5, bold=True)]

    # ліворуч — той самий 6-кроковий маршрут (стисло), праворуч — підсистеми
    lx, ly = 44, 56
    steps = ["1 перша сторінка", "2 абсолютні максимуми", "3 робочий режим",
             "4 критичний параметр", "5 графіки", "6 errata й виноски"]
    f.append(text(lx + 95, ly - 10, "маршрут одного компонента", size=11, color=MUTED, bold=True))
    for i, s in enumerate(steps):
        yy = ly + i * 30
        f.append(rect(lx, yy, 190, 24, fill=FILL, stroke="#9bb0c2", sw=1.3, rx=6))
        f.append(text(lx + 12, yy + 16, s, size=10.5, color=INK, anchor="start"))
        if i < len(steps) - 1:
            f.append(line(lx + 95, yy + 24, lx + 95, yy + 30, color=MUTED, sw=1.2))

    # велика стрілка «×N підсистем»
    midx = 270
    f.append(arrow(midx, 150, midx + 60, 150, color=INK, sw=2.2))
    b, _, _ = textbox(midx + 30, 122, "× кожна\nпідсистема", size=10.5, fill=BG, stroke=INK)
    f.append(b)

    # праворуч — стос підсистем, кожна зі своїм критичним рядком
    rx, ry = 372, 56
    subs = [
        ("Живлення", "пік струму, brown-out, розв'язка", "#eaf0fd", BLU),
        ("Такти", "кварц, допуск частоти, межа f", "#eafaf1", GRN),
        ("GPIO", "VIH/VIL, струм піна, дерейт", "#fdf1dc", "#b8860b"),
        ("Периферія", "скільки, спільні піни, мукс", "#f3e9f3", "#7d5ba6"),
        ("Пам'ять", "Flash/RAM, межі доступу", "#fdecea", RED),
    ]
    for i, (nm, cr, fill, col) in enumerate(subs):
        yy = ry + i * 50
        f.append(rect(rx, yy, 300, 42, fill=fill, stroke=col, sw=1.6, rx=8))
        f.append(text(rx + 14, yy + 18, nm, size=12, color=col, bold=True, anchor="start"))
        fs = fit_font(cr, 280, 10.5)
        f.append(text(rx + 14, yy + 34, cr, size=fs, color=INK, anchor="start"))
    f.append(text(W / 2, H - 8,
                  "Маршрут той самий; змінюється лише, який рядок критичний у кожному блоці",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "subsystem-route.svg"), W, H, *f)


# ── 4. Історія: як один аркуш розрісся в полицю (для hist-вставки) ───────────
def fig_doc_timeline():
    W, H = 720, 360
    f = [text(W / 2, 26, "Півстоліття нашарувань: як аркуш даних став полицею", size=15.5, bold=True)]

    # горизонтальна вісь часу (позначки самі кажуть, що це час — окремий підпис зайвий)
    ax, ay, aw = 60, 300, 600
    f.append(line(ax, ay, ax + aw, ay, color=INK, sw=1.8))
    marks = [(0.02, "1930-ті"), (0.30, "1970-ті"), (0.55, "1980-ті"),
             (0.72, "1994"), (0.98, "сьогодні")]
    for fr, lbl in marks:
        mx = ax + aw * fr
        f.append(line(mx, ay - 5, mx, ay + 5, color=INK, sw=1.5))
        f.append(text(mx, ay + 20, lbl, size=10, color=MUTED))

    # шари, що додаються один за одним; кожен «стартує» на своїй позначці й тягнеться далі
    def layer(y, x_start_fr, name, note, fill, col):
        xs = ax + aw * x_start_fr
        xe = ax + aw * 0.985
        f.append(rect(xs, y, xe - xs, 34, fill=fill, stroke=col, sw=1.6, rx=8))
        f.append(text(xs + 12, y + 15, name, size=11.5, color=col, bold=True, anchor="start"))
        fs = fit_font(note, (xe - xs) - 24, 10)
        f.append(text(xs + 12, y + 29, note, size=fs, color=INK, anchor="start"))

    layer(54, 0.02, "Data sheet (аркуш даних)",
          "паспорт замість виміру: межі, крива, типова схема — спершу буквально один аркуш",
          "#eaf0fd", BLU)
    layer(98, 0.30, "Datasheet vs Reference manual",
          "опис розділили за роллю читача: «чи годиться» окремо від «як програмувати»",
          "#eafaf1", GRN)
    layer(142, 0.55, "Errata: листок помилок кремнію",
          "де кремній розходиться з паспортом, плюс обхід",
          "#fdf1dc", "#b8860b")

    # маркер FDIV — поворотна точка: вертикаль на осі + callout ЛІВОРУЧ, що клеарить лінію,
    # і короткий поводок від рамки до точки на осі
    fx = ax + aw * 0.72
    f.append(line(fx, 234, fx, ay - 6, color=RED, sw=1.5, dash="4 3"))
    f.append(circle(fx, ay, 4, fill=RED, stroke=RED, sw=1))
    bcx = fx - 96
    b, bw, bh = textbox(bcx, 214, "1994: Pentium FDIV —\nerrata стає ПУБЛІЧНОЮ", size=10,
                        fill="#fdecea", stroke=RED, color=RED)
    f.append(line(bcx + bw / 2, 214, fx, 234, color=RED, sw=1.2))  # поводок до вертикалі
    f.append(b)

    f.append(text(W / 2, H - 12,
                  "Кожен шар додала конкретна незручність; полиця не задум, а наросла історія",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "doc-timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_docfamily()
    fig_power_burst()
    fig_subsystem_route()
    fig_doc_timeline()
    print("OK: 4 figures ->", IMG)
