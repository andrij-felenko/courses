# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 34 — «Орієнтація й керування зі зворотним
зв'язком (ПІД)» (Модуль 5). Чистий Python, без сторонніх залежностей. → ./img/.

Поточний файл покриває історичну вставку (Рис. 34.0.k):
  1 поплавковий регулятор Ктесібія (водяний годинник) — найдавніший зворотний зв'язок;
  2 відцентровий регулятор Уатта на паровій машині (1788);
  3 узагальнена петля від'ємного зворотного зв'язку (блок-схема);
  4 стійкість проти «хитання» (Максвелл, Вишнеградський) — обчислені перехідні криві;
  5 три складові Мінорського (P/I/D) очима стернового (1922);
  6 «від куль до коду»: еволюція регулятора.
Спільні помічники — у стилі Розділів 28–33.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
GOLD  = "#caa24a"
PURP  = "#9a4ea8"
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


def arc_arrow(cx, cy, r, a0, a1, color=INK, w=2):
    x0 = cx + r * math.cos(math.radians(a0))
    y0 = cy + r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy + r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    m = _MARK.get(color, "aInk")
    return (f'<path d="M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} {sweep} '
            f'{x1:.1f},{y1:.1f}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    if weight == "italic":
        weight, style = "normal", "italic"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def dot(cx, cy, r=5, fill=INK):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def poly(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def polygon(pts, fill=INK, stroke="none", sw=1):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("  saved", name)


def _pt(x0, y0, w, ht, xv, uv):
    return (x0 + xv * w, y0 - uv * ht)


def _plot_path(x0, y0, w, ht, pts_norm, color, sw=2.4, dash=None):
    return poly([_pt(x0, y0, w, ht, xv, uv) for (xv, uv) in pts_norm], color, sw, dash=dash)


def axes(x0, y0, w, ht, color=INK):
    return arrow(x0, y0, x0, y0 - ht, color, 1.6) + arrow(x0, y0, x0 + w, y0, color, 1.6)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ════════════════════════════════════════════════════════════════════════════
#  §34.0 Історія — від відцентрового регулятора Уатта до ПІД
# ════════════════════════════════════════════════════════════════════════════

def fig_float_clock():
    """Рис. 34.0.1 — поплавковий регулятор Ктесібія: сталий рівень → рівний відлік."""
    w, h = 720, 330
    s = header(w, h)
    s += text(w / 2, 26, "Поплавковий регулятор Ктесібія (~270 до н.е.): рівень тримає сам себе",
              13.5, INK, "middle", "bold")

    # supply tank (constant head)
    s += rect(58, 66, 120, 44, fill="#cfe0f5", stroke=INK, sw=1.6)
    s += text(118, 60, "подача води", 11, INK, "middle")
    # pipe from supply: right then down into regulator inlet at x=330
    s += line(178, 88, 330, 88, GREY, 7)
    s += line(330, 88, 330, 150, GREY, 7)

    # regulator vessel
    s += rect(250, 150, 160, 122, fill="none", stroke=INK, sw=2)
    # water inside up to constant level y=196
    lvl = 196
    s += rect(252, lvl, 156, 122 - (lvl - 150), fill="#dCEBFb", stroke="none")
    s += line(250, lvl, 410, lvl, BLUE, 1.6, dash="6 4")
    s += text(414, lvl - 4, "сталий рівень", 11, BLUE, "start", "bold")

    # conical valve plug at inlet (closes as float rises)
    s += polygon([(322, 150), (338, 150), (330, 166)], fill=RED)
    s += text(330, 142, "клапан", 10, RED, "middle")
    # float on the surface + stem to plug
    s += line(330, 166, 330, lvl - 14, INK, 2)
    s += circle(330, lvl - 1, 13, fill="#f6e7c4", stroke=INK, w=2)
    s += text(330, lvl + 4, "поплавок", 9, INK, "middle")

    # feedback annotation
    s += arrow(355, lvl - 18, 339, 162, RED, 2)
    s += text(430, 120, "рівень ↑  →  поплавок ↑", 12, INK, "start")
    s += text(430, 138, "→  клапан прикривається", 12, RED, "start", "bold")
    s += text(430, 156, "→  притік зменшується", 12, INK, "start")

    # outflow orifice → steady drip to measuring cylinder
    s += line(410, 250, 470, 250, GREY, 6)
    s += line(470, 250, 470, 300, GREY, 6)
    for i in range(3):
        s += dot(470, 268 + i * 12, 2.2, BLUE)

    # measuring cylinder (the clock dial-by-level)
    s += rect(508, 118, 78, 178, fill="none", stroke=INK, sw=2)
    s += rect(510, 210, 74, 84, fill="#dCEBFb", stroke="none")
    s += circle(547, 212, 9, fill="#f6e7c4", stroke=INK, w=1.6)  # float pointer
    for i, lab in enumerate(["VI", "V", "IV", "III"]):
        yy = 150 + i * 36
        s += line(586, yy, 598, yy, INK, 1.4)
        s += text(604, yy + 4, lab, 10, INK, "start")
    s += text(547, 312, "рівномірний відлік годин", 11, INK, "middle", "bold")

    s += text(w / 2, h - 8,
              "сталий напір → стала витрата краплі → точний водяний годинник",
              11.5, GREY, "middle", "italic")
    save("fig-34-0-1.svg", s)


def fig_watt_governor():
    """Рис. 34.0.2 — відцентровий («кульовий») регулятор Уатта на паровій машині, 1788."""
    w, h = 720, 372
    s = header(w, h)
    s += text(w / 2, 26, "Відцентровий регулятор Уатта (1788): швидкість тримає заслінку",
              13.5, INK, "middle", "bold")

    piv = (188, 92)           # pivot at top of spindle
    pulley = (188, 312)       # drive pulley at bottom
    # spindle
    s += line(piv[0], piv[1], pulley[0], pulley[1] - 30, INK, 3)
    s += dot(piv[0], piv[1], 4, INK)

    # drive pulley + belt
    s += circle(pulley[0], pulley[1], 30, fill="#eeeeee", stroke=INK, w=2)
    s += dot(pulley[0], pulley[1], 3, INK)
    s += line(118, pulley[1] - 30, 118, pulley[1] + 30, GREY, 3)
    s += line(118, pulley[1] - 30, pulley[0], pulley[1] - 30, GREY, 3)
    s += line(118, pulley[1] + 30, pulley[0], pulley[1] + 30, GREY, 3)
    s += arc_arrow(pulley[0], pulley[1], 44, 200, 340, INK, 2)
    s += text(pulley[0], pulley[1] + 56, "від машини (обертання)", 11, INK, "middle")

    # HIGH speed (solid) — balls flown out & up
    bhi_l, bhi_r = (104, 176), (272, 176)
    s += line(piv[0], piv[1], bhi_l[0], bhi_l[1], INK, 2.4)
    s += line(piv[0], piv[1], bhi_r[0], bhi_r[1], INK, 2.4)
    s += circle(bhi_l[0], bhi_l[1], 17, fill="#cfd6e6", stroke=INK, w=2)
    s += circle(bhi_r[0], bhi_r[1], 17, fill="#cfd6e6", stroke=INK, w=2)
    s += arrow(bhi_l[0] - 6, bhi_l[1], bhi_l[0] - 34, bhi_l[1], RED, 2)
    s += arrow(bhi_r[0] + 6, bhi_r[1], bhi_r[0] + 34, bhi_r[1], RED, 2)
    s += text(bhi_r[0] + 38, bhi_r[1] + 4, "відцентрова сила", 10.5, RED, "start")

    # LOW speed (dashed) — balls hang in & down
    blo_l, blo_r = (146, 232), (230, 232)
    s += line(piv[0], piv[1], blo_l[0], blo_l[1], GREY, 1.8, dash="5 4")
    s += line(piv[0], piv[1], blo_r[0], blo_r[1], GREY, 1.8, dash="5 4")
    s += circle(blo_l[0], blo_l[1], 13, fill="none", stroke=GREY, w=1.6)
    s += circle(blo_r[0], blo_r[1], 13, fill="none", stroke=GREY, w=1.6)
    s += text(blo_r[0] + 18, blo_r[1] + 4, "(повільно)", 9.5, GREY, "start", "italic")

    # sleeve/collar on spindle + links from arms
    sleeve_y = 158
    s += rect(174, sleeve_y, 28, 12, fill="#dddddd", stroke=INK, sw=1.6)
    s += line(184, sleeve_y + 6, bhi_l[0] + 12, bhi_l[1] + 8, INK, 1.8)
    s += line(192, sleeve_y + 6, bhi_r[0] - 12, bhi_r[1] + 8, INK, 1.8)
    s += text(150, sleeve_y - 6, "муфта", 10, INK, "end")

    # bell-crank lever from sleeve to throttle
    s += dot(360, sleeve_y + 6, 4, INK)                      # lever fulcrum
    s += line(202, sleeve_y + 6, 360, sleeve_y + 6, INK, 2.4)
    s += line(360, sleeve_y + 6, 452, 214, INK, 2.4)        # down-link to valve
    s += text(286, sleeve_y - 4, "важіль", 10, INK, "middle")

    # steam pipe + butterfly valve
    s += line(396, 248, 626, 248, INK, 2)
    s += line(396, 286, 626, 286, INK, 2)
    s += rect(396, 248, 230, 38, fill="#f1efe6", stroke="none")
    s += line(396, 248, 626, 248, INK, 2)
    s += line(396, 286, 626, 286, INK, 2)
    # valve disc (partly closed): tilted line across pipe
    vx = 452
    s += line(vx - 16, 252, vx + 16, 282, RED, 4)
    s += dot(vx, 267, 3, INK)
    s += text(540, 242, "пара → циліндр", 11, INK, "middle", "bold")
    s += text(452, 306, "заслінка", 10, RED, "middle")

    s += text(w / 2, h - 10,
              "швидкість ↑ → кулі розходяться → муфта ↑ → заслінка прикривається → машина гальмує",
              11.5, GREEN, "middle", "bold")
    save("fig-34-0-2.svg", s)


def fig_feedback_loop():
    """Рис. 34.0.3 — узагальнена петля від'ємного зворотного зв'язку (спільна суть усіх регуляторів)."""
    w, h = 720, 252
    s = header(w, h)
    s += text(w / 2, 26, "Спільна суть: петля від'ємного зворотного зв'язку", 13.5, INK, "middle", "bold")

    sj = (150, 116)            # summing junction
    s += circle(sj[0], sj[1], 17, fill="#ffffff", stroke=INK, w=2)
    s += line(sj[0] - 8, sj[1], sj[0] + 8, sj[1], INK, 1.4)
    s += line(sj[0], sj[1] - 8, sj[0], sj[1] + 8, INK, 1.4)
    # setpoint in
    s += arrow(54, sj[1], sj[0] - 17, sj[1], BLUE, 2.2)
    s += text(54, sj[1] - 10, "завдання r", 11.5, BLUE, "start", "bold")
    s += text(54, sj[1] + 22, "(бажане)", 10, GREY, "start")
    s += text(sj[0] - 24, sj[1] + 30, "−", 16, RED, "middle", "bold")

    # controller
    s += rect(232, 92, 116, 48, fill="#eef3fb", stroke=INK, sw=2, rx=6)
    s += text(290, 113, "Регулятор", 12.5, INK, "middle", "bold")
    s += text(290, 130, "P · I · D", 11, BLUE, "middle")
    s += arrow(sj[0] + 17, sj[1], 232, sj[1], INK, 2.2)
    s += text(200, sj[1] - 9, "похибка e", 11, RED, "middle", "bold")

    # plant
    s += rect(420, 92, 150, 48, fill="#eef7ee", stroke=INK, sw=2, rx=6)
    s += text(495, 113, "Об'єкт (машина)", 12, INK, "middle", "bold")
    s += text(495, 130, "двигун · судно · дрон", 9.5, GREY, "middle")
    s += arrow(348, sj[1], 420, sj[1], INK, 2.2)
    s += text(384, sj[1] - 9, "вплив u", 10.5, INK, "middle")

    # output
    out_x = 660
    s += line(570, sj[1], out_x, sj[1], INK, 2.2)
    s += arrow(out_x, sj[1], out_x, sj[1] - 40, GREEN, 2.2)
    s += text(out_x + 6, sj[1] - 44, "вихід y", 11.5, GREEN, "start", "bold")
    s += dot(610, sj[1], 3.5, INK)

    # feedback path through sensor
    s += line(610, sj[1], 610, 196, INK, 2)
    s += rect(360, 178, 116, 36, fill="#fbf3f3", stroke=INK, sw=2, rx=6)
    s += text(418, 201, "Давач", 12, INK, "middle", "bold")
    s += line(610, 196, 476, 196, INK, 2)
    s += arrow(360, 196, sj[0], 196, INK, 2)
    s += line(sj[0], 196, sj[0], sj[1] + 17, INK, 2)
    s += text(540, 211, "вимір y", 10.5, GREY, "middle")

    s += text(w / 2, h - 10,
              "відняти вимір від завдання → діяти на похибку → так працює і регулятор Уатта, і ПІД у дроні",
              11, GREY, "middle", "italic")
    save("fig-34-0-3.svg", s)


def fig_stability():
    """Рис. 34.0.4 — стійкість проти «хитання»: обчислені перехідні криві (Максвелл/Вишнеградський)."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Чому регулятор іноді «шаленіє»: стійкість проти хитання", 13.5, INK, "middle", "bold")

    x0, y0, pw, ph = 90, 250, 560, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 - 8, y0 - ph - 6, "відхилення", 11, INK, "end")
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")

    # setpoint line
    sp = 0.56
    s += line(x0, y0 - sp * ph, x0 + pw, y0 - sp * ph, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, y0 - sp * ph + 4, "ціль", 10.5, GREY, "start")

    N = 200
    stable, unstable = [], []
    for i in range(N + 1):
        t = i / N
        xv = t
        # stable: underdamped step that settles to the setpoint
        st = sp * (1.0 - math.exp(-3.4 * t) * math.cos(13.5 * t))
        stable.append((xv, _clamp(st, 0.0, 0.98)))
        # unstable: oscillation whose envelope grows ("hunting")
        env = 0.05 * (math.exp(2.7 * t) - 1.0)
        un = sp + env * math.sin(13.5 * t)
        unstable.append((xv, _clamp(un, 0.02, 0.98)))

    s += _plot_path(x0, y0, pw, ph, unstable, RED, 2.6)
    s += _plot_path(x0, y0, pw, ph, stable, GREEN, 2.6)

    # legend
    s += line(x0 + 24, 64, x0 + 54, 64, GREEN, 3)
    s += text(x0 + 60, 68, "стійко: коливання згасає, система заспокоюється", 11, GREEN, "start", "bold")
    s += line(x0 + 24, 86, x0 + 54, 86, RED, 3)
    s += text(x0 + 60, 90, "хитання: амплітуда росте — система йде «вразнос»", 11, RED, "start", "bold")

    s += text(w / 2, h - 8,
              "Максвелл (1868) і Вишнеградський (1876) першими порахували, де межа — так народилася теорія керування",
              10.8, GREY, "middle", "italic")
    save("fig-34-0-4.svg", s)


def fig_pid_helmsman():
    """Рис. 34.0.5 — три складові Мінорського (P/I/D) очима стернового (1922)."""
    w, h = 720, 326
    s = header(w, h)
    s += text(w / 2, 26, "Закон Мінорського (1922): кермо за похибкою — зараз, у минулому й наперед",
              13.5, INK, "middle", "bold")

    x0, y0, pw, ph = 92, 244, 500, 176
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    s += text(x0 - 8, y0 - ph - 6, "курс", 11, INK, "end")

    tgt = 0.74                         # target heading
    s += line(x0, y0 - tgt * ph, x0 + pw, y0 - tgt * ph, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, y0 - tgt * ph + 4, "бажаний курс", 10.5, GREY, "start")

    N = 160
    k = 2.7
    actual = [(i / N, tgt * (1.0 - math.exp(-k * (i / N)))) for i in range(N + 1)]
    s += _plot_path(x0, y0, pw, ph, actual, BLUE, 2.6)

    # mark t*
    ts = 0.40
    a_ts = tgt * (1.0 - math.exp(-k * ts))
    px = x0 + ts * pw
    p_act = y0 - a_ts * ph
    p_tgt = y0 - tgt * ph

    # I — shaded accumulated error up to t*
    fillpts = [(x0, p_tgt)]
    for i in range(int(N * ts) + 1):
        t = i / N
        fillpts.append((x0 + t * pw, y0 - tgt * (1.0 - math.exp(-k * t)) * ph))
    fillpts.append((px, p_tgt))
    s += polygon(fillpts, fill="#fbeede", stroke="none")
    s += text(x0 + 40, p_tgt + 30, "I: ∫e — накопичене минуле", 11, GOLD, "start", "bold")

    # P — current gap
    s += line(px, p_act, px, p_tgt, RED, 2.6)
    s += text(px + 8, (p_act + p_tgt) / 2 + 4, "P: e зараз", 11, RED, "start", "bold")
    s += dot(px, p_act, 4, BLUE)

    # D — tangent (rate) at t*
    slope = tgt * k * math.exp(-k * ts)        # d(actual)/dt in normalized units
    dx = 0.16
    x_a, x_b = ts - dx, ts + dx
    y_a = a_ts - slope * dx
    y_b = a_ts + slope * dx
    s += line(x0 + x_a * pw, y0 - y_a * ph, x0 + x_b * pw, y0 - y_b * ph, GREEN, 2.4)
    s += text(x0 + x_b * pw + 4, y0 - y_b * ph - 2, "D: de/dt — нахил, передбачення", 10.5, GREEN, "start", "bold")

    # rudder law box
    s += rect(x0 + pw + 14, 70, 96, 0.1, fill="none", stroke="none")
    s += text(w / 2, h - 30, "кермо  u  =  Kp·e  +  Ki·∫e dt  +  Kd·de/dt",
              13.5, INK, "middle", "bold")
    s += text(w / 2, h - 10,
              "P — реакція на теперішню похибку · I — на накопичену · D — на швидкість зміни",
              10.8, GREY, "middle", "italic")
    save("fig-34-0-5.svg", s)


def fig_evolution():
    """Рис. 34.0.6 — «від куль до коду»: та сама ідея в різних оболонках."""
    w, h = 720, 232
    s = header(w, h)
    s += text(w / 2, 26, "Та сама ідея — інша оболонка: від куль Уатта до рядка коду",
              13.5, INK, "middle", "bold")

    cx = [110, 290, 470, 645]
    cy = 120
    boxw = 150

    # 1 — Watt governor (mini)
    s += rect(cx[0] - boxw / 2, 56, boxw, 116, fill="#f6f4ec", stroke=INK, sw=1.6, rx=8)
    s += line(cx[0], 78, cx[0], 132, INK, 2)
    s += line(cx[0], 84, cx[0] - 24, 108, INK, 2)
    s += line(cx[0], 84, cx[0] + 24, 108, INK, 2)
    s += circle(cx[0] - 26, 110, 8, fill="#cfd6e6", stroke=INK, w=1.6)
    s += circle(cx[0] + 26, 110, 8, fill="#cfd6e6", stroke=INK, w=1.6)
    s += text(cx[0], 150, "кулі Уатта", 11, INK, "middle", "bold")
    s += text(cx[0], 166, "1788 · механіка", 9.5, GREY, "middle")

    # 2 — pneumatic
    s += rect(cx[1] - boxw / 2, 56, boxw, 116, fill="#f6f4ec", stroke=INK, sw=1.6, rx=8)
    s += rect(cx[1] - 20, 80, 40, 26, fill="#dfe7d9", stroke=INK, sw=1.6)
    s += line(cx[1] - 20, 86, cx[1] + 20, 86, INK, 1)
    s += line(cx[1] - 20, 92, cx[1] + 20, 92, INK, 1)
    s += line(cx[1] - 20, 98, cx[1] + 20, 98, INK, 1)
    s += line(cx[1], 106, cx[1], 130, INK, 2)
    s += text(cx[1], 150, "пневматика", 11, INK, "middle", "bold")
    s += text(cx[1], 166, "1930-ті · Ціглер–Ніколс", 9, GREY, "middle")

    # 3 — analog op-amp
    s += rect(cx[2] - boxw / 2, 56, boxw, 116, fill="#f6f4ec", stroke=INK, sw=1.6, rx=8)
    s += polygon([(cx[2] - 18, 84), (cx[2] - 18, 124), (cx[2] + 22, 104)], fill="none", stroke=INK, sw=2)
    s += line(cx[2] - 40, 94, cx[2] - 18, 94, INK, 1.6)
    s += line(cx[2] - 40, 114, cx[2] - 18, 114, INK, 1.6)
    s += line(cx[2] + 22, 104, cx[2] + 40, 104, INK, 1.6)
    s += text(cx[2], 150, "аналог (ОП)", 11, INK, "middle", "bold")
    s += text(cx[2], 166, "1950–60-ті · R, C", 9.5, GREY, "middle")

    # 4 — MCU code
    s += rect(cx[3] - boxw / 2, 56, boxw, 116, fill="#eef3fb", stroke=BLUE, sw=2, rx=8)
    s += rect(cx[3] - 30, 80, 60, 30, fill="#ffffff", stroke=INK, sw=1.6)
    for i in range(4):
        s += line(cx[3] - 30, 88 + i * 7, cx[3] - 34, 88 + i * 7, INK, 1.4)
        s += line(cx[3] + 30, 88 + i * 7, cx[3] + 34, 88 + i * 7, INK, 1.4)
    s += text(cx[3], 99, "u=Σ", 10, BLUE, "middle", "bold")
    s += text(cx[3], 150, "код у МК", 11, BLUE, "middle", "bold")
    s += text(cx[3], 166, "сьогодні · ПІД", 9.5, GREY, "middle")

    for i in range(3):
        s += arrow(cx[i] + boxw / 2 + 2, cy, cx[i + 1] - boxw / 2 - 2, cy, INK, 2)

    s += text(w / 2, h - 8,
              "об'єкти різні, рівняння — те саме: зворотний зв'язок керує помилкою",
              11, GREY, "middle", "italic")
    save("fig-34-0-6.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.1 Орієнтація в просторі: кути Ейлера
#  (трійки осей проєктуються ізометрично після РЕАЛЬНОГО множення на матриці)
# ════════════════════════════════════════════════════════════════════════════

def ellipse(cx, cy, rx, ry, rot=0, stroke=INK, fill="none", w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{w}"{d} '
            f'transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})"/>\n')


def _Rx(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def _Ry(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def _Rz(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def _matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _apply(M, v):
    return [sum(M[i][k] * v[k] for k in range(3)) for i in range(3)]


def _iso(p, ox, oy, sc):
    x, y, z = p
    cx = math.cos(math.radians(30))
    sx = ox + (x - y) * cx * sc
    sy = oy + (x + y) * 0.5 * sc - z * sc
    return (sx, sy)


def _triad(R, ox, oy, sc=44, lw=2.6, labels=True):
    o2 = _iso((0, 0, 0), ox, oy, sc)
    out = ""
    order = [((0, 0, 1), BLUE, "z"), ((0, 1, 0), GREEN, "y"), ((1, 0, 0), RED, "x")]
    # draw far axes first (painter): sort by projected depth (x+y)
    order.sort(key=lambda a: (_apply(R, a[0])[0] + _apply(R, a[0])[1]))
    for v, col, lab in order:
        rv = _apply(R, v)
        p2 = _iso(rv, ox, oy, sc)
        out += arrow(o2[0], o2[1], p2[0], p2[1], col, lw)
        if labels:
            right = (rv[0] - rv[1]) >= 0
            out += text(p2[0] + (7 if right else -7), p2[1] - 5, lab,
                        11, col, "start" if right else "end", "bold")
    out += dot(o2[0], o2[1], 3, INK)
    return out


def _plane_pts(cx, cy, s, rot=0):
    base = [(0, -34), (6, -20), (6, -6), (40, 6), (40, 16), (6, 12), (6, 26),
            (14, 34), (14, 40), (0, 34), (-14, 40), (-14, 34), (-6, 26),
            (-6, 12), (-40, 16), (-40, 6), (-6, -6), (-6, -20)]
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for (x, y) in base:
        x *= s
        y *= s
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def fig_dof6():
    """Рис. 34.1.1 — 6 ступенів свободи: 3 переміщення + 3 обертання."""
    w, h = 720, 308
    s = header(w, h)
    s += text(w / 2, 26, "Шість ступенів свободи твердого тіла", 13.5, INK, "middle", "bold")

    # LEFT — translation
    cxl = 196
    s += text(cxl, 56, "Положення: 3 переміщення", 12, INK, "middle", "bold")
    s += polygon(_plane_pts(cxl, 178, 1.35), fill="#dce4f2", stroke=INK, sw=1.6)
    s += arrow(cxl, 150, cxl, 96, INK, 2)
    s += arrow(cxl, 206, cxl, 252, INK, 2)
    s += text(cxl + 6, 104, "вперед / назад", 10.5, INK, "start")
    s += arrow(cxl, 178, cxl + 92, 178, INK, 2)
    s += arrow(cxl, 178, cxl - 92, 178, INK, 2)
    s += text(cxl + 96, 174, "вбік", 10.5, INK, "start")
    s += arrow(cxl + 30, 200, cxl + 66, 236, INK, 2)
    s += arrow(cxl - 30, 156, cxl - 66, 120, INK, 2)
    s += text(cxl + 70, 240, "вгору / вниз", 10.5, INK, "start")

    # RIGHT — rotation (triad + spin glyphs)
    cxr = 524
    s += text(cxr, 56, "Орієнтація: 3 обертання", 12, INK, "middle", "bold")
    R = _matmul(_Rz(math.radians(18)), _Ry(math.radians(-12)))
    s += _triad(R, cxr, 186, 70)
    s += arc_arrow(cxr + 78, 150, 14, 70, 330, RED)
    s += text(cxr + 96, 150, "крен φ", 10.5, RED, "start", "bold")
    s += arc_arrow(cxr - 70, 150, 14, 210, 470, GREEN)
    s += text(cxr - 88, 150, "тангаж θ", 10.5, GREEN, "end", "bold")
    s += arc_arrow(cxr, 250, 14, 70, 330, BLUE)
    s += text(cxr + 20, 256, "рискання ψ", 10.5, BLUE, "start", "bold")

    save("fig-34-1-1.svg", s)


def fig_frames():
    """Рис. 34.1.2 — рамка тіла повернута відносно нерухомої світової (NED)."""
    w, h = 720, 322
    s = header(w, h)
    s += text(w / 2, 26, "Орієнтація = поворот рамки тіла відносно світової", 13.5, INK, "middle", "bold")

    # world frame NED (fixed)
    wx, wy = 150, 250
    s += arrow(wx, wy, wx, wy - 84, INK, 2.2)
    s += text(wx, wy - 92, "N", 12, INK, "middle", "bold")
    s += arrow(wx, wy, wx + 96, wy, INK, 2.2)
    s += text(wx + 102, wy + 4, "E", 12, INK, "start", "bold")
    s += arrow(wx, wy, wx - 40, wy + 44, INK, 2.2)
    s += text(wx - 48, wy + 52, "D", 12, INK, "end", "bold")
    s += text(wx + 10, wy + 70, "світова рамка (NED) — нерухома, Земля", 11, GREY, "middle")

    # body frame on a tilted plane (upper-right)
    bx, by = 500, 150
    s += polygon(_plane_pts(bx, by, 1.25, rot=28), fill="#dce4f2", stroke=INK, sw=1.5)
    R = _matmul(_matmul(_Rz(math.radians(38)), _Ry(math.radians(20))), _Rx(math.radians(18)))
    s += _triad(R, bx, by, 64)
    s += text(bx, by + 92, "рамка тіла — летить з апаратом", 11, GREY, "middle")
    s += text(bx + 44, by - 70, "x — ніс · y — праве крило · z — черево", 9.8, INK, "middle")

    # link
    s += arrow(250, 190, 410, 168, RED, 2, dash="6 4")
    s += text(330, 150, "поворот між рамками", 11, RED, "middle", "italic")
    save("fig-34-1-2.svg", s)


def fig_rpy():
    """Рис. 34.1.3 — крен, тангаж, рискання: три повороти навколо осей тіла."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Крен · тангаж · рискання — три кути Ейлера", 13.5, INK, "middle", "bold")
    cy = 168

    # 1) ROLL — front view, wings tilted by phi
    c1 = 140
    s += text(c1, 60, "Крен φ", 12.5, RED, "middle", "bold")
    phi = math.radians(22)
    dx, dy = 64 * math.cos(phi), 64 * math.sin(phi)
    s += line(c1 - dx, cy + dy, c1 + dx, cy - dy, INK, 3)          # wings
    s += circle(c1, cy, 12, fill="#dce4f2", stroke=INK, w=2)       # fuselage
    s += line(c1, cy, c1 + 10 * math.sin(phi), cy - 22 * math.cos(phi), INK, 2)  # fin
    s += dot(c1, cy, 3, RED)
    s += arc_arrow(c1, cy, 30, 200, 360, RED)
    s += text(c1, cy + 70, "крило вниз/вгору", 10, GREY, "middle")
    s += text(c1, cy + 86, "вісь — поздовжня (ніс)", 9.5, GREY, "middle")

    # 2) PITCH — side view, nose up by theta
    c2 = 360
    s += text(c2, 60, "Тангаж θ", 12.5, GREEN, "middle", "bold")
    th = math.radians(20)
    nose = (c2 + 60 * math.cos(th), cy - 60 * math.sin(th))
    tail = (c2 - 50 * math.cos(th), cy + 50 * math.sin(th))
    s += line(tail[0], tail[1], nose[0], nose[1], INK, 3)
    s += polygon([(nose[0], nose[1]), (nose[0] - 14, nose[1] - 2), (nose[0] - 10, nose[1] + 10)],
                 fill="#dce4f2", stroke=INK, sw=1)
    s += line(tail[0], tail[1], tail[0] - 6 * math.sin(th), tail[1] - 18 * math.cos(th), INK, 2)
    s += dot(c2, cy, 3, GREEN)
    s += arc_arrow(c2, cy, 30, 150, 300, GREEN)
    s += text(c2, cy + 70, "ніс угору/вниз", 10, GREY, "middle")
    s += text(c2, cy + 86, "вісь — поперечна (крила)", 9.5, GREY, "middle")

    # 3) YAW — top view, plane rotated by psi
    c3 = 580
    s += text(c3, 60, "Рискання ψ", 12.5, BLUE, "middle", "bold")
    s += polygon(_plane_pts(c3, cy, 1.0, rot=24), fill="#dce4f2", stroke=INK, sw=1.5)
    s += arc_arrow(c3, cy, 34, 70, 330, BLUE)
    s += text(c3, cy + 70, "ніс ліворуч/праворуч", 10, GREY, "middle")
    s += text(c3, cy + 86, "вісь — вертикальна", 9.5, GREY, "middle")

    save("fig-34-1-3.svg", s)


def fig_noncommute():
    """Рис. 34.1.4 — повороти не комутують: інший порядок → інша орієнтація."""
    w, h = 720, 348
    s = header(w, h)
    s += text(w / 2, 24, "Повороти не переставні: порядок змінює результат", 13.5, INK, "middle", "bold")

    a90 = math.radians(90)
    xs = [120, 330, 545]

    # Row A: X then Z  → R = Rz·Rx
    yA = 132
    s += text(46, yA - 64, "A", 14, INK, "start", "bold")
    s += _triad([[1, 0, 0], [0, 1, 0], [0, 0, 1]], xs[0], yA, 40)
    s += _triad(_Rx(a90), xs[1], yA, 40)
    s += _triad(_matmul(_Rz(a90), _Rx(a90)), xs[2], yA, 40)
    s += arrow(xs[0] + 56, yA, xs[1] - 56, yA, INK, 2)
    s += text((xs[0] + xs[1]) / 2, yA - 50, "+90° навколо X", 10.5, INK, "middle")
    s += arrow(xs[1] + 56, yA, xs[2] - 56, yA, INK, 2)
    s += text((xs[1] + xs[2]) / 2, yA - 50, "+90° навколо Z", 10.5, INK, "middle")

    # Row B: Z then X → R = Rx·Rz
    yB = 280
    s += text(46, yB - 64, "B", 14, INK, "start", "bold")
    s += _triad([[1, 0, 0], [0, 1, 0], [0, 0, 1]], xs[0], yB, 40)
    s += _triad(_Rz(a90), xs[1], yB, 40)
    s += _triad(_matmul(_Rx(a90), _Rz(a90)), xs[2], yB, 40)
    s += arrow(xs[0] + 56, yB, xs[1] - 56, yB, INK, 2)
    s += text((xs[0] + xs[1]) / 2, yB - 50, "+90° навколо Z", 10.5, INK, "middle")
    s += arrow(xs[1] + 56, yB, xs[2] - 56, yB, INK, 2)
    s += text((xs[1] + xs[2]) / 2, yB - 50, "+90° навколо X", 10.5, INK, "middle")

    # compare finals
    s += rect(xs[2] - 52, yA - 56, 104, 112 + (yB - yA) - 56, fill="none", stroke=RED, sw=1.6, rx=8)
    s += text(xs[2] + 86, (yA + yB) / 2, "≠", 26, RED, "middle", "bold")
    s += text(xs[2] + 86, (yA + yB) / 2 + 22, "різні", 11, RED, "middle", "bold")
    save("fig-34-1-4.svg", s)


def fig_zyx():
    """Рис. 34.1.5 — послідовність 3-2-1: рискання → тангаж → крен."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Послідовність 3-2-1 (Z-Y-X): як накручується орієнтація", 13.5, INK, "middle", "bold")

    ps = math.radians(40)
    th = math.radians(25)
    ph = math.radians(35)
    R1 = _Rz(ps)
    R2 = _matmul(R1, _Ry(th))
    R3 = _matmul(R2, _Rx(ph))
    xs = [110, 290, 470, 632]
    cy = 168
    mats = [[[1, 0, 0], [0, 1, 0], [0, 0, 1]], R1, R2, R3]
    labs = ["по світу", "рискання ψ", "тангаж θ", "крен φ"]
    cols = [GREY, BLUE, GREEN, RED]
    for i, (m, lab, col) in enumerate(zip(mats, labs, cols)):
        s += _triad(m, xs[i], cy, 42)
        s += text(xs[i], cy + 78, lab, 11, col, "middle", "bold")
        if i < 3:
            s += arrow(xs[i] + 50, cy, xs[i + 1] - 50, cy, INK, 2)
    save("fig-34-1-5.svg", s)


def fig_gimbal():
    """Рис. 34.1.6 — кардановий підвіс: три вкладені кільця = три кути Ейлера."""
    w, h = 720, 332
    s = header(w, h)
    s += text(w / 2, 26, "Кардановий підвіс: кути Ейлера «в металі»", 13.5, INK, "middle", "bold")
    cx, cy = 350, 180

    s += ellipse(cx, cy, 150, 138, 0, stroke=BLUE, w=3)            # outer — yaw
    s += line(cx, cy - 138, cx, cy + 138, BLUE, 1.4, dash="5 4")
    s += text(cx, cy - 150, "зовнішнє — рискання ψ", 11, BLUE, "middle", "bold")

    s += ellipse(cx, cy, 134, 50, 0, stroke=GREEN, w=3)           # middle — pitch
    s += text(cx + 158, cy + 4, "середнє — тангаж θ", 11, GREEN, "start", "bold")

    s += ellipse(cx, cy, 58, 110, 0, stroke=RED, w=3)            # inner — roll
    s += text(cx, cy + 150, "внутрішнє — крен φ", 11, RED, "middle", "bold")

    # center payload
    s += rect(cx - 16, cy - 12, 32, 24, fill="#f6e7c4", stroke=INK, sw=1.6, rx=3)
    s += text(cx, cy + 4, "гіро", 9, INK, "middle")
    s += text(cx + 158, cy + 22, "у центрі — те, що тримають", 9.5, GREY, "start")
    save("fig-34-1-6.svg", s)


def fig_gimballock():
    """Рис. 34.1.7 — складання рамок (gimbal lock): дві осі збіглися."""
    w, h = 720, 332
    s = header(w, h)
    s += text(w / 2, 26, "Складання рамок (gimbal lock): втрата ступеня свободи", 13.5, INK, "middle", "bold")

    # LEFT — normal
    lx, ly = 198, 184
    s += ellipse(lx, ly, 104, 96, 0, stroke=BLUE, w=2.6)
    s += ellipse(lx, ly, 94, 36, 0, stroke=GREEN, w=2.6)
    s += ellipse(lx, ly, 40, 78, 0, stroke=RED, w=2.6)
    s += line(lx, ly - 96, lx, ly + 96, BLUE, 1.2, dash="4 4")
    s += line(lx - 94, ly, lx + 94, ly, GREEN, 1.2, dash="4 4")
    s += dot(lx, ly, 4, INK)
    s += text(lx, 70, "Норма · тангаж 0°", 12, GREEN, "middle", "bold")
    s += text(lx, ly + 116, "осі взаємно ⊥ → 3 свободи", 10.5, INK, "middle")

    # RIGHT — locked (pitch 90°, roll-axis ≡ yaw-axis, both vertical)
    rx, ry = 520, 184
    s += ellipse(rx, ry, 104, 96, 0, stroke=BLUE, w=2.6)          # yaw ring
    s += ellipse(rx, ry, 132, 18, 0, stroke=GREEN, w=2.6)        # pitch ring edge-on
    s += ellipse(rx, ry, 46, 92, 0, stroke=RED, w=2.6)          # roll ring now vertical too
    # both inner & outer spin about SAME vertical axis
    s += arrow(rx - 18, ry - 110, rx - 18, ry + 110, RED, 2.4)
    s += arrow(rx + 18, ry - 110, rx + 18, ry + 110, BLUE, 2.4)
    s += dot(rx, ry, 4, INK)
    s += text(rx, 70, "Тангаж 90° · крен ≡ рискання", 12, RED, "middle", "bold")
    s += text(rx, ry + 116, "дві осі збіглися → 2 свободи", 10.5, RED, "middle", "bold")
    s += text(rx, ry + 134, "крен і рискання нерозрізненні", 10, GREY, "middle")
    save("fig-34-1-7.svg", s)


def fig_conventions():
    """Рис. 34.1.8 — пастка конвенцій: NED проти ENU."""
    w, h = 720, 296
    s = header(w, h)
    s += text(w / 2, 26, "Та сама орієнтація — різні домовленості", 13.5, INK, "middle", "bold")

    # NED (aviation)
    ax, ay = 180, 196
    s += arrow(ax, ay, ax, ay - 92, RED, 2.4)
    s += text(ax, ay - 100, "N (x)", 11.5, RED, "middle", "bold")
    s += arrow(ax, ay, ax + 96, ay, GREEN, 2.4)
    s += text(ax + 102, ay + 4, "E (y)", 11.5, GREEN, "start", "bold")
    s += arrow(ax, ay, ax - 40, ay + 46, BLUE, 2.4)
    s += text(ax - 48, ay + 54, "D (z)", 11.5, BLUE, "end", "bold")
    s += text(ax, 70, "Авіація: NED", 12.5, INK, "middle", "bold")
    s += text(ax, ay + 86, "північ · схід · вниз", 10.5, GREY, "middle")

    # ENU (ROS / robotics)
    bx, by = 540, 196
    s += arrow(bx, by, bx + 96, by, RED, 2.4)
    s += text(bx + 102, by + 4, "E (x)", 11.5, RED, "start", "bold")
    s += arrow(bx, by, bx, by - 92, GREEN, 2.4)
    s += text(bx, by - 100, "N (y)", 11.5, GREEN, "middle", "bold")
    s += arrow(bx, by, bx - 40, by - 44, BLUE, 2.4)
    s += text(bx - 48, by - 50, "U (z)", 11.5, BLUE, "end", "bold")
    s += text(bx, 70, "Робототехніка: ENU", 12.5, INK, "middle", "bold")
    s += text(bx, by + 86, "схід · північ · вгору", 10.5, GREY, "middle")

    s += text(w / 2, h - 14,
              "знаки, додатний напрям і послідовність різняться між бібліотеками — завжди звіряйте",
              11, RED, "middle", "bold")
    save("fig-34-1-8.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.2 Кватерніони
# ════════════════════════════════════════════════════════════════════════════

def _axis_angle(n, ang):
    nx, ny, nz = n
    L = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    nx, ny, nz = nx / L, ny / L, nz / L
    c, s = math.cos(ang), math.sin(ang)
    C = 1 - c
    return [
        [c + nx * nx * C, nx * ny * C - nz * s, nx * nz * C + ny * s],
        [ny * nx * C + nz * s, c + ny * ny * C, ny * nz * C - nx * s],
        [nz * nx * C - ny * s, nz * ny * C + nx * s, c + nz * nz * C],
    ]


def _triad_c(R, ox, oy, sc, cols, labels=True, lw=2.6):
    o2 = _iso((0, 0, 0), ox, oy, sc)
    out = ""
    axes3 = [((0, 0, 1), cols[2], "z"), ((0, 1, 0), cols[1], "y"), ((1, 0, 0), cols[0], "x")]
    axes3.sort(key=lambda a: (_apply(R, a[0])[0] + _apply(R, a[0])[1]))
    for v, col, lab in axes3:
        rv = _apply(R, v)
        p2 = _iso(rv, ox, oy, sc)
        out += arrow(o2[0], o2[1], p2[0], p2[1], col, lw)
        if labels:
            right = (rv[0] - rv[1]) >= 0
            out += text(p2[0] + (7 if right else -7), p2[1] - 5, lab,
                        11, col, "start" if right else "end", "bold")
    out += dot(o2[0], o2[1], 3, INK)
    return out


def fig_axisangle():
    """Рис. 34.2.1 — теорема Ейлера: один поворот навколо однієї осі."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Теорема Ейлера: будь-яка орієнтація — один поворот навколо однієї осі",
              13, INK, "middle", "bold")
    ox, oy, sc = 380, 178, 70

    # reference (grey) and rotated (color) triads
    Iden = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    s += _triad_c(Iden, ox, oy, sc, (GREY, GREY, GREY), labels=False, lw=2.0)
    n = (0.32, 0.26, 1.0)
    R = _axis_angle(n, math.radians(95))
    s += _triad_c(R, ox, oy, sc, (RED, GREEN, BLUE), labels=True)

    # axis n
    nL = math.sqrt(sum(c * c for c in n))
    nn = tuple(c / nL for c in n)
    pax = _iso((nn[0] * 1.35, nn[1] * 1.35, nn[2] * 1.35), ox, oy, sc)
    o2 = _iso((0, 0, 0), ox, oy, sc)
    s += arrow(o2[0], o2[1], pax[0], pax[1], GOLD, 3)
    s += text(pax[0] + 6, pax[1] - 4, "вісь n", 11.5, GOLD, "start", "bold")
    s += arc_arrow(ox + 6, oy - 70, 18, 30, 320, INK, 2)
    s += text(ox + 30, oy - 84, "кут θ", 11.5, INK, "start", "bold")

    s += text(70, 92, "Сіра трійка — початок,", 11, GREY, "start")
    s += text(70, 108, "кольорова — кінець.", 11, INK, "start")
    s += text(70, 130, "Між ними — ОДИН поворот", 11, INK, "start", "bold")
    s += text(70, 146, "θ навколо осі n.", 11, INK, "start", "bold")
    save("fig-34-2-1.svg", s)


def fig_quatcomp():
    """Рис. 34.2.2 — кватерніон як упакована вісь-кут (4 числа, пів-кута)."""
    w, h = 720, 268
    s = header(w, h)
    s += text(w / 2, 26, "Кватерніон = вісь-кут, упакований у чотири числа", 13.5, INK, "middle", "bold")

    # left: axis-angle icon
    s += rect(54, 70, 190, 120, fill="#f6f4ec", stroke=INK, sw=1.6, rx=8)
    s += text(149, 92, "вісь-кут", 12, INK, "middle", "bold")
    s += arrow(110, 165, 180, 110, GOLD, 3)
    s += text(186, 108, "n", 12, GOLD, "start", "bold")
    s += arc_arrow(120, 150, 18, 20, 300, INK, 2)
    s += text(120, 182, "θ", 12, INK, "middle", "bold")

    s += arrow(252, 130, 300, 130, INK, 2.4)

    # right: four cells
    labs = ["w", "x", "y", "z"]
    cols = [PURP, RED, GREEN, BLUE]
    for i, (lab, col) in enumerate(zip(labs, cols)):
        x = 320 + i * 92
        s += rect(x, 84, 78, 60, fill="#ffffff", stroke=col, sw=2.2, rx=6)
        s += text(x + 39, 120, lab, 20, col, "middle", "bold")
    s += text(320, 76, "скаляр", 10, PURP, "start")
    s += text(412, 76, "вектор (x, y, z)", 10, INK, "start")

    s += text(515, 168, "w = cos(θ/2)", 13, PURP, "middle", "bold")
    s += text(515, 190, "(x,y,z) = sin(θ/2)·n", 13, INK, "middle", "bold")
    s += text(w / 2, h - 12, "пів-кута θ/2 — саме воно прибирає особливі точки", 11, GREY, "middle", "italic")
    save("fig-34-2-2.svg", s)


def fig_why4():
    """Рис. 34.2.3 — порівняння: кути Ейлера проти кватерніона."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Кути Ейлера проти кватерніона", 13.5, INK, "middle", "bold")

    x1, x2 = 360, 545
    s += text(x1, 64, "Кути Ейлера", 12.5, INK, "middle", "bold")
    s += text(x2, 64, "Кватерніон", 12.5, BLUE, "middle", "bold")
    rows = [
        ("скільки чисел", "3", "4  (|q| = 1)"),
        ("складання рамок", "є — фатальне", "немає"),
        ("плавна інтерполяція", "стрибки, кривий шлях", "slerp — рівно"),
        ("обчислення", "тригонометрія", "множення, стабільно"),
        ("наочність для людини", "висока", "низька"),
    ]
    y = 96
    for name, a, b in rows:
        s += text(60, y, name, 11.5, INK, "start")
        good_a = name == "наочність для людини"
        s += text(x1, y, a, 11, GREEN if good_a else RED, "middle",
                  "bold" if good_a else "normal")
        bad_b = name == "наочність для людини"
        s += text(x2, y, b, 11, RED if bad_b else GREEN, "middle",
                  "normal" if bad_b else "bold")
        s += line(48, y + 10, 660, y + 10, FAINT, 1)
        y += 38
    s += line((x1 + x2) / 2 - 92, 78, (x1 + x2) / 2 - 92, y - 18, FAINT, 1)
    save("fig-34-2-3.svg", s)


def fig_nolock():
    """Рис. 34.2.4 — через полюс: Ейлер стрибає, кватерніон неперервний (q порахований)."""
    w, h = 720, 322
    s = header(w, h)
    s += text(w / 2, 24, "Перекидка через зеніт: поганий опис ламається, добрий — ні", 13, INK, "middle", "bold")

    # TOP — Euler
    x0, y0, pw, ph = 96, 150, 540, 78
    s += axes(x0, y0, pw, ph)
    s += text(x0 - 6, y0 - ph - 4, "кути Ейлера", 11, INK, "end", "bold")
    # pitch rising 0..1 (0..180) green
    s += _plot_path(x0, y0, pw, ph, [(t / 100, 0.1 + 0.8 * (t / 100)) for t in range(101)], GREEN, 2.4)
    s += text(x0 + pw + 4, y0 - 0.9 * ph, "θ тангаж", 10, GREEN, "start")
    # yaw flat then jump at pole (t=0.5)
    s += _plot_path(x0, y0, pw, ph, [(t / 100, 0.16) for t in range(0, 50)], RED, 2.6)
    s += _plot_path(x0, y0, pw, ph, [(t / 100, 0.84) for t in range(50, 101)], RED, 2.6)
    s += line(x0 + 0.5 * pw, y0 - 0.16 * ph, x0 + 0.5 * pw, y0 - 0.84 * ph, RED, 1.6, dash="4 4")
    s += text(x0 + 0.5 * pw + 6, y0 - 0.52 * ph, "ψ стрибає 180°", 10, RED, "start", "bold")
    s += line(x0 + 0.5 * pw, y0, x0 + 0.5 * pw, y0 - ph, GREY, 1, dash="2 3")
    s += text(x0 + 0.5 * pw, y0 + 14, "полюс (90°)", 9.5, GREY, "middle")

    # BOTTOM — quaternion (computed)
    x0b, y0b, phb = 96, 300, 78
    s += axes(x0b, y0b, pw, phb)
    s += text(x0b - 6, y0b - phb - 4, "кватерніон", 11, BLUE, "end", "bold")
    wq = [(t / 100, 0.1 + 0.8 * math.cos((math.pi * t / 100) / 2)) for t in range(101)]
    yq = [(t / 100, 0.1 + 0.8 * math.sin((math.pi * t / 100) / 2)) for t in range(101)]
    s += _plot_path(x0b, y0b, pw, phb, wq, PURP, 2.4)
    s += _plot_path(x0b, y0b, pw, phb, yq, GREEN, 2.4)
    s += _plot_path(x0b, y0b, pw, phb, [(t / 100, 0.1) for t in range(101)], GREY, 1.8)
    s += text(x0b + pw + 4, y0b - 0.86 * phb, "w", 10, PURP, "start", "bold")
    s += text(x0b + pw + 4, y0b - 0.5 * phb, "y", 10, GREEN, "start", "bold")
    s += text(x0b + pw + 4, y0b - 0.12 * phb, "x,z", 9.5, GREY, "start")
    s += text(x0b + 0.5 * pw, y0b + 14, "усі складові неперервні", 10, GREEN, "middle", "bold")
    save("fig-34-2-4.svg", s)


def fig_slerp():
    """Рис. 34.2.5 — slerp: найкоротша дуга між двома орієнтаціями."""
    w, h = 720, 296
    s = header(w, h)
    s += text(w / 2, 26, "Slerp: плавний перехід найкоротшою дугою", 13.5, INK, "middle", "bold")
    cx, cy, r = 360, 162, 116
    s += circle(cx, cy, r, fill="#fbfbff", stroke=FAINT, w=2)

    aA, aB = math.radians(202), math.radians(338)
    A = (cx + r * math.cos(aA), cy + r * math.sin(aA))
    B = (cx + r * math.cos(aB), cy + r * math.sin(aB))
    s += line(cx, cy, A[0], A[1], GREY, 1.6)
    s += line(cx, cy, B[0], B[1], GREY, 1.6)
    s += dot(A[0], A[1], 6, INK)
    s += dot(B[0], B[1], 6, INK)
    s += text(A[0] - 8, A[1] + 18, "A", 13, INK, "middle", "bold")
    s += text(B[0] + 10, B[1] + 18, "B", 13, INK, "middle", "bold")

    # short arc (green) with steps
    short = []
    for i in range(41):
        a = aA + (aB - aA) * i / 40
        short.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    s += poly(short, GREEN, 3)
    for i in range(1, 8):
        a = aA + (aB - aA) * i / 8
        s += dot(cx + r * math.cos(a), cy + r * math.sin(a), 4, GREEN)
    # long way (faint)
    longp = []
    for i in range(61):
        a = aA - (2 * math.pi - (aB - aA)) * i / 60
        longp.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    s += poly(longp, GREY, 1.4, dash="5 5")

    s += text(cx, cy + 70, "найкоротша дуга — рівно, без ривків", 11, GREEN, "middle", "bold")
    s += text(cx, cy - 70, "(кожна точка кола — орієнтація)", 10, GREY, "middle", "italic")
    s += text(580, 250, "змішування кутів Ейлера", 10, GREY, "middle")
    s += text(580, 264, "дало б кривий шлях →", 10, GREY, "middle")
    save("fig-34-2-5.svg", s)


def fig_unitcover():
    """Рис. 34.2.6 — одинична норма й подвійне покриття (q ≡ −q)."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "Дві дрібниці: норма |q| = 1 і подвійне покриття q ≡ −q", 13, INK, "middle", "bold")
    cx, cy, r = 232, 158, 100
    s += circle(cx, cy, r, fill="#fbfbff", stroke=INK, w=1.8)
    s += text(cx, cy + r + 22, "одинична сфера |q| = 1", 11, INK, "middle")

    # q and -q antipodal
    aq = math.radians(-40)
    q = (cx + r * math.cos(aq), cy + r * math.sin(aq))
    mq = (cx - r * math.cos(aq), cy - r * math.sin(aq))
    s += arrow(cx, cy, q[0], q[1], BLUE, 2.6)
    s += arrow(cx, cy, mq[0], mq[1], BLUE, 2.2, dash="5 4")
    s += text(q[0] + 8, q[1] + 4, "q", 13, BLUE, "start", "bold")
    s += text(mq[0] - 8, mq[1] - 4, "−q", 13, BLUE, "end", "bold")
    s += text(cx, cy - r - 10, "q і −q — той самий поворот", 10.5, BLUE, "middle", "bold")

    # drifted vector pulled back
    ad = math.radians(70)
    dft = (cx + 1.28 * r * math.cos(ad), cy + 1.28 * r * math.sin(ad))
    onc = (cx + r * math.cos(ad), cy + r * math.sin(ad))
    s += dot(dft[0], dft[1], 5, RED)
    s += arrow(dft[0], dft[1], onc[0], onc[1], RED, 2.2)
    s += text(dft[0] + 6, dft[1] - 4, "похибка", 9.5, RED, "start")
    s += text(dft[0] + 6, dft[1] + 10, "→ нормуй", 9.5, RED, "start", "bold")

    # right text
    s += rect(404, 84, 286, 150, fill="#f6f4ec", stroke=FAINT, sw=1.5, rx=8)
    s += text(420, 116, "|q| = √(w²+x²+y²+z²) = 1", 12.5, INK, "start", "bold")
    s += text(420, 150, "скласти повороти:  q₂ ⊗ q₁", 12, INK, "start")
    s += text(420, 178, "(не комутує — порядок важливий)", 10, GREY, "start")
    s += text(420, 206, "повернути вектор:  q · v · q⁻¹", 12, INK, "start")
    save("fig-34-2-6.svg", s)


def fig_qpipeline():
    """Рис. 34.2.7 — кватерніон усередині, кути Ейлера назовні для людини."""
    w, h = 720, 240
    s = header(w, h)
    s += text(w / 2, 24, "Конвеєр орієнтації: кватерніон усередині, кути — для людини", 13, INK, "middle", "bold")

    sensors = ["гіроскоп", "акселерометр", "магнітометр"]
    for i, nm in enumerate(sensors):
        y = 62 + i * 46
        s += rect(40, y, 124, 34, fill="#fbf3f3", stroke=INK, sw=1.5, rx=5)
        s += text(102, y + 22, nm, 11, INK, "middle")
        s += arrow(164, y + 17, 236, 120, INK, 1.8)

    s += rect(236, 92, 178, 56, fill="#eef3fb", stroke=BLUE, sw=2.2, rx=8)
    s += text(325, 116, "Оцінювач", 13, BLUE, "middle", "bold")
    s += text(325, 134, "орієнтація = кватерніон q", 10.5, INK, "middle")

    # output: control
    s += arrow(414, 110, 520, 88, GREEN, 2.2)
    s += rect(520, 66, 168, 40, fill="#eef7ee", stroke=GREEN, sw=2, rx=6)
    s += text(604, 90, "Керування (стабілізація)", 10.5, INK, "middle", "bold")

    # output: euler for display
    s += arrow(414, 134, 470, 168, INK, 2.2)
    s += rect(470, 158, 120, 38, fill="#ffffff", stroke=INK, sw=1.8, rx=6)
    s += text(530, 176, "→ крен/тангаж", 10, INK, "middle")
    s += text(530, 190, "/рискання", 10, INK, "middle")
    s += arrow(590, 177, 626, 177, INK, 2)
    s += text(656, 174, "людині", 10.5, GREY, "middle", "bold")
    s += text(656, 190, "дисплей/лог", 9, GREY, "middle")
    save("fig-34-2-7.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.3 Комплементарний фільтр (реальна рекурсія фільтра на синтетичному сигналі)
# ════════════════════════════════════════════════════════════════════════════

CF_T, CF_N, CF_DRIFT = 4.0, 240, 3.0
CF_VMIN, CF_VMAX = -32.0, 40.0


def _cf_nz(t):
    return 3.4 * (math.sin(31 * t) + 0.7 * math.sin(57 * t + 1.0) + 0.5 * math.sin(91 * t + 2.0)) / 2.2


def _cf_true(t):
    return 22.0 * math.sin(1.15 * t)


def _cf_rate(t):
    return 22.0 * 1.15 * math.cos(1.15 * t)


def _cf_series(alpha, drift=CF_DRIFT, T=CF_T, N=CF_N):
    dt = T / N
    ang = 0.0
    out = []
    for i in range(N + 1):
        t = i * dt
        true = _cf_true(t)
        accel = true + _cf_nz(t)
        gyro = true + drift * t
        if i == 0:
            ang = accel
        else:
            rate = _cf_rate(t) + drift
            ang = alpha * (ang + rate * dt) + (1 - alpha) * accel
        out.append((t, true, gyro, accel, ang))
    return out


def _cf_uv(v):
    return (v - CF_VMIN) / (CF_VMAX - CF_VMIN)


def _cf_curve(series, idx):
    return [(r[0] / CF_T, _cf_uv(r[idx])) for r in series]


def fig_cf_motiv():
    """Рис. 34.3.1 — дзеркальні вади: гіроскоп дрейфує, акселерометр шумить."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Чому потрібні обидва давачі", 13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 76, 248, 580, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    s += text(x0 - 6, y0 - ph - 6, "кут", 11, INK, "end")
    ser = _cf_series(0.98)
    s += _plot_path(x0, y0, pw, ph, _cf_curve(ser, 1), GREY, 2.0, dash="6 4")
    s += _plot_path(x0, y0, pw, ph, _cf_curve(ser, 3), RED, 1.6)
    s += _plot_path(x0, y0, pw, ph, _cf_curve(ser, 2), BLUE, 2.4)
    s += line(x0 + 16, 56, x0 + 44, 56, GREY, 2.4, dash="6 4")
    s += text(x0 + 50, 60, "справжній кут", 10.5, GREY, "start")
    s += line(x0 + 200, 56, x0 + 228, 56, BLUE, 2.4)
    s += text(x0 + 234, 60, "гіроскоп: дрейф (повільна вада)", 10.5, BLUE, "start", "bold")
    s += line(x0 + 16, 74, x0 + 44, 74, RED, 2.4)
    s += text(x0 + 50, 78, "акселерометр: шум (швидка вада)", 10.5, RED, "start", "bold")
    save("fig-34-3-1.svg", s)


def fig_cf_split():
    """Рис. 34.3.2 — поділ за частотою."""
    w, h = 720, 232
    s = header(w, h)
    s += text(w / 2, 26, "Поділити сигнал за частотою — кожному давачу своє", 13.5, INK, "middle", "bold")
    x0, y0, pw = 80, 150, 560
    fc = x0 + 0.42 * pw
    s += rect(x0, y0 - 56, fc - x0, 56, fill="#fbeeee", stroke="none")
    s += rect(fc, y0 - 56, x0 + pw - fc, 56, fill="#eef1fb", stroke="none")
    s += arrow(x0, y0, x0 + pw + 10, y0, INK, 2)
    s += text(x0 + pw + 14, y0 + 4, "частота", 11, INK, "start")
    s += line(fc, y0 + 8, fc, y0 - 70, INK, 1.6, dash="4 4")
    s += text(fc, y0 - 78, "межа  f_c = 1/τ", 11, INK, "middle", "bold")
    s += text((x0 + fc) / 2, y0 - 24, "НИЗЬКІ частоти", 12, RED, "middle", "bold")
    s += text((x0 + fc) / 2, y0 + 26, "акселерометр", 11, RED, "middle", "bold")
    s += text((x0 + fc) / 2, y0 + 42, "правда, без дрейфу", 10, GREY, "middle")
    s += text((fc + x0 + pw) / 2, y0 - 24, "ВИСОКІ частоти", 12, BLUE, "middle", "bold")
    s += text((fc + x0 + pw) / 2, y0 + 26, "гіроскоп", 11, BLUE, "middle", "bold")
    s += text((fc + x0 + pw) / 2, y0 + 42, "швидкі рухи, без шуму", 10, GREY, "middle")
    save("fig-34-3-2.svg", s)


def fig_cf_sum():
    """Рис. 34.3.3 — ФВЧ + ФНЧ = 1 (обчислені першопорядкові відгуки)."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Чому «комплементарний»: ФВЧ + ФНЧ = 1", 13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 84, 234, 560, 168
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "частота", 11, INK, "middle")
    s += text(x0 - 6, y0 - ph - 6, "підсилення", 11, INK, "end")
    gmax = 1.15
    xc = 0.30
    lp, hp = [], []
    for i in range(201):
        xv = i / 200.0
        u = (xv / xc) if xc else 0
        L = 1.0 / math.sqrt(1 + u * u)
        H = u / math.sqrt(1 + u * u)
        lp.append((xv, L / gmax))
        hp.append((xv, H / gmax))
    s += line(x0, y0 - (1.0 / gmax) * ph, x0 + pw, y0 - (1.0 / gmax) * ph, GREEN, 2.6)
    s += text(x0 + pw - 4, y0 - (1.0 / gmax) * ph - 6, "сума = 1", 11, GREEN, "end", "bold")
    s += _plot_path(x0, y0, pw, ph, lp, RED, 2.4)
    s += _plot_path(x0, y0, pw, ph, hp, BLUE, 2.4)
    s += line(x0 + xc * pw, y0, x0 + xc * pw, y0 - ph, GREY, 1, dash="3 3")
    s += text(x0 + xc * pw, y0 + 14, "f_c", 10.5, GREY, "middle")
    s += dot(x0 + xc * pw, y0 - (0.707 / gmax) * ph, 3.5, INK)
    s += text(x0 + xc * pw + 8, y0 - (0.707 / gmax) * ph - 4, "−3 дБ", 9.5, INK, "start")
    s += text(x0 + 0.13 * pw, y0 - 0.86 * ph, "ФНЧ (акс.)", 10.5, RED, "middle", "bold")
    s += text(x0 + 0.74 * pw, y0 - 0.86 * ph, "ФВЧ (гіро)", 10.5, BLUE, "middle", "bold")
    save("fig-34-3-3.svg", s)


def fig_cf_block():
    """Рис. 34.3.4 — потік даних: інтеграл гіро + atan2 акс → зважена сума."""
    w, h = 720, 252
    s = header(w, h)
    s += text(w / 2, 24, "Один рядок коду: передбачення гіро + опора акселерометра", 13, INK, "middle", "bold")

    s += rect(40, 70, 110, 36, fill="#eef1fb", stroke=INK, sw=1.6, rx=5)
    s += text(95, 92, "гіроскоп ω", 11, INK, "middle")
    s += arrow(150, 88, 196, 88, INK, 2)
    s += rect(196, 66, 150, 44, fill="#ffffff", stroke=BLUE, sw=2, rx=6)
    s += text(271, 86, "кут + ω·dt", 11.5, INK, "middle", "bold")
    s += text(271, 102, "(ФВЧ · швидке)", 9.5, BLUE, "middle")

    s += rect(40, 158, 110, 36, fill="#fbf3f3", stroke=INK, sw=1.6, rx=5)
    s += text(95, 180, "акселер. a", 11, INK, "middle")
    s += arrow(150, 176, 196, 176, INK, 2)
    s += rect(196, 154, 150, 44, fill="#ffffff", stroke=RED, sw=2, rx=6)
    s += text(271, 174, "atan2(a_y,a_z)", 11.5, INK, "middle", "bold")
    s += text(271, 190, "(ФНЧ · повільне)", 9.5, RED, "middle")

    sj = (440, 132)
    s += circle(sj[0], sj[1], 20, fill="#ffffff", stroke=INK, w=2)
    s += text(sj[0], sj[1] + 6, "Σ", 18, INK, "middle", "bold")
    s += arrow(346, 88, sj[0] - 14, sj[1] - 10, BLUE, 2)
    s += text(395, 96, "α", 13, BLUE, "middle", "bold")
    s += arrow(346, 176, sj[0] - 14, sj[1] + 10, RED, 2)
    s += text(395, 172, "1−α", 12, RED, "middle", "bold")

    s += arrow(sj[0] + 20, sj[1], 560, sj[1], GREEN, 2.4)
    s += rect(560, 110, 120, 44, fill="#eef7ee", stroke=GREEN, sw=2, rx=6)
    s += text(620, 137, "кут (оцінка)", 11.5, INK, "middle", "bold")

    # feedback of estimate into the gyro-integrate block
    s += line(620, 154, 620, 224, INK, 1.6, dash="5 4")
    s += line(620, 224, 271, 224, INK, 1.6, dash="5 4")
    s += arrow(271, 224, 271, 110, INK, 1.6, dash="5 4")
    s += text(430, 240, "попередня оцінка повертається у передбачення", 10, GREY, "middle", "italic")
    save("fig-34-3-4.svg", s)


def fig_cf_result():
    """Рис. 34.3.5 — злита оцінка: гладка й без дрейфу (реальний фільтр)."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Результат злиття: гладко, як гіро, і без дрейфу, як акселерометр", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 76, 248, 580, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    s += text(x0 - 6, y0 - ph - 6, "кут", 11, INK, "end")
    ser = _cf_series(0.98)
    s += _plot_path(x0, y0, pw, ph, _cf_curve(ser, 2), BLUE, 1.3)
    s += _plot_path(x0, y0, pw, ph, _cf_curve(ser, 3), RED, 1.3)
    s += _plot_path(x0, y0, pw, ph, _cf_curve(ser, 1), GREY, 1.8, dash="6 4")
    s += _plot_path(x0, y0, pw, ph, _cf_curve(ser, 4), GREEN, 3.0)
    s += line(x0 + 16, 56, x0 + 44, 56, GREEN, 3)
    s += text(x0 + 50, 60, "злита оцінка (комплементарний фільтр)", 10.5, GREEN, "start", "bold")
    s += text(x0 + 360, 60, "— гіро    — акс    -- правда", 9.5, GREY, "start")
    save("fig-34-3-5.svg", s)


def fig_cf_alpha():
    """Рис. 34.3.6 — вибір α: компроміс дрейф ↔ шум (три прогони фільтра)."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Налаштування α: гладкість проти швидкості реакції", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 76, 248, 580, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    s += _plot_path(x0, y0, pw, ph, _cf_curve(_cf_series(0.98), 1), GREY, 1.8, dash="6 4")
    s += _plot_path(x0, y0, pw, ph, _cf_curve(_cf_series(0.995), 4), BLUE, 2.2)
    s += _plot_path(x0, y0, pw, ph, _cf_curve(_cf_series(0.90), 4), RED, 1.8)
    s += _plot_path(x0, y0, pw, ph, _cf_curve(_cf_series(0.98), 4), GREEN, 2.6)
    s += line(x0 + 16, 56, x0 + 44, 56, BLUE, 2.2)
    s += text(x0 + 50, 60, "α=0.995: гладко, але дрейф/мляво", 10, BLUE, "start", "bold")
    s += line(x0 + 16, 74, x0 + 44, 74, RED, 2.2)
    s += text(x0 + 50, 78, "α=0.90: швидко, але шумно", 10, RED, "start", "bold")
    s += line(x0 + 330, 56, x0 + 358, 56, GREEN, 2.6)
    s += text(x0 + 364, 60, "α=0.98: збалансовано", 10, GREEN, "start", "bold")
    save("fig-34-3-6.svg", s)


def fig_cf_limits():
    """Рис. 34.3.7 — тривале прискорення відхиляє «низ» акселерометра."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "Слабке місце: акселерометр плутає прискорення з нахилом", 12.5, INK, "middle", "bold")

    # rest
    cx1, cy1 = 200, 150
    s += rect(cx1 - 40, cy1 - 26, 80, 52, fill="#eef1fb", stroke=INK, sw=1.6, rx=5)
    s += arrow(cx1, cy1, cx1, cy1 + 78, GREEN, 3)
    s += text(cx1 + 8, cy1 + 70, "g", 12, GREEN, "start", "bold")
    s += text(cx1, 80, "Спокій", 12, INK, "middle", "bold")
    s += text(cx1, cy1 + 100, "«низ» правильний", 10.5, GREEN, "middle")

    # accelerating
    cx2, cy2 = 500, 150
    s += rect(cx2 - 40, cy2 - 26, 80, 52, fill="#eef1fb", stroke=INK, sw=1.6, rx=5)
    s += arrow(cx2, cy2, cx2, cy2 + 78, GREEN, 2.2)
    s += text(cx2 - 14, cy2 + 70, "g", 11, GREEN, "end", "bold")
    s += arrow(cx2, cy2, cx2 + 70, cy2, BLUE, 2.4)
    s += text(cx2 + 60, cy2 - 8, "a (розгін)", 11, BLUE, "middle", "bold")
    s += arrow(cx2, cy2, cx2 + 66, cy2 + 74, RED, 3)
    s += text(cx2 + 74, cy2 + 78, "g + a", 11, RED, "start", "bold")
    s += text(cx2, 80, "Розгін", 12, INK, "middle", "bold")
    s += text(cx2 + 20, cy2 + 104, "виміряний «низ» відхилений → кут бреше", 10, RED, "middle", "bold")

    s += text(w / 2, h - 10,
              "короткі поштовхи згладжуються; тривале прискорення фільтр від нахилу не відрізнить · рискання теж не видно",
              10, GREY, "middle", "italic")
    save("fig-34-3-7.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.4 Ідея фільтра Калмана (справжні гаусіани й скалярна рекурсія KF)
# ════════════════════════════════════════════════════════════════════════════

def _gauss(x, mu, sig):
    return math.exp(-((x - mu) ** 2) / (2 * sig * sig)) / (sig * math.sqrt(2 * math.pi))


def _fill_under(x0, y0, pw, ph, pts_norm, fill):
    scr = [_pt(x0, y0, pw, ph, xv, uv) for (xv, uv) in pts_norm]
    scr = scr + [(x0 + pw, y0), (x0, y0)]
    return polygon(scr, fill=fill, stroke="none")


def fig_kf_fuse():
    """Рис. 34.4.1 — дві гаусіани зливаються у вужчу (точнішу) третю."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Серце Калмана: два неточні джерела дають точнішу оцінку", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 560, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "кут", 11, INK, "middle")
    xmin, xmax, n = -22.0, 22.0, 180
    mu1, s1 = -6.0, 4.5
    mu2, s2 = 6.0, 3.0
    iv = 1 / (s1 * s1) + 1 / (s2 * s2)
    sf = math.sqrt(1 / iv)
    muf = (mu1 / (s1 * s1) + mu2 / (s2 * s2)) / iv
    hmax = _gauss(muf, muf, sf)

    def pts(mu, sg):
        return [(i / n, 0.86 * _gauss(xmin + (xmax - xmin) * i / n, mu, sg) / hmax) for i in range(n + 1)]

    s += _fill_under(x0, y0, pw, ph, pts(muf, sf), "#e7f4e7")
    s += _plot_path(x0, y0, pw, ph, pts(mu1, s1), BLUE, 2.4)
    s += _plot_path(x0, y0, pw, ph, pts(mu2, s2), RED, 2.4)
    s += _plot_path(x0, y0, pw, ph, pts(muf, sf), GREEN, 3.0)
    s += line(x0 + 26, 52, x0 + 52, 52, BLUE, 2.4)
    s += text(x0 + 58, 56, "передбачення (ширше — менш певне)", 10.5, BLUE, "start", "bold")
    s += line(x0 + 26, 70, x0 + 52, 70, RED, 2.4)
    s += text(x0 + 58, 74, "вимір", 10.5, RED, "start", "bold")
    s += line(x0 + 200, 70, x0 + 226, 70, GREEN, 3)
    s += text(x0 + 232, 74, "злите: вужче за обидва = точніше", 10.5, GREEN, "start", "bold")
    save("fig-34-4-1.svg", s)


def fig_kf_cycle():
    """Рис. 34.4.2 — цикл передбачення ⇄ оновлення."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Фільтр Калмана працює циклом із двох кроків", 13.5, INK, "middle", "bold")
    s += rect(120, 92, 184, 78, fill="#eef1fb", stroke=BLUE, sw=2.2, rx=10)
    s += text(212, 122, "ПЕРЕДБАЧЕННЯ", 12.5, BLUE, "middle", "bold")
    s += text(212, 142, "модель (гіроскоп):", 10, INK, "middle")
    s += text(212, 158, "+ зсув,  + невпевненість", 10, RED, "middle")
    s += rect(420, 92, 184, 78, fill="#eef7ee", stroke=GREEN, sw=2.2, rx=10)
    s += text(512, 122, "ОНОВЛЕННЯ", 12.5, GREEN, "middle", "bold")
    s += text(512, 142, "вимір (акселерометр):", 10, INK, "middle")
    s += text(512, 158, "+ корекція,  − невпевненість", 10, GREEN, "middle")
    s += arc_arrow(362, 131, 60, 192, 348, INK, 2.2)
    s += arc_arrow(362, 131, 60, 12, 168, INK, 2.2)
    s += text(362, 86, "оцінка вперед", 9.5, GREY, "middle")
    s += text(362, 188, "виправлена оцінка", 9.5, GREY, "middle")
    s += text(w / 2, h - 14, "десятки разів на секунду", 10.5, GREY, "middle", "italic")
    save("fig-34-4-2.svg", s)


def fig_kf_predupd():
    """Рис. 34.4.3 — передбачення розширює дзвін, оновлення звужує."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Невпевненість «дихає»: ширшає на передбаченні, вужчає на вимірі", 12, INK, "middle", "bold")

    def bell(x0, y0, pw, ph, muf, sig, peak, col, ww=2.4, dash=None):
        pp = [(i / 120, peak * math.exp(-((i / 120 - muf) ** 2) / (2 * sig * sig))) for i in range(121)]
        return _plot_path(x0, y0, pw, ph, pp, col, ww, dash=dash)

    # left panel: predict
    s += text(185, 56, "ПЕРЕДБАЧЕННЯ", 12, BLUE, "middle", "bold")
    s += axes(60, 230, 250, 150)
    s += bell(60, 230, 250, 150, 0.32, 0.07, 0.9, BLUE)
    s += bell(60, 230, 250, 150, 0.6, 0.13, 0.62, BLUE, 2.2, dash="5 4")
    s += arrow(60 + 0.40 * 250, 230 - 0.95 * 150, 60 + 0.52 * 250, 230 - 0.66 * 150, INK, 1.8)
    s += text(185, 250, "зсув + ширшає", 10.5, BLUE, "middle", "bold")

    # right panel: update
    s += text(540, 56, "ОНОВЛЕННЯ", 12, GREEN, "middle", "bold")
    s += axes(410, 230, 250, 150)
    s += bell(410, 230, 250, 150, 0.42, 0.13, 0.6, BLUE, 2.2, dash="5 4")
    s += bell(410, 230, 250, 150, 0.66, 0.10, 0.78, RED, 2.2)
    s += bell(410, 230, 250, 150, 0.56, 0.07, 0.95, GREEN, 3.0)
    s += text(540, 250, "вимір стягує → вужчає", 10.5, GREEN, "middle", "bold")
    s += text(470, 80, "пріор", 9, BLUE, "middle")
    s += text(600, 80, "вимір", 9, RED, "middle")
    s += text(540, 96, "підсумок", 9, GREEN, "middle", "bold")
    save("fig-34-4-3.svg", s)


def fig_kf_gain():
    """Рис. 34.4.4 — коефіцієнт K = P/(P+R) як адаптивна довіра."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Коефіцієнт Калмана K — адаптивна довіра до виміру (1−α)", 13.5, INK, "middle", "bold")
    x0, y0, pw, ph = 96, 234, 540, 168
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "невпевненість виміру R", 10.5, INK, "middle")
    s += text(x0 - 6, y0 - ph - 6, "K", 12, INK, "end", "bold")
    P = 1.0
    Rmax = 6.0
    pts = [(i / 200, P / (P + (i / 200) * Rmax)) for i in range(201)]
    s += _plot_path(x0, y0, pw, ph, pts, GREEN, 2.8)
    s += line(x0, y0 - ph, x0 + pw, y0 - ph, FAINT, 1)
    s += text(x0 + 0.5, y0 - ph - 2, "1", 10, GREY, "end")
    s += text(x0 + 0.12 * pw, y0 - 0.86 * ph, "малий R → K≈1", 10.5, GREEN, "start", "bold")
    s += text(x0 + 0.12 * pw, y0 - 0.72 * ph, "(вір виміру)", 9.5, GREY, "start")
    s += text(x0 + 0.62 * pw, y0 - 0.22 * ph, "великий R → K≈0", 10.5, RED, "start", "bold")
    s += text(x0 + 0.62 * pw, y0 - 0.10 * ph, "(вір передбаченню)", 9.5, GREY, "start")
    save("fig-34-4-4.svg", s)


def fig_kf_converge():
    """Рис. 34.4.5 — K сам збігається (проти фіксованого α)."""
    w, h = 720, 286
    s = header(w, h)
    s += text(w / 2, 24, "Калман самоналаштовується: K збігається сам", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 96, 230, 540, 162
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "крок", 11, INK, "middle")
    s += text(x0 - 6, y0 - ph - 6, "K", 12, INK, "end", "bold")
    Q, R, P = 0.05, 1.0, 6.0
    Ks = []
    M = 30
    for k in range(M + 1):
        P = P + Q
        K = P / (P + R)
        P = (1 - K) * P
        Ks.append(K)
    kmax = max(Ks) * 1.1
    pts = [(k / M, Ks[k] / kmax) for k in range(M + 1)]
    s += line(x0, y0 - (0.22 / kmax) * ph, x0 + pw, y0 - (0.22 / kmax) * ph, GREY, 2.0, dash="6 4")
    s += text(x0 + pw - 4, y0 - (0.22 / kmax) * ph - 6, "фіксоване (1−α): комплементарний", 10, GREY, "end")
    s += _plot_path(x0, y0, pw, ph, pts, GREEN, 2.8)
    for k in [0, 4, 10, 20, 30]:
        s += dot(x0 + (k / M) * pw, y0 - (Ks[k] / kmax) * ph, 3.2, GREEN)
    s += text(x0 + 0.06 * pw, y0 - (Ks[0] / kmax) * ph - 10, "старт: невпевнено → K високе", 10, GREEN, "start", "bold")
    s += text(x0 + 0.5 * pw, y0 - (Ks[-1] / kmax) * ph - 12, "усталилося", 10, GREEN, "start", "bold")
    save("fig-34-4-5.svg", s)


def _kf_run(Q, R, P0):
    dt = CF_T / CF_N
    x, P = 0.0, P0
    out = []
    for i in range(CF_N + 1):
        t = i * dt
        true = _cf_true(t)
        meas = true + _cf_nz(t)
        if i == 0:
            x = meas
        else:
            x = x + (_cf_rate(t) + CF_DRIFT) * dt
            P = P + Q
            K = P / (P + R)
            x = x + K * (meas - x)
            P = (1 - K) * P
        out.append((t, true, meas, x, math.sqrt(P)))
    return out


def fig_kf_run():
    """Рис. 34.4.6 — оцінка Калмана з коридором ±σ, що звужується."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Калман видає кут І його невпевненість (коридор ±σ)", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 76, 250, 580, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    ser = _kf_run(0.6, 10.0, 60.0)
    up = [(r[0] / CF_T, _cf_uv(r[3] + 2.2 * r[4])) for r in ser]
    dn = [(r[0] / CF_T, _cf_uv(r[3] - 2.2 * r[4])) for r in ser]
    band = [_pt(x0, y0, pw, ph, xv, uv) for (xv, uv) in up] + \
           [_pt(x0, y0, pw, ph, xv, uv) for (xv, uv) in reversed(dn)]
    s += polygon(band, fill="#e7f4e7", stroke="none")
    s += _plot_path(x0, y0, pw, ph, [(r[0] / CF_T, _cf_uv(r[2])) for r in ser], RED, 1.2)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / CF_T, _cf_uv(r[1])) for r in ser], GREY, 1.8, dash="6 4")
    s += _plot_path(x0, y0, pw, ph, [(r[0] / CF_T, _cf_uv(r[3])) for r in ser], GREEN, 3.0)
    s += line(x0 + 20, 52, x0 + 46, 52, GREEN, 3)
    s += text(x0 + 52, 56, "оцінка Калмана", 10.5, GREEN, "start", "bold")
    s += text(x0 + 200, 56, "затінено — коридор ±σ (звужується)", 10, GREEN, "start")
    s += text(x0 + 200, 72, "-- правда    — вимір", 9.5, GREY, "start")
    save("fig-34-4-6.svg", s)


def fig_kf_state():
    """Рис. 34.4.7 — стан [кут, зсув нуля]; predict з гіро, correct з акс/маг; EKF."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 24, "Калман для орієнтації: оцінює й кут, і зсув нуля гіроскопа", 12.5, INK, "middle", "bold")

    s += rect(40, 80, 116, 40, fill="#eef1fb", stroke=INK, sw=1.6, rx=5)
    s += text(98, 104, "гіроскоп", 11, INK, "middle")
    s += arrow(156, 100, 214, 116, BLUE, 2)
    s += rect(214, 92, 150, 56, fill="#eef1fb", stroke=BLUE, sw=2, rx=8)
    s += text(289, 112, "ПЕРЕДБАЧЕННЯ", 10.5, BLUE, "middle", "bold")
    s += text(289, 130, "стан = [кут, зсув]", 10, INK, "middle")

    s += rect(40, 168, 116, 40, fill="#fbf3f3", stroke=INK, sw=1.6, rx=5)
    s += text(98, 192, "акс. + маг.", 10.5, INK, "middle")
    s += arrow(156, 188, 214, 150, RED, 2)
    s += rect(396, 92, 150, 56, fill="#eef7ee", stroke=GREEN, sw=2, rx=8)
    s += text(471, 112, "ОНОВЛЕННЯ", 10.5, GREEN, "middle", "bold")
    s += text(471, 130, "коефіцієнт K", 10, INK, "middle")
    s += arrow(364, 120, 396, 120, INK, 2)

    s += arrow(546, 120, 600, 120, GREEN, 2.2)
    s += rect(600, 96, 96, 48, fill="#ffffff", stroke=GREEN, sw=2, rx=6)
    s += text(648, 116, "кут", 11, INK, "middle", "bold")
    s += text(648, 132, "± σ", 10, GREY, "middle")

    # feedback loop
    s += line(471, 148, 471, 224, INK, 1.6, dash="5 4")
    s += line(471, 224, 289, 224, INK, 1.6, dash="5 4")
    s += arrow(289, 224, 289, 148, INK, 1.6, dash="5 4")
    s += text(380, 240, "оцінка повертається у передбачення", 9.5, GREY, "middle", "italic")
    s += text(648, 162, "нелінійно", 9.5, PURP, "middle", "bold")
    s += text(648, 176, "→ EKF", 9.5, PURP, "middle", "bold")
    save("fig-34-4-7.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.4 ІСТОРІЯ — фільтр Калмана й «Аполлон» (Рис. 34.4·H.k)
# ════════════════════════════════════════════════════════════════════════════

def _star(cx, cy, r, color=GOLD):
    out = ""
    for a in range(0, 360, 45):
        rr = r if a % 90 == 0 else r * 0.45
        x = cx + rr * math.cos(math.radians(a))
        y = cy + rr * math.sin(math.radians(a))
        out += f"{x:.1f},{y:.1f} "
    return f'<polygon points="{out.strip()}" fill="{color}" stroke="none"/>\n'


def fig_kfh_wiener():
    """Рис. 34.4·H.1 — Вінер (вся історія) проти Калмана (лише поточна оцінка)."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 26, "Чому Вінера було замало для борту", 13.5, INK, "middle", "bold")
    s += line(360, 56, 360, 280, FAINT, 1.5)

    # left: Wiener
    s += text(180, 60, "Фільтр Вінера", 12.5, INK, "middle", "bold")
    for i in range(6):
        y = 92 + i * 26
        s += rect(56, y, 44, 18, fill="#eef1fb", stroke=INK, sw=1.2)
        s += arrow(100, y + 9, 196, 150, BLUE, 1.4)
    s += rect(196, 120, 118, 60, fill="#eef1fb", stroke=BLUE, sw=2, rx=6)
    s += text(255, 146, "обробка", 11.5, INK, "middle", "bold")
    s += text(255, 164, "усієї історії", 10, INK, "middle")
    s += text(180, 268, "потрібна вся історія + стала статистика", 10, GREY, "middle")
    s += text(82, 84, "минулі виміри", 9.5, GREY, "middle")

    # right: Kalman
    s += text(540, 60, "Фільтр Калмана", 12.5, BLUE, "middle", "bold")
    s += rect(486, 120, 118, 60, fill="#eef7ee", stroke=GREEN, sw=2, rx=8)
    s += text(545, 145, "x, P", 14, INK, "middle", "bold")
    s += text(545, 165, "тільки зараз", 9.5, GREEN, "middle")
    s += arrow(420, 150, 486, 150, RED, 2)
    s += text(440, 142, "вимір", 9.5, RED, "middle")
    s += arrow(604, 150, 668, 150, GREEN, 2)
    s += text(648, 142, "оцінка", 9.5, GREEN, "middle")
    s += arc_arrow(545, 150, 44, 200, 340, INK, 1.8)
    s += text(545, 92, "передбач. ⇄ оновл.", 9.5, INK, "middle")
    s += text(540, 268, "лише поточна оцінка та її невпевненість", 10, GREY, "middle")
    save("fig-34-s4h-1-wiener-vs-kalman.svg", s)


def fig_kfh_recursive():
    """Рис. 34.4·H.2 — рекурсія тримає лише (x, P); минуле відкинуто."""
    w, h = 720, 268
    s = header(w, h)
    s += text(w / 2, 26, "Прорив Калмана: рекурсія — минуле стиснуте у два числа", 13, INK, "middle", "bold")

    # discarded past
    for i in range(5):
        s += rect(48, 70 + i * 22, 40, 15, fill="#f0f0f0", stroke=GREY, sw=1)
    s += text(68, 176, "минуле —", 10, GREY, "middle")
    s += text(68, 190, "відкинуто", 10, RED, "middle", "bold")
    s += text(68, 60, "✗", 16, RED, "middle", "bold")

    # memory cell
    s += rect(300, 110, 130, 60, fill="#eef7ee", stroke=GREEN, sw=2.4, rx=8)
    s += text(365, 134, "стан x", 12, INK, "middle", "bold")
    s += text(365, 154, "невпевненість P", 10.5, INK, "middle")

    # measurement in
    s += arrow(150, 140, 300, 140, RED, 2.2)
    s += text(220, 132, "новий вимір", 10, RED, "middle", "bold")

    # predict/update loop
    s += arc_arrow(365, 140, 70, 200, 345, BLUE, 2)
    s += text(365, 56, "ПЕРЕДБАЧЕННЯ", 10, BLUE, "middle", "bold")
    s += arc_arrow(365, 140, 70, 15, 160, GREEN, 2)
    s += text(365, 232, "ОНОВЛЕННЯ", 10, GREEN, "middle", "bold")

    # output
    s += arrow(430, 140, 560, 140, GREEN, 2.2)
    s += rect(560, 118, 110, 44, fill="#ffffff", stroke=GREEN, sw=2, rx=6)
    s += text(615, 145, "оцінка", 11.5, INK, "middle", "bold")
    save("fig-34-s4h-2-recursive-memory.svg", s)


def fig_kfh_parallel():
    """Рис. 34.4·H.3 — паралельні відкриття по обидва боки залізної завіси."""
    w, h = 720, 320
    s = header(w, h)
    s += text(w / 2, 26, "Естафета, а не самотній геній", 13.5, INK, "middle", "bold")
    x0, pw, ymid = 80, 580, 178
    s += arrow(x0 - 10, ymid, x0 + pw + 14, ymid, INK, 2)
    s += text(x0 + pw + 18, ymid + 4, "рік", 10.5, INK, "start")

    def xof(yr):
        return x0 + (yr - 1875) / (1965 - 1875) * pw
    for yr in (1880, 1900, 1920, 1940, 1960):
        s += line(xof(yr), ymid - 4, xof(yr), ymid + 4, INK, 1.4)
        s += text(xof(yr), ymid + 20, str(yr), 9.5, GREY, "middle")

    s += text(x0 - 6, 70, "Захід", 11, BLUE, "start", "bold")
    s += text(x0 - 6, 296, "СРСР", 11, PURP, "start", "bold")

    west = [(1880, "Тіле (Данія)", -96), (1942, "Вінер", -60), (1958, "Сверлінг", -96),
            (1960, "КАЛМАН", -36), (1961, "Б'юсі · Шмідт (EKF)", -66)]
    ussr = [(1941, "Колмогоров", 60), (1946, "Крейн (Одеса)", 96), (1960, "Стратонович", 60)]
    for yr, nm, dy in west:
        x = xof(yr)
        s += line(x, ymid, x, ymid + dy, BLUE, 1.4, dash="3 3")
        s += dot(x, ymid, 4, BLUE)
        s += dot(x, ymid + dy, 4, BLUE)
        bold = "bold" if "КАЛМАН" in nm else "normal"
        s += text(x, ymid + dy - 6, nm, 9.5, BLUE, "middle", bold)
    for yr, nm, dy in ussr:
        x = xof(yr)
        s += line(x, ymid, x, ymid + dy, PURP, 1.4, dash="3 3")
        s += dot(x, ymid, 4, PURP)
        s += dot(x, ymid + dy, 4, PURP)
        s += text(x, ymid + dy + 14, nm, 9.5, PURP, "middle")
    s += text(w / 2, h - 12, "Холодна війна тримала світи нарізно — одну ідею знаходили знову й знову",
              10.5, GREY, "middle", "italic")
    save("fig-34-s4h-3-parallel-discovery.svg", s)


def fig_kfh_resistance():
    """Рис. 34.4·H.4 — спротив рецензентів; стаття вийшла в журналі з механіки."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Геніальний метод ледь не загубився між дисциплінами", 13, INK, "middle", "bold")

    # EE reject
    s += rect(60, 86, 150, 90, fill="#fbf3f3", stroke=RED, sw=2, rx=8)
    s += text(135, 112, "Електротехніка", 11.5, INK, "middle", "bold")
    s += text(135, 132, "(звикла до Вінера)", 9.5, GREY, "middle")
    s += text(135, 158, "✗ скепсис", 13, RED, "middle", "bold")

    # paper
    s += rect(300, 92, 120, 78, fill="#ffffff", stroke=INK, sw=2, rx=4)
    s += text(360, 120, "стаття", 11, INK, "middle", "bold")
    s += text(360, 138, "Калмана", 11, INK, "middle", "bold")
    s += text(360, 156, "1960", 10, GREY, "middle")
    s += arrow(210, 131, 300, 131, RED, 2, dash="5 4")

    # ME accept
    s += arrow(420, 131, 510, 131, GREEN, 2.2)
    s += rect(510, 86, 158, 90, fill="#eef7ee", stroke=GREEN, sw=2, rx=8)
    s += text(589, 112, "Журнал з", 11.5, INK, "middle", "bold")
    s += text(589, 128, "машинобудування", 11.5, INK, "middle", "bold")
    s += text(589, 156, "✓ прийнято", 12.5, GREEN, "middle", "bold")
    s += text(w / 2, h - 14, "проривні ідеї часто виживають завдяки свіжому погляду збоку",
              10.5, GREY, "middle", "italic")
    save("fig-34-s4h-4-resistance.svg", s)


def fig_kfh_apollo():
    """Рис. 34.4·H.5 — навігація «Аполлона»: IMU-передбачення + зоряні візування."""
    w, h = 720, 320
    s = header(w, h)
    s += text(w / 2, 26, "Фільтр Калмана веде «Аполлон»", 13.5, INK, "middle", "bold")

    # spacecraft (simple capsule)
    cx, cy = 360, 188
    s += polygon([(cx - 26, cy + 20), (cx + 26, cy + 20), (cx + 16, cy - 22),
                  (cx - 16, cy - 22)], fill="#dce4f2", stroke=INK, sw=1.8)
    s += polygon([(cx - 16, cy - 22), (cx + 16, cy - 22), (cx, cy - 40)], fill="#cfd6e6", stroke=INK, sw=1.6)
    s += text(cx, cy + 40, "«Аполлон»", 10.5, INK, "middle", "bold")

    # predict box (left)
    s += rect(44, 150, 168, 64, fill="#eef1fb", stroke=BLUE, sw=2, rx=8)
    s += text(128, 174, "ПЕРЕДБАЧЕННЯ", 10.5, BLUE, "middle", "bold")
    s += text(128, 192, "IMU + небесна механіка", 9.3, INK, "middle")
    s += arrow(212, 184, cx - 30, 184, BLUE, 2.2)

    # measurement (top): star + sextant
    s += _star(560, 74, 16)
    s += text(560, 56, "зорі", 9.5, GOLD, "middle", "bold")
    s += rect(470, 92, 180, 50, fill="#fbf3f3", stroke=RED, sw=2, rx=8)
    s += text(560, 112, "ОНОВЛЕННЯ", 10.5, RED, "middle", "bold")
    s += text(560, 130, "секстант: візування зір", 9.3, INK, "middle")
    s += arrow(520, 142, cx + 18, cy - 36, RED, 2.2)

    # filter → state
    s += arrow(cx + 28, cy + 4, 600, 230, GREEN, 2.2)
    s += rect(520, 222, 168, 56, fill="#eef7ee", stroke=GREEN, sw=2, rx=8)
    s += text(604, 246, "EKF → стан", 11, INK, "middle", "bold")
    s += text(604, 264, "положення, швидкість", 9.3, INK, "middle")
    s += text(150, 252, "у кількадесят кілобайт пам'яті", 10, GREY, "middle", "italic")
    save("fig-34-s4h-5-apollo-nav.svg", s)


def fig_kfh_legacy():
    """Рис. 34.4·H.6 — спадок: від «Аполлона» до EKF у дроні."""
    w, h = 720, 210
    s = header(w, h)
    s += text(w / 2, 26, "Та сама математика — від Місяця до вашого дрона", 13, INK, "middle", "bold")
    cy = 118
    cx = [120, 300, 480, 645]

    # Apollo capsule
    s += polygon([(cx[0] - 22, cy + 16), (cx[0] + 22, cy + 16), (cx[0] + 13, cy - 16),
                  (cx[0] - 13, cy - 16)], fill="#dce4f2", stroke=INK, sw=1.6)
    s += text(cx[0], cy + 40, "«Аполлон»", 10, INK, "middle", "bold")
    s += text(cx[0], cy + 55, "1960-ті", 9, GREY, "middle")

    # airplane / GPS
    s += polygon(_plane_pts(cx[1], cy, 0.7, rot=90), fill="#dce4f2", stroke=INK, sw=1.4)
    s += text(cx[1], cy + 40, "авіація · GPS", 10, INK, "middle", "bold")

    # robot
    s += rect(cx[2] - 18, cy - 16, 36, 32, fill="#dce4f2", stroke=INK, sw=1.6, rx=4)
    s += circle(cx[2] - 9, cy - 4, 3, fill=INK, stroke="none")
    s += circle(cx[2] + 9, cy - 4, 3, fill=INK, stroke="none")
    s += text(cx[2], cy + 40, "робототехніка", 10, INK, "middle", "bold")

    # drone (EKF)
    s += line(cx[3] - 22, cy - 10, cx[3] + 22, cy + 10, INK, 2)
    s += line(cx[3] - 22, cy + 10, cx[3] + 22, cy - 10, INK, 2)
    for dxq, dyq in [(-22, -10), (22, -10), (-22, 10), (22, 10)]:
        s += circle(cx[3] + dxq, cy + dyq, 6, fill="none", stroke=BLUE, w=2)
    s += rect(cx[3] - 8, cy - 6, 16, 12, fill="#eef3fb", stroke=BLUE, sw=1.6)
    s += text(cx[3], cy + 40, "дрон · EKF", 10, BLUE, "middle", "bold")
    s += text(cx[3], cy + 55, "сьогодні", 9, GREY, "middle")

    for i in range(3):
        s += arrow(cx[i] + 40, cy, cx[i + 1] - 40, cy, INK, 2)
    s += text(w / 2, h - 10, "передбачення + вимір, зважені за певністю", 10.5, GREY, "middle", "italic")
    save("fig-34-s4h-6-moon-to-drone.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.5 Зворотний зв'язок: розімкнене vs замкнене (реальні симуляції об'єкта)
# ════════════════════════════════════════════════════════════════════════════

def _uvmap(v, vmin, vmax):
    return (v - vmin) / (vmax - vmin)


def _ctrl_box(x, y, w, ht, lab1, lab2, color, fill):
    s = rect(x, y, w, ht, fill=fill, stroke=color, sw=2, rx=7)
    s += text(x + w / 2, y + ht / 2 - 2, lab1, 11, INK, "middle", "bold")
    if lab2:
        s += text(x + w / 2, y + ht / 2 + 15, lab2, 9, GREY, "middle")
    return s


def fig_ol_open():
    """Рис. 34.5.1 — розімкнене керування: жодного шляху назад."""
    w, h = 720, 220
    s = header(w, h)
    s += text(w / 2, 30, "Розімкнене керування: діє за планом, не дивиться на результат",
              13, INK, "middle", "bold")
    y, ht = 96, 56
    s += arrow(40, y + ht / 2, 86, y + ht / 2, BLUE, 2.2)
    s += text(58, y + ht / 2 - 10, "завдання r", 10, BLUE, "middle", "bold")
    s += _ctrl_box(86, y, 132, ht, "Регулятор", None, INK, "#eef3fb")
    s += arrow(218, y + ht / 2, 262, y + ht / 2, INK, 2.2)
    s += _ctrl_box(262, y, 150, ht, "Виконавчий орган", None, INK, "#f6f4ec")
    s += arrow(412, y + ht / 2, 456, y + ht / 2, INK, 2.2)
    s += _ctrl_box(456, y, 132, ht, "Об'єкт", None, INK, "#eef7ee")
    s += arrow(588, y + ht / 2, 660, y + ht / 2, GREEN, 2.2)
    s += text(648, y + ht / 2 - 10, "вихід y", 10, GREEN, "middle", "bold")
    s += text(w / 2, 196, "немає шляху назад — система не знає, чи досягла мети", 11, RED, "middle", "bold")
    save("fig-34-5-1.svg", s)


def fig_ol_closed():
    """Рис. 34.5.2 — анатомія замкненого контуру з помилкою e = r − y."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Замкнений контур: міряти, порівняти, виправити", 13.5, INK, "middle", "bold")
    yc = 116
    sj = (150, yc)
    s += circle(sj[0], sj[1], 18, fill="#ffffff", stroke=INK, w=2)
    s += line(sj[0] - 9, sj[1], sj[0] + 9, sj[1], INK, 1.4)
    s += line(sj[0], sj[1] - 9, sj[0], sj[1] + 9, INK, 1.4)
    s += arrow(54, yc, sj[0] - 18, yc, BLUE, 2.2)
    s += text(56, yc - 10, "завдання r", 11, BLUE, "start", "bold")
    s += text(sj[0] - 26, yc + 30, "−", 16, RED, "middle", "bold")
    s += arrow(sj[0] + 18, yc, 246, yc, INK, 2.2)
    s += text(208, yc - 10, "помилка e = r − y", 11, RED, "middle", "bold")
    s += _ctrl_box(246, yc - 28, 120, 56, "Регулятор", None, BLUE, "#eef3fb")
    s += arrow(366, yc, 430, yc, INK, 2.2)
    s += text(398, yc - 9, "вплив u", 10, INK, "middle")
    s += _ctrl_box(430, yc - 28, 150, 56, "Об'єкт", "(мотор, нагрівач…)", INK, "#eef7ee")
    s += line(580, yc, 642, yc, INK, 2.2)
    s += arrow(642, yc, 642, yc - 40, GREEN, 2.2)
    s += text(642, yc - 48, "вихід y", 11, GREEN, "middle", "bold")
    s += dot(610, yc, 3.5, INK)
    s += line(610, yc, 610, 196, INK, 2)
    s += _ctrl_box(372, 178, 110, 36, "Давач", None, INK, "#fbf3f3")
    s += line(610, 196, 482, 196, INK, 2)
    s += arrow(372, 196, sj[0], 196, INK, 2)
    s += line(sj[0], 196, sj[0], yc + 18, INK, 2)
    s += text(w / 2, h - 12, "регулятор жене помилку e до нуля — машина підправляє себе сама",
              11, GREY, "middle", "italic")
    save("fig-34-5-2.svg", s)


def fig_ol_error():
    """Рис. 34.5.3 — помилка e = r − y у часі."""
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 24, "Помилка e = r − y — головна величина керування", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 84, 232, 560, 176
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    rr = 0.82
    s += line(x0, y0 - rr * ph, x0 + pw, y0 - rr * ph, GREY, 1.8, dash="6 4")
    s += text(x0 + pw + 4, y0 - rr * ph + 4, "завдання r", 10.5, GREY, "start")
    ypts = [(t / 100, rr * (1 - math.exp(-2.6 * t / 100 * 5))) for t in range(101)]
    s += _plot_path(x0, y0, pw, ph, ypts, BLUE, 2.6)
    s += text(x0 + pw + 4, y0 - 0.5 * ph, "вихід y", 10.5, BLUE, "start", "bold")
    # error gap at t*
    ts = 0.18
    ys = rr * (1 - math.exp(-2.6 * ts * 5))
    px = x0 + ts * pw
    s += line(px, y0 - ys * ph, px, y0 - rr * ph, RED, 2.6)
    s += text(px + 8, y0 - (ys + rr) / 2 * ph, "e = r − y", 11, RED, "start", "bold")
    s += text(x0 + 0.55 * pw, y0 - 0.55 * ph, "поки e ≠ 0 — регулятор працює", 10.5, INK, "start")
    save("fig-34-5-3.svg", s)


def _dist_series():
    a, dt, N, td, D, r, Kp = 2.0, 0.02, 250, 2.0, 0.8, 1.0, 6.0
    yo, yc = r, r
    out = []
    for k in range(N + 1):
        t = k * dt
        d = -D if t >= td else 0.0
        out.append((t, r, yo, yc))
        uo = r
        uc = r + Kp * (r - yc)
        yo = yo + dt * (a * (uo - yo) + d)
        yc = yc + dt * (a * (uc - yc) + d)
    return out


def fig_ol_disturb():
    """Рис. 34.5.4 — придушення збурення: розімкнене лишається збитим, замкнене вертається."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Збурення: замкнене вертається, розімкнене — ні", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 252, 580, 192
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = 0.45, 1.12
    ser = _dist_series()
    T = ser[-1][0]
    s += line(x0, y0 - _uvmap(1.0, vmin, vmax) * ph, x0 + pw, y0 - _uvmap(1.0, vmin, vmax) * ph,
              GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, y0 - _uvmap(1.0, vmin, vmax) * ph + 4, "завдання", 10, GREY, "start")
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(r[2], vmin, vmax)) for r in ser], RED, 2.6)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(r[3], vmin, vmax)) for r in ser], GREEN, 2.6)
    xd = x0 + (2.0 / T) * pw
    s += arrow(xd, y0 - ph - 2, xd, y0 - _uvmap(0.95, vmin, vmax) * ph, INK, 1.8)
    s += text(xd, y0 - ph - 8, "збурення", 10, INK, "middle", "bold")
    s += line(x0 + 24, 60, x0 + 50, 60, GREEN, 2.6)
    s += text(x0 + 56, 64, "замкнене — вернулося до завдання", 10.5, GREEN, "start", "bold")
    s += line(x0 + 24, 78, x0 + 50, 78, RED, 2.6)
    s += text(x0 + 56, 82, "розімкнене — лишилося збитим", 10.5, RED, "start", "bold")
    save("fig-34-5-4.svg", s)


def fig_ol_driving():
    """Рис. 34.5.5 — кермування: розімкнене з'їжджає, замкнене тримає смугу."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Кермо як контур: дивитися на дорогу — і виправлятися", 12.5, INK, "middle", "bold")

    def lane(yc, title, color):
        out = text(70, yc - 44, title, 11.5, color, "start", "bold")
        out += line(70, yc - 30, 650, yc - 30, FAINT, 6)
        out += line(70, yc + 30, 650, yc + 30, FAINT, 6)
        out += line(70, yc, 650, yc, GREY, 1, dash="10 8")
        return out

    yc1 = 110
    s += lane(yc1, "Розімкнено: кермо застигле", RED)
    drift = [(70 + i * 5.8, yc1 - 18 + (i * 5.8) ** 1.7 * 0.0016) for i in range(100)]
    s += poly(drift, RED, 2.6)
    s += rect(drift[-1][0] - 8, drift[-1][1] - 5, 16, 10, fill="#fbdada", stroke=RED, sw=1.4)
    s += text(600, yc1 + 50, "→ з'їхав зі смуги", 10, RED, "middle", "bold")

    yc2 = 232
    s += lane(yc2, "Замкнено: дивиться й виправляє", GREEN)
    wig = [(70 + i * 5.8, yc2 + 9 * math.sin(i / 7.0) * math.exp(-i / 120.0)) for i in range(100)]
    s += poly(wig, GREEN, 2.6)
    s += rect(wig[-1][0] - 8, wig[-1][1] - 5, 16, 10, fill="#daf0da", stroke=GREEN, sw=1.4)
    s += text(600, yc2 + 50, "→ тримається смуги", 10, GREEN, "middle", "bold")
    save("fig-34-5-5.svg", s)


def _instab_series(Kp):
    a, b, dt, N = 1.0, 1.2, 0.02, 400
    y, v = 0.0, 0.0
    out = []
    for k in range(N + 1):
        t = k * dt
        r = 0.0 if t < 0.4 else 1.0
        out.append((t, r, y))
        u = r + Kp * (r - y)
        v = v + dt * (a * (u - y) - b * v)
        y = y + dt * v
    return out


def fig_ol_instab():
    """Рис. 34.5.6 — м'який регулятор повзе, різкий розгойдується (другий порядок)."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Чому замало «діяти проти помилки»: дозування вирішує", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 580, 192
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = -0.25, 1.85
    g = _instab_series(1.0)
    ag = _instab_series(14.0)
    T = g[-1][0]
    s += line(x0, y0 - _uvmap(1.0, vmin, vmax) * ph, x0 + pw, y0 - _uvmap(1.0, vmin, vmax) * ph,
              GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, y0 - _uvmap(1.0, vmin, vmax) * ph + 4, "завдання", 10, GREY, "start")
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in ag], RED, 2.4)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in g], GREEN, 2.6)
    s += line(x0 + 24, 60, x0 + 50, 60, GREEN, 2.6)
    s += text(x0 + 56, 64, "м'який регулятор — спокійно підходить", 10.5, GREEN, "start", "bold")
    s += line(x0 + 24, 78, x0 + 50, 78, RED, 2.4)
    s += text(x0 + 56, 82, "надто різкий — розгойдується", 10.5, RED, "start", "bold")
    save("fig-34-5-6.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.6 Пропорційний регулятор P (реальний об'єкт 2-го порядку, чисте u = Kp·e)
# ════════════════════════════════════════════════════════════════════════════

def _p_series(Kp, a=1.0, b=0.7, dt=0.02, N=500):
    y, v = 0.0, 0.0
    out = []
    for k in range(N + 1):
        t = k * dt
        r = 0.0 if t < 0.4 else 1.0
        out.append((t, r, y))
        u = Kp * (r - y)
        v = v + dt * (a * (u - y) - b * v)
        y = y + dt * v
    return out


def fig_p_law():
    """Рис. 34.6.1 — пропорційний закон u = Kp·e (пряма через нуль)."""
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Пропорційний закон: u = Kp · e", 13.5, INK, "middle", "bold")
    ox, oy = 360, 150
    s += arrow(ox - 250, oy, ox + 250, oy, INK, 1.8)
    s += arrow(ox, oy + 92, ox, oy - 92, INK, 1.8)
    s += text(ox + 250, oy + 18, "помилка e", 11, INK, "middle")
    s += text(ox + 40, oy - 86, "вплив u", 11, INK, "middle")
    Kp = 0.62
    s += line(ox - 230, oy + Kp * 230, ox + 230, oy - Kp * 230, BLUE, 3)
    s += text(ox + 170, oy - Kp * 230 + 4, "нахил = Kp", 11, BLUE, "start", "bold")
    # sample point
    ex = 150
    s += line(ox + ex, oy, ox + ex, oy - Kp * ex, GREY, 1.4, dash="4 3")
    s += line(ox, oy - Kp * ex, ox + ex, oy - Kp * ex, GREY, 1.4, dash="4 3")
    s += dot(ox + ex, oy - Kp * ex, 4, RED)
    s += text(ox + 130, oy + 36, "велика помилка → велика дія", 10, INK, "middle")
    s += text(ox - 130, oy - 40, "помилка в один бік —", 9.5, GREY, "middle")
    s += text(ox - 130, oy - 26, "дія в той самий", 9.5, GREY, "middle")
    save("fig-34-6-1.svg", s)


def fig_p_spring():
    """Рис. 34.6.2 — P як пружина: тягне пропорційно відхиленню."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "P — це «пружина» до завдання", 13.5, INK, "middle", "bold")

    def spring(x0, y, x1, coils=8):
        out = ""
        pts = [(x0, y)]
        for i in range(coils * 2 + 1):
            xx = x0 + (x1 - x0) * (i + 1) / (coils * 2 + 2)
            yy = y + (12 if i % 2 == 0 else -12)
            pts.append((xx, yy))
        pts.append((x1, y))
        return poly(pts, INK, 1.8)

    # target wall
    for yc, ex, lab in [(96, 150, "велика помилка → сильна тяга"), (188, 60, "мала помилка → слабка тяга")]:
        s += line(120, yc - 28, 120, yc + 28, INK, 3)
        s += text(120, yc - 34, "ціль", 9.5, GREY, "middle")
        s += spring(120, yc, 120 + ex)
        s += rect(120 + ex, yc - 16, 32, 32, fill="#dce4f2", stroke=INK, sw=1.6, rx=3)
        s += arrow(120 + ex, yc, 120 + ex - min(ex * 0.5, 70), yc, RED, 3)
        s += text(120 + ex + 60, yc + 4, lab, 10, INK, "start")
        s += text(120 + ex + 16, yc - 24, "F = Kp·e", 9, RED, "middle", "bold")
    save("fig-34-6-2.svg", s)


def fig_p_kp():
    """Рис. 34.6.3 — вплив Kp: малий повільно, великий перестрілює."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Вплив Kp на відгук пропорційного регулятора", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 252, 580, 196
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = -0.08, 1.42
    T = _p_series(1)[-1][0]
    s += line(x0, y0 - _uvmap(1.0, vmin, vmax) * ph, x0 + pw, y0 - _uvmap(1.0, vmin, vmax) * ph,
              GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, y0 - _uvmap(1.0, vmin, vmax) * ph + 4, "завдання", 10, GREY, "start")
    for Kp, col, lab in [(0.7, GREEN, "малий Kp — повільно + великий зсув"),
                         (3.0, BLUE, "середній Kp — добрий баланс"),
                         (10.0, RED, "великий Kp — перестрілює, коливається")]:
        ser = _p_series(Kp)
        s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in ser], col, 2.4)
    s += line(x0 + 22, 58, x0 + 48, 58, GREEN, 2.4)
    s += text(x0 + 54, 62, "Kp = 0.7", 10, GREEN, "start", "bold")
    s += line(x0 + 22, 76, x0 + 48, 76, BLUE, 2.4)
    s += text(x0 + 54, 80, "Kp = 3", 10, BLUE, "start", "bold")
    s += line(x0 + 200, 58, x0 + 226, 58, RED, 2.4)
    s += text(x0 + 232, 62, "Kp = 10", 10, RED, "start", "bold")
    save("fig-34-6-3.svg", s)


def fig_p_offset():
    """Рис. 34.6.4 — сталий зсув: вихід застигає нижче завдання."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Сталий зсув: P завжди «недотягує» до завдання", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 246, 560, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = 0.0, 1.12
    T = _p_series(1)[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.8, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    for Kp, col in [(3.0, GREEN), (10.0, BLUE)]:
        ser = _p_series(Kp)
        s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in ser], col, 2.4)
        yss = ser[-1][2]
        yp = y0 - _uvmap(yss, vmin, vmax) * ph
        s += line(x0 + pw - 40, yr, x0 + pw - 40, yp, col, 2.4)
        s += text(x0 + pw - 34, (yr + yp) / 2 + 3, f"e_ss (Kp={int(Kp)})", 9.5, col, "start", "bold")
    s += text(x0 + 0.4 * pw, yr - 0.5 * ph, "більший Kp → менший зсув,", 10.5, INK, "start")
    s += text(x0 + 0.4 * pw, yr - 0.5 * ph + 16, "та НІКОЛИ не нуль", 10.5, RED, "start", "bold")
    save("fig-34-6-4.svg", s)


def fig_p_why():
    """Рис. 34.6.5 — чому зсув неминучий: щоб тримати u₀, треба e ≠ 0."""
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 26, "Чому зсув неминучий", 13.5, INK, "middle", "bold")

    # object held against load
    cx, cy = 200, 150
    s += rect(cx - 34, cy - 24, 68, 48, fill="#dce4f2", stroke=INK, sw=1.8, rx=4)
    s += text(cx, cy + 2, "об'єкт", 10.5, INK, "middle", "bold")
    s += arrow(cx, cy + 24, cx, cy + 78, RED, 3)
    s += text(cx + 8, cy + 70, "навантаження", 10, RED, "start", "bold")
    s += text(cx + 8, cy + 84, "(вага, тертя)", 9, GREY, "start")
    s += arrow(cx, cy - 24, cx, cy - 78, GREEN, 3)
    s += text(cx + 8, cy - 70, "вплив u₀", 10, GREEN, "start", "bold")
    s += text(cx + 8, cy - 56, "(щоб утримати)", 9, GREY, "start")

    s += arrow(280, cy, 380, cy, INK, 2)
    s += rect(390, 96, 300, 108, fill="#f6f4ec", stroke=INK, sw=1.6, rx=8)
    s += text(540, 124, "P дає вплив ТІЛЬКИ з помилки:", 11, INK, "middle", "bold")
    s += text(540, 148, "u = Kp · e", 14, BLUE, "middle", "bold")
    s += text(540, 174, "щоб u = u₀  →  e_ss = u₀ / Kp ≠ 0", 11.5, RED, "middle", "bold")
    s += text(540, 194, "помилку не прибрати, лише зменшити", 9.5, GREY, "middle")
    save("fig-34-6-5.svg", s)


def fig_p_bridge():
    """Рис. 34.6.6 — P лишає зсув; інтегральна складова (§34.7) його прибере."""
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 24, "Місток до §34.7: автоматизувати «скидач»", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 240, 560, 184
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = 0.0, 1.12
    T = _p_series(1)[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.8, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    ser = _p_series(3.0)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in ser], BLUE, 2.6)
    yss = ser[-1][2]
    yp = y0 - _uvmap(yss, vmin, vmax) * ph
    s += line(x0 + 0.62 * pw, yr, x0 + 0.62 * pw, yp, RED, 2.4)
    s += text(x0 + 0.63 * pw + 4, (yr + yp) / 2 + 3, "сталий зсув (P)", 10, RED, "start", "bold")
    # illustrative I-corrected curve reaching setpoint
    icurve = []
    for r in ser:
        t = r[0]
        base = _clamp(r[2], vmin, vmax)
        if t > 1.2:
            base = base + (1.0 - yss) * (1 - math.exp(-(t - 1.2) * 1.1))
        icurve.append((t / T, _uvmap(_clamp(base, vmin, vmax), vmin, vmax)))
    s += _plot_path(x0, y0, pw, ph, icurve, GREEN, 2.2, dash="6 4")
    s += text(x0 + 0.5 * pw, yr - 0.16 * ph, "з інтегральною (§34.7) → зсув зникає", 10, GREEN, "start", "bold")
    s += line(x0 + 22, 58, x0 + 48, 58, BLUE, 2.6)
    s += text(x0 + 54, 62, "лише P", 10, BLUE, "start", "bold")
    save("fig-34-6-6.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.7 Інтегральна складова I (реальний P+I із насиченням і антивіндапом)
# ════════════════════════════════════════════════════════════════════════════

def _pi_series(Kp, Ki, sat=None, aw=False, a=1.0, b=0.7, dt=0.02, N=600):
    y, v, I = 0.0, 0.0, 0.0
    out = []
    for k in range(N + 1):
        t = k * dt
        r = 0.0 if t < 0.4 else 1.0
        e = r - y
        I += e * dt
        u = Kp * e + Ki * I
        if sat is not None and abs(u) > sat:
            if aw:
                I -= e * dt
                u = _clamp(Kp * e + Ki * I, -sat, sat)
            else:
                u = _clamp(u, -sat, sat)
        v = v + dt * (a * (u - y) - b * v)
        y = y + dt * v
        out.append((t, r, y, e, I, u))
    return out


def fig_i_accumulate():
    """Рис. 34.7.1 — інтеграл = площа під кривою помилки."""
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 24, "Інтегральна складова накопичує площу під помилкою", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 84, 232, 560, 184
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    s += text(x0 - 6, y0 - ph - 6, "помилка e", 11, INK, "end")
    pts = [(t / 200, (0.72 * math.exp(-1.0 * (t / 200) * 5) + 0.14)) for t in range(201)]
    s += _fill_under(x0, y0, pw, ph, [(xv, uv) for (xv, uv) in pts], "#fbe4e1")
    s += _plot_path(x0, y0, pw, ph, pts, RED, 2.6)
    s += text(x0 + 0.45 * pw, y0 - 0.34 * ph, "∫ e dt", 16, RED, "middle", "bold")
    s += text(x0 + 0.45 * pw, y0 - 0.2 * ph, "(накопичена площа)", 10, GREY, "middle")
    s += text(x0 + 0.62 * pw, y0 - 0.22 * ph, "навіть малий стійкий", 9.5, INK, "start")
    s += text(x0 + 0.62 * pw, y0 - 0.13 * ph, "зсув усе накопичується →", 9.5, INK, "start")
    save("fig-34-7-1.svg", s)


def fig_i_offset():
    """Рис. 34.7.2 — P лишає зсув, P+I доводить точно до завдання."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Інтеграл прибирає сталий зсув повністю", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 246, 560, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = 0.0, 1.12
    T = _p_series(1)[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.8, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    sp = _p_series(3.0)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in sp], BLUE, 2.4)
    pi = _pi_series(3.0, 2.0)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in pi], GREEN, 2.6)
    yss = sp[-1][2]
    yp = y0 - _uvmap(yss, vmin, vmax) * ph
    s += line(x0 + 0.5 * pw, yr, x0 + 0.5 * pw, yp, RED, 2.0)
    s += text(x0 + 0.51 * pw, (yr + yp) / 2 + 3, "зсув (лише P)", 9.5, RED, "start", "bold")
    s += line(x0 + 22, 60, x0 + 48, 60, BLUE, 2.4)
    s += text(x0 + 54, 64, "лише P — застигає нижче", 10, BLUE, "start", "bold")
    s += line(x0 + 22, 78, x0 + 48, 78, GREEN, 2.6)
    s += text(x0 + 54, 82, "P + I — точно на завданні", 10, GREEN, "start", "bold")
    save("fig-34-7-2.svg", s)


def fig_i_work():
    """Рис. 34.7.3 — інтеграл росте, поки є помилка, і застигає в нулі."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Накопичувач росте, поки є помилка, тоді застигає", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 246, 560, 188
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    pi = _pi_series(3.0, 2.0)
    T = pi[-1][0]
    epeak = max(abs(r[3]) for r in pi) or 1.0
    Ifin = pi[-1][4] or 1.0
    s += line(x0, y0 - 0.04 * ph, x0 + pw, y0 - 0.04 * ph, FAINT, 1.4)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, 0.04 + 0.78 * _clamp(r[3] / epeak, -0.05, 1)) for r in pi], RED, 2.4)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, 0.04 + 0.82 * _clamp(r[4] / Ifin, 0, 1.1)) for r in pi], GREEN, 2.6)
    s += line(x0 + 22, 60, x0 + 48, 60, RED, 2.4)
    s += text(x0 + 54, 64, "помилка e — спадає до 0", 10, RED, "start", "bold")
    s += line(x0 + 22, 78, x0 + 48, 78, GREEN, 2.6)
    s += text(x0 + 54, 82, "накопичувач I — зростає, тоді застигає", 10, GREEN, "start", "bold")
    save("fig-34-7-3.svg", s)


def fig_i_ki():
    """Рис. 34.7.4 — вплив Ki: малий повільно, великий переганяє."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Вплив Ki: повільно прибирає зсув проти перельоту", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 580, 196
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = 0.0, 1.32
    T = _p_series(1)[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    for Ki, col, lab in [(0.8, GREEN, "малий Ki — повільно"),
                         (3.0, BLUE, "добрий Ki"),
                         (9.0, RED, "великий Ki — переліт + коливання")]:
        ser = _pi_series(2.0, Ki)
        s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in ser], col, 2.3)
    s += line(x0 + 22, 60, x0 + 48, 60, GREEN, 2.3)
    s += text(x0 + 54, 64, "Ki = 0.8", 10, GREEN, "start", "bold")
    s += line(x0 + 22, 78, x0 + 48, 78, BLUE, 2.3)
    s += text(x0 + 54, 82, "Ki = 3", 10, BLUE, "start", "bold")
    s += line(x0 + 200, 60, x0 + 226, 60, RED, 2.3)
    s += text(x0 + 232, 64, "Ki = 9", 10, RED, "start", "bold")
    save("fig-34-7-4.svg", s)


def fig_i_windup():
    """Рис. 34.7.5 — windup: за насичення інтеграл накручується → переліт."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 24, "Windup: інтеграл накручується за насичення — дикий переліт", 12, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 560, 196
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = -0.1, 2.0
    ser = _pi_series(1.8, 3.5, sat=1.3, aw=False)
    T = ser[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    Imax = max(r[4] for r in ser) or 1.0
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, 0.02 + 0.9 * _clamp(r[4] / Imax, 0, 1)) for r in ser], GREEN, 2.0, dash="6 4")
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in ser], RED, 2.6)
    s += line(x0 + 22, 58, x0 + 48, 58, RED, 2.6)
    s += text(x0 + 54, 62, "вихід y — величезний переліт", 10, RED, "start", "bold")
    s += line(x0 + 22, 76, x0 + 48, 76, GREEN, 2.0, dash="6 4")
    s += text(x0 + 54, 80, "інтеграл накрутився (потім розкручується)", 10, GREEN, "start", "bold")
    save("fig-34-7-5.svg", s)


def fig_i_antiwindup():
    """Рис. 34.7.6 — антивіндап: накручування спинене, переліт зникає."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Антивіндап: спинити накручування — і переліт зникає", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 246, 560, 192
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = -0.1, 2.0
    bad = _pi_series(1.8, 3.5, sat=1.3, aw=False)
    good = _pi_series(1.8, 3.5, sat=1.3, aw=True)
    T = bad[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in bad], RED, 2.3)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in good], GREEN, 2.6)
    s += line(x0 + 22, 60, x0 + 48, 60, RED, 2.3)
    s += text(x0 + 54, 64, "без антивіндапу — переліт", 10, RED, "start", "bold")
    s += line(x0 + 22, 78, x0 + 48, 78, GREEN, 2.6)
    s += text(x0 + 54, 82, "з антивіндапом — чисто на завдання", 10, GREEN, "start", "bold")
    save("fig-34-7-6.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.8 Диференційна складова D (повний PID; похідна від виміру; шум)
# ════════════════════════════════════════════════════════════════════════════

def _dnoise(t):
    return 0.5 * (math.sin(40 * t) + 0.6 * math.sin(83 * t + 1.0) + 0.4 * math.sin(127 * t + 2.0))


def _pid_series(Kp, Ki, Kd, sat=None, aw=False, dmeas=False, noise=0.0, a=1.0, b=0.7, dt=0.02, N=600):
    y, v, I = 0.0, 0.0, 0.0
    ep, ymp = None, None
    out = []
    for k in range(N + 1):
        t = k * dt
        r = 0.0 if t < 0.4 else 1.0
        ym = y + noise * _dnoise(t)
        e = r - ym
        I += e * dt
        if ep is None:
            ep, ymp = e, ym
        deriv = (-(ym - ymp) / dt) if dmeas else ((e - ep) / dt)
        u = Kp * e + Ki * I + Kd * deriv
        if sat is not None and abs(u) > sat:
            if aw:
                I -= e * dt
                u = _clamp(Kp * e + Ki * I + Kd * deriv, -sat, sat)
            else:
                u = _clamp(u, -sat, sat)
        v = v + dt * (a * (u - y) - b * v)
        y = y + dt * v
        out.append((t, r, y, e, I, u, Kd * deriv))
        ep, ymp = e, ym
    return out


def fig_d_slope():
    """Рис. 34.8.1 — D реагує на нахил кривої помилки."""
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 24, "Диференційна складова дивиться на нахил помилки", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 84, 232, 560, 184
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    s += text(x0 - 6, y0 - ph - 6, "помилка e", 11, INK, "end")
    pts = [(t / 200, math.exp(-1.7 * (t / 200) * 5) * 0.92 + 0.04) for t in range(201)]
    s += _plot_path(x0, y0, pw, ph, pts, RED, 2.6)

    def tangent(tt, lab, col):
        out = ""
        e = math.exp(-1.7 * tt * 5) * 0.92 + 0.04
        sl = -1.7 * 5 * math.exp(-1.7 * tt * 5) * 0.92
        dx = 0.1
        p0 = _pt(x0, y0, pw, ph, tt - dx, e - sl * dx)
        p1 = _pt(x0, y0, pw, ph, tt + dx, e + sl * dx)
        out += line(p0[0], p0[1], p1[0], p1[1], col, 2.4)
        px = _pt(x0, y0, pw, ph, tt, e)
        out += dot(px[0], px[1], 4, col)
        out += text(px[0], px[1] - 14, lab, 9.5, col, "middle", "bold")
        return out
    s += tangent(0.1, "крутий нахил → сильна D", BLUE)
    s += tangent(0.62, "пологий → слабка D", GREEN)
    save("fig-34-8-1.svg", s)


def fig_d_brake():
    """Рис. 34.8.2 — D як гальмо/демпфер: притримує швидкий підхід."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "D — це «гальмо»: притримує тим дужче, чим швидший підхід", 12.5, INK, "middle", "bold")
    yroad = 150
    s += line(80, yroad + 26, 660, yroad + 26, GREY, 3)
    s += line(600, yroad - 30, 600, yroad + 30, RED, 3)
    s += text(600, yroad - 38, "ціль (стоп)", 10, RED, "middle", "bold")
    # car
    s += rect(150, yroad - 2, 54, 26, fill="#dce4f2", stroke=INK, sw=1.8, rx=5)
    s += circle(166, yroad + 24, 7, fill="#eee", stroke=INK, w=1.6)
    s += circle(190, yroad + 24, 7, fill="#eee", stroke=INK, w=1.6)
    # decreasing speed arrows
    for i, (xx, ln) in enumerate([(230, 70), (330, 50), (430, 32), (510, 16)]):
        s += arrow(xx, yroad + 10, xx + ln, yroad + 10, BLUE, 2.2)
    s += text(330, yroad - 30, "швидкість спадає завчасно →", 10.5, BLUE, "middle", "bold")
    s += text(330, yroad + 56, "гальмує тим раніше, чим швидше підлітає — плавна зупинка без перельоту",
              10, GREY, "middle", "italic")
    save("fig-34-8-2.svg", s)


def fig_d_damp():
    """Рис. 34.8.3 — PI перестрілює, повний PID гасить коливання."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Диференційна складова гасить коливання", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 580, 196
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = -0.05, 1.5
    T = _pid_series(1, 0, 0)[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    pi = _pid_series(5.0, 3.0, 0.0)
    pid = _pid_series(5.0, 3.0, 1.6, dmeas=True)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in pi], RED, 2.3)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in pid], GREEN, 2.6)
    s += line(x0 + 22, 60, x0 + 48, 60, RED, 2.3)
    s += text(x0 + 54, 64, "PI — перестрілює, коливається", 10, RED, "start", "bold")
    s += line(x0 + 22, 78, x0 + 48, 78, GREEN, 2.6)
    s += text(x0 + 54, 82, "PID — плавно сідає на завдання", 10, GREEN, "start", "bold")
    save("fig-34-8-3.svg", s)


def fig_d_higherkp():
    """Рис. 34.8.4 — з D можна підняти Kp: швидко й стійко."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "З демпфером можна підняти Kp: швидкість + стійкість", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 580, 196
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = -0.25, 1.85
    T = _pid_series(1, 0, 0)[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    nod = _pid_series(12.0, 0.0, 0.0)
    wd = _pid_series(12.0, 0.0, 2.6, dmeas=True)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in nod], RED, 2.3)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in wd], GREEN, 2.6)
    s += line(x0 + 22, 60, x0 + 48, 60, RED, 2.3)
    s += text(x0 + 54, 64, "великий Kp без D — розгойдується", 10, RED, "start", "bold")
    s += line(x0 + 22, 78, x0 + 48, 78, GREEN, 2.6)
    s += text(x0 + 54, 82, "великий Kp + D — швидко й стійко", 10, GREEN, "start", "bold")
    save("fig-34-8-4.svg", s)


def fig_d_noise():
    """Рис. 34.8.5 — диференціювання шумного сигналу дає сплески."""
    w, h = 720, 320
    s = header(w, h)
    s += text(w / 2, 22, "Чому D небезпечний: похідна підсилює шум", 13, INK, "middle", "bold")
    N = 240
    dt = 1.0 / N * 4
    em = [(0.78 * math.exp(-1.2 * (i / N * 4)) + 0.1) + 0.05 * _dnoise(i / N * 4) for i in range(N + 1)]

    x0, ya, pw, pha = 84, 150, 560, 78
    s += axes(x0, ya, pw, pha)
    s += text(x0 - 6, ya - pha - 4, "помилка (з шумом)", 10, INK, "end")
    s += _plot_path(x0, ya, pw, pha, [(i / N, _clamp(em[i] * 0.9, 0, 1)) for i in range(N + 1)], RED, 2.0)

    x0b, yb, phb = 84, 300, 96
    s += axes(x0b, yb, pw, phb)
    s += text(x0b - 6, yb - phb - 4, "похідна", 10, INK, "end")
    s += line(x0b, yb - 0.5 * phb, x0b + pw, yb - 0.5 * phb, FAINT, 1)
    der = [0.0] + [(em[i] - em[i - 1]) / dt for i in range(1, N + 1)]
    clean = [-1.2 * 0.78 * math.exp(-1.2 * (i / N * 4)) for i in range(N + 1)]
    s += _plot_path(x0b, yb, pw, phb, [(i / N, _clamp(0.5 + clean[i] * 0.12, 0, 1)) for i in range(N + 1)], GREEN, 2.2)
    s += _plot_path(x0b, yb, pw, phb, [(i / N, _clamp(0.5 + der[i] * 0.012, 0, 1)) for i in range(N + 1)], RED, 1.3)
    s += text(x0b + 0.6 * pw, yb - 0.9 * phb, "сирий D — дикі сплески", 9.5, RED, "start", "bold")
    s += text(x0b + 0.6 * pw, yb - 0.34 * phb, "справжній нахил", 9.5, GREEN, "start", "bold")
    save("fig-34-8-5.svg", s)


def fig_d_kick():
    """Рис. 34.8.6 — похідний поштовх; ліки — похідна від виміру."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Похідний поштовх і ліки: похідна від виміру", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 200, 580, 150
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    s += text(x0 - 6, y0 - ph - 4, "D-член", 10, INK, "end")
    s += line(x0, y0 - 0.5 * ph, x0 + pw, y0 - 0.5 * ph, FAINT, 1)
    err = _pid_series(4.0, 0.0, 1.0, dmeas=False)
    meas = _pid_series(4.0, 0.0, 1.0, dmeas=True)
    T = err[-1][0]
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _clamp(0.5 + r[6] * 0.06, 0, 1)) for r in err], RED, 2.2)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _clamp(0.5 + r[6] * 0.06, 0, 1)) for r in meas], GREEN, 2.4)
    xk = x0 + (0.4 / T) * pw
    s += text(xk + 6, y0 - 0.92 * ph, "сплеск-поштовх", 10, RED, "start", "bold")
    s += line(x0 + 22, 56, x0 + 48, 56, RED, 2.2)
    s += text(x0 + 54, 60, "похідна від помилки — поштовх при зміні завдання", 9.5, RED, "start", "bold")
    s += line(x0 + 22, 74, x0 + 48, 74, GREEN, 2.4)
    s += text(x0 + 54, 78, "похідна від виміру — без поштовху", 9.5, GREEN, "start", "bold")
    save("fig-34-8-6.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.9 Дискретний ПІД на МК (керування з нульовим утриманням між тактами)
# ════════════════════════════════════════════════════════════════════════════

def _pid_rate(Kp, Ki, Kd, every, a=1.0, b=0.7, dt=0.01, T=8.0):
    y, v, I, u = 0.0, 0.0, 0.0, 0.0
    ep, ymp = None, None
    out = []
    N = int(T / dt)
    for k in range(N + 1):
        t = k * dt
        r = 0.0 if t < 0.4 else 1.0
        if k % every == 0:
            ym = y
            e = r - ym
            cdt = dt * every
            I += e * cdt
            if ep is None:
                ep, ymp = e, ym
            deriv = -(ym - ymp) / cdt
            u = Kp * e + Ki * I + Kd * deriv
            ep, ymp = e, ym
        v = v + dt * (a * (u - y) - b * v)
        y = y + dt * v
        out.append((t, r, y))
    return out


def fig_disc_sample():
    """Рис. 34.9.1 — інтеграл = сума прямокутників, похідна = різниця відліків."""
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 24, "Дискретизація: сума прямокутників і різниця відліків", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 84, 232, 560, 184
    M = 9
    for i in range(M):
        xv = i / M
        ev = 0.22 + 0.62 * math.exp(-1.5 * xv * 3)
        p0 = _pt(x0, y0, pw, ph, xv, 0)
        p1 = _pt(x0, y0, pw, ph, (i + 1) / M, ev)
        s += rect(p0[0], p1[1], p1[0] - p0[0], p0[1] - p1[1], fill="#eaf0fb", stroke="#cdd8ef", sw=1)
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    pts = [(t / 200, 0.22 + 0.62 * math.exp(-1.5 * (t / 200) * 3)) for t in range(201)]
    s += _plot_path(x0, y0, pw, ph, pts, RED, 2.6)
    for i in range(M + 1):
        xv = i / M
        ev = 0.22 + 0.62 * math.exp(-1.5 * xv * 3)
        px = _pt(x0, y0, pw, ph, xv, ev)
        s += dot(px[0], px[1], 3.4, INK)
    # secant (derivative) between two samples
    i = 2
    pa = _pt(x0, y0, pw, ph, i / M, 0.22 + 0.62 * math.exp(-1.5 * (i / M) * 3))
    pb = _pt(x0, y0, pw, ph, (i + 1) / M, 0.22 + 0.62 * math.exp(-1.5 * ((i + 1) / M) * 3))
    s += line(pa[0] - 18, pa[1] - 18 * (pb[1] - pa[1]) / (pb[0] - pa[0]),
              pb[0] + 18, pb[1] + 18 * (pb[1] - pa[1]) / (pb[0] - pa[0]), BLUE, 2.6)
    s += text(pb[0] + 30, pb[1] - 20, "похідна = нахил січної", 10, BLUE, "start", "bold")
    s += text(x0 + 0.62 * pw, y0 - 0.5 * ph, "інтеграл = Σ прямокутників e·Δt", 10.5, BLUE, "middle")
    save("fig-34-9-1.svg", s)


def fig_disc_tick():
    """Рис. 34.9.2 — один такт ПІД: потік від виміру до впливу."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Один такт регулятора (кожні Δt)", 13.5, INK, "middle", "bold")
    boxes = [("давач", "#fbf3f3"), ("e = r − y", "#ffffff"), ("I += e·Δt\n(затиск)", "#eef7ee"),
             ("D від виміру\n(фільтр)", "#eef3fb"), ("u = Σ", "#ffffff"),
             ("затиск u", "#f6f4ec"), ("вивід", "#eef7ee")]
    bw, gap, y, ht = 84, 8, 110, 50
    x = 26
    for i, (lab, fill) in enumerate(boxes):
        s += rect(x, y, bw, ht, fill=fill, stroke=INK, sw=1.6, rx=6)
        lines = lab.split("\n")
        for j, ln in enumerate(lines):
            s += text(x + bw / 2, y + ht / 2 + 5 + (j - (len(lines) - 1) / 2) * 13, ln, 10, INK, "middle",
                      "bold" if j == 0 else "normal")
        if i < len(boxes) - 1:
            s += arrow(x + bw, y + ht / 2, x + bw + gap, y + ht / 2, INK, 1.8)
        x += bw + gap
    s += text(w / 2, 196, "лічені множення й додавання — мікросекунди роботи", 11, GREY, "middle", "italic")
    save("fig-34-9-2.svg", s)


def fig_disc_rate():
    """Рис. 34.9.3 — часта дискретизація тримає, рідка псує (обчислено)."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Частота керування вирішує (той самий ПІД)", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 580, 196
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = -0.1, 1.6
    fast = _pid_rate(4.0, 2.0, 0.8, 1)
    slow = _pid_rate(4.0, 2.0, 0.8, 20)
    T = fast[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in slow], RED, 2.3)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in fast], GREEN, 2.6)
    s += line(x0 + 22, 60, x0 + 48, 60, GREEN, 2.6)
    s += text(x0 + 54, 64, "часто (100 Гц) — гладко й стійко", 10, GREEN, "start", "bold")
    s += line(x0 + 22, 78, x0 + 48, 78, RED, 2.3)
    s += text(x0 + 54, 82, "рідко (5 Гц) — переліт, розгойдування", 10, RED, "start", "bold")
    save("fig-34-9-3.svg", s)


def fig_disc_jitter():
    """Рис. 34.9.4 — рівномірні такти проти «плаваючих»."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 26, "Сталий крок Δt — передумова правильного ПІД", 13, INK, "middle", "bold")

    def timeline(yc, ticks, title, col):
        out = text(70, yc - 22, title, 11, col, "start", "bold")
        out += line(70, yc, 650, yc, INK, 2)
        for i in range(len(ticks) - 1):
            out += line(ticks[i], yc - 8, ticks[i], yc + 8, INK, 2)
            mid = (ticks[i] + ticks[i + 1]) / 2
            out += text(mid, yc + 22, "Δt", 9, GREY, "middle")
        out += line(ticks[-1], yc - 8, ticks[-1], yc + 8, INK, 2)
        return out
    even = [70 + i * 82 for i in range(8)]
    s += timeline(96, even, "Рівномірно: однакове Δt → коректні I та D", GREEN)
    jit = [70, 132, 250, 300, 420, 455, 560, 650]
    s += timeline(186, jit, "Джитер: крок «плаває» → I та D спотворені", RED)
    s += text(w / 2, h - 12, "I множить на Δt, D ділить на Δt — нерівний крок псує обидві складові",
              10.5, GREY, "middle", "italic")
    save("fig-34-9-4.svg", s)


def fig_disc_guards():
    """Рис. 34.9.5 — базова формула + чотири захисти."""
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 26, "Надійний ПІД = формула + чотири захисти", 13.5, INK, "middle", "bold")
    s += rect(228, 116, 264, 56, fill="#f6f4ec", stroke=INK, sw=2, rx=8)
    s += text(360, 140, "u = Kp·e + Ki·∫e + Kd·de/dt", 12.5, INK, "middle", "bold")
    s += text(360, 160, "базова формула", 9.5, GREY, "middle")
    guards = [(140, 64, "антивіндап:\nзатиск I", GREEN, 300, 116),
              (520, 64, "D від виміру\n+ ФНЧ", BLUE, 430, 116),
              (140, 210, "обмеження\nвиходу u", RED, 300, 172),
              (520, 210, "скидання стану\nпри ввімкненні", PURP, 430, 172)]
    for gx, gy, lab, col, ax, ay in guards:
        s += rect(gx - 78, gy - 22, 156, 46, fill="#ffffff", stroke=col, sw=2, rx=6)
        lines = lab.split("\n")
        for j, ln in enumerate(lines):
            s += text(gx, gy - 2 + j * 14, ln, 9.5, col, "middle", "bold" if j == 0 else "normal")
        s += arrow(gx + (78 if gx < 360 else -78) * 0, gy + (24 if gy < 140 else -22), ax, ay, col, 1.8)
    save("fig-34-9-5.svg", s)


def fig_disc_budget():
    """Рис. 34.9.6 — бюджет одного такту Δt."""
    w, h = 720, 230
    s = header(w, h)
    s += text(w / 2, 26, "Бюджет одного такту: усе має вкластися в Δt", 13, INK, "middle", "bold")
    x0, y, pw, ht = 60, 110, 600, 52
    s += text(x0, y - 14, "період Δt = 5 мс (200 Гц)", 11, INK, "start", "bold")
    segs = [("читання\nдавачів", 0.5, "#cfe0f5"), ("злиття", 0.2, "#dfeFdf"),
            ("ПІД", 0.12, "#f3dede"), ("вивід", 0.1, "#f6efd6"), ("запас (slack)", 4.08, "#eeeeee")]
    total = 5.0
    x = x0
    for lab, ms, fill in segs:
        ww = pw * ms / total
        s += rect(x, y, ww, ht, fill=fill, stroke=INK, sw=1.4)
        if ww > 40:
            for j, ln in enumerate(lab.split("\n")):
                s += text(x + ww / 2, y + ht / 2 - 2 + j * 12, ln, 9, INK, "middle")
        x += ww
    s += text(x0 + pw * 0.05, y + ht + 22, "≈0.5", 8.5, GREY, "middle")
    s += text(w / 2, h - 14, "ПІД — найдешевший (~0.02 мс); якщо сума підбирається під Δt — час бити на сполох",
              10, GREY, "middle", "italic")
    save("fig-34-9-6.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  §34.10 Налаштування й каскадні контури
# ════════════════════════════════════════════════════════════════════════════

def fig_tune_anatomy():
    """Рис. 34.10.1 — анатомія перехідної кривої для налаштування."""
    w, h = 720, 300
    s = header(w, h)
    s += text(w / 2, 22, "Що читати у відгуку на стрибок завдання", 13, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 580, 200
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    vmin, vmax = -0.05, 1.45
    ser = _pid_series(6.0, 2.0, 0.5, dmeas=True)
    T = ser[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.6, dash="6 4")
    s += text(x0 + pw + 4, yr + 4, "завдання", 10, GREY, "start")
    # settling band ±5%
    s += line(x0, y0 - _uvmap(1.05, vmin, vmax) * ph, x0 + pw, y0 - _uvmap(1.05, vmin, vmax) * ph, FAINT, 1)
    s += line(x0, y0 - _uvmap(0.95, vmin, vmax) * ph, x0 + pw, y0 - _uvmap(0.95, vmin, vmax) * ph, FAINT, 1)
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in ser], BLUE, 2.6)
    # peak
    pk = max(range(len(ser)), key=lambda i: ser[i][2])
    px = _pt(x0, y0, pw, ph, ser[pk][0] / T, _uvmap(ser[pk][2], vmin, vmax))
    s += dot(px[0], px[1], 4, RED)
    s += text(px[0] + 6, px[1] - 6, "переліт", 10, RED, "start", "bold")
    # rise time (first >=0.9)
    ri = next(i for i in range(len(ser)) if ser[i][2] >= 0.9)
    rx = _pt(x0, y0, pw, ph, ser[ri][0] / T, 0)
    s += line(rx[0], y0, rx[0], y0 - _uvmap(0.9, vmin, vmax) * ph, GREEN, 1.6, dash="3 3")
    s += text(rx[0] + 4, y0 - 12, "час наростання", 9.5, GREEN, "start", "bold")
    s += text(x0 + 0.6 * pw, yr + 0.22 * ph, "смуга встановлення ±5%", 9.5, GREY, "start")
    s += text(x0 + 0.6 * pw, y0 - 0.06 * ph, "сталий зсув ≈ 0 (є I)", 9.5, INK, "start")
    save("fig-34-10-1.svg", s)


def _mini(x0, y0, pw, ph, ser, col, title):
    s = rect(x0, y0 - ph, pw, ph, fill="#fcfcfc", stroke=FAINT, sw=1)
    vmin, vmax = -0.1, 1.6
    T = ser[-1][0]
    yr = y0 - _uvmap(1.0, vmin, vmax) * ph
    s += line(x0, yr, x0 + pw, yr, GREY, 1.4, dash="5 3")
    s += _plot_path(x0, y0, pw, ph, [(r[0] / T, _uvmap(_clamp(r[2], vmin, vmax), vmin, vmax)) for r in ser], col, 2.4)
    s += text(x0 + pw / 2, y0 - ph - 8, title, 10.5, col, "middle", "bold")
    return s


def fig_tune_manual():
    """Рис. 34.10.2 — ручне налаштування по черзі: P → D → I."""
    w, h = 720, 250
    s = header(w, h)
    s += text(w / 2, 24, "Ручне налаштування: один коефіцієнт за раз", 13, INK, "middle", "bold")
    pw, ph, y0 = 196, 120, 210
    s += _mini(40, y0, pw, ph, _pid_series(10.0, 0.0, 0.0), RED, "1. лише P → до межі коливань")
    s += _mini(262, y0, pw, ph, _pid_series(10.0, 0.0, 2.6, dmeas=True), BLUE, "2. + D → гасить переліт")
    s += _mini(484, y0, pw, ph, _pid_series(10.0, 2.5, 2.6, dmeas=True), GREEN, "3. + I → прибирає зсув")
    s += arrow(238, y0 - ph / 2, 260, y0 - ph / 2, INK, 2)
    s += arrow(460, y0 - ph / 2, 482, y0 - ph / 2, INK, 2)
    save("fig-34-10-2.svg", s)


def fig_tune_zn():
    """Рис. 34.10.3 — Зіглер–Ніколс: гранична жорсткість Ku і період Tu."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 24, "Зіглер–Ніколс: знайти Ku і період Tu стійких коливань", 12.5, INK, "middle", "bold")
    x0, y0, pw, ph = 80, 250, 580, 200
    s += axes(x0, y0, pw, ph)
    s += text(x0 + pw, y0 + 20, "час", 11, INK, "middle")
    Tu = 0.5
    Ttot = 2.4
    s += line(x0, y0 - 0.5 * ph, x0 + pw, y0 - 0.5 * ph, GREY, 1.4, dash="6 4")
    s += text(x0 + pw + 4, y0 - 0.5 * ph + 4, "завдання", 10, GREY, "start")
    pts = [(t / 300, 0.5 + 0.34 * math.sin(2 * math.pi * (t / 300 * Ttot) / Tu)) for t in range(301)]
    s += _plot_path(x0, y0, pw, ph, pts, RED, 2.4)
    # mark Tu between two peaks
    t1 = (Tu / 4) / Ttot
    t2 = (Tu / 4 + Tu) / Ttot
    yp = y0 - 0.86 * ph
    s += line(x0 + t1 * pw, yp, x0 + t2 * pw, yp, INK, 1.8)
    s += line(x0 + t1 * pw, yp - 6, x0 + t1 * pw, yp + 6, INK, 1.8)
    s += line(x0 + t2 * pw, yp - 6, x0 + t2 * pw, yp + 6, INK, 1.8)
    s += text((x0 + t1 * pw + x0 + t2 * pw) / 2, yp - 8, "Tu", 11, INK, "middle", "bold")
    s += text(x0 + 0.5 * pw, y0 - 0.12 * ph, "Kp = Ku → сталі коливання (ні згасають, ні ростуть)",
              10, RED, "middle", "bold")
    save("fig-34-10-3.svg", s)


def fig_tune_table():
    """Рис. 34.10.4 — шпаргалка: симптом → ліки."""
    w, h = 720, 290
    s = header(w, h)
    s += text(w / 2, 26, "Шпаргалка налаштування: симптом → ліки", 13.5, INK, "middle", "bold")
    s += text(180, 60, "Симптом", 12, INK, "middle", "bold")
    s += text(520, 60, "Ліки", 12, INK, "middle", "bold")
    rows = [("повільно реагує", "підняти Kp", GREEN),
            ("застигає нижче завдання", "підняти Ki", BLUE),
            ("перестрілює, коливається", "підняти Kd  або  знизити Kp", RED),
            ("повільне наростальне гойдання", "знизити Ki", PURP),
            ("мотори деренчать", "чистити вимір, фільтр D, знизити Kd", GOLD)]
    y = 92
    for sym, cure, col in rows:
        s += text(40, y, sym, 11.5, INK, "start")
        s += text(390, y, "→", 12, GREY, "start", "bold")
        s += text(414, y, cure, 11.5, col, "start", "bold")
        s += line(36, y + 10, 684, y + 10, FAINT, 1)
        y += 38
    s += line(372, 76, 372, y - 18, FAINT, 1)
    save("fig-34-10-4.svg", s)


def fig_cascade():
    """Рис. 34.10.5 — каскад: зовнішній контур кута → внутрішній контур швидкості."""
    w, h = 720, 270
    s = header(w, h)
    s += text(w / 2, 24, "Каскадні контури: зовнішній (кут) задає завдання внутрішньому (швидкість)",
              11.5, INK, "middle", "bold")
    yc = 120

    def sj(x):
        out = circle(x, yc, 15, fill="#fff", stroke=INK, w=2)
        out += line(x - 7, yc, x + 7, yc, INK, 1.2) + line(x, yc - 7, x, yc + 7, INK, 1.2)
        return out
    s += arrow(40, yc, 73, yc, BLUE, 2)
    s += text(46, yc - 10, "кут*", 10, BLUE, "start", "bold")
    s += sj(88)
    s += text(80, yc + 28, "−", 14, RED, "middle", "bold")
    s += arrow(103, yc, 132, yc, INK, 2)
    s += rect(132, yc - 22, 96, 44, fill="#eef3fb", stroke=BLUE, sw=2, rx=6)
    s += text(180, yc - 2, "ПІД кута", 10.5, INK, "middle", "bold")
    s += text(180, yc + 14, "(зовнішній)", 8.5, GREY, "middle")
    s += arrow(228, yc, 262, yc, INK, 2)
    s += text(245, yc - 10, "швид.*", 9, INK, "middle")
    s += sj(277)
    s += text(269, yc + 28, "−", 14, RED, "middle", "bold")
    s += arrow(292, yc, 320, yc, INK, 2)
    s += rect(320, yc - 22, 104, 44, fill="#eef7ee", stroke=GREEN, sw=2, rx=6)
    s += text(372, yc - 2, "ПІД швидк.", 10.5, INK, "middle", "bold")
    s += text(372, yc + 14, "(внутрішній)", 8.5, GREY, "middle")
    s += arrow(424, yc, 452, yc, INK, 2)
    s += rect(452, yc - 22, 110, 44, fill="#f6f4ec", stroke=INK, sw=2, rx=6)
    s += text(507, yc + 3, "мотори / об'єкт", 10, INK, "middle", "bold")
    s += line(562, yc, 612, yc, INK, 2)
    s += arrow(612, yc, 612, yc - 36, INK, 2)
    s += text(612, yc - 44, "політ", 10, INK, "middle", "bold")

    # inner feedback (gyro → inner sum)
    s += dot(590, yc, 3, INK)
    s += line(590, yc, 590, 200, INK, 1.6)
    s += line(590, 200, 277, 200, INK, 1.6)
    s += arrow(277, 200, 277, yc + 15, INK, 1.6)
    s += text(430, 214, "швидкість ← гіроскоп", 9, GREY, "middle")
    # outer feedback (angle estimate → outer sum)
    s += dot(607, yc, 3, INK)
    s += line(607, yc, 607, 238, INK, 1.6)
    s += line(607, 238, 88, 238, INK, 1.6)
    s += arrow(88, 238, 88, yc + 15, INK, 1.6)
    s += text(330, 252, "кут ← фьюжн (оцінка орієнтації)", 9, GREY, "middle")
    s += text(660, yc - 16, "внутрішній —", 8.5, GREY, "middle")
    s += text(660, yc - 4, "швидший ×5", 8.5, GREY, "middle")
    save("fig-34-10-5.svg", s)


def fig_flight():
    """Рис. 34.10.6 — повний контур стабілізації польоту (капітель розділу)."""
    w, h = 720, 280
    s = header(w, h)
    s += text(w / 2, 24, "Як стабілізується політ — увесь розділ на одній схемі", 12.5, INK, "middle", "bold")
    yc = 110
    chain = [("гіро + акс", "#fbf3f3", "MEMS · Р.33"),
             ("фьюжн", "#eef3fb", "§34.3–34.4"),
             ("оцінка\nорієнтації", "#eef3fb", ""),
             ("ПІД кута", "#eef7ee", "зовнішній"),
             ("ПІД швидк.", "#eef7ee", "D з гіро!"),
             ("мікшер", "#f6f4ec", "→ 4 мотори"),
             ("квад", "#fdf6e3", "тримає\nгоризонт")]
    bw, gap = 86, 6
    x = 18
    cxs = []
    for i, (lab, fill, sub) in enumerate(chain):
        s += rect(x, yc - 26, bw, 52, fill=fill, stroke=INK, sw=1.6, rx=6)
        lines = lab.split("\n")
        for j, ln in enumerate(lines):
            s += text(x + bw / 2, yc - 2 + (j - (len(lines) - 1) / 2) * 13, ln, 10, INK, "middle", "bold")
        if sub:
            s += text(x + bw / 2, yc + 20, sub, 7.6, GREY, "middle")
        cxs.append(x + bw / 2)
        if i < len(chain) - 1:
            s += arrow(x + bw, yc, x + bw + gap, yc, INK, 1.8)
        x += bw + gap
    # feedback loop from quad back to fusion
    s += line(cxs[-1], yc + 26, cxs[-1], 210, INK, 1.6)
    s += line(cxs[-1], 210, cxs[1], 210, INK, 1.6)
    s += arrow(cxs[1], 210, cxs[1], yc + 26, INK, 1.6)
    s += text(w / 2, 228, "замкнене коло — сто разів на секунду", 10.5, GREY, "middle", "italic")
    s += text(w / 2, h - 14, "виміряй → оціни → порівняй із бажаним → подій проти помилки",
              10.5, INK, "middle", "bold")
    save("fig-34-10-6.svg", s)


if __name__ == "__main__":
    print("Розділ 34 · історія до §34.4 (Рис. 34.4·H.k):")
    fig_kfh_wiener()
    fig_kfh_recursive()
    fig_kfh_parallel()
    fig_kfh_resistance()
    fig_kfh_apollo()
    fig_kfh_legacy()
    print("Розділ 34 · історія (Рис. 34.0.k):")
    fig_float_clock()
    fig_watt_governor()
    fig_feedback_loop()
    fig_stability()
    fig_pid_helmsman()
    fig_evolution()
    print("Розділ 34 · §34.1 кути Ейлера (Рис. 34.1.k):")
    fig_dof6()
    fig_frames()
    fig_rpy()
    fig_noncommute()
    fig_zyx()
    fig_gimbal()
    fig_gimballock()
    fig_conventions()
    print("Розділ 34 · §34.2 кватерніони (Рис. 34.2.k):")
    fig_axisangle()
    fig_quatcomp()
    fig_why4()
    fig_nolock()
    fig_slerp()
    fig_unitcover()
    fig_qpipeline()
    print("Розділ 34 · §34.3 комплементарний фільтр (Рис. 34.3.k):")
    fig_cf_motiv()
    fig_cf_split()
    fig_cf_sum()
    fig_cf_block()
    fig_cf_result()
    fig_cf_alpha()
    fig_cf_limits()
    print("Розділ 34 · §34.4 фільтр Калмана (Рис. 34.4.k):")
    fig_kf_fuse()
    fig_kf_cycle()
    fig_kf_predupd()
    fig_kf_gain()
    fig_kf_converge()
    fig_kf_run()
    fig_kf_state()
    print("Розділ 34 · §34.5 зворотний зв'язок (Рис. 34.5.k):")
    fig_ol_open()
    fig_ol_closed()
    fig_ol_error()
    fig_ol_disturb()
    fig_ol_driving()
    fig_ol_instab()
    print("Розділ 34 · §34.6 пропорційний регулятор (Рис. 34.6.k):")
    fig_p_law()
    fig_p_spring()
    fig_p_kp()
    fig_p_offset()
    fig_p_why()
    fig_p_bridge()
    print("Розділ 34 · §34.7 інтегральна складова (Рис. 34.7.k):")
    fig_i_accumulate()
    fig_i_offset()
    fig_i_work()
    fig_i_ki()
    fig_i_windup()
    fig_i_antiwindup()
    print("Розділ 34 · §34.8 диференційна складова (Рис. 34.8.k):")
    fig_d_slope()
    fig_d_brake()
    fig_d_damp()
    fig_d_higherkp()
    fig_d_noise()
    fig_d_kick()
    print("Розділ 34 · §34.9 дискретний ПІД (Рис. 34.9.k):")
    fig_disc_sample()
    fig_disc_tick()
    fig_disc_rate()
    fig_disc_jitter()
    fig_disc_guards()
    fig_disc_budget()
    print("Розділ 34 · §34.10 налаштування й каскади (Рис. 34.10.k):")
    fig_tune_anatomy()
    fig_tune_manual()
    fig_tune_zn()
    fig_tune_table()
    fig_cascade()
    fig_flight()
    print("Готово.")
