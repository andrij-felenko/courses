# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для вставки 🔌 «Дзвін на фронті: послідовний резистор 22–33 Ом»
(до теми §3.1.5). Самодостатній: палітра й примітиви скопійовані з figs.py розділу
(AUTHORING §9 — спільні допоміжні функції копіюються в кожен скрипт), щоб головний
figs.py не чіпати. Вивід → ./img/. Імена файлів унікальні (-s5-c-...).

Стиль: білий фон; HIGH/'1'/+ червоний, LOW/'0'/− синій; «чисте/дійсне» — зелене;
бурштин — дзвін/спотворення; стрілки через marker; шрифт sans-serif.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (як у figs.py розділу) ───────────────────────────────────────────
RED   = "#c0271e"   # HIGH / '1' / +
BLUE  = "#1f47b5"   # LOW / '0' / −
GREEN = "#1f8a3b"   # чисте / дійсне / приборкане
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # бліде тло
AMBER = "#caa24a"   # дзвін / спотворення
COPPER = "#b5742e"  # мідь / доріжка
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", AMBER: "aAmber"}


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


def dot(cx, cy, r=3.4, color=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: символ резистора (зигзаг) ─────────────────────────────────────
def resistor_h(x, y, w=46, h=12, color=INK, sw=2.4):
    """Горизонтальний резистор-зигзаг, центр входу — (x,y), вихід — (x+w,y)."""
    n = 6
    step = w / n
    pts = [(x, y)]
    for i in range(n):
        xx = x + step * (i + 0.5)
        yy = y - h if i % 2 == 0 else y + h
        pts.append((xx, yy))
    pts.append((x + w, y))
    return polyline(pts, color, sw)


# ── символ буфера/драйвера (трикутник) ───────────────────────────────────────
def buffer_tri(x, y, s=30, color=INK, label="DRV"):
    out = (f'<path d="M{x:.1f},{y - s:.1f} L{x + s * 1.5:.1f},{y:.1f} '
           f'L{x:.1f},{y + s:.1f} Z" fill="#ffffff" stroke="{color}" stroke-width="2.2"/>\n')
    out += text(x + s * 0.5, y + 5, label, 12, color, "middle", "bold")
    return out


# ── маленька «мікросхема» приймача ───────────────────────────────────────────
def chip(x, y, w, h, label, color=INK):
    out = rect(x, y, w, h, "#fbfbfb", color, 2.2, 5)
    out += text(x + w / 2, y + h / 2 + 5, label, 13, color, "middle", "bold")
    # ніжка-вивід зліва
    out += line(x - 14, y + h / 2, x, y + h / 2, color, 2.2)
    return out


# =============================================================================
# Рис. 3.1.5.c.1 — звідки дзвін і як його гасить послідовний R
# Ліворуч: механізм (драйвер → паразитна L доріжки + C входу = LC-резонатор → дзвін).
# Праворуч: той самий шлях із послідовним R 22–33 Ом, що демпфує коливання.
# =============================================================================
def fig_ringing_mechanism():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Дзвін на фронті й послідовний резистор як демпфер", 18, INK, "middle", "bold")

    # ── ліва панель: БЕЗ резистора ───────────────────────────────────────────
    Lx = 30
    s += rect(Lx, 50, 340, 250, "#fffdf6", AMBER, 1.4, 8)
    s += text(Lx + 170, 72, "БЕЗ термінатора: LC-контур дзвенить", 14, AMBER, "middle", "bold")

    by = 130
    s += buffer_tri(Lx + 30, by, 26, BLUE, "DRV")
    # доріжка з паразитною індуктивністю
    s += text(Lx + 150, by - 38, "паразитна L доріжки", 12, GREY, "middle")
    # котушка-зигзаг як L
    coilx = Lx + 110
    cpts = [(coilx, by)]
    for i in range(4):
        cpts.append((coilx + 8 + i * 22, by - 16))
        cpts.append((coilx + 19 + i * 22, by))
    s += polyline(cpts, COPPER, 2.4)
    s += text(coilx + 44, by + 22, "L", 14, COPPER, "middle", "italic")
    s += line(Lx + 56, by, coilx, by, COPPER, 2.4)
    s += line(coilx + 96, by, Lx + 260, by, COPPER, 2.4)
    # приймач з ємністю входу
    s += chip(Lx + 274, by - 26, 50, 52, "RX", INK)
    # конденсатор входу на землю
    cx = Lx + 250
    s += line(cx, by, cx, by + 36, INK, 2)
    s += line(cx - 12, by + 36, cx + 12, by + 36, INK, 3)
    s += line(cx - 8, by + 42, cx + 8, by + 42, INK, 3)
    s += text(cx - 20, by + 40, "C", 13, INK, "end", "italic")
    s += line(cx, by + 42, cx, by + 52, INK, 2)
    s += polyline([(cx - 9, by + 52), (cx + 9, by + 52)], INK, 2)
    s += text(cx, by + 66, "вхід", 11, GREY, "middle")

    # осцилограма: дзвін
    ox, oy, ow, oh = Lx + 18, 215, 300, 70
    s += line(ox, oy, ox + ow, oy, GREY, 1)            # вісь 0
    s += line(ox, oy - oh, ox + ow, oy - oh, FAINT, 1)  # Vdd
    s += text(ox - 4, oy - oh + 4, "Vdd", 10, GREY, "end")
    s += text(ox - 8, oy + 4, "0", 10, GREY, "end")
    # фронт + затухаючий дзвін навколо Vdd
    pts = [(ox, oy)]
    x0 = ox + 40
    pts += [(x0, oy), (x0 + 18, oy - oh)]
    t = 0.0
    for k in range(120):
        xx = x0 + 18 + k * 1.9
        if xx > ox + ow:
            break
        env = math.exp(-k / 26.0)
        yy = (oy - oh) - 26 * env * math.sin(k / 3.4)
        pts.append((xx, yy))
    s += polyline(pts, AMBER, 2.4)
    # викид над Vdd
    s += text(x0 + 70, oy - oh - 18, "викид > Vdd", 11, AMBER, "middle", "bold")
    s += arrow(x0 + 70, oy - oh - 12, x0 + 40, oy - oh - 20, AMBER, 1.6)

    # ── права панель: З резистором ───────────────────────────────────────────
    Rx = 400
    s += rect(Rx, 50, 330, 250, "#f4fbf5", GREEN, 1.4, 8)
    s += text(Rx + 165, 72, "З послідовним R: дзвін придушено", 14, GREEN, "middle", "bold")

    s += buffer_tri(Rx + 20, by, 26, BLUE, "DRV")
    # послідовний резистор одразу біля драйвера
    s += line(Rx + 46, by, Rx + 70, by, COPPER, 2.4)
    s += resistor_h(Rx + 70, by, 46, 10, GREEN, 2.8)
    s += text(Rx + 93, by - 22, "Rs 22–33 Ω", 12, GREEN, "middle", "bold")
    # та сама L доріжки
    coilx2 = Rx + 130
    cpts2 = [(coilx2, by)]
    for i in range(4):
        cpts2.append((coilx2 + 8 + i * 16, by - 13))
        cpts2.append((coilx2 + 16 + i * 16, by))
    s += polyline(cpts2, COPPER, 2.2)
    s += text(coilx2 + 32, by + 20, "L", 13, COPPER, "middle", "italic")
    s += line(coilx2 + 72, by, Rx + 250, by, COPPER, 2.4)
    s += chip(Rx + 264, by - 26, 48, 52, "RX", INK)
    cx2 = Rx + 240
    s += line(cx2, by, cx2, by + 36, INK, 2)
    s += line(cx2 - 11, by + 36, cx2 + 11, by + 36, INK, 3)
    s += line(cx2 - 7, by + 42, cx2 + 7, by + 42, INK, 3)
    s += text(cx2 - 18, by + 40, "C", 12, INK, "end", "italic")
    s += line(cx2, by + 42, cx2, by + 52, INK, 2)
    s += polyline([(cx2 - 9, by + 52), (cx2 + 9, by + 52)], INK, 2)

    # осцилограма: чистий фронт без дзвону
    ox2, oy2 = Rx + 18, 215
    s += line(ox2, oy2, ox2 + 290, oy2, GREY, 1)
    s += line(ox2, oy2 - oh, ox2 + 290, oy2 - oh, FAINT, 1)
    s += text(ox2 - 4, oy2 - oh + 4, "Vdd", 10, GREY, "end")
    s += text(ox2 - 8, oy2 + 4, "0", 10, GREY, "end")
    pts2 = [(ox2, oy2), (ox2 + 40, oy2)]
    x0b = ox2 + 40
    for k in range(150):
        xx = x0b + k * 1.7
        if xx > ox2 + 290:
            break
        yy = oy2 - oh * (1 - math.exp(-k / 16.0))
        # ледь помітний горбик і одразу спокій
        if k < 30:
            yy -= 4 * math.exp(-k / 8.0) * math.sin(k / 4.0)
        pts2.append((xx, yy))
    s += polyline(pts2, GREEN, 2.6)
    s += text(x0b + 120, oy2 - oh - 16, "плавно, без коливань", 11, GREEN, "middle", "bold")

    # ── підпис-механізм унизу ────────────────────────────────────────────────
    s += text(W / 2, 340, "Чому дзвенить: різкий фронт + паразитна L доріжки + ємність C входу = LC-контур.",
              13, INK, "middle")
    s += text(W / 2, 360, "Rs додає втрати (R) у контур → з недемпфованого LC робить демпфований RLC → коливання гасне.",
              13, INK, "middle")
    s += text(W / 2, 384, "Ставлять Rs ВПРИТУЛ до виходу драйвера (джерела фронту), а не біля приймача.",
              13, COPPER, "middle", "bold")
    s += text(W / 2, 408, "Ціна: Rs разом із C трохи сповільнює фронт (τ = Rs·C) — тому беруть найменший R, що вже не дзвенить.",
              12, GREY, "middle", "italic")
    save("fig-14-5-c1-ringing-fix.svg", s)


# =============================================================================
# Рис. 3.1.5.c.2 — як підібрати й перевірити Rs (процедура + орієнтири)
# Зліва — драбинка номіналів і ефект; справа — три осцилограми (мало/в міру/багато R).
# =============================================================================
def fig_choose_and_check():
    W, H = 760, 420
    s = header(W, H)
    s += text(W / 2, 30, "Підбір номіналу: від «дзвенить» до «приборкано» (і не пересолити)", 17, INK, "middle", "bold")

    # ── три осцилограми ефекту ───────────────────────────────────────────────
    panels = [
        ("Rs замалий (0–10 Ω)", AMBER, "ще дзвенить", -1),
        ("Rs у міру (22–33 Ω)", GREEN, "чистий фронт", 0),
        ("Rs завеликий (>100 Ω)", BLUE, "млявий, з'їдена швидкість", +1),
    ]
    pw, ph = 230, 110
    y0 = 70
    for i, (title, col, note, mode) in enumerate(panels):
        px = 30 + i * 245
        s += rect(px, y0, pw, ph + 38, "#ffffff", col, 1.4, 8)
        s += text(px + pw / 2, y0 + 20, title, 13, col, "middle", "bold")
        ax, ay = px + 22, y0 + ph + 4
        aw, ah = pw - 44, ph - 30
        s += line(ax, ay, ax + aw, ay, GREY, 1)
        s += line(ax, ay - ah, ax + aw, ay - ah, FAINT, 1)
        s += text(ax - 4, ay - ah + 3, "Vdd", 9, GREY, "end")
        # будуємо фронт
        pts = [(ax, ay), (ax + 24, ay)]
        x0 = ax + 24
        if mode == -1:      # дзвін
            pts.append((x0 + 12, ay - ah))
            for k in range(80):
                xx = x0 + 12 + k * 1.6
                if xx > ax + aw:
                    break
                env = math.exp(-k / 20.0)
                yy = (ay - ah) - 16 * env * math.sin(k / 3.2)
                pts.append((xx, yy))
            s += polyline(pts, col, 2.4)
        elif mode == 0:     # чисто
            for k in range(90):
                xx = x0 + k * 1.7
                if xx > ax + aw:
                    break
                yy = ay - ah * (1 - math.exp(-k / 12.0))
                if k < 18:
                    yy -= 3 * math.exp(-k / 7.0) * math.sin(k / 4.0)
                pts.append((xx, yy))
            s += polyline(pts, col, 2.6)
        else:               # млявий
            for k in range(120):
                xx = x0 + k * 1.4
                if xx > ax + aw:
                    break
                yy = ay - ah * (1 - math.exp(-k / 34.0))
                pts.append((xx, yy))
            s += polyline(pts, col, 2.4)
        s += text(px + pw / 2, y0 + ph + 30, note, 11, col, "middle", "italic")

    # ── процедура підбору (ліворуч) ──────────────────────────────────────────
    by = 250
    s += text(40, by, "Як підібрати на практиці:", 14, INK, "start", "bold")
    steps = [
        "1.  Старт із ~33 Ω (або поряд: 22 / 27 / 33 Ω).",
        "2.  Дивись фронт осцилографом біля ПРИЙМАЧА.",
        "3.  Дзвенить → бери більший R; млявий → менший.",
        "4.  Бери НАЙМЕНШИЙ R, за якого дзвін уже зник.",
    ]
    for i, st in enumerate(steps):
        s += text(48, by + 24 + i * 22, st, 13, INK, "start")

    # ── орієнтовна формула / межа (праворуч) ─────────────────────────────────
    fx = 430
    s += rect(fx, by - 16, 300, 132, "#f6f9ff", BLUE, 1.3, 8)
    s += text(fx + 150, by + 4, "Орієнтир номіналу", 13, BLUE, "middle", "bold")
    s += text(fx + 16, by + 30, "Rs + Rout(драйвера)  ≈  Z доріжки", 13, INK, "start")
    s += text(fx + 16, by + 52, "Z типової доріжки ≈ 40–70 Ω,", 12, GREY, "start")
    s += text(fx + 16, by + 70, "Rout драйвера ≈ 10–50 Ω →", 12, GREY, "start")
    s += text(fx + 16, by + 90, "лишок 22–33 Ω «добиває» до Z.", 12, GREY, "start")
    s += text(fx + 16, by + 110, "Точне Z — це вже лінії передачі, §6.8.", 11, COPPER, "start", "italic")

    s += text(W / 2, 408,
              "Головне правило: один послідовний R на лінію, впритул до драйвера; перевіряй очима на осцилографі, а не на віру.",
              12, INK, "middle", "italic")
    save("fig-14-5-c2-choose-check.svg", s)


if __name__ == "__main__":
    fig_ringing_mechanism()
    fig_choose_and_check()
    print("ch14-s5-c series-termination figures done.")
