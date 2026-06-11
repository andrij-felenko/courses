# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для КОМПОНЕНТНОЇ вставки до теми 1.9.3 —
«Шумлять і резистори: вуглецеві проти металоплівкових» (Модуль 1, Розділ 1.9).
Чистий Python, без залежностей. Вивід → ./img/ (УНІКАЛЬНІ імена з префіксом
fig-r09-s3c-…; головний figs.py розділу й історичний скрипт не чіпаємо).
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з figs.py розділу (за §9 — кожен скрипт самодостатній).
Нумерація: вставка до теми 1.9.3 → Рис. 1.9.3c.N.
"""
import os
import math
import random

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
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", ORANGE: "aOrange", PURPLE: "aPurple"}


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


# ════════════════════════════════════════════════════════════════════════════
#  Вставка до теми 1.9.3 — шум резисторів.  Рис. 1.9.3c.N
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 1.9.3c.1 — звідки надлишковий шум: будова трьох типів резисторів ──────
def fig_construction():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 30, "Звідки в резисторі «зайвий» шум: будова резистивного шару",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "тепловий шум однаковий у всіх; надлишковий 1/f-шум народжує сам матеріал, коли крізь нього тече струм",
              11.3, GREY, "middle", style="italic")

    # три панелі
    panels = [
        (40, COPPER, "Вуглецева композиція", "(carbon composition)",
         "багато", RED, "Струм скаче від зернини до зернини через тисячі\nмікроконтактів — кожен «мерехтить»"),
        (366, ORANGE, "Вуглецева плівка", "(carbon film)",
         "помітно", ORANGE, "Тонка спіральна доріжка вуглецю; контактів менше,\nале матеріал ще зернистий"),
        (692, GREEN, "Металоплівка / фольга", "(metal film)",
         "майже нема", GREEN, "Суцільна металева плівка — носії течуть рівно,\nмайже без «мерехтливих» бар'єрів"),
    ]
    px_w = 268
    for px, bodycol, title, eng, lvl, lvlcol, note in panels:
        s += rect(px, 76, px_w, 360, "#fafafa", GREY, 1.6, 12)
        s += text(px + px_w / 2, 100, title, 13.5, INK, "middle", "bold")
        s += text(px + px_w / 2, 117, eng, 10.5, GREY, "middle", style="italic")

        # корпус резистора з виводами
        cy = 178
        cx0 = px + 38
        cw = px_w - 76
        # виводи
        s += line(px + 14, cy, cx0, cy, INK, 3)
        s += line(cx0 + cw, cy, px + px_w - 14, cy, INK, 3)
        s += rect(cx0, cy - 26, cw, 52, "#ffffff", INK, 2, 8)

        if title.startswith("Вуглецева композиція"):
            # зернини всередині + хаотичний шлях струму
            random.seed(7)
            grains = []
            for _ in range(46):
                gx = cx0 + 8 + random.random() * (cw - 16)
                gy = cy - 18 + random.random() * 36
                gr = 2.6 + random.random() * 2.6
                grains.append((gx, gy, gr))
                s += circle(gx, gy, gr, bodycol, "#8a5a36", 0.8)
            # звивистий шлях струму крізь зернини
            path = [(cx0 + 2, cy)]
            xs = sorted(grains, key=lambda g: g[0])
            step = xs[::4]
            for gx, gy, _ in step:
                path.append((gx, gy))
            path.append((cx0 + cw - 2, cy))
            s += polyline(path, RED, 2.2)
            # підсвітити «мерехтливі» контакти
            for gx, gy, _ in step[1:4]:
                s += circle(gx, gy, 6.5, "none", RED, 1.4)
        elif title.startswith("Вуглецева плівка"):
            # спіральна доріжка
            n = 9
            seg = cw / (n + 1)
            pts = []
            for i in range(n):
                xx = cx0 + 6 + i * seg
                pts.append((xx, cy - 16 if i % 2 == 0 else cy + 16))
            # намалювати зигзаг-спіраль
            s += rect(cx0 + 4, cy - 20, cw - 8, 40, bodycol + "", "none", 0)
            zig = [(cx0 + 4, cy)]
            for i, (xx, yy) in enumerate(pts):
                zig.append((xx, yy))
            zig.append((cx0 + cw - 4, cy))
            s += polyline(zig, "#9a5a20", 5.5)
            s += polyline(zig, RED, 2.0)
            # дрібна зернистість крапками
            random.seed(3)
            for _ in range(40):
                gx = cx0 + 8 + random.random() * (cw - 16)
                gy = cy - 16 + random.random() * 32
                s += circle(gx, gy, 1.2, "#7a4010", "none", 0)
        else:
            # суцільна рівна плівка + прямий потік
            s += rect(cx0 + 4, cy - 18, cw - 8, 36, "#d9e8df", GREEN, 1.2, 4)
            # рівні лінії струму
            for dy in (-9, 0, 9):
                s += arrow(cx0 + 8, cy + dy, cx0 + cw - 8, cy + dy, GREEN, 1.8)

        # рядок «зайвого шуму»
        s += text(px + px_w / 2, 244, "надлишковий шум:", 11, INK, "middle")
        s += text(px + px_w / 2, 264, lvl, 16, lvlcol, "middle", "bold")

        # пояснення
        yy = 296
        for ln in note.split("\n"):
            s += text(px + px_w / 2, yy, ln, 10.2, GREY, "middle")
            yy += 15

        # індикатор-«шумова доріжка» внизу панелі
        random.seed(hash(title) & 0xffff)
        base_y, amp = 392, {"багато": 16, "помітно": 8.5, "майже нема": 2.5}[lvl]
        tx0, tw = px + 24, px_w - 48
        wave = []
        for i in range(int(tw)):
            xx = tx0 + i
            yy = base_y + (random.random() - 0.5) * 2 * amp
            wave.append((xx, yy))
        s += line(tx0 - 6, base_y, tx0 + tw + 6, base_y, FAINT, 1)
        s += polyline(wave, lvlcol, 1.3)
        s += text(px + px_w / 2, 424, "сигнал шуму на виводах (та сама смуга)", 9.4, GREY, "middle", style="italic")

    save("fig-r09-s3c-1-construction.svg", s)


# ── Рис. 1.9.3c.2 — спектр: тепловий поріг + надлишковий 1/f та кутова частота ─
def fig_spectrum():
    W, H = 1000, 470
    s = header(W, H)
    s += text(W / 2, 30, "Спектр шуму резистора: тепловий поріг + надлишкова «гірка» 1/f",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "тепловий шум (§1.9.2) — рівна підлога; надлишковий шум росте на низьких частотах і залежить від типу резистора",
              11.0, GREY, "middle", style="italic")

    # осі (log–log, схематично)
    ox, oy = 120, 386
    ow, oh = 760, 286
    s += line(ox, oy, ox + ow, oy, INK, 2)          # вісь X
    s += line(ox, oy, ox, oy - oh, INK, 2)          # вісь Y
    s += polygon([(ox + ow, oy), (ox + ow - 12, oy - 5), (ox + ow - 12, oy + 5)], INK)
    s += polygon([(ox, oy - oh), (ox - 5, oy - oh + 12), (ox + 5, oy - oh + 12)], INK)
    s += text(ox + ow - 4, oy + 32, "частота f  (лог)", 12.5, INK, "end", "bold")
    s += text(ox - 12, oy - oh + 4, "густина шуму", 12.5, INK, "end", "bold")
    s += text(ox - 12, oy - oh + 20, "нВ/√Гц (лог)", 11, GREY, "end")

    # позначки частот на осі X
    fmarks = [(0.04, "0.1 Гц"), (0.235, "1 Гц"), (0.43, "10 Гц"),
              (0.625, "100 Гц"), (0.82, "1 кГц")]
    for frac, lab in fmarks:
        xx = ox + ow * frac
        s += line(xx, oy, xx, oy + 5, INK, 1.4)
        s += text(xx, oy + 20, lab, 10, GREY, "middle")

    # тепловий поріг — рівна підлога (білий шум)
    floor_y = oy - 70
    s += line(ox + 4, floor_y, ox + ow - 8, floor_y, BLUE, 2.6, "7,4")
    s += text(ox + ow - 14, floor_y - 9, "тепловий шум √(4kTRB) — рівний (білий)",
              11, BLUE, "end", "bold")

    # надлишковий шум: криві 1/f, що падають із частотою і впираються в поріг
    def excess_curve(top_y, col, lbl, lbl_y):
        out = ""
        pts = []
        N = 220
        for i in range(N + 1):
            frac = i / N
            xx = ox + 6 + (ow - 14) * frac
            # 1/f: густина ~ 1/sqrt(f); на лог-осі — спадна пряма у лог-лог.
            # висота над підлогою спадає від (floor_y-top_y) до ~0
            decay = (1 - frac) ** 1.15
            h_excess = (floor_y - top_y) * decay
            # сумарна густина = sqrt(floor² + excess²) у «висотній» метафорі
            yy = floor_y - max(0.0, (h_excess**2 + 6.0**2) ** 0.5 - 6.0)
            pts.append((xx, yy))
        out += polyline(pts, col, 2.8)
        out += text(ox + 18, lbl_y, lbl, 11.5, col, "start", "bold")
        return out

    s += excess_curve(oy - oh + 26, RED, "вуглецева композиція — велика гірка 1/f", oy - oh + 40)
    s += excess_curve(floor_y - 78, ORANGE, "вуглецева плівка — менша гірка", oy - oh + 60)
    s += excess_curve(floor_y - 22, GREEN, "металоплівка — майже сама лише підлога", oy - oh + 80)

    # позначити «кутову» частоту (1/f corner) для вуглецевого — де гірка зрівнялась з підлогою
    # знайдемо точку, де crimson крива близько до floor (visually ~ frac 0.7)
    corner_x = ox + 6 + (ow - 14) * 0.62
    s += line(corner_x, oy, corner_x, floor_y, GREY, 1.3, "3,3")
    s += circle(corner_x, floor_y, 4.5, "#ffffff", RED, 1.8)
    s += text(corner_x + 8, floor_y + 24, "кутова частота f_c:", 10, GREY, "start", "bold")
    s += text(corner_x + 8, floor_y + 38, "нижче неї панує 1/f,", 9.6, GREY, "start")
    s += text(corner_x + 8, floor_y + 51, "вище — тепловий поріг", 9.6, GREY, "start")

    # «де ми у вимірюванні» — стрілка на низькі частоти
    s += text(ox + 6, oy - oh - 0, "", 10, GREY, "start")
    s += rect(ox + ow - 250, oy - oh + 2, 244, 50, "#fff7ef", ORANGE, 1.3, 8)
    s += text(ox + ow - 128, oy - oh + 20, "Повільні/постійні виміри (DC, °C, маса)", 9.8, INK, "middle", "bold")
    s += text(ox + ow - 128, oy - oh + 35, "сидять ЛІВОРУЧ — саме там, де гірка 1/f", 9.4, GREY, "middle")
    s += text(ox + ow - 128, oy - oh + 48, "найвища. Тут тип резистора важить.", 9.4, GREY, "middle")

    save("fig-r09-s3c-2-spectrum.svg", s)


if __name__ == "__main__":
    fig_construction()
    fig_spectrum()
    print("done")
