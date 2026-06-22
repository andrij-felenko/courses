# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── latency: кожен вимір приходить застарілим ─────────────────────────────────
# Ідея: поки GPS-фікс долетів, апарат уже зрушив. Зелена точка — де фікс каже
# «тут» (минуле), синя — де апарат насправді зараз; наївна корекція тягне назад.

def fig_latency():
    W, H = 720, 330
    p = []
    y = 170
    # вісь руху
    p.append(line(70, y, 650, y, color="#e5e7eb", sw=2.0))
    p.append(text(650, y - 12, "рух апарата →", size=11, color=MUTED, anchor="end"))

    gx, nx = 250, 470          # де фікс / де апарат зараз
    # пунктир «за Δt проїхав сюди»
    p.append(line(gx + 12, y - 18, nx - 12, y - 18, color=MUTED, sw=1.3, dash="4 3"))
    p.append(text((gx + nx) / 2, y - 26, "за Δt апарат проїхав сюди", size=10, color=MUTED))

    # зелена точка — фікс (минуле)
    p.append(circle(gx, y, 9, fill=FIELD, stroke=INK, sw=1.5))
    p.append(text(gx, y + 26, "GPS каже «тут»", size=11, color=FIELD, bold=True))
    p.append(text(gx, y + 42, "(а це було Δt тому)", size=10, color=MUTED))

    # синя точка — апарат зараз
    p.append(circle(nx, y, 11, fill=NEG, stroke=INK, sw=1.6))
    p.append(text(nx, y - 22, "апарат зараз", size=11, color=NEG, bold=True))

    # червона стрілка корекції назад
    p.append(arrow(nx - 14, y + 16, gx + 14, y + 16, color=POS, sw=2.2))
    p.append(text((gx + nx) / 2, y + 36, "вставити «як тепер» → тягне оцінку НАЗАД",
                  size=10.5, color=POS, bold=True))

    p.append(text(W / 2, 290, "GPS — найзатриманіший: фікс описує, де апарат був десяту частку секунди тому.",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, 308, "Вставиш застарілий відлік як свіжий — позиція засмикається, а в утриманні піде по колу.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "latency.svg"), W, H, *p,
           title="Кожен вимір застарілий: затримка псує поєднання")


# ── rewind: виправити минуле й переграти наперед ──────────────────────────────
# Ідея: буфер минулих станів; запізнілий фікс корегує стан на момент своєї мітки,
# тоді фільтр переграє вихід уперед до «зараз».

def fig_rewind():
    W, H = 720, 340
    p = []
    y = 200
    p.append(arrow(70, y, 650, y, color=INK, sw=1.6))
    p.append(text(650, y + 22, "час →", size=11, color=MUTED, anchor="end", bold=True))

    xs = [120, 210, 300, 390, 480, 570]
    cols = [MUTED, MUTED, FIELD, NEG, NEG, NEG]
    for i, (sx, c) in enumerate(zip(xs, cols)):
        p.append(circle(sx, y, 7, fill=c, stroke=INK, sw=1.2))
    p.append(text(120, y + 26, "буфер минулих станів", size=10, color=MUTED, anchor="start"))
    p.append(text(570, y - 18, "«зараз»", size=10.5, color=NEG, bold=True))

    # прилетів фікс
    b, bw, bh = textbox(560, 92, "прилетів GPS-фікс\nіз міткою часу (минуле)", size=10.5,
                        fill="#eafaf0", stroke=FIELD, sw=1.6, color=INK, bold=True)
    p.append(b)
    # 1) корекція на момент мітки (до зеленої точки)
    p.append(line(525, 110, 308, y - 10, color=FIELD, sw=1.8, dash="5 4"))
    p.append(text(300, y - 18, "1) корегуємо стан на МОМЕНТ виміру", size=10.5, color=FIELD, bold=True))
    # 2) переграти вперед
    p.append(arrow(305, y + 16, 568, y + 16, color="#b06b00", sw=2.2))
    p.append(text(440, y + 34, "2) переграти вихід уперед до «зараз»", size=10.5, color="#b06b00", bold=True))

    p.append(text(W / 2, 318, "Корекція лягає в правильну точку часу — без ривків. Саме так робить EKF в ArduPilot.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "rewind.svg"), W, H, *p,
           title="Лік від затримки: виправ минуле, переграй наперед")


# ── innovation: несподіванка як пульс фільтра ─────────────────────────────────
# Ідея: різниця «вимір − передбачення» в часі; мала коло нуля = здорово, стрибок
# за «ворота» = давач збрехав, такий вимір відхиляють.

def fig_innovation():
    W, H = 720, 330
    p = []
    bx, by, bw, bh = 70, 80, 580, 190
    p.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=8))
    zero = by + bh / 2
    p.append(line(bx, zero, bx + bw, zero, color=INK, sw=1.3))
    p.append(text(bx - 8, zero + 4, "0", size=10, color=MUTED, anchor="end"))
    p.append(text(bx - 8, by + 14, "вимір−передбач", size=10, color=MUTED, anchor="end", bold=True))
    p.append(text(bx + bw, by + bh - 6, "час →", size=11, color=MUTED, anchor="end"))

    # ворота
    g = bh * 0.36
    p.append(line(bx, zero - g, bx + bw, zero - g, color=POS, sw=1.2, dash="6 4"))
    p.append(line(bx, zero + g, bx + bw, zero + g, color=POS, sw=1.2, dash="6 4"))
    p.append(text(bx + 6, zero - g - 6, "ворота (поза ними → відхилити вимір)",
                  size=9.5, color=POS, anchor="start"))

    # крива: шум коло нуля, тоді стрибок за верхні ворота й назад
    import random
    random.seed(7)
    pts = []
    n = 220
    for i in range(n + 1):
        t = i / n
        x = bx + t * bw
        if 0.56 < t < 0.62:                # стрибок
            v = -g * (1.7 if 0.57 < t < 0.61 else 1.0)
        else:
            v = (random.random() - 0.5) * g * 0.55
        pts.append("%.1f,%.1f" % (x, zero + v))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    p.append(text(bx + 70, zero + g * 0.62, "здорово: мала, коло нуля",
                  size=10.5, color=FIELD, anchor="start", bold=True))
    p.append(circle(bx + bw * 0.585, by + 18, 5, fill=POS, stroke=INK, sw=1.2))
    p.append(text(bx + bw * 0.585 + 9, by + 21, "стрибок: давач збрехав / розбіжність",
                  size=10.5, color=POS, anchor="start", bold=True))

    p.append(text(W / 2, 300, "Несподіванка — найкорисніший показник здоров'я: мала — давачі згодні; стрибок — хтось бреше.",
                  size=11, color=MUTED, italic=True))
    p.append(text(W / 2, 318, "Вилізла за ворота — фільтр відхиляє той вимір: захист від поодинокого збою давача.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "innovation.svg"), W, H, *p,
           title="Несподіванка (innovation) — пульс оцінювача")


# ── logreading: лог викриває винного давача ───────────────────────────────────
# Ідея: три доріжки несподіванок (GNSS / магнітометр / баро); GNSS стрибає,
# решта спокійна — отже, винен GPS.

def fig_logreading():
    W, H = 720, 360
    p = []
    rows = [("GNSS", POS, True), ("Магнітометр", "#9333ea", False), ("Барометр", "#d98a00", False)]
    import random
    random.seed(3)
    lx, lw = 200, 460
    for r, (name, col, jump) in enumerate(rows):
        cy = 90 + r * 74
        p.append(text(lx - 14, cy + 4, name, size=11.5, color=col, anchor="end", bold=True))
        p.append(rect(lx, cy - 24, lw, 48, fill="#f8fafc", stroke="#e5e7eb", sw=1, rx=6))
        mid = cy
        p.append(line(lx, mid, lx + lw, mid, color="#cbd5e1", sw=1))
        pts = []
        n = 150
        for i in range(n + 1):
            t = i / n
            x = lx + t * lw
            if jump and 0.52 < t < 0.58:
                v = -19
            else:
                v = (random.random() - 0.5) * 11
            pts.append("%.1f,%.1f" % (x, mid + v))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" '
                 'stroke-linejoin="round"/>' % (" ".join(pts), col))
        if jump:
            p.append(text(lx + lw + 12, cy + 4, "← СТРИБОК тут!", size=10.5, color=POS, anchor="start", bold=True))
        else:
            p.append(text(lx + lw + 12, cy + 4, "спокійно ✓", size=10.5, color=FIELD, anchor="start", bold=True))

    b, bw, bh = textbox(W / 2, 318,
                        "Винен GPS (затінення / багатопроменевість): його несподіванка вилетіла за ворота, решта чиста.",
                        size=11, fill="#eef2ff", stroke=NEG, sw=1.5, color=INK, bold=True, min_w=600)
    p.append(b)

    render(os.path.join(OUT, "logreading.svg"), W, H, *p,
           title="Читання логу: оцінювач сам звітує, де болить")


if __name__ == "__main__":
    fig_latency()
    fig_rewind()
    fig_innovation()
    fig_logreading()
    print("OK: figures written to", OUT)
