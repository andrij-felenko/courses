# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 17 — «Представлення чисел» (Модуль 3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; «дійсне» зелене;
стрілки через marker; шрифт sans-serif. Підписи — посекційно (Рис. C.S.N);
історія до розділу — секція 0 (Рис. 17.0.N). Скрипт нарощується по темах.
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


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


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


# ── гексаграми I Ching: риски «ян» (суцільна) і «інь» (розірвана) ───────────
def _yao(cx, cy, w, yang, color=INK):
    if yang:
        return line(cx - w / 2, cy, cx + w / 2, cy, color, 4)
    return (line(cx - w / 2, cy, cx - w * 0.14, cy, color, 4)
            + line(cx + w * 0.14, cy, cx + w / 2, cy, color, 4))


def _trigram(cx, cy, bits, w=44, gap=11):
    out = ""
    for i, b in enumerate(bits):  # bits зверху вниз (старший — згори)
        out += _yao(cx, cy - gap + i * gap, w, b)
    return out


# ── Рис. 17.0.1 — таймлайн: чим менше символів, тим… ───────────────────────
def fig_timeline():
    W, H = 880, 760
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: скількома символами можна рахувати?", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "від десяти цифр (пальці) до двох (0 і 1) — і чому остання, найбідніша система перемогла",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 100, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("давнина", "Пінгала, I Ching", "Двійкові ідеї задовго до Європи: просодія в Індії, гексаграми в Китаї", False),
        ("позиційні", "місце = степінь основи", "Геній «розрядів»: значення цифри залежить від місця (десяткова — з пальців)", False),
        ("1703", "Лейбніц / Leibniz", "ВСІ числа з 0 і 1: «Explication de l'Arithmétique Binaire»", False),
        ("~1703", "гексаграми I Ching", "Лейбніц вражений: давні китайці «вже мали» двійкову (інь=0, ян=1)", False),
        ("та ж епоха", "машина Лейбніца", "А рахувала вона… ДЕСЯТКОВО. Двійкова лишилась чистою теорією", False),
        ("1703–1937", "«лише курйоз»", "Двійкова чекала на застосування понад 200 років (як алгебра Буля)", False),
        ("XX ст.", "комп'ютер", "Два стани (Розд. 14) + логіка (Розд. 15) + двійкові числа — нарешті РАЗОМ", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, faint) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = INK
        if i == 2:
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15, (RED if i == 2 else col), "start", "bold")
        s += text(spine + 26, y + 17, q, 12, col, "start", style="italic")
    save("fig-17-0-1-timeline.svg", s)


# ── Рис. 17.0.2 — ідея Лейбніца: усі числа з 0 і 1 ─────────────────────────
def fig_leibniz_idea():
    W, H = 880, 450
    s = header(W, H)
    s += text(W / 2, 36, "Ідея Лейбніца: будь-яке число — лише з 0 і 1", 21, INK, "middle", "bold")
    s += text(W / 2, 58, "рахунок «перевалює» вже на двох символах; значення дає МІСЦЕ цифри — степінь двійки",
              12.5, GREY, "middle", style="italic")
    # лічба 0..8
    s += text(120, 100, "Лічба двійкою:", 13, INK, "start", "bold")
    counts = [(0, "0"), (1, "1"), (2, "10"), (3, "11"), (4, "100"), (5, "101"), (6, "110"), (7, "111"), (8, "1000")]
    for i, (d, b) in enumerate(counts):
        y = 128 + i * 28
        s += text(150, y, f"{d}", 13, GREY, "end")
        s += text(165, y, "→", 11, GREY, "start")
        s += text(195, y, b, 14, INK, "start", "bold")
    # розклад 1011
    s += text(560, 110, "Розряди = степені двійки:", 13, INK, "middle", "bold")
    bits = [("1", 8), ("0", 4), ("1", 2), ("1", 1)]
    bx = 440
    for i, (b, val) in enumerate(bits):
        x = bx + i * 80
        col = RED if b == "1" else BLUE
        s += rect(x, 140, 56, 50, "#fdf4f4" if b == "1" else "#f3f5fd", col, 2, 6)
        s += text(x + 28, 172, b, 18, col, "middle", "bold")
        s += text(x + 28, 210, f"×{val}", 12, GREY, "middle", "bold")
        s += text(x + 28, 128, f"2{['³','²','¹','⁰'][i]}", 11, GREY, "middle")
    s += text(680, 250, "= 8 + 0 + 2 + 1 = 11", 16, GREEN, "middle", "bold")
    # богословський «гачок»
    s += rect(440, 290, 400, 110, "#f4f7f4", GREEN, 1.6, 10)
    s += text(640, 316, "«Гачок» Лейбніца був і філософський:", 12.5, INK, "middle", "bold")
    s += text(640, 342, "0 — ніщо (порожнеча), 1 — єдність;", 12, INK, "middle")
    s += text(640, 364, "усе суще будується з нічого і одиниці.", 12, INK, "middle")
    s += text(640, 386, "Для нього двійкова була майже священною.", 11, GREY, "middle", style="italic")
    save("fig-17-0-2-leibniz-idea.svg", s)


# ── Рис. 17.0.3 — гексаграми I Ching ↔ двійкова ────────────────────────────
def fig_iching():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 36, "Подив Лейбніца: гексаграми I Ching — це і є двійкові числа", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "давньокитайські фігури з рисок: суцільна (ян) = 1, розірвана (інь) = 0 — точна двійкова лічба",
              12, GREY, "middle", style="italic")
    # 8 триграм 000..111
    for v in range(8):
        x = 110 + v * 90
        bits = ((v >> 2) & 1, (v >> 1) & 1, v & 1)  # старший згори
        s += _trigram(x, 170, bits, w=54, gap=14)
        # двійкове й десяткове
        bstr = f"{(bits[0])}{(bits[1])}{(bits[2])}"
        s += text(x, 215, bstr, 13, INK, "middle", "bold")
        s += text(x, 234, f"= {v}", 12, RED, "middle", "bold")
    s += text(60, 156, "ян 1", 11, INK, "end", "bold")
    s += _yao(95, 156, 36, True)
    s += text(60, 184, "інь 0", 11, INK, "end", "bold")
    s += _yao(95, 184, 36, False)
    s += rect(70, 270, W - 140, 80, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 296, "Лейбніц упізнав у тисячолітніх гексаграмах власну двійкову систему — і був вражений до глибини душі.",
              12, INK, "middle", "bold")
    s += text(W / 2, 318, "Усіх гексаграм (по 6 рисок) — 64, тобто рівно двійкові числа 0…63. Збіг не випадковий: це й є рахунок двома станами.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 338, "Одна й та сама ідея незалежно зринала в різних культурах — настільки вона глибока.", 11, GREY, "middle", style="italic")
    save("fig-17-0-3-iching.svg", s)


# ── Рис. 17.0.4 — три потоки сходяться в комп'ютері ────────────────────────
def fig_convergence():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 36, "Куди привів цей ланцюг: три потоки 0/1 сходяться в комп'ютері", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "двійкова чекала ~200 років, аж поки фізика й логіка не дали їй тіло — і всі три злилися воєдино",
              12, GREY, "middle", style="italic")
    streams = [
        ("ДВА ФІЗИЧНІ СТАНИ", "напруга низько/високо", "Розділ 14", "#f3f5fd", BLUE, 150),
        ("БУЛЕВА ЛОГІКА", "і / або / не над 0,1", "Розділ 15", "#eef7ee", GREEN, 240),
        ("ДВІЙКОВІ ЧИСЛА", "число з 0 і 1 (Лейбніц)", "Розділ 17", "#fdf4f4", RED, 330),
    ]
    for title, sub, ch, bg, col, y in streams:
        s += rect(70, y - 28, 280, 56, bg, col, 1.8, 10)
        s += text(210, y - 6, title, 13, col, "middle", "bold")
        s += text(210, y + 14, f"{sub}  ({ch})", 11, GREY, "middle")
        s += arrow(350, y, 470, 235, INK, 1.8)
    s += rect(470, 175, 340, 120, "#fff8e8", AMBER, 2, 12)
    s += text(640, 210, "КОМП'ЮТЕР", 16, "#9a7322", "middle", "bold")
    s += text(640, 236, "0 і 1 — це водночас", 12.5, INK, "middle", "bold")
    s += text(640, 258, "і фізичний стан, і логіка,", 12, INK, "middle")
    s += text(640, 278, "і ЧИСЛО", 13, RED, "middle", "bold")
    s += text(W / 2, 348, "Цей розділ — про третій потік: як саме з 0 і 1 робити ЧИСЛА — додатні й від'ємні, дробові, великі.",
              12, INK, "middle", "bold")
    s += text(W / 2, 372, "Бо щойно «0 і 1» стають числом, біти в регістрах (Розділ 16) перетворюються на арифметику.",
              11.5, GREY, "middle", style="italic")
    save("fig-17-0-4-convergence.svg", s)


def _bitbox(x, y, b, w=46, h=46, weight=None):
    col = RED if b == 1 else BLUE
    bg = "#fdf4f4" if b == 1 else "#f3f5fd"
    out = rect(x, y, w, h, bg, col, 2, 6)
    out += text(x + w / 2, y + h * 0.66, str(b), 17, col, "middle", "bold")
    if weight is not None:
        out += text(x + w / 2, y - 8, weight, 10, GREY, "middle")
    return out


# ═══════════════════════ §17.1 — Чому двійкова ══════════════════════════════
# ── Рис. 17.1.1 — два рівні vs десять для ОДНОГО розряду ───────────────────
def fig171_why_two():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 34, "Чому в залізі два символи, а не десять: надійність розряду", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "щоб зберегти цифру дротом, кожне значення — окремий рівень напруги; менше рівнів = ширші «ями» (§14.1, §14.3)",
              11.5, GREY, "middle", style="italic")
    top_y, bot_y = 100, 380
    Vdd = 3.3
    noise_px = 0.5 / Vdd * (bot_y - top_y)

    def bar(cx, levels, title, sub, col_ok):
        out = text(cx, 86, title, 14, INK, "middle", "bold")
        out += rect(cx - 50, top_y, 100, bot_y - top_y, "#fafafa", INK, 2, 0)
        for k in range(levels):
            ly = bot_y - (bot_y - top_y) * k / (levels - 1)
            out += line(cx - 50, ly, cx + 50, ly, GREY if 0 < k < levels - 1 else (RED if k == levels - 1 else BLUE), 2)
        step = (bot_y - top_y) / (levels - 1)
        out += line(cx + 64, bot_y, cx + 64, bot_y - step, INK, 1.6)
        out += line(cx + 60, bot_y, cx + 68, bot_y, INK, 1.6)
        out += line(cx + 60, bot_y - step, cx + 68, bot_y - step, INK, 1.6)
        out += text(cx + 72, bot_y - step / 2 + 4, "яма", 11, INK, "start", "bold")
        ny = top_y + 30
        out += rect(cx - 14, ny, 28, noise_px, "#fbf3e0", AMBER, 1.6, 2)
        out += text(cx, ny - 6, "шум", 10.5, AMBER, "middle", "bold")
        out += text(cx, bot_y + 24, sub, 12, col_ok, "middle", "bold")
        return out

    s += bar(230, 10, "десяткова: 10 рівнів", "крок ~0.37 В → шум плутає", RED)
    s += text(230, 412, "✘ тісно, ненадійно", 12, RED, "middle", "bold")
    s += bar(640, 2, "двійкова: 2 рівні", "крок 3.3 В → шум безсилий", GREEN)
    s += text(640, 412, "✔ просто, надійно", 12, GREEN, "middle", "bold")
    s += text(W / 2, top_y + 150, "той самий", 11, GREY, "middle", style="italic")
    s += text(W / 2, top_y + 166, "шум 0.5 В", 11, GREY, "middle", style="italic")
    save("fig-17-1-1-why-two.svg", s)


# ── Рис. 17.1.2 — ціна: двійкова довша ─────────────────────────────────────
def fig171_cost():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 34, "Ціна двійкової — довжина; виграш — простота й надійність розряду", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "те саме число займає більше розрядів, та кожен розряд тепер тривіальний (0 або 1) і стійкий до шуму",
              11.5, GREY, "middle", style="italic")
    s += text(120, 130, "десяткова:", 13, INK, "start", "bold")
    for i, d in enumerate("233"):
        x = 280 + i * 60
        s += rect(x, 110, 50, 50, "#eef4ff", INK, 2, 6)
        s += text(x + 25, 144, d, 18, INK, "middle", "bold")
    s += text(480, 144, "3 розряди (по 10 значень)", 12, GREY, "start")
    s += text(120, 230, "двійкова:", 13, INK, "start", "bold")
    for i, b in enumerate("11101001"):
        x = 230 + i * 56
        s += _bitbox(x, 210, int(b), 46, 46)
    s += text(120, 290, "8 розрядів (по 2 значення)", 12, GREY, "start")
    s += text(700, 290, "= 128+64+32+8+1 = 233", 12.5, GREEN, "end", "bold")
    s += rect(70, 312, W - 140, 22, "none", "none", 0)
    s += text(W / 2, 326, "Більше дротів/бітів — дешево; надійність кожного біта — безцінна. Тому машини обрали довшу, зате просту двійкову.",
              11.5, INK, "middle", "bold")
    save("fig-17-1-2-cost.svg", s)


# ── Рис. 17.1.3 — біт і місткість 2ᴺ ───────────────────────────────────────
def fig171_capacity():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Біт — один двійковий розряд; N бітів тримають 2ᴺ значень", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен доданий біт ПОДВОЮЄ кількість можливих комбінацій — місткість росте вибухово",
              12, GREY, "middle", style="italic")
    # перелік для 1,2,3 біти
    combos = {1: ["0", "1"], 2: ["00", "01", "10", "11"],
              3: ["000", "001", "010", "011", "100", "101", "110", "111"]}
    xs = {1: 130, 2: 280, 3: 440}
    for n in (1, 2, 3):
        x = xs[n]
        s += text(x + 14, 96, f"{n} біт → {2**n}", 12, INK, "middle", "bold")
        for i, c in enumerate(combos[n]):
            s += text(x, 122 + i * 22, c, 12, RED if c.count("1") else BLUE, "start", "bold")
    # таблиця місткостей
    s += rect(580, 90, 270, 240, "#f4f7f4", GREEN, 1.6, 10)
    s += text(715, 116, "Місткість = 2ᴺ", 13, INK, "middle", "bold")
    caps = [("1 біт", "2"), ("4 біти", "16"), ("8 бітів (байт)", "256"),
            ("16 бітів", "65 536"), ("32 біти", "≈ 4.3 млрд"), ("64 біти", "≈ 1.8·10¹⁹")]
    for i, (a, b) in enumerate(caps):
        y = 146 + i * 30
        s += text(600, y, a, 12, INK, "start", "bold")
        s += text(830, y, b, 12, GREEN, "end", "bold")
    s += text(W / 2, 396, "Один біт — це 2 значення; вісім — уже 256; тридцять два — мільярди. Кожен біт коштує небагато, а дає вдвічі більше.",
              11.5, INK, "middle", "bold")
    save("fig-17-1-3-capacity.svg", s)


# ── Рис. 17.1.4 — байт і «те саме, та різне» ───────────────────────────────
def fig171_byte():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Байт — 8 бітів (256 значень); але що вони ЗНАЧАТЬ — справа тлумачення", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вісім бітів — стандартна «порція»; самі по собі вони лише 0/1 — сенс їм надає домовленість",
              12, GREY, "middle", style="italic")
    bits = "11111111"
    x0 = 210
    for i, b in enumerate(bits):
        s += _bitbox(x0 + i * 56, 100, int(b), 50, 50, weight=str(2 ** (7 - i)))
    s += text(x0 - 12, 132, "байт:", 13, INK, "end", "bold")
    s += text(x0 + 4 * 56, 178, "8 бітів = одна порція = 256 можливих значень (0…255)", 11.5, GREY, "middle", style="italic")
    # те саме, та різне
    s += text(W / 2, 220, "Ті самі 8 бітів 11111111 можуть означати:", 13, INK, "middle", "bold")
    means = [("255", "беззнакове ціле (§17.1)"), ("−1", "знакове ціле (§17.3)"),
             ("'ÿ'", "символ (код)"), ("0.996…", "дріб (§17.5)")]
    for i, (v, d) in enumerate(means):
        x = 130 + i * 190
        s += rect(x, 244, 170, 56, "#fafafa", INK, 1.6, 8)
        s += text(x + 85, 270, v, 15, RED, "middle", "bold")
        s += text(x + 85, 290, d, 9.5, GREY, "middle")
    s += text(W / 2, 340, "Біти однакові — а число різне, залежно від ДОМОВЛЕНОСТІ. Саме про ці домовленості весь розділ.",
              11.5, INK, "middle", "bold")
    save("fig-17-1-4-byte.svg", s)


# ── Рис. 17.1.5 — усе — біти ───────────────────────────────────────────────
def fig171_everything():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Усе цифрове — це біти; цей розділ — про те, як з бітів робити ЧИСЛА", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "число, текст, зображення, звук — усе кодують тими самими 0 і 1; різниця лише в домовленості тлумачення",
              11.5, GREY, "middle", style="italic")
    # центр — біти
    s += rect(360, 150, 160, 60, "#fff8e8", AMBER, 2, 10)
    s += text(440, 178, "0 1 0 1 1 0 …", 14, INK, "middle", "bold")
    s += text(440, 198, "біти", 11, "#9a7322", "middle", "bold")
    targets = [("ЧИСЛО", "233, −7, 3.14", 150, GREEN, RED),
               ("ТЕКСT", "'A' = 65", 130, INK, INK),
               ("ЗОБРАЖЕННЯ", "піксель = R,G,B", 230, INK, INK),
               ("ЗВУК", "відлік амплітуди", 250, INK, INK)]
    pos = [(130, 130), (130, 240), (730, 130), (730, 240)]
    for (title, ex, _, col, _2), (x, y) in zip(targets, pos):
        s += rect(x - 80, y - 26, 160, 52, "#eef4ff", INK, 1.6, 8)
        s += text(x, y - 4, title, 12, col, "middle", "bold")
        s += text(x, y + 14, ex, 10, GREY, "middle")
        if x < 440:
            s += arrow(360, 180, x + 80, y, GREY, 1.6, "4 3")
        else:
            s += arrow(520, 180, x - 80, y, GREY, 1.6, "4 3")
    s += text(440, 300, "Розділ 17 — про лівий верхній квадрат: ЧИСЛА з 0 і 1", 12.5, GREEN, "middle", "bold")
    s += text(W / 2, 336, "Опанувавши числа, ви зрозумієте й решту: текст, колір, звук — це теж числа, лише інакше витлумачені.",
              11, GREY, "middle", style="italic")
    save("fig-17-1-5-everything.svg", s)


# ═══════════════════ §17.2 — Позиційні системи й hex ════════════════════════
# ── Рис. 17.2.1 — позиційне читання двійкового ─────────────────────────────
def fig172_positional():
    W, H = 880, 350
    s = header(W, H)
    s += text(W / 2, 34, "Як прочитати двійкове: кожен розряд — це степінь двійки", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "значення = сума розрядів, де стоїть 1, помножених на їхні степені 2 (як 235 = 2·100+3·10+5 у десятковій)",
              11.5, GREY, "middle", style="italic")
    bits = "10110110"
    places = [128, 64, 32, 16, 8, 4, 2, 1]
    x0 = 150
    for i, (b, p) in enumerate(zip(bits, places)):
        x = x0 + i * 72
        s += text(x + 23, 100, f"2{['⁷','⁶','⁵','⁴','³','²','¹','⁰'][i]}", 11, GREY, "middle")
        s += text(x + 23, 116, f"={p}", 10, GREY, "middle")
        s += _bitbox(x, 124, int(b), 46, 46)
        if b == "1":
            s += text(x + 23, 200, f"{p}", 12, GREEN, "middle", "bold")
        else:
            s += text(x + 23, 200, "0", 12, GREY, "middle")
    s += text(W / 2, 240, "= 128 + 32 + 16 + 4 + 2 = 182", 18, GREEN, "middle", "bold")
    s += rect(70, 270, W - 140, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 294, "Беремо лише розряди з одиницею, додаємо їхні степені двійки — і дістаємо десяткове значення.", 12, INK, "middle", "bold")
    s += text(W / 2, 312, "10110110 (двійкове) = 182 (десяткове).", 11.5, GREY, "middle", style="italic")
    save("fig-17-2-1-positional.svg", s)


# ── Рис. 17.2.2 — десяткове → двійкове через ділення ───────────────────────
def fig172_dec_to_bin():
    W, H = 860, 420
    s = header(W, H)
    s += text(W / 2, 34, "Десяткове → двійкове: ділимо на 2, читаємо остачі знизу вгору", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "щоразу ділимо на 2 й записуємо остачу (0 чи 1); коли дійшли до 0 — читаємо стовпчик остач ЗНИЗУ ВГОРУ",
              11.5, GREY, "middle", style="italic")
    steps = [(182, 91, 0), (91, 45, 1), (45, 22, 1), (22, 11, 0),
             (11, 5, 1), (5, 2, 1), (2, 1, 0), (1, 0, 1)]
    x0 = 250
    for i, (a, q, r) in enumerate(steps):
        y = 100 + i * 34
        s += text(x0, y, f"{a} ÷ 2 = {q},", 13, INK, "end")
        s += text(x0 + 12, y, "остача", 12, GREY, "start")
        s += rect(x0 + 80, y - 16, 26, 24, "#fdf4f4" if r else "#f3f5fd", RED if r else BLUE, 1.6, 4)
        s += text(x0 + 93, y, str(r), 13, RED if r else BLUE, "middle", "bold")
    # стрілка читання знизу вгору
    s += arrow(x0 + 130, 100 + 7 * 34, x0 + 130, 88, GREEN, 2)
    s += text(x0 + 150, 220, "читати", 11, GREEN, "start", "bold")
    s += text(x0 + 150, 236, "сюди", 11, GREEN, "start", "bold")
    s += text(560, 160, "остачі знизу вгору:", 13, INK, "start", "bold")
    s += text(560, 195, "1 0 1 1 0 1 1 0", 18, INK, "start", "bold")
    s += text(560, 225, "= 10110110", 15, GREEN, "start", "bold")
    s += text(560, 250, "(перевірка: = 182 ✓)", 11.5, GREY, "start", style="italic")
    s += rect(540, 280, 290, 90, "#f4f7f4", GREEN, 1.6, 10)
    s += text(685, 306, "Чому працює:", 12, INK, "middle", "bold")
    s += text(560, 330, "остача від ÷2 — це молодший біт;", 11, INK, "start")
    s += text(560, 350, "ділення «зсуває» число на розряд правіше.", 11, INK, "start")
    save("fig-17-2-2-dec-to-bin.svg", s)


# ── Рис. 17.2.3 — нечитабельність двійкового → hex ─────────────────────────
def fig172_readability():
    W, H = 860, 320
    s = header(W, H)
    s += text(W / 2, 34, "Двійкове задовге для очей — рятує шістнадцятковий «скоропис»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "32-бітне число — це 32 нулі й одиниці поспіль; те саме шістнадцятково — лише 8 знаків",
              12, GREY, "middle", style="italic")
    s += text(120, 120, "двійкове (32 біти):", 12.5, INK, "start", "bold")
    binstr = "1101 1110 1010 1101 1011 1110 1110 1111"
    s += text(120, 150, binstr, 13.5, GREY, "start", "bold")
    s += text(120, 174, "…спробуй прочитати чи не помилитися", 10.5, RED, "start", style="italic")
    s += arrow(W / 2, 195, W / 2, 225, INK, 2)
    s += text(120, 255, "шістнадцяткове:", 12.5, INK, "start", "bold")
    s += text(330, 256, "0x DE AD BE EF", 22, GREEN, "start", "bold")
    s += text(620, 256, "← ті самі 32 біти, 8 знаків", 11.5, GREY, "start", style="italic")
    s += text(W / 2, 300, "0xDEADBEEF — знаменита «налагоджувальна» позначка; одне й те саме число, та читати в рази легше.",
              11.5, INK, "middle", "bold")
    save("fig-17-2-3-readability.svg", s)


# ── Рис. 17.2.4 — hex-цифри й півбайт ──────────────────────────────────────
def fig172_hex_digits():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Шістнадцяткова: 16 цифр (0–9, A–F), кожна = рівно 4 біти", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "16 = 2⁴, тож одна hex-цифра точно відповідає чотирьом бітам (півбайту, nibble) — звідси вся зручність",
              11.5, GREY, "middle", style="italic")
    digs = "0123456789ABCDEF"
    for i, d in enumerate(digs):
        col = i % 8
        row = i // 8
        x = 90 + col * 100
        y = 110 + row * 130
        s += rect(x, y, 80, 100, "#fafafa", INK, 1.6, 8)
        s += text(x + 40, y + 26, d, 18, RED, "middle", "bold")
        s += text(x + 40, y + 48, f"{i}", 11, GREY, "middle")
        s += text(x + 40, y + 76, format(i, "04b"), 13, INK, "middle", "bold")
    s += text(90, 100, "hex", 10, GREY, "start")
    s += text(W / 2, 400, "A=10, B=11, C=12, D=13, E=14, F=15. Запам'ятати 16 «цифр» — мала ціна за стислість і легке зведення до бітів.",
              11.5, INK, "middle", "bold")
    save("fig-17-2-4-hex-digits.svg", s)


# ── Рис. 17.2.5 — двійкове ↔ hex групуванням по 4 ──────────────────────────
def fig172_grouping():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Двійкове ↔ hex: групуй по 4 біти — кожна четвірка стає однією цифрою", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "перетворення механічне й безпомилкове: 4 біти ↔ 1 hex-цифра, групуючи справа наліво",
              11.5, GREY, "middle", style="italic")
    # байт 10110110 = B6 = 182
    bits = "10110110"
    x0 = 200
    for i, b in enumerate(bits):
        x = x0 + i * 50
        s += _bitbox(x, 100, int(b), 44, 44)
    # групи
    s += rect(x0 - 4, 96, 4 * 50, 52, "none", GREEN, 1.6, 6)
    s += rect(x0 + 4 * 50 - 4, 96, 4 * 50, 52, "none", AMBER, 1.6, 6)
    s += text(x0 + 2 * 50 - 5, 170, "1011", 13, GREEN, "middle", "bold")
    s += text(x0 + 6 * 50 - 5, 170, "0110", 13, "#9a7322", "middle", "bold")
    s += arrow(x0 + 2 * 50 - 5, 178, x0 + 2 * 50 - 5, 206, INK, 1.6)
    s += arrow(x0 + 6 * 50 - 5, 178, x0 + 6 * 50 - 5, 206, INK, 1.6)
    s += text(x0 + 2 * 50 - 5, 230, "B", 22, GREEN, "middle", "bold")
    s += text(x0 + 6 * 50 - 5, 230, "6", 22, "#9a7322", "middle", "bold")
    s += text(x0 + 4 * 50 - 5, 270, "= 0xB6 = 182", 16, RED, "middle", "bold")
    s += rect(70, 296, W - 140, 64, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 320, "Записують hex з префіксом 0x (0xB6) або індексом ₁₆. Один байт = рівно 2 hex-цифри.", 12, INK, "middle", "bold")
    s += text(W / 2, 342, "Hex усюди: адреси пам'яті, значення регістрів, кольори (#RRGGBB), байти в даташитах.", 11.5, GREY, "middle", style="italic")
    save("fig-17-2-5-grouping.svg", s)


# ═══════════════════ §17.3 — Доповняльний код ══════════════════════════════
def _byte(x, y, bits, w=40, gap=2, signbit=False):
    out = ""
    for i, b in enumerate(bits):
        bx = x + i * (w + gap)
        col = RED if b == "1" else BLUE
        bg = "#fdf4f4" if b == "1" else "#f3f5fd"
        if signbit and i == 0:
            bg = "#fff3e0"
            col = "#9a7322"
        out += rect(bx, y, w, w, bg, col, 1.8, 5)
        out += text(bx + w / 2, y + w * 0.66, b, 15, col, "middle", "bold")
    return out


# ── Рис. 17.3.1 — проблема й наївний знак-величина ─────────────────────────
def fig173_problem():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Де взяти «мінус» серед 0 і 1? Наївний спосіб і його біди", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "найпростіше — віддати старший біт під ЗНАК (0=+, 1=−). Та цей «знак-величина» має дві халепи",
              11.5, GREY, "middle", style="italic")
    s += text(140, 110, "+5:", 13, INK, "end", "bold")
    s += _byte(160, 92, "00000101", signbit=True)
    s += text(140, 170, "−5:", 13, INK, "end", "bold")
    s += _byte(160, 152, "10000101", signbit=True)
    s += text(700, 110, "знак", 11, "#9a7322", "middle", "bold")
    s += text(700, 126, "↑", 12, "#9a7322", "middle", "bold")
    s += line(180, 88, 180, 80, "#9a7322", 1.4)
    # халепи
    s += rect(70, 220, 360, 140, "#fdf6f6", RED, 1.6, 10)
    s += text(250, 246, "Халепа 1: ДВА нулі", 13, RED, "middle", "bold")
    s += text(90, 274, "+0 = 00000000", 13, INK, "start", "bold")
    s += text(90, 300, "−0 = 10000000", 13, INK, "start", "bold")
    s += text(90, 326, "«мінус нуль»? — безглуздя, та", 11, GREY, "start")
    s += text(90, 344, "марнує одне значення й плутає логіку", 11, GREY, "start")
    s += rect(450, 220, 380, 140, "#fdf6f6", RED, 1.6, 10)
    s += text(640, 246, "Халепа 2: не можна просто додавати", 12.5, RED, "middle", "bold")
    s += text(470, 274, "5 + (−5) має дати 0, але «в лоб»:", 11.5, INK, "start")
    s += text(470, 298, "00000101 + 10000101 = 10001010", 12, INK, "start", "bold")
    s += text(470, 320, "= −10 (!) замість 0", 12, RED, "start", "bold")
    s += text(470, 344, "→ потрібна окрема, хитра логіка додавання", 11, GREY, "start")
    s += text(W / 2, 388, "Знак-величина проста для ока, та незручна для заліза. Потрібен спосіб, де додавання «просто працює».",
              11.5, INK, "middle", "bold")
    save("fig-17-3-1-problem.svg", s)


# ── Рис. 17.3.2 — доповняльний код: інвертувати й додати 1 ──────────────────
def fig173_twoscomp():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Доповняльний код: щоб дістати −N, інвертуй усі біти й додай 1", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "два прості кроки — і від'ємне число готове; жодних «двох нулів», а додавання працює само собою",
              12, GREY, "middle", style="italic")
    s += text(150, 110, "+5:", 13, INK, "end", "bold")
    s += _byte(170, 92, "00000101")
    s += text(150, 175, "інверсія:", 12.5, INK, "end", "bold")
    s += _byte(170, 157, "11111010")
    s += text(560, 183, "(перевернули кожен біт)", 11, GREY, "start")
    s += text(150, 240, "+1:", 13, INK, "end", "bold")
    s += _byte(170, 222, "11111011")
    s += text(560, 248, "← це й є −5", 13, GREEN, "start", "bold")
    s += arrow(250, 138, 250, 153, INK, 1.8)
    s += text(290, 150, "інвертувати", 10.5, GREY, "start")
    s += arrow(250, 203, 250, 218, INK, 1.8)
    s += text(290, 215, "додати 1", 10.5, GREY, "start")
    s += rect(70, 290, W - 140, 56, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 314, "−5 = 11111011. Той самий рецепт повертає назад: інвертуй 11111011 → 00000100, +1 → 00000101 = +5.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 334, "Нуль один-єдиний: −0 = інверсія 00000000 (11111111) + 1 = 00000000 = +0. Жодного «мінус нуля».",
              11, GREY, "middle", style="italic")
    save("fig-17-3-2-twoscomp.svg", s)


# ── Рис. 17.3.3 — коло чисел (одометр) ─────────────────────────────────────
def fig173_circle():
    W, H = 820, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому це працює: числа лежать на КОЛІ (як одометр)", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "4-бітне коло: вгору від 0 — додатні; «вниз» від нуля (через верх) — від'ємні; усе замикається по колу",
              12, GREY, "middle", style="italic")
    cx, cy, r = 410, 270, 150
    s += circle(cx, cy, r, "none", FAINT, 2)
    for v in range(16):
        ang = math.radians(-90 + v * 360 / 16)
        px = cx + r * math.cos(ang)
        py = cy + r * math.sin(ang)
        signed = v if v < 8 else v - 16
        col = GREEN if 0 < v < 8 else (RED if v >= 8 else INK)
        s += circle(px, py, 4, col, col, 1)
        lx = cx + (r + 30) * math.cos(ang)
        ly = cy + (r + 30) * math.sin(ang)
        s += text(lx, ly - 4, format(v, "04b"), 10, INK, "middle", "bold")
        s += text(lx, ly + 10, f"{signed:+d}" if v != 0 else "0", 10.5, col, "middle", "bold")
    s += text(cx, cy - 10, "додатні →", 12, GREEN, "middle", "bold")
    s += text(cx, cy + 8, "← від'ємні", 12, RED, "middle", "bold")
    s += text(cx, cy + 28, "межа: 0111(+7) | 1000(−8)", 10, GREY, "middle", style="italic")
    s += rect(60, 380, W - 120, 76, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 404, "1111 = −1 (на крок «не дійшли» до 0); 1000 = −8 (найменше). Старший біт 1 = від'ємне.", 12, INK, "middle", "bold")
    s += text(W / 2, 426, "Додавання — це крок по колу за годинниковою; −N лежить рівно там, куди впираєшся, відступивши N назад від 0.",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 444, "Саме тому додавання й віднімання тут — одне й те саме коло.", 11, GREY, "middle", style="italic")
    save("fig-17-3-3-circle.svg", s)


# ── Рис. 17.3.4 — віднімання = додавання ───────────────────────────────────
def fig173_subtraction():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 34, "Магія: віднімання — це просто додавання доповняльного коду", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "7 − 5 = 7 + (−5): подаємо на ТОЙ САМИЙ суматор (§15.6) число й доповняльний код від'ємника",
              12, GREY, "middle", style="italic")
    s += text(150, 120, "7", 14, INK, "end", "bold")
    s += text(180, 120, "= 00000111", 14, INK, "start", "bold")
    s += text(150, 160, "+ (−5)", 14, INK, "end", "bold")
    s += text(180, 160, "= 11111011", 14, INK, "start", "bold")
    s += line(180, 175, 470, 175, INK, 1.6)
    s += text(150, 205, "сума", 13, GREEN, "end", "bold")
    s += text(150, 230, "(відкидаємо", 10, GREY, "end")
    s += text(150, 244, "перенос →)", 10, GREY, "end")
    s += text(180, 205, "1 00000010", 14, GREEN, "start", "bold")
    s += rect(178, 190, 22, 22, "none", RED, 1.6, 3)
    s += text(189, 226, "↑ викинути", 9, RED, "middle")
    s += text(330, 205, "= 00000010 = 2", 14, GREEN, "start", "bold")
    s += text(330, 230, "(а 7 − 5 = 2 ✓)", 11.5, GREY, "start", style="italic")
    s += rect(540, 100, 290, 200, "#f4f7f4", GREEN, 1.6, 10)
    s += text(685, 126, "Чому це безцінно:", 12.5, INK, "middle", "bold")
    for i, t in enumerate(["• НЕ потрібен окремий «віднімач» —", "  той самий суматор робить і +, і −",
                           "• той самий додавальний ланцюг", "  обслуговує і знакові, і беззнакові",
                           "• перенос за межу байта просто", "  «викидають» (коло замкнулось)",
                           "• тому в процесорі ОДНА команда", "  додавання — на все"]):
        s += text(556, 152 + i * 19, t, 10.6, INK, "start")
    save("fig-17-3-4-subtraction.svg", s)


# ── Рис. 17.3.5 — діапазон і як читати ─────────────────────────────────────
def fig173_range():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 34, "Діапазон знакового байта й як його прочитати", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "старший біт несе ВІД'ЄМНУ вагу −128; решта — звичайні додатні ваги. Сума й дає знакове число",
              12, GREY, "middle", style="italic")
    bits = "11111011"
    weights = [-128, 64, 32, 16, 8, 4, 2, 1]
    x0 = 150
    for i, (b, w) in enumerate(zip(bits, weights)):
        x = x0 + i * 72
        col = "#9a7322" if i == 0 else GREY
        s += text(x + 23, 100, f"{w:+d}" if i == 0 else f"{w}", 11, col, "middle", "bold")
        s += _byte(x, 110, b, w=46, gap=0, signbit=(i == 0))
        if b == "1":
            s += text(x + 23, 188, f"{w}", 12, ("#9a7322" if i == 0 else GREEN), "middle", "bold")
    s += text(W / 2, 222, "= −128 + 64 + 32 + 16 + 8 + 2 + 1 = −5", 16, RED, "middle", "bold")
    # діапазон
    s += rect(70, 250, W - 140, 110, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 276, "Діапазон 8-бітного знакового: від −128 до +127", 13, INK, "middle", "bold")
    s += text(W / 2, 300, "00000000 = 0   ·   01111111 = +127   ·   10000000 = −128   ·   11111111 = −1", 11.5, INK, "middle", "bold")
    s += text(W / 2, 324, "Як читати: старший біт 0 → додатне (читай як завжди); 1 → від'ємне (врахуй вагу −128).", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, 346, "Від'ємних на одне більше (−128 є, а +128 нема) — бо нуль «займає місце» серед додатних.", 11, GREY, "middle", style="italic")
    save("fig-17-3-5-range.svg", s)


# ═══════════════════════ §17.4 — Переповнення ══════════════════════════════
# ── Рис. 17.4.1 — беззнакове переповнення: 255 + 1 = 0 ─────────────────────
def fig174_unsigned():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Беззнакове переповнення: 255 + 1 = 0 (одометр «перевалив»)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у 8-бітну комірку влазить лише 0…255; додавши 1 до 255, дев'ятий біт «випадає», лишаючи нулі",
              11.5, GREY, "middle", style="italic")
    s += text(150, 120, "255", 14, INK, "end", "bold")
    s += text(178, 120, "= 11111111", 14, INK, "start", "bold")
    s += text(150, 160, "+ 1", 14, INK, "end", "bold")
    s += text(178, 160, "= 00000001", 14, INK, "start", "bold")
    s += line(178, 175, 470, 175, INK, 1.6)
    s += text(150, 205, "сума", 13, RED, "end", "bold")
    s += text(178, 205, "1 00000000", 14, RED, "start", "bold")
    s += rect(176, 190, 22, 22, "none", RED, 1.8, 3)
    s += text(187, 232, "↑ випав за байт", 9.5, RED, "middle")
    s += text(330, 205, "= 00000000 = 0 (!)", 14, RED, "start", "bold")
    # одометр
    s += circle(640, 160, 70, "none", FAINT, 2)
    for v, ang in ((255, -100), (0, -80), (1, -60), (254, -120)):
        a = math.radians(ang)
        px, py = 640 + 70 * math.cos(a), 160 + 70 * math.sin(a)
        s += circle(px, py, 3, INK, INK, 1)
        s += text(640 + 92 * math.cos(a), 160 + 92 * math.sin(a) + 4, str(v), 10, INK, "middle", "bold")
    s += arrow(620, 95, 660, 95, RED, 2)
    s += text(640, 165, "коло 0…255", 10, GREY, "middle")
    s += text(640, 250, "255 → 0 через верх", 10, RED, "middle", "bold")
    s += rect(70, 290, W - 140, 50, "#fdf6f6", RED, 1.6, 10)
    s += text(W / 2, 314, "Залізо не зупиняється й не лається — воно ТИХО дає 0. Лічильник на 255 «обнулиться» сам.", 12, INK, "middle", "bold")
    s += text(W / 2, 332, "Той «зайвий» перенос за межу — сигнал переповнення (прапорець Carry, §17.4 далі).", 11, GREY, "middle", style="italic")
    save("fig-17-4-1-unsigned.svg", s)


# ── Рис. 17.4.2 — знакове переповнення: +127 + 1 = −128 ────────────────────
def fig174_signed():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Знакове переповнення: +127 + 1 = −128 (додав додатні — дістав від'ємне!)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "найпідступніше: сума двох додатних «перевалює» через верх кола й стає найбільшим ВІД'ЄМНИМ",
              11.5, GREY, "middle", style="italic")
    s += text(150, 130, "+127", 14, GREEN, "end", "bold")
    s += text(180, 130, "= 01111111", 14, INK, "start", "bold")
    s += text(150, 170, "+ 1", 14, GREEN, "end", "bold")
    s += text(180, 170, "= 00000001", 14, INK, "start", "bold")
    s += line(180, 185, 470, 185, INK, 1.6)
    s += text(150, 215, "сума", 13, RED, "end", "bold")
    s += text(180, 215, "10000000", 16, RED, "start", "bold")
    s += text(330, 215, "= −128 (!!)", 15, RED, "start", "bold")
    s += text(180, 240, "старший біт став 1 → знак перевернувся", 10.5, RED, "start", "bold")
    # коло
    s += circle(660, 160, 64, "none", FAINT, 2)
    s += text(660, 90, "+127", 10, GREEN, "middle", "bold")
    s += text(660, 238, "−128", 10, RED, "middle", "bold")
    s += arrow(700, 110, 700, 210, RED, 2)
    s += text(745, 160, "+1 = стрибок", 9.5, RED, "start", "bold")
    s += text(745, 174, "через межу", 9.5, RED, "start")
    s += rect(70, 290, W - 140, 50, "#fdf6f6", RED, 1.6, 10)
    s += text(W / 2, 314, "Додали два додатні — отримали від'ємне. Жодного попередження: число просто «не вмістилось».", 12, INK, "middle", "bold")
    s += text(W / 2, 332, "Правило: якщо доданки одного знаку, а сума — іншого, сталося знакове переповнення.", 11, GREY, "middle", style="italic")
    save("fig-17-4-2-signed.svg", s)


# ── Рис. 17.4.3 — як помітити: прапорці ────────────────────────────────────
def fig174_detection():
    W, H = 860, 350
    s = header(W, H)
    s += text(W / 2, 34, "Як це помітити: процесор піднімає прапорці Carry й Overflow", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "після кожного додавання АЛП виставляє ознаки; програма (чи компілятор) може їх перевірити",
              12, GREY, "middle", style="italic")
    s += rect(70, 90, 360, 200, "none", BLUE, 1.7, 10)
    s += text(250, 116, "C — прапорець ПЕРЕНОСУ", 12.5, BLUE, "middle", "bold")
    s += text(90, 144, "= переніс «випав» за старший біт", 11.5, INK, "start")
    s += text(90, 168, "→ ознака БЕЗЗНАКОВОГО", 11.5, INK, "start", "bold")
    s += text(90, 188, "  переповнення", 11.5, INK, "start", "bold")
    s += text(90, 220, "приклад: 255 + 1 → C=1", 11, GREY, "start")
    s += text(90, 252, "(беззнаково вилізли за 255)", 10.5, GREY, "start", style="italic")
    s += rect(450, 90, 380, 200, "none", RED, 1.7, 10)
    s += text(640, 116, "V — прапорець ПЕРЕПОВНЕННЯ", 12.5, RED, "middle", "bold")
    s += text(470, 144, "= переніс У старший біт ≠ перенос ІЗ нього", 11, INK, "start")
    s += text(470, 168, "→ ознака ЗНАКОВОГО", 11.5, INK, "start", "bold")
    s += text(470, 188, "  переповнення", 11.5, INK, "start", "bold")
    s += text(470, 220, "приклад: 127 + 1 → V=1", 11, GREY, "start")
    s += text(470, 252, "(знаково вилізли за +127)", 10.5, GREY, "start", style="italic")
    s += text(W / 2, 320, "Ті самі біти додаються однаково; C стежить за беззнаковим, V — за знаковим переповненням.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 340, "Біда в тім, що за замовчуванням ці прапорці часто НЕ перевіряють — тому баг і тихий.", 11, GREY, "middle", style="italic")
    save("fig-17-4-3-detection.svg", s)


# ── Рис. 17.4.4 — славетні катастрофи переповнення ─────────────────────────
def fig174_disasters():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "📜 Славетні катастрофи переповнення", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "тихий числовий баг коштував ракет, рекордів і досі загрожує — ось чому про межі типів треба пам'ятати",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("Ariane 5, 1996", "64-бітне число швидкості (float) перетворювали на 16-бітне знакове → переповнення → "
         "відмова системи орієнтації (SRI) → ракета зруйнувалася. ~$370 млн, ~37 с після старту.", RED, 84),
        ("«Gangnam Style», 2014", "Лічильник переглядів YouTube був 32-бітний знаковий (межа 2 147 483 647 ≈ 2.1 млрд). "
         "Кліп підійшов до межі — YouTube жартома оголосив про 64 біти (готові завчасно).", AMBER, 162),
        ("Проблема 2038 року", "Час у Unix — це 32-бітне знакове число секунд від 1970-го. "
         "19 січня 2038-го воно переповниться й «стрибне» у 1901-й.", "#9a7322", 240),
        ("Pac-Man, рівень 256", "8-бітний лічильник рівнів переповнюється на 256-му — "
         "екран псується наполовину («kill screen»), гру пройти неможливо.", INK, 318),
    ]
    for title, body, col, y in cards:
        s += rect(70, y, W - 140, 68, "#fafafa", col, 1.6, 10)
        s += text(90, y + 26, title, 13, col, "start", "bold")
        # розбити body на два рядки приблизно
        mid = body.rfind(" ", 0, len(body) // 2 + 12)
        s += text(90, y + 46, body[:mid], 11, INK, "start")
        s += text(90, y + 62, body[mid + 1:], 11, INK, "start")
    save("fig-17-4-4-disasters.svg", s)


# ── Рис. 17.4.5 — як уникати й коли переповнення корисне ───────────────────
def fig174_avoiding():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Як уникати — і коли переповнення навмисне корисне", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "переповнення — не завжди баг; біда лише тоді, коли воно НЕ заплановане",
              12, GREY, "middle", style="italic")
    s += rect(70, 90, 380, 230, "none", GREEN, 1.7, 10)
    s += text(260, 116, "Як убезпечитися", 13, GREEN, "middle", "bold")
    for i, t in enumerate([
        "• брати ТИП ширший за діапазон:",
        "   8→16→32→64 біти (з запасом)",
        "• перевіряти прапорці / межі перед дією",
        "• насичувальна арифметика (saturating):",
        "   не «перевалювати», а УПИРАТИСЬ у межу",
        "   (255 + 1 = 255, а не 0) — для звуку, графіки",
        "• розуміти знаковий чи беззнаковий тип"]):
        s += text(88, 144 + i * 24, t, 11, INK, "start")
    s += rect(470, 90, 360, 230, "none", BLUE, 1.7, 10)
    s += text(650, 116, "Коли wrap — це FEATURE", 13, BLUE, "middle", "bold")
    for i, t in enumerate([
        "• таймери/лічильники, що навмисно",
        "   «обнуляються» по колу (Розділ 24)",
        "• кільцевий буфер: індекс по модулю",
        "   розміру (іде по колу — Розділ 19)",
        "• модульна арифметика, гешування",
        "• різниця часу: (t2 − t1) у беззнакових",
        "   працює правильно навіть через wrap!"]):
        s += text(488, 144 + i * 24, t, 11, INK, "start")
    s += text(W / 2, 346, "Головне правило: переповнення має бути СВІДОМИМ вибором, а не несподіванкою.", 12, INK, "middle", "bold")
    save("fig-17-4-5-avoiding.svg", s)


# ═══════════════════════ §17.5 — Фіксована кома ════════════════════════════
# ── Рис. 17.5.1 — двійкова кома: дробові розряди ───────────────────────────
def fig175_point():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 34, "Двійкова кома: розряди праворуч мають ваги ½, ¼, ⅛…", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ліворуч від коми — цілі ваги (…4,2,1), праворуч — дробові (0.5, 0.25, 0.125): усе та сама позиційність",
              11.5, GREY, "middle", style="italic")
    bits = "1011"
    fbits = "011"
    wl = [8, 4, 2, 1]
    wf = [0.5, 0.25, 0.125]
    x = 150
    for i, b in enumerate(bits):
        s += text(x + 23, 100, str(wl[i]), 11, GREY, "middle", "bold")
        s += _bitbox(x, 116, int(b), 46, 46)
        if b == "1":
            s += text(x + 23, 190, str(wl[i]), 12, GREEN, "middle", "bold")
        x += 56
    # кома
    s += text(x + 4, 152, ".", 26, RED, "middle", "bold")
    s += text(x + 4, 100, "кома", 10, RED, "middle", "bold")
    x += 24
    for i, b in enumerate(fbits):
        s += text(x + 23, 100, str(wf[i]), 10, GREY, "middle", "bold")
        s += _bitbox(x, 116, int(b), 46, 46)
        if b == "1":
            s += text(x + 23, 190, str(wf[i]), 12, GREEN, "middle", "bold")
        x += 56
    s += text(W / 2, 230, "1011.011 = 8 + 2 + 1 + 0.25 + 0.125 = 11.375", 16, GREEN, "middle", "bold")
    s += rect(70, 262, W - 140, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 286, "Дробову частину читають так само, як цілу, лише ваги — від'ємні степені двійки (2⁻¹=½, 2⁻²=¼…).", 12, INK, "middle", "bold")
    s += text(W / 2, 304, "Та апаратура коми НЕ бачить — для неї це просто біти. Де ж тоді кома?", 11, GREY, "middle", style="italic")
    save("fig-17-5-1-point.svg", s)


# ── Рис. 17.5.2 — хитрість: масштабування ──────────────────────────────────
def fig175_scaling():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Хитрість фіксованої коми: кома — у голові, в залізі — ціле число", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "зберігаємо число × масштаб (тут ×16) як ЦІЛЕ; рахуємо цілою арифметикою; читаючи — ділимо назад",
              11.5, GREY, "middle", style="italic")
    s += text(260, 120, "хочемо зберегти", 12, INK, "end", "bold")
    s += text(280, 120, "23.5", 18, GREEN, "start", "bold")
    s += arrow(330, 115, 400, 115, INK, 2)
    s += text(365, 105, "× 16", 11, RED, "middle", "bold")
    s += text(420, 120, "376", 18, INK, "start", "bold")
    s += text(480, 120, "← оце ціле лежить у залізі", 11.5, GREY, "start", style="italic")
    s += text(260, 175, "читаємо назад", 12, INK, "end", "bold")
    s += text(280, 175, "376", 18, INK, "start", "bold")
    s += arrow(330, 170, 400, 170, INK, 2)
    s += text(365, 160, "÷ 16", 11, RED, "middle", "bold")
    s += text(420, 175, "23.5", 18, GREEN, "start", "bold")
    s += text(480, 175, "← знову наше число", 11.5, GREY, "start", style="italic")
    s += rect(70, 220, W - 140, 110, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 246, "Залізо тримає 376 і не знає про жодну кому — вона існує лише в нашій ДОМОВЛЕНОСТІ (§17.1).",
              12, INK, "middle", "bold")
    s += text(W / 2, 270, "«×16» = зсув коми на 4 розряди (бо 16 = 2⁴): 376 = 10111.1000 з комою після 4-го біта справа.",
              11.5, GREY, "middle", style="italic")
    s += text(W / 2, 294, "Жодного спецзаліза для дробів — лише звичайні цілі та звичка пам'ятати, де «уявна» кома.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 316, "Так само й «гроші в копійках»: зберігай ×100 цілим — і жодних похибок із дробами.", 11, GREY, "middle", style="italic")
    save("fig-17-5-2-scaling.svg", s)


# ── Рис. 17.5.3 — запис Qm.n ───────────────────────────────────────────────
def fig175_qnotation():
    W, H = 860, 350
    s = header(W, H)
    s += text(W / 2, 34, "Запис Qm.n: m бітів на ціле, n бітів на дріб", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "наприклад Q8.8 — 8 бітів цілої частини й 8 дробової (разом 16); масштаб = 2ⁿ",
              12, GREY, "middle", style="italic")
    # Q8.8 у 16-бітному
    x0 = 120
    for i in range(16):
        x = x0 + i * 42
        ipart = i < 8
        col = INK if ipart else "#9a7322"
        bg = "#eef4ff" if ipart else "#fbf6ec"
        s += rect(x, 110, 40, 40, bg, col, 1.6, 4)
    s += rect(x0, 110, 8 * 42 - 2, 40, "none", BLUE, 2, 4)
    s += rect(x0 + 8 * 42, 110, 8 * 42 - 2, 40, "none", AMBER, 2, 4)
    s += text(x0 + 4 * 42, 100, "ціла частина (8 біт)", 12, BLUE, "middle", "bold")
    s += text(x0 + 12 * 42, 100, "дробова частина (8 біт)", 12, "#9a7322", "middle", "bold")
    s += text(x0 + 8 * 42 - 1, 178, "↑ уявна кома", 11, RED, "middle", "bold")
    s += rect(70, 210, W - 140, 110, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 236, "Q8.8: масштаб 2⁸ = 256; крок (найменший дріб) = 1/256 ≈ 0.0039; діапазон ≈ −128…+127.99", 12, INK, "middle", "bold")
    s += text(W / 2, 262, "Хочеш точніший дріб — віддай більше бітів праворуч (Q4.12); хочеш більший діапазон — ліворуч (Q12.4).", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, 288, "Кома стоїть НЕРУХОМО (звідси «фіксована»): ти обираєш її місце наперед і ним торгуєш діапазон ↔ точність.", 11.5, INK, "middle", "bold")
    s += text(W / 2, 310, "Q16.16, Q8.8, Q4.4 — типові; вибір залежить від задачі.", 11, GREY, "middle", style="italic")
    save("fig-17-5-3-qnotation.svg", s)


# ── Рис. 17.5.4 — арифметика фіксованої коми ───────────────────────────────
def fig175_arithmetic():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 34, "Арифметика: додавання — просто, множення — зі зсувом назад", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "при однаковому масштабі коми «вирівняні», тож + і − просто цілі; а множення подвоює масштаб",
              11.5, GREY, "middle", style="italic")
    s += rect(60, 90, 380, 230, "none", GREEN, 1.7, 10)
    s += text(250, 116, "Додавання (Q4.4, ×16)", 12.5, GREEN, "middle", "bold")
    s += text(80, 148, "2.5  →  40", 13, INK, "start", "bold")
    s += text(80, 174, "1.25 →  20", 13, INK, "start", "bold")
    s += line(80, 186, 300, 186, INK, 1.4)
    s += text(80, 212, "сума →  60", 13, GREEN, "start", "bold")
    s += text(80, 244, "60 ÷ 16 = 3.75", 13, GREEN, "start", "bold")
    s += text(80, 272, "(а 2.5 + 1.25 = 3.75 ✓)", 11, GREY, "start", style="italic")
    s += text(80, 300, "масштаб не змінився → просто цілі +", 10.5, INK, "start", "bold")
    s += rect(470, 90, 360, 230, "none", AMBER, 1.7, 10)
    s += text(650, 116, "Множення (Q4.4, ×16)", 12.5, "#9a7322", "middle", "bold")
    s += text(490, 148, "2.5 → 40,   1.5 → 24", 13, INK, "start", "bold")
    s += text(490, 174, "40 × 24 = 960", 13, INK, "start", "bold")
    s += text(490, 200, "але масштаб став 16×16 = 256!", 11.5, RED, "start", "bold")
    s += text(490, 226, "÷ 16 (зсув на 4) → 60", 13, INK, "start", "bold")
    s += text(490, 252, "60 ÷ 16 = 3.75", 13, GREEN, "start", "bold")
    s += text(490, 278, "(а 2.5 × 1.5 = 3.75 ✓)", 11, GREY, "start", style="italic")
    s += text(490, 304, "після множення — зсунути назад на n", 10.5, "#9a7322", "start", "bold")
    s += text(W / 2, 344, "Тому фіксована кома «майже безкоштовна»: + і − задарма, множення — плюс один зсув.", 11.5, INK, "middle", "bold")
    save("fig-17-5-4-arithmetic.svg", s)


# ── Рис. 17.5.5 — плюси, мінуси, де вживають ───────────────────────────────
def fig175_proscons():
    W, H = 860, 350
    s = header(W, H)
    s += text(W / 2, 34, "Фіксована кома: швидко й точно, але діапазон і точність — фіксовані", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "ідеальна для мікроконтролерів без апаратних дробів; та доводиться наперед ділити біти між цілим і дробом",
              11.5, GREY, "middle", style="italic")
    s += rect(60, 86, 370, 200, "none", GREEN, 1.7, 10)
    s += text(245, 112, "Плюси", 13, GREEN, "middle", "bold")
    for i, t in enumerate(["• швидко: звичайна ціла арифметика", "   (не треба апаратних дробів / FPU)",
                           "• детерміновано й точно для свого кроку", "• мало пам'яті, передбачувано",
                           "• ідеально для DSP, звуку, керування", "   (Розділи 32, 34) і грошей (копійки)"]):
        s += text(78, 140 + i * 24, t, 11, INK, "start")
    s += rect(470, 86, 360, 200, "none", AMBER, 1.7, 10)
    s += text(650, 112, "Мінуси", 13, "#9a7322", "middle", "bold")
    for i, t in enumerate(["• кома НЕРУХОМА — мусиш обрати її", "   місце наперед",
                           "• торгуєш діапазон ↔ точність:", "   або великі числа, або дрібні дробі",
                           "• малий «динамічний діапазон»", "• невдалий масштаб → втрата точності"]):
        s += text(488, 140 + i * 24, t, 11, INK, "start")
    s += text(W / 2, 314, "Як одночасно тримати й величезні, й крихітні числа з гарною точністю? — це вже плаваюча кома (§17.6).",
              12, INK, "middle", "bold")
    s += text(W / 2, 336, "Фіксована кома — простий, швидкий робочий кінь; плаваюча — гнучкий, та дорожчий.", 11, GREY, "middle", style="italic")
    save("fig-17-5-5-proscons.svg", s)


# ═══════════════════════ §17.6 — Плаваюча кома ═════════════════════════════
# ── Рис. 17.6.1 — як наукова нотація: кома пливе ───────────────────────────
def fig176_scientific():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 34, "Ідея: як наукова нотація — мантиса × основа^порядок", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "число пишуть як «значущі цифри × степінь»; порядок каже, КУДИ посунути кому — тож вона «пливе»",
              12, GREY, "middle", style="italic")
    # десяткова наукова
    s += text(150, 120, "десятково:", 13, INK, "start", "bold")
    s += text(330, 120, "6.022", 18, GREEN, "middle", "bold")
    s += text(420, 120, "× 10", 16, INK, "start", "bold")
    s += text(470, 110, "23", 12, RED, "start", "bold")
    s += text(330, 145, "мантиса", 10, GREEN, "middle")
    s += text(450, 145, "порядок", 10, RED, "middle")
    # двійкова
    s += text(150, 200, "двійково:", 13, INK, "start", "bold")
    s += text(330, 200, "1.101", 18, GREEN, "middle", "bold")
    s += text(415, 200, "× 2", 16, INK, "start", "bold")
    s += text(450, 190, "3", 12, RED, "start", "bold")
    s += text(490, 200, "= 1.625 × 8 = 13", 14, GREEN, "start", "bold")
    s += rect(70, 240, W - 140, 80, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 266, "Порядок (степінь) рухає кому куди завгодно — звідси й назва «плаваюча кома».", 12.5, INK, "middle", "bold")
    s += text(W / 2, 288, "Велике число — великий порядок; крихітне — від'ємний. Одним форматом — і мільярди, і мільйонні частки.", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, 310, "Мантиса несе значущі цифри (точність), порядок — масштаб (діапазон). Розділили — і виграли обидва.", 11.5, INK, "middle", "bold")
    save("fig-17-6-1-scientific.svg", s)


# ── Рис. 17.6.2 — формат IEEE 754 (float32) ────────────────────────────────
def fig176_format():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 34, "Формат IEEE 754 (одинарна точність, float32 = 32 біти)", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "три поля: знак (1 біт), порядок (8 бітів, зі зсувом), мантиса (23 біти значущих цифр)",
              12, GREY, "middle", style="italic")
    x0 = 90
    # знак
    s += rect(x0, 110, 50, 50, "#fff3e0", "#9a7322", 2, 5)
    s += text(x0 + 25, 142, "S", 16, "#9a7322", "middle", "bold")
    s += text(x0 + 25, 100, "1", 10, GREY, "middle")
    s += text(x0 + 25, 180, "знак", 11, "#9a7322", "middle", "bold")
    # порядок
    s += rect(x0 + 60, 110, 230, 50, "#eef4ff", BLUE, 2, 5)
    s += text(x0 + 175, 142, "порядок (exponent)", 14, BLUE, "middle", "bold")
    s += text(x0 + 175, 100, "8 бітів", 10, GREY, "middle")
    s += text(x0 + 175, 180, "куди «пливе» кома", 11, BLUE, "middle", "bold")
    # мантиса
    s += rect(x0 + 300, 110, 400, 50, "#eef7ee", GREEN, 2, 5)
    s += text(x0 + 500, 142, "мантиса (significand)", 14, GREEN, "middle", "bold")
    s += text(x0 + 500, 100, "23 біти", 10, GREY, "middle")
    s += text(x0 + 500, 180, "значущі цифри (точність)", 11, GREEN, "middle", "bold")
    s += rect(70, 215, W - 140, 110, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 241, "значення = (−1)ˢ × 1.мантиса × 2^(порядок − 127)", 15, INK, "middle", "bold")
    s += text(W / 2, 266, "Старша одиниця мантиси «мається на увазі» (1.xxxx) — даровий зайвий біт точності.", 11.5, GREY, "middle", style="italic")
    s += text(W / 2, 290, "float32 ≈ 7 значущих десяткових цифр. Подвійна точність (float64): 1 + 11 + 52 = 64 біти, ≈ 16 цифр.", 11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Той самий формат — у кожному ПК, телефоні, ESP32: домовленість IEEE 754 (історія — поряд).", 11, GREY, "middle", style="italic")
    save("fig-17-6-2-format.svg", s)


# ── Рис. 17.6.3 — величезний динамічний діапазон ───────────────────────────
def fig176_range():
    W, H = 860, 320
    s = header(W, H)
    s += text(W / 2, 34, "Виграш: величезний динамічний діапазон", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "float32 покриває від ~10⁻³⁸ до ~10³⁸ — і крихітне, і астрономічне одним типом",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 110, 800
    ax = 170
    s += line(gx0, ax, gx1, ax, INK, 2)
    marks = [(-38, "10⁻³⁸"), (-19, "10⁻¹⁹"), (0, "1"), (19, "10¹⁹"), (38, "10³⁸")]
    for e, lab in marks:
        x = gx0 + (e + 38) / 76 * (gx1 - gx0)
        s += line(x, ax - 6, x, ax + 6, GREY, 1.4)
        s += text(x, ax + 24, lab, 11, INK, "middle", "bold")
    s += text(gx0, ax - 16, "крихітне ←", 11, BLUE, "start", "bold")
    s += text(gx1, ax - 16, "→ величезне", 11, RED, "end", "bold")
    # фіксована кома — вузьке вікно
    fx0 = gx0 + (32) / 76 * (gx1 - gx0)
    fx1 = gx0 + (44) / 76 * (gx1 - gx0)
    s += rect(fx0, ax + 40, fx1 - fx0, 24, "#fbf6ec", AMBER, 1.6, 4)
    s += text((fx0 + fx1) / 2, ax + 90, "фіксована кома —", 11, "#9a7322", "middle", "bold")
    s += text((fx0 + fx1) / 2, ax + 106, "лише вузьке вікно", 10.5, GREY, "middle")
    s += text(W / 2, 300, "Той самий float тримає і масу електрона, і відстань до зір. Це й є перевага плаваючої коми над фіксованою.",
              11.5, INK, "middle", "bold")
    save("fig-17-6-3-range.svg", s)


# ── Рис. 17.6.4 — чому float підступний ────────────────────────────────────
def fig176_tricky():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому float підступний: неточність і ВІДНОСНА точність", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "не всі числа представні точно, а «крок» між сусідніми зростає з величиною — звідси класичні пастки",
              11.5, GREY, "middle", style="italic")
    # 0.1 + 0.2
    s += rect(60, 84, 380, 130, "none", RED, 1.7, 10)
    s += text(250, 110, "Пастка 1: неточність", 12.5, RED, "middle", "bold")
    s += text(80, 138, "0.1 + 0.2 = 0.30000000000000004 (!)", 12.5, INK, "start", "bold")
    s += text(80, 164, "бо 0.1 у двійковій — нескінченний дріб", 11, GREY, "start")
    s += text(80, 184, "(як 1/3 у десятковій), тож зберігається з", 11, GREY, "start")
    s += text(80, 202, "крихітною похибкою округлення.", 11, GREY, "start")
    # відносна точність
    s += rect(470, 84, 360, 130, "none", AMBER, 1.7, 10)
    s += text(650, 110, "Пастка 2: відносна точність", 12, "#9a7322", "middle", "bold")
    s += text(490, 138, "крок між числами РОСТЕ з величиною:", 11, INK, "start")
    s += text(490, 160, "біля 1 → крок ≈ 0.0000001", 11, INK, "start")
    s += text(490, 180, "біля мільйона → крок ≈ 0.06", 11, INK, "start")
    s += text(490, 200, "біля мільярда → крок > 1 (!)", 11.5, RED, "start", "bold")
    # наслідок
    s += rect(60, 230, 380, 110, "#fdf6f6", RED, 1.6, 10)
    s += text(250, 256, "Наслідок:", 12, RED, "middle", "bold")
    s += text(80, 282, "1 000 000 000 + 1 = 1 000 000 000", 12.5, INK, "start", "bold")
    s += text(80, 304, "(float32): додавання просто «зникло»,", 11, GREY, "start")
    s += text(80, 322, "бо 1 менше за крок на цій величині.", 11, GREY, "start")
    s += rect(470, 230, 360, 110, "#fdf6f6", RED, 1.6, 10)
    s += text(650, 256, "Результати обчислень — не порівнюй через ==", 11, RED, "middle", "bold")
    s += text(490, 284, "погано:  if (x == 0.3)", 12, INK, "start", "bold")
    s += text(490, 308, "добре:   if (|x − 0.3| < ε)", 12, GREEN, "start", "bold")
    s += text(490, 328, "(для точних 0.0, цілих — == доречне)", 10.5, GREY, "start", style="italic")
    s += text(W / 2, 366, "float чудовий для діапазону, та оманливий для точності: рівність, накопичення похибок, гроші — його слабкі місця.",
              11.5, INK, "middle", "bold")
    save("fig-17-6-4-tricky.svg", s)


# ── Рис. 17.6.5 — особливі значення й ціна ─────────────────────────────────
def fig176_special():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 34, "Особливі значення й ціна плаваючої коми", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "float уміє «нескінченність» і «не-число», та коштує складної логіки — без апаратного блоку (FPU) повільний",
              11.5, GREY, "middle", style="italic")
    s += rect(60, 84, 380, 210, "none", BLUE, 1.7, 10)
    s += text(250, 110, "Особливі значення", 13, BLUE, "middle", "bold")
    items = [("+∞ / −∞", "переповнення, ділення на 0"),
             ("NaN", "«не число»: 0/0, √(−1) — заразне!"),
             ("+0 / −0", "два нулі (нешкідливо)"),
             ("денормалі", "найдрібніші, біля нуля")]
    for i, (v, d) in enumerate(items):
        y = 142 + i * 36
        s += text(80, y, v, 13, RED, "start", "bold")
        s += text(200, y, d, 11, INK, "start")
    s += rect(470, 84, 360, 210, "none", AMBER, 1.7, 10)
    s += text(650, 110, "Ціна", 13, "#9a7322", "middle", "bold")
    for i, t in enumerate([
        "• арифметика складна: вирівняти",
        "   порядки, нормалізувати, округлити",
        "• без апаратного FPU — емуляція",
        "   програмою → ПОВІЛЬНО (десятки тактів)",
        "• ESP32 має FPU (одинарна точність);",
        "   дрібні 8-біт МК — ні",
        "• на МК часто ШВИДШЕ й точніше —",
        "   фіксована кома (§17.5)"]):
        s += text(488, 138 + i * 20, t, 10.6, INK, "start")
    s += text(W / 2, 322, "Правило для МК: float — для зручності й діапазону; фіксована кома — для швидкості, точності й контролю.",
              11.5, INK, "middle", "bold")
    save("fig-17-6-5-special.svg", s)


# ═════════════ §17.6i — історія: Кехен і IEEE 754 ══════════════════════════
def _machine(x, y, name, fmt, ans, col):
    out = rect(x, y, 130, 86, "#fafafa", INK, 1.8, 8)
    out += text(x + 65, y + 22, name, 12, INK, "middle", "bold")
    out += text(x + 65, y + 42, fmt, 9.5, GREY, "middle")
    out += text(x + 65, y + 66, ans, 12, col, "middle", "bold")
    return out


# ── Рис. 17.6i.1 — до й після стандарту ────────────────────────────────────
def fig17_6i_chaos():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "До й після IEEE 754: від хаосу форматів до спільного стандарту", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "до 1985-го кожен виробник робив плаваючу кому по-своєму — та сама програма давала РІЗНІ числа",
              11.5, GREY, "middle", style="italic")
    s += text(220, 92, "ДО: Вавилон форматів", 13, RED, "middle", "bold")
    s += text(220, 110, "(та сама програма →)", 10, GREY, "middle", style="italic")
    s += _machine(70, 124, "IBM", "16-кова основа", "= 3.1399", RED)
    s += _machine(70, 224, "DEC VAX", "свій формат", "= 3.1416", RED)
    s += _machine(290, 124, "Cray", "інше округлення", "= 3.14001", RED)
    s += _machine(290, 224, "CDC", "60-біт слова", "= 3.1420", RED)
    s += text(220, 332, "різні відповіді → нікому не вірити", 11, RED, "middle", "bold")
    s += arrow(440, 230, 510, 230, INK, 2.4)
    s += text(475, 218, "754", 11, GREEN, "middle", "bold")
    s += text(700, 92, "ПІСЛЯ: один стандарт", 13, GREEN, "middle", "bold")
    s += _machine(560, 124, "Intel", "IEEE 754", "= 3.14159", GREEN)
    s += _machine(710, 124, "ARM", "IEEE 754", "= 3.14159", GREEN)
    s += _machine(560, 224, "ESP32", "IEEE 754", "= 3.14159", GREEN)
    s += _machine(710, 224, "ПК", "IEEE 754", "= 3.14159", GREEN)
    s += text(700, 332, "формат → базові операції біт-у-біт", 11, GREEN, "middle", "bold")
    s += text(W / 2, 372, "IEEE 754 (1985) зробив плаваючу кому ПЕРЕДБАЧУВАНОЮ й ПЕРЕНОСНОЮ — і лише тому їй узагалі можна довіряти.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 394, "Пастки §17.6 нікуди не зникли — та принаймні стали однаковими й відтворюваними на будь-якій машині.",
              11, GREY, "middle", style="italic")
    save("fig-17-6i-1-chaos.svg", s)


# ── Рис. 17.6i.2 — що навів лад ────────────────────────────────────────────
def fig17_6i_fixed():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Що саме стандартизував IEEE 754", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "формати, округлення, особливі значення й залізну гарантію коректного результату",
              12, GREY, "middle", style="italic")
    items = [
        ("Формати", "одинарна (32) і подвійна (64) точність — однакові скрізь"),
        ("Коректне округлення", "результат +−×÷ і √ — це ТОЧНО округлене істинне значення"),
        ("Округлення «до парного»", "round-to-nearest-even за замовчуванням (без систематичного зсуву)"),
        ("Особливі значення", "±∞, NaN, ±0 — означені однозначно"),
        ("Поступове зникання", "денормалі: біля нуля числа «згасають» плавно, а не падають у 0"),
        ("Винятки/прапорці", "ділення на 0, переповнення, неточність — сигналізуються"),
    ]
    for i, (name, d) in enumerate(items):
        y = 96 + i * 40
        s += rect(70, y, W - 140, 34, "#f6f8f6" if i % 2 == 0 else "#ffffff", GREY, 1, 6)
        s += text(90, y + 22, name, 12.5, GREEN, "start", "bold")
        s += text(310, y + 22, d, 11.5, INK, "start")
    s += text(W / 2, 348, "Найреволюційніша — «коректне округлення»: воно зробило результат float ОДНОЗНАЧНИМ, а не «приблизним як вийде».",
              11, GREY, "middle", style="italic")
    save("fig-17-6i-2-fixed.svg", s)


# ── Рис. 17.6i.3 — підсумовування Кехена ───────────────────────────────────
def fig17_6i_kahan():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Спадок Кехена: компенсоване підсумовування проти втрати дрібних", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "через відносну точність (§17.6) наївна сума «губить» малі доданки; Кехен навчив повертати втрачене",
              11.5, GREY, "middle", style="italic")
    s += rect(60, 84, 380, 220, "none", RED, 1.7, 10)
    s += text(250, 110, "Наївна сума", 12.5, RED, "middle", "bold")
    s += text(80, 138, "sum = 0", 12, INK, "start", "bold")
    s += text(80, 160, "for x: sum += x", 12, INK, "start", "bold")
    s += text(80, 192, "додаючи дрібне до великого,", 11, GREY, "start")
    s += text(80, 210, "молодші біти «зрізаються» —", 11, GREY, "start")
    s += text(80, 228, "і губляться НАЗАВЖДИ", 11, RED, "start", "bold")
    s += text(80, 262, "сумуючи мільйон чисел,", 11, GREY, "start")
    s += text(80, 280, "похибка накопичується помітно", 11, GREY, "start")
    s += rect(470, 84, 360, 220, "none", GREEN, 1.7, 10)
    s += text(650, 110, "Сума Кехена (компенсована)", 11.5, GREEN, "middle", "bold")
    s += text(490, 138, "тримаємо «загублене» c:", 11.5, INK, "start", "bold")
    s += text(490, 162, "y = x − c", 12, INK, "start")
    s += text(490, 182, "t = sum + y", 12, INK, "start")
    s += text(490, 202, "c = (t − sum) − y   ← ловить", 12, GREEN, "start", "bold")
    s += text(490, 220, "      зрізані біти", 11, GREEN, "start")
    s += text(490, 240, "sum = t", 12, INK, "start")
    s += text(490, 272, "наступного кроку c повертає", 11, GREY, "start")
    s += text(490, 290, "втрачене → похибка ~ стала", 11, GREEN, "start", "bold")
    s += text(W / 2, 332, "Той самий Кехен, що творив IEEE 754, дав і цей прийом — щоб дрібниці не губилися в сумах.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 354, "Це пряме лікування «пастки 2» з §17.6: компенсація відновлює те, що відносна точність відкидає.",
              11, GREY, "middle", style="italic")
    save("fig-17-6i-3-kahan.svg", s)


# ═══════════ §17.7 — Біти, байти, слова й порядок байтів (endianness) ═══════
_TINT = {RED: "#fdf4f4", BLUE: "#f3f5fd", GREEN: "#eef7ee", AMBER: "#fbf6ea"}


def _memcell(x, y, addr, val, col, w=92, h=52):
    out = rect(x, y, w, h, "#ffffff", INK, 1.6, 6)
    out += rect(x + 5, y + 5, w - 10, h - 10, _TINT[col], col, 1.6, 4)
    out += text(x + w / 2, y + h / 2 + 6, val, 16, col, "middle", "bold")
    out += text(x + w / 2, y - 8, addr, 11, GREY, "middle")
    return out


def _egg(cx, cy, col, big=True):
    out = (f'<ellipse cx="{cx}" cy="{cy}" rx="34" ry="44" '
           f'fill="#fffdf5" stroke="{col}" stroke-width="2.4"/>\n')
    if big:  # тріщина на тупому (нижньому) кінці
        out += polyline([(cx - 16, cy + 38), (cx - 6, cy + 30), (cx + 2, cy + 40),
                         (cx + 12, cy + 31), (cx + 18, cy + 39)], col, 2)
    else:    # тріщина на гострому (верхньому) кінці
        out += polyline([(cx - 14, cy - 36), (cx - 5, cy - 44), (cx + 3, cy - 35),
                         (cx + 11, cy - 44), (cx + 16, cy - 36)], col, 2)
    return out


# ── Рис. 17.7.1 — сходинки групування: біт → півбайт → байт → слово ─────────
def fig177_hierarchy():
    W, H = 900, 482
    s = header(W, H)
    s += text(W / 2, 34, "Сходинки групування: біт → півбайт → байт → слово", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "біти збираються в усе більші «порції»: найменша — біт, робоча — байт, найбільша (машинна) — слово",
              11.5, GREY, "middle", style="italic")
    # біт
    s += text(60, 108, "біт (bit)", 14, INK, "start", "bold")
    s += text(60, 126, "1 розряд", 10.5, GREY, "start")
    s += _bitbox(250, 88, 1, 46, 46)
    s += text(316, 106, "одне з двох значень: 0 або 1", 12, INK, "start", "bold")
    s += text(316, 126, "найменша одиниця інформації (біт, Шеннон — Розділ 14)", 10.5, GREY, "start")
    # півбайт
    s += text(60, 190, "півбайт (nibble)", 13.5, INK, "start", "bold")
    s += text(60, 208, "4 біти", 10.5, GREY, "start")
    for i, b in enumerate("1010"):
        s += _bitbox(250 + i * 50, 168, int(b), 46, 46)
    s += text(466, 188, "= 1 hex-цифра (§17.2)", 12, GREEN, "start", "bold")
    s += text(466, 208, "16 значень · 0…F", 10.5, GREY, "start")
    # байт
    s += text(60, 286, "байт (byte)", 13.5, INK, "start", "bold")
    s += text(60, 304, "8 бітів", 10.5, GREY, "start")
    bx = 250
    for i, b in enumerate("10110110"):
        s += _bitbox(bx + i * 50, 258, int(b), 46, 46)
    s += text(bx + 23, 246, "MSB", 10, "#9a7322", "middle", "bold")
    s += text(bx + 23, 322, "старший", 9.5, GREY, "middle")
    s += text(bx + 7 * 50 + 23, 246, "LSB", 10, "#9a7322", "middle", "bold")
    s += text(bx + 7 * 50 + 23, 322, "молодший", 9.5, GREY, "middle")
    s += text(bx + 8 * 50 + 12, 278, "256 значень = 2 hex-цифри", 12, GREEN, "start", "bold")
    s += text(bx + 8 * 50 + 12, 298, "стандартна «порція» пам'яті", 10.5, GREY, "start")
    # слово
    s += text(60, 392, "слово (word)", 13.5, INK, "start", "bold")
    s += text(60, 410, "машинне", 10.5, GREY, "start")
    for j in range(4):
        gx = 250 + j * 100
        s += rect(gx, 367, 92, 46, "#eef4ff", INK, 1.8, 6)
        s += text(gx + 46, 395, "байт", 11, INK, "middle", "bold")
    s += text(662, 384, "16 / 32 / 64 біти", 12, GREEN, "start", "bold")
    s += text(662, 404, "залежить від машини (нижче)", 10.5, GREY, "start")
    s += text(W / 2, 456, "Кожна сходинка — просто більше бітів разом. Біт і байт — сталі; «слово» — стільки, скільки машина бере за раз.",
              11.5, INK, "middle", "bold")
    save("fig-17-7-1-hierarchy.svg", s)


# ── Рис. 17.7.2 — розмір слова: 8/16/32/64 біти ────────────────────────────
def fig177_wordsize():
    W, H = 900, 466
    s = header(W, H)
    s += text(W / 2, 34, "Розмір слова: 8, 16, 32, 64 біти — скільки машина бере за раз", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "«N-бітний процесор» — це ширина його регістрів і шини; вона ж задає, які числа влазять у слово (2ᴺ, §17.1)",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("8 біт", 1, "0…255", "AVR (Arduino Uno), 8051", RED),
        ("16 біт", 2, "0…65 535", "8086, MSP430", AMBER),
        ("32 біти", 4, "0…~4.29 млрд", "ARM Cortex-M, ESP32", GREEN),
        ("64 біти", 8, "0…~1.8·10¹⁹", "x86-64, ARM64 (ПК, телефон)", BLUE),
    ]
    y0, step = 92, 74
    for r, (name, nbytes, rng, mach, col) in enumerate(rows):
        y = y0 + r * step
        s += text(128, y + 28, name, 14, col, "end", "bold")
        for k in range(nbytes):
            s += rect(150 + k * 40, y + 8, 36, 40, _TINT[col], col, 1.8, 5)
        s += text(150 + 8 * 40 + 16, y + 22, f"беззнаковий діапазон: {rng}", 12.5, INK, "start", "bold")
        s += text(150 + 8 * 40 + 16, y + 42, f"приклад: {mach}", 10.5, GREY, "start")
    s += text(150, y0 + 4 * step - 8, "(кожен квадрат — байт; ширше слово = більше байтів за раз = більші числа)",
              10.5, GREY, "start", style="italic")
    s += rect(60, 422, W - 120, 34, "#fff8e8", AMBER, 1.4, 8)
    s += text(W / 2, 444, "Увага: у деяких системах (Windows API) «word» жорстко = 16 біт, dword = 32, qword = 64 — незалежно від машини.",
              11, INK, "middle", "bold")
    save("fig-17-7-2-wordsize.svg", s)


# ── Рис. 17.7.3 — порядок байтів: big-endian vs little-endian ──────────────
def fig177_endianness():
    W, H = 900, 500
    s = header(W, H)
    s += text(W / 2, 34, "Порядок байтів (endianness): у якій послідовності байти лежать у пам'яті", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "одне 32-бітне число — це чотири байти; та в якому ПОРЯДКУ покласти їх за зростанням адрес? Дві школи",
              11.5, GREY, "middle", style="italic")
    # число → 4 кольорові байти (колір — щоб відстежувати кожен у пам'яті)
    chips = [("0x12", RED), ("0x34", AMBER), ("0x56", GREEN), ("0x78", BLUE)]
    s += text(238, 118, "число", 13, INK, "end", "bold")
    s += text(238, 138, "0x12345678", 14, INK, "end", "bold")
    bx = 258
    for i, (v, col) in enumerate(chips):
        x = bx + i * 120
        s += rect(x, 92, 104, 46, _TINT[col], col, 2, 6)
        s += text(x + 52, 122, v, 16, col, "middle", "bold")
    s += text(bx + 52, 162, "старший байт (MSB)", 10, GREY, "middle")
    s += text(bx + 3 * 120 + 52, 162, "молодший байт (LSB)", 10, GREY, "middle")
    # big-endian
    s += text(150, 232, "BIG-ENDIAN", 14, INK, "start", "bold")
    s += text(150, 252, "старший — першим", 10.5, GREY, "start")
    be = [("0x00", "0x12", RED), ("0x01", "0x34", AMBER), ("0x02", "0x56", GREEN), ("0x03", "0x78", BLUE)]
    for i, (a, v, col) in enumerate(be):
        s += _memcell(360 + i * 120, 212, a, v, col)
    # напрямок адрес
    s += arrow(362, 300, 812, 300, GREY, 1.6)
    s += text(360, 292, "адреса →", 10.5, GREY, "start", "bold")
    # little-endian
    s += text(150, 352, "LITTLE-ENDIAN", 14, INK, "start", "bold")
    s += text(150, 372, "молодший — першим", 10.5, GREY, "start")
    le = [("0x00", "0x78", BLUE), ("0x01", "0x56", GREEN), ("0x02", "0x34", AMBER), ("0x03", "0x12", RED)]
    for i, (a, v, col) in enumerate(le):
        s += _memcell(360 + i * 120, 332, a, v, col)
    s += rect(60, 414, W - 120, 78, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 438, "Той самий колір — той самий байт: у big-endian 0x12 лежить за адресою 0x00, у little-endian — за 0x03. Порядок дзеркальний.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 460, "LITTLE-ENDIAN: x86, ARM (звичайно), ESP32, RISC-V.   BIG-ENDIAN: мережа (network byte order), Motorola 68k, PowerPC.",
              11, GREY, "middle")
    s += text(W / 2, 480, "Мнемоніка: little-endian кладе «маленький кінець» (молодший байт) за найменшою адресою.", 10.5, GREY, "middle", style="italic")
    save("fig-17-7-3-endianness.svg", s)


# ── Рис. 17.7.4 — «свята війна»: Свіфт, Коен і практичний укус ─────────────
def fig177_holywar():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Звідки назва й чому це «свята війна»: Ліліпутія, Свіфт і Коен", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "обидва порядки однаково правильні — суперечка про них така ж «принципова», як з якого кінця розбивати яйце",
              11.5, GREY, "middle", style="italic")
    # ліворуч — Свіфт і яйця
    s += rect(60, 84, 360, 252, "#fafafa", INK, 1.6, 10)
    s += text(240, 110, "«Мандри Гуллівера» (Свіфт, 1726)", 12.5, INK, "middle", "bold")
    s += _egg(150, 198, RED, big=True)
    s += _egg(330, 198, BLUE, big=False)
    s += text(150, 268, "тупоконечники", 11.5, RED, "middle", "bold")
    s += text(150, 284, "(б'ють з тупого кінця)", 9.5, GREY, "middle")
    s += text(330, 268, "гостроконечники", 11.5, BLUE, "middle", "bold")
    s += text(330, 284, "(б'ють з гострого кінця)", 9.5, GREY, "middle")
    s += text(240, 314, "Ліліпути воювали, з якого кінця бити яйце", 10.5, INK, "middle", style="italic")
    # праворуч — Коен
    s += rect(440, 84, 400, 252, "#f4f7f4", GREEN, 1.6, 10)
    s += text(640, 110, "Денні Коен, 1980", 12.5, GREEN, "middle", "bold")
    s += text(640, 132, "«On Holy Wars and a Plea for Peace»", 11, INK, "middle", style="italic")
    for i, t in enumerate([
        "Коен узяв образ Свіфта й охрестив два порядки",
        "байтів: big-endian і little-endian.",
        "",
        "Його теза: жоден не «кращий» — головне",
        "ДОМОВИТИСЯ, інакше машини не зрозуміють",
        "одна одну. Це й була його «мольба про мир».",
    ]):
        s += text(460, 160 + i * 22, t, 11, INK, "start")
    s += text(W / 2, 364, "Практичний укус: на little-endian машині число 0x12345678 у hex-дампі пам'яті виглядає як «78 56 34 12».",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 386, "Новачки лякаються «перевернутих» байтів — а це просто little-endian показує молодший байт першим.",
              11, GREY, "middle", style="italic")
    s += rect(60, 410, W - 120, 48, "#fff8e8", AMBER, 1.4, 10)
    s += text(W / 2, 431, "Усередині однієї машини порядок байтів НЕВИДИМИЙ — він кусає лише на МЕЖІ: обмін по мережі, файли, давачі.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 449, "Тому й «свята війна»: суперечка пристрасна, а по суті — лише угода, якого кінця триматися.", 10.5, GREY, "middle", style="italic")
    save("fig-17-7-4-holy-war.svg", s)


# ── Рис. 17.7.5 — endianness на практиці: коли кусає і як жити ──────────────
def fig177_practice():
    W, H = 900, 442
    s = header(W, H)
    s += text(W / 2, 34, "Порядок байтів на практиці: коли кусає і як із ним жити", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ендіанність важлива лише там, де байти перетинають межу машини — у протоколах, файлах і давачах",
              11.5, GREY, "middle", style="italic")
    s += rect(60, 80, 380, 300, "#fdf6f6", RED, 1.6, 10)
    s += text(250, 106, "Коли кусає", 14, RED, "middle", "bold")
    for i, (t, sub) in enumerate([
        ("Читаєш багатобайтове значення", "побайтно: файл, пакет, регістр давача"),
        ("Обмін між машинами", "різної ендіанності — байти переставляться"),
        ("Hex-дамп «задом наперед»", "на little-endian: 0x1234 → «34 12»"),
        ("Невідповідність у протоколі", "відправник BE, отримувач LE → сміття"),
    ]):
        y = 134 + i * 58
        s += text(78, y, "✘ " + t, 12, INK, "start", "bold")
        s += text(96, y + 18, sub, 10.5, GREY, "start")
    s += rect(460, 80, 380, 300, "#f4f7f4", GREEN, 1.6, 10)
    s += text(650, 106, "Як із цим жити", 14, GREEN, "middle", "bold")
    for i, (t, sub) in enumerate([
        ("Мережевий порядок = big-endian", "htons/htonl/ntohs/ntohl переставляють байти"),
        ("Даташит каже порядок", "MSB-first чи LSB-first — читай і дотримуйся"),
        ("Складай число явно з байтів", "v = b0 | (b1<<8) | (b2<<16) | (b3<<24)"),
        ("Усередині машини — байдуже", "ендіанність невидима, поки байти «вдома»"),
    ]):
        y = 134 + i * 58
        s += text(478, y, "✔ " + t, 12, INK, "start", "bold")
        s += text(496, y + 18, sub, 10.5, GREY, "start")
    s += text(W / 2, 410, "Золоте правило: складай багатобайтові значення явними зсувами — і код працюватиме на будь-якій машині.",
              11.5, INK, "middle", "bold")
    save("fig-17-7-5-practice.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_leibniz_idea()
    fig_iching()
    fig_convergence()
    # §17.1
    fig171_why_two()
    fig171_cost()
    fig171_capacity()
    fig171_byte()
    # §17.2
    fig172_positional()
    fig172_dec_to_bin()
    fig172_readability()
    fig172_hex_digits()
    fig172_grouping()
    # §17.3
    fig173_problem()
    fig173_twoscomp()
    fig173_circle()
    fig173_subtraction()
    fig173_range()
    # §17.4
    fig174_unsigned()
    fig174_signed()
    fig174_detection()
    fig174_disasters()
    fig174_avoiding()
    # §17.5
    fig175_point()
    fig175_scaling()
    fig175_qnotation()
    fig175_arithmetic()
    fig175_proscons()
    # §17.6
    fig176_scientific()
    fig176_format()
    fig176_range()
    fig176_tricky()
    fig176_special()
    # §17.6i — історія IEEE 754
    fig17_6i_chaos()
    fig17_6i_fixed()
    fig17_6i_kahan()
    # §17.7
    fig177_hierarchy()
    fig177_wordsize()
    fig177_endianness()
    fig177_holywar()
    fig177_practice()
    print("ch17 figures done.")
