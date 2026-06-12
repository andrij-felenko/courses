# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для математичної вставки §3.7.3m —
«Скільки функцій уміщує LUT: 2^(2ⁿ) і чому 4–6 входів — солодка точка».
Чистий Python, без залежностей. Вивід → ./img/ (унікальні імена fig-r07-3m-*).
Стиль (AUTHORING §9): білий фон; «1»/істина червоний, «0»/хибність синій;
поле/висновок/«накриття» зелене; стрілки через marker; шрифт sans-serif.
Хелпери скопійовано з math-вставок розділу (за §9 — кожен скрипт самодостатній).
Нумерація підписів: Рис. 3.7.3m.k.
НЕ чіпає головний figs.py розділу.
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"   # «1» / істина
BLUE  = "#1f47b5"   # «0» / хибність
GREEN = "#1f8a3b"   # висновок / накриття / «солодка точка»
AMBER = "#caa24a"   # акцент
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen", BLUE: "aBlue", GREY: "aGrey"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def polyline(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<polyline points="{p}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def roundrect(x, y, w, h, color=GREEN, sw=3, rx=14, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{sw}"{d}/>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


def bit_chip(x, y, w, h, val, big=20):
    """Комірка-біт зі значенням 0/1; «1» червона, «0» синя."""
    s = rect(x, y, w, h, "#ffffff", GREY, 1.6, rx=3)
    col = RED if val == "1" else BLUE
    s += text(x + w / 2, y + h / 2 + big * 0.34, val, big, col, "middle", "bold")
    return s


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.7.3m.1 — LUT = крихітна пам'ять, що адресується входами.
#  3-входова LUT: 8 конфіг-бітів (стовпець таблиці істинності) → мультиплексор
#  8→1, керований A,B,C → один вихід. Серце «таблиці замість вентилів».
# ════════════════════════════════════════════════════════════════════════════
def fig_lut_is_memory():
    W, H = 980, 600
    s = header(W, H)
    s += text(W / 2, 34, "LUT зсередини: таблиця істинності, зашита в пам'ять",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "3-входова LUT — це 8 комірок пам'яті (стовпець виходів таблиці) і мультиплексор, що входами A,B,C вибирає одну з них",
              12.5, GREY, "middle", style="italic")

    # --- ліворуч: таблиця істинності F(A,B,C) ---
    tx, ty = 56, 120
    cw, rh = 40, 40
    heads = ["A", "B", "C", "F"]
    for j, hd in enumerate(heads):
        hx = tx + j * cw
        col = INK if j < 3 else GREEN
        s += rect(hx, ty - rh, cw, rh, "#f3f3f3", GREY, 1.6)
        s += text(hx + cw / 2, ty - rh / 2 + 6, hd, 16, col, "middle", "bold")
    # конкретна функція: «більшість» (majority) трьох входів — F=1, коли ≥2 одиниць
    conf = ["0", "0", "0", "1", "0", "1", "1", "1"]  # m0..m7
    for m in range(8):
        a, b, c = (m >> 2) & 1, (m >> 1) & 1, m & 1
        ry = ty + m * rh
        for j, v in enumerate((a, b, c)):
            s += rect(tx + j * cw, ry, cw, rh, "#ffffff", GREY, 1.2)
            s += text(tx + j * cw + cw / 2, ry + rh / 2 + 5, str(v), 14, GREY, "middle")
        s += bit_chip(tx + 3 * cw, ry, cw, rh, conf[m], 18)
        s += text(tx + 4 * cw + 8, ry + rh / 2 + 4, f"m{m}", 10, GREY, "start")
    s += text(tx + 2 * cw, ty + 8 * rh + 24, "8 рядків = 2³ комбінацій входів",
              11.5, GREY, "middle", style="italic")
    s += text(tx + 2 * cw, ty - rh - 14, "функція «більшість 2 з 3»", 12, GREEN, "middle", "bold")

    # --- стрілка: стовпець F → конфіг-комірки SRAM ---
    s += arrow(tx + 4 * cw + 36, ty + 4 * rh, 470, ty + 4 * rh, GREEN, 2.4, "6,5")
    s += text((tx + 4 * cw + 36 + 470) / 2, ty + 4 * rh - 12,
              "стовпець F →", 11.5, GREEN, "middle", style="italic")
    s += text((tx + 4 * cw + 36 + 470) / 2, ty + 4 * rh + 16,
              "у комірки", 11.5, GREEN, "middle", style="italic")

    # --- центр: 8 конфіг-комірок SRAM (вертикальний стек) ---
    mx, my = 500, 96
    ch = 40
    s += text(mx + 22, my - 14, "8 конфіг-комірок", 12.5, INK, "middle", "bold")
    s += text(mx + 22, my + 2, "(SRAM)", 11, GREY, "middle")
    for m in range(8):
        cy = my + 14 + m * ch
        s += bit_chip(mx, cy, 44, ch - 4, conf[m], 18)
        s += text(mx - 8, cy + (ch - 4) / 2 + 4, f"{m}", 10, GREY, "end")
        # лінія від комірки до мультиплексора
        s += line(mx + 44, cy + (ch - 4) / 2, mx + 92, my + 14 + 3.5 * ch + 0, GREY, 1.1)

    # --- мультиплексор 8→1 (трапеція) ---
    muxx = mx + 92
    mux_top, mux_bot = my + 14, my + 14 + 8 * ch - 4
    muxw_top, muxw_bot = 0, 0
    mux_h = mux_bot - mux_top
    mw = 58
    # трапеція звужується донизу до виходу
    p = [(muxx, mux_top), (muxx + mw, mux_top + mux_h * 0.30),
         (muxx + mw, mux_top + mux_h * 0.70), (muxx, mux_bot)]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in p)
    s += f'<polygon points="{pts}" fill="#eef6ef" stroke="{GREEN}" stroke-width="2.4"/>\n'
    s += text(muxx + mw / 2 - 4, (mux_top + mux_bot) / 2 - 6, "MUX", 15, GREEN, "middle", "bold")
    s += text(muxx + mw / 2 - 4, (mux_top + mux_bot) / 2 + 12, "8→1", 12.5, GREEN, "middle")

    # вихід MUX
    outx = muxx + mw
    outy = (mux_top + mux_bot) / 2
    s += line(outx, outy, outx + 70, outy, INK, 2.4)
    s += text(outx + 86, outy + 6, "F", 20, GREEN, "middle", "bold")
    s += text(outx + 86, outy + 26, "вихід", 11, GREY, "middle")

    # --- адресні входи A,B,C знизу в мультиплексор ---
    sel_y = mux_bot + 54
    labels = ["A", "B", "C"]
    for i, lab in enumerate(labels):
        sx = muxx + 12 + i * 20
        s += arrow(sx, sel_y, sx, mux_bot + 4, BLUE, 2)
        s += text(sx, sel_y + 18, lab, 15, BLUE, "middle", "bold")
    s += text(muxx + 32, sel_y + 40, "адреса = (A,B,C)", 12, BLUE, "middle", "bold")
    s += text(muxx + 32, sel_y + 56, "вибирає одну комірку", 11, GREY, "middle", style="italic")

    # підсумкова рамка-думка
    s += roundrect(606, 150, 350, 150, GREEN, 2.2, 12, dash="5,4")
    s += text(620, 178, "Суть LUT", 14.5, GREEN, "start", "bold")
    s += text(620, 204, "• схему не «будують» з вентилів —", 12.5, INK, "start")
    s += text(620, 224, "  її ВПИСУЮТЬ як стовпець бітів;", 12.5, INK, "start")
    s += text(620, 248, "• ті самі 8 комірок зберуть БУДЬ-ЯКУ", 12.5, INK, "start")
    s += text(620, 268, "  функцію 3 входів — змінивши лише вміст;", 12.5, INK, "start")
    s += text(620, 292, "• затримка — одна: час доступу до пам'яті.", 12.5, GREEN, "start", "bold")
    save("fig-r07-3m-1-lut-is-memory.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.7.3m.2 — подвійний степінь: n входів → 2ⁿ рядків → 2^(2ⁿ) функцій.
#  Драбинка чисел показує вибух, який словами не відчути.
# ════════════════════════════════════════════════════════════════════════════
def fig_double_exponential():
    W, H = 980, 560
    s = header(W, H)
    s += text(W / 2, 34, "Дві сходинки степеня: чому функцій астрономічно багато",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "Кожен вхід ПОДВОЮЄ число рядків таблиці; кожен рядок — вільний біт виходу, тож функцій рівно 2 у степені (2ⁿ)",
              12.5, GREY, "middle", style="italic")

    # ланцюжок-схема вгорі: n → 2^n рядків → 2^(2^n) функцій
    cy = 110
    s += rect(70, cy - 26, 110, 52, "#eef2fb", BLUE, 2, rx=10)
    s += text(125, cy - 4, "n входів", 14, BLUE, "middle", "bold")
    s += text(125, cy + 16, "(стільки змінних)", 10.5, GREY, "middle")
    s += arrow(184, cy, 250, cy, GREY, 2.2)
    s += text(217, cy - 10, "2ⁿ", 13, INK, "middle", "bold")

    s += rect(254, cy - 26, 150, 52, "#fdeef0", RED, 2, rx=10)
    s += text(329, cy - 4, "2ⁿ рядків", 14, RED, "middle", "bold")
    s += text(329, cy + 16, "у таблиці істинності", 10.5, GREY, "middle")
    s += arrow(408, cy, 474, cy, GREY, 2.2)
    s += text(441, cy - 10, "2^(·)", 12, INK, "middle", "bold")

    s += rect(478, cy - 26, 210, 52, "#eef6ef", GREEN, 2.2, rx=10)
    s += text(583, cy - 4, "2^(2ⁿ) функцій", 14.5, GREEN, "middle", "bold")
    s += text(583, cy + 16, "стільки РІЗНИХ таблиць виходу", 10.5, GREY, "middle")

    s += text(800, cy - 6, "кожен рядок —", 11.5, GREY, "start", style="italic")
    s += text(800, cy + 10, "вільний 0/1 →", 11.5, GREY, "start", style="italic")
    s += text(800, cy + 26, "перемножуємо 2×2×…", 11.5, GREY, "start", style="italic")

    # таблиця-драбинка
    rows = [
        ("1", "2", "4", "4"),
        ("2", "4", "16", "16"),
        ("3", "8", "256", "256"),
        ("4", "16", "65 536", "65 536"),
        ("5", "32", "≈ 4.3 ·10⁹", "понад 4 мільярди"),
        ("6", "64", "≈ 1.8 ·10¹⁹", "більше за вік Всесвіту в секундах"),
    ]
    tx, ty = 120, 190
    colw = [80, 150, 200, 290]
    heads = ["n", "рядків 2ⁿ", "функцій 2^(2ⁿ)", "відчуй масштаб"]
    cx = tx
    xcols = []
    for j, hd in enumerate(heads):
        xcols.append(cx)
        s += rect(cx, ty, colw[j], 40, "#f3f3f3", GREY, 1.6)
        col = [BLUE, RED, GREEN, INK][j]
        s += text(cx + colw[j] / 2, ty + 26, hd, 14.5, col, "middle", "bold")
        cx += colw[j]
    total_w = sum(colw)
    for i, r in enumerate(rows):
        ry = ty + 40 + i * 46
        bg = "#ffffff" if i % 2 == 0 else "#fafafa"
        s += rect(tx, ry, total_w, 46, bg, FAINT, 1)
        for j in range(4):
            xx = xcols[j]
            col = [BLUE, RED, GREEN, GREY][j]
            wt = "bold" if j <= 2 else "normal"
            sz = 16 if j <= 2 else 12
            st = "normal" if j != 3 else "italic"
            s += text(xx + colw[j] / 2, ry + 30, r[j], sz, col, "middle", wt, st)
        # вертикальні лінії сітки
    for xx in xcols[1:]:
        s += line(xx, ty, xx, ty + 40 + len(rows) * 46, FAINT, 1)
    s += rect(tx, ty, total_w, 40 + len(rows) * 46, "none", GREY, 1.4)

    # підсвітити рядок n=4 (типова базова LUT) та n=6 (сучасна)
    s += roundrect(tx - 5, ty + 40 + 3 * 46 - 3, total_w + 10, 46 + 6, AMBER, 2.4, 8)
    s += text(tx + total_w + 14, ty + 40 + 3 * 46 + 30, "класична", 11.5, AMBER, "start", "bold")
    s += text(tx + total_w + 14, ty + 40 + 3 * 46 + 45, "база", 11.5, AMBER, "start")
    s += roundrect(tx - 5, ty + 40 + 5 * 46 - 3, total_w + 10, 46 + 6, GREEN, 2.6, 8)
    s += text(tx + total_w + 14, ty + 40 + 5 * 46 + 30, "сучасна", 11.5, GREEN, "start", "bold")
    s += text(tx + total_w + 14, ty + 40 + 5 * 46 + 45, "база", 11.5, GREEN, "start")

    s += text(W / 2, H - 22,
              "Уже 6-входова LUT перекриває стільки функцій, що перебрати їх неможливо — а коштує всього 64 біти пам'яті.",
              12.5, INK, "middle", style="italic")
    save("fig-r07-3m-2-double-exponential.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Рис. 3.7.3m.3 — «солодка точка» 4–6: ціна одного LUT (2ⁿ комірок, подвоєння)
#  росте, а виграш від ширшого входу (зекономлені рівні логіки) насичується.
#  Перетин лягає на 4–6.
# ════════════════════════════════════════════════════════════════════════════
def fig_sweet_spot():
    W, H = 980, 560
    s = header(W, H)
    s += text(W / 2, 34, "Чому 4–6 входів — солодка точка LUT",
              20, INK, "middle", "bold")
    s += text(W / 2, 56,
              "Ціна одного LUT подвоюється з кожним входом (2ⁿ комірок); а виграш від ширшого входу швидко насичується",
              12.5, GREY, "middle", style="italic")

    # вісі
    ox, oy = 110, 430      # початок координат (лівий-низ)
    axw, axh = 560, 320
    s += arrow(ox, oy, ox + axw + 16, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh - 16, INK, 2)
    s += text(ox + axw + 8, oy + 28, "число входів n", 13, INK, "middle", "bold")
    s += text(ox - 70, oy - axh - 4, "відносна", 12, INK, "start")
    s += text(ox - 70, oy - axh + 14, "величина", 12, INK, "start")

    ns = [1, 2, 3, 4, 5, 6, 7, 8]
    nx = {n: ox + (n - 1) / 7 * axw for n in ns}
    for n in ns:
        s += line(nx[n], oy, nx[n], oy + 6, INK, 1.4)
        s += text(nx[n], oy + 24, str(n), 13, INK, "middle", "bold")

    # --- крива ціни: 2^n, нормуємо в лог-подобі до висоти (щоб усе влізло) ---
    # використаємо власне 2^n, але стиснемо: y = oy - axh * (n/8)  для «подвоєння»
    # натомість покажемо реальні 2^n підписами, а криву проведемо опуклою вгору.
    cost_pts = []
    import math
    for n in ns:
        val = (2 ** n)
        yy = oy - axh * (math.log2(val) / math.log2(256))  # лог-шкала: 2^8=256 -> верх
        cost_pts.append((nx[n], yy))
    s += polyline(cost_pts, RED, 3)
    for i, n in enumerate(ns):
        x, y = cost_pts[i]
        s += circle(x, y, 4.5, RED, RED, 1)
    s += text(cost_pts[-1][0] - 6, cost_pts[-1][1] - 14,
              "ціна LUT = 2ⁿ комірок", 13, RED, "end", "bold")
    s += text(nx[3], oy - axh * (3 / 8) - 12, "×2 на кожен +1 вхід", 11.5, RED, "middle", style="italic")

    # --- крива виграшу: насичення (зекономлені рівні логіки) ---
    # benefit ~ 1 - 1/n -подібна, нормована
    ben_pts = []
    for n in ns:
        b = 1 - (1.0 / (n + 0.4))
        yy = oy - axh * (b / (1 - 1.0 / 8.4)) * 0.92
        ben_pts.append((nx[n], yy))
    s += polyline(ben_pts, BLUE, 3, dash="2,0")
    for i, n in enumerate(ns):
        x, y = ben_pts[i]
        s += circle(x, y, 4.5, BLUE, BLUE, 1)
    # підпис кривої виграшу — над лівою її частиною (праворуч стоїть бічна панель)
    s += text(nx[3], ben_pts[2][1] - 16, "виграш: зекономлені рівні логіки",
              13, BLUE, "middle", "bold")
    s += text(nx[6] - 6, ben_pts[5][1] - 12, "далі майже не росте", 11.5, BLUE, "end", style="italic")

    # --- зелена смуга «солодкої точки» 4..6 ---
    x4 = nx[4] - (nx[2] - nx[1]) * 0.35
    x6 = nx[6] + (nx[2] - nx[1]) * 0.35
    s += f'<rect x="{x4:.1f}" y="{oy - axh - 4:.1f}" width="{x6 - x4:.1f}" height="{axh + 4:.1f}" fill="#1f8a3b" opacity="0.10"/>\n'
    s += line(x4, oy - axh - 4, x4, oy, GREEN, 1.6, "5,4")
    s += line(x6, oy - axh - 4, x6, oy, GREEN, 1.6, "5,4")
    s += text((x4 + x6) / 2, oy - axh - 16, "солодка точка", 14, GREEN, "middle", "bold")
    s += text((x4 + x6) / 2, oy + 46, "тут виграш ще вартий ціни", 11.5, GREEN, "middle", style="italic")

    # --- бічна панель: K=6 = два K=5 (фрактуровна LUT) ---
    px, py = 720, 120
    s += roundrect(px, py, 232, 320, GREY, 1.6, 12)
    s += text(px + 116, py + 26, "Як зняти решту виграшу", 13.5, INK, "middle", "bold")
    s += text(px + 116, py + 44, "не платячи за широкий вхід", 11, GREY, "middle", style="italic")
    # дві K5 LUT
    s += rect(px + 24, py + 64, 80, 46, "#eef6ef", GREEN, 2, rx=8)
    s += text(px + 64, py + 86, "LUT-5", 12.5, GREEN, "middle", "bold")
    s += text(px + 64, py + 102, "32 біти", 10, GREY, "middle")
    s += rect(px + 128, py + 64, 80, 46, "#eef6ef", GREEN, 2, rx=8)
    s += text(px + 168, py + 86, "LUT-5", 12.5, GREEN, "middle", "bold")
    s += text(px + 168, py + 102, "32 біти", 10, GREY, "middle")
    s += text(px + 116, py + 130, "спільні 5 входів", 11, BLUE, "middle")
    # мультиплексор-зведення
    s += rect(px + 84, py + 150, 64, 34, "#fdeef0", RED, 2, rx=6)
    s += text(px + 116, py + 172, "MUX", 12, RED, "middle", "bold")
    s += arrow(px + 64, py + 110, px + 104, py + 150, GREY, 1.6)
    s += arrow(px + 168, py + 110, px + 128, py + 150, GREY, 1.6)
    s += text(px + 158, py + 146, "6-й вхід", 10.5, RED, "start")
    s += line(px + 116, py + 184, px + 116, py + 204, INK, 2)
    s += text(px + 116, py + 220, "= одна LUT-6", 13, INK, "middle", "bold")
    s += text(px + 116, py + 240, "(64 біти разом)", 10.5, GREY, "middle")
    s += line(px + 16, py + 256, px + 216, py + 256, FAINT, 1.4)
    s += text(px + 116, py + 278, "А коли треба 5 входів —", 11, INK, "middle")
    s += text(px + 116, py + 294, "працюють ОБИДВІ половини", 11, GREEN, "middle", "bold")
    s += text(px + 116, py + 310, "як дві окремі LUT-5.", 11, INK, "middle")

    save("fig-r07-3m-3-sweet-spot.svg", s)


if __name__ == "__main__":
    fig_lut_is_memory()
    fig_double_exponential()
    fig_sweet_spot()
    print("done.")
