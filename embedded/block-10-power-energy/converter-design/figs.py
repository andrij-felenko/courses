# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 10.2 — «Спроєктувати і виміряти перетворювач» (Модуль 10).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються по темах
(Рис. 10.2.T.k). Спільні допоміжні функції — копія з Розділу 10.1 (єдиний вигляд).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
COPP  = "#b5763a"
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


def poly(points, color=INK, w=2.4, dash=None):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def polygon(points, fill, opacity=1.0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    op = f' fill-opacity="{opacity}"' if opacity != 1.0 else ""
    return f'<polygon points="{pts}" fill="{fill}"{op}/>\n'


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def coil_h(x0, x1, y, loops=4, r=10, color=COPP, w=2.6):
    seg = (x1 - x0) / loops
    d = f'M {x0:.1f} {y:.1f} '
    for i in range(loops):
        xb = x0 + seg * (i + 1)
        d += f'A {seg/2:.1f} {r:.1f} 0 0 1 {xb:.1f} {y:.1f} '
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 10.2.1.1 — від бюджету до ТЗ ────────────────────────────────────────
def fig_budget_to_spec():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Рядок бюджету — це ще не ТЗ: одна шина → ціла специфікація", 17.5,
              INK, "middle", "bold")
    # бюджетний рядок
    s += rect(40, 150, 220, 90, "#eef3fb", BLUE, 2, 10)
    s += text(150, 180, "Бюджет живлення", 12, BLUE, "middle", "bold")
    s += text(150, 204, "(§8.1.4):", 10.5, GREY, "middle")
    s += text(150, 226, "«шина 5 В, 3 А»", 13, INK, "middle", "bold")
    s += arrow(264, 195, 330, 195, INK, 2.4)
    s += text(297, 184, "розгорнути", 9.5, GREY, "middle", style="italic")
    # специфікація
    s += rect(340, 70, 540, 320, "#ffffff", GREEN, 2, 10)
    s += text(610, 96, "ТЗ перетворювача", 13.5, GREEN, "middle", "bold")
    rows = [
        "Vвх: діапазон  (min … max), не одне число",
        "Vвих: ціль + допуск  (5.0 В ± 2 %)",
        "Iвих: максимальний + піковий/перехідний",
        "Пульсація виходу:  ≤ … мВ (за навантаженням)",
        "Перехідний процес:  провал ≤ …, час ≤ …",
        "ККД:  ціль у заданих точках навантаження",
        "Тепло:  Tамб, допустиме нагрівання",
        "ЕМС / шум, розмір, ціна",
        "Захисти:  OCP / OVP / теплозахист",
    ]
    for i, r in enumerate(rows):
        y = 124 + i * 29
        s += circle(362, y - 4, 3, GREEN, GREEN, 0)
        s += text(376, y, r, 11.5, INK, "start")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 17, "Перетворювач, побудований без ТЗ, майже завжди побудований не так. Спершу — специфікація, тоді деталі", 10.5, INK, "middle")
    save("fig-10-1-1-budget.svg", s)


# ── Рис. 10.2.1.2 — діапазон входу ───────────────────────────────────────────
def fig_vin_range():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Vвх — це діапазон, а не число: кожен край щось диктує", 18, INK, "middle", "bold")
    ox = 110
    y = 150
    s += line(ox, y, 800, y, INK, 2)
    s += arrow(790, y, 810, y, INK, 2)
    s += text(812, y + 4, "Vвх", 12, INK, "start", "bold")
    vmin, vmax = 280, 620
    s += line(vmin, y - 12, vmin, y + 12, RED, 3)
    s += line(vmax, y - 12, vmax, y + 12, RED, 3)
    s += line(vmin, y, vmax, y, GREEN, 6)
    s += text((vmin + vmax) / 2, y - 22, "робочий діапазон", 12, GREEN, "middle", "bold")
    s += text(vmin, y + 30, "Vвх min", 12, RED, "middle", "bold")
    s += text(vmin, y + 46, "(батарея сіла,", 9.5, GREY, "middle")
    s += text(vmin, y + 59, "USB просів)", 9.5, GREY, "middle")
    s += text(vmax, y + 30, "Vвх max", 12, RED, "middle", "bold")
    s += text(vmax, y + 46, "(повний заряд,", 9.5, GREY, "middle")
    s += text(vmax, y + 59, "сплеск мережі)", 9.5, GREY, "middle")
    # що диктує кожен край
    s += rect(60, 250, 360, 120, "#eef3fb", BLUE, 1.8, 10)
    s += text(240, 276, "Vвх min диктує:", 12.5, BLUE, "middle", "bold")
    for i, t in enumerate(["• чи дотягне buck (запас на dropout)", "• чи треба boost/buck-boost узагалі", "• найбільша шпаруватість D"]):
        s += text(80, 300 + i * 22, t, 11, INK, "start")
    s += rect(480, 250, 380, 120, "#fbe9e7", RED, 1.8, 10)
    s += text(670, 276, "Vвх max диктує:", 12.5, RED, "middle", "bold")
    for i, t in enumerate(["• номінали напруги ключів і конденсаторів", "• найгіршу пульсацію струму (тема 10.1.2)", "• пусковий струм (інраш), стрес на старті"]):
        s += text(500, 300 + i * 22, t, 11, INK, "start")
    save("fig-10-1-2-vinrange.svg", s)


# ── Рис. 10.2.1.3 — вихід: ціль, допуск, пульсація ───────────────────────────
def fig_output_spec():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Вихід: ціль ± допуск, і пульсація всередині нього", 18, INK, "middle", "bold")
    ox, oy = 110, 230
    s += arrow(ox, 360, ox, 80, INK, 1.6)
    s += arrow(ox, oy, 840, oy, INK, 1.6)
    s += text(ox - 10, 88, "Vвих", 11, INK, "end", "bold")
    s += text(842, oy + 4, "t", 12, INK, "start", "bold")
    nom = 170
    tol = 40
    # смуга допуску
    s += f'<rect x="{ox}" y="{nom-tol}" width="700" height="{2*tol}" fill="{GREEN}" fill-opacity="0.10"/>\n'
    s += line(ox, nom, 810, nom, GREY, 1.4, dash="6,5")
    s += line(ox, nom - tol, 810, nom - tol, GREEN, 1.4)
    s += line(ox, nom + tol, 810, nom + tol, GREEN, 1.4)
    s += text(816, nom + 4, "5.0 В", 11, INK, "start", "bold")
    s += text(816, nom - tol + 4, "+2%", 10, GREEN, "start", "bold")
    s += text(816, nom + tol + 4, "−2%", 10, GREEN, "start", "bold")
    # пульсація (дрібна хвиля) навколо nom
    pts = []
    for i in range(0, 700, 4):
        xx = ox + i
        yy = nom - 12 * math.sin(i / 18.0)
        pts.append((xx, yy))
    s += poly(pts, RED, 2)
    s += text(300, nom - 28, "пульсація (пік-пік) ≤ задане", 11.5, RED, "middle", "bold")
    s += arrow(560, nom - 12, 560, nom + 12, INK, 1.4)
    s += arrow(560, nom + 12, 560, nom - 12, INK, 1.4)
    s += text(580, nom + 4, "ΔVпп", 11, INK, "start", "bold")
    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 18, "Допуск задає СЕРЕДНЮ напругу (точність), пульсація — її дрібне коливання. Логіка терпить багато, опора АЦП — мало", 10.5, INK, "middle")
    save("fig-10-1-3-output.svg", s)


# ── Рис. 10.2.1.4 — перехідний процес (реакція на стрибок) ───────────────────
def fig_transient():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 32, "Перехідний процес: стрибок навантаження → провал → відновлення", 17.5,
              INK, "middle", "bold")
    ox = 110
    # струм навантаження (верх)
    s += text(ox - 16, 95, "Iнаван", 11, INK, "end", "bold")
    b1 = 150
    s += line(ox, b1 + 20, 360, b1 + 20, COPP, 2.6)
    s += line(360, b1 + 20, 360, b1 - 20, COPP, 2.6)
    s += line(360, b1 - 20, 820, b1 - 20, COPP, 2.6)
    s += text(230, b1 + 36, "0.5 А", 10, GREY, "middle")
    s += text(590, b1 - 30, "3 А (різкий стрибок)", 10, GREY, "middle")
    # вихідна напруга (низ)
    s += text(ox - 16, 250, "Vвих", 11, INK, "end", "bold")
    nom = 270
    s += line(ox, nom, 820, nom, GREY, 1.3, dash="6,5")
    s += text(826, nom + 4, "ціль", 10, GREY, "start")
    # провал і відновлення
    pts = [(ox, nom), (360, nom), (385, nom + 46), (430, nom + 10), (480, nom - 6), (520, nom), (820, nom)]
    s += poly(pts, BLUE, 3)
    s += arrow(385, nom, 385, nom + 46, RED, 1.6)
    s += text(330, nom + 40, "провал ≤ ΔVмакс", 11, RED, "end", "bold")
    s += line(360, nom + 60, 520, nom + 60, INK, 1.3)
    s += text(440, nom + 74, "час встановлення ≤ tвст", 11, INK, "middle", "bold")
    # дзвін — погано
    s += text(640, nom - 22, "якщо «дзвенить» — запас стійкості малий", 10.5, AMBER, "middle", style="italic")
    s += rect(70, H - 40, W - 140, 28, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 22, "Критерій здоров'я (без теорії керування — Розділ 10.2.5): стрибок навантаження дає короткий провал і чисте", 10.5, INK, "middle")
    s += text(W / 2, H - 9, "відновлення БЕЗ дзвону. Глибина провалу й час — у ТЗ.", 10.5, INK, "middle")
    save("fig-10-1-4-transient.svg", s)


# ── Рис. 10.2.1.5 — осі ТЗ (контрольний список) ──────────────────────────────
def fig_spec_axes():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "Осі ТЗ: що мусить бути пришпилено перед вибором деталей", 18,
              INK, "middle", "bold")
    cards = [
        ("Vвх", "діапазон min…max", BLUE),
        ("Vвих", "ціль + допуск", GREEN),
        ("Iвих", "макс + пік", BLUE),
        ("Пульсація", "≤ … мВ", RED),
        ("Перехідний", "провал, час", AMBER),
        ("ККД", "у точках навант.", GREEN),
        ("Тепло", "Tамб, нагрів", RED),
        ("ЕМС/шум", "біля радіо?", AMBER),
        ("Розмір/ціна", "межі плати/BOM", GREY),
        ("Захисти", "OCP/OVP/тепло", BLUE),
    ]
    cols = 5
    cw, ch = 165, 86
    x0, y0 = 35, 70
    for i, (t, sub, c) in enumerate(cards):
        cx = x0 + (i % cols) * (cw + 9)
        cy = y0 + (i // cols) * (ch + 18)
        s += rect(cx, cy, cw, ch, "#ffffff", c, 1.8, 10)
        s += text(cx + cw / 2, cy + 34, t, 14, c, "middle", "bold")
        s += text(cx + cw / 2, cy + 58, sub, 11, INK, "middle")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Пропущена вісь = прихований ризик: забув діапазон входу — перетворювач відмовить на сівшій батареї;", 10.5, INK, "middle")
    s += text(W / 2, H - 9, "забув перехідний — логіка перезаватажиться на стрибку струму.", 10.5, INK, "middle")
    save("fig-10-1-5-axes.svg", s)


# ── Рис. 10.2.1.6 — приклад ТЗ (специфікація вузла) ──────────────────────────
def fig_spec_sheet():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Приклад ТЗ: шина 5 В логіки на дроні (4S)", 18, INK, "middle", "bold")
    rows = [
        ("Vвх", "12.0 – 16.8 В (4S LiPo), сплеск до 18 В"),
        ("Vвих", "5.0 В ± 2 %"),
        ("Iвих", "3 А тривало, 4 А пік"),
        ("Пульсація", "≤ 50 мВ пік-пік"),
        ("Перехідний", "0.5→3 А: провал ≤ 150 мВ, відн. ≤ 50 мкс, без дзвону"),
        ("ККД", "≥ 90 % @ 3 А, ≥ 80 % @ 0.3 А"),
        ("Тепло", "Tамб 60 °C, нагрів ≤ +40 °C"),
        ("ЕМС", "поряд радіо → стала частота (forced-PWM)"),
        ("Захисти", "OCP, теплозахист, обмеження інрашу"),
    ]
    x0, y0 = 80, 64
    rw, rh = 740, 36
    for i, (k, v) in enumerate(rows):
        y = y0 + i * rh
        fill = "#ffffff" if i % 2 == 0 else "#f6f6f6"
        s += rect(x0, y, rw, rh, fill, FAINT, 1, 0)
        s += rect(x0, y, 160, rh, "#eef3fb", FAINT, 1, 0)
        s += text(x0 + 14, y + 23, k, 12, BLUE, "start", "bold")
        s += text(x0 + 178, y + 23, v, 11.5, INK, "start")
    s += text(W / 2, H - 16, "Таке ТЗ — вхід у наступні теми: контролер, частота, котушка, конденсатори, розводка, вимірювання", 10.5, GREY, "middle", style="italic")
    save("fig-10-1-6-spec.svg", s)


# ── Рис. 10.2.2.1 — рівні інтеграції контролера ──────────────────────────────
def fig_levels():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Три рівні реалізації: від контролера до готового модуля", 18,
              INK, "middle", "bold")
    cards = [
        ("Контролер + зовнішні MOSFET", BLUE,
         ["ключі окремо, контролер ними керує", "+ будь-яка потужність, гнучко, дешеві ключі", "− найбільше роботи й місця, складна розводка"]),
        ("Інтегрований switcher", GREEN,
         ["ключі ВСЕРЕДИНІ чипа", "+ просто, компактно, мало деталей", "− стеля за струмом (кілька ампер)"]),
        ("Готовий power-модуль", AMBER,
         ["контролер + ключі + котушка в корпусі", "+ найпростіше й найшвидше, мала площа", "− найдорожче, менш гнучко"]),
    ]
    for i, (title, c, lines) in enumerate(cards):
        x = 35 + i * 295
        s += rect(x, 70, 270, 250, "#ffffff", c, 2, 12)
        s += text(x + 135, 100, title, 12.5, c, "middle", "bold")
        s += line(x + 20, 114, x + 250, 114, FAINT, 1)
        for j, ln in enumerate(lines):
            col = GREEN if ln.startswith("+") else (RED if ln.startswith("−") else INK)
            s += text(x + 18, 142 + j * 46, ln, 10.5, col, "start", "bold" if ln[0] in "+−" else "normal")
    # стрілка інтеграції
    s += arrow(60, 345, 860, 345, GREY, 2)
    s += text(460, 365, "більше інтеграції → простіше, але дорожче й менш гнучко →", 11, GREY, "middle", style="italic")
    save("fig-10-2-1-levels.svg", s)


# ── Рис. 10.2.2.2 — компроміс частоти ────────────────────────────────────────
def fig_freq():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Частота комутації: менша магнетика проти більших втрат", 18,
              INK, "middle", "bold")
    ox, oy = 110, 340
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += arrow(ox, oy, ox, 80, INK, 1.6)
    s += text(822, oy + 4, "частота f →", 11, INK, "start", "bold")
    s += text(ox - 10, 88, "вартість", 11, INK, "end", "bold")
    def X(t): return ox + t * 680
    # магнетика ∝ 1/f (спадає)
    mag = [(X(t), oy - 230 * (0.12 / (0.12 + t * 0.9))) for t in [i / 40 for i in range(41)]]
    s += poly(mag, BLUE, 3)
    s += text(X(0.18), oy - 165, "розмір котушки й C ∝ 1/f", 11, BLUE, "start", "bold")
    # втрати ∝ f (зростають)
    los = [(X(t), oy - 20 - 240 * t) for t in [i / 40 for i in range(41)]]
    s += poly(los, RED, 3)
    s += text(X(0.62), oy - 200, "втрати на перемиканні ∝ f", 11, RED, "start", "bold")
    # сума (долина)
    tot = []
    for i in range(41):
        t = i / 40
        mg = 230 * (0.12 / (0.12 + t * 0.9))
        ls = 20 + 240 * t
        tot.append((X(t), oy - (mg + ls) / 1.7))
    s += poly(tot, GREEN, 3)
    s += text(X(0.30), oy - 95, "сукупно", 11, GREEN, "start", "bold")
    # солодке місце
    s += line(X(0.42), oy, X(0.42), 110, AMBER, 1.6, dash="5,5")
    s += text(X(0.42), 102, "розумна частота", 11, AMBER, "middle", "bold")
    # підписи осі
    for t, lb in [(0.08, "100 кГц"), (0.42, "0.5–1 МГц"), (0.85, "кілька МГц")]:
        s += text(X(t), oy + 20, lb, 9.5, GREY, "middle")
    s += rect(70, H - 36, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 18, "Вища f робить котушку й конденсатори дрібними (тому сучасні БЖ малі), та задорого — і втрати на перемиканні з'їдають ККД і гріють", 10.5, INK, "middle")
    save("fig-10-2-2-freq.svg", s)


# ── Рис. 10.2.2.3 — анатомія втрат на перемиканні ────────────────────────────
def fig_swloss():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 32, "Звідки втрати: перекриття V та I на кожному перемиканні", 18,
              INK, "middle", "bold")
    ox, oy = 110, 250
    s += arrow(ox, oy + 10, ox, 80, INK, 1.5)
    s += arrow(ox, oy, 700, oy, INK, 1.5)
    s += text(702, oy + 4, "t", 12, INK, "start", "bold")
    # V зростає, I спадає під час вимкнення
    s += poly([(ox, oy - 10), (300, oy - 10), (360, oy - 150), (680, oy - 150)], RED, 2.6)
    s += text(560, oy - 160, "напруга на ключі V", 11, RED, "middle", "bold")
    s += poly([(ox, oy - 150), (300, oy - 150), (360, oy - 10), (680, oy - 10)], BLUE, 2.6)
    s += text(200, oy - 160, "струм ключа I", 11, BLUE, "middle", "bold")
    # перекриття — заштрихована зона втрат
    s += polygon([(300, oy), (300, oy - 150), (360, oy - 10), (360, oy)], AMBER, 0.35)
    s += polygon([(300, oy), (360, oy), (360, oy - 10), (330, oy - 75), (300, oy - 150)], "#fff", 0.0)
    s += text(420, oy - 70, "перекриття V×I", 11, AMBER, "start", "bold")
    s += text(420, oy - 54, "= енергія в тепло", 10, INK, "start")
    s += arrow(415, oy - 62, 345, oy - 72, AMBER, 1.6)
    # формула
    s += rect(60, 300, W - 120, 70, "#f6f6f6", GREY, 1.4, 10)
    s += text(W / 2, 326, "Pперемик ≈ ½·Vвх·Iнаван·(tвкл+tвикл)·f   +   Qg·Vкер·f", 14, INK, "middle", "bold")
    s += text(W / 2, 350, "обидві складові ∝ f: що частіше перемикаєш, то більше тепла (від перекриття й перезаряду затвора, §2.7.7)", 10.5, GREY, "middle")
    s += rect(70, H - 30, W - 140, 22, "#fbf7ec", AMBER, 1.4, 8)
    s += text(W / 2, H - 15, "Тому частоту не задирають безмежно: кожне ввімкнення-вимкнення коштує енергії, і ця ціна росте лінійно з f", 10.5, INK, "middle")
    save("fig-10-2-3-swloss.svg", s)


# ── Рис. 10.2.2.4 — частота й EMI ────────────────────────────────────────────
def fig_emi():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Частота і завади: гармоніки та чутливі смуги", 18, INK, "middle", "bold")
    ox, oy = 100, 250
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += arrow(ox, oy, ox, 80, INK, 1.6)
    s += text(822, oy + 4, "частота", 11, INK, "start", "bold")
    s += text(ox - 10, 88, "амплітуда", 11, INK, "end", "bold")
    # чутлива смуга
    s += f'<rect x="380" y="90" width="120" height="{oy-90}" fill="{RED}" fill-opacity="0.10"/>\n'
    s += text(440, 104, "чутлива смуга", 10, RED, "middle", "bold")
    s += text(440, 118, "(напр. радіо)", 9, RED, "middle")
    # гармоніки f_sw
    for k, h in [(1, 150), (2, 96), (3, 64), (4, 44), (5, 30)]:
        x = ox + 60 + (k - 1) * 90
        s += line(x, oy, x, oy - h, BLUE, 3)
        s += text(x, oy + 16, f"{k}·f" if k > 1 else "f", 9.5, GREY, "middle")
    # спред-спектрум — розмазування
    s += text(650, 150, "спред-спектрум:", 11, GREEN, "middle", "bold")
    s += text(650, 166, "тремтіння f розмазує", 10, INK, "middle")
    s += text(650, 180, "піки в смугу (нижчі)", 10, INK, "middle")
    s += poly([(600, oy - 30), (620, oy - 38), (640, oy - 34), (660, oy - 40), (680, oy - 33), (700, oy - 39)], GREEN, 2.4)
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "f і її гармоніки (2f, 3f…) не повинні падати в чутливу смугу. Частоту підбирають так, щоб гармоніки минали радіо;", 10.5, INK, "middle")
    s += text(W / 2, H - 9, "спред-спектрум розмазує гострі піки в ширшу смугу, знижуючи їх — корисно для проходження ЕМС-тестів.", 10.5, INK, "middle")
    save("fig-10-2-4-emi.svg", s)


# ── Рис. 10.2.2.5 — струмова стеля ───────────────────────────────────────────
def fig_current_cap():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 32, "Скільки струму: стеля інтегрованого проти зовнішніх ключів", 17.5,
              INK, "middle", "bold")
    ox, oy = 120, 300
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += text(822, oy + 4, "Iвих", 11, INK, "start", "bold")
    def X(a): return ox + a * 19
    for a in (1, 3, 6, 10, 20, 30):
        s += line(X(a), oy, X(a), oy + 5, GREY, 1)
        s += text(X(a), oy + 20, f"{a} А", 9.5, GREY, "middle")
    bars = [
        ("інтегрований switcher", 0.5, 6, GREEN, 110),
        ("power-модуль", 0.5, 12, AMBER, 160),
        ("контролер + зовн. MOSFET", 1, 30, BLUE, 210),
    ]
    for name, a0, a1, c, y in bars:
        s += rect(X(a0), y, X(a1) - X(a0), 32, "#ffffff", c, 2, 6)
        s += f'<rect x="{X(a0):.0f}" y="{y}" width="{X(a1)-X(a0):.0f}" height="32" rx="6" fill="{c}" fill-opacity="0.13"/>\n'
        s += text(X(a0) + 10, y + 21, name, 11, c, "start", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "Беруть за Iвих із ТЗ + запас: до кількох ампер — інтегрований; десятки ампер — лише зовнішні ключі", 10.5, INK, "middle")
    save("fig-10-2-5-current.svg", s)


# ── Рис. 10.2.2.6 — режим керування (якісно) ─────────────────────────────────
def fig_control_mode():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Режим керування: за напругою чи за струмом (якісно)", 18, INK, "middle", "bold")
    s += rect(50, 70, 380, 250, "#eef3fb", BLUE, 1.8, 12)
    s += text(240, 98, "За напругою (voltage-mode)", 12.5, BLUE, "middle", "bold")
    for i, t in enumerate(["міряє лише вихідну напругу", "простіша ідея", "− немає вбудованого ліміту струму", "− повільніша реакція", "− складніше стабілізувати"]):
        col = RED if t.startswith("−") else INK
        s += text(72, 128 + i * 30, t, 11, col, "start")
    s += rect(470, 70, 380, 250, "#eef8ef", GREEN, 1.8, 12)
    s += text(660, 98, "За струмом (current-mode)", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["міряє ще й струм котушки", "+ ліміт струму ПОцикловий (захист)", "+ швидша реакція на вхід", "+ простіша компенсація", "майже всі сучасні контролери"]):
        col = GREEN if t.startswith("+") else INK
        s += text(492, 128 + i * 30, t, 11, col, "start", "bold" if t.startswith("+") else "normal")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "За замовчуванням беруть current-mode: вбудований поцикловий захист за струмом і легша стабільність (деталі стійкості — 10.2.5)", 10, INK, "middle")
    save("fig-10-2-6-control.svg", s)


# ── Рис. 10.2.3.1 — параметри котушки в даташиті ─────────────────────────────
def fig_ind_datasheet():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Котушка в даташиті: п'ять чисел, що вирішують усе", 18, INK, "middle", "bold")
    rows = [
        ("L", "індуктивність", "задає пульсацію ΔI (з вимог — §10.1.2)", BLUE),
        ("Isat", "струм насичення", "пік струму НЕ сміє його сягнути (магнітна межа)", RED),
        ("Irms", "номінальний RMS", "нагрів від DCR; тривалий струм нижче нього (теплова межа)", AMBER),
        ("DCR", "опір обмотки", "втрати міді I²·DCR → тепло й падіння ккд", GREEN),
        ("Pяд", "втрати в осерді", "змінні втрати на частоті ∝ f, ΔI → теж гріють", "#9b59b6"),
    ]
    y0 = 66
    for i, (k, name, lim, c) in enumerate(rows):
        y = y0 + i * 62
        s += rect(40, y, 120, 50, "#f6f9fc", c, 2, 8)
        s += text(100, y + 24, k, 16, c, "middle", "bold")
        s += text(100, y + 42, name, 9.5, GREY, "middle")
        s += arrow(166, y + 25, 196, y + 25, INK, 2)
        s += rect(200, y, 680, 50, "#ffffff", FAINT, 1.4, 8)
        s += text(218, y + 30, lim, 12.5, INK, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "L беруть із пульсації, а тоді перевіряють ДВІ струмові межі (Isat і Irms) та рахують втрати — пропустиш одну, котушка підведе", 10.5, INK, "middle")
    save("fig-10-3-1-datasheet.svg", s)


# ── Рис. 10.2.3.2 — насичення: «зникнення» індуктивності ─────────────────────
def fig_saturation():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Насичення: за Isat індуктивність «зникає»", 18, INK, "middle", "bold")
    ox, oy = 110, 330
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += arrow(ox, oy, ox, 80, INK, 1.6)
    s += text(822, oy + 4, "струм I", 11, INK, "start", "bold")
    s += text(ox - 10, 88, "L", 12, INK, "end", "bold")
    L0 = 110
    isat = 560
    # крива: пласка, тоді обрив
    pts = [(ox, oy - L0), (isat - 60, oy - L0), (isat, oy - L0 * 0.7), (isat + 70, oy - 30), (isat + 140, oy - 12)]
    s += poly(pts, RED, 3)
    s += text(280, oy - L0 - 12, "L стала (осердя не насичене)", 11, INK, "start")
    s += line(isat, oy, isat, oy - L0 * 0.7, GREY, 1.4, dash="5,5")
    s += text(isat, oy + 18, "Isat", 12, RED, "middle", "bold")
    s += text(isat + 90, oy - 70, "обрив: μ осердя падає,", 10.5, RED, "start", "bold")
    s += text(isat + 90, oy - 54, "L зникає, струм лавиною", 10.5, RED, "start")
    # I_peak ліворуч із запасом
    ipk = isat - 130
    s += line(ipk, oy, ipk, oy - L0, GREEN, 1.6, dash="4,4")
    s += text(ipk, oy + 18, "Iпік", 11, GREEN, "middle", "bold")
    s += arrow(ipk, oy - L0 - 20, isat, oy - L0 - 20, GREEN, 1.6)
    s += text((ipk + isat) / 2, oy - L0 - 26, "запас", 10, GREEN, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#fbe9e7", RED, 1.5, 8)
    s += text(W / 2, H - 17, "Пік струму (Iнаван + ΔI/2) мусить лишатися ЛІВОРУЧ від Isat із запасом: інакше L обвалиться, пульсація вибухне, ключ згорить", 10, INK, "middle")
    save("fig-10-3-2-saturation.svg", s)


# ── Рис. 10.2.3.3 — дві струмові межі ────────────────────────────────────────
def fig_two_limits():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Дві РІЗНІ струмові межі: Isat (магнітна) і Irms (теплова)", 17.5,
              INK, "middle", "bold")
    # верх — Isat
    s += rect(50, 70, 800, 120, "#fbe9e7", RED, 1.8, 10)
    s += text(70, 96, "Isat — магнітна, миттєва:", 13, RED, "start", "bold")
    s += text(70, 120, "обмежує ПІКОВЕ значення струму (Iнаван + ΔI/2).", 11.5, INK, "start")
    s += text(70, 140, "Перевищив на мить — осердя насичується, L зникає.", 11.5, INK, "start")
    s += text(70, 164, "Перевірка:  Iпік < Isat  (із запасом ~20–30 %)", 12, RED, "start", "bold")
    # низ — Irms
    s += rect(50, 210, 800, 120, "#fbf7ec", AMBER, 1.8, 10)
    s += text(70, 236, "Irms — теплова, тривала:", 13, AMBER, "start", "bold")
    s += text(70, 260, "обмежує СЕРЕДНІЙ (RMS) струм через нагрів на DCR.", 11.5, INK, "start")
    s += text(70, 280, "Перевищив надовго — котушка перегрівається.", 11.5, INK, "start")
    s += text(70, 304, "Перевірка:  Iнаван(rms) < Irms  (із запасом)", 12, AMBER, "start", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "Обидві мусять виконуватись — і їх легко сплутати: одна про миттєвий пік (магнетизм), друга про тривалий нагрів (тепло)", 10.5, INK, "middle")
    save("fig-10-3-3-two-limits.svg", s)


# ── Рис. 10.2.3.4 — втрати в котушці ─────────────────────────────────────────
def fig_ind_losses():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Втрати в котушці: мідь + осердя → нагрів", 18, INK, "middle", "bold")
    base = 280
    s += line(120, base, 760, base, INK, 1.6)
    # мідь
    s += rect(180, base - 130, 130, 130, "#ffffff", GREEN, 2, 6)
    s += f'<rect x="180" y="{base-130}" width="130" height="130" rx="6" fill="{GREEN}" fill-opacity="0.13"/>\n'
    s += text(245, base - 100, "МІДЬ", 13, GREEN, "middle", "bold")
    s += text(245, base - 78, "I²·DCR", 12, INK, "middle", "bold")
    s += text(245, base - 56, "пост. + змінна", 10, GREY, "middle")
    s += text(245, base + 20, "росте зі струмом", 10, GREY, "middle")
    # осердя
    s += rect(380, base - 90, 130, 90, "#ffffff", "#9b59b6", 2, 6)
    s += f'<rect x="380" y="{base-90}" width="130" height="90" rx="6" fill="#9b59b6" fill-opacity="0.13"/>\n'
    s += text(445, base - 62, "ОСЕРДЯ", 13, "#9b59b6", "middle", "bold")
    s += text(445, base - 40, "∝ f, ΔI", 12, INK, "middle", "bold")
    s += text(445, base + 20, "росте з частотою", 10, GREY, "middle")
    s += text(540, base - 55, "+", 22, INK, "middle", "bold")
    s += arrow(575, base - 55, 615, base - 55, INK, 2.4)
    # нагрів
    s += rect(625, base - 110, 130, 110, "#fbe9e7", RED, 2, 8)
    s += text(690, base - 70, "НАГРІВ", 13, RED, "middle", "bold")
    s += text(690, base - 48, "ΔT = Pвтр·Rθ", 11, INK, "middle", "bold")
    s += text(690, base - 26, "→ Irms, спалах", 10, GREY, "middle")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "Сумарні втрати (мідь росте зі струмом, осердя — з частотою й пульсацією) гріють котушку; саме нагрів і ставить межу Irms", 10.5, INK, "middle")
    save("fig-10-3-4-losses.svg", s)


# ── Рис. 10.2.3.5 — тверде проти м'якого насичення ───────────────────────────
def fig_hard_soft():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Тверде (ферит) проти м'якого (порошкове залізо) насичення", 17,
              INK, "middle", "bold")
    ox, oy = 110, 310
    s += arrow(ox, oy, 820, oy, INK, 1.6)
    s += arrow(ox, oy, ox, 80, INK, 1.6)
    s += text(822, oy + 4, "струм", 11, INK, "start", "bold")
    s += text(ox - 10, 88, "L", 12, INK, "end", "bold")
    L0 = 150
    # ферит — різкий обрив
    s += poly([(ox, oy - L0), (520, oy - L0), (560, oy - L0 * 0.65), (600, oy - 25), (660, oy - 10)], RED, 3)
    s += text(330, oy - L0 - 10, "ферит: тримає L, тоді РІЗКИЙ обрив", 11, RED, "start", "bold")
    # порошкове — м'який спад
    s += poly([(ox, oy - L0 * 0.78), (250, oy - L0 * 0.72), (450, oy - L0 * 0.55),
               (650, oy - L0 * 0.32), (800, oy - L0 * 0.16)], BLUE, 3)
    s += text(470, oy - 40, "порошкове залізо: плавний спад", 11, BLUE, "start", "bold")
    s += rect(60, H - 60, W - 120, 44, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 42, "Ферит: висока L і чітка межа — але за Isat падає лавиною, тож запас обов'язковий.", 10.5, INK, "middle")
    s += text(W / 2, H - 26, "Порошкове залізо: нижча L, зате «прощає» перевантаження плавним спадом — добре, де можливі сплески струму.", 10.5, INK, "middle")
    save("fig-10-3-5-hard-soft.svg", s)


# ── Рис. 10.2.3.6 — наскрізний вибір котушки ─────────────────────────────────
def fig_ind_pick():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Наскрізний вибір: котушка для шини 5 В / 3 А", 18, INK, "middle", "bold")
    steps = [
        ("1. L із пульсації", "ΔI≈34% @ 6.8 мкГ (вставка 🧮 §10.1.2)", BLUE),
        ("2. Iпік", "Iнаван + ΔI/2 = 3 + 0.5 ≈ 3.5 А", INK),
        ("3. Isat", "≥ Iпік × 1.3 ≈ 4.5 А (магнітна межа)", RED),
        ("4. Irms", "≥ Iнаван × запас ≈ 3.5 А (теплова межа)", AMBER),
        ("5. DCR", "малий: 20 мОм → Pмідь=3²·0.02=0.18 Вт", GREEN),
        ("6. Перевірка", "крива ккд/нагріву в даташиті у твоїх точках", "#9b59b6"),
    ]
    for i, (k, v, c) in enumerate(steps):
        y = 66 + i * 48
        s += rect(50, y, 230, 38, "#f6f9fc", c, 1.8, 7)
        s += text(66, y + 24, k, 12.5, c, "start", "bold")
        s += arrow(286, y + 19, 316, y + 19, INK, 2)
        s += rect(320, y, 530, 38, "#ffffff", FAINT, 1.2, 7)
        s += text(338, y + 24, v, 11.5, INK, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Котушка готова, коли пройдені ВСІ шість кроків: одна пропущена межа (частіше Isat або Irms) — і вузол ненадійний", 10.5, INK, "middle")
    save("fig-10-3-6-pick.svg", s)


# ── Рис. 10.2.4.1 — дві ролі конденсаторів ───────────────────────────────────
def fig_cap_roles():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 32, "Дві різні роботи: вхідний поглинає ривки, вихідний згладжує", 18,
              INK, "middle", "bold")
    # вхідний
    s += rect(40, 64, 410, 280, "#fbe9e7", RED, 1.8, 12)
    s += text(245, 90, "ВХІДНИЙ конденсатор", 13, RED, "middle", "bold")
    s += text(245, 110, "перетворювач смикає вхід ІМПУЛЬСАМИ", 10.5, INK, "middle")
    ox = 80
    s += text(ox - 16, 150, "iвх", 10, INK, "end", "bold")
    s += line(ox, 160, 420, 160, GREY, 1.2)
    x = ox
    for k in range(3):
        s += line(x, 160, x + 35, 160, COPP, 2.4)
        s += poly([(x + 35, 160), (x + 35, 130), (x + 70, 130), (x + 70, 160)], COPP, 2.4)
        x += 105
    s += text(245, 200, "кондер віддає ці ривки, щоб джерело", 10, INK, "middle")
    s += text(245, 215, "бачило ГЛАДКИЙ струм (інакше дзвін на дроті)", 10, INK, "middle")
    s += text(245, 250, "несе великий RMS-струм → найважчий режим", 11, RED, "middle", "bold")
    # вихідний
    s += rect(470, 64, 410, 280, "#eef8ef", GREEN, 1.8, 12)
    s += text(675, 90, "ВИХІДНИЙ конденсатор", 13, GREEN, "middle", "bold")
    s += text(675, 110, "згладжує трикутник струму котушки", 10.5, INK, "middle")
    ox2 = 510
    s += text(ox2 - 16, 150, "Vвих", 10, INK, "end", "bold")
    s += line(ox2, 175, 850, 175, GREY, 1.2, dash="5,4")
    pts = []
    for i in range(0, 340, 4):
        pts.append((ox2 + i, 175 - 8 * math.sin(i / 16.0)))
    s += poly(pts, GREEN, 2.2)
    s += text(675, 215, "перетворює пульсацію струму", 10, INK, "middle")
    s += text(675, 230, "на маленьку пульсацію НАПРУГИ", 10, INK, "middle")
    s += text(675, 258, "тримає вихід під час стрибка навантаження", 11, GREEN, "middle", "bold")
    s += rect(70, H - 32, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 17, "Обидва обов'язкові, але роблять РІЗНЕ: вхідний бореться зі струмом, вихідний — із напругою", 10.5, INK, "middle")
    save("fig-10-4-1-roles.svg", s)


# ── Рис. 10.2.4.2 — вхідний конденсатор як найважчий режим ───────────────────
def fig_cap_input():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Вхідний конденсатор — найбільш навантажена деталь за RMS-струмом", 17,
              INK, "middle", "bold")
    ox, oy = 110, 230
    s += arrow(ox, oy + 10, ox, 80, INK, 1.5)
    s += arrow(ox, oy, 760, oy, INK, 1.5)
    s += text(762, oy + 4, "t", 12, INK, "start", "bold")
    s += text(ox - 16, 92, "iвх", 11, INK, "end", "bold")
    # імпульси вхідного струму (повний під час ВКЛ, 0 під час ВИКЛ)
    T = 200
    x = ox
    for k in range(3):
        s += poly([(x, oy), (x, oy - 120), (x + T * 0.3, oy - 120), (x + T * 0.3, oy), (x + T, oy)], COPP, 2.6)
        x += T
    s += text(ox + 30, oy - 130, "Iнаван (повний струм)", 10, COPP, "start", "bold")
    # середній струм
    s += line(ox, oy - 36, 720, oy - 36, BLUE, 1.6, dash="6,4")
    s += text(726, oy - 32, "Iвх сер = D·Iнаван", 10, BLUE, "start", "bold")
    s += text(330, oy + 26, "джерело має давати лише СЕРЕДНЄ; різницю (ривки) бере на себе вхідний конденсатор", 10.5, INK, "middle")
    # формула RMS
    s += rect(60, 300, W - 120, 70, "#fbe9e7", RED, 1.5, 10)
    s += text(W / 2, 326, "Iвх(rms) ≈ Iнаван·√(D·(1−D))   — максимум при D=0.5 (≈ 0.5·Iнаван)", 14, INK, "middle", "bold")
    s += text(W / 2, 350, "Цей RMS-струм гріє кондер через його ESR — тому вхідний добирають за RMS-струмом, а не лише за ємністю", 10.5, GREY, "middle")
    save("fig-10-4-2-input.svg", s)


# ── Рис. 10.2.4.3 — ESR і пульсація виходу ───────────────────────────────────
def fig_cap_esr():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 32, "Пульсація виходу: ємнісна складова + на ESR", 18, INK, "middle", "bold")
    s += rect(60, 60, W - 120, 34, "#f6f6f6", GREY, 1.4, 8)
    s += text(W / 2, 82, "ΔVвих = ΔI/(8·f·C)  [ємнісна, плавна]   +   ΔI·ESR  [на ESR, гостра, у фазі зі струмом]", 13, INK, "middle", "bold")
    # ємнісна (парабола/синус)
    ox = 110
    b1 = 180
    s += text(ox - 16, b1, "ємн.", 10, BLUE, "end", "bold")
    s += line(ox, b1, 760, b1, GREY, 1.1, dash="5,4")
    pts = [(ox + i, b1 - 12 * math.sin(2 * math.pi * (i % 200) / 200)) for i in range(0, 600, 4)]
    s += poly(pts, BLUE, 2.2)
    s += text(770, b1, "∝ 1/C", 10.5, BLUE, "start", "bold")
    # ESR (трикутник, у фазі)
    b2 = 280
    s += text(ox - 16, b2, "ESR", 10, RED, "end", "bold")
    s += line(ox, b2, 760, b2, GREY, 1.1, dash="5,4")
    x = ox
    for k in range(3):
        s += poly([(x, b2 + 10), (x + 60, b2 - 10), (x + 200, b2 + 10)], RED, 2.4)
        x += 200
    s += text(770, b2, "∝ ESR", 10.5, RED, "start", "bold")
    s += rect(70, H - 56, W - 140, 40, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "З електролітом ESR великий → домінує гостра складова (пульсація повторює струм котушки).", 10.5, INK, "middle")
    s += text(W / 2, H - 22, "З керамікою ESR мізерний → лишається плавна ємнісна. Тому на виходи перетворювачів ставлять кераміку.", 10.5, INK, "middle")
    save("fig-10-4-3-esr.svg", s)


# ── Рис. 10.2.4.4 — типи конденсаторів ───────────────────────────────────────
def fig_cap_types():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Типи конденсаторів: ємність, ESR, розмір, головна вада", 18,
              INK, "middle", "bold")
    cols = ["тип", "ємність", "ESR", "розмір", "головна вада"]
    cx = [60, 250, 400, 530, 650]
    s += rect(40, 64, 820, 32, "#eef3fb", BLUE, 1.6, 6)
    for i, c in enumerate(cols):
        s += text(cx[i] + (0 if i == 0 else 20), 86, c, 12, BLUE, "start" if i == 0 else "middle", "bold")
    rows = [
        ("Кераміка (MLCC)", "мала–середня", "крихітний", "малий", "просідає під напругою (DC-bias)!", GREEN),
        ("Полімерний", "середня", "малий", "середній", "дорожчий", BLUE),
        ("Електроліт (Al)", "велика", "великий", "великий", "ESR, старіння, висихання", RED),
        ("Тантал", "велика", "середній", "малий", "горить при перенапрузі", AMBER),
    ]
    for r, (name, cap, esr, size, vada, col) in enumerate(rows):
        y = 100 + r * 56
        s += rect(40, y, 820, 50, "#ffffff" if r % 2 == 0 else "#f6f6f6", FAINT, 1, 0)
        s += text(cx[0], y + 30, name, 12, col, "start", "bold")
        s += text(cx[1] + 20, y + 30, cap, 11, INK, "middle")
        s += text(cx[2] + 20, y + 30, esr, 11, INK, "middle")
        s += text(cx[3] + 20, y + 30, size, 11, INK, "middle")
        s += text(cx[4] + 20, y + 30, vada, 10.5, INK, "middle")
    s += text(W / 2, H - 16, "Часто комбінують: великий «об'ємний» (електроліт/полімер) + кераміка поряд для високих частот", 10.5, GREY, "middle", style="italic")
    save("fig-10-4-4-types.svg", s)


# ── Рис. 10.2.4.5 — DC-bias просідання кераміки ──────────────────────────────
def fig_cap_dcbias():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 32, "Підступ кераміки: ємність ПРОСІДАЄ під напругою (DC-bias)", 17,
              INK, "middle", "bold")
    ox, oy = 120, 300
    s += arrow(ox, oy, 800, oy, INK, 1.6)
    s += arrow(ox, oy, ox, 80, INK, 1.6)
    s += text(802, oy + 4, "напруга на кондері", 10.5, INK, "start", "bold")
    s += text(ox - 10, 88, "ємність, %", 10.5, INK, "end", "bold")
    def Y(p): return oy - p * 2.0
    for p in (25, 50, 75, 100):
        s += line(ox, Y(p), 780, Y(p), FAINT, 1)
        s += text(ox - 8, Y(p) + 4, f"{p}%", 9.5, GREY, "end")
    # крива просідання
    pts = [(ox, Y(100)), (ox + 120, Y(92)), (ox + 260, Y(70)), (ox + 420, Y(45)), (ox + 560, Y(32)), (ox + 660, Y(28))]
    s += poly(pts, RED, 3)
    s += text(ox + 250, Y(82), "«10 мкФ»", 11, INK, "start", "bold")
    s += line(ox + 560, oy, ox + 560, Y(32), GREY, 1.3, dash="5,5")
    s += text(ox + 560, oy + 18, "робоча напруга", 10, AMBER, "middle", "bold")
    s += circle(ox + 560, Y(32), 5, RED, RED, 0)
    s += text(ox + 575, Y(32) - 6, "реально ≈ 3 мкФ!", 11, RED, "start", "bold")
    s += rect(70, H - 34, W - 140, 24, "#fbe9e7", RED, 1.5, 8)
    s += text(W / 2, H - 17, "MLCC на «10 мкФ» при робочій напрузі може дати лише ~3 мкФ. Беруть кондер на ВИЩУ напругу й більший номінал, ніж здається", 10, INK, "middle")
    save("fig-10-4-5-dcbias.svg", s)


# ── Рис. 10.2.4.6 — наскрізний вибір конденсаторів ───────────────────────────
def fig_cap_pick():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Наскрізний вибір: конденсатори для шини 5 В / 3 А", 18, INK, "middle", "bold")
    steps = [
        ("Вихідний: пульсація", "ΔV≤50 мВ → C з ΔI/(8fC) + ESR·ΔI; кераміка низькоESR", GREEN),
        ("Вихідний: перехідний", "провал ≤150 мВ на стрибку → ще більше C (енергія §10.2.1)", GREEN),
        ("Вхідний: RMS-струм", "Iвх(rms)=3·√(0.3·0.7)≈1.4 А → кондер з таким RMS-рейтингом", RED),
        ("DC-bias запас", "номінал кераміки × ~2–3 і вища робоча напруга", AMBER),
        ("Розміщення", "кераміка щільно до ключів (коротка гаряча петля §10.2.6)", BLUE),
    ]
    for i, (k, v, c) in enumerate(steps):
        y = 66 + i * 54
        s += rect(50, y, 250, 42, "#f6f9fc", c, 1.8, 7)
        s += text(66, y + 26, k, 12, c, "start", "bold")
        s += arrow(306, y + 21, 336, y + 21, INK, 2)
        s += rect(340, y, 510, 42, "#ffffff", FAINT, 1.2, 7)
        s += text(356, y + 26, v, 10.5, INK, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Вихідний — за пульсацією й перехідним; вхідний — за RMS-струмом; кераміку рахують з урахуванням DC-bias", 10.5, INK, "middle")
    save("fig-10-4-6-pick.svg", s)


# ── Рис. 10.2.5.1 — контур зворотного зв'язку ────────────────────────────────
def fig_fb_loop():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Контур зворотного зв'язку: виміряти → порівняти → підправити D", 18,
              INK, "middle", "bold")
    def box(x, y, w, h, t1, t2, c):
        out = rect(x, y, w, h, "#eef3fb", c, 2, 8)
        out += text(x + w / 2, y + (h / 2 + 2 if not t2 else h / 2 - 5), t1, 12.5, c, "middle", "bold")
        if t2:
            out += text(x + w / 2, y + h / 2 + 13, t2, 10, INK, "middle")
        return out
    y = 130
    s += box(60, y, 150, 70, "Силова частина", "ключ+котушка", BLUE)
    s += line(210, y + 35, 300, y + 35, INK, 2)
    s += circle(330, y + 35, 4, INK, INK, 0)
    s += text(330, y + 20, "Vвих", 12, RED, "middle", "bold")
    s += line(330, y + 35, 420, y + 35, INK, 2)
    # дільник
    s += box(360, y + 90, 120, 56, "дільник", "→ FB", GREEN)
    s += line(330, y + 35, 330, y + 118, INK, 2)
    s += line(330, y + 118, 360, y + 118, INK, 2)
    # підсилювач похибки
    s += box(540, y + 88, 150, 60, "підсилювач", "похибки", AMBER)
    s += line(480, y + 118, 540, y + 118, INK, 2)
    s += text(615, y + 170, "Vоп (еталон)", 11, GREY, "middle")
    s += arrow(615, y + 162, 615, y + 148, GREY, 1.6)
    # контролер
    s += box(740, y + 88, 130, 60, "контролер", "задає D", BLUE)
    s += arrow(690, y + 118, 740, y + 118, INK, 2)
    # назад до силової
    s += line(805, y + 88, 805, y - 10, GREY, 2)
    s += line(805, y - 10, 135, y - 10, GREY, 2)
    s += arrow(135, y - 10, 135, y, GREY, 2)
    s += text(470, y - 18, "підправлена шпаруватість D", 10.5, GREY, "middle", style="italic")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Той самий цикл «виміряти → порівняти → виправити», що в ПІД-регуляторі (§5.8): дільник зменшує Vвих до еталона,", 10.5, INK, "middle")
    s += text(W / 2, H - 9, "підсилювач похибки бачить різницю, контролер підкручує D — сотні тисяч разів на секунду.", 10.5, INK, "middle")
    save("fig-10-5-1-loop.svg", s)


# ── Рис. 10.2.5.2 — дільник задає напругу ────────────────────────────────────
def fig_fb_divider():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 32, "Дільник задає вихідну напругу", 18, INK, "middle", "bold")
    vx = 300
    s += circle(vx, 110, 4, INK, INK, 0)
    s += text(vx, 96, "Vвих = 5 В", 13, RED, "middle", "bold")
    s += line(vx, 110, vx, 150, INK, 2)
    s += rect(vx - 22, 150, 44, 54, "#ffffff", INK, 2, 4)
    s += text(vx + 40, 180, "Rверх", 12, INK, "start", "bold")
    s += line(vx, 204, vx, 240, INK, 2)
    s += circle(vx, 240, 4, INK, INK, 0)
    s += text(vx - 12, 244, "FB", 12, GREEN, "end", "bold")
    s += text(vx + 14, 240, "тримається = Vоп (0.8 В)", 11, GREEN, "start", "bold")
    s += rect(vx - 22, 270, 44, 54, "#ffffff", INK, 2, 4)
    s += text(vx + 40, 300, "Rниз", 12, INK, "start", "bold")
    s += line(vx, 324, vx, 350, INK, 2)
    s += line(vx - 16, 350, vx + 16, 350, INK, 2)
    # вхід підсилювача
    s += line(vx, 240, vx + 120, 240, GREEN, 2)
    s += rect(vx + 120, 220, 90, 40, "#fff7e6", AMBER, 1.8, 6)
    s += text(vx + 165, 245, "підсил.", 11, AMBER, "middle", "bold")
    # формула
    s += rect(560, 120, 290, 180, "#f6f6f6", GREY, 1.4, 10)
    s += text(705, 150, "Vвих = Vоп·(1 + Rверх/Rниз)", 13.5, INK, "middle", "bold")
    s += text(705, 186, "контролер тримає FB рівним Vоп,", 11, INK, "middle")
    s += text(705, 204, "тож Vвих задає САМ дільник", 11, INK, "middle")
    s += text(705, 240, "5 В при Vоп=0.8 В:", 11.5, INK, "middle", "bold")
    s += text(705, 260, "Rверх/Rниз = 5/0.8 − 1 = 5.25", 11.5, BLUE, "middle", "bold")
    s += text(705, 286, "напр. Rверх=52.5 к, Rниз=10 к", 10.5, GREY, "middle")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Двома резисторами задають будь-яку напругу понад еталон — звідси й гнучкість регульованих перетворювачів", 10.5, INK, "middle")
    save("fig-10-5-2-divider.svg", s)


# ── Рис. 10.2.5.3 — швидкість проти стабільності ─────────────────────────────
def fig_fb_speed():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Напруга швидкості й стабільності: три реакції на стрибок", 18,
              INK, "middle", "bold")
    def panel(x0, title, c, kind):
        out = rect(x0, 64, 280, 250, "none", FAINT, 2, 10)
        out += text(x0 + 140, 88, title, 12.5, c, "middle", "bold")
        bx, by = x0 + 30, 200
        out += line(bx, by, x0 + 260, by, GREY, 1.2, dash="5,4")
        out += line(bx, 110, bx, by + 60, INK, 1.3)
        step = bx + 50
        if kind == "slow":
            pts = [(bx, by), (step, by), (step + 8, by + 50), (step + 90, by + 20), (x0 + 260, by + 4)]
            out += text(x0 + 140, by + 78, "млявий, глибокий провал", 10, RED, "middle")
        elif kind == "good":
            pts = [(bx, by), (step, by), (step + 8, by + 28), (step + 40, by + 4), (x0 + 260, by)]
            out += text(x0 + 140, by + 78, "малий провал, чисте відновлення ✓", 10, GREEN, "middle", "bold")
        else:
            pts = [(bx, by), (step, by), (step + 8, by + 34), (step + 36, by - 26), (step + 64, by + 18),
                   (step + 92, by - 12), (step + 120, by + 8), (step + 150, by - 4), (x0 + 250, by)]
            out += text(x0 + 140, by + 78, "дзвенить — мала стійкість", 10, AMBER, "middle", "bold")
        out += poly(pts, c, 2.8)
        return out
    s += panel(20, "Заповільний", RED, "slow")
    s += panel(320, "Саме так", GREEN, "good")
    s += panel(620, "Зашвидкий/агресивний", AMBER, "ring")
    s += rect(70, H - 40, W - 140, 28, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 22, "Заповільний контур дає глибокий провал; зашвидкий «перестаравшись» дзвенить чи коливається.", 10.5, INK, "middle")
    s += text(W / 2, H - 9, "Мета — посередині: швидко, але без дзвону. Це баланс, який і налаштовує компенсація.", 10.5, INK, "middle")
    save("fig-10-5-3-speed.svg", s)


# ── Рис. 10.2.5.4 — чому дзвенить ────────────────────────────────────────────
def fig_fb_ringing():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Чому контур дзвенить: перекорекція із запізненням", 18, INK, "middle", "bold")
    cx, cy, r = 250, 210, 110
    steps = [
        (cx, cy - r, "вихід просів"),
        (cx + r, cy, "контур СИЛЬНО додає D"),
        (cx, cy + r, "вихід ПЕРЕскочив угору"),
        (cx - r, cy, "контур різко прибирає D"),
    ]
    for i, (x, y, t) in enumerate(steps):
        s += circle(x, y, 6, AMBER, AMBER, 0)
        anc = "middle"
        dy = -14 if y < cy else 24
        if x > cx + 10: anc, dy = "start", 4
        if x < cx - 10: anc, dy = "end", 4
        s += text(x + (12 if anc == "start" else (-12 if anc == "end" else 0)), y + dy, t, 11, INK, anc, "bold")
    # дуги по колу
    for a in range(4):
        a0 = math.radians(-90 + a * 90 + 16)
        a1 = math.radians(-90 + (a + 1) * 90 - 16)
        x0c, y0c = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1c, y1c = cx + r * math.cos(a1), cy + r * math.sin(a1)
        s += f'<path d="M {x0c:.0f} {y0c:.0f} A {r} {r} 0 0 1 {x1c:.0f} {y1c:.0f}" fill="none" stroke="{AMBER}" stroke-width="2.4" marker-end="url(#aInk)"/>\n'
    # аналогія
    s += rect(500, 110, 360, 200, "#eef8ef", GREEN, 1.8, 12)
    s += text(680, 138, "Аналогія: водій на слизькому", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["машину занесло вліво →", "різко крутить кермо вправо →", "заносить вправо →", "крутить вліво… і так гойдається.",
                           "", "Спокійний водій (повільніший контур)", "не перекручує — і занос гасне без рисків."]):
        s += text(520, 168 + i * 22, t, 11, INK if i < 4 else GREEN, "start", "normal" if i < 5 else "bold")
    s += rect(70, H - 30, W - 140, 22, "#fbf7ec", AMBER, 1.4, 8)
    s += text(W / 2, H - 15, "Контур реагує із запізненням; якщо коригує надто сильно — перестрибує, потім перестрибує назад: це і є дзвін", 10.5, INK, "middle")
    save("fig-10-5-4-ringing.svg", s)


# ── Рис. 10.2.5.5 — тест load-step (критерій здоров'я) ───────────────────────
def fig_fb_loadstep():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Критерій здоров'я: тест стрибком навантаження на осцилографі", 17.5,
              INK, "middle", "bold")
    def panel(x0, title, c, kind):
        out = rect(x0, 64, 280, 250, "none", FAINT, 2, 10)
        out += text(x0 + 140, 88, title, 12.5, c, "middle", "bold")
        bx, by = x0 + 30, 190
        out += line(bx, by, x0 + 260, by, GREY, 1.2, dash="5,4")
        out += line(bx, 110, bx, by + 70, INK, 1.3)
        step = bx + 60
        if kind == "ok":
            pts = [(bx, by), (step, by), (step + 8, by + 26), (step + 44, by + 3), (x0 + 260, by)]
            out += text(x0 + 140, by + 92, "малий провал, чисто — здоровий", 10, GREEN, "middle", "bold")
        elif kind == "marg":
            pts = [(bx, by), (step, by), (step + 8, by + 30), (step + 34, by - 18), (step + 60, by + 12),
                   (step + 86, by - 6), (step + 112, by + 3), (x0 + 250, by)]
            out += text(x0 + 140, by + 92, "кілька періодів дзвону — на межі", 10, AMBER, "middle", "bold")
        else:
            pts = [(bx, by)]
            x = step
            for k in range(7):
                pts.append((x + 8, by + (28 if k % 2 == 0 else -28)))
                x += 26
            pts.append((x0 + 250, by + 28 * (1 if 7 % 2 else -1)))
            out += text(x0 + 140, by + 92, "не вгаває — НЕСТІЙКИЙ", 10, RED, "middle", "bold")
        out += poly(pts, c, 2.8)
        return out
    s += panel(20, "Здоровий ✓", GREEN, "ok")
    s += panel(320, "На межі", AMBER, "marg")
    s += panel(620, "Нестійкий ✗", RED, "bad")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Не рахуємо запас стійкості формулами — ПЕРЕВІРЯЄМО його на осцилографі: подаємо стрибок навантаження", 10.5, INK, "middle")
    s += text(W / 2, H - 9, "й дивимось форму. Малий провал без дзвону — здоровий; дзвін чи коливання — мала стійкість, треба правити.", 10.5, INK, "middle")
    save("fig-10-5-5-loadstep.svg", s)


# ── Рис. 10.2.5.6 — конденсатор впливає на стійкість ─────────────────────────
def fig_fb_cap():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Підступ: вихідний конденсатор впливає на стійкість контуру", 17,
              INK, "middle", "bold")
    s += rect(50, 70, 380, 210, "#eef8ef", GREEN, 1.8, 12)
    s += text(240, 98, "Контур налаштовано під", 12, GREEN, "middle", "bold")
    s += text(240, 116, "конкретні C та ESR виходу", 12, GREEN, "middle", "bold")
    s += text(70, 150, "• компенсація припускає певну", 11, INK, "start")
    s += text(82, 168, "ємність і ESR вихідного кондера", 11, INK, "start")
    s += text(70, 196, "• ESR додає контуру стабільності,", 11, INK, "start")
    s += text(82, 214, "а гола кераміка (ESR≈0) — навпаки", 11, INK, "start")
    s += text(70, 244, "• більше/менше C зсуває швидкість", 11, INK, "start")
    s += rect(470, 70, 380, 210, "#fbe9e7", RED, 1.8, 12)
    s += text(660, 98, "Поміняли кондер — перевірте!", 12, RED, "middle", "bold")
    s += text(490, 132, "Заміна електроліта на кераміку", 11, INK, "start")
    s += text(490, 150, "(менший ESR) може РОЗХИТАТИ контур,", 11, INK, "start")
    s += text(490, 168, "що був стійкий, — і навпаки.", 11, INK, "start")
    s += text(490, 200, "Тому після будь-якої зміни вихідного", 11, INK, "start", "bold")
    s += text(490, 218, "конденсатора — знову тест load-step.", 11, INK, "start", "bold")
    s += text(490, 250, "Даташит часто задає діапазон C/ESR.", 10.5, GREY, "start")
    s += rect(70, H - 30, W - 140, 22, "#fbf7ec", AMBER, 1.4, 8)
    s += text(W / 2, H - 15, "Стійкість — властивість усього контуру разом із виходом, а не лише контролера: змінив вихід — перевір стійкість", 10.5, INK, "middle")
    save("fig-10-5-6-cap.svg", s)


def _mosbox(x, y, label, c=BLUE):
    out = rect(x, y, 56, 34, "#eef3fb", c, 2, 6)
    out += text(x + 28, y + 22, label, 11.5, c, "middle", "bold")
    return out


# ── Рис. 10.2.6.1 — гаряча петля в buck ──────────────────────────────────────
def fig_hot_loop():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Гаряча петля: коло різкого імпульсного струму", 18, INK, "middle", "bold")
    # Vвх рейка
    vx, gx = 150, 150
    yr, yg = 110, 320
    s += plus(vx, yr, 9, RED)
    s += text(vx, yr - 22, "Vвх", 12, INK, "middle", "bold")
    # Cin
    s += line(vx, yr + 9, vx, yg, INK, 2)
    s += line(vx - 16, (yr + yg) / 2 - 8, vx + 16, (yr + yg) / 2 - 8, COPP, 3.4)
    s += line(vx - 16, (yr + yg) / 2 + 8, vx + 16, (yr + yg) / 2 + 8, COPP, 3.4)
    s += text(vx - 24, (yr + yg) / 2 + 4, "Cвх", 12, COPP, "end", "bold")
    # верхній ключ Q1
    s += line(vx, yr, 260, yr, RED, 3)
    s += _mosbox(260, yr - 17, "Q1", BLUE)
    sw = 360
    s += line(316, yr, sw, yr, RED, 3)
    s += circle(sw, yr, 4, INK, INK, 0)
    s += text(sw, yr - 18, "вузол SW", 10.5, AMBER, "middle", "bold")
    # нижній ключ Q2
    s += line(sw, yr, sw, 200, RED, 3)
    s += _mosbox(sw - 28, 200, "Q2", GREEN)
    s += line(sw, 234, sw, yg, RED, 3)
    s += line(vx, yg, sw, yg, RED, 3)
    # котушка + вихід (поза петлею)
    s += coil_h(sw + 14, sw + 110, yr, loops=4, r=9, color=COPP, w=2.6)
    s += line(sw + 110, yr, 640, yr, INK, 2)
    s += line(640, yr, 640, yg, INK, 2)
    s += line(640 - 14, (yr + yg) / 2 - 8, 640 + 14, (yr + yg) / 2 - 8, INK, 3)
    s += line(640 - 14, (yr + yg) / 2 + 8, 640 + 14, (yr + yg) / 2 + 8, INK, 3)
    s += text(660, yr - 6, "Vвих", 12, RED, "start", "bold")
    s += line(sw, yg, 640, yg, INK, 2)
    # підсвітка петлі
    s += f'<rect x="{vx-6}" y="{yr-6}" width="{sw-vx+12}" height="{yg-yr+12}" rx="10" fill="{RED}" fill-opacity="0.07"/>\n'
    s += text(255, yg - 60, "ГАРЯЧА ПЕТЛЯ", 13, RED, "middle", "bold")
    s += text(255, yg - 44, "Cвх → Q1 → Q2 → Cвх", 11, RED, "middle", "bold")
    s += text(255, yg - 28, "тут струм РІЖЕТЬСЯ (велике di/dt)", 10, INK, "middle")
    # формула спайка
    s += rect(700, 130, 170, 110, "#fbe9e7", RED, 1.6, 10)
    s += text(785, 156, "V = L·di/dt", 14, INK, "middle", "bold")
    s += text(785, 182, "L — паразитна", 10.5, INK, "middle")
    s += text(785, 198, "індуктивність", 10.5, INK, "middle")
    s += text(785, 214, "САМОЇ петлі", 10.5, INK, "middle")
    s += text(785, 232, "→ викид, дзвін, ЕМС", 10, RED, "middle", "bold")
    s += rect(70, H - 30, W - 140, 22, "#fbf7ec", AMBER, 1.4, 8)
    s += text(W / 2, H - 15, "Площа цієї петлі — паразитна котушка: чим вона більша, тим вищі викиди на ключах і завади. Її мінімізують ПЕРШОЮ", 10.5, INK, "middle")
    save("fig-10-6-1-hotloop.svg", s)


# ── Рис. 10.2.6.2 — мала проти великої петлі ─────────────────────────────────
def fig_loop_size():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Правило №1: гаряча петля має бути МАЛЕНЬКОЮ", 18, INK, "middle", "bold")
    # мала
    s += rect(40, 70, 400, 250, "#eef8ef", GREEN, 1.8, 12)
    s += text(240, 96, "МАЛА петля (добре)", 13, GREEN, "middle", "bold")
    s += _mosbox(150, 140, "Q1", BLUE)
    s += _mosbox(150, 190, "Q2", BLUE)
    s += line(120, 157, 120, 207, COPP, 3)  # Cin поруч
    s += text(104, 185, "Cвх", 10.5, COPP, "end", "bold")
    s += line(120, 157, 150, 157, COPP, 2)
    s += line(120, 207, 150, 207, COPP, 2)
    s += f'<rect x="112" y="150" width="80" height="64" rx="6" fill="{GREEN}" fill-opacity="0.18"/>\n'
    s += text(240, 250, "Cвх упритул до ключів → крихітна площа", 10.5, INK, "middle")
    s += text(240, 270, "→ мала L → чистий SW, мало завад ✓", 11, GREEN, "middle", "bold")
    # велика
    s += rect(470, 70, 400, 250, "#fbe9e7", RED, 1.8, 12)
    s += text(670, 96, "ВЕЛИКА петля (погано)", 13, RED, "middle", "bold")
    s += _mosbox(720, 140, "Q1", BLUE)
    s += _mosbox(720, 190, "Q2", BLUE)
    s += line(520, 157, 520, 207, COPP, 3)  # Cin далеко
    s += text(504, 185, "Cвх", 10.5, COPP, "end", "bold")
    s += line(520, 157, 720, 157, COPP, 2)
    s += line(520, 207, 720, 207, COPP, 2)
    s += f'<rect x="512" y="150" width="216" height="64" rx="6" fill="{RED}" fill-opacity="0.13"/>\n'
    s += text(670, 250, "Cвх далеко → велика площа петлі", 10.5, INK, "middle")
    s += text(670, 270, "→ велика L → викиди, дзвін, ЕМС ✗", 11, RED, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "Та сама схема, та сама деталь — лише ближче чи далі. У імпульсному БЖ розводка є частиною кола: погана топологія вбиває гарну схему", 10, INK, "middle")
    save("fig-10-6-2-loopsize.svg", s)


# ── Рис. 10.2.6.3 — яка петля гаряча ─────────────────────────────────────────
def fig_which_loop():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Яка петля гаряча: шукай РІЗАНИЙ струм", 18, INK, "middle", "bold")
    yr, yg = 130, 300
    vx, sw, ox = 130, 360, 620
    # вхідна петля (гаряча)
    s += plus(vx, yr, 8, RED)
    s += line(vx, yr + 8, vx, yg, INK, 2)
    s += line(vx, yr, 250, yr, RED, 3)
    s += _mosbox(250, yr - 17, "Q1")
    s += line(306, yr, sw, yr, RED, 3)
    s += circle(sw, yr, 4, INK, INK, 0)
    s += line(sw, yr, sw, 200, RED, 3)
    s += _mosbox(sw - 28, 200, "Q2", GREEN)
    s += line(sw, 234, sw, yg, RED, 3)
    s += line(vx, yg, sw, yg, RED, 3)
    s += f'<rect x="{vx-6}" y="{yr-6}" width="{sw-vx+12}" height="{yg-yr+12}" rx="10" fill="{RED}" fill-opacity="0.08"/>\n'
    s += text((vx + sw) / 2, yg + 22, "ВХІДНА петля: струм РІЗАНИЙ (повний/нуль) → ГАРЯЧА", 10.5, RED, "middle", "bold")
    # вихідна петля (холодна)
    s += coil_h(sw + 14, sw + 110, yr, loops=4, r=9, color=COPP, w=2.6)
    s += line(sw + 110, yr, ox, yr, GREEN, 2.4)
    s += line(ox, yr, ox, yg, GREEN, 2.4)
    s += line(ox - 14, (yr + yg) / 2 - 8, ox + 14, (yr + yg) / 2 - 8, INK, 3)
    s += line(ox - 14, (yr + yg) / 2 + 8, ox + 14, (yr + yg) / 2 + 8, INK, 3)
    s += text(ox + 18, yr - 6, "Vвих", 12, RED, "start", "bold")
    s += line(sw, yg, ox, yg, GREEN, 2.4)
    s += f'<rect x="{sw+8}" y="{yr-6}" width="{ox-sw-2}" height="{yg-yr+12}" rx="10" fill="{GREEN}" fill-opacity="0.08"/>\n'
    s += text((sw + ox) / 2 + 10, yg + 22, "ВИХІДНА: струм БЕЗПЕРЕРВНИЙ (котушка) → холодна", 10.5, GREEN, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "У buck гаряча — ВХІДНА петля (там струм рветься). У boost навпаки — вихідна. Знайди різаний струм — і мінімізуй саме його петлю", 10, INK, "middle")
    save("fig-10-6-3-whichloop.svg", s)


# ── Рис. 10.2.6.4 — вузол перемикання ────────────────────────────────────────
def fig_sw_node():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Вузол перемикання SW: найгаласливіша мідь на платі", 18,
              INK, "middle", "bold")
    # маленький SW (добре)
    s += rect(50, 70, 380, 220, "#eef8ef", GREEN, 1.8, 12)
    s += text(240, 96, "Малий SW (добре)", 12.5, GREEN, "middle", "bold")
    s += _mosbox(120, 150, "ключ", BLUE)
    s += rect(210, 152, 40, 30, AMBER, AMBER, 0, 4)
    s += text(230, 200, "SW", 10, AMBER, "middle", "bold")
    s += coil_h(250, 350, 167, loops=4, r=8, color=COPP, w=2.4)
    s += text(240, 250, "рівно стільки міді, скільки треба", 10, INK, "middle")
    s += text(240, 268, "для струму й тепла — і не більше ✓", 10.5, GREEN, "middle", "bold")
    # великий SW (погано) — антена
    s += rect(470, 70, 380, 220, "#fbe9e7", RED, 1.8, 12)
    s += text(660, 96, "Розлитий SW (погано)", 12.5, RED, "middle", "bold")
    s += _mosbox(520, 150, "ключ", BLUE)
    s += rect(600, 130, 150, 70, AMBER, AMBER, 0, 6)
    s += text(675, 170, "SW", 12, "#fff", "middle", "bold")
    s += coil_h(660, 760, 230, loops=4, r=8, color=COPP, w=2.4)
    s += text(660, 250, "велика площа SW коливається на Vвх", 10, INK, "middle")
    s += text(660, 268, "з високою швидкістю → ВИПРОМІНЮЄ ✗", 10.5, RED, "middle", "bold")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "SW стрибає всім розмахом Vвх за наносекунди: велика мідь тут — це антена. Тримай SW малим (але достатнім для струму й тепла)", 10, INK, "middle")
    save("fig-10-6-4-swnode.svg", s)


# ── Рис. 10.2.6.5 — Kelvin до FB-дільника ────────────────────────────────────
def fig_kelvin_fb():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Зворотний зв'язок: Kelvin до справжнього виходу, подалі від SW", 17,
              INK, "middle", "bold")
    # погано
    s += rect(50, 70, 380, 250, "#fbe9e7", RED, 1.8, 12)
    s += text(240, 96, "Погано", 12.5, RED, "middle", "bold")
    s += line(80, 140, 360, 140, INK, 3)
    s += text(80, 132, "Vвих-доріжка (тече струм)", 9.5, GREY, "start")
    s += circle(180, 140, 4, RED, RED, 0)
    s += line(180, 140, 180, 200, RED, 2)
    s += text(180, 218, "FB тут", 10, RED, "middle", "bold")
    s += text(240, 250, "відбір посеред силової доріжки:", 10, INK, "middle")
    s += text(240, 268, "ловить падіння IR + шум SW ✗", 10.5, RED, "middle", "bold")
    # добре
    s += rect(470, 70, 380, 250, "#eef8ef", GREEN, 1.8, 12)
    s += text(660, 96, "Добре (Kelvin)", 12.5, GREEN, "middle", "bold")
    s += line(500, 140, 760, 140, INK, 3)
    s += line(760, 140, 760, 175, INK, 2)
    s += line(744, 175, 776, 175, INK, 3)
    s += line(744, 188, 776, 188, INK, 3)
    s += text(792, 165, "Cвих", 10, COPP, "start", "bold")
    s += circle(760, 140, 4, GREEN, GREEN, 0)
    s += line(760, 140, 690, 230, GREEN, 2)
    s += text(660, 250, "відбір ПРЯМО з виводів Cвих,", 10, INK, "middle")
    s += text(660, 268, "окремою тихою доріжкою (без струму) ✓", 10.5, GREEN, "middle", "bold")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "FB-вузол чутливий (§10.2.5): беруть напругу Kelvin-доріжкою прямо з виводів вихідного конденсатора —", 10.5, INK, "middle")
    s += text(W / 2, H - 9, "так контролер бачить СПРАВЖНІЙ вихід, а не падіння на доріжці; землю дільника — теж із тихої точки.", 10.5, INK, "middle")
    save("fig-10-6-5-kelvin.svg", s)


# ── Рис. 10.2.6.6 — карта доброї розводки ────────────────────────────────────
def fig_layout_map():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Карта доброї розводки перетворювача", 18, INK, "middle", "bold")
    checks = [
        ("Cвх — упритул до ключів", "крихітна гаряча петля (правило №1)", GREEN),
        ("Вузол SW — малий", "рівно для струму й тепла, не антена", AMBER),
        ("Суцільна земля (полігон)", "спільний тихий зворотний шлях", BLUE),
        ("FB — Kelvin із Cвих", "тиха доріжка, подалі від SW", GREEN),
        ("Тепловідвід — мідь+перехідні", "під ключами, котушкою, діодом", RED),
        ("Силове й сигнальне — нарізно", "шум не лізе в давачі й FB", BLUE),
    ]
    for i, (k, v, c) in enumerate(checks):
        col = i % 2
        row = i // 2
        x = 40 + col * 430
        y = 70 + row * 92
        s += rect(x, y, 410, 76, "#ffffff", c, 1.8, 10)
        s += circle(x + 24, y + 26, 8, c, c, 0)
        s += text(x + 22, y + 30, "✓", 12, "#fff", "middle", "bold")
        s += text(x + 44, y + 30, k, 12.5, c, "start", "bold")
        s += text(x + 44, y + 54, v, 10.5, INK, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Розводка імпульсного БЖ — це частина схеми, а не оформлення. Тому її називають найважливішим прикладом курсу", 10.5, INK, "middle")
    save("fig-10-6-6-map.svg", s)


# ── Рис. 10.2.7.1 — помилка «хвоста» щупа ────────────────────────────────────
def fig_probe_error():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 32, "Головна пастка виміру пульсації: довгий «хвіст» землі щупа", 17,
              INK, "middle", "bold")
    # конденсатор
    cx, cy = 200, 240
    s += line(cx, cy - 50, cx, cy - 12, INK, 2)
    s += line(cx - 22, cy - 12, cx + 22, cy - 12, COPP, 3.4)
    s += line(cx - 22, cy + 12, cx + 22, cy + 12, COPP, 3.4)
    s += line(cx, cy + 12, cx, cy + 50, INK, 2)
    s += text(cx - 30, cy + 4, "Cвих", 11, COPP, "end", "bold")
    # щуп: вістря на верх, довгий «хвіст» землі великою петлею
    s += line(cx, cy - 50, cx + 30, cy - 80, INK, 2)
    s += circle(cx + 30, cy - 80, 4, INK, INK, 0)
    s += text(cx + 36, cy - 84, "вістря", 10, INK, "start")
    # земляний хвіст — велика дуга
    s += f'<path d="M {cx} {cy+50} C {cx-120} {cy+120}, {cx+140} {cy-160}, {cx+30} {cy-72}" fill="none" stroke="{RED}" stroke-width="2.4" stroke-dasharray="2,0"/>\n'
    s += text(cx + 90, cy + 70, "довгий «хвіст»", 11, RED, "middle", "bold")
    s += text(cx + 90, cy + 86, "землі — ВЕЛИКА петля", 10.5, RED, "middle")
    s += text(cx, cy + 130, "петля ловить магнітне поле перемикання", 10, INK, "middle")
    # осцилограма — хибний дзвін
    ox = 500
    s += text(ox + 150, 110, "Що бачите:", 12, RED, "middle", "bold")
    s += line(ox, 230, ox + 320, 230, GREY, 1.2, dash="5,4")
    pts = []
    for i in range(0, 320, 3):
        damp = math.exp(-((i % 80)) / 30.0)
        pts.append((ox + i, 230 - 34 * damp * math.sin(i / 4.0) * (1 if (i % 80) < 50 else 0.2)))
    s += poly(pts, RED, 2)
    s += text(ox + 150, 290, "величезний «дзвін» — та це НЕ пульсація,", 10.5, INK, "middle")
    s += text(ox + 150, 306, "а шум, наведений у петлю самого щупа!", 10.5, RED, "middle", "bold")
    s += rect(70, H - 30, W - 140, 22, "#fbe9e7", RED, 1.4, 8)
    s += text(W / 2, H - 15, "З довгим хвостом ви міряєте не вихід, а власну петлю щупа в полі перемикання — класична хибна «пульсація на 200 мВ»", 10, INK, "middle")
    save("fig-10-7-1-probeerror.svg", s)


# ── Рис. 10.2.7.2 — пружинка замість хвоста ──────────────────────────────────
def fig_spring_tip():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Правильно: пружинка просто на виводах конденсатора (§1.6.7)", 17,
              INK, "middle", "bold")
    cx, cy = 220, 220
    s += line(cx, cy - 46, cx, cy - 12, INK, 2)
    s += line(cx - 22, cy - 12, cx + 22, cy - 12, COPP, 3.4)
    s += line(cx - 22, cy + 12, cx + 22, cy + 12, COPP, 3.4)
    s += line(cx, cy + 12, cx, cy + 46, INK, 2)
    s += text(cx - 30, cy + 4, "Cвих", 11, COPP, "end", "bold")
    # пружинка — крихітна петля прямо на виводах
    s += line(cx, cy - 46, cx + 18, cy - 60, INK, 2)
    s += circle(cx + 18, cy - 60, 3.5, INK, INK, 0)
    # коротка спіраль-земля
    s += f'<path d="M {cx} {cy+46} q 10 -6 0 -14 q -10 -6 8 -12 q 10 -4 2 -12" fill="none" stroke="{GREEN}" stroke-width="2.4"/>\n'
    s += text(cx + 70, cy + 6, "пружинка: крихітна петля", 10.5, GREEN, "middle", "bold")
    s += text(cx + 70, cy + 22, "без хвоста", 10.5, GREEN, "middle")
    # осцилограма — справжня пульсація
    ox = 500
    s += text(ox + 150, 100, "Що бачите:", 12, GREEN, "middle", "bold")
    s += line(ox, 200, ox + 320, 200, GREY, 1.2, dash="5,4")
    pts = [(ox + i, 200 - 7 * math.sin(2 * math.pi * (i % 64) / 64)) for i in range(0, 320, 3)]
    s += poly(pts, GREEN, 2.2)
    s += text(ox + 150, 250, "маленька СПРАВЖНЯ пульсація ✓", 11, GREEN, "middle", "bold")
    # ще поради
    s += rect(ox - 20, 280, 360, 70, "#eef8ef", GREEN, 1.5, 8)
    s += text(ox + 160, 302, "Ще: міряти на виводах Cвих, AC-зв'язок,", 10, INK, "middle")
    s += text(ox + 160, 318, "обмежити смугу осцилографа (20 МГц),", 10, INK, "middle")
    s += text(ox + 160, 334, "щоб прибрати високочастотні голки.", 10, INK, "middle")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Прибравши петлю щупа, бачите справжню пульсацію — і лише тоді її можна звіряти з ТЗ", 10.5, INK, "middle")
    save("fig-10-7-2-spring.svg", s)


# ── Рис. 10.2.7.3 — вимір ККД ────────────────────────────────────────────────
def fig_eff_setup():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Вимір ККД: чотири величини й чотири дроти (Kelvin)", 17.5,
              INK, "middle", "bold")
    def blk(x, t, sub, c):
        out = rect(x, 150, 130, 70, "#eef3fb", c, 2, 8)
        out += text(x + 65, 182, t, 12.5, c, "middle", "bold")
        out += text(x + 65, 202, sub, 10, GREY, "middle")
        return out
    s += blk(60, "Джерело", "Vвх", BLUE)
    s += blk(380, "ПЕРЕТВОРЮВАЧ", "DUT", GREEN)
    s += blk(710, "Електронне", "навант. (§1.6.10)", RED)
    s += arrow(190, 185, 380, 185, INK, 2)
    s += arrow(510, 185, 710, 185, INK, 2)
    # вимірювання
    s += text(285, 165, "Vвх, Iвх", 11, BLUE, "middle", "bold")
    s += text(610, 165, "Vвих, Iвих", 11, RED, "middle", "bold")
    # Kelvin
    s += text(285, 250, "напругу міряти ОКРЕМИМИ", 10, INK, "middle")
    s += text(285, 265, "дротами (Kelvin) — не на", 10, INK, "middle")
    s += text(285, 280, "силових, де є падіння", 10, INK, "middle")
    s += rect(560, 245, 300, 50, "#f6f6f6", GREY, 1.4, 8)
    s += text(710, 268, "η = (Vвих·Iвих) / (Vвх·Iвх)", 14, INK, "middle", "bold")
    s += text(710, 286, "× 100 %", 11, GREY, "middle")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Чотири точні виміри (V та I з обох боків) — і Kelvin-відбір напруги, інакше падіння на дротах підмінить ккд", 10.5, INK, "middle")
    save("fig-10-7-3-effsetup.svg", s)


# ── Рис. 10.2.7.4 — сітка точок навантаження ─────────────────────────────────
def fig_load_grid():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Сітка точок навантаження: крива ккд, а не одне число", 18,
              INK, "middle", "bold")
    ox, oy = 110, 320
    s += arrow(ox, oy, 800, oy, INK, 1.6)
    s += arrow(ox, oy, ox, 80, INK, 1.6)
    s += text(802, oy + 4, "Iвих", 11, INK, "start", "bold")
    s += text(ox - 10, 88, "ккд %", 11, INK, "end", "bold")
    for p, yy in [("90", 120), ("70", 200), ("50", 280)]:
        s += line(ox, yy, 780, yy, FAINT, 1)
        s += text(ox - 8, yy + 4, p, 10, GREY, "end")
    labels = ["0.1 А", "0.3 А", "1 А", "2 А", "3 А"]
    xs = [ox + 40 + i * 170 for i in range(5)]
    # дві криві для двох Vвх
    c1 = [(xs[0], 175), (xs[1], 140), (xs[2], 122), (xs[3], 124), (xs[4], 132)]
    c2 = [(xs[0], 190), (xs[1], 155), (xs[2], 134), (xs[3], 140), (xs[4], 152)]
    for pts, c, lab, ly in [(c1, GREEN, "Vвх=12 В", 150), (c2, BLUE, "Vвх=16.8 В", 168)]:
        s += poly(pts, c, 2.8)
        for (x, y) in pts:
            s += circle(x, y, 3.5, c, c, 0)
        s += text(xs[4] + 8, ly, lab, 10.5, c, "start", "bold")
    for lx, lb in zip(xs, labels):
        s += line(lx, oy, lx, oy + 5, GREY, 1)
        s += text(lx, oy + 20, lb, 10, GREY, "middle")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "Проходять СІТКУ Vвх × Iвих (електронним навантаженням) — і будують криву ккд; перевіряють вимоги ТЗ у кожній точці, не лише в одній", 10, INK, "middle")
    save("fig-10-7-4-loadgrid.svg", s)


# ── Рис. 10.2.7.5 — теплова карта ────────────────────────────────────────────
def fig_thermal_map():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Теплова карта: знайти гарячі точки й звірити з межами", 18,
              INK, "middle", "bold")
    # плата
    s += rect(60, 70, 480, 250, "#fbfbf8", INK, 2, 10)
    s += text(300, 92, "вид згори (тепловізор)", 10.5, GREY, "middle", style="italic")
    def part(x, y, w, h, name, temp, c):
        out = rect(x, y, w, h, "#ffffff", c, 2, 6)
        out += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{c}" fill-opacity="0.20"/>\n'
        out += text(x + w / 2, y + h / 2 - 2, name, 10.5, c, "middle", "bold")
        out += text(x + w / 2, y + h / 2 + 14, temp, 10, INK, "middle")
        return out
    s += part(110, 130, 90, 60, "ключі", "95 °C", RED)
    s += part(240, 120, 100, 80, "котушка", "82 °C", AMBER)
    s += part(390, 140, 90, 60, "Cвх", "70 °C", AMBER)
    s += part(150, 230, 90, 50, "Cвих", "48 °C", GREEN)
    # перевірка меж
    s += rect(570, 90, 290, 220, "#f6f6f6", GREY, 1.4, 10)
    s += text(715, 116, "Звірка з межами:", 12, INK, "middle", "bold")
    checks = [("ключі 95° < межа 125° ✓", GREEN), ("котушка 82° < 125° ✓", GREEN),
              ("Cвх 70° — на межі, стежити", AMBER), ("при Tамб 60° і повному навант.", GREY)]
    for i, (t, c) in enumerate(checks):
        s += text(590, 148 + i * 32, "• " + t, 10.5, c, "start", "bold" if c != GREY else "normal")
    s += text(715, 290, "міряти в НАЙГІРШОМУ режимі", 10, RED, "middle", "bold")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Кожна деталь має лишатися нижче своєї межі за найгіршого режиму (макс. навантаження, макс. Vвх, гаряче довкілля)", 10, INK, "middle")
    save("fig-10-7-5-thermal.svg", s)


# ── Рис. 10.2.7.6 — звірка з ТЗ (замкнути коло) ──────────────────────────────
def fig_verify_tz():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Замкнути коло: вимір звіряють із кожним рядком ТЗ", 18,
              INK, "middle", "bold")
    # цикл ТЗ→проєкт→вимір→підтвердження
    cyc = [("ТЗ", BLUE, 150), ("проєкт", AMBER, 360), ("вимір", RED, 570), ("підтвердж.", GREEN, 760)]
    for i, (t, c, x) in enumerate(cyc):
        s += rect(x - 55, 70, 110, 44, "#ffffff", c, 2, 8)
        s += text(x, 97, t, 12.5, c, "middle", "bold")
        if i < 3:
            s += arrow(x + 55, 92, cyc[i + 1][2] - 55, 92, INK, 2)
    s += arrow(760, 116, 150, 145, GREY, 1.6)
    s += text(455, 138, "(не зійшлося — назад до проєкту)", 10, GREY, "middle", style="italic")
    rows = [
        ("Пульсація ≤ 50 мВ", "пружинкою на Cвих", "32 мВ ✓"),
        ("ККД ≥ 90 % @ 3 А", "сітка Vвх×Iвих", "92 % ✓"),
        ("Перехідний ≤ 150 мВ", "стрибок навантаж. (§10.2.5)", "120 мВ ✓"),
        ("Нагрів ≤ +40 °C", "теплова карта", "+35 °C ✓"),
    ]
    y0 = 175
    for i, (k, how, res) in enumerate(rows):
        y = y0 + i * 44
        s += rect(60, y, 280, 36, "#eef3fb", FAINT, 1, 6)
        s += text(74, y + 23, k, 11, BLUE, "start", "bold")
        s += arrow(346, y + 18, 376, y + 18, INK, 1.8)
        s += text(386, y + 23, how, 10.5, INK, "start")
        s += rect(660, y, 180, 36, "#eef8ef", GREEN, 1.4, 6)
        s += text(750, y + 23, res, 11.5, GREEN, "middle", "bold")
    s += rect(70, H - 28, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 14, "Вимірювання має сенс лише як звірка з ТЗ: кожен рядок специфікації — підтверджений числом. Не зійшлося — назад на доопрацювання", 9.5, INK, "middle")
    save("fig-10-7-6-verify.svg", s)


# ── Рис. 10.2.8.1 — карта симптом → причина → лік ────────────────────────────
def fig_symptom_map():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Карта діагностики: симптом → ймовірна причина → лік", 18,
              INK, "middle", "bold")
    cols = ["Симптом", "Ймовірна причина", "Лік"]
    cx = [50, 330, 650]
    s += rect(40, 60, 840, 30, "#eef3fb", BLUE, 1.6, 6)
    for i, c in enumerate(cols):
        s += text(cx[i] + 14, 80, c, 12.5, BLUE, "start", "bold")
    rows = [
        ("Свист/спів (чути)", "PFM у звуковій смузі · спів кераміки/котушки", "forced-PWM · інші C · демпфер", AMBER),
        ("Дзвін/коливання", "мала стійкість контуру · поганий C/ESR", "компенсація · правильний Cвих", RED),
        ("Чергування імпульсів", "субгармоніка при D>0.5 (current-mode)", "нахилова компенсація · нижчий D", RED),
        ("Просідання виходу", "ліміт струму · насичення котушки · DCR/ESR", "більший Isat/C · перевірити ТЗ", BLUE),
        ("Перегрів", "великі втрати · погана розводка/тепловідвід", "інші деталі · мідь+via (§10.2.6)", RED),
        ("Не стартує / рве на пуску", "інраш · спрацьовує захист · просід входу", "м'який старт · більший Cвх", GREEN),
    ]
    for r, (sym, cause, fix, c) in enumerate(rows):
        y = 92 + r * 48
        s += rect(40, y, 840, 44, "#ffffff" if r % 2 == 0 else "#f6f6f6", FAINT, 1, 0)
        s += text(cx[0] + 14, y + 27, sym, 11, c, "start", "bold")
        s += text(cx[1] + 14, y + 27, cause, 10.5, INK, "start")
        s += text(cx[2] + 14, y + 27, fix, 10.5, GREEN, "start")
    save("fig-10-8-1-symptommap.svg", s)


# ── Рис. 10.2.8.2 — свист і спів ─────────────────────────────────────────────
def fig_singing():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Свист: PFM у звуковій смузі та спів кераміки", 18, INK, "middle", "bold")
    # звукова смуга
    ox, oy = 100, 230
    s += arrow(ox, oy, 800, oy, INK, 1.6)
    s += text(802, oy + 4, "частота", 11, INK, "start", "bold")
    s += f'<rect x="200" y="120" width="220" height="{oy-120}" fill="{AMBER}" fill-opacity="0.12"/>\n'
    s += text(310, 110, "чутно (20 Гц – 20 кГц)", 11, AMBER, "middle", "bold")
    for x, lb in [(150, "інфра"), (310, "ЗВУК"), (600, "робоча fsw (500 кГц)")]:
        s += text(x, oy + 22, lb, 9.5, GREY, "middle")
    s += line(600, oy, 600, 130, GREEN, 2)
    s += text(600, 122, "норма: вище звуку", 9.5, GREEN, "middle", "bold")
    # PFM падає в смугу
    s += line(310, oy, 310, 150, RED, 2)
    s += text(310, 142, "PFM на легкому навант.", 9.5, RED, "middle", "bold")
    s += arrow(560, 170, 340, 170, RED, 1.8)
    s += text(450, 162, "частота падає в чутне", 9.5, RED, "middle")
    # пояснення спів
    s += rect(60, 280, 800, 70, "#fbf7ec", AMBER, 1.5, 10)
    s += text(W / 2, 304, "Дві причини свисту: (1) PFM/пропуск імпульсів на легкому навантаженні знижує частоту в чутну смугу;", 10.5, INK, "middle")
    s += text(W / 2, 322, "(2) кераміка п'єзоелектрична (§10.2.4) — пульсація змушує її вібрувати, і вона тоненько пищить.", 10.5, INK, "middle")
    s += text(W / 2, 340, "Лік: режим forced-PWM (стала висока fsw), інші конденсатори, демпфер.", 10.5, GREEN, "middle", "bold")
    save("fig-10-8-2-singing.svg", s)


# ── Рис. 10.2.8.3 — субгармонічні коливання ──────────────────────────────────
def fig_subharmonic():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Субгармоніка: при D>0.5 імпульси чергуються широкий-вузький", 17,
              INK, "middle", "bold")
    # норма
    ox = 100
    s += text(ox - 16, 110, "норма", 11, GREEN, "end", "bold")
    y = 130
    s += line(ox, y + 30, 420, y + 30, GREY, 1.2)
    x = ox
    for k in range(4):
        s += poly([(x, y + 30), (x, y), (x + 50, y), (x + 50, y + 30), (x + 70, y + 30)], GREEN, 2.4)
        x += 70
    s += text(210, y + 50, "усі імпульси однакові", 10, INK, "middle")
    # субгармоніка
    s += text(ox - 16, 250, "хвороба", 11, RED, "end", "bold")
    y2 = 270
    s += line(ox, y2 + 30, 420, y2 + 30, GREY, 1.2)
    x = ox
    widths = [62, 30, 62, 30]
    for w in widths:
        s += poly([(x, y2 + 30), (x, y2), (x + w, y2), (x + w, y2 + 30), (x + 78, y2 + 30)], RED, 2.4)
        x += 78
    s += text(210, y2 + 50, "широкий-вузький-широкий… (період подвоївся)", 10, RED, "middle", "bold")
    # пояснення
    s += rect(470, 110, 390, 230, "#f6f6f6", GREY, 1.4, 10)
    s += text(665, 136, "Чому й як лікують", 12.5, INK, "middle", "bold")
    for i, t in enumerate([
        "У керуванні за струмом (§10.2.2) при",
        "шпаруватості D > 0.5 контур може",
        "«роздвоїтися»: кожен другий імпульс",
        "інший. Це субгармонічна нестійкість.",
        "",
        "Лік — нахилова компенсація: контролер",
        "додає штучний нахил, що вирівнює",
        "імпульси. Вона зашита всередині;",
        "якщо вже зривається — знизити D",
        "(інша топологія/витки) чи частоту.",
    ]):
        c = GREEN if t.startswith("Лік") else INK
        s += text(490, 162 + i * 17, t, 10.5, c, "start", "bold" if t.startswith("Лік") else "normal")
    save("fig-10-8-3-subharmonic.svg", s)


# ── Рис. 10.2.8.4 — причини просідання ───────────────────────────────────────
def fig_sag():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Просідання виходу: чотири різні причини, чотири підписи", 17.5,
              INK, "middle", "bold")
    def panel(x0, title, c, kind):
        out = rect(x0, 64, 210, 250, "none", FAINT, 2, 10)
        out += text(x0 + 105, 88, title, 11.5, c, "middle", "bold")
        bx, by = x0 + 24, 200
        out += line(bx, by, x0 + 192, by, GREY, 1.2, dash="4,4")
        out += line(bx, 110, bx, by + 50, INK, 1.2)
        if kind == "ilim":
            out += poly([(bx, by - 50), (bx + 70, by - 50), (bx + 80, by - 6), (x0 + 190, by - 6)], c, 2.6)
            out += text(x0 + 105, by + 36, "впав до полиці ліміту", 9, INK, "middle")
        elif kind == "sat":
            out += poly([(bx, by - 50), (bx + 60, by - 50), (bx + 66, by - 50), (bx + 70, by - 70), (bx + 74, by + 10), (x0 + 190, by + 10)], c, 2.4)
            out += text(x0 + 105, by + 36, "сплеск струму, тоді обвал", 9, INK, "middle")
        elif kind == "dcr":
            out += poly([(bx, by - 50), (x0 + 190, by - 12)], c, 2.6)
            out += text(x0 + 105, by + 36, "лінійно зі струмом (DCR/ESR)", 9, INK, "middle")
        else:
            out += poly([(bx, by - 50), (bx + 90, by - 48), (bx + 140, by - 20), (x0 + 190, by - 8)], c, 2.6)
            out += text(x0 + 105, by + 36, "вихід іде за входом (батарея сіла)", 9, INK, "middle")
        return out
    s += panel(20, "Ліміт струму", RED, "ilim")
    s += panel(250, "Насичення котушки", AMBER, "sat")
    s += panel(480, "Падіння DCR/ESR", BLUE, "dcr")
    s += panel(700, "Просід входу", GREEN, "in")
    s += rect(70, H - 34, W - 140, 24, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 17, "Форма просідання видає причину: полиця → ліміт; сплеск+обвал → насичення (перевір Isat); лінійно → DCR/ESR; за входом → батарея", 10, INK, "middle")
    save("fig-10-8-4-sag.svg", s)


# ── Рис. 10.2.8.5 — галерея осцилограм ───────────────────────────────────────
def fig_scope_gallery():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Галерея підписів: за формою на екрані впізнаєш хворобу", 17.5,
              INK, "middle", "bold")
    def panel(x0, y0, title, sub, c, kind):
        out = rect(x0, y0, 210, 130, "none", c, 1.8, 10)
        out += text(x0 + 105, y0 + 22, title, 11.5, c, "middle", "bold")
        bx, by = x0 + 20, y0 + 90
        out += line(bx, by, x0 + 192, by, GREY, 1, dash="3,3")
        if kind == "swring":
            pts = [(bx, by)]
            for i in range(0, 170, 3):
                d = math.exp(-(i % 50) / 14.0) if (i % 50) < 30 else 0
                pts.append((bx + i, by - 22 * d * math.sin(i / 2.5) - (18 if (i % 50) < 4 else 0)))
            out += poly(pts, c, 1.8)
        elif kind == "loopring":
            pts = [(bx, by), (bx + 40, by), (bx + 46, by + 22), (bx + 66, by - 14), (bx + 86, by + 9), (bx + 106, by - 5), (x0 + 190, by)]
            out += poly(pts, c, 2)
        elif kind == "sub":
            x = bx
            for w in [40, 18, 40, 18]:
                out += poly([(x, by), (x, by - 24), (x + w, by - 24), (x + w, by), (x + 48, by)], c, 1.8)
                x += 48
        else:
            out += poly([(bx, by), (bx + 60, by - 6), (bx + 110, by - 40), (x0 + 190, by - 70)], c, 2)
        out += text(x0 + 105, y0 + 120, sub, 9, INK, "middle")
        return out
    s += panel(40, 70, "Дзвін на SW", "→ розводка (гаряча петля §10.2.6)", RED, "swring")
    s += panel(260, 70, "Дзвін виходу на стрибку", "→ стійкість контуру §10.2.5", AMBER, "loopring")
    s += panel(480, 70, "Широкий-вузький", "→ субгармоніка (нахил. компенс.)", BLUE, "sub")
    s += panel(700, 70, "Струм біжить угору", "→ насичення котушки §10.2.3", "#9b59b6", "sat")
    s += rect(70, H - 60, W - 140, 44, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 42, "Осцилограф — головний діагност: кожна хвороба має свій підпис. Чіпляй пружинку (§10.2.7) до підозрілого вузла", 10.5, INK, "middle")
    s += text(W / 2, H - 25, "(SW, вихід, струм котушки) — і форма сама підкаже, куди дивитись і що правити.", 10.5, INK, "middle")
    save("fig-10-8-5-scopegallery.svg", s)


# ── Рис. 10.2.8.6 — діагностичний потік ──────────────────────────────────────
def fig_diag_flow():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Діагностичний потік: від симптому до причини", 18, INK, "middle", "bold")
    steps = [
        ("Чути свист?", "→ глянь режим (PFM?) і кераміку → forced-PWM/інші C", AMBER),
        ("Дзвенить вихід?", "→ стрибок навантаж.: контур (§10.2.5) чи C/ESR", RED),
        ("Імпульси нерівні?", "→ субгармоніка при D>0.5 → нахилова компенсація", RED),
        ("Вихід просідає?", "→ форма підкаже: ліміт / насичення / DCR / вхід", BLUE),
        ("Гріється?", "→ теплова карта (§10.2.7): втрати чи розводка", "#9b59b6"),
        ("Не стартує?", "→ інраш / захист / просід входу → м'який старт, Cвх", GREEN),
    ]
    for i, (q, a, c) in enumerate(steps):
        y = 66 + i * 50
        s += rect(50, y, 230, 38, "#f6f9fc", c, 1.8, 7)
        s += text(66, y + 24, q, 12, c, "start", "bold")
        s += arrow(286, y + 19, 316, y + 19, INK, 2)
        s += rect(320, y, 540, 38, "#ffffff", FAINT, 1.2, 7)
        s += text(336, y + 24, a, 10.5, INK, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Майже всі хвороби зводяться до вже знайомих причин із цього розділу — діагностика лише читає їхні підписи", 10.5, INK, "middle")
    save("fig-10-8-6-flow.svg", s)


def fig_a7_sweep():
    """Вставка ⚙️ до 10.2.7 — автоматизація сітки ккд Vвх×Iвих."""
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 30, "Автоматизація ккд: скрипт обходить сітку Vвх × Iвих", 17,
              INK, "middle", "bold")
    # сітка з обхідним шляхом
    ox, oy = 90, 300
    s += arrow(ox, oy, 430, oy, INK, 1.5)
    s += arrow(ox, oy, ox, 90, INK, 1.5)
    s += text(432, oy + 4, "Iвих", 10.5, INK, "start", "bold")
    s += text(ox - 8, 96, "Vвх", 10.5, INK, "end", "bold")
    cols = [ox + 40 + i * 80 for i in range(4)]
    rows = [oy - 40 - j * 60 for j in range(3)]
    # змійка
    path = []
    for j, y in enumerate(rows):
        line_cols = cols if j % 2 == 0 else cols[::-1]
        for x in line_cols:
            path.append((x, y))
    s += poly(path, GREEN, 1.6, dash="4,3")
    for j, y in enumerate(rows):
        for x in cols:
            s += circle(x, y, 4, BLUE, BLUE, 0)
    s += circle(path[0][0], path[0][1], 6, "none", GREEN, 2.4)
    s += text(path[0][0] - 6, path[0][1] + 18, "старт", 9, GREEN, "middle", "bold")
    s += text(270, oy + 22, "Iвих: 0.1·0.3·1·2·3 А", 9, GREY, "middle")
    s += text(ox - 18, 200, "Vвх:", 9, GREY, "end")
    s += text(ox - 18, 215, "12·16.8", 9, GREY, "end")
    # кроки на вузлі
    s += rect(480, 80, 390, 250, "#f6f6f6", GREY, 1.4, 10)
    s += text(675, 104, "На КОЖНОМУ вузлі:", 12.5, INK, "middle", "bold")
    steps = [
        ("1", "PSU: задати Vвх (CV + ліміт струму)", BLUE),
        ("2", "Навантаження: задати Iвих (CC)", RED),
        ("3", "ЧЕКАТИ усталення (електр.+тепло)", AMBER),
        ("4", "Зчитати Vвх, Iвх, Vвих, Iвих (Kelvin)", GREEN),
        ("5", "η = (Vвих·Iвих)/(Vвх·Iвх) · 100 %", INK),
        ("6", "Записати рядок у таблицю/файл", GREY),
    ]
    for i, (n, t, c) in enumerate(steps):
        y = 130 + i * 31
        s += circle(502, y, 11, c, c, 0)
        s += text(502, y + 4, n, 11, "#fff", "middle", "bold")
        s += text(522, y + 4, t, 10.5, INK, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Десятки точок руками — години й помилки; скрипт через SCPI робить це за хвилини й без зайвих очепяток", 10.5, INK, "middle")
    save("fig-10-7a1-sweep.svg", s)


def fig_c7_eload():
    """Вставка 🔌 до 10.2.7 — електронне навантаження: стік + режими CC/CR/CP."""
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 30, "Електронне навантаження: програмований «поглинач» струму", 17,
              INK, "middle", "bold")
    # тракт: БЖ → DUT → навантаження
    def blk(x, t, sub, c):
        out = rect(x, 80, 130, 64, "#eef3fb", c, 2, 8)
        out += text(x + 65, 108, t, 12, c, "middle", "bold")
        out += text(x + 65, 128, sub, 9.5, GREY, "middle")
        return out
    s += blk(50, "лаб. БЖ", "джерело (дає)", BLUE)
    s += blk(280, "ПЕРЕТВОРЮВАЧ", "DUT", GREEN)
    s += blk(540, "ЕЛ. НАВАНТ.", "стік (бере)", RED)
    s += arrow(180, 112, 280, 112, INK, 2)
    s += arrow(410, 112, 540, 112, INK, 2)
    s += text(230, 100, "Vвх", 10, BLUE, "middle", "bold")
    s += text(475, 100, "Vвих, Iвих", 10, RED, "middle", "bold")
    # нутро навантаження
    s += rect(540, 170, 320, 160, "#fbe9e7", RED, 1.8, 10)
    s += text(700, 192, "усередині: MOSFET у лінійному режимі", 10.5, INK, "middle")
    s += text(700, 208, "+ контур, що тримає заданий режим", 10, GREY, "middle")
    # MOSFET-стік
    s += line(600, 230, 600, 250, INK, 2)
    s += rect(572, 250, 56, 30, "#ffffff", RED, 2, 5)
    s += text(600, 270, "ключ", 9.5, RED, "middle", "bold")
    s += line(600, 280, 600, 305, INK, 2)
    s += line(580, 305, 620, 305, INK, 2)
    s += text(600, 322, "тепло (радіатор+вентилятор)", 9, GREY, "middle")
    # панель режимів
    s += rect(40, 180, 470, 150, "#f6f6f6", GREY, 1.4, 10)
    s += text(275, 204, "Режими (що тримає сталим):", 12, INK, "middle", "bold")
    modes = [
        ("CC", "сталий СТРУМ — головний для сітки ккд і ліміту", GREEN),
        ("CR", "стала опірність (I∝V) — для пуску/рампи", BLUE),
        ("CP", "стала ПОТУЖНІСТЬ (I=P/V) — імітує DC-DC-споживача", AMBER),
        ("динам.", "швидкий стрибок струму — тест load-step (§10.2.5)", RED),
    ]
    for i, (m, d, c) in enumerate(modes):
        y = 226 + i * 26
        s += rect(56, y - 14, 52, 22, "#fff", c, 1.6, 5)
        s += text(82, y + 2, m, 11, c, "middle", "bold")
        s += text(120, y + 2, d, 10, INK, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "БЖ дає напругу, навантаження бере струм: разом вони проганяють перетворювач по всій сітці Vвх×Iвих (§10.2.7)", 10.5, INK, "middle")
    save("fig-10-7c1-eload.svg", s)


def fig_m5_loadstep():
    """Вставка 🧮 до 10.2.5 — провал і дзвін на стрибку навантаження «на пальцях»."""
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 30, "Стрибок навантаження «на пальцях»: глибина провалу й дзвін", 17,
              INK, "middle", "bold")
    ox = 100
    # струм навантаження (верх)
    s += text(ox - 16, 92, "Iнаван", 11, INK, "end", "bold")
    b1 = 110
    s += line(ox, b1 + 18, 320, b1 + 18, COPP, 2.4)
    s += line(320, b1 + 18, 320, b1 - 12, COPP, 2.4)
    s += line(320, b1 - 12, 820, b1 - 12, COPP, 2.4)
    s += text(230, b1 + 34, "0.5 А", 9.5, GREY, "middle")
    s += text(560, b1 - 22, "3 А (ΔIнаван = 2.5 А)", 9.5, GREY, "middle")
    # вихідна напруга (низ)
    nom = 250
    s += text(ox - 16, nom - 50, "Vвих", 11, INK, "end", "bold")
    s += line(ox, nom, 820, nom, GREY, 1.3, dash="6,4")
    s += text(826, nom + 4, "ціль", 9.5, GREY, "start")
    # форма: миттєвий ESR-крок + просадка + відновлення з дзвоном
    pts = [(ox, nom), (320, nom), (322, nom + 16), (340, nom + 70), (360, nom + 40),
           (380, nom + 64), (400, nom + 48), (420, nom + 58), (445, nom + 52),
           (475, nom + 55), (560, nom + 8), (820, nom)]
    s += poly(pts, BLUE, 2.6)
    # ESR-крок
    s += arrow(322, nom, 322, nom + 16, RED, 1.6)
    s += text(300, nom + 10, "ESR-крок = ΔI·ESR", 9.5, RED, "end", "bold")
    # просадка
    s += arrow(345, nom, 345, nom + 70, AMBER, 1.6)
    s += text(355, nom + 86, "провал ≈ ΔI·ESR + ΔI·tвідгук/C", 10, AMBER, "start", "bold")
    # дзвін
    s += text(430, nom + 100, "дзвін: лічи цикли → запас стійкості (без Боде)", 9.5, INK, "middle")
    s += rect(560, nom - 70, 250, 100, "#f6f6f6", GREY, 1.4, 8)
    s += text(685, nom - 48, "Лічба «на пальцях»:", 11, INK, "middle", "bold")
    s += text(575, nom - 26, "0 циклів → добрий запас ✓", 9.5, GREEN, "start", "bold")
    s += text(575, nom - 8, "1–2 цикли → на межі", 9.5, AMBER, "start")
    s += text(575, nom + 10, "не вгаває → нестійко ✗", 9.5, RED, "start", "bold")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Глибина провалу — це число для ТЗ (ESR-крок + просадка C за час відгуку). Кількість циклів дзвону —", 10.5, INK, "middle")
    s += text(W / 2, H - 9, "замість запасу фази: чим менше дзвону, тим більший запас стійкості. Усе видно оком на осцилографі.", 10.5, INK, "middle")
    save("fig-10-5m1-loadstep.svg", s)


def fig_m4_ripple_compare():
    """Вставка 🧮 до 10.2.4 — ємнісна складова проти ESR: кераміка vs електроліт."""
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 30, "Дві складові пульсації: хто домінує (ΔI=0.68 А, f=500 кГц)", 16.5,
              INK, "middle", "bold")

    def panel(x0, title, sub, capv, esrv, cap_dom):
        out = rect(x0, 60, 410, 300, "none", FAINT, 2, 10)
        out += text(x0 + 205, 84, title, 13, INK, "middle", "bold")
        out += text(x0 + 205, 102, sub, 10, GREY, "middle")
        base = 320
        sc = 1.7   # px на мВ (кліп великих)
        def bar(bx, val, lab, c, dom):
            h = min(val * sc, 210)
            out2 = rect(bx, base - h, 90, h, "#ffffff", c, 2, 5)
            out2 += f'<rect x="{bx}" y="{base-h:.0f}" width="90" height="{h:.0f}" rx="5" fill="{c}" fill-opacity="0.18"/>\n'
            out2 += text(bx + 45, base - h - 10, f"{val:g} мВ", 12, c, "middle", "bold")
            out2 += text(bx + 45, base + 18, lab, 10.5, c, "middle", "bold")
            if dom:
                out2 += text(bx + 45, base + 34, "← домінує", 9.5, c, "middle", "bold")
            if val * sc > 210:
                out2 += text(bx + 45, base - 200, "∿", 14, c, "middle")
            return out2
        out += line(x0 + 30, base, x0 + 390, base, INK, 1.4)
        out += bar(x0 + 70, capv, "ємнісна ΔI/8fC", BLUE, cap_dom)
        out += bar(x0 + 240, esrv, "на ESR  ΔI·ESR", RED, not cap_dom)
        return out

    s += panel(20, "Кераміка", "22 мкФ, ESR 3 мОм", 7.7, 2.0, True)
    s += panel(470, "Електроліт", "220 мкФ (×10!), ESR 200 мОм", 0.77, 136, False)
    s += rect(70, H - 50, W - 140, 38, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 32, "Кераміка: ESR мізерний → пульсацію задає ЄМНІСТЬ (додаси C — менша пульсація).", 10.5, INK, "middle")
    s += text(W / 2, H - 16, "Електроліт: ESR величезний → він і домінує (136 мВ!), і ×10 ємності майже не рятує — треба нижчий ESR.", 10.5, INK, "middle")
    save("fig-10-4m1-ripplecompare.svg", s)


def fig_m3_worksheet():
    """Вставка 🧮 до 10.2.3 — наскрізний розрахунок котушки buck 5→3.3 В."""
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 30, "Розрахунок котушки покроково: buck 5 В → 3.3 В, 2 А, 500 кГц", 16.5,
              INK, "middle", "bold")
    steps = [
        ("1", "Шпаруватість", "D = Vвих/Vвх = 3.3/5 = 0.66", BLUE),
        ("2", "Цільова пульсація", "ΔI = 35 %·2 А = 0.7 А", GREEN),
        ("3", "Індуктивність", "L = (Vвх−Vвих)·D/(ΔI·f) = 1.7·0.66/(0.7·500к) ≈ 3.2 мкГ → беремо 3.3 мкГ", BLUE),
        ("", "(перерахунок ΔI)", "ΔI = 1.7·0.66/(3.3мкГ·500к) ≈ 0.68 А = 34 % ✓", GREY),
        ("4", "Пік → Isat", "Iпік = 2 + 0.68/2 ≈ 2.34 А → Isat ≥ 2.34·1.3 ≈ 3.3 А", RED),
        ("5", "Тривалий → Irms", "Iнаван(rms) ≈ 2 А → Irms ≥ 2.5 А (із запасом)", AMBER),
        ("6", "DCR → втрати", "DCR 30 мОм → Pмідь = 2²·0.03 = 0.12 Вт", GREEN),
    ]
    y = 56
    for num, name, formula, c in steps:
        h = 40
        s += rect(40, y, 820, h, "#ffffff" if num else "#f6f6f6", c if num else FAINT, 1.6 if num else 1, 6)
        if num:
            s += circle(64, y + h / 2, 13, c, c, 0)
            s += text(64, y + h / 2 + 5, num, 13, "#fff", "middle", "bold")
        s += text(96, y + 17, name, 11, c, "start", "bold")
        s += text(96, y + 33, formula, 11, INK, "start")
        y += h + 6
    # результат
    s += rect(40, y + 4, 820, 40, "#eef8ef", GREEN, 2, 8)
    s += text(W / 2, y + 29, "Котушка: 3.3 мкГ · Isat ≥ 3.3 А · Irms ≥ 2.5 А · DCR ~30 мОм (екранована, з запасом за гарячим Isat)",
              12, GREEN, "middle", "bold")
    save("fig-10-3m1-worksheet.svg", s)


def fig_c2_module():
    """Вставка 🔌 до 10.2.2 — power-модуль: усе всередині, мінімум зовні."""
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Power-модуль: увесь Розділ 10.2 запакований в один корпус", 17.5,
              INK, "middle", "bold")
    # корпус модуля
    s += rect(120, 70, 380, 250, "#eef8ef", GREEN, 2.4, 14)
    s += text(310, 94, "POWER-МОДУЛЬ", 13, GREEN, "middle", "bold")
    for i, (t, c) in enumerate([("контролер", BLUE), ("верхній + нижній ключ", BLUE), ("котушка", COPP), ("компенсація", AMBER)]):
        y = 116 + i * 42
        s += rect(150, y, 320, 32, "#ffffff", c, 1.6, 6)
        s += text(310, y + 21, t, 11.5, c, "middle", "bold")
    s += text(310, 304, "гаряча петля вже розведена ВСЕРЕДИНІ (§10.2.6)", 9.5, GREEN, "middle", "bold")
    # піни
    pins = [("VIN", 110, True), ("EN", 160, True), ("FB", 210, False), ("VOUT", 110, False), ("PG", 160, False), ("GND", 260, True)]
    # зовнішня обвʼязка — мінімум
    s += plus(60, 110, 8, RED)
    s += text(60, 90, "Vвх", 11, INK, "middle", "bold")
    s += line(60, 118, 60, 300, INK, 2)
    s += line(60, 110, 120, 110, INK, 2)
    s += line(85, 150, 85, 300, COPP, 2)  # Cin
    s += line(85 - 12, 220, 85 + 12, 220, COPP, 3)
    s += line(85 - 12, 232, 85 + 12, 232, COPP, 3)
    s += text(72, 258, "Cвх", 9.5, COPP, "end", "bold")
    # вихід
    s += line(500, 110, 580, 110, INK, 2)
    s += text(600, 114, "Vвих", 12, RED, "start", "bold")
    s += line(560, 150, 560, 300, COPP, 2)  # Cout
    s += line(560 - 12, 220, 560 + 12, 220, COPP, 3)
    s += line(560 - 12, 232, 560 + 12, 232, COPP, 3)
    s += text(576, 258, "Cвих", 9.5, COPP, "start", "bold")
    s += line(60, 300, 560, 300, INK, 2)
    # FB-резистор (опц.)
    s += line(500, 210, 640, 210, GREEN, 2)
    s += rect(645, 196, 60, 28, "#ffffff", GREEN, 1.6, 5)
    s += text(675, 214, "Rдільн.", 9.5, GREEN, "middle", "bold")
    s += text(675, 240, "(або фікс. вихід)", 9, GREY, "middle")
    s += line(500, 160, 560, 160, AMBER, 2)
    s += text(600, 164, "PG (готово)", 9.5, AMBER, "start")
    # «за що платимо» / «що виграємо»
    s += rect(730, 70, 150, 250, "#fbf7ec", AMBER, 1.6, 10)
    s += text(805, 92, "Компроміс", 11.5, AMBER, "middle", "bold")
    s += text(740, 116, "✓ найшвидше", 9.5, GREEN, "start", "bold")
    s += text(740, 132, "✓ мала площа", 9.5, GREEN, "start")
    s += text(740, 148, "✓ розводка — в", 9.5, GREEN, "start")
    s += text(740, 162, "  корпусі (надійно)", 9.5, GREEN, "start")
    s += text(740, 184, "✗ дорожче/штуку", 9.5, RED, "start", "bold")
    s += text(740, 200, "✗ тепло щільне", 9.5, RED, "start")
    s += text(740, 216, "✗ фікс. котушка", 9.5, RED, "start")
    s += text(740, 230, "  → менш гнучко", 9.5, RED, "start")
    s += text(740, 252, "✗ стеля струму", 9.5, RED, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Платиш ціною за штуку й гнучкістю — а купуєш час, площу й те, що найризикованіше (розводку) зроблено за тебе", 10.5, INK, "middle")
    save("fig-10-2c1-module.svg", s)


if __name__ == "__main__":
    # тема 10.2.1
    fig_budget_to_spec()
    fig_vin_range()
    fig_output_spec()
    fig_transient()
    fig_spec_axes()
    fig_spec_sheet()
    # вставка 🔌 до 10.2.2
    fig_c2_module()
    # вставка 🧮 до 10.2.3
    fig_m3_worksheet()
    # вставка 🧮 до 10.2.4
    fig_m4_ripple_compare()
    # вставка 🧮 до 10.2.5
    fig_m5_loadstep()
    # вставка 🔌 до 10.2.7
    fig_c7_eload()
    # вставка ⚙️ до 10.2.7
    fig_a7_sweep()
    # тема 10.2.2
    fig_levels()
    fig_freq()
    fig_swloss()
    fig_emi()
    fig_current_cap()
    fig_control_mode()
    # тема 10.2.3
    fig_ind_datasheet()
    fig_saturation()
    fig_two_limits()
    fig_ind_losses()
    fig_hard_soft()
    fig_ind_pick()
    # тема 10.2.4
    fig_cap_roles()
    fig_cap_input()
    fig_cap_esr()
    fig_cap_types()
    fig_cap_dcbias()
    fig_cap_pick()
    # тема 10.2.5
    fig_fb_loop()
    fig_fb_divider()
    fig_fb_speed()
    fig_fb_ringing()
    fig_fb_loadstep()
    fig_fb_cap()
    # тема 10.2.6
    fig_hot_loop()
    fig_loop_size()
    fig_which_loop()
    fig_sw_node()
    fig_kelvin_fb()
    fig_layout_map()
    # тема 10.2.7
    fig_probe_error()
    fig_spring_tip()
    fig_eff_setup()
    fig_load_grid()
    fig_thermal_map()
    fig_verify_tz()
    # тема 10.2.8
    fig_symptom_map()
    fig_singing()
    fig_subharmonic()
    fig_sag()
    fig_scope_gallery()
    fig_diag_flow()
    print("done r02 figures")
