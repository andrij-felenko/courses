# -*- coding: utf-8 -*-
"""
Окремий генератор SVG-фігур для історичної вставки до §2.10.7 —
«Кварцова криза» (Модуль 2, Розділ 2.10).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Не чіпає головний figs.py розділу. Імена файлів унікальні: fig-10-7i-*.svg.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Підписи історії до теми — «Рис. 2.10.7і.k». Допоміжні функції
скопійовано з figs.py розділу (щоб скрипти не ділили файлів).
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
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LYEL  = "#fcf3da"
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


def _sine(ox, oy, w, amp, cycles, col, wv=2.2, phase=0.0):
    pts = []
    n = int(w)
    for j in range(0, n + 1):
        t = j / w
        y = oy - amp * math.sin(2 * math.pi * cycles * t + phase)
        pts.append((ox + j, y))
    return _poly(pts, col, wv)


def _chip(x, y, w, h, label, sub="", fill=LBLUE, stroke="#5f76bd"):
    s = rect(x, y, w, h, fill, stroke, 1.8, 7)
    s += text(x + w / 2, y + (h / 2 - 3 if sub else h / 2 + 5), label, 14, INK, "middle", "bold")
    if sub:
        s += text(x + w / 2, y + h / 2 + 14, sub, 11.5, "#4a4a4a", "middle")
    return s


# ───────────────────────── Рис. 2.10.7і.1 — таймлайн стиснення ─────────────────
def fig_timeline():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 30, "Кварцовий годинник: півстоліття стиснення", 18, INK, "middle", "bold")

    ax_y = 232
    x0, x1 = 70, W - 50
    s += line(x0, ax_y, x1, ax_y, INK, 2.2)
    s += arrow(x1 - 2, ax_y, x1 + 18, ax_y, INK, 2.2)
    s += text(x1 + 22, ax_y + 5, "рік", 12, INK, "start")

    # роки уздовж осі
    years = [(1927, "1927"), (1969, "1969"), (1970, "1970"), (1985, "1985")]
    yr_min, yr_max = 1920, 1990
    def X(yr):
        return x0 + (x1 - x0 - 30) * (yr - yr_min) / (yr_max - yr_min)
    for yr, lab in years:
        s += line(X(yr), ax_y - 5, X(yr), ax_y + 5, INK, 2)
        s += text(X(yr), ax_y + 22, lab, 12, INK, "middle", "bold")

    # «розмір» приладу спадає — стовпчики.
    # 1969 і 1970 на осі майже збігаються — рознесемо їх центри на dx, щоб не накладались.
    bars = [
        (1927, -36, 150, "шафа", "лабораторія\n(Маррісон)", COPP, -18),
        (1969, -36, 64,  "Seiko Astron", "наручний\n(Японія, 1969)", RED, 0),
        (1970, +36, 60,  "рух Beta 21", "наручний\n(CEH, 1970)", BLUE, -18),
        (1985, -36, 30,  "масовий", "дешевий чип\n(Японія/США)", GREEN, 0),
    ]
    base = ax_y - 8
    for yr, dx, hgt, top, sub, col, lbl_dy in bars:
        cx = X(yr) + dx
        s += rect(cx - 26, base - hgt, 52, hgt, "#ffffff", col, 2.2, 4)
        # сполучна риска від центру стовпчика до позначки року на осі
        if dx:
            s += line(cx, base, X(yr), ax_y - 6, col, 1, dash="3,3")
        s += text(cx, base - hgt - 8 + lbl_dy, top, 12, col, "middle", "bold")
        for i, ln in enumerate(sub.split("\n")):
            s += text(cx, base - hgt + 18 + i * 14, ln, 10.5, "#444", "middle")

    # стрілка «розмір падає»
    s += arrow(X(1930), 72, X(1984) - 6, 188, GREY, 2, dash="6,5")
    s += text(322, 96, "розмір приладу падає, тираж зростає", 12.5, GREY, "middle", "italic")
    save("fig-10-7i-1-timeline.svg", s)


# ───────────────────── Рис. 2.10.7і.2 — перегони CEH vs Seiko ──────────────────
def fig_race():
    W, H = 760, 330
    s = header(W, H)
    s += text(W / 2, 30, "Дві школи на спільному порозі (1967–1970)", 18, INK, "middle", "bold")

    # дві доріжки
    midx = W / 2
    s += line(midx, 56, midx, H - 24, FAINT, 1.6, dash="4,5")

    # Швейцарія (ліворуч)
    s += text(190, 58, "ШВЕЙЦАРІЯ — консорціум CEH", 14, BLUE, "middle", "bold")
    sw = [
        (84, "1962", "20 фірм скидаються,\nзасновують лабораторію CEH"),
        (140, "1966", "Фрай: кварц 8192 Гц + дільник\nна мікросхемах"),
        (196, "1967", "прототипи Beta 1 і Beta 2\nна конкурсі в Невшателі"),
        (252, "1970", "серійний рух Beta 21\nна Базельському ярмарку"),
    ]
    for yv, yr, txt in sw:
        s += circle(70, yv, 6, BLUE, BLUE, 2)
        s += text(86, yv - 4, yr, 12.5, BLUE, "start", "bold")
        for i, ln in enumerate(txt.split("\n")):
            s += text(86, yv + 11 + i * 13, ln, 11, "#3a3a3a", "start")
    s += line(70, 84, 70, 252, BLUE, 2)

    # Японія (праворуч)
    s += text(W - 190, 58, "ЯПОНІЯ — Seiko власними силами", 14, RED, "middle", "bold")
    jp = [
        (96, "поч. 1960-х", "кварцові годинники:\nнастільні → дедалі менші"),
        (168, "кін. 1968", "Хаторі ставить строк:\nнаручний кварц за рік"),
        (240, "25.12.1969", "Quartz-Astron 35SQ —\nперший у продажу"),
    ]
    rx = W - 70
    for yv, yr, txt in jp:
        s += circle(rx, yv, 6, RED, RED, 2)
        s += text(rx - 16, yv - 4, yr, 12.5, RED, "end", "bold")
        for i, ln in enumerate(txt.split("\n")):
            s += text(rx - 16, yv + 11 + i * 13, ln, 11, "#3a3a3a", "end")
    s += line(rx, 96, rx, 240, RED, 2)

    # вердикт унизу
    s += rect(150, H - 36, W - 300, 26, LYEL, SUN, 1.5, 6)
    s += text(W / 2, H - 18, "Швейцарці виграли лабораторні перегони — Seiko виграв ринкові (першим у продаж)",
              11.5, "#7a5a13", "middle", "bold")
    save("fig-10-7i-2-race.svg", s)


# ─────────────────── Рис. 2.10.7і.3 — анатомія краху (масовість) ───────────────
def fig_collapse():
    W, H = 760, 340
    s = header(W, H)
    s += text(W / 2, 30, "Програли не фізику, а економіку масовості", 18, INK, "middle", "bold")

    # дві ставки — дві колонки
    s += rect(48, 52, 320, 150, LBLUE, "#5f76bd", 1.8, 9)
    s += text(208, 74, "Ставка Швейцарії", 14.5, BLUE, "middle", "bold")
    for i, ln in enumerate([
        "• лишитися при механіці й майстерності",
        "• Beta 21 — лише ~6000 шт., знято за рік-два",
        "• точність є, дешевого конвеєра — нема",
    ]):
        s += text(64, 100 + i * 26, ln, 12, "#33405e", "start")
    s += text(208, 188, "→ продукт-витвір, малий тираж", 12, BLUE, "middle", "italic")

    s += rect(W - 368, 52, 320, 150, LGRN, "#3f9a57", 1.8, 9)
    s += text(W - 208, 74, "Ставка Японії та США", 14.5, GREEN, "middle", "bold")
    for i, ln in enumerate([
        "• Seiko, Citizen, Casio: мислять електронікою",
        "• TI, Fairchild, National: дешева ІС-дільник",
        "• кварц мільйонами, ціна → копійки",
    ]):
        s += text(W - 352, 100 + i * 26, ln, 12, "#23502f", "start")
    s += text(W - 208, 188, "→ масовий товар, величезний тираж", 12, GREEN, "middle", "italic")

    # графік зайнятості
    gx, gy, gw, gh = 130, 240, 500, 70
    s += text(W / 2, 228, "Зайнятість у швейцарській годинниковій галузі (перевірити)", 12.5, INK, "middle", "bold")
    s += line(gx, gy + gh, gx + gw, gy + gh, INK, 1.8)  # вісь X
    s += line(gx, gy, gx, gy + gh, INK, 1.8)            # вісь Y
    # дві точки: 1970 -> 90k, 1988 -> 28k
    p70 = (gx + 40, gy + gh - gh * (90 / 90))
    p88 = (gx + gw - 60, gy + gh - gh * (28 / 90))
    s += _poly([p70, p88], RED, 3)
    s += circle(p70[0], p70[1], 5, RED, RED, 2)
    s += circle(p88[0], p88[1], 5, RED, RED, 2)
    s += text(p70[0], p70[1] - 10, "1970: ~90 000", 12, RED, "middle", "bold")
    s += text(p88[0], p88[1] - 10, "1988: ~28 000", 12, RED, "middle", "bold")
    s += text((p70[0] + p88[0]) / 2, gy + gh + 22, "за десятиліття — мінус дві третини галузі",
              11, GREY, "middle", "italic")
    save("fig-10-7i-3-collapse.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_race()
    fig_collapse()
    print("done ->", OUT)
