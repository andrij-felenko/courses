# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 📜-вставки до теми 1.8.8 —
«Едвін Холл: ефект, відкритий за 18 років до електрона».
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Хелпери скопійовано з figs.py розділу (за §9 — самодостатній скрипт).
Нумерація підписів у тексті: Рис. 1.8.8i.k (історія до теми 1.8.8).
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
GOLD = "#d8a92b"
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


def _bfield_into(cx, cy, r, col=GREEN, n=4):
    """Кружок із хрестиками — поле B спрямоване «у площину» (від нас)."""
    out = ""
    step = 2 * r / (n + 1)
    for i in range(n):
        for j in range(n):
            x = cx - r + step * (i + 1)
            y = cy - r + step * (j + 1)
            if (x - cx) ** 2 + (y - cy) ** 2 <= (r - 4) ** 2:
                d = 3.0
                out += line(x - d, y - d, x + d, y + d, col, 1.4)
                out += line(x - d, y + d, x + d, y - d, col, 1.4)
    return out


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.8.8i.1 — суперечка з Максвеллом: на що діє сила — на провідник чи на струм?
#                  і як тонке золото зробило крихітний ефект видимим
# ════════════════════════════════════════════════════════════════════════════
def fig_maxwell_question():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 30, "Питання 1879 року: магніт штовхає провідник — чи самі носії в ньому?",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 51,
              "Максвелл у «Трактаті» (1873) писав: сила діє «на провідник, а не на струм». Холл вирішив це перевірити.",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВА панель: версія Максвелла — рухається весь провідник ──
    s += rect(34, 74, 405, 196, "#f4f4f4", GREY, 1.6, 12)
    s += text(236, 98, "Якби сила діяла на ПРОВІДНИК", 13, GREY, "middle", "bold")
    # провідник (брусок)
    bx, by, bw, bh = 96, 150, 230, 40
    s += rect(bx, by, bw, bh, "#fbe9d6", COPPER, 2, 6)
    s += text(bx + bw / 2, by + bh / 2 + 5, "струм І →", 12.5, INK, "middle", "bold")
    # поле B (у площину)
    s += _bfield_into(bx + bw / 2, by - 36, 26, GREEN, 4)
    s += text(bx + bw / 2, by - 70, "B (у площину)", 11, GREEN, "middle", "bold")
    # стрілка: весь брусок зноситься вниз
    s += arrow(bx + bw / 2, by + bh + 8, bx + bw / 2, by + bh + 44, INK, 2.6)
    s += text(bx + bw / 2, by + bh + 60, "зноситься брусок цілком", 11, INK, "middle")
    s += text(236, 262, "→ розподіл заряду в металі не міняється", 11, GREY, "middle", style="italic")

    # ── ПРАВА панель: версія Холла — носії тиснуться вбік ──
    s += rect(461, 74, 405, 196, "#eef6ef", GREEN, 1.6, 12)
    s += text(663, 98, "Якби сила діяла на НОСІЇ струму", 13, GREEN, "middle", "bold")
    bx2 = 523
    s += rect(bx2, by, bw, bh, "#fbe9d6", COPPER, 2, 6)
    s += text(bx2 + bw / 2, by - 6, "струм І →", 12, INK, "middle", "bold")
    s += _bfield_into(bx2 + bw / 2, by - 40, 22, GREEN, 4)
    # носії тиснуться до нижнього краю → + знизу, − зверху (умовно)
    for k in range(5):
        xx = bx2 + 30 + k * 44
        s += arrow(xx, by + 8, xx, by + bh - 8, BLUE, 1.8)
    s += text(bx2 + bw + 6, by + 6, "−", 18, BLUE, "start", "bold")
    s += text(bx2 + bw + 6, by + bh - 2, "+", 18, RED, "start", "bold")
    # поперечна напруга
    s += line(bx2 - 14, by + 2, bx2 - 14, by + bh - 2, INK, 1.4, "3 3")
    s += text(bx2 - 20, by + bh / 2 + 4, "Uₕ", 13, INK, "end", "bold", "italic")
    s += text(663, 262, "→ виникає поперечна напруга на краях — ОЦЕ й шукав Холл",
              11, GREEN, "middle", "bold")

    # ── НИЖНЯ панель: чому золота фольга ──
    ny = 300
    s += rect(34, ny, 832, 178, "#fff7e6", ORANGE, 1.6, 12)
    s += text(450, ny + 24, "Ефект крихітний — тож Холл узяв найтоншу золоту фольгу",
              13.5, INK, "middle", "bold")
    s += text(450, ny + 46,
              "У товстому бруску носіїв багато, поперечне поле мізерне; у тонкому листку той самий струм «згущено» —",
              11, INK, "middle")
    s += text(450, ny + 63,
              "напруга на краях зростає й нарешті ворушить стрілку гальванометра.",
              11, INK, "middle")

    # товстий брусок vs тонкий листок
    cy = ny + 122
    s += text(150, cy - 34, "товстий брусок", 11.5, GREY, "middle", "bold")
    s += rect(80, cy - 22, 140, 44, "#fbe9d6", COPPER, 2, 5)
    s += text(150, cy + 5, "Uₕ — мізерна", 11, GREY, "middle", style="italic")

    s += text(420, cy, "→", 22, INK, "middle", "bold")

    s += text(640, cy - 34, "тонка золота фольга", 11.5, GOLD, "middle", "bold")
    s += rect(560, cy - 6, 160, 12, "#fdf0c8", GOLD, 2, 3)
    s += text(640, cy + 26, "Uₕ — вимірна", 11.5, GREEN, "middle", "bold")

    s += line(305, ny + 86, 305, ny + 162, FAINT, 1.6)
    save("hist-hall-maxwell-question.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.8.8i.2 — стрічка часу: ефект (1879) на 18 років випередив електрон (1897);
#                  знак напруги виявився «не тим» → загадка, яку зняла квантова теорія
# ════════════════════════════════════════════════════════════════════════════
def fig_timeline_puzzle():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 30, "Ефект є — а носія ще нема: 18 років без електрона",
              17.5, INK, "middle", "bold")
    s += text(W / 2, 51,
              "Холл міряв рух заряду, не знаючи, що то за заряд. А знак напруги в деяких металах виявився «неправильним».",
              11.5, GREY, "middle", style="italic")

    # вісь часу
    ax0, ax1 = 80, 820
    ay = 150
    s += line(ax0, ay, ax1, ay, INK, 2)
    s += arrow(ax1, ay, ax1 + 12, ay, INK, 2)
    s += text(ax1 + 16, ay + 5, "рік", 12.5, INK, "start", "bold")

    ymin, ymax = 1870, 1985

    def tx(y):
        return ax0 + (y - ymin) / (ymax - ymin) * (ax1 - ax0)

    # події
    events = [
        (1873, "Максвелл:\n«Трактат»", GREY, 1, "сила на провідник,\nне на струм"),
        (1879, "ЕФЕКТ ХОЛЛА", RED, -1, "поперечна напруга;\nХоллу 23 роки"),
        (1880, "аномальний\nефект", ORANGE, 1, "у залізі ~10×\nбільший"),
        (1897, "ЕЛЕКТРОН", BLUE, -1, "Дж. Дж. Томсон;\nаж тепер ясно,\nщо то за носій"),
        (1980, "квантовий\nефект Холла", GREEN, 1, "фон Клітцинг;\nеталон опору"),
    ]
    for yr, lab, col, side, note in events:
        x = tx(yr)
        big = lab in ("ЕФЕКТ ХОЛЛА", "ЕЛЕКТРОН")
        s += line(x, ay - 7, x, ay + 7, col, 2.4 if big else 1.8)
        s += circle(x, ay, 5.5 if big else 4, col, col, 1)
        s += text(x, ay + 24, str(yr), 12 if big else 11, col, "middle", "bold")
        # підпис подієвий
        ly = ay - 30 if side < 0 else ay + 46
        for i, ln in enumerate(lab.split("\n")):
            s += text(x, ly + i * 15 * (1 if side > 0 else -1) - (0 if side > 0 else 0),
                      ln, 12 if big else 11, col, "middle", "bold")
        # примітка дрібним
        ny0 = ay - 30 - 17 * (len(lab.split("\n"))) if side < 0 else ay + 46 + 16 * len(lab.split("\n"))
        for i, ln in enumerate(note.split("\n")):
            s += text(x, ny0 + i * 13, ln, 9.5, INK, "middle", style="italic")

    # дужка «18 років» між 1879 і 1897
    x1, x2 = tx(1879), tx(1897)
    yb = ay + 96
    s += line(x1, yb, x2, yb, INK, 1.6)
    s += line(x1, yb - 5, x1, yb + 5, INK, 1.6)
    s += line(x2, yb - 5, x2, yb + 5, INK, 1.6)
    s += text((x1 + x2) / 2, yb + 18, "18 років", 12.5, INK, "middle", "bold")
    s += text((x1 + x2) / 2, yb + 34, "ефект виміряно раніше за носія", 10, GREY, "middle", style="italic")

    # нижня рамка — загадка знаку
    py = 372
    s += rect(60, py, 780, 80, "#eef2fb", BLUE, 1.6, 12)
    s += text(450, py + 24, "Загадка, що пережила самого Холла", 13, BLUE, "middle", "bold")
    s += text(450, py + 45,
              "Знак напруги показує знак носіїв. Та в деяких металах він виходив «додатним», ніби заряд +",
              11, INK, "middle")
    s += text(450, py + 63,
              "— провідники з ДІРКАМИ. Пояснила це лише квантова зонна теорія (1930-ті), а не сам дослід.",
              11, INK, "middle")
    save("hist-hall-timeline-puzzle.svg", s)


if __name__ == "__main__":
    fig_maxwell_question()
    fig_timeline_puzzle()
    print("done")
