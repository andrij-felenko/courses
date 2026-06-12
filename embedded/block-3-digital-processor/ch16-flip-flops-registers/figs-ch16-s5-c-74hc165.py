# -*- coding: utf-8 -*-
"""
SVG-фігури для 🔌-вставки §3.3.5c — «74HC165: вісім кнопок в одну ніжку».
Окремий генератор (головний figs.py не чіпаємо), чистий Python без залежностей.
Вивід → ./img/. Стиль за AUTHORING §9: білий фон; «1» червоний, «0» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.

Фігури:
  fig-16-5c-1-concept.svg   — вісім входів (кнопок) → 8 тригерів → один послідовний дріт
  fig-16-5c-2-wiring.svg    — розпіновка DIP-16 і підключення до МК (+ каскад)
  fig-16-5c-3-firstbyte.svg — «перший байт»: імпульс PL (load) і 8 фронтів CLK, біти виходять Q7→Q0
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: маленька кнопка (момент-вимикач) ──────────────────────────────
def button(cx, cy, pressed, label):
    """Схематична кнопка: коло-штовхач + підпис стану під нею."""
    out = circle(cx, cy, 11, "#fff", INK, 2)
    out += line(cx - 6, cy, cx + 6, cy, INK, 2)          # контактна планка
    if pressed:
        out += line(cx, cy - 7, cx, cy, RED, 2.4)         # натиснутий шток
        out += text(cx, cy + 26, "1", 14, RED, "middle", "bold")
    else:
        out += line(cx, cy - 10, cx, cy - 3, GREY, 2)     # відпущений шток
        out += text(cx, cy + 26, "0", 14, BLUE, "middle", "bold")
    out += text(cx, cy - 18, label, 11, GREY, "middle")
    return out


# ── Фігура 1: концепція PISO — 8 кнопок → 8 тригерів → один дріт ─────────────
def fig1_concept():
    W, H = 760, 470
    b = header(W, H)
    b += text(W/2, 30, "74HC165: вісім незалежних входів — один послідовний вихід",
              17, INK, "middle", "bold")

    # вісім кнопок угорі, по одній на біт D7..D0
    bits = [1, 0, 1, 1, 0, 0, 1, 0]               # приклад: байт 0b10110010
    names = ["D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0"]
    x0, dx = 95, 82
    by = 92
    for i, (v, nm) in enumerate(zip(bits, names)):
        cx = x0 + i * dx
        b += button(cx, by, v, nm)
        # дріт від кнопки вниз до «засувки»
        b += arrow(cx, by + 30, cx, 165, INK, 1.8)

    # корпус: банк із восьми D-тригерів (PISO-ядро)
    rx, ry, rw, rh = 60, 168, 640, 92
    b += rect(rx, ry, rw, rh, "#f4f7ff", BLUE, 2, 10)
    b += text(W/2, ry - 8, "вісім тригерів в одному корпусі (паралельне завантаження → послідовний зсув)",
              13, BLUE, "middle", style="italic")
    # вісім комірок-тригерів усередині
    for i, v in enumerate(bits):
        cx = x0 + i * dx
        col = RED if v else BLUE
        b += rect(cx - 22, ry + 18, 44, 56, "#fff", col, 2, 6)
        b += text(cx, ry + 52, str(v), 22, col, "middle", "bold")
    # стрілки зсуву між комірками (ланцюжок праворуч → до виходу)
    for i in range(7):
        cxa = x0 + i * dx + 22
        cxb = x0 + (i + 1) * dx - 22
        b += arrow(cxb, ry + 46, cxa, ry + 46, GREY, 1.6)   # зсув ←: біт їде до D0/QH
    b += text(rx + rw/2, ry + 88, "кожен фронт CLK зсуває весь рядок на один щабель →",
              11, GREY, "middle")

    # один-єдиний вихідний дріт до МК
    qy = 330
    b += arrow(x0 - 22, ry + 46, 40, qy, BLUE, 2.2)
    b += text(40, qy + 18, "QH", 14, BLUE, "start", "bold")
    b += text(40, qy + 38, "(один дріт)", 12, GREY, "start")
    b += arrow(70, qy + 30, 250, qy + 30, GREEN, 2.4)
    # потік бітів у часі на цьому дроті
    seq = bits  # послідовно виходить той самий байт
    sx = 270
    for i, v in enumerate(seq):
        col = RED if v else BLUE
        b += rect(sx + i * 40, qy + 12, 34, 34, "#fff", col, 2, 5)
        b += text(sx + i * 40 + 17, qy + 36, str(v), 18, col, "middle", "bold")
    b += text(sx + 8 * 40 + 8, qy + 36, "→ час", 12, GREY, "start")
    b += text(sx + 160, qy - 4, "ті самі 8 бітів, але по черзі в часі", 12, GREEN, "middle", style="italic")

    # підсумковий рядок-висновок
    b += text(W/2, 412, "8 ніжок входу → 1 ніжка виходу: економія виводів МК у вісім разів",
              14, GREEN, "middle", "bold")
    b += text(W/2, 438, "(а каскад із кількох таких чипів — у 16, 24, 32… на тих самих трьох лініях)",
              12, GREY, "middle")
    save("fig-16-5c-1-concept.svg", b)


# ── Фігура 2: розпіновка DIP-16 і підключення до МК (+ каскад) ───────────────
def fig2_wiring():
    W, H = 770, 520
    b = header(W, H)
    b += text(W/2, 30, "Розпіновка (DIP-16) і підключення трьох ліній до МК",
              17, INK, "middle", "bold")

    # корпус мікросхеми
    cx, cy, cw, ch = 250, 70, 130, 360
    b += rect(cx, cy, cw, ch, "#fbfbfb", INK, 2, 8)
    b += circle(cx + cw/2, cy + 14, 7, "#fff", INK, 1.6)          # ключ-виїмка
    b += text(cx + cw/2, cy + 40, "74HC165", 15, INK, "middle", "bold")
    b += text(cx + cw/2, cy + 58, "8-біт PISO", 11, GREY, "middle")

    left  = [("QH", "вихід (інверсний)"), ("D7", "вхід"), ("D6", "вхід"),
             ("D5", "вхід"), ("D4", "вхід"), ("CLK INH", "стоп-такт"),
             ("CLK", "такт"), ("GND", "земля")]
    right = [("VCC", "живлення"), ("D0", "вхід"), ("D1", "вхід"), ("D2", "вхід"),
             ("D3", "вхід"), ("PL", "паралельне\nзавантаження"),
             ("SER", "вхід каскаду"), ("QH'", "вихід (прямий)")]

    n = 8
    pitch = (ch - 40) / (n - 1)
    py0 = cy + 30
    # ліві ніжки 1..8
    for i, (nm, role) in enumerate(left):
        y = py0 + i * pitch
        b += line(cx - 26, y, cx, y, INK, 2)
        b += circle(cx - 26, y, 3, INK, INK, 1)
        col = GREEN if nm in ("CLK",) else (BLUE if "вхід" in role else INK)
        b += text(cx - 32, y - 4, f"{i+1}", 10, GREY, "end")
        b += text(cx + 6, y + 4, nm, 12, col, "start", "bold")
        b += text(cx - 34, y + 9, role.split(" ")[0], 9, GREY, "end")
    # праві ніжки 16..9
    for i, (nm, role) in enumerate(right):
        y = py0 + i * pitch
        b += line(cx + cw, y, cx + cw + 26, y, INK, 2)
        b += circle(cx + cw + 26, y, 3, INK, INK, 1)
        col = GREEN if nm in ("PL", "SER", "QH'") else (BLUE if "вхід" in role else INK)
        b += text(cx + cw + 32, y - 4, f"{16-i}", 10, GREY, "start")
        b += text(cx + cw - 6, y + 4, nm, 12, col, "end", "bold")

    # МК зліва, три керівні лінії (опущено нижче, щоб лінії не перетинали входи)
    mx, my, mw, mh = 44, 250, 96, 120
    b += rect(mx, my, mw, mh, "#eef7ee", GREEN, 2, 8)
    b += text(mx + mw/2, my + 24, "МК", 15, GREEN, "middle", "bold")
    b += text(mx + mw/2, my + 42, "(SPI-хост)", 10, GREY, "middle")
    b += text(mx + mw/2, my + 66, "QH  ←", 11, BLUE, "middle")
    b += text(mx + mw/2, my + 86, "CLK →", 11, GREEN, "middle")
    b += text(mx + mw/2, my + 106, "PL  →", 11, GREEN, "middle")

    # три лінії від МК до чипа (QH, CLK, PL) — кожна до своєї ніжки, без перетинів
    yQH  = py0 + 0 * pitch        # QH  — ліва ніжка 1 (index 0)
    yCLK = py0 + 6 * pitch        # CLK — ліва ніжка 7 (index 6)
    yPL  = py0 + 5 * pitch        # PL  — права ніжка 11
    # QH назад у МК (ліворуч угору): з ніжки 1 по лівому полю вниз до МК
    b += polyline([(cx - 26, yQH), (mx + mw/2, yQH), (mx + mw/2, my)], BLUE, 2)
    b += arrow(mx + mw/2, my - 2, mx + mw/2, my, BLUE, 2)
    b += text(mx + mw/2, yQH - 8, "QH: біти приходять по черзі →", 11, BLUE, "middle")
    # CLK: горизонтально від МК до лівої ніжки 7
    b += arrow(mx + mw, my + 86, cx - 26, yCLK, GREEN, 2)
    b += text((mx + mw + cx) / 2, yCLK + 18, "CLK: 8 фронтів — висуваємо байт", 11, GREEN, "middle")
    # PL: від МК вниз і праворуч під корпусом до правої ніжки 11
    b += polyline([(mx + mw, my + 106), (cx + cw + 70, my + 106),
                   (cx + cw + 70, yPL), (cx + cw + 26, yPL)], GREEN, 2)
    b += arrow(cx + cw + 30, yPL, cx + cw + 26, yPL, GREEN, 2)
    b += text(cx + cw + 74, yPL - 6, "PL: «клац — захопи всі 8 входів»", 11, GREEN, "start")

    # живлення/земля
    b += text(cx + cw + 32, py0 - 4 + 0 * pitch, "→ +VCC (з C 0.1 µF)", 10, RED, "start")
    b += text(cx - 34, py0 + 7 * pitch + 22, "GND", 10, BLUE, "end")

    # каскад: QH' одного → SER наступного
    b += rect(560, 300, 165, 130, "#fff7ec", AMBER, 2, 8)
    b += text(642, 322, "Каскад", 13, AMBER, "middle", "bold")
    b += text(642, 344, "QH' (ніжка 9) одного чипа", 10, INK, "middle")
    b += text(642, 360, "→ SER (ніжка 10) наступного.", 10, INK, "middle")
    b += text(642, 382, "PL і CLK — спільні для всіх.", 10, GREEN, "middle")
    b += text(642, 404, "Так у ланцюг стають", 10, GREY, "middle")
    b += text(642, 420, "16, 24, 32… біти.", 10, GREY, "middle")
    # стрілка від ніжки QH' (9) до коробки каскаду (амбер, без чорного наконечника)
    b += line(cx + cw + 26, py0 + 7 * pitch, 560, 360, AMBER, 1.8, "5,4")

    b += text(W/2, 500, "Три дроти (PL, CLK, QH) — і неважливо, скільки чипів у ланцюзі та скільки кнопок",
              13, GREEN, "middle", "bold")
    save("fig-16-5c-2-wiring.svg", b)


# ── Фігура 3: «перший байт» — імпульс PL і 8 фронтів CLK, біти Q7..Q0 ────────
def fig3_firstbyte():
    W, H = 780, 470
    b = header(W, H)
    b += text(W/2, 30, "«Перший байт»: один імпульс PL, далі 8 фронтів CLK",
              17, INK, "middle", "bold")

    # часова сітка
    x0, x1 = 150, 720
    span = x1 - x0
    nclk = 8
    # позиції фронтів CLK
    edges = [x0 + 60 + i * ((span - 80) / nclk) for i in range(nclk)]

    def track(y, label, sub):
        b_ = text(x0 - 12, y + 5, label, 13, INK, "end", "bold")
        b_ += text(x0 - 12, y + 22, sub, 9, GREY, "end")
        b_ += line(x0, y - 24, x0, y + 24, FAINT, 1)
        return b_

    # — PL (active-low): низький короткий імпульс на старті, потім високий
    yPL = 90
    b += track(yPL, "PL", "(акт. низ.)")
    plx = x0 + 18
    b += polyline([(x0, yPL - 18), (plx, yPL - 18), (plx, yPL + 14),
                   (plx + 26, yPL + 14), (plx + 26, yPL - 18), (x1, yPL - 18)], GREEN, 2.4)
    b += text(plx + 13, yPL + 32, "захоплення", 10, GREEN, "middle")
    b += text((plx + 26 + edges[0]) / 2, yPL - 26, "далі PL=1: зсув дозволено", 10, GREY, "middle")

    # — CLK: 8 імпульсів після PL
    yCLK = 175
    b += track(yCLK, "CLK", "(8 фронтів)")
    pts = [(x0, yCLK + 16)]
    cur = x0
    pulse_w = 18
    for i, ex in enumerate(edges):
        pts += [(ex, yCLK + 16), (ex, yCLK - 16), (ex + pulse_w, yCLK - 16), (ex + pulse_w, yCLK + 16)]
        b += text(ex + pulse_w/2, yCLK + 34, f"{i+1}", 10, GREY, "middle")
        # позначка фронту-зчитування
        b += circle(ex, yCLK - 16, 3, GREEN, GREEN, 1)
    pts += [(x1, yCLK + 16)]
    b += polyline(pts, INK, 2.2)
    b += text(x1, yCLK - 24, "↑ — фронт", 10, GREEN, "end")

    # — QH: на кожному фронті виходить наступний біт, старший першим
    yQH = 270
    b += track(yQH, "QH", "(вихід)")
    byte = [1, 0, 1, 1, 0, 0, 1, 0]   # D7..D0, той самий приклад, що у фіг.1
    labels = ["D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0"]
    seg_w = (span - 80) / nclk
    prev = yQH + 16
    qpts = [(x0, prev)]                       # початковий «спокій» до першого фронту
    for i, (v, ex) in enumerate(zip(byte, edges)):
        lvl = yQH - 16 if v else yQH + 16
        col = RED if v else BLUE
        x_end = ex + seg_w if i < nclk - 1 else x1
        if lvl != prev:                        # вертикальний перехід лише коли рівень змінився
            qpts.append((ex, prev))
            qpts.append((ex, lvl))
        qpts.append((x_end, lvl))              # горизонтальна полиця біта
        prev = lvl
        mid = (ex + min(x_end, ex + seg_w)) / 2
        b += text(mid, yQH + (40 if not v else -24), labels[i], 10, col, "middle", "bold")
        b += text(mid, yQH + (54 if not v else -38), str(v), 11, col, "middle", "bold")
    b += polyline(qpts, INK, 2.4)
    # стрілка «старший біт першим»
    b += arrow(edges[0], yQH - 40, edges[0], yQH - 20, RED, 1.8)
    b += text(edges[0], yQH - 46, "старший біт першим (D7)", 10, RED, "middle")

    # підпис «прочитаний байт»
    b += text(W/2, 360, "МК зсунув 8 разів — у нього в зсувному регістрі зібрався байт 10110010",
              13, GREEN, "middle", "bold")
    # відповідність зчитаного значення
    b += text(W/2, 384, "(D7…D0) = 1 0 1 1 0 0 1 0  →  0xB2", 13, INK, "middle")

    # ключова думка
    b += text(W/2, 420, "Рецепт незмінний: імпульс PL «сфотографував» входи, 8 тактів їх «висунули».",
              12, GREY, "middle", style="italic")
    b += text(W/2, 440, "Саме так одна ніжка QH віддає весь стан восьми кнопок.",
              12, GREY, "middle", style="italic")
    save("fig-16-5c-3-firstbyte.svg", b)


if __name__ == "__main__":
    fig1_concept()
    fig2_wiring()
    fig3_firstbyte()
    print("ch16-s5-c-74hc165 figures done.")
