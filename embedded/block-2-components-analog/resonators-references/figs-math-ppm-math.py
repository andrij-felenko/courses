# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки 2.10.6m «ppm-арифметика».
Чистий Python, без сторонніх залежностей. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(префікс fig-10-6m-…), щоб не зачіпати головний figs.py розділу.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; стрілки через marker;
шрифт sans-serif. Допоміжні функції скопійовано з попередніх розділів модуля.
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
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LSUN  = "#fbf3e0"
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aSun" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{SUN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen", BLUE: "aBlue", SUN: "aSun"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round" '
            f'marker-end="url(#{m})"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    r = f' rx="{rx}"' if rx else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"'
            f'{r} fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal", mono=False):
    fam = '"Consolas","Courier New",monospace' if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family={fam!r} '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def save(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", path)


# ---------------------------------------------------------------------------
# Рис. 2.10.6m.1 — «драбина» ppm → секунди за добу / за рік
# Кожен рядок: допуск у ppm, частка, помилка часу за добу і за рік.
# ---------------------------------------------------------------------------
def fig1():
    W, H = 760, 412
    s = header(W, H)
    s += text(W / 2, 30, "Один і той самий годинник, різний кварц: ppm → час", 17, INK, "middle", "bold")

    # колонки
    cx_ppm  = 70
    cx_frac = 215
    cx_day  = 390
    cx_year = 560
    cx_bar  = 660  # початок смужки наочності
    bar_max = 86   # макс ширина смужки (px)

    top = 70
    # заголовки колонок
    s += text(cx_ppm,  top, "допуск", 13, GREY, "start", "bold")
    s += text(cx_frac, top, "частка", 13, GREY, "start", "bold")
    s += text(cx_day,  top, "за добу", 13, GREY, "start", "bold")
    s += text(cx_year, top, "за рік", 13, GREY, "start", "bold")
    s += text(cx_bar + bar_max / 2, top, "наочно/добу", 13, GREY, "middle", "bold")
    s += line(50, top + 8, W - 24, top + 8, FAINT, 1.5)

    SEC_DAY = 86400
    SEC_YEAR = 86400 * 365
    rows = [
        ("±20 ppm", 20,  "хороший кварц МК", BLUE),
        ("±50 ppm", 50,  "годинниковий 32 кГц", GREEN),
        ("±100 ppm", 100, "керамічний резонатор", SUN),
        ("±0.5 ppm", 0.5, "TCXO", RED),
    ]
    # масштаб смужки: log-подібний, але простіше — за коренем, щоб 0.5 теж було видно
    maxppm = 100.0
    y = top + 40
    dy = 74
    for label, ppm, note, col in rows:
        # значення
        frac = ppm * 1e-6
        per_day = frac * SEC_DAY
        per_year = frac * SEC_YEAR
        # форматування за добу
        if per_day >= 1:
            day_s = f"{per_day:.2f} с"
        elif per_day >= 0.001:
            day_s = f"{per_day*1000:.0f} мс"
        else:
            day_s = f"{per_day*1000:.2f} мс"
        # за рік
        if per_year >= 3600:
            year_s = f"{per_year/60:.0f} хв"
        elif per_year >= 60:
            year_s = f"{per_year:.0f} с"
        else:
            year_s = f"{per_year:.1f} с"

        s += text(cx_ppm,  y, label, 16, col, "start", "bold")
        s += text(cx_ppm,  y + 18, note, 12, GREY, "start")
        pct = ppm / 10000.0
        pct_s = f"{pct:.4f}".rstrip("0").rstrip(".") if pct < 0.001 else f"{pct:g}"
        s += text(cx_frac, y, f"{ppm:g}·10⁻⁶", 15, INK, "start", mono=True)
        s += text(cx_frac, y + 18, f"= {pct_s} %", 12, GREY, "start", mono=True)
        s += text(cx_day,  y, day_s, 16, INK, "start", "bold", mono=True)
        s += text(cx_year, y, year_s, 16, INK, "start", mono=True)
        # смужка (за коренем від ppm для видимості)
        bw = bar_max * (ppm / maxppm) ** 0.5
        s += rect(cx_bar, y - 12, bar_max, 14, fill="none", stroke=FAINT, sw=1, rx=3)
        s += rect(cx_bar, y - 12, bw, 14, fill=col, stroke="none", rx=3)
        if label.startswith("±20"):
            s += rect(50, y - 30, W - 74, dy - 18, fill="none", stroke=col, sw=1.5, rx=6)
        y += dy

    s += text(W / 2, H - 14,
              "20 ppm ≈ 1.7 с/добу ≈ 10.5 хв/рік. RC-генератор (±1–2 %) набрав би стільки за хвилини.",
              13, GREY, "middle", style="italic")
    s += footer()
    save("fig-10-6m-1-ppm-ladder.svg", s)


# ---------------------------------------------------------------------------
# Рис. 2.10.6m.2 — бюджет похибки UART: вісь ppm, де живуть джерела,
# і де лежить «стіна»半-біта кадру.
# ---------------------------------------------------------------------------
def fig2():
    W, H = 760, 400
    s = header(W, H)
    s += text(W / 2, 30, "Бюджет похибки UART: 20 ppm vs «стіна» пів-біта", 17, INK, "middle", "bold")

    # лог-вісь похибки годинника: 1 ppm ... 100000 ppm (=10 %)
    x0, x1 = 80, W - 40
    axy = 250
    import math
    lo_e, hi_e = 0, 5  # 10^0 = 1 ppm ... 10^5 = 100000 ppm
    def xof(ppm):
        e = math.log10(ppm)
        return x0 + (e - lo_e) / (hi_e - lo_e) * (x1 - x0)

    # вісь
    s += line(x0, axy, x1, axy, INK, 2)
    for e in range(lo_e, hi_e + 1):
        ppm = 10 ** e
        x = xof(ppm)
        s += line(x, axy - 6, x, axy + 6, INK, 2)
        if ppm >= 10000:
            lab = f"{ppm/10000:g}%"
        else:
            lab = f"{ppm:g}ppm"
        s += text(x, axy + 24, lab, 12, INK, "middle")
    s += text(x1, axy + 46, "похибка частоти (лог.)", 12, GREY, "end", style="italic")

    # «стіна»: для типового кадру 10.5 біт безпечний бюджет на ОДИН бік ≈ ±2 %
    # (повний half-bit ≈ 4.8 %, але це межа на нуль запасу). Показуємо обидві.
    def vwall(ppm, col, label, sub, up=True, dash=None):
        x = xof(ppm)
        y_t = 70 if up else axy + 70
        body = line(x, axy, x, (axy - 150) if up else (axy + 60), col, 2, dash=dash)
        ty = (axy - 158) if up else (axy + 78)
        body += text(x, ty, label, 13, col, "middle", "bold")
        body += text(x, ty + 17, sub, 11, GREY, "middle")
        return body

    # зони
    s += rect(xof(20000), 60, xof(100000) - xof(20000), axy - 60, fill=LRED, stroke="none")
    s += rect(xof(1), 60, xof(20000) - xof(1), axy - 60, fill=LGRN, stroke="none")
    s += text(xof(140), 80, "сигнал ще читається", 12, GREEN, "middle", "bold")
    s += text(xof(45000), 80, "кадр псується", 12, RED, "middle", "bold")

    # межі
    s += line(xof(20000), 60, xof(20000), axy, RED, 2, dash="5 4")
    s += text(xof(20000), 52, "≈2 % (безпечно)", 12, RED, "middle", "bold")
    s += line(xof(48000), 60, xof(48000), axy, RED, 1.5, dash="2 4")
    s += text(xof(48000), 52, "≈4.8 % (пів-біт, межа)", 11, GREY, "middle")

    # джерела частоти — мітки знизу зі стрілками вгору на вісь
    def src(ppm, label, col):
        x = xof(ppm)
        b = line(x, axy, x, axy + 4, col, 2)
        b += "<polygon points='%.1f,%.1f %.1f,%.1f %.1f,%.1f' fill='%s'/>\n" % (
            x, axy, x - 6, axy + 12, x + 6, axy + 12, col)
        return b
    # підписи джерел зверху, щоб не зіткнулися з підписами осі
    s += text(xof(20), 120, "кварц 20 ppm", 13, BLUE, "middle", "bold")
    s += arrow(xof(20), 128, xof(20), axy - 4, BLUE, 2)
    s += text(xof(20), 138, "0.002 %", 11, GREY, "middle", mono=True)

    s += text(xof(3000), 160, "RC ±0.3 %", 13, SUN, "middle", "bold")
    s += arrow(xof(3000), 168, xof(3000), axy - 4, SUN, 2)
    s += text(xof(3000), 178, "(калібрований)", 11, GREY, "middle")

    s += text(xof(15000), 200, "RC ±1.5 %", 13, RED, "middle", "bold")
    s += arrow(xof(15000), 208, xof(15000), axy - 4, RED, 2)
    s += text(xof(15000), 218, "(сирий, по T)", 11, GREY, "middle")

    s += text(W / 2, H - 14,
              "Два кінці лінії складають похибки. 20 + 20 ppm = 0.004 % — тоне в бюджеті; ±1.5 % RC уже чіпає стіну.",
              13, GREY, "middle", style="italic")
    s += footer()
    save("fig-10-6m-2-uart-budget.svg", s)


if __name__ == "__main__":
    fig1()
    fig2()
    print("done")
