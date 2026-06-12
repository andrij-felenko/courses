# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки §1.7.2c — «Генератор сигналів».
Чистий Python, без залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами (fig-7-2c-*).
НЕ чіпає головний figs.py розділу.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Нумерація підписів у тексті: Рис. 1.7.2c.k.
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
ORANGE = "#e08030"
PURPLE = "#7a4fb0"
FONT = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREEN: "aGreen", ORANGE: "aOrange"}


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


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── маленькі іконки форм у рамці (вписані в прямокутник x,y,w,h) ───────────────
def _sine_icon(x, y, w, h, color=INK, lw=2.6, cycles=1.0):
    pts = []
    n = 60
    for i in range(n + 1):
        t = i / n
        px = x + t * w
        py = y + h / 2 - (h / 2 - 2) * math.sin(2 * math.pi * cycles * t)
        pts.append((px, py))
    return polyline(pts, color, lw)


def _square_icon(x, y, w, h, color=INK, lw=2.6):
    top = y + 2
    bot = y + h - 2
    mid = y + h / 2  # умовно для повноти, не використовується
    x0, x1, x2, x3, x4 = x, x + w * 0.25, x + w * 0.5, x + w * 0.75, x + w
    pts = [(x0, bot), (x0, top), (x1, top), (x1, bot),
           (x2, bot), (x2, top), (x3, top), (x3, bot), (x4, bot)]
    return polyline(pts, color, lw)


def _tri_icon(x, y, w, h, color=INK, lw=2.6):
    top = y + 2
    bot = y + h - 2
    pts = [(x, bot), (x + w * 0.25, top), (x + w * 0.5, bot),
           (x + w * 0.75, top), (x + w, bot)]
    return polyline(pts, color, lw)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 1.7.2c.1 — будова генератора сигналів: ядро → форма → амплітуда → вихід
# ════════════════════════════════════════════════════════════════════════════
def fig_function_generator():
    W, H = 940, 540
    s = header(W, H)
    s += text(W / 2, 30, "Генератор сигналів: від цифрового ядра до сигналу на BNC",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "форму, частоту й амплітуду задають незалежно — і будь-яку видають «на вимогу»",
              12, GREY, "middle", style="italic")

    # ── ланцюг блоків (верхній ряд) ──────────────────────────────────────────
    by = 92
    bh = 78
    boxes = [
        (40, "Опорний\nтакт", "кварц (§1.7.1)\nстабільна f₀", "#eef2fb", BLUE),
        (210, "Фазовий\nакумулятор", "лічить фазу\n0 → 2π → 0", "#eef2fb", BLUE),
        (385, "Таблиця\nформи (ROM)", "фаза → відлік\nsin / ▢ / △", "#fdf0e6", ORANGE),
        (560, "ЦАП\n(DAC)", "число →\nнапруга", "#fdf0e6", ORANGE),
        (730, "Підсилювач\n+ атенюатор", "амплітуда,\nзсув, 50 Ω", "#eaf6ee", GREEN),
    ]
    bw = 150
    centers = []
    for (x, title, sub, fill, stroke) in boxes:
        s += rect(x, by, bw, bh, fill, stroke, 2.2, 10)
        tlines = title.split("\n")
        ty = by + 26 if len(tlines) == 2 else by + 32
        for i, ln in enumerate(tlines):
            s += text(x + bw / 2, ty + i * 18, ln, 14.5, INK, "middle", "bold")
        slines = sub.split("\n")
        syy = by + bh - 22
        for i, ln in enumerate(slines):
            s += text(x + bw / 2, syy + i * 14, ln, 11, GREY, "middle")
        centers.append((x, x + bw))

    # стрілки між блоками
    for i in range(len(centers) - 1):
        x1 = centers[i][1]
        x2 = centers[i + 1][0]
        s += arrow(x1 + 3, by + bh / 2, x2 - 3, by + bh / 2, INK, 2.4)

    # вихід BNC праворуч
    bnc_x = centers[-1][1] + 18
    s += arrow(bnc_x - 15, by + bh / 2, bnc_x + 18, by + bh / 2, GREEN, 2.6)
    s += circle(bnc_x + 30, by + bh / 2, 12, "#fff", GREEN, 2.6)
    s += circle(bnc_x + 30, by + bh / 2, 4, GREEN, GREEN, 1)
    s += text(bnc_x + 30, by + bh + 22, "вихід", 11.5, GREEN, "middle", "bold")
    s += text(bnc_x + 30, by + bh + 37, "BNC", 11, GREY, "middle")

    # пояснення «три незалежні ручки»
    s += text(295, by + bh + 30, "ЧАСТОТА", 11.5, BLUE, "middle", "bold")
    s += text(295, by + bh + 44, "(крок акумулятора)", 10, GREY, "middle")
    s += text(472, by + bh + 30, "ФОРМА", 11.5, ORANGE, "middle", "bold")
    s += text(472, by + bh + 44, "(яку таблицю читати)", 10, GREY, "middle")
    s += text(730 + bw / 2, by + bh + 30, "АМПЛІТУДА", 11.5, GREEN, "middle", "bold")

    # ── три форми (нижній ряд): осцилограми, що видає прилад ──────────────────
    fy = 300
    fh = 170
    panels = [
        (60, "Синус (sine)", "плавна хвиля §1.7.1", RED, "sine"),
        (350, "Меандр (square)", "різкі фронти, шпаруватість", BLUE, "square"),
        (640, "Трикутник (triangle)", "лінійні наростання й спад", PURPLE, "tri"),
    ]
    pw = 240
    for (x, title, sub, color, kind) in panels:
        s += rect(x, fy, pw, fh, "#ffffff", FAINT, 1.6, 10)
        s += text(x + pw / 2, fy - 10, title, 14.5, color, "middle", "bold")
        # осі
        axw = pw - 40
        axx = x + 24
        ax_mid = fy + fh / 2
        s += line(axx, ax_mid, axx + axw, ax_mid, GREY, 1.3)        # вісь часу
        s += line(axx, fy + 18, axx, fy + fh - 18, GREY, 1.3)        # вісь V
        s += text(axx + axw + 2, ax_mid + 4, "t", 11, GREY, "start", "bold", "italic")
        s += text(axx - 8, fy + 22, "V", 11, GREY, "end", "bold", "italic")
        amp = fh / 2 - 26
        n = 220
        pts = []
        cycles = 2.0
        for i in range(n + 1):
            t = i / n
            px = axx + t * axw
            ph = 2 * math.pi * cycles * t
            if kind == "sine":
                val = math.sin(ph)
            elif kind == "square":
                val = 1.0 if (math.sin(ph) >= 0) else -1.0
            else:  # triangle
                frac = (cycles * t) % 1.0
                if frac < 0.25:
                    val = frac / 0.25
                elif frac < 0.75:
                    val = 1 - (frac - 0.25) / 0.25
                else:
                    val = -1 + (frac - 0.75) / 0.25
            py = ax_mid - amp * val
            pts.append((px, py))
        s += polyline(pts, color, 2.8)
        s += text(x + pw / 2, fy + fh + 22, sub, 11, GREY, "middle")

    # підпис-зв'язка під формами
    s += text(W / 2, H - 14,
              "Одне ядро, три таблиці форми — і той самий прилад на вимогу видає будь-яку з цих хвиль із заданими f і Vₘ",
              12, INK, "middle", style="italic")
    return s


if __name__ == "__main__":
    save("fig-7-2c-1-function-generator.svg", fig_function_generator())
    print("done.")
