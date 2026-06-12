# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 10.3 — «USB-живлення і розумна зарядка» (Модуль 10).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи: «Рис. 10.3.T.k»;
для історії до розділу — тема 0 (Рис. 10.3.0.k). Хелпери — копія з §10.1/10.2.

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
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
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
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


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── Рис. 10.3.0.1 — таймлайн стандартизації зарядки ──────────────────────────
def fig_timeline():
    W, H = 940, 880
    s = header(W, H)
    s += text(W / 2, 40, "Один дріт замість зоопарку: колективна історія стандартизації", 20,
              INK, "middle", "bold")
    s += text(W / 2, 62, "індустрія, консорціуми й регулятори — а не один герой — дотиснули світ до спільного роз'єму",
              12.5, GREY, "middle", style="italic")
    spine = 248
    top, bot = 96, H - 60
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("2007", "USB Battery Charging 1.0", "Дозволено брати з USB більше за 500 мА → можлива швидша зарядка", False, False),
        ("2009", "GSMA UCS · OMTP", "Індустрія узгоджує спільний зарядний на microUSB (Universal Charging Solution)", True, False),
        ("черв. 2009", "Меморандум ЄС (MoU)", "14 виробників (Apple, Nokia, Samsung, LG…) ДОБРОВІЛЬНО на micro-USB-B; під тиском Єврокомісії", True, False),
        ("2010–11", "IEC 62684", "Спільний зарядний стає міжнародним стандартом (IEC + USB-IF)", False, False),
        ("2014", "USB-IF: USB-C", "Один симетричний роз'єм на все: дані, відео, живлення — і реверсивний", True, False),
        ("2022", "Директива ЄС 2022/2380", "USB-C тепер ОБОВ'ЯЗКОВИЙ, не добровільний (поправка до RED 2014/53)", True, True),
        ("2023", "Apple → USB-C (iPhone 15)", "Останнього холдаута дотиснули законом; представники Apple визнали: «комплаєнс»", False, True),
        ("2024 · 2026", "Дедлайни ЄС", "Телефони/планшети — груд. 2024; ноутбуки — квіт. 2026 (PD до 240 Вт)", False, False),
    ]
    n = len(nodes)
    for i, (yr, who, what, hot, force) in enumerate(nodes):
        y = top + 24 + (bot - top - 48) * i / (n - 1)
        if force:
            s += circle(spine, y, 11, "#fff", RED, 3.2)
            s += circle(spine, y, 5, RED, RED, 0)
        elif hot:
            s += circle(spine, y, 8.5, "#fff", GREEN, 3)
        else:
            s += circle(spine, y, 7, "#fff", INK, 2.4)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 4, who, 15, (RED if force else (GREEN if hot else INK)), "start", "bold")
        s += text(spine + 26, y + 15, what, 12, INK, "start", style="italic")
    ly = bot + 26
    s += circle(spine - 150, ly - 4, 8.5, "#fff", GREEN, 3)
    s += text(spine - 134, ly, "крок індустрії/консорціуму", 12, INK, "start")
    s += circle(spine + 110, ly - 4, 11, "#fff", RED, 3.2)
    s += circle(spine + 110, ly - 4, 5, RED, RED, 0)
    s += text(spine + 128, ly, "коли довелося ПРИМУСИТИ законом", 12, INK, "start")
    s += text(W / 2, H - 16, "Жодного «винахідника спільної зарядки» — це 15-річна спільна робота консорціумів, стандартизаторів і регуляторів",
              12.5, RED, "middle", style="italic")
    save("fig-10-0-1-timeline.svg", s)


# ── Рис. 10.3.0.2 — зоопарк роз'ємів → один ──────────────────────────────────
def fig_zoo_to_one():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 34, "Від «зоопарку» роз'ємів до одного USB-C", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "до 2009-го майже кожен виробник мав свій штекер — нова модель означала новий зарядний на смітник",
              12, GREY, "middle", style="italic")
    # ліворуч — різні штекери
    olds = [
        ("циліндр (barrel)", 110),
        ("mini-USB", 165),
        ("Nokia тонкий", 220),
        ("30-pin (Apple)", 275),
        ("фірмові інших", 330),
    ]
    s += text(170, 92, "БУЛО: десятки несумісних", 12.5, RED, "middle", "bold")
    for name, y in olds:
        s += rect(70, y - 14, 28, 28, "#fbe9e7", RED, 1.8, 4)
        s += rect(80, y - 5, 12, 10, RED, RED, 0)
        s += text(110, y + 4, name, 12, INK, "start")
        s += arrow(300, y, 360, 222, GREY, 1.4)
    # центр — тиск
    s += rect(360, 150, 200, 150, "#fff7e6", AMBER, 2, 12)
    s += text(460, 178, "ТИСК НА ОДНЕ", 12.5, AMBER, "middle", "bold")
    for i, t in enumerate(["GSMA / OMTP (індустрія)", "Меморандум + директива ЄС", "USB-IF (стандарт USB-C)", "екологія: гори e-сміття"]):
        s += text(372, 204 + i * 24, "• " + t, 10.5, INK, "start")
    s += arrow(560, 225, 640, 225, GREEN, 2.6)
    # праворуч — USB-C
    s += rect(660, 180, 200, 90, "#eef8ef", GREEN, 2.4, 12)
    s += text(760, 210, "СТАЛО: USB-C", 14, GREEN, "middle", "bold")
    s += rect(735, 230, 50, 18, "none", GREEN, 2, 9)
    s += rect(742, 235, 36, 8, GREEN, GREEN, 0)
    s += text(760, 262, "один роз'єм на все", 10.5, INK, "middle")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Кінцевий «один дріт» — не чийсь винахід, а результат тиску з усіх боків: індустрії, стандартизаторів,", 11, INK, "middle")
    s += text(W / 2, H - 8, "законодавців і екології. Навіть найбільший холдаут (Apple) поступився лише під обов'язковою нормою.", 11, INK, "middle")
    save("fig-10-0-2-zoo.svg", s)


# ── Рис. 10.3.1.1 — драбина потужності USB ───────────────────────────────────
def fig_power_ladder():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "Драбина живлення USB: від 2.5 Вт до 240 Вт", 19, INK, "middle", "bold")
    steps = [
        ("USB 2.0", "5 В · 0.5 А", "2.5 Вт", BLUE),
        ("USB 3.0", "5 В · 0.9 А", "4.5 Вт", BLUE),
        ("BC 1.2", "5 В · 1.5 А", "7.5 Вт", AMBER),
        ("USB-C базово", "5 В · до 3 А (CC)", "15 Вт", GREEN),
        ("USB PD (SPR)", "до 20 В · 5 А", "100 Вт", RED),
        ("USB PD EPR", "до 48 В · 5 А", "240 Вт", "#9b59b6"),
    ]
    n = len(steps)
    bx = 70
    bw = (W - 140) / n
    base = 350
    for i, (name, vi, p, c) in enumerate(steps):
        h = 40 + i * 48
        x = bx + i * bw
        s += rect(x + 8, base - h, bw - 16, h, "#ffffff", c, 2, 6)
        s += f'<rect x="{x+8:.0f}" y="{base-h:.0f}" width="{bw-16:.0f}" height="{h:.0f}" rx="6" fill="{c}" fill-opacity="0.14"/>\n'
        s += text(x + bw / 2, base - h - 26, p, 13, c, "middle", "bold")
        s += text(x + bw / 2, base - h - 10, name, 10.5, INK, "middle", "bold")
        s += text(x + bw / 2, base + 18, vi, 9.5, GREY, "middle")
    s += line(bx, base, W - 70, base, INK, 1.6)
    s += arrow(bx, base + 36, W - 90, base + 36, GREY, 1.6)
    s += text(W / 2, base + 52, "той самий роз'єм — на два порядки більша потужність, бо змінилося не залізо, а ДОМОВЛЕНІСТЬ", 11, INK, "middle")
    save("fig-10-1-1-ladder.svg", s)


# ── Рис. 10.3.1.2 — покоління роз'ємів ───────────────────────────────────────
def fig_connectors():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Покоління роз'ємів USB і їхні межі", 19, INK, "middle", "bold")
    conns = [
        ("Type-A", "хост (ПК, зарядка)", "до 0.9 А (3.0)", BLUE, 60),
        ("Type-B", "великі пристрої", "як 2.0/3.0", BLUE, 230),
        ("mini-USB", "старі камери/HDD", "застарів", GREY, 400),
        ("micro-USB", "телефони 2009–17", "до 1.5 А (BC)", AMBER, 570),
        ("Type-C", "усе сучасне", "до 5 А + PD", GREEN, 740),
    ]
    for name, role, lim, c, x in conns:
        s += rect(x, 90, 130, 56, "#ffffff", c, 2, 8)
        # стилізований штекер
        if name == "Type-C":
            s += rect(x + 40, 108, 50, 20, "none", c, 2, 10)
            s += rect(x + 48, 114, 34, 8, c, c, 0)
        else:
            s += rect(x + 48, 108, 34, 20, "none", c, 2, 3)
            s += rect(x + 54, 112, 22, 12, c, c, 0)
        s += text(x + 65, 170, name, 12.5, c, "middle", "bold")
        s += text(x + 65, 188, role, 9.5, INK, "middle")
        s += text(x + 65, 204, lim, 9.5, GREY, "middle")
    s += text(W / 2, 250, "Усі, крім Type-C, — однобічні (є «правильний» бік) і обмежені за струмом.", 12, INK, "middle")
    s += rect(70, H - 60, W - 140, 44, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 42, "Type-C — реверсивний, тримає до 5 А і несе сучасні домовленості (CC, PD). Решта — історія:", 11, INK, "middle")
    s += text(W / 2, H - 26, "Type-A ще живе як хост-роз'єм і зарядка, micro-USB доживає в дешевих пристроях, mini й Type-B — майже зникли.", 11, INK, "middle")
    save("fig-10-1-2-connectors.svg", s)


# ── Рис. 10.3.1.3 — USB-C базово: рівні через CC ─────────────────────────────
def fig_usbc_base():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "USB-C без PD: 5 В і три рівні струму через резистори CC", 17.5,
              INK, "middle", "bold")
    levels = [
        ("стандарт", "5 В · до 0.9/1.5 А", "Rp за замовчуванням", GREY, 150),
        ("1.5 А", "5 В · 1.5 А", "середній Rp", AMBER, 290),
        ("3.0 А", "5 В · 3 А = 15 Вт", "сильний Rp", GREEN, 430),
    ]
    for name, vi, how, c, y in levels:
        s += rect(120, y, 260, 44, "#ffffff", c, 2, 8)
        s += text(250, y + 20, vi, 13, c, "middle", "bold")
        s += text(250, y + 38, name + " режим", 10, GREY, "middle")
        s += arrow(390, y + 22, 440, y + 22, INK, 1.8)
        s += text(450, y + 26, "джерело каже резистором Rp →", 10.5, INK, "start")
    s += rect(450, 130, 360, 220, "#f6f6f6", GREY, 1.4, 10)
    s += text(630, 156, "Як це працює (деталі — 10.3.2):", 11.5, INK, "middle", "bold")
    for i, t in enumerate([
        "• джерело вішає на лінію CC резистор Rp",
        "• пристрій — резистор Rd",
        "• за рівнем напруги на CC пристрій",
        "  читає, скільки ампер дозволено",
        "• усе БЕЗ жодного протоколу й чипа —",
        "  лише два резистори",
        "• більше за 5 В × 3 А? → потрібен PD",
    ]):
        s += text(468, 184 + i * 23, t, 10.5, INK, "start")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Базовий USB-C дає до 15 Вт зовсім без розуму — самими резисторами CC. Більше — лише через переговори PD", 10.5, INK, "middle")
    save("fig-10-1-3-usbc-base.svg", s)


# ── Рис. 10.3.1.4 — драбина напруг PD ────────────────────────────────────────
def fig_pd_ladder():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 32, "USB PD: домовитися про вищу напругу", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "пристрій просить профіль, джерело дає — і напруга піднімається на вимогу", 12, GREY, "middle", style="italic")
    fixed = [("5 В", 110), ("9 В", 180), ("15 В", 250), ("20 В", 330)]
    ox, oy = 110, 330
    for v, p in fixed:
        x = ox + p
        s += rect(x, oy - (40 + p // 4), 56, (40 + p // 4), "#eef3fb", BLUE, 2, 5)
        s += text(x + 28, oy - (40 + p // 4) - 8, v, 12, BLUE, "middle", "bold")
    s += text(ox + 230, 100, "фіксовані профілі (SPR)", 11, BLUE, "middle", "bold")
    # PPS
    s += rect(540, 150, 150, 180, "#eef8ef", GREEN, 2, 8)
    s += text(615, 174, "PPS", 13, GREEN, "middle", "bold")
    s += text(615, 194, "програмована", 9.5, INK, "middle")
    s += text(615, 208, "напруга", 9.5, INK, "middle")
    s += poly([(560, 310), (590, 250), (620, 290), (650, 220), (675, 280)], GREEN, 2.4)
    s += text(615, 326, "плавно, кроком ~20 мВ", 9, GREY, "middle")
    # EPR
    s += rect(710, 120, 150, 210, "#f3eafa", "#9b59b6", 2, 8)
    s += text(785, 144, "EPR", 13, "#9b59b6", "middle", "bold")
    for i, t in enumerate(["28 В", "36 В", "48 В"]):
        s += rect(745, 164 + i * 40, 80, 30, "#fff", "#9b59b6", 1.8, 5)
        s += text(785, 184 + i * 40, t, 11.5, "#9b59b6", "middle", "bold")
    s += text(785, 320, "до 240 Вт", 11, "#9b59b6", "middle", "bold")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Фіксовані 5/9/15/20 В, програмована PPS і високовольтна EPR (до 48 В) — усе по тому самому дроту, через протокол PD", 10.5, INK, "middle")
    save("fig-10-1-4-pd-ladder.svg", s)


# ── Рис. 10.3.1.5 — розв'язка живлення й даних ───────────────────────────────
def fig_decouple():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 32, "Один роз'єм, різні ролі: живлення окремо від даних", 18, INK, "middle", "bold")
    cx = W / 2
    s += rect(cx - 70, 80, 140, 220, "#fbfbf8", INK, 2, 10)
    s += text(cx, 104, "USB-C", 13, INK, "middle", "bold")
    rows = [
        ("CC1/CC2", "переговори про живлення (CC, PD)", AMBER),
        ("VBUS/GND", "власне живлення (5–48 В)", RED),
        ("D+/D−", "дані USB 2.0", BLUE),
        ("TX/RX пари", "швидкі дані, відео (3.x, DisplayPort)", GREEN),
    ]
    for i, (pin, role, c) in enumerate(rows):
        y = 130 + i * 44
        s += circle(cx - 70, y, 5, c, c, 0)
        s += circle(cx + 70, y, 5, c, c, 0)
        s += text(cx, y - 6, pin, 10.5, c, "middle", "bold")
        side = 1 if i % 2 == 0 else -1
        tx = cx + side * 95
        s += text(tx, y + 4, role, 9.5, INK, "start" if side > 0 else "end")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 26, "Живлення домовляється по лінії CC окремо від даних — тому той самий роз'єм возить і 5 мА мишки,", 10.5, INK, "middle")
    s += text(W / 2, H - 12, "і 240 Вт ноутбука, і відео на монітор. Дані й потужність не заважають одне одному.", 10.5, INK, "middle")
    save("fig-10-1-5-decouple.svg", s)


# ── Рис. 10.3.1.6 — «скільки можу взяти?» ────────────────────────────────────
def fig_howmuch():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Скільки можу взяти з цього порту? — карта рішення", 18, INK, "middle", "bold")
    s += rect(370, 60, 160, 40, "#eef3fb", BLUE, 2, 8)
    s += text(450, 85, "бачу USB-порт", 12, BLUE, "middle", "bold")
    branches = [
        ("Старий A/micro?", "→ BC1.2: тип порту по D+/D−\n(до 1.5 А) — тема 10.3.5", AMBER, 90),
        ("Type-C без PD?", "→ резистори CC: 5 В, 1.5/3 А\n(до 15 Вт) — тема 10.3.2", GREEN, 370),
        ("Type-C з PD?", "→ переговори: 9/15/20/48 В\n(до 240 Вт) — теми 10.3.3–4", RED, 650),
    ]
    for q, a, c, x in branches:
        s += arrow(450, 100, x + 70, 150, GREY, 1.6)
        s += rect(x, 150, 220, 50, "#ffffff", c, 2, 8)
        s += text(x + 110, 176, q, 12, c, "middle", "bold")
        for j, ln in enumerate(a.split("\n")):
            s += text(x + 110, 222 + j * 16, ln, 9.5, INK, "middle")
    s += rect(70, H - 44, W - 140, 32, "#fbf7ec", AMBER, 1.5, 8)
    s += text(W / 2, H - 26, "Перш ніж брати струм, пристрій мусить ЗАПИТАТИ, скільки можна, — інакше або недобере, або перевантажить джерело.", 10.5, INK, "middle")
    s += text(W / 2, H - 12, "Три способи спитати (BC1.2 / CC / PD) — три наступні теми розділу. Тут — лише карта, куди дивитись.", 10.5, INK, "middle")
    save("fig-10-1-6-howmuch.svg", s)


def _res(x, y, w, h, label, c=INK):
    out = rect(x, y, w, h, "#ffffff", c, 1.8, 4)
    out += text(x + w / 2, y + h / 2 + 4, label, 10.5, c, "middle", "bold")
    return out


# ── Рис. 10.3.2.1 — CC-дільник Rp/Rd ─────────────────────────────────────────
def fig_cc_divider():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 32, "Лінія CC: дільник Rp/Rd кодує дозволений струм", 18, INK, "middle", "bold")
    # джерело
    s += rect(50, 90, 300, 230, "#fbe9e7", RED, 1.8, 12)
    s += text(200, 114, "ДЖЕРЕЛО (source)", 13, RED, "middle", "bold")
    s += plus(110, 150, 8, RED)
    s += text(110, 134, "Vоп", 11, INK, "middle", "bold")
    s += line(110, 158, 110, 190, INK, 2)
    s += _res(86, 190, 48, 50, "Rp", RED)
    s += line(110, 240, 110, 280, INK, 2)
    s += circle(110, 280, 4, INK, INK, 0)
    s += text(110, 300, "CC", 11, AMBER, "middle", "bold")
    # кабель
    s += line(110, 280, 590, 280, AMBER, 2.6)
    s += text(350, 268, "лінія CC крізь кабель", 10, GREY, "middle", style="italic")
    # пристрій
    s += rect(550, 90, 300, 230, "#eef8ef", GREEN, 1.8, 12)
    s += text(700, 114, "ПРИСТРІЙ (sink)", 13, GREEN, "middle", "bold")
    s += circle(590, 280, 4, INK, INK, 0)
    s += line(590, 280, 590, 240, INK, 2)
    s += _res(566, 190, 48, 50, "Rd", GREEN)
    s += text(640, 215, "5.1 кОм", 10, GREEN, "start", "bold")
    s += line(590, 190, 590, 150, INK, 2)
    s += line(575, 150, 605, 150, INK, 2)
    s += text(700, 175, "пристрій МІРЯЄ напругу на CC", 10.5, INK, "middle")
    s += text(700, 192, "→ читає дозволений струм", 10.5, INK, "middle", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 26, "Vcc = Vоп · Rd/(Rp+Rd). Джерело вибирає Rp → задає напругу; пристрій її міряє й дізнається струм.", 10.5, INK, "middle")
    s += text(W / 2, H - 12, "А ще: Rd каже джерелу «тут пристрій», бо без нього CC висить і джерело тримає живлення вимкненим.", 10.5, INK, "middle")
    save("fig-10-2-1-ccdivider.svg", s)


# ── Рис. 10.3.2.2 — три рівні струму через Rp ────────────────────────────────
def fig_cc_levels():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 32, "Три рівні струму: джерело вибирає Rp", 18, INK, "middle", "bold")
    cols = ["Rp джерела", "напруга на CC (≈)", "дозволено", ""]
    cx = [80, 290, 560]
    s += rect(50, 64, 780, 30, "#eef3fb", BLUE, 1.6, 6)
    for i, c in enumerate(cols[:3]):
        s += text(cx[i] + 12, 84, c, 11.5, BLUE, "start", "bold")
    rows = [
        ("56 кОм", "≈ 0.4 В", "стандарт (0.5/0.9 А)", GREY),
        ("22 кОм", "≈ 0.9 В", "1.5 А", AMBER),
        ("10 кОм", "≈ 1.6 В", "3.0 А = 15 Вт", GREEN),
    ]
    for r, (rp, v, lvl, c) in enumerate(rows):
        y = 100 + r * 56
        s += rect(50, y, 780, 50, "#ffffff" if r % 2 == 0 else "#f6f6f6", FAINT, 1, 0)
        s += _res(cx[0] + 4, y + 9, 70, 32, rp, c)
        s += text(cx[1] + 40, y + 30, v, 12.5, INK, "middle", "bold")
        s += text(cx[2] + 12, y + 30, lvl, 12, c, "start", "bold")
        # стовпчик-індикатор
        bx = 760
        bh = 12 + r * 12
        s += rect(bx, y + 40 - bh, 26, bh, "#fff", c, 1.5, 3)
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "Чим менший Rp, тим вища напруга на CC і тим більший дозволений струм. Точні пороги — у вставці 🔌", 10.5, INK, "middle")
    save("fig-10-2-2-levels.svg", s)


# ── Рис. 10.3.2.3 — визначення ролей ─────────────────────────────────────────
def fig_cc_roles():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 32, "Хто кого живить: роль задає резистор на CC", 18, INK, "middle", "bold")
    cards = [
        ("ДЖЕРЕЛО (DFP)", "вішає Rp (підтяжка)", "дає живлення", RED, 60),
        ("ПРИСТРІЙ (UFP)", "вішає Rd (5.1 кОм)", "бере живлення", GREEN, 330),
        ("ДВОРОЛЬОВИЙ (DRP)", "чергує Rp↔Rd", "хто перший — той і…", AMBER, 600),
    ]
    for title, what, role, c, x in cards:
        s += rect(x, 80, 240, 180, "#ffffff", c, 2, 12)
        s += text(x + 120, 108, title, 12.5, c, "middle", "bold")
        s += text(x + 120, 150, what, 11.5, INK, "middle", "bold")
        s += text(x + 120, 180, role, 11, GREY, "middle")
        if "DRP" in title:
            s += text(x + 120, 210, "домовляються, хто", 10, INK, "middle")
            s += text(x + 120, 226, "стане джерелом", 10, INK, "middle")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 26, "Сам резистор визначає роль: підтяжка Rp = «я джерело», підтяжка вниз Rd = «я пристрій».", 10.5, INK, "middle")
    s += text(W / 2, H - 12, "Дворольовий (ноутбук, павербанк) чергує обидва, поки не вирішить, ким бути в цій парі.", 10.5, INK, "middle")
    save("fig-10-2-3-roles.svg", s)


# ── Рис. 10.3.2.4 — орієнтація й VCONN ───────────────────────────────────────
def fig_cc_orientation():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Два піни CC: який з'єднано — той і каже орієнтацію", 18, INK, "middle", "bold")
    # роз'єм
    s += rect(360, 80, 180, 70, "none", INK, 2, 12)
    s += text(450, 70, "роз'єм Type-C", 10.5, GREY, "middle")
    s += circle(400, 115, 6, AMBER, AMBER, 0)
    s += text(400, 119, "", 1, INK, "middle")
    s += text(400, 100, "CC1", 10, AMBER, "middle", "bold")
    s += circle(500, 115, 6, "none", GREY, 2)
    s += text(500, 100, "CC2", 10, GREY, "middle", "bold")
    # CC1 з'єднано
    s += line(400, 150, 400, 230, AMBER, 2.4)
    s += _res(376, 230, 48, 40, "Rd", GREEN)
    s += text(400, 296, "З'ЄДНАНО → це активна CC", 10, GREEN, "middle", "bold")
    s += text(400, 312, "(пристрій бачить Rp джерела тут)", 9.5, INK, "middle")
    # CC2 → VCONN
    s += line(500, 150, 500, 230, GREY, 2, dash="5,4")
    s += rect(470, 230, 60, 40, "#fff7e6", AMBER, 1.6, 6)
    s += text(500, 254, "VCONN", 10, AMBER, "middle", "bold")
    s += text(500, 296, "не з'єднано напряму →", 9.5, GREY, "middle")
    s += text(500, 310, "стає живленням для кабелю", 9.5, GREY, "middle")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 26, "Роз'єм реверсивний, тож пінів CC два. Через кабель з'єднується ЛИШЕ один — і саме він несе Rp/Rd.", 10.5, INK, "middle")
    s += text(W / 2, H - 12, "За тим, який з двох ожив, система й розуміє, яким боком устромлено штекер — і куди вести дані.", 10.5, INK, "middle")
    save("fig-10-2-4-orientation.svg", s)


# ── Рис. 10.3.2.5 — VCONN живить e-marker кабелю ─────────────────────────────
def fig_cc_emarker():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 32, "Навіщо кабелю чип: VCONN живить e-marker", 18, INK, "middle", "bold")
    # кабель з чипом
    s += rect(120, 120, 640, 90, "#f6f6f6", GREY, 1.8, 14)
    s += text(440, 110, "USB-C кабель", 10.5, GREY, "middle")
    s += line(150, 165, 730, 165, COPP, 3)
    s += rect(400, 145, 80, 44, "#eef3fb", BLUE, 2, 8)
    s += text(440, 164, "e-marker", 10.5, BLUE, "middle", "bold")
    s += text(440, 180, "чип", 9, BLUE, "middle")
    s += line(440, 145, 440, 120, AMBER, 2)
    s += text(560, 132, "живиться від VCONN", 10, AMBER, "middle", "bold")
    s += text(150, 240, "Чип каже системі:", 12, INK, "start", "bold")
    for i, t in enumerate(["• скільки ампер тримає кабель (3 А чи 5 А)", "• довжину / швидкість даних", "• чи активний (зі своєю електронікою)"]):
        s += text(170, 266 + i * 22, t, 11, INK, "start")
    s += rect(520, 235, 320, 90, "#fbe9e7", RED, 1.6, 10)
    s += text(680, 258, "Без e-marker:", 11.5, RED, "middle", "bold")
    s += text(540, 282, "система НЕ дозволить 5 А", 10.5, INK, "start")
    s += text(540, 300, "(припустить безпечні 3 А) — звідси", 10.5, INK, "start")
    s += text(540, 316, "«чому повільно заряджає цим шнуром»", 10.5, INK, "start")
    s += rect(70, H - 26, W - 140, 18, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 13, "Повний струм несуть лише кабелі з e-marker; деталі — у темі 10.3.7", 10, INK, "middle")
    save("fig-10-2-5-emarker.svg", s)


# ── Рис. 10.3.2.6 — мінімальний sink ─────────────────────────────────────────
def fig_minimal_sink():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 32, "Найпростіший USB-C пристрій: два резистори й трохи уваги", 17.5,
              INK, "middle", "bold")
    s += rect(60, 80, 380, 230, "#eef8ef", GREEN, 1.8, 12)
    s += text(250, 106, "Що поставити", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate([
        "1. Rd = 5.1 кОм з КОЖНОГО CC на землю",
        "   (обидва піни — бо роз'єм реверсивний)",
        "2. узяти VBUS (5 В) як живлення",
        "3. (опц.) зчитати напругу на CC,",
        "   щоб знати: 0.9 / 1.5 / 3 А",
        "4. не брати більше, ніж дозволено",
    ]):
        s += text(78, 136 + i * 27, t, 10.5, INK, "start")
    s += rect(470, 80, 370, 230, "#fbe9e7", RED, 1.8, 12)
    s += text(655, 106, "Типові граблі", 12.5, RED, "middle", "bold")
    for i, t in enumerate([
        "• забув Rd → пристрій не бачать,",
        "  VBUS не вмикається",
        "• Rd лише на одному CC → працює",
        "  тільки одним боком штекера",
        "• припустив 3 А, а порт дає 0.9 →",
        "  перевантаження, просадка",
        "• не плутати Rd (5.1к) з іншими",
    ]):
        s += text(488, 136 + i * 25, t, 10.5, INK, "start")
    s += rect(70, H - 26, W - 140, 18, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 13, "Для простого 5-вольтового пристрою це все: Rd на CC — і ти законний USB-C sink", 10.5, INK, "middle")
    save("fig-10-2-6-minimalsink.svg", s)


# ── Рис. 10.3.3.1 — рукостискання PD ─────────────────────────────────────────
def fig_pd_handshake():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Рукостискання PD: меню → запит → згода → нова напруга", 18,
              INK, "middle", "bold")
    sx, dx = 230, 670
    top, bot = 70, 380
    s += rect(sx - 90, top, 180, 34, "#fbe9e7", RED, 2, 8)
    s += text(sx, top + 22, "ДЖЕРЕЛО", 12.5, RED, "middle", "bold")
    s += rect(dx - 90, top, 180, 34, "#eef8ef", GREEN, 2, 8)
    s += text(dx, top + 22, "ПРИСТРІЙ", 12.5, GREEN, "middle", "bold")
    s += line(sx, top + 34, sx, bot, GREY, 1.6, dash="4,4")
    s += line(dx, top + 34, dx, bot, GREY, 1.6, dash="4,4")
    msgs = [
        (130, "під'єднання (резистори CC) → на VBUS лише 5 В", None, AMBER),
        (170, "Source_Capabilities (меню профілів PDO)", "right", RED),
        (210, "Request: «хочу профіль, напр. 20 В / 3 А»", "left", GREEN),
        (250, "Accept", "right", RED),
        (290, "VBUS плавно піднімається до 20 В", None, BLUE),
        (330, "PS_RDY (живлення готове)", "right", RED),
    ]
    for y, t, d, c in msgs:
        if d == "right":
            s += arrow(sx + 6, y, dx - 6, y, c, 2)
            s += text((sx + dx) / 2, y - 6, t, 10.5, c, "middle", "bold")
        elif d == "left":
            s += arrow(dx - 6, y, sx + 6, y, c, 2)
            s += text((sx + dx) / 2, y - 6, t, 10.5, c, "middle", "bold")
        else:
            s += text((sx + dx) / 2, y, t, 10, GREY, "middle", style="italic")
    s += rect(sx - 60, 350, dx - sx + 120, 26, "#eef8ef", GREEN, 1.6, 8)
    s += text((sx + dx) / 2, 367, "КОНТРАКТ активний — і його можна переукласти будь-коли", 11, GREEN, "middle", "bold")
    s += rect(70, H - 30, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 15, "PD — це розмова цифровими повідомленнями по тій самій лінії CC: джерело пропонує меню, пристрій просить, джерело погоджується", 10, INK, "middle")
    save("fig-10-3-1-handshake.svg", s)


# ── Рис. 10.3.3.2 — меню профілів (PDO) ──────────────────────────────────────
def fig_pdos():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 32, "Меню джерела: список профілів (PDO)", 18, INK, "middle", "bold")
    s += rect(120, 64, 480, 300, "#ffffff", INK, 2, 12)
    s += text(360, 90, "Source_Capabilities", 13, INK, "middle", "bold")
    s += line(140, 100, 580, 100, FAINT, 1)
    items = [
        ("Fixed", "5 В · 3 А", "(є завжди — обов'язковий)", BLUE),
        ("Fixed", "9 В · 3 А", "27 Вт", BLUE),
        ("Fixed", "15 В · 3 А", "45 Вт", BLUE),
        ("Fixed", "20 В · 5 А", "100 Вт (SPR-стеля)", BLUE),
        ("APDO", "PPS 3.3–11 В, до 5 А", "програмована напруга", GREEN),
        ("(EPR)", "28/36/48 В", "до 240 Вт — якщо всі готові", "#9b59b6"),
    ]
    for i, (typ, vi, note, c) in enumerate(items):
        y = 122 + i * 38
        s += rect(140, y, 70, 28, "#fff", c, 1.6, 5)
        s += text(175, y + 19, typ, 10, c, "middle", "bold")
        s += text(228, y + 19, vi, 12, INK, "start", "bold")
        s += text(430, y + 19, note, 10, GREY, "start")
    s += text(700, 150, "Пристрій читає меню", 11.5, GREEN, "middle", "bold")
    s += text(700, 170, "й вибирає ОДИН", 11.5, GREEN, "middle")
    s += text(700, 190, "профіль під свою", 11.5, INK, "middle")
    s += text(700, 210, "потребу.", 11.5, INK, "middle")
    s += text(700, 244, "Немає потрібного —", 10.5, GREY, "middle")
    s += text(700, 260, "бере найближчий", 10.5, GREY, "middle")
    s += text(700, 276, "нижчий або 5 В.", 10.5, GREY, "middle")
    s += rect(70, H - 26, W - 140, 18, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 13, "PDO (Power Data Object) — один рядок меню: яка напруга й до якого струму. 5 В є завжди", 10, INK, "middle")
    save("fig-10-3-2-pdos.svg", s)


# ── Рис. 10.3.3.3 — фіксовані профілі проти PPS ──────────────────────────────
def fig_fixed_vs_pps():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Фіксовані сходинки проти програмованої PPS", 18, INK, "middle", "bold")
    # фіксовані
    s += rect(50, 70, 380, 250, "#eef3fb", BLUE, 1.8, 12)
    s += text(240, 96, "Фіксовані профілі", 13, BLUE, "middle", "bold")
    ox, oy = 90, 280
    s += arrow(ox, oy, 400, oy, INK, 1.4)
    s += arrow(ox, oy, ox, 110, INK, 1.4)
    for v, h in [("5", 30), ("9", 60), ("15", 110), ("20", 160)]:
        x = ox + 30 + int(v) * 13
        s += rect(x, oy - h, 30, h, "none", BLUE, 2, 3)
        s += text(x + 15, oy - h - 8, v + " В", 9.5, BLUE, "middle", "bold")
    s += text(240, 304, "лише дискретні щаблі: 5/9/15/20", 10, INK, "middle")
    # PPS
    s += rect(470, 70, 380, 250, "#eef8ef", GREEN, 1.8, 12)
    s += text(660, 96, "PPS (програмована)", 13, GREEN, "middle", "bold")
    ox2 = 510
    s += arrow(ox2, oy, 820, oy, INK, 1.4)
    s += arrow(ox2, oy, ox2, 110, INK, 1.4)
    s += poly([(ox2 + 10, oy - 20), (820, oy - 150)], GREEN, 3)
    for xx in range(0, 300, 18):
        s += circle(ox2 + 10 + xx, oy - 20 - xx * 0.43, 2.5, GREEN, GREEN, 0)
    s += text(660, 200, "плавно, кроком ~20 мВ", 10.5, GREEN, "middle", "bold")
    s += text(660, 304, "будь-яка напруга в діапазоні + ліміт струму", 10, INK, "middle")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Фіксовані — швидко й просто, але грубо. PPS дає точну напругу дрібним кроком — ідеально, щоб заряджати", 10.5, INK, "middle")
    s += text(W / 2, H - 8, "батарею НАПРЯМУ (зарядка стає CC/CV-джерелом, §7.4.6), без зайвого перетворювача в пристрої.", 10.5, INK, "middle")
    save("fig-10-3-3-fixedvspps.svg", s)


# ── Рис. 10.3.3.4 — контракт ─────────────────────────────────────────────────
def fig_pd_contract():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 32, "Контракт PD: до згоди — лише 5 В", 18, INK, "middle", "bold")
    # до
    s += rect(60, 80, 360, 200, "#fbf7ec", AMBER, 1.8, 12)
    s += text(240, 108, "ДО контракту", 13, AMBER, "middle", "bold")
    s += text(240, 142, "на VBUS — лише безпечні 5 В", 11.5, INK, "middle")
    s += text(240, 166, "(хоч би що могло джерело)", 10.5, GREY, "middle")
    s += text(240, 206, "5 В", 30, AMBER, "middle", "bold")
    s += text(240, 248, "пристрій ще не просив більше", 10, INK, "middle")
    s += arrow(430, 180, 480, 180, GREEN, 2.6)
    s += text(455, 168, "запит+згода", 9, GREEN, "middle")
    # після
    s += rect(490, 80, 360, 200, "#eef8ef", GREEN, 1.8, 12)
    s += text(670, 108, "ПІСЛЯ контракту", 13, GREEN, "middle", "bold")
    s += text(670, 142, "узгоджені напруга + макс. струм", 11.5, INK, "middle")
    s += text(670, 206, "напр. 20 В · 5 А", 22, GREEN, "middle", "bold")
    s += text(670, 248, "можна переукласти будь-коли", 10, INK, "middle")
    s += rect(70, H - 40, W - 140, 28, "#fbe9e7", RED, 1.5, 8)
    s += text(W / 2, H - 22, "Це і є вбудована безпека: висока напруга з'являється ЛИШЕ після того, як пристрій явно її попросив", 10.5, INK, "middle")
    s += text(W / 2, H - 8, "і джерело погодилося. Інакше дешевий 5-вольтовий пристрій згорів би від 20 В «про всяк випадок».", 10.5, INK, "middle")
    save("fig-10-3-4-contract.svg", s)


# ── Рис. 10.3.3.5 — EPR до 240 Вт ────────────────────────────────────────────
def fig_epr():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 32, "EPR: високовольтні щаблі до 240 Вт", 18, INK, "middle", "bold")
    base = ["5", "9", "15", "20"]
    epr = ["28", "36", "48"]
    ox, oy = 110, 280
    s += arrow(ox, oy, 760, oy, INK, 1.5)
    s += text(762, oy + 4, "профілі", 10.5, INK, "start", "bold")
    x = ox + 20
    for v in base:
        h = 20 + int(v) * 4
        s += rect(x, oy - h, 44, h, "none", BLUE, 2, 3)
        s += text(x + 22, oy - h - 8, v, 10, BLUE, "middle", "bold")
        x += 64
    s += text(x + 70, 110, "SPR (до 100 Вт)", 10, BLUE, "middle")
    for v in epr:
        h = 20 + int(v) * 4
        s += rect(x, oy - h, 44, h, "none", "#9b59b6", 2.4, 3)
        s += text(x + 22, oy - h - 8, v, 10, "#9b59b6", "middle", "bold")
        x += 64
    s += text(x + 30, 110, "EPR", 11, "#9b59b6", "middle", "bold")
    s += text(x + 30, 126, "до 240 Вт", 10, "#9b59b6", "middle")
    s += rect(70, H - 56, W - 140, 44, "#f3eafa", "#9b59b6", 1.6, 10)
    s += text(W / 2, H - 38, "EPR (Extended Power Range) додає 28/36/48 В і доводить межу до 240 Вт (48 В × 5 А) — досить ноутбуку.", 10.5, INK, "middle")
    s += text(W / 2, H - 22, "Та вмикається лише тоді, коли EPR підтримують УСІ троє: джерело, пристрій і кабель (з e-marker).", 10.5, INK, "middle")
    s += text(W / 2, H - 8, "Бракує когось одного — лишаються звичні SPR-щаблі до 100 Вт.", 10.5, GREY, "middle")
    save("fig-10-3-5-epr.svg", s)


# ── Рис. 10.3.3.6 — як це реалізувати ────────────────────────────────────────
def fig_pd_implement():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Як дати пристрою PD: три шляхи", 18, INK, "middle", "bold")
    cards = [
        ("«Тригер»-чип", "просить ОДНУ фіксовану напругу\n(напр. 12 В) і видає її", "без коду · §10.3.4", GREEN, 50),
        ("PD-контролер", "окремий чип веде всі переговори,\nкерується по шині від МК", "гнучко, надійно", BLUE, 330),
        ("МК + PD-стек", "сам мікроконтролер говорить PD\n(потрібен PHY + програма)", "найгнучкіше, найскладніше", AMBER, 610),
    ]
    for title, what, note, c, x in cards:
        s += rect(x, 76, 250, 200, "#ffffff", c, 2, 12)
        s += text(x + 125, 104, title, 13, c, "middle", "bold")
        for j, ln in enumerate(what.split("\n")):
            s += text(x + 125, 138 + j * 20, ln, 10.5, INK, "middle")
        s += text(x + 125, 240, note, 10, GREY, "middle", style="italic")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Треба стала вища напруга — найпростіше «тригер» (одна напруга, без коду). Складна політика живлення — контролер чи МК.", 10.5, INK, "middle")
    s += text(W / 2, H - 8, "Машину станів sink-політики (capabilities → request → accept) розберемо у ⚙️-вставці цього розділу.", 10.5, INK, "middle")
    save("fig-10-3-6-implement.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.3.4 — PD у власному пристрої: sink-контролер чи МК
# ════════════════════════════════════════════════════════════════════════════

def _diamond(cx, cy, w, h, c=INK, fill="#ffffff"):
    pts = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2),
           (cx - w / 2, cy), (cx, cy - h / 2)]
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{c}" stroke-width="2"/>\n'


# ── Рис. 10.3.4.1 — три шляхи в залізі ───────────────────────────────────────
def fig_paths_hw():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 32, "PD у власному пристрої: три шляхи в залізі", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "хто веде переговори і де живлення доходить до навантаження — від автономного чипа до повного стека в МК",
              12, GREY, "middle", style="italic")

    def usbc(x, y):
        out = rect(x, y, 92, 56, "#fbfbf8", INK, 2, 10)
        out += text(x + 46, y - 8, "USB-C", 10.5, INK, "middle", "bold")
        out += rect(x + 28, y + 20, 36, 16, "none", INK, 1.8, 8)
        out += rect(x + 34, y + 25, 24, 6, INK, INK, 0)
        return out

    def load(x, y, v):
        out = rect(x, y, 120, 56, "#eef8ef", GREEN, 2, 10)
        out += text(x + 60, y + 24, "Навантаження", 11, GREEN, "middle", "bold")
        out += text(x + 60, y + 42, v, 10, INK, "middle")
        return out

    # ── lane 1: тригер ──
    y = 104
    s += usbc(56, y)
    s += line(148, y + 28, 250, y + 28, AMBER, 2.4)
    s += text(199, y + 20, "CC", 9.5, AMBER, "middle", "bold")
    s += rect(250, y, 150, 56, "#eef8ef", GREEN, 2, 10)
    s += text(325, y + 24, "Тригер-чип", 12, GREEN, "middle", "bold")
    s += text(325, y + 42, "задано: 12 В", 9.5, INK, "middle")
    s += rect(470, y + 6, 66, 44, "#fff7e6", AMBER, 1.8, 6)
    s += text(503, y + 24, "ключ", 9.5, AMBER, "middle", "bold")
    s += text(503, y + 40, "power-good", 7.5, GREY, "middle")
    s += arrow(400, y + 28, 468, y + 28, RED, 2.4)
    s += arrow(536, y + 28, 700, y + 28, RED, 2.4)
    s += text(618, y + 20, "12 В", 9.5, RED, "middle", "bold")
    s += load(700, y, "12 В")
    s += text(325, y + 82, "0 рядків коду · МК не потрібен", 10.5, GREEN, "middle", "bold")

    # ── lane 2: контролер + МК ──
    y = 252
    s += usbc(56, y)
    s += line(148, y + 28, 250, y + 28, AMBER, 2.4)
    s += text(199, y + 20, "CC", 9.5, AMBER, "middle", "bold")
    s += rect(250, y, 170, 56, "#eef3fb", BLUE, 2, 10)
    s += text(335, y + 24, "PD-контролер", 12, BLUE, "middle", "bold")
    s += text(335, y + 42, "веде переговори", 9.5, INK, "middle")
    s += arrow(420, y + 28, 700, y + 28, RED, 2.4)
    s += text(560, y + 20, "узгоджена напруга", 9.5, RED, "middle", "bold")
    s += load(700, y, "5…20 В")
    s += rect(285, y + 80, 100, 40, "#ffffff", INK, 2, 8)
    s += text(335, y + 105, "МК", 12, INK, "middle", "bold")
    s += line(335, y + 56, 335, y + 80, BLUE, 2)
    s += text(360, y + 72, "I²C / керування", 9, BLUE, "start")
    s += text(335, y + 138, "МК командує по шині — гнучко, без власного PD-стека", 10, BLUE, "middle")

    # ── lane 3: МК зі стеком ──
    y = 440
    s += usbc(56, y)
    s += line(148, y + 28, 250, y + 28, AMBER, 2.4)
    s += text(199, y + 20, "CC", 9.5, AMBER, "middle", "bold")
    s += rect(250, y, 190, 56, "#fbf7ec", AMBER, 2, 10)
    s += text(345, y + 24, "МК + PD-PHY (стек)", 11.5, AMBER, "middle", "bold")
    s += text(345, y + 42, "сам говорить PD", 9.5, INK, "middle")
    s += arrow(440, y + 28, 700, y + 28, RED, 2.4)
    s += load(700, y, "5…48 В")
    s += text(345, y + 80, "жодного зайвого чипа, та весь протокол — твій клопіт", 10, AMBER, "middle")

    save("fig-10-4-1-paths.svg", s)


# ── Рис. 10.3.4.2 — анатомія тригера/sink-контролера ─────────────────────────
def fig_trigger_anatomy():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 32, "Усередині тригера: автономні переговори без процесора", 18, INK, "middle", "bold")
    s += rect(250, 90, 420, 250, "#fbfbf8", INK, 2.2, 14)
    s += text(460, 114, "sink-контролер («тригер»)", 12.5, INK, "middle", "bold")
    # входи зліва
    s += line(140, 150, 250, 150, AMBER, 2.4)
    s += text(150, 142, "CC1/CC2", 10, AMBER, "start", "bold")
    s += line(140, 200, 250, 200, RED, 2.4)
    s += text(150, 192, "VBUS (вхід)", 10, RED, "start", "bold")
    # блоки всередині
    s += rect(270, 130, 180, 44, "#eef8ef", GREEN, 1.8, 8)
    s += text(360, 148, "PD-рушій", 11, GREEN, "middle", "bold")
    s += text(360, 165, "(автономний, апаратний)", 8.5, INK, "middle")
    s += rect(270, 186, 180, 60, "#eef3fb", BLUE, 1.8, 8)
    s += text(360, 204, "Список бажаних PDO", 10.5, BLUE, "middle", "bold")
    s += text(360, 221, "за пріоритетом:", 9, INK, "middle")
    s += text(360, 238, "12 В → 9 В → 5 В", 10.5, INK, "middle", "bold")
    s += rect(270, 258, 180, 44, "#fff7e6", AMBER, 1.8, 8)
    s += text(360, 276, "Контроль VBUS-ключа", 9.5, AMBER, "middle", "bold")
    s += text(360, 292, "+ сигнал power-good", 9, INK, "middle")
    # конфіг зверху-праворуч
    s += rect(480, 130, 170, 80, "#f6f6f6", GREY, 1.6, 8)
    s += text(565, 150, "Налаштування", 10.5, INK, "middle", "bold")
    s += text(565, 169, "перемички або", 9.5, INK, "middle")
    s += text(565, 185, "однораз. запис у NVM:", 9.5, INK, "middle")
    s += text(565, 202, "яку напругу просити", 9.5, GREY, "middle")
    # вихід праворуч
    s += rect(480, 230, 170, 72, "#eef8ef", GREEN, 1.8, 8)
    s += text(565, 250, "Готово до навантаження", 9.5, GREEN, "middle", "bold")
    s += text(565, 268, "VBUS-ключ замкнено", 9.5, INK, "middle")
    s += text(565, 284, "лише за контрактом", 9.5, INK, "middle")
    s += arrow(670, 200, 740, 200, RED, 2.4)
    s += text(800, 188, "12 В на", 10.5, RED, "middle", "bold")
    s += text(800, 204, "навантаження", 10.5, RED, "middle", "bold")
    s += text(800, 224, "(по power-good)", 9, GREY, "middle")
    s += rect(70, H - 60, W - 140, 44, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 42, "Тригер сам робить усе рукостискання PD (тема 10.3.3) і вмикає живлення на навантаження лише тоді,", 10.5, INK, "middle")
    s += text(W / 2, H - 26, "коли дістав контракт на потрібну напругу. Розробник лише раз обирає, що просити, — і пише нуль коду.", 10.5, INK, "middle")
    save("fig-10-4-2-trigger.svg", s)


# ── Рис. 10.3.4.3 — що робити, коли контракту не дали ────────────────────────
def fig_no_contract():
    W, H = 900, 560
    s = header(W, H)
    s += text(W / 2, 32, "Коли контракту не дали: безпечні запасні шляхи", 18, INK, "middle", "bold")
    cxm = 300
    s += rect(cxm - 110, 56, 220, 40, "#fbf7ec", AMBER, 2, 8)
    s += text(cxm, 81, "Під'єднано → на VBUS 5 В", 11, INK, "middle", "bold")
    s += arrow(cxm, 96, cxm, 122, INK, 2)
    s += rect(cxm - 100, 122, 200, 38, "#eef3fb", BLUE, 2, 8)
    s += text(cxm, 146, "Прошу свій профіль (12 В)", 11, BLUE, "middle", "bold")
    s += arrow(cxm, 160, cxm, 186, INK, 2)
    # рішення 1
    s += _diamond(cxm, 222, 220, 78, GREEN)
    s += text(cxm, 218, "Джерело пропонує", 10, INK, "middle")
    s += text(cxm, 234, "12 В?", 10, INK, "middle", "bold")
    s += arrow(cxm + 110, 222, 560, 222, GREEN, 2.2)
    s += text(420, 212, "так", 10, GREEN, "middle", "bold")
    s += rect(560, 198, 300, 48, "#eef8ef", GREEN, 2, 8)
    s += text(710, 218, "Контракт 12 В", 11.5, GREEN, "middle", "bold")
    s += text(710, 236, "→ вмикаю навантаження", 10, INK, "middle")
    s += arrow(cxm, 261, cxm, 300, INK, 2)
    s += text(cxm + 16, 284, "ні", 10, RED, "start", "bold")
    # рішення 2
    s += _diamond(cxm, 342, 232, 80, BLUE)
    s += text(cxm, 338, "Налаштовано запасний", 9.5, INK, "middle")
    s += text(cxm, 354, "(9/15 В)?", 10, INK, "middle", "bold")
    s += arrow(cxm + 116, 342, 560, 342, BLUE, 2.2)
    s += text(420, 332, "так", 10, BLUE, "middle", "bold")
    s += rect(560, 318, 300, 48, "#eef3fb", BLUE, 2, 8)
    s += text(710, 338, "Контракт на запасний", 11, BLUE, "middle", "bold")
    s += text(710, 356, "→ працюю обмежено", 10, INK, "middle")
    s += arrow(cxm, 382, cxm, 421, INK, 2)
    s += text(cxm + 16, 405, "ні", 10, RED, "start", "bold")
    s += rect(cxm - 150, 421, 300, 64, "#fbe9e7", RED, 2, 10)
    s += text(cxm, 443, "Лишаюся на 5 В:", 11, RED, "middle", "bold")
    s += text(cxm, 461, "навантаження ВИМКНЕНО,", 10, INK, "middle")
    s += text(cxm, 477, "сигналю користувачу", 10, INK, "middle")
    s += rect(70, H - 36, W - 140, 26, "#fbe9e7", RED, 1.6, 8)
    s += text(W / 2, H - 19, "Залізне правило: вмикати навантаження ЛИШЕ за дійсним контрактом (по power-good). Нема потрібної напруги — не вмикай.", 9.5, INK, "middle")
    save("fig-10-4-3-nocontract.svg", s)


# ── Рис. 10.3.4.4 — широкий вхід замість точної вимоги ───────────────────────
def fig_wide_input():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Приймати, що дали: широкий вхід замість точної вимоги", 18, INK, "middle", "bold")
    # ліворуч — жорстко
    s += rect(40, 60, 410, 320, "#fdf3f2", RED, 1.6, 12)
    s += text(245, 86, "Жорстко: вимагаю рівно 12 В", 12.5, RED, "middle", "bold")
    s += rect(70, 110, 90, 46, "#fbfbf8", INK, 1.8, 8)
    s += text(115, 138, "USB-C", 10, INK, "middle", "bold")
    s += arrow(160, 133, 208, 133, AMBER, 2)
    s += rect(208, 110, 112, 46, "#eef3fb", BLUE, 1.8, 8)
    s += text(264, 130, "PD: прошу", 9.5, BLUE, "middle", "bold")
    s += text(264, 146, "тільки 12 В", 9.5, INK, "middle")
    s += arrow(320, 133, 368, 133, RED, 2)
    s += rect(355, 110, 72, 46, "#eef8ef", GREEN, 1.8, 8)
    s += text(391, 130, "12 В", 10, GREEN, "middle", "bold")
    s += text(391, 146, "вузол", 8.5, INK, "middle")
    s += rect(70, 200, 355, 70, "#fbe9e7", RED, 1.6, 10)
    s += text(247, 224, "Зарядка без профілю 12 В", 11, RED, "middle", "bold")
    s += text(247, 244, "→ контракту нема → пристрій", 10, INK, "middle")
    s += text(247, 260, "не вмикається зовсім", 10, INK, "middle")
    s += text(245, 320, "крихко: залежиш від однієї напруги", 10.5, RED, "middle", "bold")
    s += text(245, 344, "у меню саме цього зарядного", 10, INK, "middle")
    # праворуч — гнучко
    s += rect(490, 60, 410, 320, "#f1f8f2", GREEN, 1.6, 12)
    s += text(695, 86, "Гнучко: беру, що дали, і перетворюю", 12, GREEN, "middle", "bold")
    s += rect(510, 110, 84, 46, "#fbfbf8", INK, 1.8, 8)
    s += text(552, 138, "USB-C", 10, INK, "middle", "bold")
    s += arrow(594, 133, 634, 133, AMBER, 2)
    s += rect(634, 110, 106, 46, "#eef3fb", BLUE, 1.8, 8)
    s += text(687, 130, "PD: будь-який", 9, BLUE, "middle", "bold")
    s += text(687, 146, "профіль 5–20 В", 9, INK, "middle")
    s += arrow(740, 133, 778, 133, RED, 2)
    s += rect(778, 104, 106, 58, "#fff7e6", AMBER, 1.9, 8)
    s += text(831, 126, "buck-boost", 9.5, AMBER, "middle", "bold")
    s += text(831, 142, "5–20 В→12 В", 9, INK, "middle")
    s += text(831, 156, "(10.1.4)", 8, GREY, "middle")
    s += rect(634, 210, 250, 70, "#eef8ef", GREEN, 1.6, 10)
    s += text(759, 234, "Будь-яка PD-зарядка годиться:", 10, GREEN, "middle", "bold")
    s += text(759, 254, "9, 15, 20 В → перетворювач", 9.5, INK, "middle")
    s += text(759, 270, "зробить рівні 12 В", 9.5, INK, "middle")
    s += text(695, 320, "стійко: працює навіть від 5 В", 10.5, GREEN, "middle", "bold")
    s += text(695, 344, "(хай і меншою потужністю)", 10, INK, "middle")
    s += rect(70, H - 28, W - 140, 20, "#fff7e6", AMBER, 1.4, 8)
    s += text(W / 2, H - 14, "Ціна гнучкості — зайвий перетворювач; натомість пристрій не прив'язаний до того, чи має саме цей зарядний саме твою напругу.", 10, INK, "middle")
    save("fig-10-4-4-wideinput.svg", s)


# ── Рис. 10.3.4.5 — МК міняє контракт на ходу ────────────────────────────────
def fig_mcu_runtime():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 32, "Що вміє МК і не вміє тригер: міняти контракт на ходу", 18, INK, "middle", "bold")
    s += rect(60, 90, 150, 70, "#ffffff", INK, 2, 10)
    s += text(135, 118, "МК", 13, INK, "middle", "bold")
    s += text(135, 138, "політика живлення", 9, INK, "middle")
    s += rect(60, 200, 150, 64, "#eef3fb", BLUE, 2, 10)
    s += text(135, 226, "PD-контролер", 11, BLUE, "middle", "bold")
    s += text(135, 244, "веде CC/PD", 9, INK, "middle")
    s += line(135, 160, 135, 200, BLUE, 2)
    s += text(150, 184, "I²C", 9, BLUE, "start", "bold")
    s += text(135, 292, "читає меню (capabilities),", 9.5, INK, "middle")
    s += text(135, 308, "просить і ПЕРЕпросить", 9.5, INK, "middle")
    s += text(360, 86, "Вибір профілю за умовами в реальному часі:", 12, INK, "start", "bold")
    rows = [
        ("Холодно, треба швидко", "→ просить 20 В · максимум потужності", GREEN, 110),
        ("Грійка / гаряче", "→ просить 15 В · менше тепла на перетворювачі", AMBER, 174),
        ("Заряджаю батарею", "→ APDO/PPS: веде напругу за Vбат (CC/CV, §7.4.6)", BLUE, 238),
        ("Навантаження впало", "→ перепогоджує менший профіль, економить", GREY, 302),
    ]
    for q, a, c, y in rows:
        s += rect(360, y, 250, 44, "#ffffff", c, 1.8, 8)
        s += text(485, y + 27, q, 10.5, c, "middle", "bold")
        s += arrow(610, y + 22, 660, y + 22, INK, 1.8)
        s += text(668, y + 26, a, 10, INK, "start")
    s += arrow(232, 244, 352, 200, GREEN, 1.8, dash="5,4")
    s += text(300, 212, "нове рішення", 8.5, GREEN, "middle")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 26, "Тригер просить ОДНУ наперед задану напругу — і на цьому все. МК читає умови (тепло, заряд, режим) і ПЕРЕукладає контракт,", 9.5, INK, "middle")
    s += text(W / 2, H - 12, "коли треба, — аж до плавної PPS, щоб живити батарею напряму. Ціна — код, PD-стек чи контролер і більше способів помилитися.", 9.5, INK, "middle")
    save("fig-10-4-5-runtime.svg", s)


# ── Рис. 10.3.4.6 — що обрати ────────────────────────────────────────────────
def fig_decision_guide():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 32, "Що обрати: тригер, контролер чи МК", 18, INK, "middle", "bold")
    cards = [
        ("ТРИГЕР", "Одна стала напруга,|нема змін на ходу?", "просто · дешево · 0 коду",
         "зусилля ▮▯▯   гнучкість ▮▯▯", GREEN, 50),
        ("PD-КОНТРОЛЕР", "Треба міняти напругу|чи PPS, керує МК?", "гнучко · надійний чип",
         "зусилля ▮▮▯   гнучкість ▮▮▯", BLUE, 360),
        ("МК + СТЕК", "Без зайвого чипа й|повний контроль?", "максимум волі · максимум праці",
         "зусилля ▮▮▮   гнучкість ▮▮▮", AMBER, 670),
    ]
    for title, q, note, bars, c, x in cards:
        s += rect(x, 70, 220, 250, "#ffffff", c, 2, 12)
        s += text(x + 110, 100, title, 13.5, c, "middle", "bold")
        s += line(x + 20, 112, x + 200, 112, FAINT, 1)
        for j, ln in enumerate(q.split("|")):
            s += text(x + 110, 142 + j * 20, ln, 11, INK, "middle")
        s += text(x + 110, 212, note, 10, GREY, "middle", style="italic")
        s += text(x + 110, 250, bars, 10, c, "middle", "bold")
        s += text(x + 110, 298, "↓", 16, c, "middle", "bold")
    s += rect(70, H - 80, W - 140, 64, "#eef8ef", GREEN, 1.6, 10)
    s += text(W / 2, H - 58, "І незалежно від шляху — два залізні правила:", 11.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 38, "1) навантаження вмикати лише за дійсним контрактом (power-good);   2) проєктувати так, щоб пристрій пережив відкат у 5 В.", 10.5, INK, "middle")
    s += text(W / 2, H - 18, "Найкраще — поєднати: тригер чи контролер для напруги + широкий вхід або вимкнення навантаження для безпеки.", 10, GREY, "middle")
    save("fig-10-4-6-decision.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.3.5 — Легасі-зарядка: BC1.2 і кодування D+/D−
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.3.5.1 — нащо взагалі впізнавати порт ─────────────────────────────
def fig_why_dumb_charger():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 32, "Чому пристрій мусить «упізнавати» порт", 19, INK, "middle", "bold")
    s += text(W / 2, 54, "USB 2.0 за замовчуванням дозволяє лише 100–500 мА, доки не домовишся з хостом — а в зарядці хоста нема",
              12, GREY, "middle", style="italic")
    # ліворуч: хост-порт
    s += rect(50, 80, 400, 300, "#eef3fb", BLUE, 1.6, 12)
    s += text(250, 106, "Хост-порт (ПК)", 13, BLUE, "middle", "bold")
    s += rect(90, 130, 120, 56, "#fff", BLUE, 1.8, 8)
    s += text(150, 154, "ПК / хост", 11, BLUE, "middle", "bold")
    s += text(150, 172, "є процесор", 9, INK, "middle")
    s += rect(290, 130, 120, 56, "#fff", GREEN, 1.8, 8)
    s += text(350, 154, "пристрій", 11, GREEN, "middle", "bold")
    s += arrow(210, 150, 288, 150, INK, 1.8)
    s += arrow(288, 170, 212, 170, INK, 1.8)
    s += text(250, 210, "D+/D−: енумерація (розмова)", 10.5, INK, "middle", "bold")
    s += text(250, 246, "→ хост дозволяє 0.5 А (USB2)", 11, INK, "middle")
    s += text(250, 264, "або 0.9 А (USB3)", 11, INK, "middle")
    s += text(250, 320, "є з ким домовитися —", 11, BLUE, "middle", "bold")
    s += text(250, 340, "струм беремо з дозволу", 11, INK, "middle")
    # праворуч: тупий блок
    s += rect(470, 80, 400, 300, "#fbf7ec", AMBER, 1.6, 12)
    s += text(670, 106, "Блок у розетку (зарядка)", 13, AMBER, "middle", "bold")
    s += rect(510, 130, 120, 56, "#fff", AMBER, 1.8, 8)
    s += text(570, 154, "зарядка", 11, AMBER, "middle", "bold")
    s += text(570, 172, "нема процесора", 9, INK, "middle")
    s += rect(710, 130, 120, 56, "#fff", GREEN, 1.8, 8)
    s += text(770, 154, "пристрій", 11, GREEN, "middle", "bold")
    s += line(630, 150, 708, 150, GREY, 1.8, dash="5,4")
    s += text(670, 138, "нема з ким", 8.5, GREY, "middle")
    s += text(670, 214, "D+/D−: нема розмови", 10.5, RED, "middle", "bold")
    s += text(670, 250, "скільки можна взяти?!", 13, RED, "middle", "bold")
    s += text(670, 286, "(візьмеш забагато —", 9.5, INK, "middle")
    s += text(670, 302, "просадиш або спалиш блок)", 9.5, INK, "middle")
    s += text(670, 340, "BC1.2: упізнати тип порту", 11, AMBER, "middle", "bold")
    s += text(670, 358, "самими лініями D+/D−", 10, INK, "middle")
    s += rect(70, H - 26, W - 140, 18, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 13, "Розв'язок — домовлений у USB-IF стандарт BC1.2: пристрій упізнає порт по лініях даних, без жодного хоста", 10, INK, "middle")
    save("fig-10-5-1-dumbcharger.svg", s)


# ── Рис. 10.3.5.2 — три типи портів BC1.2 ────────────────────────────────────
def fig_port_types():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Три типи портів за BC1.2", 19, INK, "middle", "bold")
    cards = [
        ("SDP", "Standard Downstream Port", "ПК-порт «як завжди»",
         ["дані: так (звичайні)", "0.5 А (USB2)", "0.9 А (USB3)", "до енумерації — 100 мА"], BLUE, 40),
        ("CDP", "Charging Downstream Port", "ПК-порт, що ще й заряджає",
         ["дані: так", "до 1.5 А", "+ рукостискання", "  на D+/D−"], GREEN, 360),
        ("DCP", "Dedicated Charging Port", "блок у розетку, без даних",
         ["дані: нема", "ознака: D+↔D−", "  закорочені", "до 1.5 А"], AMBER, 680),
    ]
    for tag, full, role, rows, c, x in cards:
        s += rect(x, 70, 220, 260, "#ffffff", c, 2, 12)
        s += text(x + 110, 102, tag, 17, c, "middle", "bold")
        s += text(x + 110, 122, full, 9, INK, "middle")
        s += text(x + 110, 142, role, 10, GREY, "middle", style="italic")
        s += line(x + 20, 152, x + 200, 152, FAINT, 1)
        for j, r in enumerate(rows):
            s += text(x + 24, 176 + j * 24, "• " + r, 10.5, INK, "start")
    s += rect(70, H - 56, W - 140, 44, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "Уся легасі-зарядка тримається на одному питанні: цей порт — звичайний хост (SDP), заряджальний хост (CDP)", 10.5, INK, "middle")
    s += text(W / 2, H - 22, "чи тупий блок (DCP)? Стеля BC1.2 — 1.5 А × 5 В = 7.5 Вт; усе, що більше, — лише через CC (10.3.2) або PD (10.3.3).", 10.5, INK, "middle")
    save("fig-10-5-2-porttypes.svg", s)


# ── Рис. 10.3.5.3 — як виявляють DCP ─────────────────────────────────────────
def fig_dcp_short():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 32, "Підпис «тупої» зарядки: D+ закорочено на D−", 18, INK, "middle", "bold")
    # зарядка
    s += rect(60, 80, 330, 250, "#fbf7ec", AMBER, 1.8, 12)
    s += text(225, 106, "DCP (блок у розетку)", 12.5, AMBER, "middle", "bold")
    s += circle(140, 160, 5, INK, INK, 0)
    s += text(120, 164, "D+", 11, INK, "end", "bold")
    s += circle(140, 230, 5, INK, INK, 0)
    s += text(120, 234, "D−", 11, INK, "end", "bold")
    s += line(140, 160, 200, 160, INK, 2)
    s += line(140, 230, 200, 230, INK, 2)
    s += line(200, 160, 200, 230, INK, 2)
    s += _res(176, 178, 48, 34, "≤200 Ω", AMBER)
    s += text(225, 272, "лінії даних просто замкнені", 10, INK, "middle")
    s += text(225, 290, "(через малий опір)", 9.5, GREY, "middle")
    # кабель
    s += line(145, 160, 540, 160, COPP, 2.4)
    s += line(145, 230, 540, 230, COPP, 2.4)
    # пристрій
    s += rect(540, 80, 330, 250, "#eef8ef", GREEN, 1.8, 12)
    s += text(705, 106, "пристрій детектує", 12.5, GREEN, "middle", "bold")
    s += plus(582, 160, 7, RED)
    s += text(582, 138, "проба", 9, INK, "middle")
    s += text(620, 152, "подаю напругу на D+", 10, INK, "start")
    s += text(620, 192, "дивлюсь, чи з'явилась", 10, INK, "start")
    s += text(620, 208, "вона на D−", 10, INK, "start")
    s += text(620, 252, "з'явилась → замкнено", 10.5, GREEN, "start", "bold")
    s += text(620, 270, "→ зарядник, можна 1.5 А", 10.5, GREEN, "start", "bold")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "DCP не вміє говорити — тож його впізнають за простою ознакою: D+ і D− замкнені наскрізь. Пристрій подає пробну", 10, INK, "middle")
    s += text(W / 2, H - 8, "напругу на одну лінію й перевіряє, чи з'явиться вона на другій. Замкнено — отже, перед нами заряджальний блок.", 10, INK, "middle")
    save("fig-10-5-3-dcpshort.svg", s)


# ── Рис. 10.3.5.4 — послідовність розпізнавання BC1.2 ────────────────────────
def fig_bc12_flow():
    W, H = 920, 540
    s = header(W, H)
    s += text(W / 2, 32, "Як пристрій розпізнає порт: кроки BC1.2", 18, INK, "middle", "bold")
    cxm = 330

    def stp(y, t1, t2, c):
        o = rect(cxm - 120, y, 240, 40, "#ffffff", c, 2, 8)
        o += text(cxm, y + (18 if t2 else 24), t1, 10.5, c, "middle", "bold")
        if t2:
            o += text(cxm, y + 33, t2, 9, INK, "middle")
        return o

    s += stp(60, "VBUS з'явилась — є живлення", None, AMBER)
    s += arrow(cxm, 100, cxm, 122, INK, 2)
    s += stp(122, "Data Contact Detect", "переконавсь, що D+/D− торкнулись", GREY)
    s += arrow(cxm, 162, cxm, 184, INK, 2)
    s += _diamond(cxm, 224, 230, 84, BLUE)
    s += text(cxm, 216, "Первинне виявлення:", 9.5, INK, "middle")
    s += text(cxm, 232, "є відгук на D−?", 10, INK, "middle", "bold")
    # ні -> SDP (left)
    s += arrow(cxm - 115, 224, 184, 224, GREY, 2)
    s += text(150, 214, "ні", 9.5, GREY, "middle", "bold")
    s += rect(40, 200, 144, 50, "#eef3fb", BLUE, 2, 8)
    s += text(112, 220, "SDP", 12, BLUE, "middle", "bold")
    s += text(112, 238, "0.5/0.9 А · енумерація", 8.5, INK, "middle")
    # так -> down
    s += arrow(cxm, 266, cxm, 290, INK, 2)
    s += text(cxm + 16, 284, "так (зарядний порт)", 9, GREEN, "start", "bold")
    s += _diamond(cxm, 332, 230, 84, GREEN)
    s += text(cxm, 324, "Вторинне виявлення:", 9.5, INK, "middle")
    s += text(cxm, 340, "наскрізь замкнено?", 10, INK, "middle", "bold")
    # так -> DCP (right)
    s += arrow(cxm + 115, 332, 744, 332, AMBER, 2)
    s += text(580, 322, "так", 9.5, AMBER, "middle", "bold")
    s += rect(744, 308, 136, 50, "#fbf7ec", AMBER, 2, 8)
    s += text(812, 328, "DCP", 12, AMBER, "middle", "bold")
    s += text(812, 346, "до 1.5 А", 9, INK, "middle")
    # ні -> CDP (down)
    s += arrow(cxm, 374, cxm, 398, INK, 2)
    s += text(cxm + 14, 392, "ні", 9.5, GREEN, "start", "bold")
    s += rect(cxm - 100, 398, 200, 50, "#eef8ef", GREEN, 2, 8)
    s += text(cxm, 418, "CDP", 12, GREEN, "middle", "bold")
    s += text(cxm, 436, "ПК-порт + до 1.5 А", 9, INK, "middle")
    s += rect(70, H - 50, W - 140, 38, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 32, "Два прості тести по черзі: «це взагалі зарядний порт?» (первинне) і «це тупий блок чи розумний хост?» (вторинне).", 10, INK, "middle")
    s += text(W / 2, H - 16, "За підсумком пристрій ставить безпечний струм: 0.5/0.9 А для SDP або до 1.5 А для CDP чи DCP.", 10, INK, "middle")
    save("fig-10-5-4-bc12flow.svg", s)


# ── Рис. 10.3.5.5 — фірмові коди проти стандарту ─────────────────────────────
def fig_proprietary_codes():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Чому «не заряджає»: фірмові коди на D+/D−", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "до спільного стандарту кожен виробник кодував дозволений струм по-своєму — і пристрій шукає САМЕ свій підпис",
              11.5, GREY, "middle", style="italic")
    schemes = [
        ("Стандарт BC1.2", "D+ ↔ D− закорочені", "= «я зарядник», 1.5 А", GREEN, 40),
        ("Фірмовий A", "фіксовані ~2.0 / 2.7 В", "на D+/D− = 1 А / 2.1 А", BLUE, 360),
        ("Фірмовий B", "інші рівні / комбінації", "свій секрет на D+/D−", AMBER, 680),
    ]
    for tag, l1, l2, c, x in schemes:
        s += rect(x, 84, 220, 130, "#ffffff", c, 2, 12)
        s += text(x + 110, 110, tag, 12.5, c, "middle", "bold")
        s += text(x + 110, 144, l1, 10.5, INK, "middle", "bold")
        s += text(x + 110, 168, l2, 10, INK, "middle")
        s += text(x + 110, 196, "D+ / D−", 10, GREY, "middle", style="italic")
    s += rect(120, 244, 700, 96, "#fbe9e7", RED, 1.8, 12)
    s += text(470, 270, "Пристрій бачить ЧУЖИЙ підпис → не впізнає → падає в безпечні 0.5 А", 12, RED, "middle", "bold")
    s += text(470, 298, "Тому старий пристрій повільно заряджається від нового зарядного — і навпаки:", 11, INK, "middle")
    s += text(470, 318, "кожен чекав на свій код, а отримав незнайомий. Стандарт BC1.2 і пізніше USB-C це й лікують.", 10.5, INK, "middle")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Гарний сучасний зарядний навмисне підтримує кілька кодувань одразу (стандарт + найпоширеніші фірмові),", 10, INK, "middle")
    s += text(W / 2, H - 8, "щоб і старі, і нові пристрої впізнали його й узяли повний струм. Та універсальної гарантії нема — звідси несумісності.", 10, INK, "middle")
    save("fig-10-5-5-proprietary.svg", s)


# ── Рис. 10.3.5.6 — два світи: D+/D− і CC ────────────────────────────────────
def fig_two_worlds():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Два світи живлення в одному роз'ємі", 18, INK, "middle", "bold")
    # зарядка в центрі
    s += rect(390, 150, 160, 130, "#fbfbf8", INK, 2, 12)
    s += text(470, 178, "сучасний", 11, INK, "middle", "bold")
    s += text(470, 196, "зарядний", 11, INK, "middle", "bold")
    s += text(470, 224, "говорить", 10, GREY, "middle")
    s += text(470, 240, "ОБОМА", 11.5, GREEN, "middle", "bold")
    s += text(470, 256, "мовами", 10, GREY, "middle")
    # світ 1: D+/D−
    s += rect(40, 90, 300, 250, "#fbf7ec", AMBER, 1.6, 12)
    s += text(190, 116, "Легасі-світ: D+/D−", 12.5, AMBER, "middle", "bold")
    for i, t in enumerate(["BC1.2: SDP / CDP / DCP", "фірмові коди напругою", "межа ~1.5 А (7.5 Вт)", "для старих пристроїв", "(і через перехідники)"]):
        s += text(60, 146 + i * 26, "• " + t, 10.5, INK, "start")
    s += arrow(345, 200, 388, 200, AMBER, 2.2)
    # світ 2: CC
    s += rect(600, 90, 300, 250, "#eef8ef", GREEN, 1.6, 12)
    s += text(750, 116, "Сучасний світ: CC", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["резистори CC (10.3.2)", "5 В, до 3 А = 15 Вт", "USB PD (10.3.3–4)", "до 240 Вт", "для USB-C-пристроїв"]):
        s += text(620, 146 + i * 26, "• " + t, 10.5, INK, "start")
    s += arrow(552, 200, 598, 200, GREEN, 2.2)
    s += rect(70, H - 56, W - 140, 44, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "Старий механізм (коди на лініях даних) і новий (резистори CC та PD) не заперечують один одного — вони співіснують.", 10.5, INK, "middle")
    s += text(W / 2, H - 22, "Добрий зарядний відповідає на обидва запитання, тож живить і легасі-пристрій по D+/D−, і USB-C-пристрій по CC.", 10.5, INK, "middle")
    save("fig-10-5-6-twoworlds.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.3.6 — Свій «павербанк»: source, dual-role і power path
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.3.6.1 — від sink до source ───────────────────────────────────────
def fig_sink_to_source():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Перевертаємо роль: від sink до source", 19, INK, "middle", "bold")
    s += line(W / 2, 60, W / 2, H - 70, FAINT, 1.5, dash="6,5")
    # ліворуч sink
    s += text(235, 84, "Досі: пристрій БЕРЕ (sink)", 13, GREEN, "middle", "bold")
    s += rect(90, 110, 110, 70, "#fbe9e7", RED, 1.8, 10)
    s += text(145, 140, "джерело", 10.5, RED, "middle", "bold")
    s += text(145, 158, "(Rp)", 9.5, INK, "middle")
    s += rect(330, 110, 110, 70, "#eef8ef", GREEN, 1.8, 10)
    s += text(385, 138, "наш пристрій", 10, GREEN, "middle", "bold")
    s += text(385, 158, "Rd · бере", 9.5, INK, "middle")
    s += arrow(200, 145, 328, 145, RED, 2.4)
    s += text(264, 134, "VBUS →", 9.5, RED, "middle", "bold")
    s += text(235, 222, "виставляє Rd, просить, споживає", 10, INK, "middle")
    # праворуч source
    s += text(685, 84, "Тепер: пристрій ДАЄ (source)", 13, RED, "middle", "bold")
    s += rect(540, 110, 120, 70, "#eef8ef", GREEN, 1.8, 10)
    s += text(600, 138, "наш пристрій", 10, GREEN, "middle", "bold")
    s += text(600, 158, "Rp · живить", 9.5, INK, "middle")
    s += rect(780, 110, 110, 70, "#eef3fb", BLUE, 1.8, 10)
    s += text(835, 140, "споживач", 10.5, BLUE, "middle", "bold")
    s += text(835, 158, "(Rd)", 9.5, INK, "middle")
    s += arrow(660, 145, 778, 145, RED, 2.4)
    s += text(719, 134, "VBUS →", 9.5, RED, "middle", "bold")
    s += text(685, 222, "виставляє Rp, дає 5 В, у PD відповідає як джерело", 9.5, INK, "middle")
    s += rect(70, H - 56, W - 140, 44, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "Щоб давати живлення, пристрій міняє роль на дзеркальну: підтяжка Rp замість Rd (тема 10.3.2), сам виставляє", 10.5, INK, "middle")
    s += text(W / 2, H - 22, "5 В на VBUS, а схоче PD — відповідає на чужі запити меню профілів (тема 10.3.3). Той самий роз'єм, інший бік розмови.", 10.5, INK, "middle")
    save("fig-10-6-1-sinktosource.svg", s)


# ── Рис. 10.3.6.2 — OTG-boost із батареї до 5 В ──────────────────────────────
def fig_otg_boost():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Павербанк: підняти батарею до 5 В (OTG-boost)", 18, INK, "middle", "bold")
    s += rect(70, 120, 150, 90, "#eef8ef", GREEN, 1.8, 10)
    s += text(145, 150, "батарея 1S", 11.5, GREEN, "middle", "bold")
    s += text(145, 172, "3.0–4.2 В", 14, INK, "middle", "bold")
    s += text(145, 192, "(нижче за 5 В!)", 9, RED, "middle")
    s += arrow(220, 165, 298, 165, INK, 2.2)
    s += rect(300, 118, 150, 94, "#fff7e6", AMBER, 2, 10)
    s += text(375, 146, "BOOST ↑", 13, AMBER, "middle", "bold")
    s += text(375, 168, "підвищувач", 10, INK, "middle")
    s += text(375, 190, "(тема 10.1.3)", 9, GREY, "middle")
    s += arrow(450, 165, 528, 165, RED, 2.4)
    s += rect(530, 120, 130, 90, "#fbe9e7", RED, 1.8, 10)
    s += text(595, 150, "VBUS", 11.5, RED, "middle", "bold")
    s += text(595, 174, "5 В", 16, RED, "middle", "bold")
    s += arrow(660, 165, 718, 165, RED, 2.2)
    s += rect(720, 120, 110, 90, "#eef3fb", BLUE, 1.8, 10)
    s += text(775, 150, "чужий", 10.5, BLUE, "middle", "bold")
    s += text(775, 168, "пристрій", 10.5, BLUE, "middle", "bold")
    s += text(775, 192, "(заряджаємо)", 8.5, INK, "middle")
    s += text(W / 2, 252, "Одна літієва комірка дає лише 3.0–4.2 В — менше за потрібні 5 В на VBUS.", 11.5, INK, "middle")
    s += text(W / 2, 272, "Тому джерело-з-батареї ОБОВ'ЯЗКОВО має підвищувач, що тягне напругу комірки вгору до 5 В.", 11.5, INK, "middle")
    s += rect(70, H - 46, W - 140, 34, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 28, "Історично цей режим звали OTG (On-The-Go) — коли пристрій із хоста-споживача стає тим, хто сам живить периферію.", 10, INK, "middle")
    s += text(W / 2, H - 13, "Суть та сама: щоб віддавати 5 В від однокоміркової батареї, потрібен boost із ~3.7 В до 5 В.", 10, INK, "middle")
    save("fig-10-6-2-otgboost.svg", s)


# ── Рис. 10.3.6.3 — дворольовість і обмін ролями ─────────────────────────────
def fig_dual_role():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Дворольовість: той самий порт і бере, і дає", 18, INK, "middle", "bold")
    s += rect(60, 70, 360, 150, "#fbfbf8", INK, 1.6, 12)
    s += text(240, 96, "DRP: чергує Rp ↔ Rd (тема 10.3.2)", 11, INK, "middle", "bold")
    s += rect(95, 120, 110, 40, "#fbe9e7", RED, 1.6, 8)
    s += text(150, 145, "Rp (даю)", 10, RED, "middle", "bold")
    s += text(240, 147, "↔", 18, INK, "middle", "bold")
    s += rect(275, 120, 110, 40, "#eef8ef", GREEN, 1.6, 8)
    s += text(330, 145, "Rd (беру)", 10, GREEN, "middle", "bold")
    s += text(240, 192, "поки не вирішать, хто кому джерело", 9.5, INK, "middle")
    s += rect(520, 70, 360, 150, "#eef3fb", BLUE, 1.6, 12)
    s += text(700, 96, "PD power-role swap", 11.5, BLUE, "middle", "bold")
    s += text(700, 117, "ролі міняються БЕЗ перетикання", 9.5, INK, "middle")
    s += rect(545, 135, 130, 50, "#eef8ef", GREEN, 1.6, 8)
    s += text(610, 156, "був sink", 9.5, GREEN, "middle", "bold")
    s += text(610, 174, "(брав)", 8.5, INK, "middle")
    s += arrow(680, 160, 723, 160, INK, 2)
    s += rect(725, 135, 130, 50, "#fbe9e7", RED, 1.6, 8)
    s += text(790, 156, "став source", 9.5, RED, "middle", "bold")
    s += text(790, 174, "(дає)", 8.5, INK, "middle")
    s += rect(120, 250, 700, 90, "#f6f6f6", GREY, 1.5, 12)
    s += text(470, 276, "Приклад: ноутбук", 12, INK, "middle", "bold")
    s += text(470, 300, "спершу САМ заряджається від доку (sink) →", 11, INK, "middle")
    s += text(470, 320, "тоді тим самим кабелем живить телефон (source): роль помінялась по PD, дріт не чіпали", 10.5, INK, "middle")
    s += rect(70, H - 34, W - 140, 22, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 19, "Дворольовий порт корисний скрізь, де пристрій то бере, то віддає — ноутбук, павербанк, телефон із периферією", 10, INK, "middle")
    save("fig-10-6-3-dualrole.svg", s)


# ── Рис. 10.3.6.4 — архітектура power path ───────────────────────────────────
def fig_power_path():
    W, H = 940, 450
    s = header(W, H)
    s += text(W / 2, 32, "Power path: живити систему й заряджати батарею окремо", 18, INK, "middle", "bold")
    # наївно
    s += rect(50, 60, 850, 112, "#fdf3f2", RED, 1.5, 12)
    s += text(80, 84, "Наївно: USB → заряд → батарея → система", 12, RED, "start", "bold")
    s += rect(90, 102, 90, 44, "#fff", AMBER, 1.6, 6)
    s += text(135, 129, "USB", 10.5, AMBER, "middle", "bold")
    s += arrow(180, 124, 228, 124, INK, 1.8)
    s += rect(228, 102, 112, 44, "#eef8ef", GREEN, 1.6, 6)
    s += text(284, 129, "батарея", 10, GREEN, "middle", "bold")
    s += arrow(340, 124, 388, 124, INK, 1.8)
    s += rect(388, 102, 112, 44, "#eef3fb", BLUE, 1.6, 6)
    s += text(444, 129, "система", 10, BLUE, "middle", "bold")
    s += text(700, 118, "мертва батарея →", 11, RED, "middle", "bold")
    s += text(700, 138, "система не стартує", 10.5, INK, "middle")
    # power path
    s += rect(50, 192, 850, 208, "#f1f8f2", GREEN, 1.6, 12)
    s += text(80, 218, "Power path: вузол годує систему НАПРЯМУ, а батарею заряджає окремо", 12, GREEN, "start", "bold")
    s += rect(90, 250, 90, 50, "#fff", AMBER, 1.8, 8)
    s += text(135, 280, "USB", 10.5, AMBER, "middle", "bold")
    s += arrow(180, 275, 248, 275, RED, 2.4)
    s += rect(250, 248, 130, 56, "#fbfbf8", INK, 2, 8)
    s += text(315, 272, "вузол", 10.5, INK, "middle", "bold")
    s += text(315, 290, "power path", 9.5, INK, "middle")
    s += arrow(380, 262, 468, 240, RED, 2.4)
    s += rect(470, 214, 120, 48, "#eef3fb", BLUE, 1.8, 8)
    s += text(530, 234, "система", 10.5, BLUE, "middle", "bold")
    s += text(530, 252, "працює одразу", 8.5, INK, "middle")
    s += arrow(380, 290, 468, 322, GREEN, 2.4)
    s += rect(470, 300, 120, 48, "#eef8ef", GREEN, 1.8, 8)
    s += text(530, 320, "батарея", 10.5, GREEN, "middle", "bold")
    s += text(530, 338, "заряд залишком", 8.5, INK, "middle")
    s += text(710, 268, "мертва / відсутня батарея —", 10.5, GREEN, "middle", "bold")
    s += text(710, 286, "пристрій усе одно вмикається", 10, INK, "middle")
    s += text(710, 310, "(батарея = буфер, не єдиний шлях)", 9.5, GREY, "middle")
    s += rect(70, H - 38, W - 140, 26, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 20, "Розв'язавши «вхід → систему» й «вхід → батарею», дістаємо миттєвий старт навіть із розрядженою батареєю і чистий перехід на батарею, коли USB прибрали.", 9.5, INK, "middle")
    save("fig-10-6-4-powerpath.svg", s)


# ── Рис. 10.3.6.5 — розподіл струму (load sharing) ───────────────────────────
def fig_load_sharing():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Розподіл струму: система в пріоритеті, батарея — із залишку", 17.5, INK, "middle", "bold")
    # normal
    s += rect(60, 70, 380, 150, "#eef8ef", GREEN, 1.6, 12)
    s += text(250, 94, "Звичайно: вистачає на все", 12, GREEN, "middle", "bold")
    s += text(250, 120, "Iвх  =  Iсист  +  Iбат(заряд)", 13, INK, "middle", "bold")
    s += rect(90, 140, 320, 30, "#fff", GREY, 1.4, 6)
    s += rect(90, 140, 180, 30, "#cfe8d6", GREEN, 0, 6)
    s += text(180, 160, "система", 10, INK, "middle", "bold")
    s += rect(270, 140, 140, 30, "#dfeefb", BLUE, 0, 6)
    s += text(340, 160, "заряд батареї", 9.5, INK, "middle")
    s += text(250, 198, "вхідний ліміт ділиться: систему годуємо першою", 9.5, INK, "middle")
    # spike
    s += rect(480, 70, 380, 150, "#fbf7ec", AMBER, 1.6, 12)
    s += text(670, 94, "Пік: системі треба більше за вхід", 12, AMBER, "middle", "bold")
    s += text(670, 120, "Iсист  =  Iвх  +  Iбат(розряд)", 13, INK, "middle", "bold")
    s += rect(510, 140, 320, 30, "#fff", GREY, 1.4, 6)
    s += rect(510, 140, 200, 30, "#dfeefb", BLUE, 0, 6)
    s += text(610, 160, "із входу", 9.5, INK, "middle")
    s += rect(710, 140, 120, 30, "#f6e0c8", AMBER, 0, 6)
    s += text(770, 160, "+ батарея", 9.5, INK, "middle")
    s += text(670, 198, "батарея ДОПОМАГАЄ входу — тримає просадку (§7.4.5)", 9.5, INK, "middle")
    s += rect(70, 250, W - 140, 84, "#f6f6f6", GREY, 1.5, 12)
    s += text(W / 2, 276, "Вхідний струм обмежений тим, що дозволив порт (BC1.2 чи PD, теми 10.3.3–5).", 11, INK, "middle")
    s += text(W / 2, 298, "Розумний вузол стежить за цим лімітом: не дає сумарному споживанню просадити VBUS, а коли системі замало —", 10.5, INK, "middle")
    s += text(W / 2, 318, "тимчасово підмішує струм із батареї. Це і є динамічне керування power path.", 10.5, INK, "middle")
    save("fig-10-6-5-loadsharing.svg", s)


# ── Рис. 10.3.6.6 — добре джерело: запобіжники ───────────────────────────────
def fig_good_source():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Бути добрим джерелом: чотири запобіжники", 18, INK, "middle", "bold")
    items = [
        ("Не бреши про струм", "рекламуй (Rp/PDO) лише те,|що реально витягнеш", GREEN, 50),
        ("Обмеж струм і КЗ", "захист від перевантаження|й короткого на виході", BLUE, 285),
        ("Стережи зворотний струм", "не дай чужій вищій напрузі|затекти назад у батарею", RED, 520),
        ("Міняй роль безпечно", "при swap спершу зняти живлення,|тоді вже перемикати (DRP)", AMBER, 755),
    ]
    for title, body, c, x in items:
        s += rect(x, 70, 150, 180, "#ffffff", c, 2, 12)
        s += text(x + 75, 100, title, 10.5, c, "middle", "bold")
        s += line(x + 18, 110, x + 132, 110, FAINT, 1)
        for j, ln in enumerate(body.split("|")):
            s += text(x + 75, 136 + j * 18, ln, 9, INK, "middle")
        s += text(x + 75, 218, "✔", 18, c, "middle", "bold")
    s += rect(70, H - 56, W - 140, 44, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 38, "Джерело несе відповідальність: воно вирішує, скільки дати, і мусить пережити жадібний чи несправний споживач —", 10.5, INK, "middle")
    s += text(W / 2, H - 22, "коротке замикання, перевантаження, спробу зворотного живлення. Деталі чипів power path — у компонентній вставці розділу.", 10.5, INK, "middle")
    save("fig-10-6-6-goodsource.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 10.3.7 — Кабелі і сумісність у полі
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.3.7.1 — анатомія кабелю ──────────────────────────────────────────
def fig_cable_anatomy():
    W, H = 940, 450
    s = header(W, H)
    s += text(W / 2, 32, "Що всередині USB-C кабелю — і чому вони такі різні", 18, INK, "middle", "bold")

    def plug(x):
        o = rect(x, 86, 28, 70, "none", INK, 2, 6)
        o += rect(x + 7, 98, 14, 46, INK, INK, 0)
        return o

    s += plug(70)
    s += plug(W - 98)
    s += rect(98, 86, W - 196, 70, "#fbfbf8", GREY, 1.4, 14)
    conders = [
        ("VBUS / GND", "живлення — товщина дроту вирішує падіння", RED, 100),
        ("CC", "орієнтація, роль, живить e-marker (VCONN)", AMBER, 116),
        ("D+/D−", "дані USB 2.0", BLUE, 132),
        ("SS-пари", "швидкі дані / відео (USB 3.x), є не в усіх", GREEN, 148),
    ]
    for name, role, c, y in conders:
        s += line(126, y, W - 126, y, c, 3)
    s += rect(W - 192, 92, 60, 28, "#eef3fb", BLUE, 1.8, 6)
    s += text(W - 162, 110, "e-marker", 8.5, BLUE, "middle", "bold")
    for i, (name, role, c, y) in enumerate(conders):
        yy = 192 + i * 26
        s += line(120, yy - 4, 150, yy - 4, c, 3)
        s += text(158, yy, name + " — " + role, 10.5, INK, "start")
    variants = [
        ("«тільки заряд»", "лише VBUS/GND (часто й CC).", "даних нема — пристрій не|домовиться по D+/D−", RED, 70),
        ("повний, 3 А", "усі лінії, без e-marker.", "заряд і дані, але струм|обмежать безпечними 3 А", AMBER, 370),
        ("5 А / EPR", "усі лінії + e-marker.", "повний струм і висока|напруга (потрібен чип)", GREEN, 670),
    ]
    for title, l1, l2, c, x in variants:
        s += rect(x, 300, 200, 122, "#ffffff", c, 1.8, 10)
        s += text(x + 100, 324, title, 11.5, c, "middle", "bold")
        s += text(x + 100, 346, l1, 9.5, INK, "middle")
        for j, ln in enumerate(l2.split("|")):
            s += text(x + 100, 370 + j * 16, ln, 9, GREY, "middle")
    save("fig-10-7-1-cable.svg", s)


# ── Рис. 10.3.7.2 — роль e-marker ────────────────────────────────────────────
def fig_emarker_role():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "e-marker: чип, що дозволяє кабелю більше", 18, INK, "middle", "bold")
    s += rect(60, 80, 380, 130, "#fbf7ec", AMBER, 1.7, 12)
    s += text(250, 106, "Кабель БЕЗ e-marker", 12.5, AMBER, "middle", "bold")
    s += line(90, 140, 410, 140, COPP, 3)
    s += text(250, 168, "система не знає меж кабелю", 10.5, INK, "middle")
    s += text(250, 188, "→ припускає безпечні 3 А, EPR нема", 10.5, INK, "middle", "bold")
    s += rect(480, 80, 380, 130, "#eef8ef", GREEN, 1.7, 12)
    s += text(670, 106, "Кабель З e-marker", 12.5, GREEN, "middle", "bold")
    s += line(510, 140, 830, 140, COPP, 3)
    s += rect(640, 124, 60, 28, "#eef3fb", BLUE, 1.8, 6)
    s += text(670, 142, "e-marker", 8.5, BLUE, "middle", "bold")
    s += line(670, 124, 670, 110, AMBER, 1.8)
    s += text(748, 116, "живиться з VCONN", 8.5, AMBER, "start")
    s += text(670, 188, "доповідає: 5 А, швидкість, довжина", 10.5, INK, "middle", "bold")
    s += rect(120, 240, 680, 100, "#f6f6f6", GREY, 1.5, 12)
    s += text(460, 266, "Що каже e-marker системі", 12, INK, "middle", "bold")
    cols = [("струм", "3 А чи 5 А"), ("швидкість", "USB 2.0 / 3.x"), ("довжина", "затримки, втрати"), ("тип", "пасивний / активний")]
    for i, (a, b) in enumerate(cols):
        x = 178 + i * 162
        s += text(x, 296, a, 11, GREEN, "middle", "bold")
        s += text(x, 316, b, 9.5, INK, "middle")
    s += rect(70, H - 40, W - 140, 28, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 22, "Понад 3 А й уся EPR (теми 10.3.2–4) вимагають кабелю з e-marker. Нема чипа — система перестраховується 3 амперами,", 10, INK, "middle")
    s += text(W / 2, H - 8, "хоч би що міг зарядний. Тому «той самий блок, але інший шнур» інколи заряджає геть по-різному.", 10, INK, "middle")
    save("fig-10-7-2-emarker.svg", s)


# ── Рис. 10.3.7.3 — падіння на дроті ─────────────────────────────────────────
def fig_voltage_drop():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Падіння на дроті: 5 В виходять, 4.2 В доходять", 18, INK, "middle", "bold")
    s += rect(60, 110, 130, 80, "#fbe9e7", RED, 1.8, 10)
    s += text(125, 142, "зарядка", 11, RED, "middle", "bold")
    s += text(125, 166, "5.0 В", 15, RED, "middle", "bold")
    s += line(190, 135, 740, 135, COPP, 3)
    s += line(190, 165, 740, 165, COPP, 3)
    s += _res(420, 116, 70, 36, "R кабелю", AMBER)
    s += text(455, 198, "R = 2×Rдроту + Rконтактів", 10, INK, "middle")
    s += arrow(290, 150, 350, 150, RED, 2)
    s += text(320, 142, "I →", 9.5, RED, "middle", "bold")
    s += rect(740, 110, 140, 80, "#eef8ef", GREEN, 1.8, 10)
    s += text(810, 142, "пристрій", 11, GREEN, "middle", "bold")
    s += text(810, 166, "4.2 В", 15, RED, "middle", "bold")
    s += rect(120, 240, 700, 112, "#f6f6f6", GREY, 1.5, 12)
    s += text(460, 266, "ΔV = I × R   (закон Ома, §1.3)", 12.5, INK, "middle", "bold")
    s += text(460, 294, "тонкий/довгий шнур при 3 А: ΔV ≈ 0.8 В → на пристрої 4.2 В (заряд гальмує)", 10.5, INK, "middle")
    s += text(460, 316, "та сама потужність вищою напругою (PD 9 В): струм менший → і падіння менше", 10.5, INK, "middle")
    s += text(460, 338, "ось чому PD воліє підняти напругу, а не струм (теми 10.3.3–4)", 10.5, GREEN, "middle", "bold")
    s += rect(70, H - 34, W - 140, 22, "#fff7e6", AMBER, 1.4, 8)
    s += text(W / 2, H - 19, "Половину «не заряджає» в полі дає саме падіння на дешевому тонкому шнурі — деталь розрахунку у 🧮-вставці про падіння на кабелі", 10, INK, "middle")
    save("fig-10-7-3-drop.svg", s)


# ── Рис. 10.3.7.4 — карта несумісностей ──────────────────────────────────────
def fig_incompat_map():
    W, H = 940, 450
    s = header(W, H)
    s += text(W / 2, 32, "Чому «не заряджає»: карта типових несумісностей", 18, INK, "middle", "bold")
    causes = [
        ("«тільки заряд» шнур", "нема ліній даних/CC →|нема переговорів", AMBER, 70, 92),
        ("кабель на 3 А", "нема e-marker →|стелю 3 А, EPR зась", GREEN, 385, 82),
        ("тонкий / довгий", "падіння напруги →|заряд гальмує", RED, 700, 92),
        ("кривий A→C", "невірний 56 кОм →|невпізнання струму", BLUE, 70, 330),
        ("джерело без профілю", "нема твоєї напруги →|відкат у 5 В (10.3.4)", AMBER, 385, 358),
        ("чужий фірмовий код", "BC1.2 не збігся →|0.5 А (10.3.5)", BLUE, 700, 330),
    ]
    for title, body, c, x, y in causes:
        cyv = y + (70 if y < 200 else 0)
        s += line(x + 85, cyv, 470, 230, FAINT, 1.4)
    for title, body, c, x, y in causes:
        s += rect(x, y, 170, 70, "#ffffff", c, 1.8, 10)
        s += text(x + 85, y + 22, title, 10.5, c, "middle", "bold")
        for j, ln in enumerate(body.split("|")):
            s += text(x + 85, y + 40 + j * 15, ln, 8.8, INK, "middle")
    s += rect(385, 200, 170, 60, "#fbe9e7", RED, 2, 12)
    s += text(470, 226, "не заряджає", 12.5, RED, "middle", "bold")
    s += text(470, 244, "або повільно", 10.5, INK, "middle")
    s += rect(70, H - 30, W - 140, 20, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 16, "Причина майже завжди в одному з трьох: кабель, зарядний або переговори. Системна перевірка — на наступному рисунку.", 10, INK, "middle")
    save("fig-10-7-4-incompat.svg", s)


# ── Рис. 10.3.7.5 — діагностика по кроках ────────────────────────────────────
def fig_diagnosis_flow():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 32, "Діагностика «не заряджає» як інженерна задача", 18, INK, "middle", "bold")
    cxm = 300
    s += rect(cxm - 130, 56, 260, 38, "#fbe9e7", RED, 2, 8)
    s += text(cxm, 80, "Скарга: не заряджає / повільно", 11, RED, "middle", "bold")
    s += arrow(cxm, 94, cxm, 116, INK, 2)
    s += _diamond(cxm, 150, 230, 70, BLUE)
    s += text(cxm, 154, "Заряджає взагалі?", 10.5, INK, "middle", "bold")
    s += arrow(cxm - 115, 150, 152, 150, GREY, 2)
    s += text(150, 140, "ні", 9.5, GREY, "middle", "bold")
    s += rect(30, 128, 150, 46, "#fff", GREY, 1.8, 8)
    s += text(105, 148, "контакт / цілість", 9.5, INK, "middle", "bold")
    s += text(105, 164, "кабелю, роз'єм", 8.5, INK, "middle")
    s += arrow(cxm, 185, cxm, 210, INK, 2)
    s += text(cxm + 14, 204, "так, але мляво", 8.5, INK, "start")
    s += rect(cxm - 130, 210, 260, 44, "#eef3fb", BLUE, 2, 8)
    s += text(cxm, 230, "ВИМІРЯЙ VBUS на пристрої", 10.5, BLUE, "middle", "bold")
    s += text(cxm, 246, "під навантаженням (§1.6)", 9, INK, "middle")
    s += arrow(cxm, 254, cxm, 280, INK, 2)
    s += _diamond(cxm, 318, 240, 76, AMBER)
    s += text(cxm, 322, "VBUS просідає?", 10.5, INK, "middle", "bold")
    s += arrow(cxm + 120, 318, 700, 318, AMBER, 2)
    s += text(560, 308, "так", 9.5, AMBER, "middle", "bold")
    s += rect(700, 294, 200, 50, "#fbf7ec", AMBER, 2, 8)
    s += text(800, 314, "падіння на кабелі", 10, AMBER, "middle", "bold")
    s += text(800, 332, "→ товщий/коротший шнур", 9, INK, "middle")
    s += arrow(cxm, 356, cxm, 382, INK, 2)
    s += text(cxm + 14, 376, "ні (тримає, та струм малий)", 8.5, INK, "start")
    s += _diamond(cxm, 422, 240, 78, GREEN)
    s += text(cxm, 416, "Переговори вдались?", 10, INK, "middle", "bold")
    s += text(cxm, 432, "CC / PD / BC1.2", 9, INK, "middle")
    s += arrow(cxm + 120, 422, 700, 422, GREEN, 2)
    s += text(560, 412, "ні", 9.5, GREEN, "middle", "bold")
    s += rect(700, 398, 200, 50, "#eef8ef", GREEN, 2, 8)
    s += text(800, 416, "кабель без ліній / e-marker", 8.8, GREEN, "middle", "bold")
    s += text(800, 434, "чи джерело без профілю", 9, INK, "middle")
    s += arrow(cxm, 461, cxm, 484, INK, 2)
    s += text(cxm + 14, 478, "так", 8.5, GREEN, "start", "bold")
    s += rect(cxm - 130, 484, 260, 44, "#f6f6f6", GREY, 1.8, 8)
    s += text(cxm, 504, "усе гаразд — це стеля", 10, INK, "middle", "bold")
    s += text(cxm, 520, "цього блока/кабелю", 9, INK, "middle")
    s += rect(70, H - 26, W - 140, 18, "#eef8ef", GREEN, 1.4, 8)
    s += text(W / 2, H - 13, "Не «магія», а чотири перевірки по черзі: контакт → виміряй VBUS → просідання (кабель) → переговори (лінії/профіль)", 10, INK, "middle")
    save("fig-10-7-5-diagnosis.svg", s)


# ── Рис. 10.3.7.6 — проєктувати під поле ─────────────────────────────────────
def fig_field_robust():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Проєктувати під поле: п'ять звичок", 18, INK, "middle", "bold")
    items = [
        ("Приймай діапазон", "широкий вхід — будь-який|профіль годиться (10.3.4/6)", GREEN),
        ("Не вимагай максимум", "не проси 5 А/EPR без потреби —|менше залежиш від кабелю", BLUE),
        ("Міряй VBUS у себе", "стеж за напругою на пристрої|під навантаженням, не на блоці", AMBER),
        ("Не падай від просадки", "терпи 4.5 В: тримай|низький поріг brownout", RED),
        ("Кажи користувачу", "«повільно — інший шнур/блок»|краще за німу загадку", "#9b59b6"),
    ]
    n = len(items)
    bw = (W - 100) / n
    for i, (title, body, c) in enumerate(items):
        x = 50 + i * bw
        s += rect(x + 8, 70, bw - 16, 200, "#ffffff", c, 1.9, 12)
        s += text(x + bw / 2, 100, title, 10.5, c, "middle", "bold")
        s += line(x + 18, 110, x + bw - 18, 110, FAINT, 1)
        for j, ln in enumerate(body.split("|")):
            s += text(x + bw / 2, 136 + j * 18, ln, 8.6, INK, "middle")
        s += text(x + bw / 2, 240, "✔", 17, c, "middle", "bold")
    s += rect(70, H - 44, W - 140, 32, "#eef8ef", GREEN, 1.5, 8)
    s += text(W / 2, H - 26, "Поле непередбачуване: випадковий шнур, випадковий блок, бруд у роз'ємі. Надійний пристрій не вимагає ідеалу —", 10.5, INK, "middle")
    s += text(W / 2, H - 12, "він приймає, що дають, чесно міряє, що дійшло, терпить просадку й каже людині, коли щось не так.", 10.5, INK, "middle")
    save("fig-10-7-6-fieldrobust.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🧮 (до теми 10.3.1) — Падіння на кабелі
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.3.1m.1 — модель падіння (дві жили) ───────────────────────────────
def fig_cabledrop_model():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 32, "Модель падіння на кабелі: дві жили — туди й назад", 18, INK, "middle", "bold")
    s += rect(70, 120, 130, 120, "#fbe9e7", RED, 1.8, 10)
    s += text(135, 158, "джерело", 11, RED, "middle", "bold")
    s += text(135, 188, "5.0 В", 17, RED, "middle", "bold")
    s += rect(700, 120, 130, 120, "#eef8ef", GREEN, 1.8, 10)
    s += text(765, 158, "пристрій", 11, GREEN, "middle", "bold")
    s += text(765, 186, "Vпр", 14, INK, "middle", "bold")
    s += text(765, 208, "= 5 − ΔV", 11, INK, "middle")
    # верхня жила VBUS
    s += line(200, 145, 380, 145, COPP, 3)
    s += _res(380, 128, 70, 34, "Rжили", COPP)
    s += line(450, 145, 700, 145, COPP, 3)
    s += arrow(270, 145, 330, 145, RED, 2)
    s += text(290, 137, "I →", 9.5, RED, "middle", "bold")
    s += text(415, 116, "VBUS (туди)", 9.5, INK, "middle")
    # нижня жила GND
    s += line(200, 215, 380, 215, INK, 3)
    s += _res(380, 198, 70, 34, "Rжили", INK)
    s += line(450, 215, 700, 215, INK, 3)
    s += arrow(630, 215, 570, 215, RED, 2)
    s += text(610, 232, "← I", 9.5, RED, "middle", "bold")
    s += text(415, 250, "GND (назад)", 9.5, INK, "middle")
    s += rect(150, 290, 600, 66, "#f6f6f6", GREY, 1.5, 10)
    s += text(450, 314, "Rкаб = 2 · (L · ρ) + Rконтактів      ΔV = I · Rкаб", 13, INK, "middle", "bold")
    s += text(450, 338, "струм біжить туди по VBUS і назад по GND — тому опір ПОДВІЙНИЙ", 10.5, INK, "middle")
    save("fig-10-1m1-model.svg", s)


# ── Рис. 10.3.1m.2 — опір за калібром і падіння ──────────────────────────────
def fig_cabledrop_table():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 32, "Опір за калібром і падіння при 3 А (кабель 1 м)", 18, INK, "middle", "bold")
    # таблиця
    s += rect(50, 70, 330, 300, "#ffffff", GREY, 1.5, 10)
    s += text(215, 96, "Опір мідної жили", 12, INK, "middle", "bold")
    s += rect(70, 110, 290, 28, "#eef3fb", BLUE, 1.2, 5)
    s += text(120, 129, "AWG", 11, BLUE, "middle", "bold")
    s += text(255, 129, "Ω на метр", 11, BLUE, "middle", "bold")
    rows = [("20", "0.033"), ("22", "0.053"), ("24", "0.084"),
            ("26", "0.133"), ("28", "0.213"), ("30", "0.339")]
    for i, (a, b) in enumerate(rows):
        y = 138 + i * 36
        s += rect(70, y, 290, 36, "#ffffff" if i % 2 == 0 else "#f6f6f6", FAINT, 1, 0)
        s += text(120, y + 23, a, 11.5, INK, "middle", "bold")
        s += text(255, y + 23, b, 11.5, INK, "middle")
    s += text(215, 362, "більший номер AWG = тонша жила = більший опір", 8.8, GREY, "middle")
    # стовпчики
    s += text(680, 96, "ΔV при I = 3 А, 1 м (+ ~0.1 Ω контакти)", 11, INK, "middle", "bold")
    bars = [("24 AWG", 0.80, GREEN), ("28 AWG", 1.58, AMBER), ("30 AWG", 2.33, RED)]
    bx, by = 470, 300
    s += line(bx, by, 900, by, INK, 1.5)
    s += line(bx, by, bx, 120, INK, 1.5)
    s += text(bx - 8, 130, "ΔV, В", 9.5, INK, "end")
    for i, (name, dv, c) in enumerate(bars):
        x = bx + 40 + i * 120
        h = dv * 68
        s += rect(x, by - h, 70, h, "#fff", c, 2, 4)
        s += f'<rect x="{x:.0f}" y="{by-h:.0f}" width="70" height="{h:.0f}" rx="4" fill="{c}" fill-opacity="0.18"/>\n'
        s += text(x + 35, by - h - 8, f"{dv:.1f} В", 11, c, "middle", "bold")
        s += text(x + 35, by + 18, name, 10, INK, "middle")
    s += rect(470, 348, 420, 52, "#eef8ef", GREEN, 1.4, 8)
    s += text(680, 368, "Та сама потужність 15 Вт вищою напругою:", 9.5, GREEN, "middle", "bold")
    s += text(680, 386, "9 В × 1.67 А на 28 AWG → ΔV ≈ 0.9 В замість 1.6 В", 9.5, INK, "middle")
    save("fig-10-1m2-table.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🔌 (до теми 10.3.2) — Резистори CC
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.3.2c.1 — дільник Rp/Rd зі значеннями ─────────────────────────────
def fig_cc_resistors():
    W, H = 900, 460
    s = header(W, H)
    s += text(W / 2, 32, "Резистори CC: дільник Rp (джерело) / Rd (пристрій)", 18, INK, "middle", "bold")
    mx = 360
    s += text(mx, 78, "+5 В  (підтяжка джерела)", 10.5, RED, "middle", "bold")
    s += line(mx, 84, mx, 104, INK, 2)
    s += _res(mx - 28, 104, 56, 44, "Rp", RED)
    s += text(mx + 70, 130, "56 / 22 / 10 кОм", 10, RED, "start", "bold")
    s += text(mx + 70, 146, "(джерело обирає → струм)", 9, INK, "start")
    s += line(mx, 148, mx, 200, INK, 2)
    s += circle(mx, 200, 5, AMBER, AMBER, 0)
    s += text(mx - 12, 196, "CC", 10.5, AMBER, "end", "bold")
    s += line(mx, 200, 560, 200, GREEN, 1.6, dash="4,3")
    s += rect(560, 178, 150, 44, "#eef8ef", GREEN, 1.6, 8)
    s += text(635, 198, "пристрій міряє", 9.5, GREEN, "middle", "bold")
    s += text(635, 214, "Vcc на CC", 9, INK, "middle")
    s += line(mx, 200, mx, 252, INK, 2)
    s += _res(mx - 28, 252, 56, 44, "Rd", GREEN)
    s += text(mx + 70, 278, "5.1 кОм (фіксовано)", 10, GREEN, "start", "bold")
    s += text(mx + 70, 294, "= «тут пристрій (sink)»", 9, INK, "start")
    s += line(mx, 296, mx, 326, INK, 2)
    s += line(mx - 18, 326, mx + 18, 326, INK, 3)
    s += line(mx - 11, 332, mx + 11, 332, INK, 2)
    s += line(mx - 4, 338, mx + 4, 338, INK, 1.5)
    s += text(155, 130, "ДЖЕРЕЛО", 12, RED, "middle", "bold")
    s += text(155, 150, "(source)", 9.5, INK, "middle")
    s += text(155, 280, "ПРИСТРІЙ", 12, GREEN, "middle", "bold")
    s += text(155, 300, "(sink)", 9.5, INK, "middle")
    s += rect(60, 360, 780, 92, "#f6f6f6", GREY, 1.4, 10)
    s += text(450, 384, "Vcc = 5 В · Rd / (Rp + Rd)   — за нею пристрій читає дозволений струм", 11.5, INK, "middle", "bold")
    trip = [("Rp = 56 кОм", "Vcc ≈ 0.42 В", "→ 0.5 / 0.9 А (типово)"),
            ("Rp = 22 кОм", "Vcc ≈ 0.94 В", "→ 1.5 А"),
            ("Rp = 10 кОм", "Vcc ≈ 1.69 В", "→ 3.0 А (15 Вт)")]
    for i, (a, b, c) in enumerate(trip):
        y = 408 + i * 15
        s += text(120, y, a, 9.5, RED, "start", "bold")
        s += text(335, y, b, 9.5, INK, "start")
        s += text(560, y, c, 9.5, GREEN, "start", "bold")
    save("fig-10-2c1-ccres.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка ⚙️ (до теми 10.3.3) — Машина станів PD-sink
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.3.3a.1 — FSM sink-політики ───────────────────────────────────────
def fig_pd_fsm():
    W, H = 960, 430
    s = header(W, H)
    s += text(W / 2, 32, "Машина станів PD-sink: від під'єднання до контракту", 18, INK, "middle", "bold")
    states = [
        ("VBUS 5 В", "безпечний|старт", AMBER),
        ("WAIT_CAPS", "чекаю меню|(Source_Caps)", BLUE),
        ("CHOOSE", "обираю PDO|(політика)", GREEN),
        ("REQ_SENT", "послав|Request", BLUE),
        ("WAIT_PSRDY", "є Accept,|чекаю PS_RDY", BLUE),
        ("CONTRACT", "робота на|12 В", GREEN),
    ]
    n = len(states)
    bw = 130
    gap = (W - 80 - n * bw) / (n - 1)
    y = 90
    xs = []
    for i, (name, sub, c) in enumerate(states):
        x = 40 + i * (bw + gap)
        xs.append(x)
        s += rect(x, y, bw, 64, "#ffffff", c, 2, 10)
        s += text(x + bw / 2, y + 24, name, 10.5, c, "middle", "bold")
        for j, ln in enumerate(sub.split("|")):
            s += text(x + bw / 2, y + 40 + j * 14, ln, 8.5, INK, "middle")
    labels = ["attach", "caps", "Request", "Accept", "PS_RDY"]
    for i in range(n - 1):
        s += arrow(xs[i] + bw, y + 32, xs[i + 1], y + 32, INK, 2)
        s += text((xs[i] + bw + xs[i + 1]) / 2, y + 24, labels[i], 8.5, INK, "middle", "bold")
    ry = 250
    s += text(W / 2, ry - 14, "Будь-яка біда → безпечні 5 В (скинути контракт, зняти навантаження)", 11, RED, "middle", "bold")
    s += line(80, ry, W - 80, ry, RED, 1.8, dash="6,4")
    fbs = ["Reject", "timeout", "detach", "Hard Reset", "нові Caps"]
    for i, lb in enumerate(fbs):
        x = 170 + i * 150
        s += line(x, y + 64, x, ry, RED, 1.4, dash="3,3")
        s += text(x, ry + 18, lb, 9, RED, "middle", "bold")
    s += arrow(80, ry, xs[0] + bw / 2 - 6, y + 66, RED, 2)
    s += text(112, ry - 22, "↺ до 5 В", 9, RED, "start", "bold")
    s += rect(60, 300, W - 120, 110, "#f6f6f6", GREY, 1.4, 10)
    s += text(W / 2, 326, "Політика pick_pdo(caps): обрати найкращий профіль під потребу", 12, INK, "middle", "bold")
    s += text(W / 2, 350, "1) шукай бажану напругу (12 В) з достатнім струмом    2) нема — бери запасну зі списку (9/15 В)", 10, INK, "middle")
    s += text(W / 2, 370, "3) нема жодної — лишайся на 5 В і сигналь    •    завжди звіряй: чи дає профіль потрібні ампери", 10, INK, "middle")
    s += text(W / 2, 392, "Протокол (GoodCRC, кодування, повтори) веде PD-PHY/контролер — FSM лише ухвалює рішення", 9.5, GREY, "middle", style="italic")
    save("fig-10-3a1-fsm.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🔌 (до теми 10.3.4) — PD-sink тригер
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.3.4c.1 — тригер на платі ─────────────────────────────────────────
def fig_pd_sink_chip():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "PD-sink тригер на платі: контракт без процесора", 18, INK, "middle", "bold")
    # роз'єм
    s += rect(40, 110, 80, 150, "#fbfbf8", INK, 1.8, 8)
    s += text(80, 100, "USB-C", 10, INK, "middle", "bold")
    s += circle(120, 135, 3.5, RED, RED, 0)
    s += text(112, 139, "VBUS", 8, RED, "end", "bold")
    s += circle(120, 175, 3.5, AMBER, AMBER, 0)
    s += text(112, 179, "CC1", 8, AMBER, "end", "bold")
    s += circle(120, 200, 3.5, AMBER, AMBER, 0)
    s += text(112, 204, "CC2", 8, AMBER, "end", "bold")
    s += circle(120, 240, 3.5, INK, INK, 0)
    s += text(112, 244, "GND", 8, INK, "end", "bold")
    # верхній силовий ряд: VBUS → ключ → пристрій
    s += line(120, 135, 300, 135, RED, 2.4)
    s += circle(220, 135, 3, RED, RED, 0)
    s += rect(300, 112, 80, 46, "#fff7e6", AMBER, 1.8, 6)
    s += text(340, 132, "ключ", 9.5, AMBER, "middle", "bold")
    s += text(340, 148, "(FET)", 8, INK, "middle")
    s += line(380, 135, 520, 135, RED, 2.4)
    s += rect(520, 105, 130, 70, "#eef3fb", BLUE, 1.8, 10)
    s += text(585, 134, "пристрій", 11, BLUE, "middle", "bold")
    s += text(585, 152, "12 В по контракту", 8.5, INK, "middle")
    # чип нижче
    s += rect(300, 220, 200, 130, "#eef8ef", GREEN, 2, 10)
    s += text(400, 244, "PD-sink тригер", 11.5, GREEN, "middle", "bold")
    s += text(400, 261, "STUSB4500-клас", 9, INK, "middle")
    s += rect(320, 275, 160, 58, "#fff", GREEN, 1.2, 6)
    s += text(400, 293, "NVM: список PDO", 9, INK, "middle", "bold")
    s += text(400, 309, "12 В → 9 В → 5 В", 9.5, INK, "middle", "bold")
    s += text(400, 326, "+ PD-рушій", 8.5, GREY, "middle")
    # CC роз'єм → чип
    s += line(120, 175, 300, 250, AMBER, 2)
    s += line(120, 200, 300, 268, AMBER, 2)
    s += text(205, 238, "CC1/CC2", 8.5, AMBER, "middle", "bold")
    # VBUS-sense
    s += line(220, 135, 220, 292, RED, 1.8, dash="4,3")
    s += line(220, 292, 300, 292, RED, 1.8, dash="4,3")
    s += text(250, 306, "VBUS-sense", 7.5, RED, "middle")
    # POWER_OK → ключ
    s += line(360, 220, 360, 178, GREEN, 2)
    s += line(360, 178, 340, 178, GREEN, 2)
    s += line(340, 178, 340, 158, GREEN, 2)
    s += text(405, 202, "POWER_OK → ключ", 8, GREEN, "middle", "bold")
    # МК опційно
    s += rect(560, 250, 180, 56, "#f6f6f6", GREY, 1.4, 8)
    s += text(650, 272, "МК (опційно)", 10, INK, "middle", "bold")
    s += text(650, 290, "задати напругу по I²C", 8.5, GREY, "middle")
    s += line(500, 284, 560, 278, BLUE, 1.6, dash="4,3")
    s += text(530, 270, "I²C", 8, BLUE, "middle", "bold")
    # caption
    s += rect(60, 360, W - 120, 56, "#eef8ef", GREEN, 1.5, 10)
    s += text(W / 2, 382, "Чип сам веде все рукостискання PD (тема 10.3.3) і за дійсним контрактом піднімає POWER_OK, що замикає ключ —", 10, INK, "middle")
    s += text(W / 2, 400, "і лише тоді 12 В доходять до пристрою. Список напруг живе в NVM, тож процесор не потрібен; I²C — лише для зміни на ходу.", 10, INK, "middle")
    save("fig-10-4c1-trigger.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Вставка 🔌 (до теми 10.3.6) — Power path у зарядних чипах
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 10.3.6c.1 — power-path чип на платі ─────────────────────────────────
def fig_powerpath_chip():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Зарядний чип із power path: вхід · система · батарея", 18, INK, "middle", "bold")
    # система (зверху)
    s += rect(370, 56, 200, 46, "#eef3fb", BLUE, 1.8, 10)
    s += text(470, 77, "СИСТЕМА (SYS)", 11, BLUE, "middle", "bold")
    s += text(470, 94, "працює одразу від входу", 8.5, INK, "middle")
    # VBUS (ліворуч)
    s += rect(45, 180, 120, 66, "#fbe9e7", RED, 1.8, 10)
    s += text(105, 206, "USB / VBUS", 10.5, RED, "middle", "bold")
    s += text(105, 224, "вхід (ліміт)", 8.5, INK, "middle")
    # батарея (праворуч)
    s += rect(775, 180, 130, 66, "#eef8ef", GREEN, 1.8, 10)
    s += text(840, 206, "БАТАРЕЯ", 10.5, GREEN, "middle", "bold")
    s += text(840, 224, "буфер (BAT)", 8.5, INK, "middle")
    # чип
    s += rect(300, 160, 340, 165, "#fbfbf8", INK, 2, 12)
    s += rect(330, 185, 90, 40, "#eef3fb", BLUE, 1.4, 6)
    s += text(375, 209, "вх. ключ", 9, BLUE, "middle", "bold")
    s += circle(470, 205, 5, AMBER, AMBER, 0)
    s += text(470, 193, "SYS", 9, AMBER, "middle", "bold")
    s += rect(520, 185, 90, 40, "#eef8ef", GREEN, 1.4, 6)
    s += text(565, 209, "бат. ключ", 9, GREEN, "middle", "bold")
    s += line(420, 205, 465, 205, INK, 1.6)
    s += line(475, 205, 520, 205, INK, 1.6)
    s += text(470, 300, "зарядний чип із power path", 10.5, INK, "middle", "bold")
    s += text(470, 316, "(BQ2407x / BQ2419x-клас)", 8.5, GREY, "middle")
    # VBUS → IN
    s += arrow(165, 210, 300, 205, RED, 2.4)
    s += text(235, 198, "IN", 9, RED, "middle", "bold")
    # SYS → система
    s += arrow(470, 185, 470, 104, RED, 2.4)
    s += text(486, 140, "вхід годує", 8.5, RED, "start", "bold")
    s += text(486, 153, "систему НАПРЯМУ", 8.5, RED, "start", "bold")
    # бат. ключ → батарея (залишок)
    s += arrow(610, 200, 775, 205, GREEN, 2.2)
    s += text(692, 192, "залишок → заряд", 8.5, GREEN, "middle", "bold")
    # supplement
    s += arrow(775, 222, 612, 220, AMBER, 1.8, dash="5,4")
    s += text(694, 240, "пік: батарея допомагає", 8.5, AMBER, "middle", "bold")
    # ILIM / ISET / TS
    s += line(375, 325, 375, 350, INK, 1.4)
    s += _res(350, 350, 50, 28, "ILIM", BLUE)
    s += text(375, 392, "ліміт входу", 8, INK, "middle")
    s += line(565, 325, 565, 350, INK, 1.4)
    s += _res(540, 350, 50, 28, "ISET", GREEN)
    s += text(565, 392, "струм заряду", 8, INK, "middle")
    s += line(470, 325, 470, 360, INK, 1.2, dash="3,3")
    s += text(470, 374, "TS термістор", 8, INK, "middle")
    # caption
    s += rect(60, 404, W - 120, 52, "#eef8ef", GREEN, 1.4, 10)
    s += text(W / 2, 424, "Вхід через «вх. ключ» годує SYS напряму — пристрій стартує миттєво навіть із мертвою батареєю. Батарея окремим", 9.5, INK, "middle")
    s += text(W / 2, 439, "ключем бере залишок у заряд, а під пік підкидає струм назад у SYS (supplement). ILIM/ISET задають межі входу й заряду.", 9.5, INK, "middle")
    save("fig-10-6c1-powerpath.svg", s)


if __name__ == "__main__":
    # історія до розділу
    fig_timeline()
    fig_zoo_to_one()
    # тема 10.3.1
    fig_power_ladder()
    fig_connectors()
    fig_usbc_base()
    fig_pd_ladder()
    fig_decouple()
    fig_howmuch()
    # тема 10.3.2
    fig_cc_divider()
    fig_cc_levels()
    fig_cc_roles()
    fig_cc_orientation()
    fig_cc_emarker()
    fig_minimal_sink()
    # тема 10.3.3
    fig_pd_handshake()
    fig_pdos()
    fig_fixed_vs_pps()
    fig_pd_contract()
    fig_epr()
    fig_pd_implement()
    # тема 10.3.4
    fig_paths_hw()
    fig_trigger_anatomy()
    fig_no_contract()
    fig_wide_input()
    fig_mcu_runtime()
    fig_decision_guide()
    # тема 10.3.5
    fig_why_dumb_charger()
    fig_port_types()
    fig_dcp_short()
    fig_bc12_flow()
    fig_proprietary_codes()
    fig_two_worlds()
    # тема 10.3.6
    fig_sink_to_source()
    fig_otg_boost()
    fig_dual_role()
    fig_power_path()
    fig_load_sharing()
    fig_good_source()
    # тема 10.3.7
    fig_cable_anatomy()
    fig_emarker_role()
    fig_voltage_drop()
    fig_incompat_map()
    fig_diagnosis_flow()
    fig_field_robust()
    # вставка 🧮 cable-drop
    fig_cabledrop_model()
    fig_cabledrop_table()
    # вставка 🔌 cc-resistors
    fig_cc_resistors()
    # вставка ⚙️ pd-state-machine
    fig_pd_fsm()
    # вставка 🔌 pd-sink тригер
    fig_pd_sink_chip()
    # вставка 🔌 power-path
    fig_powerpath_chip()
    print("done r03 figures")
