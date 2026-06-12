# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для 🧮-вставки до теми §3.4.6 — «IEEE 754 докладно».
Окремий скрипт (головний figs.py не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/. Імена файлів: fig-17-6m-k-<slug>.svg, підписи — Рис. 3.4.6m.k.

Стиль (AUTHORING §9) узгоджений із figs.py розділу: білий фон; «1» червоний,
«0»/від'ємне синій; правильний результат зелений; стрілки через marker;
шрифт sans-serif. Допоміжні функції скопійовано з figs.py розділу (розділи не
ділять коду, щоб loop'и не конфліктували).
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
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
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


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=15, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, Menlo, monospace" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── допоміжне: ряд бітових клітинок ─────────────────────────────────────────
def bitcells(x, y, bits, cw, ch, fill, fg, sw=1.4, size=14):
    """bits: рядок із '0'/'1'. Повертає svg."""
    out = ""
    for i, b in enumerate(bits):
        cx = x + i * cw
        out += rect(cx, y, cw, ch, fill, INK, sw)
        out += text(cx + cw / 2, y + ch * 0.70, b, size, fg, "middle", "bold")
    return out


# ── Рис. 3.4.6m.1 — побітове декодування одного float32 (число −3.5) ─────────
def fig_decode():
    W, H = 980, 600
    s = header(W, H)
    s += text(W / 2, 32, "Розбираємо один float32 по бітах: як 32 нулі та одиниці стають числом",
              21, INK, "middle", "bold")
    s += text(W / 2, 54, "беремо конкретний запис 1 10000000 11000000000000000000000 і відновлюємо значення крок за кроком",
              12.5, GREY, "middle", style="italic")

    sign = "1"
    expo = "10000000"
    mant = "11000000000000000000000"

    # ── рядок із 32 клітинок, поля різного кольору ──────────────────────────
    cw, ch = 25, 32
    x0 = (W - 32 * cw) / 2
    y0 = 84
    # знак (1) — фіолетово-сірий, порядок (8) — синюватий, мантиса (23) — теплий
    s += bitcells(x0, y0, sign, cw, ch, "#f0e8f6", INK)
    s += bitcells(x0 + cw, y0, expo, cw, ch, "#e7eefb", BLUE)
    s += bitcells(x0 + 9 * cw, y0, mant, cw, ch, "#fbf3e4", AMBER)
    # номери бітів (31 … 0): 31=знак, 30..23=порядок, 22..0=мантиса
    s += mono(x0 + 0.5 * cw, y0 - 7, "31", 10, GREY, "middle")
    s += mono(x0 + 1.5 * cw, y0 - 7, "30", 10, GREY, "middle")
    s += mono(x0 + 8.5 * cw, y0 - 7, "23", 10, GREY, "middle")
    s += mono(x0 + 9.5 * cw, y0 - 7, "22", 10, GREY, "middle")
    s += mono(x0 + 31.5 * cw, y0 - 7, "0", 10, GREY, "middle")

    # дужки-підписи полів
    by = y0 + ch + 6
    s += line(x0, by, x0 + cw, by, INK, 1.6)
    s += text(x0 + 0.5 * cw, by + 16, "знак", 12, INK, "middle", "bold")
    s += line(x0 + cw, by, x0 + 9 * cw, by, BLUE, 1.6)
    s += text(x0 + 5 * cw, by + 16, "порядок — 8 бітів", 12, BLUE, "middle", "bold")
    s += line(x0 + 9 * cw, by, x0 + 32 * cw, by, AMBER, 1.6)
    s += text(x0 + 20.5 * cw, by + 16, "мантиса (дробова частина) — 23 біти", 12, AMBER, "middle", "bold")

    # ── три колонки розбору ─────────────────────────────────────────────────
    colY = by + 56
    col1 = x0 + 1.5 * cw
    col2 = x0 + 12 * cw
    col3 = x0 + 23 * cw
    bw, bh = 230, 150

    # знак
    s += rect(col1 - 16, colY, bw, bh, "#faf6fc", INK, 1.6, 8)
    s += text(col1 + bw / 2 - 16, colY + 24, "1) Знак", 14, INK, "middle", "bold")
    s += mono(col1, colY + 52, "біт = 1", 13, INK)
    s += text(col1, colY + 76, "1 → мінус", 13, BLUE)
    s += text(col1, colY + 100, "0 була б +", 12, GREY)
    s += mono(col1, colY + 130, "(−1)¹ = −1", 13, BLUE, "start", "bold")

    # порядок
    s += rect(col2 - 16, colY, bw, bh, "#f5f8fe", BLUE, 1.6, 8)
    s += text(col2 + bw / 2 - 16, colY + 24, "2) Порядок", 14, INK, "middle", "bold")
    s += mono(col2, colY + 52, "10000000₂ = 128", 12.5, INK)
    s += text(col2, colY + 76, "віднімаємо зсув 127:", 12, GREY)
    s += mono(col2, colY + 100, "128 − 127 = 1", 13, BLUE, "start", "bold")
    s += text(col2, colY + 130, "степінь двійки = 2¹", 12.5, BLUE)

    # мантиса
    s += rect(col3 - 16, colY, bw + 10, bh, "#fdf8ee", AMBER, 1.6, 8)
    s += text(col3 + bw / 2 - 12, colY + 24, "3) Мантиса", 14, INK, "middle", "bold")
    s += mono(col3, colY + 52, "11000…₂ → .11₂", 12.5, INK)
    s += text(col3, colY + 76, "додаємо приховану 1:", 12, GREY)
    s += mono(col3, colY + 100, "1.11₂ = 1.75", 13, AMBER, "start", "bold")
    s += text(col3, colY + 130, "(½ + ¼ після коми)", 12, GREY)

    # ── підсумкова формула ──────────────────────────────────────────────────
    fy = colY + bh + 40
    s += rect(x0, fy, 32 * cw, 46, "#eef9ee", GREEN, 2.0, 8)
    s += mono(W / 2, fy + 22, "значення = (−1)ˢ × 1.мантиса × 2^(порядок−127)", 14, INK, "middle", "bold")
    s += mono(W / 2, fy + 40, "= (−1) × 1.75 × 2¹ = −3.5", 14, GREEN, "middle", "bold")

    # стрілки від колонок до формули
    s += arrow(col1 + bw / 2 - 16, colY + bh, col1 + bw / 2 - 16, fy - 2, INK, 1.6)
    s += arrow(col2 + bw / 2 - 16, colY + bh, col2 + bw / 2 - 16, fy - 2, BLUE, 1.6)
    s += arrow(col3 + bw / 2 - 12, colY + bh, col3 + bw / 2 - 12, fy - 2, AMBER, 1.6)

    s += text(W / 2, H - 16,
              "Зворотний хід (закодувати число) — той самий ланцюг навпаки: винести 2^порядок, відкинути провідну 1, додати зсув 127.",
              12, GREY, "middle", style="italic")
    save("fig-17-6m-1-decode.svg", s)


# ── Рис. 3.4.6m.2 — що означають 256 значень поля порядку + числова вісь ─────
def fig_exponent_map():
    W, H = 980, 580
    s = header(W, H)
    s += text(W / 2, 32, "Поле порядку керує всім: ті самі 8 бітів задають чотири різні режими",
              21, INK, "middle", "bold")
    s += text(W / 2, 54, "крайні значення порядку (000…0 і 111…1) зарезервовані під особливі числа — звідси нуль, денормалі, ∞ і NaN",
              12.5, GREY, "middle", style="italic")

    # ── таблиця-смуга значень порядку ───────────────────────────────────────
    tx, ty = 60, 84
    tw = W - 120
    rowh = 40
    cols = [0.0, 0.16, 0.56, 0.84, 1.0]  # частки ширини: межі стовпців
    labels = [
        ("00000000", "усе нулі", "#eef2ff"),
        ("00000001 … 11111110", "1 … 254 (звичайні)", "#eef9ee"),
        ("11111111", "усе одиниці", "#fdeeee"),
    ]
    # три блоки: 0 | 1..254 | 255
    seg = [(0.0, 0.18), (0.18, 0.82), (0.82, 1.0)]
    fills = ["#eef2ff", "#eef9ee", "#fdeeee"]
    edge = [BLUE, GREEN, RED]
    head = ["порядок = 0", "порядок = 1 … 254", "порядок = 255"]
    sub = ["(біти 00000000)", "(звичайний діапазон)", "(біти 11111111)"]
    for i, (a, b) in enumerate(seg):
        xa = tx + a * tw
        xb = tx + b * tw
        s += rect(xa, ty, xb - xa, rowh, fills[i], edge[i], 1.8, 6)
        s += mono((xa + xb) / 2, ty + 18, head[i], 13, edge[i], "middle", "bold")
        s += text((xa + xb) / 2, ty + 34, sub[i], 11, GREY, "middle")

    # ── що кожен блок означає (дві гілки за мантисою) ───────────────────────
    cy = ty + rowh + 30
    box_w = 250
    boxh = 92

    def two_branch(cx, title_col, m0_title, m0_body, mN_title, mN_body):
        out = ""
        # мантиса = 0
        out += rect(cx - box_w / 2, cy, box_w, boxh, "#ffffff", title_col, 1.6, 8)
        out += text(cx, cy + 20, m0_title, 12.5, title_col, "middle", "bold")
        for j, ln in enumerate(m0_body):
            out += text(cx, cy + 40 + j * 17, ln, 11.5, INK, "middle")
        # мантиса ≠ 0
        out += rect(cx - box_w / 2, cy + boxh + 14, box_w, boxh, "#ffffff", title_col, 1.6, 8)
        out += text(cx, cy + boxh + 34, mN_title, 12.5, title_col, "middle", "bold")
        for j, ln in enumerate(mN_body):
            out += text(cx, cy + boxh + 54 + j * 17, ln, 11.5, INK, "middle")
        return out

    cx0 = tx + 0.09 * tw
    cx1 = tx + 0.50 * tw
    cx2 = tx + 0.91 * tw
    # стрілки від смуги вниз
    s += arrow(cx0, ty + rowh, cx0, cy - 2, BLUE, 1.6)
    s += arrow(cx1, ty + rowh, cx1, cy - 2, GREEN, 1.6)
    s += arrow(cx2, ty + rowh, cx2, cy - 2, RED, 1.6)

    s += two_branch(cx0, BLUE,
                    "мантиса = 0  →  ±0",
                    ["рівно нуль", "(є і +0, і −0)"],
                    "мантиса ≠ 0  →  денормаль",
                    ["0.мантиса × 2⁻¹²⁶", "(приховано 0, не 1)"])
    s += two_branch(cx1, GREEN,
                    "будь-яка мантиса",
                    ["1.мантиса × 2^(e−127)", "приховано провідну 1"],
                    "це 99,99 % усіх чисел",
                    ["звичайна арифметика", "(див. Рис. 3.4.6m.1)"])
    s += two_branch(cx2, RED,
                    "мантиса = 0  →  ±∞",
                    ["переповнення,", "ділення на 0"],
                    "мантиса ≠ 0  →  NaN",
                    ["0/0, √(−1);", "заразний"])

    # ── числова вісь біля нуля: денормалі заповнюють «діру» ─────────────────
    ax = tx
    aw = tw
    ayy = cy + 2 * boxh + 14 + 64
    s += text(W / 2, ayy - 20, "Числова вісь біля нуля (логарифмічно за модулем): денормалі рівномірно «дотягують» до 0",
              12.5, INK, "middle", "bold")
    s += line(ax, ayy, ax + aw, ayy, INK, 2)
    s += arrow(ax + aw, ayy, ax + aw + 10, ayy, INK, 2)
    # нуль ліворуч
    s += text(ax, ayy + 22, "0", 13, INK, "middle", "bold")
    s += line(ax, ayy - 7, ax, ayy + 7, INK, 2)

    # зона денормалей (рівний крок) — синя; зона нормальних — зелена
    den_x0 = ax + 0.06 * aw
    norm_x0 = ax + 0.40 * aw
    # денормалі: рівномірні риски
    n_den = 9
    for k in range(n_den):
        xx = den_x0 + (norm_x0 - den_x0) * k / (n_den - 1)
        s += line(xx, ayy - 6, xx, ayy + 6, BLUE, 1.6)
    s += text((den_x0 + norm_x0) / 2, ayy - 14, "денормалі: рівний крок 2⁻¹⁴⁹", 11.5, BLUE, "middle", "bold")
    s += text((den_x0 + norm_x0) / 2, ayy + 24, "плавне згасання до нуля", 11, BLUE, "middle")

    # нормальні: крок росте (риски рідшають праворуч)
    pos = 0.0
    step = (1.0 - 0.40) * aw
    xx = norm_x0
    frac = 0.10
    while xx < ax + aw - 8:
        s += line(xx, ayy - 8, xx, ayy + 8, GREEN, 1.8)
        gap = (ax + aw - norm_x0) * frac
        xx += gap
        frac *= 1.45
    s += text((norm_x0 + ax + aw) / 2, ayy - 16, "нормальні: крок подвоюється щопорядку", 11.5, GREEN, "middle", "bold")
    # межа
    s += line(norm_x0, ayy - 26, norm_x0, ayy + 14, GREY, 1.4, "4 3")
    s += mono(norm_x0, ayy + 30, "2⁻¹²⁶", 11, GREY, "middle")
    s += text(den_x0, ayy + 38, "2⁻¹⁴⁹ (найменше)", 10.5, BLUE, "middle")

    # ── контраст: без денормалей була б діра ───────────────────────────────
    s += rect(ax, H - 50, aw, 32, "#fff6e6", AMBER, 1.4, 8)
    s += text(W / 2, H - 29,
              "Без денормалей усе між 0 і 2⁻¹²⁶ різко падало б у нуль — «діра», де віднімання близьких чисел брехало б. Денормалі її закривають.",
              12, INK, "middle")
    save("fig-17-6m-2-exponent-map.svg", s)


if __name__ == "__main__":
    fig_decode()
    fig_exponent_map()
    print("ch17 s6m (ieee754 details) figures done.")
