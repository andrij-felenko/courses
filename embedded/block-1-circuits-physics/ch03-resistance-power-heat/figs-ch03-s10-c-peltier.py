# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки §1.3.10c — «Елемент Пельтьє».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена s10c-*).
НЕ чіпає головний figs.py розділу (за §9 — самодостатній скрипт).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; sans-serif.
Нумерація підписів у тексті: Рис. 1.3.10c.k.
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
ORANGE = "#e08030"
COLD = "#3a86c8"
WARM = "#d6552b"
NSEMI = "#3f6fa8"
PSEMI = "#b8472e"
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
        f'  <marker id="aWarm" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{WARM}"/></marker>\n'
        f'  <marker id="aCold" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{COLD}"/></marker>\n'
        f'  <marker id="aN" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{NSEMI}"/></marker>\n'
        f'  <marker id="aP" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PSEMI}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", WARM: "aWarm", COLD: "aCold",
         NSEMI: "aN", PSEMI: "aP"}


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


def plus(cx, cy, r=11, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=11, color=BLUE, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def heatwaves(cx, cy, n=3, color=WARM, up=True, span=26):
    """Хвилясті лінії-тепло (вгору, якщо up=True)."""
    out = ""
    sgn = -1 if up else 1
    h = span
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * 13
        out += (f'<path d="M {x:.1f},{cy:.1f} q 5,{sgn*h*0.27:.1f} 0,{sgn*h*0.5:.1f} '
                f'q -5,{sgn*h*0.27:.1f} 0,{sgn*h*0.5:.1f}" fill="none" '
                f'stroke="{color}" stroke-width="1.8"/>\n')
    return out


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 1.3.10c.1 — один спай: чому струм носить тепло ──────────────────────
def fig_junction():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 32, "Чому струм носить тепло: пара n- і p-стовпчиків", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "носії несуть не лише заряд, а й енергію; на одному спаї вони її забирають, на іншому — віддають",
              12, GREY, "middle", style="italic")

    # Холодна (верхня) і гаряча (нижня) керамічні пластини
    s += rect(150, 96, 520, 26, "#eef4fb", COLD, 2.2, 4)
    s += text(160, 113, "ХОЛОДНА пластина", 13, COLD, "start", "bold")
    s += rect(150, 360, 520, 26, "#fbeee8", WARM, 2.2, 4)
    s += text(160, 377, "ГАРЯЧА пластина", 13, WARM, "start", "bold")

    # Два напівпровідникові стовпчики
    nx, px = 330, 490
    colw, coltop, colbot = 56, 130, 356
    s += rect(nx - colw / 2, coltop, colw, colbot - coltop, "#dbe6f3", NSEMI, 2.4, 4)
    s += text(nx, (coltop + colbot) / 2 - 8, "n", 22, NSEMI, "middle", "bold")
    s += text(nx, (coltop + colbot) / 2 + 14, "(−)", 12, NSEMI, "middle")
    s += rect(px - colw / 2, coltop, colw, colbot - coltop, "#f3dcd4", PSEMI, 2.4, 4)
    s += text(px, (coltop + colbot) / 2 - 8, "p", 22, PSEMI, "middle", "bold")
    s += text(px, (coltop + colbot) / 2 + 14, "(+)", 12, PSEMI, "middle")

    # Мідні перемички: зверху n↔p, знизу до контактів
    s += rect(nx - colw / 2 - 4, 122, (px - nx) + colw + 8, 10, "#cf8b5e", "#9c6038", 1.5, 3)
    s += text((nx + px) / 2, 118, "мідна перемичка (холодний спай)", 11, "#7a4a26", "middle")
    s += rect(nx - colw / 2 - 4, 350, 40, 10, "#cf8b5e", "#9c6038", 1.5, 3)
    s += rect(px - colw / 2 - 36, 350, 40, 10, "#cf8b5e", "#9c6038", 1.5, 3)

    # Зовнішнє джерело струму
    s += line(nx - colw / 2 - 24, 355, nx - colw / 2 - 24, 420, INK, 2.4)
    s += line(px + colw / 2 + 24, 355, px + colw / 2 + 24, 420, INK, 2.4)
    s += line(nx - colw / 2 - 24, 420, px + colw / 2 + 24, 420, INK, 2.4)
    s += plus(px + colw / 2 + 24, 438)
    s += minus(nx - colw / 2 - 24, 438)
    s += text((nx + px) / 2, 414, "джерело постійного струму", 12, INK, "middle", "bold")

    # Напрям струму (умовний) — через коло
    s += arrow(px + colw / 2 + 24, 400, px + colw / 2 + 24, 372, RED, 2.4)
    s += text(px + colw / 2 + 34, 392, "I", 14, RED, "start", "bold")

    # Рух носіїв у стовпчиках (несуть енергію вгору, до холодної пластини)
    s += arrow(nx, 330, nx, 165, NSEMI, 2.6)   # електрони в n рухаються вгору
    s += text(nx - 70, 250, "електрони", 12, NSEMI, "start", "bold")
    s += text(nx - 70, 266, "несуть енергію ↑", 11, NSEMI, "start")
    s += arrow(px, 330, px, 165, PSEMI, 2.6)    # дірки в p теж "вгору" за потоком тепла
    s += text(px + 16, 250, "дірки", 12, PSEMI, "start", "bold")
    s += text(px + 16, 266, "несуть енергію ↑", 11, PSEMI, "start")

    # Тепло забирається зверху (холодний спай охолоджується)
    s += text((nx + px) / 2, 88, "тут тепло ЗАБИРАЄТЬСЯ → холодно", 13, COLD, "middle", "bold")
    s += arrow((nx + px) / 2, 96, (nx + px) / 2, 130, COLD, 2.4)
    s += heatwaves((nx + px) / 2, 86, 3, COLD, up=True, span=22)

    # Тепло віддається знизу (гарячий спай гріється) + Джоуль
    s += heatwaves(255, 396, 3, WARM, up=False, span=22)
    s += heatwaves(565, 396, 3, WARM, up=False, span=22)
    s += text(255, 348, "тепло ВІДДАЄТЬСЯ", 11, WARM, "middle", "bold")
    s += text(565, 348, "+ нагрів I²R", 11, WARM, "middle", "bold")

    # Підсумковий баланс праворуч
    s += rect(688, 150, 120, 180, "#fbfbf4", "#c9c178", 1.6, 6)
    s += text(748, 172, "Баланс", 12, INK, "middle", "bold")
    s += text(696, 196, "холодна:", 11, COLD, "start", "bold")
    s += text(700, 212, "Qc = α·I·T", 11, INK, "start")
    s += text(700, 228, "  − ½I²R − …", 11, GREY, "start")
    s += text(696, 252, "гаряча:", 11, WARM, "start", "bold")
    s += text(700, 268, "Qh = Qc", 11, INK, "start")
    s += text(700, 284, "  + I²R", 11, INK, "start")
    s += text(696, 312, "споживає", 11, RED, "start", "bold")
    s += text(700, 328, "P = V·I", 11, INK, "start")

    save("s10c-1-junction.svg", s)


# ── Рис. 1.3.10c.2 — модуль TEC: стос і тепловий шлях ────────────────────────
def fig_module():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 32, "Модуль Пельтьє (TEC): десятки пар між двома пластинами", 20, INK, "middle", "bold")
    s += text(W / 2, 54, "увесь фокус — у тепловому шляху: гарячий бік МУСИТЬ мати радіатор, інакше модуль зварить сам себе",
              12, GREY, "middle", style="italic")

    cx = 300
    # Холодна пластина (верх)
    s += rect(cx - 150, 110, 300, 24, "#e7f0fb", COLD, 2.2, 4)
    s += text(cx, 127, "холодна кераміка", 12, COLD, "middle", "bold")
    # Масив n/p стовпчиків між пластинами
    y0, y1 = 134, 250
    n_pairs = 6
    x = cx - 132
    step = 264 / (n_pairs * 2)
    for i in range(n_pairs * 2):
        col = NSEMI if i % 2 == 0 else PSEMI
        fillc = "#dbe6f3" if i % 2 == 0 else "#f3dcd4"
        s += rect(x, y0, step * 0.62, y1 - y0, fillc, col, 1.6, 2)
        x += step
    # внутрішні мідні перемички (схематично: зверху й знизу зиґзаґ)
    s += text(cx, (y0 + y1) / 2 + 5, "n  p  n  p  …  (послідовно)", 12, INK, "middle", "bold")
    # Гаряча пластина (низ)
    s += rect(cx - 150, 250, 300, 24, "#fbe9e1", WARM, 2.2, 4)
    s += text(cx, 267, "гаряча кераміка", 12, WARM, "middle", "bold")

    # Термопаста + радіатор знизу (тепловий шлях, §1.3.9)
    s += rect(cx - 150, 274, 300, 7, "#cccccc", "#9a9a9a", 1.2, 1)
    s += text(cx + 158, 281, "термопаста", 10, GREY, "start")
    # ребра радіатора
    base_y = 281
    s += rect(cx - 150, base_y, 300, 12, "#d8d8d8", "#8f8f8f", 1.4, 2)
    for k in range(11):
        fx = cx - 144 + k * 27
        s += rect(fx, base_y + 12, 9, 58, "#e2e2e2", "#9a9a9a", 1.0, 1)
    s += text(cx, base_y + 88, "РАДІАТОР на гарячому боці (обов'язково!)", 12, INK, "middle", "bold")

    # Холод зверху
    s += text(cx, 96, "холодний бік: сюди тулять об'єкт, який охолоджують", 12, COLD, "middle", "bold")
    s += heatwaves(cx - 90, 110, 3, COLD, up=True, span=20)
    s += arrow(cx, 110, cx, 88, COLD, 2.2)
    s += heatwaves(cx + 90, 110, 3, COLD, up=True, span=20)

    # Два дроти живлення
    s += line(cx - 150, 262, cx - 196, 262, RED, 2.4)
    s += line(cx + 150, 262, cx + 196, 262, INK, 2.4)
    s += text(cx - 200, 252, "червоний", 10, RED, "middle")
    s += text(cx + 200, 252, "чорний", 10, INK, "middle")

    # Права колонка: правила підключення й попередження
    bx = 500
    s += rect(bx, 92, 308, 360, "#fbfbf4", "#c9c178", 1.6, 8)
    s += text(bx + 154, 116, "Як вмикати й де граблі", 14, INK, "middle", "bold")

    rows = [
        (RED, "Живлення — ЧИСТА постійна напруга", ""),
        (INK, "(скажімо, з лінійного БЖ), а не PWM —", "GREY"),
        (INK, "інакше I²R-нагрів зростає, ефект падає.", "GREY"),
        (WARM, "Гарячий бік — на радіатор з обдувом.", ""),
        (INK, "Без відводу тепла ΔT не тримається,", "GREY"),
        (INK, "обидва боки гріються — модуль гине.", "GREY"),
        (COLD, "Полярність задає напрям: поміняв", ""),
        (INK, "дроти — холодний і гарячий міняються.", "GREY"),
        (BLUE, "Конденсат на холодному боці —", ""),
        (INK, "волога з повітря; ізолюй від плати.", "GREY"),
        (RED, "ККД низький: качаєш Qc, а в мережу", ""),
        (INK, "віддаєш Qc + уся спожита P = V·I.", "GREY"),
    ]
    yy = 142
    for col, t, mode in rows:
        c = GREY if mode == "GREY" else col
        wt = "normal" if mode == "GREY" else "bold"
        bullet = ""
        if mode != "GREY":
            s += circle(bx + 18, yy - 4, 3.4, col, col, 1)
        s += text(bx + 30, yy, t, 11.5, c, "start", wt)
        yy += 25

    save("s10c-2-module.svg", s)


if __name__ == "__main__":
    fig_junction()
    fig_module()
    print("done")
