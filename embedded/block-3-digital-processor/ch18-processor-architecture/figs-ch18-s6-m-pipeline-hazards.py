# -*- coding: utf-8 -*-
"""
Фігури для 🧮-вставки до теми §3.5.6 «Конвеєр і хазарди» (Модуль 3, Розділ 18).
Окремий скрипт (головний figs.py не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Стиль (AUTHORING §9) і допоміжні функції — копія з figs.py,
щоб вигляд був єдиний із рештою розділу.
Підписи фігур у тексті — «Рис. 3.5.6m.k».
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
AMBER = "#caa24a"
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
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", GREEN: "aGreen"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── клітинка стадії конвеєра (копія стилю §18.6) ────────────────────────────
_STG = [("Виб", RED, "#fdf4f4"), ("Дек", AMBER, "#fff8e8"), ("Вик", GREEN, "#eef7ee")]


def _pcell(x, y, w, h, stg, faded=False, killed=False):
    name, col, bg = _STG[stg]
    if killed:
        out = rect(x, y, w, h, "#fbecec", RED, 1.4, 4)
        out += text(x + w / 2, y + h * 0.66, name, 11, RED, "middle", "bold")
        # перекреслення — «викинуто»
        out += line(x + 6, y + 6, x + w - 6, y + h - 6, RED, 1.6)
        out += line(x + w - 6, y + 6, x + 6, y + h - 6, RED, 1.6)
        return out
    out = rect(x, y, w, h, "#f4f4f4" if faded else bg, GREY if faded else col, 1.4, 4)
    out += text(x + w / 2, y + h * 0.66, name, 11, GREY if faded else col, "middle", "bold")
    return out


def _ticks(x0, y, n, cw, col=GREY):
    out = ""
    for t in range(n):
        out += text(x0 + t * cw + cw / 2, y, f"т{t + 1}", 10, col, "middle", "bold")
    return out


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.5.6m.1 — штраф розгалуження: скільки тактів викидає промах
# П'ятистадійний конвеєр; гілка з'ясовується аж на стадії Вик (такт 5),
# тож три команди, вибрані «по інерції» слідом, треба викинути → штраф = 3.
# ════════════════════════════════════════════════════════════════════════════
def fig_branch_penalty():
    W, H = 940, 432
    s = header(W, H)
    s += text(W / 2, 34, "Штраф розгалуження: промах спорожнює вже почату частину конвеєра", 19, INK, "middle", "bold")
    s += text(W / 2, 56,
              "5 стадій; куди піде гілка, відомо аж по стадії «Вик» — а до того конвеєр уже втягнув наступні команди «по інерції»",
              11.5, GREY, "middle", style="italic")

    # 5-стадійний конвеєр: Виб, Дек, Вик(=рах), Пам, Зап — але кольорів три,
    # тож показуємо 5 стадій назвами, а заливку беремо з палітри по колу.
    stage_names = ["Виб", "Дек", "Вик", "Пам", "Зап"]
    stage_col = [RED, AMBER, GREEN, BLUE, INK]
    stage_bg = ["#fdf4f4", "#fff8e8", "#eef7ee", "#eef1fb", "#f1f1f1"]

    def cell(x, y, w, h, st, killed=False):
        col, bg, nm = stage_col[st], stage_bg[st], stage_names[st]
        if killed:
            o = rect(x, y, w, h, "#fbecec", RED, 1.4, 4)
            o += text(x + w / 2, y + h * 0.64, nm, 10.5, RED, "middle", "bold")
            o += line(x + 6, y + 6, x + w - 6, y + h - 6, RED, 1.5)
            o += line(x + w - 6, y + 6, x + 6, y + h - 6, RED, 1.5)
            return o
        o = rect(x, y, w, h, bg, col, 1.4, 4)
        o += text(x + w / 2, y + h * 0.64, nm, 10.5, col, "middle", "bold")
        return o

    cw, ch = 70, 34
    x0, y0 = 250, 104
    NT = 9
    s += _ticks(x0, y0 - 8, NT, cw)

    # рядки команд: (підпис, старт-такт, список стадій, killed?)
    rows = [
        ("BNE  (гілка)", 0, [0, 1, 2, 3, 4], False),   # гілка; рішення на «Вик» = такт 3
        ("наст. +1", 1, [0, 1, 2], True),               # вибрані по інерції — викид
        ("наст. +2", 2, [0, 1], True),
        ("наст. +3", 3, [0], True),
        ("ціль гілки", 4, [0, 1, 2, 3, 4], False),      # правильна — стартує аж після промаху
    ]
    for r, (lbl, start, stages, killed) in enumerate(rows):
        y = y0 + r * (ch + 8)
        lc = RED if killed else (BLUE if lbl == "ціль гілки" else INK)
        s += text(x0 - 14, y + 23, lbl, 11, lc, "end", "bold")
        for j, st in enumerate(stages):
            s += cell(x0 + (start + j) * cw, y, cw - 6, ch, st, killed)

    # позначити момент, коли гілка «розкривається» (кінець стадії Вик першого рядка = такт 3)
    bx = x0 + 3 * cw
    s += line(bx, y0 - 22, bx, y0 + 5 * (ch + 8) - 4, RED, 1.6, "5 4")
    s += text(bx + 6, y0 - 24, "тут гілка стає відома", 10.5, RED, "start", "bold")

    # дужка штрафу над викинутими тактами (т4..т6 — три бульбашки до старту цілі)
    py = y0 + 5 * (ch + 8) + 10
    s += line(x0 + 3 * cw + 2, py, x0 + 6 * cw - 8, py, RED, 2)
    s += line(x0 + 3 * cw + 2, py - 5, x0 + 3 * cw + 2, py + 5, RED, 2)
    s += line(x0 + 6 * cw - 8, py - 5, x0 + 6 * cw - 8, py + 5, RED, 2)
    s += text((x0 + 3 * cw + 2 + x0 + 6 * cw - 8) / 2, py + 20,
              "штраф = 3 такти змарновано (вся почата робота викинута)", 11, RED, "middle", "bold")

    s += text(W / 2, 380,
              "Штраф дорівнює числу тактів від вибірки гілки до того такту, коли її напрям з'ясовано: тут гілку видно на «Вик», тож штраф = 3.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 404,
              "Глибший конвеєр (більше стадій до перевірки гілки) — більший штраф. Передбачення переходів намагається не платити його зовсім.",
              10.5, GREY, "middle", style="italic")
    save("fig-18-6m-1-branch-penalty.svg", s)


# ════════════════════════════════════════════════════════════════════════════
# Рис. 3.5.6m.2 — ефективний CPI росте з частотою гілок і промахами
# Криві CPI = 1 + f·(1−a)·p для трьох частот гілок, по осі — точність a.
# ════════════════════════════════════════════════════════════════════════════
def fig_cpi_curve():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 34, "Скільки коштують розгалуження: ефективний CPI як функція точності передбачення", 18, INK, "middle", "bold")
    s += text(W / 2, 56,
              "CPI ≈ 1 + f · (1 − a) · p   —   f — частка гілок, a — точність вгадування, p — штраф промаху (тут p = 3)",
              11.5, GREY, "middle", style="italic")

    # осі
    L, R = 130, 720
    T, B = 110, 430
    p = 3.0
    a_lo, a_hi = 0.5, 1.0  # точність 50%..100%

    def X(a):
        return L + (a - a_lo) / (a_hi - a_lo) * (R - L)

    cpi_lo, cpi_hi = 1.0, 1.8  # межі осі Y
    def Y(c):
        return B - (c - cpi_lo) / (cpi_hi - cpi_lo) * (B - T)

    s += line(L, T, L, B, INK, 2)
    s += line(L, B, R + 10, B, INK, 2)
    s += text(L - 10, T - 18, "ефективний CPI", 12.5, INK, "start", "bold")
    s += text(R + 16, B + 4, "точність a", 12, INK, "start", "bold")

    # сітка/підписи Y
    for c in [1.0, 1.2, 1.4, 1.6, 1.8]:
        y = Y(c)
        s += line(L - 5, y, R, y, FAINT, 1)
        s += text(L - 10, y + 4, f"{c:.1f}", 11, GREY, "end")
    # ідеал CPI=1
    s += line(L, Y(1.0), R, Y(1.0), GREEN, 1.4, "4 4")
    s += text(R - 4, Y(1.0) - 6, "ідеал конвеєра: CPI = 1", 10.5, GREEN, "end", "bold")
    # підписи X
    for a in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        x = X(a)
        s += line(x, B, x, B + 5, INK, 1.4)
        s += text(x, B + 20, f"{int(a*100)}%", 10.5, GREY, "middle")

    # три криві за часткою гілок
    series = [
        (0.30, RED, "багато гілок (f = 30%)"),
        (0.20, AMBER, "типово (f = 20%)"),
        (0.10, BLUE, "мало гілок (f = 10%)"),
    ]
    for f, col, lbl in series:
        pts = []
        a = a_lo
        while a <= a_hi + 1e-9:
            c = 1.0 + f * (1.0 - a) * p
            pts.append((X(a), Y(c)))
            a += 0.02
        s += polyline(pts, col, 2.6)
        # підпис біля лівого кінця (a=50%)
        c0 = 1.0 + f * (1.0 - a_lo) * p
        s += text(L + 8, Y(c0) - 7, lbl, 10.5, col, "start", "bold")

    # робоча точка: f=20%, a=90% → CPI=1.06
    ax, ay = X(0.90), Y(1.0 + 0.20 * 0.10 * p)
    s += rect(ax - 4, ay - 4, 8, 8, AMBER, INK, 1.4)
    s += arrow(ax + 70, ay - 46, ax + 6, ay - 6, INK, 1.6)
    s += text(ax + 74, ay - 52, "реалістично: f=20%, a=90%, p=3", 10.5, INK, "start", "bold")
    s += text(ax + 74, ay - 38, "→ CPI ≈ 1.06 (втрата лише ~6%)", 10.5, INK, "start")

    # погана точка: f=30%, a=60% → CPI=1.36
    bx, by = X(0.60), Y(1.0 + 0.30 * 0.40 * p)
    s += rect(bx - 4, by - 4, 8, 8, RED, INK, 1.4)
    s += arrow(bx - 60, by - 30, bx - 6, by - 6, RED, 1.6)
    s += text(bx - 64, by - 36, "кепсько: f=30%, a=60% → CPI ≈ 1.36", 10.5, RED, "end", "bold")

    s += text(W / 2, 478,
              "Дві ручки тримають CPI біля 1: менше гілок (f) і краще їх угадувати (a). Сучасні передбачувачі дають a ≈ 95–98%, тож втрати малі.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 502,
              "Глибший конвеєр піднімає штраф p (більше стадій до перевірки гілки) — тому довгі конвеєри особливо бояться непередбачуваних розгалужень.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 526,
              "Це і є «напівкількісний» бік §3.5.6: ідеальне ×N конвеєра з'їдають саме ці доданки.",
              10.5, GREY, "middle", style="italic")
    save("fig-18-6m-2-cpi-curve.svg", s)


if __name__ == "__main__":
    fig_branch_penalty()
    fig_cpi_curve()
    print("done: inserts for 3.5.6")
