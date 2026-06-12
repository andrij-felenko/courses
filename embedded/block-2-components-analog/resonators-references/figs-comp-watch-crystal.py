# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для компонентної вставки 2.10.7c — «Годинниковий кварц
зблизька: камертон у циліндрику і чому він боїться перегріву при паянні».
НЕ чіпає головний figs.py розділу. Вивід → ./img/ з УНІКАЛЬНИМИ іменами
(fig-r10-s7c-*). Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій;
поле зелене; стрілки через marker; шрифт sans-serif. Допоміжні функції
скопійовано з figs.py розділу (єдиний вигляд між розділами).
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


# ── Рис. 2.10.7c.1 — камертон у циліндрику + ланцюжок поділу 32768 → 1 Гц ──────
def fig_tuning_fork():
    """Ліворуч: будова годинникового кварцу — камертон (дві вилки) на спільній
    ніжці, металізація, два виводи, герметичний циліндрик. Праворуч: чому
    32768 = 2¹⁵ — п'ятнадцять каскадів /2 дають рівно 1 Гц (такт секунди)."""
    W, H = 940, 500
    s = header(W, H)
    s += text(W / 2, 32, "Годинниковий кварц зсередини — і навіщо саме 32768 = 2¹⁵ Гц",
              20, INK, "middle", "bold")
    s += text(W / 2, 54, "камертонний кристал у вакуумованому циліндрику · поділ на два × 15 = такт секунди",
              12.5, GREY, "middle", style="italic")

    # ── ЛІВА ПАНЕЛЬ: будова кварцу ────────────────────────────────────────
    # циліндрик (контур корпусу)
    cx = 215
    can_x, can_y, can_w, can_h = 150, 110, 130, 250
    s += rect(can_x, can_y, can_w, can_h, "#fbfbfb", GREY, 2.0, 60)
    s += text(cx, can_y - 12, "циліндрик 3 × 8 мм", 12.5, GREY, "middle", style="italic")
    s += text(cx, can_y + 16, "вакуум / інертний газ", 11, GREY, "middle", style="italic")

    # камертон: спільна ніжка + дві вилки
    base_y = can_y + can_h - 40
    stem_top = can_y + 150
    # ніжка
    s += rect(cx - 10, stem_top, 20, base_y - stem_top, LBLUE, BLUE, 2.0, 3)
    # дві вилки (tines), що згинаються
    tine_top = can_y + 40
    s += rect(cx - 34, tine_top, 18, stem_top - tine_top + 4, LBLUE, BLUE, 2.0, 4)
    s += rect(cx + 16, tine_top, 18, stem_top - tine_top + 4, LBLUE, BLUE, 2.0, 4)
    # металізовані доріжки на вилках (збудження)
    s += line(cx - 25, tine_top + 8, cx - 25, stem_top - 6, COPP, 2.4)
    s += line(cx + 25, tine_top + 8, cx + 25, stem_top - 6, COPP, 2.4)
    s += text(cx, tine_top - 8, "дві вилки камертона", 11.5, BLUE, "middle", "bold")

    # стрілки коливання (вилки сходяться/розходяться)
    ya = tine_top + 60
    s += arrow(cx - 44, ya, cx - 30, ya, GREEN, 1.8)
    s += arrow(cx + 44, ya, cx + 30, ya, GREEN, 1.8)
    s += arrow(cx - 8, ya + 36, cx - 22, ya + 36, GREEN, 1.8)
    s += arrow(cx + 8, ya + 36, cx + 22, ya + 36, GREEN, 1.8)
    s += text(cx, ya + 70, "згинальна мода", 11, GREEN, "middle", style="italic")

    # два виводи з торця
    lead_y = base_y
    s += line(cx - 10, lead_y, cx - 10, can_y + can_h + 26, INK, 2.2)
    s += line(cx + 10, lead_y, cx + 10, can_y + can_h + 26, INK, 2.2)
    s += text(cx, can_y + can_h + 44, "2 рівноцінні виводи (без полярності)", 11, INK, "middle")

    # підпис «32768 Гц»
    s += text(cx, can_y + can_h + 70, "32768 Гц", 16, BLUE, "middle", "bold")

    # роздільник
    s += line(420, 90, 420, H - 40, FAINT, 1.6, "5 5")

    # ── ПРАВА ПАНЕЛЬ: ланцюжок поділу ─────────────────────────────────────
    px = 470
    s += text(px, 112, "Чому 2¹⁵: 15 каскадів «÷2» → рівно 1 Гц", 14.5, INK, "start", "bold")

    # вхід
    bx, by, bw, bh = px, 140, 70, 40
    s += rect(bx, by, bw, bh, LBLUE, BLUE, 2.0, 6)
    s += text(bx + bw / 2, by + bh / 2 + 5, "32768", 13, BLUE, "middle", "bold")
    s += text(bx + bw / 2, by - 8, "Гц", 11, GREY, "middle")

    # каскади ÷2 (показуємо кілька + три крапки + останній)
    stages = [
        ("÷2", "16384"),
        ("÷2", "8192"),
        ("÷2", "4096"),
        ("…",  "…"),
        ("÷2", "2"),
        ("÷2", "1"),
    ]
    x = bx + bw + 16
    y = by
    dw, dh = 56, 40
    prevx = bx + bw
    for i, (op, out) in enumerate(stages):
        col = INK if op == "÷2" else GREY
        s += arrow(prevx, y + dh / 2, x, y + dh / 2, INK, 1.8)
        if op == "…":
            s += text(x + dw / 2, y + dh / 2 + 6, "…  ÷2 ×N  …", 12, GREY, "middle", style="italic")
        else:
            s += rect(x, y, dw, dh, "#ffffff", col, 2.0, 5)
            s += text(x + dw / 2, y + dh / 2 + 5, op, 14, col, "middle", "bold")
        s += text(x + dw / 2, y + dh + 16, out, 11, GREY, "middle")
        prevx = x + dw
        x = prevx + 14
        # перенесення на новий рядок після 3-го блоку
        if i == 2:
            # стрілка вниз-ліворуч на новий ряд
            s += arrow(prevx + 4, y + dh / 2, prevx + 4, y + dh + 40, INK, 1.8)
            x = bx + 0
            y = by + dh + 56
            prevx = x
            # маленький підпис «далі»
            s += text(prevx, y - 8, "(далі тими ж тригерами)", 10.5, GREY, "start", style="italic")
            prevx = x - 12

    # вихід 1 Гц
    outx = prevx + 16
    s += arrow(prevx, y + dh / 2, outx, y + dh / 2, GREEN, 2.0)
    s += rect(outx, y - 4, 96, dh + 8, LGRN, GREEN, 2.2, 7)
    s += text(outx + 48, y + dh / 2 - 2, "1 Гц", 15, GREEN, "middle", "bold")
    s += text(outx + 48, y + dh / 2 + 16, "такт секунди", 10.5, GREEN, "middle")

    # підсумок під правою панеллю
    s += text(px, H - 22,
              "поділ на два = один тригер: без дробів, без PLL, майже без споживання — звідси сотні нА на весь годинник",
              11.5, GREY, "start", style="italic")
    return s


# ── Рис. 2.10.7c.2 — парабола температури і зсув від перегріву при паянні ─────
def fig_thermal():
    """Частота камертона f(T) — парабола з вершиною ~+25 °C (відхід завжди вниз).
    Перегрів при паянні необоротно зсуває всю криву (solder-down shift)."""
    W, H = 900, 480
    s = header(W, H)
    s += text(W / 2, 32, "Парабола температури — і що з нею робить перегрів при паянні",
              20, INK, "middle", "bold")
    s += text(W / 2, 54, "вершина (turnover) ~ +25 °C: будь-який відхід температури тягне частоту вниз",
              12.5, GREY, "middle", style="italic")

    ox, oy = 110, H - 96
    w, h = W - 230, H - 210
    s += arrow(ox, oy, ox, oy - h - 14, INK, 2)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 2)
    s += text(ox + w + 20, oy + 4, "T, °C", 13, INK, "start", "bold")
    s += text(ox - 8, oy - h - 22, "Δf/f, ppm", 13, INK, "middle", "bold")

    # горизонталь 0 ppm трохи нижче вершини параболи
    y0 = oy - h * 0.80                       # рівень 0 ppm
    s += line(ox, y0, ox + w, y0, GREY, 1.4, "5 4")
    s += text(ox - 8, y0 + 4, "0", 12, GREY, "end")

    # шкала T: від -40 до +90, вершина при +25
    Tmin, Tmax, Ttop = -40.0, 90.0, 25.0
    def tx(T):
        return ox + w * (T - Tmin) / (Tmax - Tmin)
    for T in (-40, 0, 25, 50, 90):
        x = tx(T)
        s += line(x, oy, x, oy + 5, INK, 1.6)
        s += text(x, oy + 20, f"{T:+d}".replace("+0", "0"), 11, INK, "middle")
    # позначити turnover
    s += line(tx(Ttop), y0, tx(Ttop), oy, FAINT, 1.4, "3 4")
    s += text(tx(Ttop), y0 - 8, "вершина ≈ +25 °C", 11.5, INK, "middle", "bold")

    # парабола: f = -k*(T-25)^2, у ppm; на краях ~ -40 ppm (типово для камертона)
    k = 0.034                                 # ppm/°C^2 (порядок камертонного кварцу)
    def fppm(T):
        return -k * (T - Ttop) ** 2
    def fy(ppm):
        # масштаб: 0 ppm → y0; -45 ppm → нижче
        return y0 + (-(ppm)) * (h * 0.62) / 45.0
    pts = []
    N = 160
    for j in range(N + 1):
        T = Tmin + (Tmax - Tmin) * j / N
        pts.append((tx(T), fy(fppm(T))))
    s += _poly(pts, BLUE, 2.8)
    s += text(tx(78), fy(fppm(78)) - 10, "до паяння", 12, BLUE, "start", "bold")

    # зсунена крива (solder-down shift): уся парабола вниз на кілька ppm
    shift = 7.0
    pts2 = []
    for j in range(N + 1):
        T = Tmin + (Tmax - Tmin) * j / N
        pts2.append((tx(T), fy(fppm(T) - shift)))
    s += _poly(pts2, RED, 2.6, "7 5")
    s += text(tx(78), fy(fppm(78) - shift) + 18, "після перегріву", 12, RED, "start", "bold")

    # стрілка зсуву біля вершини
    xv = tx(Ttop)
    s += arrow(xv + 70, fy(0) + 2, xv + 70, fy(-shift) - 2, RED, 2)
    s += text(xv + 78, fy(-shift / 2) + 4, "необоротний зсув (solder-down shift)", 11.5, RED, "start", "bold")

    # бічна примітка-«граблі»
    nx, ny = ox + w - 244, oy - h + 8
    s += rect(nx, ny, 252, 86, "#fff", FAINT, 1.4, 8)
    s += text(nx + 12, ny + 22, "Паяти безпечно:", 12.5, INK, "start", "bold")
    s += text(nx + 12, ny + 42, "• жало ~350 °C, дотик 1–2 с", 11.5, INK, "start")
    s += text(nx + 12, ny + 60, "• гріти ВИВОДИ, не тіло циліндра", 11.5, INK, "start")
    s += text(nx + 12, ny + 78, "• перегрів → зсув або «німий» кварц", 11.5, RED, "start")

    # нижній висновок
    s += text(W / 2, H - 18,
              "чим гарячіше й довше жало — тим більший зсув; тривала перевитримка може зовсім зірвати коливання",
              11.5, GREY, "middle", style="italic")
    return s


if __name__ == "__main__":
    save("fig-r10-s7c-1-tuning-fork.svg", fig_tuning_fork())
    save("fig-r10-s7c-2-thermal.svg", fig_thermal())
    print("done.")
