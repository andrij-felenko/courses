# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🧮-вставки 2.5.8m — «Зворотне відновлення діода (Qrr)».
НЕ чіпає головний figs.py розділу. Вивід → ./img/ з унікальними іменами
(fig-10-8m-*). Чистий Python, без залежностей.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділу (єдиний вигляд).
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
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def _polyfill(pts, fill, stroke="none", wv=0.0):
    sw = f' stroke="{stroke}" stroke-width="{wv}"' if stroke != "none" else ' stroke="none"'
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)} Z" fill="{fill}"{sw}/>\n'


def _diode(cx, cy, s=14, color=INK, w=2.4, vertical=False):
    """Символ діода. Горизонтально: анод ліворуч, катод (риска) праворуч."""
    out = ""
    if not vertical:
        out += f'<path d="M {cx-s:.1f},{cy-s:.1f} L {cx-s:.1f},{cy+s:.1f} L {cx+s:.1f},{cy:.1f} Z" fill="none" stroke="{color}" stroke-width="{w}"/>\n'
        out += line(cx + s, cy - s, cx + s, cy + s, color, w)
    else:
        # анод зверху, катод (риска) знизу
        out += f'<path d="M {cx-s:.1f},{cy-s:.1f} L {cx+s:.1f},{cy-s:.1f} L {cx:.1f},{cy+s:.1f} Z" fill="none" stroke="{color}" stroke-width="{w}"/>\n'
        out += line(cx - s, cy + s, cx + s, cy + s, color, w)
    return out


# ── Рис. 2.5.8m.1 — форма струму при зворотному відновленні ──────────────────
def fig_trr_waveform():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 32, "Зворотне відновлення: мить, коли діод проводить «назад»",
              19, INK, "middle", "bold")

    # осі
    ox, oy = 90, 250          # початок координат (вісь часу проходить тут)
    axw, axup, axdn = 700, 150, 130
    s += line(ox, oy - axup, ox, oy + axdn, INK, 2)          # вісь струму (I)
    s += arrow(ox, oy - axup, ox, oy - axup - 8, INK, 2)
    s += line(ox - 10, oy, ox + axw, oy, INK, 2)             # вісь часу
    s += arrow(ox + axw - 8, oy, ox + axw, oy, INK, 2)
    s += text(ox - 14, oy - axup - 4, "I", 15, INK, "end", "bold")
    s += text(ox + axw, oy + 22, "t", 15, INK, "end", "bold")
    s += text(ox - 14, oy - axup + 16, "+", 14, RED, "end", "bold")
    s += text(ox - 14, oy + axdn, "−", 14, BLUE, "end", "bold")

    # рівень прямого струму I_F
    ify = oy - 95
    t0 = ox + 60          # початок спаду (di/dt)
    tz = ox + 250         # перетин нуля
    trm = ox + 330        # пік зворотного струму I_RM
    tend = ox + 470       # кінець відновлення (струм назад до 0)

    s += line(ox + 6, ify, t0, ify, RED, 3)                 # пряма поличка I_F
    s += line(ox + 6, ify, ox + 6, ify, RED)
    # лінійний спад крізь нуль до I_RM
    s += _poly([(t0, ify), (tz, oy), (trm, oy + 100)], RED, 3)
    # «хвіст» відновлення назад до нуля (опуклий)
    tail = []
    for j in range(0, 101):
        u = j / 100.0
        x = trm + (tend - trm) * u
        # експоненційний підйом від -I_RM до 0
        y = (oy + 100) - 100 * (1 - math.exp(-3.0 * u))
        tail.append((x, y))
    s += _poly(tail, RED, 3)
    s += line(tend, oy, ox + axw - 30, oy, RED, 3)          # далі нуль

    # площа Qrr (заштрихований трикутник-хвіст під віссю)
    area = [(tz, oy)]
    area += [(trm, oy + 100)]
    area += tail
    s += _polyfill(area, LRED, RED, 0.0)
    s += _poly([(tz, oy), (trm, oy + 100)], RED, 1.2)        # обвід лівого боку
    s += text((tz + tend) / 2 + 6, oy + 58, "Q_rr", 16, RED, "middle", "bold")
    s += text((tz + tend) / 2 + 6, oy + 76, "(вимітений заряд)", 11.5, RED, "middle", style="italic")

    # пунктири й підписи рівнів
    s += line(ox, ify, t0, ify, GREY, 1.2, "4 3")
    s += text(ox - 14, ify + 5, "I_F", 14, RED, "end", "bold")
    s += line(ox, oy + 100, trm, oy + 100, GREY, 1.2, "4 3")
    s += text(ox - 14, oy + 105, "−I_RM", 13, BLUE, "end", "bold")

    # позначки часу t_rr
    s += line(tz, oy + 4, tz, oy + axdn - 6, GREY, 1.2, "4 3")
    s += line(tend, oy + 4, tend, oy + axdn - 6, GREY, 1.2, "4 3")
    yb = oy + axdn - 2
    s += arrow(tz, yb, tend, yb, INK, 1.8)
    s += arrow(tend, yb, tz, yb, INK, 1.8)
    s += text((tz + tend) / 2, yb + 18, "t_rr", 15, INK, "middle", "bold")

    # фаза di/dt (спад)
    s += text((t0 + tz) / 2 - 6, oy - 30, "крутість", 11.5, GREY, "middle", style="italic")
    s += text((t0 + tz) / 2 - 6, oy - 16, "di/dt", 12.5, INK, "middle", "bold")
    s += arrow(t0 + 6, ify + 14, tz - 6, oy - 14, GREY, 1.6)

    # підписи фаз зверху
    s += text(ox + 33, ify - 18, "проводить", 12, GREEN, "middle")
    s += text(ox + 33, ify - 4, "уперед", 12, GREEN, "middle")
    s += text(trm + 4, oy + 132, "діод ще «відкритий» назад", 12, BLUE, "middle", "bold")
    s += text(trm + 4, oy + 148, "= майже коротке замикання", 11.5, BLUE, "middle", style="italic")

    s += text(W / 2, H - 12,
              "Струм не спиняється на нулі: діод проводить назад, аж доки не вимете накопичений заряд Q_rr. Площа під віссю = Q_rr.",
              12, GREY, "middle", style="italic")
    save("fig-10-8m-1-trr-waveform.svg", s)


# ── Рис. 2.5.8m.2 — наскрізний струм у півмості ──────────────────────────────
def fig_halfbridge_shoot():
    W, H = 860, 410
    s = header(W, H)
    s += text(W / 2, 30, "Чому це небезпечно: наскрізний кидок у півмості",
              19, INK, "middle", "bold")

    # дві однакові панелі: ДО і ПІД ЧАС відновлення
    def panel(x0, title, recover):
        out = text(x0 + 150, 60, title, 14, INK, "middle", "bold")
        # шина живлення
        vtop, vbot = 92, 330
        railx = x0 + 150
        out += line(x0 + 40, vtop, x0 + 260, vtop, INK, 2)
        out += line(x0 + 40, vbot, x0 + 260, vbot, INK, 2)
        out += text(x0 + 36, vtop - 8, "+V", 13, RED, "end", "bold")
        out += text(x0 + 36, vbot + 16, "GND", 13, BLUE, "end", "bold")
        mid = (vtop + vbot) / 2

        # верхнє плече: ключ (прямокутник) + діод паралельно
        sw_w, sw_h = 36, 40
        # верхній ключ
        topon = recover  # під час відновлення верхній ключ уже ВВІМКНЕНО
        out += rect(railx - sw_w / 2, vtop + 22, sw_w, sw_h,
                    LGRN if topon else "#ffffff", GREEN if topon else INK, 2, 4)
        out += text(railx, vtop + 22 + sw_h / 2 + 4, "ON" if topon else "OFF",
                    11.5, GREEN if topon else GREY, "middle", "bold")
        out += line(railx, vtop, railx, vtop + 22, INK, 2)
        out += line(railx, vtop + 22 + sw_h, railx, mid, INK, 2)
        # верхній антипаралельний діод (катод догори)
        dx = railx + 70
        out += line(dx, vtop, dx, mid, INK, 1.6)
        out += line(railx, vtop, dx, vtop, INK, 1.6)
        out += line(railx, mid, dx, mid, INK, 1.6)
        out += _diode(dx, (vtop + mid) / 2, 12, INK, 2.2, vertical=True)

        # нижній ключ + діод
        out += rect(railx - sw_w / 2, mid + 22, sw_w, sw_h, "#ffffff", INK, 2, 4)
        out += text(railx, mid + 22 + sw_h / 2 + 4, "OFF", 11.5, GREY, "middle", "bold")
        out += line(railx, mid, railx, mid + 22, INK, 2)
        out += line(railx, mid + 22 + sw_h, railx, vbot, INK, 2)
        # нижній діод — той, що ПРОВОДИВ і тепер відновлюється
        dcol = RED if recover else GREEN
        out += line(dx, mid, dx, vbot, dcol, 2.0 if recover else 1.6)
        out += line(railx, mid, dx, mid, dcol, 2.0 if recover else 1.6)
        out += line(railx, vbot, dx, vbot, dcol, 2.0 if recover else 1.6)
        out += _diode(dx, (mid + vbot) / 2, 12, dcol, 2.4 if recover else 2.2, vertical=True)
        dly = (mid + vbot) / 2
        if recover:
            out += text(dx + 18, dly - 2, "ще", 11, dcol, "start", "bold")
            out += text(dx + 18, dly + 13, "проводить", 11, dcol, "start", "bold")
        else:
            out += text(dx + 18, dly + 4, "проводив", 11, dcol, "start", "bold")

        # вузол виходу
        out += circle(railx, mid, 4, INK, INK)
        out += text(railx + 8, mid - 6, "вихід", 11.5, INK, "start")

        if recover:
            # наскрізний струм: +V → верхній ключ → нижній діод (назад) → GND
            ar = RED
            out += arrow(railx, vtop + 4, railx, vtop + 20, ar, 3)
            out += arrow(railx, mid + 4, railx + 0.1, mid + 18, ar, 3)
            out += arrow(dx, vbot - 16, dx, vbot - 2, ar, 3)
            out += text(x0 + 150, vbot + 40, "НАСКРІЗНИЙ кидок струму", 12.5, RED, "middle", "bold")
            out += text(x0 + 150, vbot + 56, "крізь діод, що ще не закрився", 11, RED, "middle", style="italic")
        else:
            out += arrow(dx, vbot - 4, dx, vbot - 18, GREEN, 2.4)
            out += text(x0 + 150, vbot + 40, "діод котушки проводив струм", 12, GREEN, "middle")
            out += text(x0 + 150, vbot + 56, "обидва ключі ще керовані", 11, GREY, "middle", style="italic")
        return out

    s += panel(20, "До: нижній діод проводить", False)
    # роздільник
    s += line(W / 2, 70, W / 2, H - 70, FAINT, 1.4)
    s += panel(440, "Під час відновлення: верхній ключ увімкнувся", True)

    s += text(W / 2, H - 12,
              "Поки нижній діод вимітає Q_rr, він ще проводить — і щойно ввімкнений верхній ключ закорочує шину крізь нього.",
              12, GREY, "middle", style="italic")
    save("fig-10-8m-2-halfbridge-shoot.svg", s)


def main():
    fig_trr_waveform()
    fig_halfbridge_shoot()


if __name__ == "__main__":
    main()
