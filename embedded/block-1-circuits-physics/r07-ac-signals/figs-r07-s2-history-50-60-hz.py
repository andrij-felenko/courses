# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 📜-вставки до теми 1.7.2 —
«Чому 50 і 60 Гц: як світ розколовся на дві частоти».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена, головний figs.py не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — самодостатній скрипт).
Нумерація підписів у тексті: Рис. 1.7.2i.k (історія до теми 1.7.2).
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED = "#c0271e"
BLUE = "#1f47b5"
GREEN = "#1f8a3b"
INK = "#1b1b1b"
GREY = "#8a8a8a"
FAINT = "#e4e4e4"
COPPER = "#cf8b5e"
ORANGE = "#e08030"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", ORANGE: "aOrange"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def _sine_path(x0, y0, width, amp, cycles=1.0, phase=0.0, n=160):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * width
        y = y0 - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((x, y))
    return pts


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.2i.1 — «зоопарк частот» 1880–1900-х і збіжність до 50/60 Гц
# ════════════════════════════════════════════════════════════════════════════
def fig_frequency_zoo():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 30, "Зоопарк частот, що звузився до двох",
              18, INK, "middle", "bold")
    s += text(W / 2, 51, "1880-ті — десятки несумісних частот; 1890-ті — інженерний компроміс лишив 50 і 60 Гц",
              11.5, GREY, "middle", style="italic")

    # вісь частот (лог-подібна, але підписи реальні) ─ горизонтальна шкала
    ax0, ax1 = 70, 830
    ay = 150
    s += line(ax0, ay, ax1, ay, INK, 2)
    s += arrow(ax1, ay, ax1 + 12, ay, INK, 2)
    s += text(ax1 + 16, ay + 5, "Гц", 13, INK, "start", "bold")

    # позиції частот уздовж осі (приблизно лог-розкладка)
    freqs = [
        (16.667, "16⅔", GREY),
        (25, "25", GREY),
        (30, "30", GREY),
        (40, "40", ORANGE),
        (50, "50", BLUE),
        (60, "60", RED),
        (125, "125", GREY),
        (133, "133⅓", GREY),
    ]
    fmin, fmax = math.log10(15), math.log10(160)

    def fx(f):
        return ax0 + (math.log10(f) - fmin) / (fmax - fmin) * (ax1 - ax0)

    # риски шкали
    for f, lab, col in freqs:
        x = fx(f)
        big = f in (50, 60)
        s += line(x, ay - (9 if big else 6), x, ay + (9 if big else 6), col, 2.6 if big else 1.8)
        s += text(x, ay + 26, lab, 13 if big else 11.5, col, "middle",
                  "bold" if big else "normal")

    # зона освітлення (високі частоти) — вгорі праворуч
    xl0, xl1 = fx(62), fx(140)
    s += rect(xl0, 78, xl1 - xl0, 50, "#fdecea", RED, 1.4, 7)
    s += text((xl0 + xl1) / 2, 98, "освітлення любить", 11.5, RED, "middle", "bold")
    s += text((xl0 + xl1) / 2, 114, "ВИСОКУ частоту", 11.5, RED, "middle", "bold")
    s += text((xl0 + xl1) / 2, 124, "(менше мерехтіння)", 9.5, RED, "middle", style="italic")
    s += arrow(xl0 - 4, 116, fx(48) + 6, ay - 12, RED, 1.6, "4 3")

    # зона моторів (низькі частоти) — угорі ліворуч
    xm0, xm1 = fx(16), fx(58)
    s += rect(xm0, 78, xm1 - xm0, 50, "#eef6ef", GREEN, 1.4, 7)
    s += text((xm0 + xm1) / 2, 98, "мотор і трансформатор", 11.5, GREEN, "middle", "bold")
    s += text((xm0 + xm1) / 2, 114, "люблять НИЗЬКУ частоту", 11.5, GREEN, "middle", "bold")
    s += arrow(xm1 + 4, 116, fx(56) - 2, ay - 12, GREEN, 1.6, "4 3")

    # «вікно компромісу» 50–60
    xc0, xc1 = fx(48), fx(63)
    s += rect(xc0, ay + 36, xc1 - xc0, 22, "#fff7e6", ORANGE, 1.6, 6)
    s += text((xc0 + xc1) / 2, ay + 51, "вікно компромісу", 11, ORANGE, "middle", "bold")

    # дві гілки стандартизації вниз
    by = 304
    x50 = fx(50)
    x60 = fx(60)

    # 50 Гц — Європа (бокс ліворуч)
    bw = 332
    l50 = 40
    c50 = l50 + bw / 2
    s += arrow(x50, ay + 60, c50, by - 2, BLUE, 2.2)
    s += rect(l50, by, bw, 66, "#eef2fb", BLUE, 1.6, 10)
    s += text(c50, by + 23, "50 Гц — AEG (1891)", 13, BLUE, "middle", "bold")
    s += text(c50, by + 42, "після мерехтіння 40 Гц у Лауффен–Франкфурті;", 11, INK, "middle")
    s += text(c50, by + 58, "→ Європа й більшість світу", 11, INK, "middle")

    # 60 Гц — Захід (бокс праворуч)
    r60 = 860
    c60 = r60 - bw / 2
    s += arrow(x60, ay + 60, c60, by - 2, RED, 2.2)
    s += rect(r60 - bw, by, bw, 66, "#fdecea", RED, 1.6, 10)
    s += text(c60, by + 23, "60 Гц — Вестингауз (бл. 1890)", 13, RED, "middle", "bold")
    s += text(c60, by + 42, "арк-лампи йшли трохи краще на 60;", 11, INK, "middle")
    s += text(c60, by + 58, "→ Північна Америка, частина Японії", 11, INK, "middle")

    # 40 Гц — звідки підняли
    x40 = fx(40)
    s += arrow(x40, ay + 14, x40, ay - 12, ORANGE, 1.6)
    s += text(x40, ay + 47, "(40 — мерехтіло)", 9.5, ORANGE, "middle", style="italic")

    # 25 Гц — Ніагара (окрема гілка, бокс по центру внизу)
    x25 = fx(25)
    s += arrow(x25, ay + 14, W / 2 - 150, 398, GREY, 1.8, "5 4")
    s += rect(W / 2 - 150, 398, 300, 46, "#f4f4f4", GREY, 1.4, 9)
    s += text(W / 2, 417, "25 Гц — Ніагара (1895)", 12, INK, "middle", "bold")
    s += text(W / 2, 433, "швидкість турбіни зафіксували заздалегідь", 10, GREY, "middle")

    # підпис-висновок
    s += text(W / 2, 462, "Жодна з частот не «правильніша» фізично — вибір лишили інерція обладнання й ринку",
              11, INK, "middle", style="italic")
    save("hist-50-60-frequency-zoo.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.2i.2 — фізична суперечка: мерехтіння (висока f) vs мотор (низька f)
#                  + зв'язок частоти зі швидкістю генератора
# ════════════════════════════════════════════════════════════════════════════
def fig_tradeoff():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 30, "Чому саме десятки герц: дві вимоги тягнуть у різні боки",
              18, INK, "middle", "bold")
    s += text(W / 2, 51, "Висока частота вбиває мерехтіння ламп; низька — потрібна моторам і трансформаторам. 50–60 Гц — стик",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВА панель: лампа і мерехтіння ──
    s += rect(34, 72, 405, 196, "#fdecea", RED, 1.6, 12)
    s += text(236, 96, "Лампа: яскравість пульсує вдвічі частіше за струм", 12.5, RED, "middle", "bold")

    # дві осі: низька f (мерехтить) і висока f (рівно)
    ax = 70
    # низька частота
    s += text(ax, 124, "низька f (мала кількість «пульсів»)", 11, INK, "start", "bold")
    s += line(ax, 158, ax + 330, 158, GREY, 1.2)
    pts = []
    for i in range(0, 331):
        t = i / 330.0
        # яскравість ~ sin^2 → подвоєна частота, не падає до нуля повністю (теплова інерція)
        b = 0.5 + 0.5 * abs(math.sin(2 * math.pi * 2.0 * t))
        pts.append((ax + i, 158 - 26 * b))
    s += polyline(pts, RED, 2.4)
    s += text(ax + 340, 150, "мерехтить", 10.5, RED, "start", "bold")

    # висока частота
    s += text(ax, 200, "висока f (133 Гц): пульси зливаються в рівне світло", 11, INK, "start", "bold")
    s += line(ax, 236, ax + 330, 236, GREY, 1.2)
    pts = []
    for i in range(0, 331):
        t = i / 330.0
        b = 0.78 + 0.22 * abs(math.sin(2 * math.pi * 8.0 * t))
        pts.append((ax + i, 236 - 26 * b))
    s += polyline(pts, GREEN, 2.4)
    s += text(ax + 340, 228, "рівно", 10.5, GREEN, "start", "bold")
    s += text(236, 260, "→ освітлення штовхало частоту ВГОРУ (133, 125 Гц)", 11, INK, "middle", "bold")

    # ── ПРАВА панель: мотор/трансформатор ──
    s += rect(461, 72, 405, 196, "#eef6ef", GREEN, 1.6, 12)
    s += text(663, 96, "Індукційний мотор і трансформатор", 12.5, GREEN, "middle", "bold")
    s += text(663, 120, "матеріали 1890-х на 133 Гц працювали кепсько:", 11, INK, "middle")
    s += text(663, 140, "великий реактивний опір обмоток, втрати в залізі,", 11, INK, "middle")
    s += text(663, 160, "іскріння на колекторі перетворювачів", 11, INK, "middle")
    # стрілка вниз
    s += arrow(663, 178, 663, 214, GREEN, 2.4)
    s += text(663, 200, "потрібна НИЖЧА частота (~50–60 Гц)", 11.5, GREEN, "middle", "bold")
    s += text(663, 236, "один мотор + одне освітлення на спільній", 11, INK, "middle")
    s += text(663, 254, "мережі → компроміс десь посередині", 11, INK, "middle")

    # ── НИЖНЯ панель: зв'язок частоти зі швидкістю генератора ──
    by = 296
    s += rect(34, by, 832, 188, "#f7f7f7", INK, 1.4, 12)
    s += text(450, by + 24, "Частоту неможливо вибрати окремо від генератора",
              13.5, INK, "middle", "bold")
    s += text(450, by + 45, "f = (число пар полюсів) × (оберти за секунду)    —    те саме N = 120·f / P",
              12, INK, "middle")

    # три кружечки-генератори з різними полюсами/обертами → та сама родина
    def gen(cx, cy, poles, rpm, f, col):
        out = circle(cx, cy, 34, "#fff", col, 2.4)
        # полюси як рисочки по колу
        for k in range(poles):
            a = 2 * math.pi * k / poles
            x1 = cx + 24 * math.cos(a)
            y1 = cy + 24 * math.sin(a)
            x2 = cx + 33 * math.cos(a)
            y2 = cy + 33 * math.sin(a)
            out += line(x1, y1, x2, y2, col, 2.2)
        out += text(cx, cy + 5, f"{poles}п", 12, col, "middle", "bold")
        out += text(cx, cy + 58, f"{rpm} об/хв", 11, INK, "middle")
        out += text(cx, cy + 74, f"→ {f} Гц", 11.5, col, "middle", "bold")
        return out

    cy = by + 108
    s += gen(180, cy, 2, 3000, 50, BLUE)
    s += gen(360, cy, 4, 1500, 50, BLUE)
    s += text(270, cy - 44, "однакові 50 Гц — різні машини", 10.5, BLUE, "middle", style="italic")

    s += gen(620, cy, 2, 3600, 60, RED)
    s += gen(800, cy, 4, 1800, 60, RED)
    s += text(710, cy - 44, "однакові 60 Гц — різні машини", 10.5, RED, "middle", style="italic")

    # розділювач
    s += line(490, by + 60, 490, by + 172, FAINT, 1.6)

    s += text(450, by + 180, "Тому світ міг застрягти на будь-якій зручній частоті — і застряг одразу на двох",
              11, INK, "middle", style="italic")
    save("hist-50-60-tradeoff.svg", s)


if __name__ == "__main__":
    fig_frequency_zoo()
    fig_tradeoff()
    print("done")
