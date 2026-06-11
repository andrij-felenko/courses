# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 1.8 —
«Від магнітного каменю до Ерстеда» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена, головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу 7 (за §9 — кожен скрипт самодостатній).
Нумерація: історія до розділу — секція 0 → Рис. 1.8.0.N.
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", ORANGE: "aOrange"}


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


def _arc_arrow(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.4):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    m = _MARK.get(color, "aInk")
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


def _compass_needle(cx, cy, length, ang_deg, north=RED, south=BLUE, w=6):
    """Стрілка компаса: північ (кольорова) у напрямі ang_deg (0° = праворуч, проти годинн. вгору)."""
    a = math.radians(ang_deg)
    nx, ny = cx + (length / 2) * math.cos(a), cy - (length / 2) * math.sin(a)
    sx, sy = cx - (length / 2) * math.cos(a), cy + (length / 2) * math.sin(a)
    out = line(sx, sy, cx, cy, south, w)
    out += line(cx, cy, nx, ny, north, w)
    # вістря-наконечник на півночі
    pa = a
    perp = a + math.pi / 2
    tip = [(nx, ny),
           (nx - 12 * math.cos(pa) + 5 * math.cos(perp), ny + 12 * math.sin(pa) - 5 * math.sin(perp)),
           (nx - 12 * math.cos(pa) - 5 * math.cos(perp), ny + 12 * math.sin(pa) + 5 * math.sin(perp))]
    out += polygon(tip, north)
    out += circle(cx, cy, 3.2, "#ffffff", INK, 1.4)
    return out


# ════════════════════════════════════════════════════════════════════════════
#  Історія до Розділу 1.8 — від магнітного каменю до Ерстеда.  Рис. 1.8.0.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.8.0.1 — стрічка часу: дві тисячі років компаса ─────────────────────
def fig_timeline():
    W, H = 980, 430
    s = header(W, H)
    s += text(W / 2, 30, "Дві тисячі років компаса: довга тиша між каменем і струмом",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "магнітний камінь знали тисячоліттями — але зв'язок із електрикою відкрився лише 1820 року",
              11.5, GREY, "middle", style="italic")

    # вісь часу (нелінійна — лише порядок подій; підписи дат на мітках)
    ax, ay, aw = 70, 250, 840
    s += line(ax, ay, ax + aw, ay, INK, 2.2)
    s += polygon([(ax + aw, ay), (ax + aw - 14, ay - 6), (ax + aw - 14, ay + 6)], INK)
    s += text(ax + aw + 6, ay + 5, "час", 11.5, INK, "start", "bold")

    # події: (частка по осі, дата, рядок1, рядок2, колір, «вгору?»)
    events = [
        (0.045, "~600 до н.е.", "Греція: Фалес", "магнітний камінь притягує", GREY, True),
        (0.165, "~80 н.е.", "Китай: Ван Чун", "«ківш, що вказує на південь»", RED, False),
        (0.345, "1088", "Шень Ко", "намагнічена голка; перше схилення", RED, True),
        (0.50, "~1190", "Александр Неккам", "перша згадка в Європі", BLUE, False),
        (0.625, "1269", "Петро Перегрін", "полюси N/S, стрілка на вістрі", BLUE, True),
        (0.785, "1600", "Вільям Гілберт", "Земля — це магніт (terrella)", GREEN, False),
        (0.95, "1820", "Ганс Ерстед", "СТРУМ хитає стрілку", INK, True),
    ]
    for frac, date, l1, l2, col, up in events:
        x = ax + aw * frac
        s += circle(x, ay, 6.5, col, col, 1)
        if up:
            s += line(x, ay - 6, x, ay - 40, col, 1.4, "4,3")
            box_y = ay - 40 - 56
            s += rect(x - 78, box_y, 156, 52, "#ffffff", col, 1.5, 8)
            s += text(x, box_y + 17, date, 11.5, col, "middle", "bold")
            s += text(x, box_y + 33, l1, 10, INK, "middle", "bold")
            s += text(x, box_y + 47, l2, 9, GREY, "middle")
        else:
            s += line(x, ay + 6, x, ay + 40, col, 1.4, "4,3")
            box_y = ay + 40
            s += rect(x - 78, box_y, 156, 52, "#ffffff", col, 1.5, 8)
            s += text(x, box_y + 17, date, 11.5, col, "middle", "bold")
            s += text(x, box_y + 33, l1, 10, INK, "middle", "bold")
            s += text(x, box_y + 47, l2, 9, GREY, "middle")

    # підсвітити «велику тишу» — від навігації до Ерстеда
    gx0 = ax + aw * 0.345
    gx1 = ax + aw * 0.95
    s += line(gx0, ay + 132, gx1, ay + 132, ORANGE, 1.6)
    s += line(gx0, ay + 127, gx0, ay + 137, ORANGE, 1.6)
    s += line(gx1, ay + 127, gx1, ay + 137, ORANGE, 1.6)
    s += text((gx0 + gx1) / 2, ay + 150, "понад 700 років компас служить, але МАГНЕТИЗМ і ЕЛЕКТРИКА лишаються двома різними загадками",
              10.5, ORANGE, "middle", "bold")
    save("fig-r08-hist-1-timeline.svg", s)


# ── Рис. 1.8.0.2 — дослід Ерстеда: стрілка стає ПОПЕРЕК дроту ──────────────────
def fig_oersted():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Дослід Ерстеда (1820): стрілка повертається ПОПЕРЕК дроту",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "не до дроту й не від нього — сила немовби обвиває провідник кільцем; так уперше зустрілися електрика й магнетизм",
              11, GREY, "middle", style="italic")

    # ── ЛІВА панель: струму нема — стрілка вздовж дроту (на північ) ──
    s += rect(40, 78, 410, 318, "#f7f7f7", GREY, 1.6, 12)
    s += text(245, 104, "Коло РОЗІМКНЕНЕ (струму нема)", 13, GREY, "middle", "bold")
    # дріт — горизонтальний (вісь Пн-Пд позначимо вертикаллю)
    wy = 250
    s += line(70, wy, 420, wy, COPPER, 4)
    s += text(80, wy - 10, "дріт", 10, COPPER, "start", "bold")
    # розрив кола + батарея-натяк
    s += line(245, wy, 245, wy + 60, COPPER, 3)
    s += line(220, wy + 60, 270, wy + 60, COPPER, 3)
    s += rect(232, wy + 64, 26, 34, "#ffffff", INK, 1.6, 3)
    s += line(245, wy + 64, 245, wy + 56, GREY, 5)        # розрив (ключ)
    s += text(262, wy + 84, "ключ", 9.5, GREY, "start")
    # позначка сторін світу
    s += text(245, 128, "Пн", 11, INK, "middle", "bold")
    s += text(245, 392, "Пд", 11, INK, "middle", "bold")
    s += arrow(245, 140, 245, 122, GREY, 1.4)
    # компас: стрілка дивиться на північ (вздовж дроту? — ні: уздовж Пн-Пд, тобто поперек дроту, бо дріт горизонтальний)
    # У цій панелі дріт горизонтальний, тож «вздовж меридіана» = вертикально (вгору на Пн).
    s += circle(245, wy, 46, "none", FAINT, 1.6)
    s += _compass_needle(245, wy, 78, 90, RED, BLUE, 6)   # 90° = вгору (на північ)
    s += text(150, wy + 4, "стрілка —", 10, INK, "end", "bold")
    s += text(150, wy + 18, "на північ", 10, INK, "end", "bold")

    # ── стрілка-перехід «вмикаємо струм» ──
    s += arrow(456, 235, 498, 235, GREEN, 3.2)
    s += text(477, 224, "вмикаємо", 10, GREEN, "middle", "bold")
    s += text(477, 256, "струм I", 10.5, RED, "middle", "bold")

    # ── ПРАВА панель: струм тече — стрілка розвертається ПОПЕРЕК дроту ──
    s += rect(506, 78, 410, 318, "#eef7f0", GREEN, 1.8, 12)
    s += text(711, 104, "Коло ЗАМКНЕНЕ — тече струм I", 13, GREEN, "middle", "bold")
    wy2 = 250
    s += arrow(536, wy2, 890, wy2, RED, 4)                # дріт зі струмом (напрям I)
    s += text(884, wy2 - 12, "I", 12.5, RED, "end", "bold", "italic")
    s += line(711, wy2, 711, wy2 + 60, COPPER, 3)
    s += line(686, wy2 + 60, 736, wy2 + 60, COPPER, 3)
    s += rect(698, wy2 + 64, 26, 34, "#ffffff", INK, 1.6, 3)
    s += line(703, wy2 + 81, 719, wy2 + 81, INK, 2)       # ключ замкнено
    s += text(728, wy2 + 84, "ключ", 9.5, GREY, "start")
    s += text(711, 128, "Пн", 11, GREY, "middle", "bold")
    # кільцеве поле навколо дроту (концентричні дуги + напрям)
    for r in (60, 84):
        s += _arc_arrow(711, wy2, r, 200, 340, GREEN, 1.6)
    s += text(711, wy2 - 96, "магнітне поле обвиває дріт кільцями", 10, GREEN, "middle", "bold")
    # компас: стрілка розвернулась майже поперек дроту (≈ горизонтально)
    s += circle(711, wy2, 46, "none", FAINT, 1.6)
    s += _compass_needle(711, wy2, 78, 18, RED, BLUE, 6)  # ~18° від горизонту → майже поперек початкового напряму
    # дуга повороту від «на північ» (90°) до нового напряму
    s += _arc_arrow(711, wy2, 30, 90, 24, ORANGE, 2.0)
    s += text(670, wy2 - 30, "поворот", 9.5, ORANGE, "end", "bold")

    s += text(W / 2, 420, "Ключ спостереження: стрілка стала ПОПЕРЕК, а не вздовж — отже, дія струму не «по лінії», а закручена навколо провідника.",
              11, INK, "middle", "bold")
    save("fig-r08-hist-2-oersted.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_oersted()
    print("done.")
