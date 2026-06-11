# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для компонентної вставки 🔌 до теми 1.9.6 —
«Розводка "землі" на макетці: зірка проти ланцюжка» (Модуль 1, Розділ 1.9).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена; головний figs.py розділу не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: вставка-компонент до теми 1.9.6 → Рис. 1.9.6c.N.
"""
import os

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
PURPLE = "#7a3fae"
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


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", ORANGE: "aOrange"}


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


def gnd_symbol(x, y, color=INK, scale=1.0):
    """Символ землі ⏚ зі стовбуром угору від (x,y)."""
    s = line(x, y, x, y + 12 * scale, color, 2)
    yy = y + 12 * scale
    s += line(x - 12 * scale, yy, x + 12 * scale, yy, color, 2)
    s += line(x - 7.5 * scale, yy + 5 * scale, x + 7.5 * scale, yy + 5 * scale, color, 2)
    s += line(x - 3.5 * scale, yy + 10 * scale, x + 3.5 * scale, yy + 10 * scale, color, 2)
    return s


def block(x, y, w, h, label, sub, fill="#f3f5f8", stroke=INK):
    s = rect(x, y, w, h, fill, stroke, 2, 7)
    s += text(x + w / 2, y + h / 2 - 2, label, 13.5, INK, "middle", "bold")
    if sub:
        s += text(x + w / 2, y + h / 2 + 15, sub, 10.5, GREY, "middle")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🔌 до теми 1.9.6 — зірка проти ланцюжка.  Рис. 1.9.6c.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.9.6c.1 — топологія: ланцюжок (спільний імпеданс) проти зірки ──────
def fig_topology():
    W, H = 1020, 600
    s = header(W, H)
    s += text(W / 2, 30, "Чому ланцюжок «землі» додає помилку, а зірка — ні",
              19, INK, "middle", "bold")
    s += text(W / 2, 52,
              "однаковий провідник «землі» (тонкий ⇒ має опір r); різниця лише в тому, ЯК під'єднані повернення струмів",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВО: ЛАНЦЮЖОК (daisy-chain) ────────────────────────────────────────
    bx = 60
    s += text(bx + 200, 92, "ЛАНЦЮЖОК (daisy-chain)", 14.5, RED, "middle", "bold")
    s += text(bx + 200, 110, "усі повернення йдуть одним спільним відрізком", 10.5, GREY, "middle")

    # спільна шина землі (горизонтальна), праворуч — точка GND (0 В)
    railY = 430
    gx0, gx1 = bx + 30, bx + 380
    s += line(gx0, railY, gx1, railY, INK, 6)              # «товста» частина праворуч
    # три сегменти з опором між трьома точками під'єднання
    seg_x = [bx + 60, bx + 170, bx + 280]                  # вузли A, B, C на шині
    node_lbl = ["A", "B", "C"]
    # ділянки опору між вузлами (зиґзаґ-резистор)
    def zig(x1, x2, y, color, lab):
        out = ""
        n = 6
        amp = 7
        pts = [(x1, y)]
        for i in range(1, n):
            xx = x1 + (x2 - x1) * i / n
            pts.append((xx, y + (amp if i % 2 else -amp)))
        pts.append((x2, y))
        out += polyline(pts, color, 2.6)
        out += text((x1 + x2) / 2, y - 14, lab, 10.5, color, "middle", "bold")
        return out

    # GND-точка (0 В) праворуч
    s += line(gx1, railY, gx1, railY, INK, 6)
    s += circle(gx1, railY, 4, INK, INK, 1)
    s += gnd_symbol(gx1, railY, INK, 1.1)
    s += text(gx1 + 16, railY + 4, "GND (0 В)", 11, INK, "start", "bold")

    # сегменти опору: C–GND, B–C, A–B
    s += zig(seg_x[2], gx1, railY, RED, "r")
    s += zig(seg_x[1], seg_x[2], railY, RED, "r")
    s += zig(seg_x[0], seg_x[1], railY, RED, "r")

    # три блоки-споживачі над шиною, кожен веде «землю» у свій вузол
    blocks = [
        (bx + 20,  150, "Цифра", "великий\nімпульсний струм", PURPLE, seg_x[0], "I₁"),
        (bx + 135, 150, "АЦП", "слабкий\nсигнал", GREEN, seg_x[1], "I₂"),
        (bx + 250, 150, "Давач", "мікроампери", BLUE, seg_x[2], "I₃"),
    ]
    bw, bh = 90, 56
    for x, y, lab, sub, col, nx, cur in blocks:
        s += rect(x, y, bw, bh, "#f3f5f8", col, 2, 7)
        s += text(x + bw / 2, y + 22, lab, 12.5, INK, "middle", "bold")
        lines = sub.split("\n")
        for k, ln in enumerate(lines):
            s += text(x + bw / 2, y + 38 + k * 12, ln, 8.8, GREY, "middle")
        # провід «землі» вниз до свого вузла
        s += line(x + bw / 2, y + bh, x + bw / 2, railY - 2, col, 2)
        s += circle(nx, railY, 3.4, col, col, 1)
        # струм униз
        s += text(x + bw / 2 + 6, (y + bh + railY) / 2, cur, 10, col, "start", "bold")

    # ключова ідея: струм цифри тече через r(B-C) і r(C-GND) — спільні з АЦП
    s += text(bx + 200, railY + 58,
              "струм I₁ цифри тече і через ділянки B→C→GND,", 10.3, RED, "middle", "bold")
    s += text(bx + 200, railY + 73,
              "спільні з поверненням АЦП ⇒ «земля» АЦП стрибає", 10.3, RED, "middle", "bold")
    # підсвітити спільний відрізок
    s += line(seg_x[1], railY + 14, gx1, railY + 14, RED, 2, "5,4")
    s += text((seg_x[1] + gx1) / 2, railY + 12, "спільний шлях", 9, RED, "middle", style="italic")

    # формула помилки
    s += rect(bx + 18, 512, 364, 70, "#fff4f2", RED, 1.5, 8)
    s += text(bx + 200, 534, "потенціал «землі» АЦП ≠ 0:", 11, INK, "middle", "bold")
    s += text(bx + 200, 554, "V_земля(B) = (I₁ + I₂)·r_BC + (I₁+I₂+I₃)·r_CG", 11.5, RED, "middle", "bold")
    s += text(bx + 200, 572, "імпульси цифри домішуються до сигналу", 9.6, GREY, "middle", style="italic")

    # ── ПРАВО: ЗІРКА (star / single-point) ──────────────────────────────────
    px = 600
    s += text(px + 200, 92, "ЗІРКА (single-point)", 14.5, GREEN, "middle", "bold")
    s += text(px + 200, 110, "кожне повернення — окремим проводом в одну точку", 10.5, GREY, "middle")

    # центральна точка-зірка
    starX, starY = px + 200, 440
    s += circle(starX, starY, 8, "#eaf6ee", GREEN, 2.5)
    s += text(starX, starY + 32, "точка-зірка", 10.5, GREEN, "middle", "bold")
    s += text(starX, starY + 46, "(єдина «земля» = 0 В)", 9.2, GREY, "middle")
    s += gnd_symbol(starX, starY + 8, INK, 1.1)

    pblocks = [
        (px + 20,  150, "Цифра", PURPLE, "I₁"),
        (px + 135, 150, "АЦП", GREEN, "I₂"),
        (px + 250, 150, "Давач", BLUE, "I₃"),
    ]
    for x, y, lab, col, cur in pblocks:
        s += rect(x, y, bw, bh, "#f3f5f8", col, 2, 7)
        s += text(x + bw / 2, y + 26, lab, 12.5, INK, "middle", "bold")
        s += text(x + bw / 2, y + 43, "своя «земля»", 8.8, GREY, "middle")
        # окремий провід прямо в точку-зірку
        s += arrow(x + bw / 2, y + bh, starX, starY - 9, col, 2)
        # власний опір, але струм НЕ ділиться з іншими
        midx = (x + bw / 2 + starX) / 2
        midy = (y + bh + starY) / 2
        s += text(midx, midy, cur, 10, col, "middle", "bold")

    s += rect(px + 18, 512, 364, 70, "#eefaf1", GREEN, 1.5, 8)
    s += text(px + 200, 534, "кожне V_земля = Iₖ·rₖ — від СВОГО струму:", 11, INK, "middle", "bold")
    s += text(px + 200, 554, "імпульс цифри тече лише по СВОЄМУ проводу", 11, GREEN, "middle", "bold")
    s += text(px + 200, 572, "у «землю» АЦП він не потрапляє", 9.6, GREY, "middle", style="italic")

    # роздільник
    s += line(W / 2, 80, W / 2, 590, FAINT, 2, "6,5")
    return s


# ── Рис. 1.9.6c.2 — практична розводка на макетці ────────────────────────────
def fig_breadboard():
    W, H = 1020, 470
    s = header(W, H)
    s += text(W / 2, 30, "Та сама ідея на макетці: одна шина «−» проти зірки до однієї точки",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52,
              "контакти й перемички мають перехідний опір; де сходяться повернення — там і домішується завада",
              11.5, GREY, "middle", style="italic")

    def board(x0, y0, title, color):
        bw_, bh_ = 380, 250
        s_ = rect(x0, y0, bw_, bh_, "#fbfbf7", "#cfcfc4", 2, 9)
        s_ += text(x0 + bw_ / 2, y0 - 12, title, 14, color, "middle", "bold")
        # шини живлення зверху (+ червона) і знизу («−» синя) — як у §1.4.1c
        return s_, x0, y0, bw_, bh_

    # дві колонки гнізд (спрощено): малюємо рядок крапок для шини «−»
    def rail(x0, x1, y, color, label):
        out = line(x0, y, x1, y, color, 5)
        n = 16
        for i in range(n):
            xx = x0 + (x1 - x0) * (i + 0.5) / n
            out += circle(xx, y, 2.4, "#ffffff", color, 1.3)
        out += text(x0 - 8, y + 4, label, 13, color, "end", "bold")
        return out

    # ── ЛІВО: погано — спільна шина «−» (ланцюжок) ─────────────────────────
    bd, x0, y0, bw_, bh_ = board(60, 110, "ПОГАНО: усе на спільну шину «−»", RED)
    s += bd
    minusY = y0 + bh_ - 30
    plusY = y0 + 30
    s += rail(x0 + 30, x0 + bw_ - 20, plusY, RED, "+")
    s += rail(x0 + 30, x0 + bw_ - 20, minusY, BLUE, "−")
    # точка живлення приходить ліворуч
    s += arrow(x0 - 4, minusY + 40, x0 + 30, minusY, INK, 2)
    s += text(x0 - 10, minusY + 52, "від БЖ «−»", 10, INK, "end", "bold")
    s += arrow(x0 - 4, plusY - 30, x0 + 30, plusY, RED, 2)
    s += text(x0 - 10, plusY - 36, "від БЖ «+»", 10, RED, "end", "bold")

    # три споживачі, всі «землять» у різні точки тієї самої шини
    cons = [
        (x0 + 90,  "Цифра", PURPLE, "I₁ (імпульси)"),
        (x0 + 190, "АЦП", GREEN, "I₂"),
        (x0 + 290, "Давач", BLUE, "I₃"),
    ]
    midY = (plusY + minusY) / 2 - 10
    for cx, lab, col, cur in cons:
        s += rect(cx - 34, midY - 18, 68, 40, "#f3f5f8", col, 1.8, 6)
        s += text(cx, midY + 6, lab, 11, INK, "middle", "bold")
        s += line(cx, midY + 22, cx, minusY - 2, col, 2)   # земля на шину
        s += line(cx, midY - 18, cx, plusY + 2, RED, 1.6, "3,3")  # живлення
    # підсвітити, що між точками шини є опір
    s += text(x0 + bw_ / 2, y0 + bh_ + 26,
              "повернення цифри тече по шині повз точку АЦП ⇒ зсув «землі»",
              10.5, RED, "middle", "bold")
    s += line(x0 + 90, minusY + 9, x0 + 190, minusY + 9, RED, 2, "4,4")
    s += text((x0 + 90 + x0 + 190) / 2, minusY + 7, "r шини", 9, RED, "middle", style="italic")

    # ── ПРАВО: добре — зірка до однієї точки ───────────────────────────────
    bd2, x1, y1, bw2, bh2 = board(580, 110, "ДОБРЕ: зірка до однієї точки «−»", GREEN)
    s += bd2
    plusY2 = y1 + 30
    minusY2 = y1 + bh2 - 30
    s += rail(x1 + 30, x1 + bw2 - 20, plusY2, RED, "+")
    # точка-зірка: одне «жирне» гніздо ближче до входу живлення
    starX, starY = x1 + 60, minusY2
    s += circle(starX, starY, 9, "#eaf6ee", GREEN, 2.6)
    s += text(starX, starY + 22, "точка-зірка", 10, GREEN, "middle", "bold")
    s += arrow(x1 - 4, starY + 40, starX - 9, starY + 4, INK, 2)
    s += text(x1 - 10, starY + 52, "від БЖ «−»", 10, INK, "end", "bold")
    s += arrow(x1 - 4, plusY2 - 30, x1 + 30, plusY2, RED, 2)
    s += text(x1 - 10, plusY2 - 36, "від БЖ «+»", 10, RED, "end", "bold")

    cons2 = [
        (x1 + 150, "Цифра", PURPLE, "I₁"),
        (x1 + 240, "АЦП", GREEN, "I₂"),
        (x1 + 330, "Давач", BLUE, "I₃"),
    ]
    midY2 = (plusY2 + minusY2) / 2 - 10
    for cx, lab, col, cur in cons2:
        s += rect(cx - 34, midY2 - 18, 68, 40, "#f3f5f8", col, 1.8, 6)
        s += text(cx, midY2 + 6, lab, 11, INK, "middle", "bold")
        # окремий провід «землі» прямо в точку-зірку
        s += arrow(cx, midY2 + 22, starX, starY - 9, col, 1.8)
        s += line(cx, midY2 - 18, cx, plusY2 + 2, RED, 1.6, "3,3")
    s += gnd_symbol(starX, starY + 9, INK, 1.0)
    s += text(x1 + bw2 / 2, y1 + bh2 + 26,
              "кожен струм має власний шлях ⇒ «землі» не змішуються",
              10.5, GREEN, "middle", "bold")

    # легенда внизу
    ly = 432
    s += line(120, ly, 150, ly, RED, 1.6, "3,3")
    s += text(156, ly + 4, "живлення «+»", 11, INK, "start")
    s += line(330, ly, 360, ly, INK, 2)
    s += text(366, ly + 4, "провід повернення «−» (землі)", 11, INK, "start")
    s += circle(620, ly, 6, "#eaf6ee", GREEN, 2)
    s += text(634, ly + 4, "спільна точка «землі» (єдиний нуль)", 11, INK, "start")
    return s


if __name__ == "__main__":
    save("fig-r09-s6c-1-star-vs-daisy.svg", fig_topology())
    save("fig-r09-s6c-2-breadboard.svg", fig_breadboard())
    print("done")
