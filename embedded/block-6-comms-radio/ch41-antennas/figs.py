# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 41 — «Антени й лінії передачі» (Модуль 6).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; хвиля синя, провід/антена темні, земля коричнева,
висновок зелений, спірне/міф червоні. Підписи посекційно; історія — секція 0 (41.0.N).
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
AMBER = "#b08900"
SPARK = "#e8b53a"
METAL = "#9a9aa0"
EARTH = "#8a6a3a"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fbf3df"
LGREY = "#f3f3f3"
LEAR  = "#f0e7d8"
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
        f'  <marker id="aAmb" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey", AMBER: "aAmb"}


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


def _poly(pts, color, w):
    return ('<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            + f'" fill="none" stroke="{color}" stroke-width="{w}"/>\n')


def sine(x0, y0, length, amp, periods, color, w=2.4, phase=0.0):
    pts = []
    n = max(60, int(length / 2))
    for i in range(n + 1):
        t = i / n
        x = x0 + t * length
        y = y0 - amp * math.sin(2 * math.pi * periods * t + phase)
        pts.append((x, y))
    return _poly(pts, color, w)


def _stem(x, y_base, h, color, w=3):
    return line(x, y_base, x, y_base - h, color, w)


def arc(cx, cy, r, a0, a1, color, w=2, dash=None):
    a0r, a1r = math.radians(a0), math.radians(a1)
    x0, y0 = cx + r * math.cos(a0r), cy + r * math.sin(a0r)
    x1, y1 = cx + r * math.cos(a1r), cy + r * math.sin(a1r)
    large = 1 if abs(a1 - a0) > 180 else 0
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M {x0:.1f},{y0:.1f} A {r:.1f} {r:.1f} 0 {large} 1 {x1:.1f},{y1:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n')


def spark(cx, cy, r=12, col=SPARK, w=2.0):
    pts = []
    for k in range(8):
        ang = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    path = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _ground(x0, x1, y, col=EARTH):
    s = line(x0, y, x1, y, col, 2.5)
    for x in range(int(x0) + 10, int(x1), 26):
        s += line(x, y, x - 9, y + 11, col, 1.6)
    return s


# ============================================================================
#  Історія до Розділу 41 — Марконі через Атлантику (секція 0)
# ============================================================================

# ── Рис. 41.0.1 — таймлайн колективного винаходу ─────────────────────────────
def figh_timeline():
    W, H = 940, 660
    s = header(W, H)
    s += text(W / 2, 36, "Як радіо стало далеким — і чому це праця багатьох", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "Марконі дотягнув хвилю через океан, але «винайшли радіо» десятки людей у різних країнах",
              12, GREY, "middle", style="italic")
    spine = 300
    top, bot = 92, H - 24
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1887", "Герц", "Доводить, що електромагнітні хвилі існують (Розділ 39)", "sci"),
        ("1890", "Бранлі", "Когерер — перший чутливий детектор хвиль (Франція)", "sci"),
        ("1894", "Бозе й Лодж", "Бозе в Калькутті дзвонить у дзвоник по радіо; Лодж сигналить і вводить настройку", "sci"),
        ("1895", "Попов і Марконі", "Попов (7 травня, Росія) — приймач-грозовідмітник; Марконі — перші передачі, заземлена антена", "sci"),
        ("1901", "Марконі: «через Атлантику»", "Чує «S» з Корнуоллу в Ньюфаундленді — гучний, але СПІРНИЙ дослід", "claim"),
        ("1909", "Нобель", "Марконі й Braun — за внесок у радіотелеграф (разом!)", "win"),
        ("1943", "Верховний суд США", "Скасовує широкий патент Марконі: раніше були Stone, Лодж, Тесла", "court"),
    ]
    n = len(nodes)
    for i, (yr, who, q, kind) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        if kind == "win":
            s += circle(spine, y, 9, "#fff", GREEN, 3)
            s += circle(spine, y, 4, GREEN, GREEN, 0)
            wc = GREEN
        elif kind == "claim":
            s += rect(spine - 8, y - 8, 16, 16, "#fff", AMBER, 2.6, 3)
            wc = AMBER
        elif kind == "court":
            s += rect(spine - 8, y - 8, 16, 16, "#fff", RED, 2.6, 3)
            wc = RED
        else:
            s += circle(spine, y, 7, "#fff", BLUE, 2.6)
            wc = BLUE
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 2, who, 15, wc, "start", "bold")
        s += text(spine + 26, y + 18, q, 11, INK, "start", style="italic")
    save("fig-41-0-1-timeline.svg", s)


# ── Рис. 41.0.2 — стрибок дальності прийшов від антени ───────────────────────
def figh_antenna_leap():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "Головний секрет дальності — АНТЕНА", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Герц мав крихітний диполь на метри; Марконі взяв велику заземлену антену — і дотягнув на милі",
              11.5, GREY, "middle", style="italic")
    gy = 320
    # Герц — малий диполь
    s += text(230, 100, "Герц: лабораторний диполь", 12, BLUE, "middle", "bold")
    s += line(190, 200, 270, 200, INK, 3)
    s += circle(190, 200, 7, "none", INK, 2)
    s += circle(270, 200, 7, "none", INK, 2)
    s += spark(230, 200, 8, SPARK, 1.8)
    s += sine(230, 160, 120, 10, 3, BLUE, 1.4)
    s += text(230, 250, "кілька метрів", 11, RED, "middle", "bold")
    s += _ground(120, 340, gy)
    # Марконі — велика заземлена
    s += text(680, 100, "Марконі: висока заземлена антена", 12, GREEN, "middle", "bold")
    s += line(680, gy, 680, 130, METAL, 4)
    s += line(640, 130, 720, 130, METAL, 3)  # верхній «капелюх»
    for dx in (-30, -10, 10, 30):
        s += line(680, 130, 680 + dx, 116, METAL, 1.4)
    s += line(680, gy, 680, gy + 8, EARTH, 3)  # заземлення
    s += text(700, gy + 4, "земля", 9.5, EARTH, "start", "bold")
    for r in (40, 70, 100):
        s += arc(680, 150, r, -150, -30, BLUE, 1.4)
    s += text(680, 250, "милі, потім — океан", 11, GREEN, "middle", "bold")
    s += _ground(520, 860, gy)
    s += rect(60, 350, W - 120, 40, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 374, "Велика антена + заземлення + довша хвиля = величезна дальність. Саме цьому присвячено Розділ 41.",
              11.5, INK, "middle", "bold")
    save("fig-41-0-2-antenna-leap.svg", s)


# ── Рис. 41.0.3 — 1901: через Атлантику ──────────────────────────────────────
def figh_transatlantic():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "12 грудня 1901: сигнал «S» нібито перетнув Атлантику", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "Полдгу (Корнуолл) → Сигнал-Гілл (Ньюфаундленд), ~3500 км, антена на повітряному змії",
              11, GREY, "middle", style="italic")
    # дуга Землі
    cx, cy, R = W / 2, 1150, 900
    s += arc(cx, cy, R, -135, -45, EARTH, 3)
    # Корнуолл (праворуч), Ньюфаундленд (ліворуч)
    ax = cx + R * math.cos(math.radians(-58))
    ay = cy + R * math.sin(math.radians(-58))
    bx = cx + R * math.cos(math.radians(-122))
    by = cy + R * math.sin(math.radians(-122))
    s += line(ax, ay, ax, ay - 60, METAL, 3)
    s += text(ax + 8, ay - 64, "Полдгу (TX)", 11, BLUE, "start", "bold")
    s += text(ax + 8, ay - 50, "велика щогла", 9, GREY, "start")
    s += line(bx, by, bx, by - 70, METAL, 2)
    s += text(bx - 8, by - 74, "Сигнал-Гілл (RX)", 11, GREEN, "end", "bold")
    s += text(bx - 8, by - 60, "антена на змії", 9, GREY, "end")
    # змій
    s += rect(bx - 18, by - 110, 16, 16, LGRN, GREEN, 1.4)
    # дуга сигналу над водою
    s += arc((ax + bx) / 2, 560, 320, -148, -32, BLUE, 2, "6 4")
    s += text((ax + bx) / 2, 150, "хвиля «через горб» Землі", 11, BLUE, "middle", "bold")
    s += text((ax + bx) / 2, 250, "«S» = · · · (три крапки)", 13, INK, "middle", "bold")
    s += text((ax + bx) / 2, 330, "Атлантичний океан", 10.5, EARTH, "middle", style="italic")
    save("fig-41-0-3-transatlantic.svg", s)


# ── Рис. 41.0.4 — спірність досліду ──────────────────────────────────────────
def figh_controversy():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чесно: чи справді він це почув?", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "славетний дослід 1901 року й досі лишається СПІРНИМ — варто знати чому",
              12, GREY, "middle", style="italic")
    doubts = [
        ("🎧", "Лише він у навушниках", "Жодного незалежного свідка: «S» чув тільки сам Марконі."),
        ("📼", "Жодного запису", "Нічого не зафіксували — ні приладу, ні протоколу сигналу."),
        ("⚡", "Можливо, просто шум", "Едісон та інші: це могли бути атмосферні розряди, а не сигнал."),
        ("🌍", "Фізика проти", "Удень на тій хвилі сигнал навряд чи дійшов би — іоносферу ще не знали."),
    ]
    y = 92
    for ico, t, d in doubts:
        s += rect(60, y, W - 120, 56, "#fbfbfb", AMBER, 1.5, 9)
        s += text(92, y + 35, ico, 20, INK, "middle")
        s += text(124, y + 24, t, 12.5, AMBER, "start", "bold")
        s += text(124, y + 44, d, 11, INK, "start")
        y += 66
    s += text(W / 2, 366, "Це не применшує Марконі — лише нагадує: гучна заява потребує доказів. Пізніші передачі (1902+) надійніші.",
              10.5, GREY, "middle", style="italic")
    save("fig-41-0-4-controversy.svg", s)


# ── Рис. 41.0.5 — колективний винахід ────────────────────────────────────────
def figh_collective():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 34, "Радіо винайшли БАГАТО людей у різних країнах", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "немає одного «винахідника радіо» — кожен додав свою ланку",
              12, GREY, "middle", style="italic")
    people = [
        ("Герц", "Німеччина", "довів існування хвиль (1887)"),
        ("Бранлі", "Франція", "когерер — детектор хвиль"),
        ("Лодж", "Британія", "настройка (syntony), сигнали"),
        ("Бозе", "Індія", "детектор; сигнали 1894 — НЕ патентував"),
        ("Попов", "Росія", "приймач 1895 (реальний внесок)"),
        ("Тесла", "США/Серб.", "коливальні контури, патенти"),
        ("Стоун / Braun", "США / Нім.", "настройка; далекий зв'язок, Нобель"),
        ("Марконі", "Італія", "система, антена, дальність, бізнес"),
    ]
    cols = 4
    cw, ch = 215, 92
    x0, y0 = 30, 86
    for i, (nm, country, what) in enumerate(people):
        cx = x0 + (i % cols) * (cw + 8)
        cy = y0 + (i // cols) * (ch + 14)
        col = GREEN if nm == "Марконі" else BLUE
        s += rect(cx, cy, cw, ch, "#fbfbfb", col, 1.8, 10)
        s += text(cx + cw / 2, cy + 26, nm, 13.5, col, "middle", "bold")
        s += text(cx + cw / 2, cy + 45, country, 10, GREY, "middle", style="italic")
        words = what.split()
        ln, yy = "", cy + 64
        for wd in words:
            if len(ln) + len(wd) > 26:
                s += text(cx + cw / 2, yy, ln.strip(), 9.8, INK, "middle")
                ln, yy = "", yy + 15
            ln += wd + " "
        s += text(cx + cw / 2, yy, ln.strip(), 9.8, INK, "middle")
    s += text(W / 2, 408, "Марконі — не самотній геній, а блискучий ІНЖЕНЕР-СИСТЕМНИК, що звів чужі цеглинки в робочу далеку лінію.",
              11, INK, "middle", "bold")
    save("fig-41-0-5-collective.svg", s)


# ── Рис. 41.0.6 — суд 1943 і міф ─────────────────────────────────────────────
def figh_court_myth():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 34, "Суд 1943 року: що він СПРАВДІ постановив", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "розповсюджений міф проти точного факту — добра нагода звірити джерела",
              12, GREY, "middle", style="italic")
    # міф
    s += rect(50, 86, 400, 220, LRED, RED, 1.8, 12)
    s += text(250, 116, "МІФ", 15, RED, "middle", "bold")
    for i, ln in enumerate([
        "«Верховний суд США 1943 року",
        "визнав, що радіо винайшов Тесла,",
        "а не Марконі.»",
        "",
        "Так часто пишуть — але це",
        "спрощення того, що сталося.",
    ]):
        s += text(250, 146 + i * 25, ln, 11, INK, "middle")
    s += arrow(455, 196, 485, 196, INK, 2.2)
    # факт
    s += rect(490, 86, 400, 220, LGRN, GREEN, 1.8, 12)
    s += text(690, 116, "ФАКТ", 15, GREEN, "middle", "bold")
    for i, ln in enumerate([
        "Суд скасував ШИРОКИЙ патент",
        "Марконі — бо те саме раніше",
        "зробили Stone, Лодж і Тесла.",
        "",
        "Суд НЕ призначав «винахідника",
        "радіо». Спір був про оплату",
        "державою патентів часів війни.",
    ]):
        s += text(690, 146 + i * 23, ln, 10.6, INK, "middle")
    save("fig-41-0-6-court-myth.svg", s)


# ── Рис. 41.0.7 — що з цього лишилось ────────────────────────────────────────
def figh_legacy():
    W, H = 920, 330
    s = header(W, H)
    s += text(W / 2, 34, "Що лишилось — і чому це веде нас до антен", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "урок про колективність винаходу — і конкретний місток у тему розділу",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("🌍", "Радіо — колективне", "Жодного одного «винахідника»; визнаймо й забутих — Бозе, Попова, Лоджа.", BLUE),
        ("📡", "Геній Марконі — антена", "Його реальна сила: велика заземлена антена, система й завзяття — дальність.", GREEN),
        ("🔭", "Іоносфера", "Хвилю «за горб» відбиває шар іонів угорі — його відкрили вже після 1901-го.", AMBER),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 86, 277, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 138, 126, ico, 23, INK, "middle")
        s += text(x + 138, 156, title, 13, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 186
        for wd in words:
            if len(ln) + len(wd) > 30:
                s += text(x + 138, yy, ln.strip(), 10.3, INK, "middle")
                ln, yy = "", yy + 18
            ln += wd + " "
        s += text(x + 138, yy, ln.strip(), 10.3, INK, "middle")
        x += 290
    save("fig-41-0-7-legacy.svg", s)


# ============================================================================
#  §41.1 — Антена: перетворити струм у хвилю
# ============================================================================

# ── Рис. 41.1.1 — антена як «розкрите» коло ──────────────────────────────────
def fig11_open_circuit():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Антена — це навмисно «розкрите» коло", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у тісному колі поля замкнені всередині; розсуньмо провідники — і поля відриваються в простір",
              11.5, GREY, "middle", style="italic")
    # закрите коло
    s += text(230, 100, "тісне коло", 12.5, BLUE, "middle", "bold")
    s += rect(170, 140, 120, 90, "none", INK, 2.4, 6)
    s += circle(170, 185, 7, "none", RED, 2)
    s += text(150, 189, "~", 12, RED, "end", "bold")
    for r in (16, 26):
        s += circle(230, 185, r, "none", BLUE, 1)
    s += text(230, 260, "поля замкнені → не випромінює", 10, RED, "middle", "bold")
    # розкрите коло (диполь)
    s += text(690, 100, "розкрите коло (антена)", 12.5, GREEN, "middle", "bold")
    s += line(690, 140, 690, 170, INK, 3)
    s += line(690, 200, 690, 230, INK, 3)
    s += circle(690, 185, 6, "none", RED, 2)
    s += text(668, 189, "~", 12, RED, "end", "bold")
    for r in (30, 55, 80):
        s += arc(690, 155, r, -150, -30, BLUE, 1.4)
        s += arc(690, 215, r, 30, 150, BLUE, 1.4)
    s += text(690, 270, "поля відриваються й летять геть", 10, GREEN, "middle", "bold")
    s += rect(60, 300, W - 120, 50, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 324, "Антена — це коло, навмисне «відкрите» так, щоб електромагнітна енергія не лишалася всередині,",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 343, "а зривалася в простір вільною хвилею. Решта розділу — про те, як зробити це ефективно.",
              11, GREY, "middle", style="italic")
    save("fig-41-1-1-open-circuit.svg", s)


# ── Рис. 41.1.2 — трясемо заряди → хвиля ─────────────────────────────────────
def fig12_shake_charges():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Як народжується хвиля: змінний струм трясе заряди", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "жени по дроту змінний струм — заряди прискорюються вгору-вниз — і випромінюють хвилю (§39.1)",
              11, GREY, "middle", style="italic")
    ax = 260
    # антена-дріт
    s += line(ax, 110, ax, 300, METAL, 5)
    s += circle(ax, 320, 12, "none", RED, 2)
    s += text(ax, 325, "~", 14, RED, "middle", "bold")
    s += line(ax, 300, ax, 308, METAL, 3)
    # заряди + стрілки прискорення
    s += text(ax, 130, "+", 18, RED, "middle", "bold")
    s += arrow(ax + 18, 150, ax + 18, 120, RED, 2)
    s += text(ax - 14, 290, "−", 18, BLUE, "middle", "bold")
    s += arrow(ax + 18, 270, ax + 18, 300, BLUE, 2)
    s += text(ax + 40, 205, "заряди гойдаються", 10.5, INK, "start", "bold")
    s += text(ax + 40, 222, "вгору-вниз", 10.5, GREY, "start")
    # хвиля
    for r in (60, 110, 160, 210):
        s += arc(ax, 205, r, -75, 75, BLUE, 1.6)
    s += text(620, 130, "хвиля летить геть", 12, BLUE, "middle", "bold")
    s += rect(60, 336, W - 120, 30, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 356, "Передавання = перетворити коливний струм на хвилю. Приймання — навпаки (далі).",
              11.5, INK, "middle", "bold")
    save("fig-41-1-2-shake-charges.svg", s)


# ── Рис. 41.1.3 — розподіл струму на півхвильовому диполі ─────────────────────
def fig13_dipole_current():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Півхвильовий диполь: де струм, а де напруга", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "на антені стоїть хвиля струму: максимум — у центрі (живлення), нуль — на кінцях",
              11.5, GREY, "middle", style="italic")
    cx, cy = W / 2, 180
    arm = 280
    # диполь
    s += line(cx - arm, cy, cx - 14, cy, METAL, 6)
    s += line(cx + 14, cy, cx + arm, cy, METAL, 6)
    s += circle(cx, cy, 6, "none", RED, 2)
    s += text(cx, cy + 26, "живлення", 10, RED, "middle", "bold")
    s += line(cx - arm, cy - 90, cx + arm, cy - 90, FAINT, 1)
    # крива струму (максимум центр)
    pts = []
    for i in range(81):
        t = i / 80
        x = cx - arm + t * 2 * arm
        amp = math.cos((t - 0.5) * math.pi)
        pts.append((x, cy - 20 - amp * 70))
    s += _poly(pts, BLUE, 2.6)
    s += text(cx, cy - 110, "струм I (max у центрі)", 11.5, BLUE, "middle", "bold")
    # крива напруги (максимум кінці)
    pts2 = []
    for i in range(81):
        t = i / 80
        x = cx - arm + t * 2 * arm
        amp = math.sin((t - 0.5) * math.pi)
        pts2.append((x, cy + 30 + amp * 55))
    s += _poly(pts2, GREEN, 2.2)
    s += text(cx, cy + 120, "напруга V (max на кінцях)", 11, GREEN, "middle", "bold")
    s += text(cx - arm, cy + 16, "λ/4", 10, GREY, "middle")
    s += text(cx + arm, cy + 16, "λ/4", 10, GREY, "middle")
    s += text(cx, 348, "Повна довжина — близько λ/2; чому саме так, розберемо в наступній темі.", 10.5, GREY, "middle", style="italic")
    save("fig-41-1-3-dipole-current.svg", s)


# ── Рис. 41.1.4 — антена як перетворювач ─────────────────────────────────────
def fig14_transducer():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Антена — перетворювач: ведений струм ↔ вільна хвиля", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "як гучномовець перетворює струм на звук, так антена перетворює струм на радіохвилю",
              11, GREY, "middle", style="italic")
    # ліворуч — струм по дроту
    s += sine(70, 150, 180, 22, 4, RED, 2)
    s += text(160, 110, "струм по дроту", 11, RED, "middle", "bold")
    s += text(160, 200, "(ведена енергія)", 9.5, GREY, "middle")
    s += arrow(255, 150, 300, 150, INK, 2.2)
    # антена
    s += line(340, 100, 340, 200, METAL, 5)
    s += text(340, 224, "антена", 11, INK, "middle", "bold")
    s += arrow(380, 150, 425, 150, INK, 2.2)
    # праворуч — хвиля
    for r in (30, 55, 80):
        s += arc(440, 150, r, -70, 70, BLUE, 1.6)
    s += text(560, 110, "хвиля у просторі", 11, BLUE, "middle", "bold")
    s += text(560, 200, "(вільна енергія)", 9.5, GREY, "middle")
    # аналогія
    s += rect(660, 96, 210, 120, LGREY, GREY, 1.4, 10)
    s += text(765, 122, "та сама ідея:", 11, INK, "middle", "bold")
    s += text(765, 146, "гучномовець", 11.5, GREEN, "middle", "bold")
    s += text(765, 166, "струм → звук", 10, GREY, "middle")
    s += text(765, 190, "антена", 11.5, GREEN, "middle", "bold")
    s += text(765, 208, "струм → радіохвиля", 10, GREY, "middle")
    s += rect(60, 300, 580, 36, LBLUE, BLUE, 1.3, 8)
    s += text(350, 323, "Перетворювач в обидва боки: те, що випромінює, те й приймає.", 11.5, INK, "middle", "bold")
    save("fig-41-1-4-transducer.svg", s)


# ── Рис. 41.1.5 — опір випромінювання ────────────────────────────────────────
def fig15_rad_resistance():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Опір випромінювання: куди дівається потужність", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "для передавача антена «виглядає» як опір — але енергія не гріє, а ВИПРОМІНЮЄТЬСЯ",
              11.5, GREY, "middle", style="italic")
    # джерело
    s += circle(160, 180, 22, "none", RED, 2)
    s += text(160, 186, "~", 16, RED, "middle", "bold")
    s += text(160, 220, "передавач", 10.5, INK, "middle", "bold")
    s += line(182, 180, 280, 180, INK, 2.4)
    # «резистор» = антена
    s += rect(280, 162, 90, 36, LAMB, AMBER, 2, 4)
    s += text(325, 185, "R_вип", 12.5, AMBER, "middle", "bold")
    s += text(325, 220, "≈ 73 Ом (диполь)", 9.5, GREY, "middle")
    s += line(370, 180, 430, 180, INK, 2.4)
    s += line(430, 150, 430, 210, METAL, 4)
    # хвиля геть
    for r in (30, 55, 80):
        s += arc(430, 180, r, -70, 70, BLUE, 1.5)
    s += text(560, 140, "потужність ЙДЕ у простір", 11, BLUE, "middle", "bold")
    s += text(560, 230, "P_вип = I² · R_вип", 13, GREEN, "middle", "bold")
    s += rect(60, 290, W - 120, 44, LGRN, GREEN, 1.3, 9)
    s += text(W / 2, 313, "«Резистор», що не гріється, а світить у простір. Опір диполя ≈ 73 Ом — звідси й знамениті 50 Ом (§41.5).",
              11, INK, "middle", "bold")
    save("fig-41-1-5-rad-resistance.svg", s)


# ── Рис. 41.1.6 — взаємність ─────────────────────────────────────────────────
def fig16_reciprocity():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Взаємність: та сама антена передає й приймає", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "патерн, виграш, резонанс — однакові в обидва боки; одна антена годиться і для TX, і для RX",
              11, GREY, "middle", style="italic")
    # TX
    s += rect(60, 86, 380, 210, "#fbfbfb", RED, 1.8, 10)
    s += text(250, 112, "Передавання (TX)", 13, RED, "middle", "bold")
    s += line(150, 150, 150, 250, METAL, 4)
    s += circle(150, 270, 10, "none", RED, 2)
    s += text(150, 275, "~", 12, RED, "middle", "bold")
    for r in (30, 55, 80):
        s += arc(150, 200, r, -70, 70, BLUE, 1.5)
    s += text(330, 200, "струм → хвиля", 11, INK, "middle", "bold")
    # RX
    s += rect(460, 86, 380, 210, "#fbfbfb", GREEN, 1.8, 10)
    s += text(650, 112, "Приймання (RX)", 13, GREEN, "middle", "bold")
    s += line(750, 150, 750, 250, METAL, 4)
    s += circle(750, 270, 10, "none", GREEN, 2)
    for r in (30, 55, 80):
        s += arc(750, 200, r, 110, 250, BLUE, 1.5)
    s += text(580, 200, "хвиля → струм", 11, INK, "middle", "bold")
    s += text(W / 2, 322, "Це принцип взаємності: антена — симетричний перетворювач, і її властивості тотожні для обох напрямів.",
              11, INK, "middle", "bold")
    save("fig-41-1-6-reciprocity.svg", s)


# ── Рис. 41.1.7 — ближнє й дальнє поле ───────────────────────────────────────
def fig17_near_far():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Ближнє й дальнє поле: що саме «летить»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "біля антени енергія ще «хлюпає» туди-сюди; справжня хвиля формується далі — це дальнє поле",
              11, GREY, "middle", style="italic")
    cx, cy = 250, 190
    s += line(cx, cy - 70, cx, cy + 70, METAL, 5)
    # ближнє поле
    s += circle(cx, cy, 60, "#fdf3f3", RED, 1.6)
    s += text(cx, cy - 80, "ближнє поле", 10.5, RED, "middle", "bold")
    s += text(cx, cy + 92, "(енергія хлюпає, ~< λ/6)", 9, GREY, "middle")
    # дальнє поле
    for r in (110, 150, 190):
        s += arc(cx, cy, r, -65, 65, BLUE, 1.6)
    s += text(560, 120, "дальнє поле — справжня хвиля", 11.5, BLUE, "middle", "bold")
    s += text(560, 140, "(те, що долітає до приймача)", 9.5, GREY, "middle")
    s += rect(440, 165, 360, 50, LBLUE, BLUE, 1.3, 9)
    s += text(620, 187, "Корисний радіозв'язок — це завжди", 10.5, INK, "middle", "bold")
    s += text(620, 205, "дальнє поле антени.", 10.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Ближнє поле важливе для розмірів антени й зв'язку «впритул» (NFC), та сигнал у простір несе дальнє.",
              10, GREY, "middle", style="italic")
    save("fig-41-1-7-near-far.svg", s)


# ============================================================================
#  §41.2 — Резонанс і довжина: чверть хвилі, диполь
# ============================================================================

# ── Рис. 41.2.1 — антена резонує, як струна ──────────────────────────────────
def fig21_string():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Антена має резонансну довжину — як струна чи труба", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "хвиля «вкладається» в антену тільки за певної довжини; тоді коливання найсильніше",
              11.5, GREY, "middle", style="italic")
    # струна
    s += text(220, 100, "струна, закріплена з кінців", 11.5, BLUE, "middle", "bold")
    s += line(90, 150, 350, 150, GREY, 1, "4 3")
    s += circle(90, 150, 5, INK, INK, 0)
    s += circle(350, 150, 5, INK, INK, 0)
    s += _poly([(90 + i * 260 / 60, 150 - 40 * math.sin(math.pi * i / 60)) for i in range(61)], BLUE, 2.4)
    s += _poly([(90 + i * 260 / 60, 150 + 40 * math.sin(math.pi * i / 60)) for i in range(61)], BLUE, 1.2)
    s += text(220, 210, "пів хвилі вкладається → резонанс", 10, GREY, "middle")
    # антена
    s += text(680, 100, "півхвильовий диполь", 11.5, GREEN, "middle", "bold")
    s += line(550, 150, 666, 150, METAL, 5)
    s += line(694, 150, 810, 150, METAL, 5)
    s += circle(680, 150, 5, "none", RED, 2)
    s += _poly([(550 + i * 260 / 60, 150 - 42 * math.sin(math.pi * i / 60)) for i in range(61)], GREEN, 2.4)
    s += text(680, 210, "пів хвилі струму → резонанс", 10, GREY, "middle")
    s += rect(60, 300, W - 120, 56, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 324, "Резонанс — те саме явище, що в коливальному контурі (Розділ 9): на «своїй» частоті відгук максимальний.",
              11, INK, "middle", "bold")
    s += text(W / 2, 344, "Для антени «своя» частота задається її довжиною відносно λ.", 10.5, GREY, "middle", style="italic")
    save("fig-41-2-1-string.svg", s)


# ── Рис. 41.2.2 — півхвильовий диполь і скасування реактивності ──────────────
def fig22_halfwave():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Півхвильовий диполь (λ/2): на резонансі реактивність зникає", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "розподілені ємність та індуктивність дроту гасять одна одну → лишається чистий опір ≈ 73 Ом",
              11, GREY, "middle", style="italic")
    cx, cy = W / 2, 150
    arm = 250
    s += line(cx - arm, cy, cx - 12, cy, METAL, 6)
    s += line(cx + 12, cy, cx + arm, cy, METAL, 6)
    s += circle(cx, cy, 6, "none", RED, 2)
    # дужки довжин
    s += line(cx - arm, cy + 30, cx + arm, cy + 30, GREY, 1.2)
    s += line(cx - arm, cy + 25, cx - arm, cy + 35, GREY, 1.2)
    s += line(cx + arm, cy + 25, cx + arm, cy + 35, GREY, 1.2)
    s += text(cx, cy + 48, "повна довжина ≈ λ/2", 12, INK, "middle", "bold")
    s += line(cx - arm, cy - 30, cx, cy - 30, GREY, 1.2)
    s += text(cx - arm / 2, cy - 38, "λ/4", 10.5, GREY, "middle", "bold")
    s += text(cx + arm / 2, cy - 38, "λ/4", 10.5, GREY, "middle", "bold")
    # резонанс
    s += rect(170, 230, 250, 90, LBLUE, BLUE, 1.5, 9)
    s += text(295, 256, "не на резонансі:", 11, INK, "middle", "bold")
    s += text(295, 278, "є реактивність (X ≠ 0)", 10.5, RED, "middle")
    s += text(295, 300, "→ передавачу важко", 10, GREY, "middle")
    s += rect(480, 230, 250, 90, LGRN, GREEN, 1.5, 9)
    s += text(605, 256, "на резонансі (λ/2):", 11, INK, "middle", "bold")
    s += text(605, 278, "X = 0, лише R ≈ 73 Ом", 10.5, GREEN, "middle", "bold")
    s += text(605, 300, "→ живиться легко й ефективно", 10, GREY, "middle")
    save("fig-41-2-2-halfwave.svg", s)


# ── Рис. 41.2.3 — чвертьхвильовий штир і «дзеркало» землі ─────────────────────
def fig23_quarterwave():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чвертьхвильовий штир (λ/4): земля добудовує другу половину", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "штир λ/4 над провідною землею «віддзеркалюється» в неї — і працює як половина диполя",
              11, GREY, "middle", style="italic")
    gy = 230
    cx = W / 2
    # земля
    s += _ground(cx - 280, cx + 280, gy)
    s += text(cx + 250, gy + 26, "земля / GND", 10, EARTH, "middle", "bold")
    # реальний штир
    s += line(cx, gy, cx, gy - 130, METAL, 5)
    s += text(cx + 16, gy - 130, "штир λ/4", 11, GREEN, "start", "bold")
    s += circle(cx, gy - 4, 5, "none", RED, 2)
    # дзеркальне зображення
    s += line(cx, gy, cx, gy + 130, METAL, 2, "5 4")
    s += text(cx + 16, gy + 120, "«дзеркало» (уявне λ/4)", 10, GREY, "start", style="italic")
    # хвилі
    for r in (50, 85, 120):
        s += arc(cx, gy - 65, r, -150, -30, BLUE, 1.3)
    s += rect(60, 300, W - 120, 60, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 324, "Це і є антена Марконі — і та сама на авто, роутері, рації, телефоні: коротка, бо землю «позичає».",
              11, INK, "middle", "bold")
    s += text(W / 2, 344, "Опір такого штиря ≈ 36 Ом (половина диполя). Земля (чи «противага») тут обов'язкова.",
              10.5, GREY, "middle", style="italic")
    save("fig-41-2-3-quarterwave.svg", s)


# ── Рис. 41.2.4 — довжина антени від частоти ─────────────────────────────────
def fig24_length_table():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Розмір антени напряму залежить від частоти", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "λ = c / f, далі беремо λ/4 (штир) або λ/2 (диполь); ось чому антени такі різні",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("FM-радіо", "100 МГц", "3 м", "λ/2 ≈ 1.5 м", "велика щогла/диполь"),
        ("LoRa (ЄС)", "868 МГц", "35 см", "λ/4 ≈ 8.6 см", "штир-«вус»"),
        ("433 МГц пульт", "433 МГц", "69 см", "λ/4 ≈ 17 см", "довгий дріт"),
        ("Wi-Fi / BT", "2.4 ГГц", "12.5 см", "λ/4 ≈ 3.1 см", "коротка паличка"),
    ]
    x0, y0 = 70, 92
    ws = [180, 120, 110, 150, 230]
    heads = ["система", "частота", "λ", "розмір антени", "вигляд"]
    cx = x0
    for h, w_ in zip(heads, ws):
        s += rect(cx, y0, w_, 34, "#f0f0f0", GREY, 1.3)
        s += text(cx + w_ / 2, y0 + 23, h, 11, INK, "middle", "bold")
        cx += w_
    yy = y0 + 34
    for sysn, f, lam, ant, look in rows:
        cx = x0
        vals = [(sysn, INK, "bold"), (f, BLUE, "bold"), (lam, GREY, "normal"), (ant, GREEN, "bold"), (look, INK, "normal")]
        for (val, col, wt), w_ in zip(vals, ws):
            s += rect(cx, yy, w_, 40, "#fff", "#e2e2e2", 1)
            s += text(cx + w_ / 2, yy + 26, val, 10.5, col, "middle", ("bold" if wt == "bold" else "normal"))
            cx += w_
        yy += 40
    s += text(W / 2, yy + 26, "Практична поправка: реальна резонансна довжина на ~5% коротша (крайові ефекти).",
              10.5, GREY, "middle", style="italic")
    save("fig-41-2-4-length-table.svg", s)


# ── Рис. 41.2.5 — не та довжина = втрати ─────────────────────────────────────
def fig25_off_resonance():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Неправильна довжина — антена «не резонує»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "закоротка → ємнісна, задовга → індуктивна; в обох випадках частину потужності відбито назад",
              11, GREY, "middle", style="italic")
    panels = [
        ("закоротка", "ємнісна (−jX)", "погано випромінює", RED, 70),
        ("саме λ/4 (λ/2)", "чистий R ≈ 73/36 Ом", "максимум випромінювання", GREEN, 110),
        ("задовга", "індуктивна (+jX)", "знову відбиття", RED, 70),
    ]
    x = 60
    for nm, react, eff, col, hh in panels:
        s += rect(x, 92, 250, 180, "#fbfbfb", col, 2, 10)
        s += line(x + 125, 250, x + 125, 250 - hh, METAL, 5)
        s += text(x + 125, 128, nm, 12.5, col, "middle", "bold")
        s += text(x + 125, 280, react, 10.5, INK, "middle", "bold")
        s += text(x + 125, 298, eff, 9.5, GREY, "middle")
        x += 270
    s += text(W / 2, 332, "Відбита потужність повертається в передавач — про це й «коефіцієнт стійної хвилі» (КСХ) далі.",
              10.5, GREY, "middle", style="italic")
    save("fig-41-2-5-off-resonance.svg", s)


# ── Рис. 41.2.6 — електрично короткі антени ──────────────────────────────────
def fig26_loading():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Коли λ/4 не влазить: «електрично короткі» антени", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "котушка чи звивиста доріжка роблять коротку антену резонансною — ціною ефективності",
              11, GREY, "middle", style="italic")
    gy = 250
    # повна λ/4
    s += text(160, 100, "повна λ/4", 11.5, GREEN, "middle", "bold")
    s += line(160, gy, 160, gy - 140, METAL, 5)
    s += text(160, gy + 22, "ефективна, але довга", 9.5, GREY, "middle")
    # котушка (rubber duck)
    s += text(420, 100, "з котушкою (rubber duck)", 11, BLUE, "middle", "bold")
    s += line(420, gy, 420, gy - 50, METAL, 5)
    yy = gy - 50
    for k in range(6):
        s += arc(420, yy - 4 - k * 8, 9, 0, 360, BLUE, 1.8)
    s += line(420, gy - 100, 420, gy - 120, METAL, 5)
    s += text(420, gy + 22, "коротка, зручна, менш ефективна", 9, GREY, "middle")
    # меандр на платі
    s += text(700, 100, "доріжка на платі (меандр)", 10.5, AMBER, "middle", "bold")
    mx, my = 640, gy - 40
    pts = []
    for k in range(9):
        pts.append((mx + k * 14, my - (20 if k % 2 else 0)))
        pts.append((mx + k * 14, my - (0 if k % 2 else 20)))
    s += _poly(pts, AMBER, 2.4)
    s += text(700, gy + 22, "майже безкоштовна, у телефонах/IoT", 9, GREY, "middle")
    s += _ground(80, 760, gy)
    s += rect(60, 300, W - 120, 36, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 323, "Фізично коротшу антену «доганяють» до резонансу індуктивністю — але менша антена випромінює гірше.",
              10.5, INK, "middle", "bold")
    save("fig-41-2-6-loading.svg", s)


# ── Рис. 41.2.7 — галерея реальних антен ─────────────────────────────────────
def fig27_gallery():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "Реальні антени — це все та сама λ/4 чи λ/2", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "за різними формами ховається один принцип: довжина, узгоджена з хвилею",
              11.5, GREY, "middle", style="italic")
    gy = 240
    items = [
        ("диполь", "λ/2", "FM, ТБ", 120),
        ("штир", "λ/4", "авто, рація", 100),
        ("rubber duck", "λ/4 + котушка", "роутер, Wi-Fi", 70),
        ("чип/меандр", "коротка", "телефон, IoT", 40),
    ]
    x = 110
    for nm, frac, use, hh in items:
        s += line(x, gy, x, gy - hh, METAL, 5)
        if "котушка" in frac:
            for k in range(4):
                s += arc(x, gy - hh + 6 + k * 8, 7, 0, 360, BLUE, 1.6)
        s += text(x, gy + 24, nm, 11, INK, "middle", "bold")
        s += text(x, gy + 42, frac, 10, GREEN, "middle", "bold")
        s += text(x, gy + 60, use, 9, GREY, "middle")
        x += 210
    s += line(70, gy, 830, gy, EARTH, 2)
    save("fig-41-2-7-gallery.svg", s)


# ============================================================================
#  §41.3 — Підсилення й діаграма спрямованості
# ============================================================================

def polar(cx, cy, scale, func, color, w=2.4, fill="none", a0=0, a1=360, step=2):
    pts = []
    a = a0
    while a <= a1 + 0.001:
        r = max(0.0, func(math.radians(a)))
        x = cx + r * scale * math.cos(math.radians(a))
        y = cy - r * scale * math.sin(math.radians(a))
        pts.append((x, y))
        a += step
    d = '<path d="M ' + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d += f'" fill="{fill}" stroke="{color}" stroke-width="{w}"/>\n'
    return d


# ── Рис. 41.3.1 — діаграма спрямованості ─────────────────────────────────────
def fig31_pattern():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Антена світить не однаково навсібіч: діаграма спрямованості", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "форма-«пелюстка» показує, куди антена випромінює сильно, а куди — майже нічого",
              11, GREY, "middle", style="italic")
    cx, cy = 260, 200
    # осі
    s += line(cx - 130, cy, cx + 170, cy, FAINT, 1)
    s += line(cx, cy - 110, cx, cy + 110, FAINT, 1)
    s += line(cx, cy, cx, cy - 60, METAL, 4)  # антена
    # спрямований патерн
    s += polar(cx, cy, 150, lambda a: max(0, math.cos(a)) ** 1.5 + 0.12 * abs(math.cos(2.5 * a)),
               GREEN, 2.4, "#eef6ef33")
    s += text(cx + 150, cy - 10, "головна", 10.5, GREEN, "middle", "bold")
    s += text(cx + 150, cy + 6, "пелюстка", 10.5, GREEN, "middle", "bold")
    s += text(cx - 95, cy - 40, "бічні", 9.5, GREY, "middle")
    s += text(cx - 60, cy + 60, "задня", 9.5, GREY, "middle")
    s += rect(470, 110, 400, 180, LGREY, GREY, 1.3, 10)
    s += text(670, 138, "Як читати діаграму:", 12, INK, "middle", "bold")
    for i, ln in enumerate([
        "• що далі «пелюстка» — то сильніший сигнал туди",
        "• головна пелюстка — головний напрям променя",
        "• бічні й задня — небажані «витоки»",
        "• те саме й на прийом (взаємність, §41.1)",
    ]):
        s += text(490, 166 + i * 26, ln, 10.5, INK, "start")
    save("fig-41-3-1-pattern.svg", s)


# ── Рис. 41.3.2 — ізотропна vs диполь ────────────────────────────────────────
def fig32_isotropic_dipole():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Еталон і реальність: ізотропна антена та диполь", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ізотропна світить рівно навсібіч (лише в теорії); диполь — «бубликом» упоперек дроту",
              11, GREY, "middle", style="italic")
    # ізотропна
    cx1, cy1 = 220, 200
    s += circle(cx1, cy1, 80, "#e9eefb55", BLUE, 2)
    s += circle(cx1, cy1, 4, BLUE, BLUE, 0)
    s += text(cx1, 100, "ізотропна (еталон)", 12, BLUE, "middle", "bold")
    s += text(cx1, cy1 + 110, "0 дБі — рівна куля, лише в теорії", 9.5, GREY, "middle")
    # диполь — бублик
    cx2, cy2 = 660, 200
    s += line(cx2, cy2 - 70, cx2, cy2 + 70, METAL, 5)
    s += polar(cx2, cy2, 95, lambda a: abs(math.sin(a)), GREEN, 2.4, "#eef6ef55")
    s += text(cx2, 100, "диполь", 12, GREEN, "middle", "bold")
    s += text(cx2 + 110, cy2, "max упоперек", 9.5, GREEN, "start", "bold")
    s += text(cx2, cy2 - 80, "нуль уздовж", 9.5, RED, "middle", "bold")
    s += text(cx2, cy2 + 110, "2.15 дБі — «бублик» навколо дроту", 9.5, GREY, "middle")
    s += rect(60, 300, W - 120, 36, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 323, "Підсилення міряють у дБі — у децибелах відносно ідеальної ізотропної антени.",
              11.5, INK, "middle", "bold")
    save("fig-41-3-2-isotropic-dipole.svg", s)


# ── Рис. 41.3.3 — підсилення = концентрація ──────────────────────────────────
def fig33_gain():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Підсилення антени — це КОНЦЕНТРАЦІЯ, а не зайва енергія", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "антена нічого не додає (§40.6); вона збирає ту саму потужність у вужчий промінь",
              11, GREY, "middle", style="italic")
    # ліхтарик без рефлектора
    s += text(230, 100, "лампа без рефлектора", 11.5, BLUE, "middle", "bold")
    cx1, cy1 = 230, 200
    s += circle(cx1, cy1, 6, SPARK, SPARK, 0)
    for a in range(0, 360, 30):
        s += line(cx1, cy1, cx1 + 55 * math.cos(math.radians(a)), cy1 - 55 * math.sin(math.radians(a)), AMBER, 1)
    s += text(cx1, cy1 + 90, "слабко, але навсібіч", 9.5, GREY, "middle")
    # з рефлектором — промінь
    s += text(660, 100, "лампа з рефлектором", 11.5, GREEN, "middle", "bold")
    cx2, cy2 = 600, 200
    s += circle(cx2, cy2, 6, SPARK, SPARK, 0)
    s += f'<path d="M {cx2},{cy2} L {cx2+180},{cy2-45} L {cx2+180},{cy2+45} Z" fill="#fff6d8" stroke="{GREEN}" stroke-width="2"/>\n'
    s += text(cx2 + 120, cy2 + 90, "яскраво — але лише вперед", 9.5, GREEN, "middle", "bold")
    s += rect(60, 300, W - 120, 50, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 322, "Та сама лампа, та сама потужність — рефлектор лише ЗБИРАЄ світло в промінь. Антена робить так само.",
              11, INK, "middle", "bold")
    s += text(W / 2, 341, "Більше підсилення (дБі) = вужчий промінь. Виграш в один бік — це втрата в інші.", 10.5, GREY, "middle", style="italic")
    save("fig-41-3-3-gain.svg", s)


# ── Рис. 41.3.4 — всебічна vs спрямована ─────────────────────────────────────
def fig34_omni_directional():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Всебічна чи спрямована: головний вибір", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "покрити все навколо помірно — чи добити далеко, але точно цілячись",
              11.5, GREY, "middle", style="italic")
    # всебічна
    s += rect(60, 86, 380, 230, "#fbfbfb", BLUE, 1.8, 10)
    s += text(250, 112, "Всебічна (omni)", 13, BLUE, "middle", "bold")
    cx1, cy1 = 250, 200
    s += line(cx1, cy1 - 40, cx1, cy1 + 40, METAL, 4)
    s += circle(cx1, cy1, 55, "#e9eefb66", BLUE, 2)
    s += text(250, 290, "покриває всі напрями, не треба цілитися", 9.5, GREY, "middle")
    s += text(250, 306, "роутер, телефон, авто — менше підсилення", 9.5, GREY, "middle")
    # спрямована
    s += rect(460, 86, 380, 230, "#fbfbfb", GREEN, 1.8, 10)
    s += text(650, 112, "Спрямована (directional)", 12.5, GREEN, "middle", "bold")
    cx2, cy2 = 560, 200
    s += polar(cx2, cy2, 110, lambda a: max(0, math.cos(a)) ** 2, GREEN, 2.2, "#eef6ef66")
    s += text(650, 290, "б'є далеко вузьким променем — треба цілитися", 9.5, GREY, "middle")
    s += text(650, 306, "тарілка, Yagi — велике підсилення, лінк точка-точка", 9.5, GREY, "middle")
    s += text(W / 2, 352, "Обидві мають однакову «загальну» потужність — питання лише, як її розподілити в просторі.",
              11, INK, "middle", "bold")
    save("fig-41-3-4-omni-directional.svg", s)


# ── Рис. 41.3.5 — ширина променя ─────────────────────────────────────────────
def fig35_beamwidth():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Ширина променя: більше підсилення — вужчий промінь", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "що гостріший промінь, то далі добиває — але то точніше треба наводити антену",
              11, GREY, "middle", style="italic")
    # широкий промінь
    cx1, cy1 = 230, 210
    s += line(cx1, cy1, cx1, cy1 - 40, METAL, 4)
    s += polar(cx1, cy1, 120, lambda a: max(0, math.cos(a)), GREEN, 2, "#eef6ef55", a0=-90, a1=90)
    s += text(cx1, 100, "помірне підсилення", 11, GREEN, "middle", "bold")
    s += text(cx1, cy1 + 70, "широкий промінь", 9.5, GREY, "middle")
    s += text(cx1, cy1 + 86, "легко навести", 9.5, GREY, "middle")
    # вузький промінь
    cx2, cy2 = 660, 210
    s += line(cx2, cy2, cx2, cy2 - 40, METAL, 4)
    s += polar(cx2, cy2, 160, lambda a: max(0, math.cos(a)) ** 6, GREEN, 2, "#eef6ef55", a0=-90, a1=90)
    s += text(cx2, 100, "велике підсилення", 11, GREEN, "middle", "bold")
    s += text(cx2, cy2 + 70, "вузький промінь — далеко", 9.5, GREY, "middle")
    s += text(cx2, cy2 + 86, "треба точно цілитися", 9.5, RED, "middle", "bold")
    s += rect(60, 300, W - 120, 36, LGREY, GREY, 1.3, 8)
    s += text(W / 2, 323, "Груба оцінка: підсилення ≈ 30000 / (ширина_° × висота_°). Вузький промінь 20°×20° → ≈ 18 дБі.",
              10.5, INK, "middle", "bold")
    save("fig-41-3-5-beamwidth.svg", s)


# ── Рис. 41.3.6 — підсилення у бюджеті ───────────────────────────────────────
def fig36_link():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Підсилення працює на обидва боки лінії", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "за взаємністю (§41.1) спрямована антена додає дБі і на передачі, і на прийомі",
              11.5, GREY, "middle", style="italic")
    # TX dish
    s += f'<path d="M 120,120 Q 150,170 120,220" fill="none" stroke="{METAL}" stroke-width="4"/>\n'
    s += line(120, 170, 150, 170, METAL, 3)
    s += text(120, 248, "TX +15 дБі", 11, GREEN, "middle", "bold")
    # промінь
    s += f'<path d="M 150,150 L 750,160 L 750,180 L 150,190 Z" fill="#eef6ef" stroke="{GREEN}" stroke-width="1.5"/>\n'
    s += text(450, 150, "вузький промінь — велика дальність", 11, GREEN, "middle", "bold")
    # RX dish
    s += f'<path d="M 780,120 Q 750,170 780,220" fill="none" stroke="{METAL}" stroke-width="4"/>\n'
    s += line(750, 170, 780, 170, METAL, 3)
    s += text(780, 248, "RX +15 дБі", 11, GREEN, "middle", "bold")
    s += rect(60, 270, W - 120, 44, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 293, "У бюджеті (§40.6): G_tx + G_rx = +15 + 15 = +30 дБ запасу — лише завдяки спрямованим антенам.",
              11, INK, "middle", "bold")
    s += text(W / 2, 308, "Тому далекі лінки (супутник, радіорелейка) — це майже завжди тарілки з обох боків.", 9.5, GREY, "middle", style="italic")
    save("fig-41-3-6-link.svg", s)


# ── Рис. 41.3.7 — галерея за підсиленням ─────────────────────────────────────
def fig37_gallery():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Типи антен — від всебічних до гостроспрямованих", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "що більше підсилення, то вужчий промінь і то точніше треба наводити",
              11.5, GREY, "middle", style="italic")
    items = [
        ("штир/диполь", "~2 дБі", "всебічна", "роутер, авто", BLUE),
        ("патч/панель", "~5–9 дБі", "сектор", "Wi-Fi, стільник", GREEN),
        ("Yagi", "~10–18 дБі", "промінь", "ТБ, точка-точка", AMBER),
        ("тарілка", "20–40 дБі", "вузький", "супутник, радар", RED),
    ]
    x = 50
    for nm, g, beam, use, col in items:
        s += rect(x, 90, 200, 200, "#fbfbfb", col, 2, 12)
        s += text(x + 100, 120, nm, 13, INK, "middle", "bold")
        s += rect(x + 45, 134, 110, 30, "#fff", col, 1.4, 6)
        s += text(x + 100, 154, g, 12.5, col, "middle", "bold")
        s += text(x + 100, 186, beam, 11, INK, "middle", "bold")
        s += text(x + 100, 214, use, 10, GREY, "middle")
        # міні-патерн
        if col == BLUE:
            s += circle(x + 100, 252, 18, "none", col, 1.6)
        else:
            sharp = {GREEN: 1, AMBER: 3, RED: 8}[col]
            s += polar(x + 100, 252, 30, lambda a, p=sharp: max(0, math.cos(a)) ** p, col, 1.6, "none", a0=-90, a1=90)
        x += 213
    save("fig-41-3-7-gallery.svg", s)


# ============================================================================
#  §41.4 — Поляризація антени
# ============================================================================

# ── Рис. 41.4.1 — орієнтація антени задає поляризацію ────────────────────────
def fig41_pol_recap():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Орієнтація антени задає поляризацію хвилі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "поле E коливається вздовж дроту: вертикальна антена → вертикальна поляризація (§39.3)",
              11, GREY, "middle", style="italic")
    # вертикальна
    s += text(230, 100, "вертикальна антена", 12, BLUE, "middle", "bold")
    s += line(150, 130, 150, 270, METAL, 5)
    for x in (230, 290, 350):
        s += arrow(x, 200, x, 150, RED, 2)
        s += arrow(x, 200, x, 250, RED, 2)
    s += sine(200, 200, 180, 0, 0, BLUE, 0)
    s += text(300, 285, "E коливається ВГОРУ-ВНИЗ", 10, RED, "middle", "bold")
    # горизонтальна
    s += text(680, 100, "горизонтальна антена", 12, GREEN, "middle", "bold")
    s += line(560, 200, 700, 200, METAL, 5)
    for y in (150, 200, 250):
        s += arrow(760, y, 720, y, RED, 2)
        s += arrow(760, y, 800, y, RED, 2)
    s += text(740, 285, "E коливається ВБІК", 10, RED, "middle", "bold")
    s += rect(60, 305, W - 120, 30, LBLUE, BLUE, 1.3, 8)
    s += text(W / 2, 325, "Антена — це і є «дороговказ» для поля E: куди дріт, туди й поляризація хвилі.",
              11.5, INK, "middle", "bold")
    save("fig-41-4-1-pol-recap.svg", s)


# ── Рис. 41.4.2 — узгодження поляризації ─────────────────────────────────────
def fig42_matching():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Передавач і приймач мусять мати ту саму поляризацію", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "збіг — повний сигнал; схрещені під 90° антени майже не чують одна одну",
              11.5, GREY, "middle", style="italic")
    cases = [
        ("обидві ⊥ верт.", "верт", "верт", GREEN, "повний сигнал", 150),
        ("обидві гориз.", "гор", "гор", GREEN, "повний сигнал", 150),
        ("схрещені 90°", "верт", "гор", RED, "майже нуль!", 14),
    ]
    x = 60
    for title, tx, rx, col, res, bar in cases:
        s += rect(x, 86, 250, 210, "#fbfbfb", col, 2, 10)
        s += text(x + 125, 112, title, 12.5, col, "middle", "bold")
        # TX
        if tx == "верт":
            s += line(x + 60, 150, x + 60, 200, METAL, 4)
        else:
            s += line(x + 35, 175, x + 85, 175, METAL, 4)
        s += text(x + 60, 220, "TX", 10, INK, "middle", "bold")
        # RX
        if rx == "верт":
            s += line(x + 190, 150, x + 190, 200, METAL, 4)
        else:
            s += line(x + 165, 175, x + 215, 175, METAL, 4)
        s += text(x + 190, 220, "RX", 10, INK, "middle", "bold")
        # сигнал-бар
        s += rect(x + 40, 240, 170, 16, "#f0f0f0", GREY, 1)
        s += rect(x + 40, 240, 170 * bar / 150, 16, ("#cdeccd" if col == GREEN else "#f6cccc"), col, 1.2)
        s += text(x + 125, 278, res, 11.5, col, "middle", "bold")
        x += 270
    save("fig-41-4-2-matching.svg", s)


# ── Рис. 41.4.3 — втрати від кута неузгодження ───────────────────────────────
def fig43_angle_loss():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Втрати від кута: закон cos²θ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "що більший кут θ між поляризаціями, то менше потужності проходить (cos²θ)",
              11.5, GREY, "middle", style="italic")
    ox, oy = 110, 300
    axw, axh = 540, 210
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += arrow(ox, oy, ox, oy - axh, INK, 2)
    s += text(ox + axw, oy + 22, "кут θ", 11, INK, "end", "bold")
    s += text(ox - 70, oy - axh + 8, "проходить", 10, INK, "start", "bold")

    def X(th):
        return ox + th / 90 * axw

    def Y(frac):
        return oy - frac * axh
    pts = []
    th = 0
    while th <= 90:
        pts.append((X(th), Y(math.cos(math.radians(th)) ** 2)))
        th += 2
    s += _poly(pts, GREEN, 2.8)
    for th, lab in [(0, "0° → 100%"), (45, "45° → −3 дБ"), (60, "60° → −6 дБ"), (90, "90° → ≈0")]:
        fr = math.cos(math.radians(th)) ** 2
        s += circle(X(th), Y(fr), 4, RED, RED, 0)
        s += text(X(th) + (8 if th < 80 else -8), Y(fr) - 8, lab, 9.5, RED, ("start" if th < 80 else "end"), "bold")
    s += line(ox, oy + 6, ox, oy - 6, INK, 1)
    s += text(X(0), oy + 22, "0°", 9.5, GREY, "middle")
    s += text(X(90), oy + 22, "90°", 9.5, GREY, "middle")
    s += rect(680, 110, 200, 170, LRED, RED, 1.3, 9)
    s += text(780, 136, "На практиці:", 11, INK, "middle", "bold")
    s += text(780, 160, "90° дає не «нуль»,", 10, INK, "middle")
    s += text(780, 178, "а −20…−30 дБ —", 10, RED, "middle", "bold")
    s += text(780, 196, "тобто фактично", 10, INK, "middle")
    s += text(780, 214, "мертвий зв'язок.", 10, RED, "middle", "bold")
    s += text(780, 244, "Завжди узгоджуй", 9.5, GREY, "middle", style="italic")
    s += text(780, 260, "поляризацію!", 9.5, GREY, "middle", style="italic")
    save("fig-41-4-3-angle-loss.svg", s)


# ── Рис. 41.4.4 — чому телефон усе ж працює ──────────────────────────────────
def fig44_depol():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Чому телефон працює під будь-яким нахилом", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у приміщенні відбиття «перемішують» поляризацію — мimохіть рятуючи неузгодження",
              11, GREY, "middle", style="italic")
    # приміщення
    s += rect(60, 86, 380, 200, "#fbfbfb", GREEN, 1.8, 10)
    s += text(250, 110, "У приміщенні (багатопроменевість)", 11, GREEN, "middle", "bold")
    s += line(110, 150, 110, 200, METAL, 4)
    s += text(110, 218, "AP верт.", 9, INK, "middle")
    # відбиття зі зміною кута
    s += line(125, 175, 250, 130, BLUE, 1.4)
    s += line(250, 130, 360, 190, BLUE, 1.4)
    s += line(125, 180, 240, 250, AMBER, 1.4)
    s += line(240, 250, 360, 200, AMBER, 1.4)
    s += line(370, 175, 350, 215, METAL, 4)  # нахилений телефон
    s += text(385, 210, "нахилений", 9, INK, "start")
    s += text(385, 224, "телефон — чує!", 9, GREEN, "start", "bold")
    # пряма видимість
    s += rect(460, 86, 380, 200, "#fbfbfb", RED, 1.8, 10)
    s += text(650, 110, "Пряма видимість (без відбить)", 11, RED, "middle", "bold")
    s += line(520, 150, 520, 200, METAL, 4)
    s += text(520, 218, "TX верт.", 9, INK, "middle")
    s += line(540, 175, 760, 175, BLUE, 1.6)
    s += line(770, 160, 810, 190, METAL, 4)  # нахилений RX
    s += text(785, 215, "схрещений →", 9, RED, "middle")
    s += text(785, 229, "великі втрати", 9, RED, "middle", "bold")
    s += text(W / 2, 322, "Висновок: у місті/будинку поляризація «прощається»; у прямій видимості (лінк, FPV) — узгоджуй обов'язково.",
              10.5, INK, "middle", "bold")
    save("fig-41-4-4-depol.svg", s)


# ── Рис. 41.4.5 — колова поляризація ─────────────────────────────────────────
def fig45_circular():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Колова поляризація: поле E обертається, наче гвинт", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "складемо дві схрещені хвилі зі зсувом 90° — і вектор E піде по спіралі (права чи ліва)",
              10.5, GREY, "middle", style="italic")
    ox, cy = 130, 190
    axl = 600
    s += arrow(ox, cy, ox + axl + 30, cy, GREY, 1.6)
    s += text(ox + axl + 30, cy + 20, "напрям руху", 9.5, GREY, "end")
    # обертові вектори
    nseg = 9
    tips = []
    for i in range(nseg):
        x = ox + 30 + i * (axl - 30) / (nseg - 1)
        ang = i * 360 / (nseg - 1)
        ex = 0.0
        ey = -40 * math.sin(math.radians(ang))
        s += circle(x, cy, 40, "none", FAINT, 1)
        s += arrow(x, cy, x + ex, cy + ey, RED, 2)
        tips.append((x, cy + ey))
    s += _poly(tips, BLUE, 1.8)
    s += text(ox + axl / 2, 300, "вектор E обертається на повний оберт за одну довжину хвилі — це «гвинт»",
              10.5, INK, "middle", "bold")
    s += text(ox + axl / 2, 322, "за напрямом обертання: права (RHCP) чи ліва (LHCP) колова поляризація",
              10, GREY, "middle", style="italic")
    save("fig-41-4-5-circular.svg", s)


# ── Рис. 41.4.6 — переваги колової ───────────────────────────────────────────
def fig46_circular_benefit():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо колова: працює за будь-якого нахилу", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "колова антена ловить лінійну під будь-яким кутом — лише −3 дБ, без глибокого провалу",
              11, GREY, "middle", style="italic")
    cards = [
        ("🧭", "Будь-яка орієнтація", "Колова чує лінійну хоч вертикальну, хоч горизонтальну — завжди ~−3 дБ, без нуля.", GREEN),
        ("🔄", "Відсікає віддзеркалення", "Відбиття перевертає «руку» (RHCP↔LHCP) → антена його відкидає (плюс проти багатопроменевості).", BLUE),
        ("🛰️", "GPS і супутники", "Супутник обертається відносно тебе; колова (RHCP) знімає нулі неузгодження.", AMBER),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 86, 270, 210, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 126, ico, 23, INK, "middle")
        s += text(x + 135, 154, title, 12.5, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 184
        for wd in words:
            if len(ln) + len(wd) > 30:
                s += text(x + 135, yy, ln.strip(), 10.2, INK, "middle")
                ln, yy = "", yy + 18
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 10.2, INK, "middle")
        x += 290
    save("fig-41-4-6-circular-benefit.svg", s)


# ── Рис. 41.4.7 — практичні правила ──────────────────────────────────────────
def fig47_practical():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Поляризація на практиці: що коли брати", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "правило просте — нерухоме узгоджуй лінійно, рухоме й супутникове роби коловим",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("Фіксований лінк точка-точка", "лінійна, узгоджена (обидві верт. або гор.)", GREEN),
        ("Міський/кімнатний зв'язок", "лінійна; відбиття й так перемішають", BLUE),
        ("GPS, супутник", "колова (RHCP) — орієнтація не важить", AMBER),
        ("FPV-дрон, що крутиться", "колова — не «провалюється» в маневрі", RED),
    ]
    y = 90
    for case, rec, col in rows:
        s += rect(60, y, 360, 44, "#fbfbfb", col, 1.5, 8)
        s += text(80, y + 27, case, 11.5, INK, "start", "bold")
        s += arrow(425, y + 22, 455, y + 22, INK, 1.8)
        s += rect(460, y, 380, 44, ("#eef6ef" if col in (GREEN,) else "#f7f7f7"), col, 1.5, 8)
        s += text(480, y + 27, rec, 11, col, "start", "bold")
        y += 54
    save("fig-41-4-7-practical.svg", s)


# ============================================================================
#  §41.5 — Лінії передачі й хвильовий опір: чому 50 Ом
# ============================================================================

# ── Рис. 41.5.1 — на ВЧ дріт — це не просто дріт ─────────────────────────────
def fig51_not_wire():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "На радіочастотах дріт — це не просто з'єднання", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "коли довжина дроту порівнянна з λ, сигнал біжить ним як ХВИЛЯ — напруга різна вздовж лінії",
              11, GREY, "middle", style="italic")
    # низька частота
    s += text(230, 100, "низька частота / короткий дріт", 11, BLUE, "middle", "bold")
    s += line(110, 150, 350, 150, METAL, 4)
    s += text(230, 175, "та сама напруга по всій довжині", 10, GREY, "middle")
    s += text(230, 195, "— просто «з'єднання»", 10, BLUE, "middle", "bold")
    # ВЧ
    s += text(680, 100, "ВЧ / дріт ~ λ", 11, GREEN, "middle", "bold")
    s += sine(560, 150, 240, 18, 3, GREEN, 2.2)
    s += line(560, 175, 800, 175, METAL, 3)
    s += arrow(810, 175, 840, 175, GREEN, 2)
    s += text(680, 205, "хвиля біжить уздовж → V і I різні в різних точках", 9.5, GREEN, "middle", "bold")
    s += rect(60, 240, W - 120, 96, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 266, "Орієнтир: якщо довжина дроту більша за ~λ/10, його вже треба рахувати як ЛІНІЮ ПЕРЕДАЧІ,",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 288, "а не як ідеальний провідник. На 2.4 ГГц λ/10 ≈ 1.2 см — тобто майже будь-яка доріжка!",
              11, INK, "middle")
    s += text(W / 2, 312, "Саме тому ВЧ-частина плати проєктується зовсім інакше, ніж звичайна цифрова.",
              10.5, GREY, "middle", style="italic")
    save("fig-41-5-1-not-wire.svg", s)


# ── Рис. 41.5.2 — типи ліній передачі ────────────────────────────────────────
def fig52_lines():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Лінія передачі — це завжди ДВА провідники", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "сигнал «їде» між прямим і зворотним провідником; форма буває різна, суть одна",
              11.5, GREY, "middle", style="italic")
    # коакс
    s += text(180, 110, "коаксіал", 12, BLUE, "middle", "bold")
    s += circle(180, 190, 55, "#eef2fb", BLUE, 2)
    s += circle(180, 190, 8, METAL, INK, 2)
    s += text(180, 260, "центр + екран", 9.5, GREY, "middle")
    s += text(180, 276, "радіо, антени", 9, GREY, "middle")
    # мікросмужка
    s += text(450, 110, "мікросмужка (плата)", 11.5, GREEN, "middle", "bold")
    s += rect(400, 150, 100, 12, METAL, INK, 1)
    s += text(450, 145, "доріжка", 9, INK, "middle")
    s += rect(370, 200, 160, 14, "#d9d9d9", GREY, 1)
    s += text(450, 232, "земляний шар під нею", 9.5, GREY, "middle")
    s += rect(400, 162, 100, 38, "#f4efe0", "#cbb87a", 1)
    # кручена пара
    s += text(720, 110, "кручена пара", 12, AMBER, "middle", "bold")
    pts1, pts2 = [], []
    for i in range(61):
        t = i / 60
        x = 650 + t * 140
        pts1.append((x, 190 - 16 * math.sin(2 * math.pi * 4 * t)))
        pts2.append((x, 190 + 16 * math.sin(2 * math.pi * 4 * t)))
    s += _poly(pts1, AMBER, 2)
    s += _poly(pts2, "#7a5e00", 2)
    s += text(720, 260, "Ethernet, USB", 9.5, GREY, "middle")
    s += text(720, 276, "~100 Ом (диф.)", 9, GREY, "middle")
    s += text(W / 2, 322, "Хвиля завжди потребує «прямого» і «зворотного» шляху — між ними й біжить електромагнітне поле.",
              10.5, INK, "middle", "bold")
    save("fig-41-5-2-lines.svg", s)


# ── Рис. 41.5.3 — хвильовий опір Z0 ──────────────────────────────────────────
def fig53_z0():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Хвильовий опір Z₀: не резистор, а «характер» лінії", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "Z₀ = відношення напруги до струму біжучої хвилі; задається геометрією, а не довжиною",
              11, GREY, "middle", style="italic")
    s += sine(90, 150, 720, 22, 6, BLUE, 2.2)
    s += line(90, 175, 810, 175, METAL, 2)
    s += text(450, 110, "V / I хвилі = Z₀", 13, INK, "middle", "bold")
    facts = [
        ("Z₀ = √(L/C)", "залежить від розмірів і діелектрика лінії", BLUE),
        ("не залежить від довжини", "хоч метр, хоч кілометр — те саме Z₀", GREEN),
        ("це НЕ опір, що гріється", "енергія проходить крізь, а не втрачається", AMBER),
    ]
    y = 215
    for f, d, col in facts:
        s += circle(150, y - 4, 4, col, col, 0)
        s += text(168, y, f, 12, col, "start", "bold")
        s += text(400, y, "— " + d, 11, INK, "start")
        y += 34
    s += rect(60, 318, W - 120, 1, "none", "none", 0)
    save("fig-41-5-3-z0.svg", s)


# ── Рис. 41.5.4 — узгодження й відбиття ──────────────────────────────────────
def fig54_matching():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо все це: узгодження проти відбиття", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "якщо навантаження ≠ Z₀, частина хвилі ВІДБИВАЄТЬСЯ назад, не дійшовши до антени",
              11, GREY, "middle", style="italic")
    # узгоджено
    s += rect(60, 86, 380, 240, "#fbfbfb", GREEN, 1.8, 10)
    s += text(250, 112, "узгоджено: навантаження = Z₀", 11.5, GREEN, "middle", "bold")
    s += sine(90, 160, 250, 16, 4, BLUE, 2)
    s += arrow(345, 160, 380, 160, BLUE, 2)
    s += rect(385, 142, 30, 36, LGRN, GREEN, 1.6, 4)
    s += text(400, 200, "Z₀", 10, GREEN, "middle", "bold")
    s += text(250, 245, "уся потужність іде в антену ✓", 11, GREEN, "middle", "bold")
    s += text(250, 270, "як рівна мотузка: хвиля вбирається без луни", 9.5, GREY, "middle", style="italic")
    s += text(250, 300, "(те саме, що антена на резонансі, §41.2)", 9.5, GREY, "middle", style="italic")
    # неузгоджено
    s += rect(460, 86, 380, 240, "#fbfbfb", RED, 1.8, 10)
    s += text(650, 112, "неузгоджено: навантаження ≠ Z₀", 11, RED, "middle", "bold")
    s += sine(490, 150, 250, 14, 4, BLUE, 2)
    s += arrow(745, 150, 775, 150, BLUE, 2)
    s += rect(780, 132, 30, 36, LRED, RED, 1.6, 4)
    s += sine(490, 185, 250, 11, 4, RED, 1.8)
    s += arrow(520, 185, 490, 185, RED, 2)
    s += text(650, 245, "частина вертається назад ✗", 11, RED, "middle", "bold")
    s += text(650, 270, "як вузол на мотузці: хвиля відбивається луною", 9.5, GREY, "middle", style="italic")
    s += text(650, 300, "втрачена потужність — і ризик для передавача", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, 352, "Тому всю лінію — джерело, кабель, антену — роблять на ОДИН опір. Найчастіше — 50 Ом.",
              11.5, INK, "middle", "bold")
    save("fig-41-5-4-matching.svg", s)


# ── Рис. 41.5.5 — чому саме 50 Ом ────────────────────────────────────────────
def fig55_why50():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чому 50 Ом: компроміс між втратами й потужністю", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "для коаксіалу різні оптимуми не збігаються — і 50 Ом лягає посередині",
              11.5, GREY, "middle", style="italic")
    ox, oy = 110, 290
    axw = 700
    smin, smax = 20.0, 90.0

    def X(z):
        return ox + (z - smin) / (smax - smin) * axw
    s += line(ox, oy, ox + axw, oy, INK, 2)
    for z in (20, 30, 50, 77, 90):
        s += line(X(z), oy, X(z), oy + 5, INK, 1.2)
        s += text(X(z), oy + 22, f"{z}", 10, GREY, "middle")
    s += text(ox + axw, oy + 40, "Z₀, Ом", 10, INK, "end", "bold")
    # маркери оптимумів
    s += _stem(X(30), oy, 120, RED, 4)
    s += text(X(30), oy - 130, "макс. потужність", 10, RED, "middle", "bold")
    s += text(X(30), oy - 116, "≈ 30 Ом", 9, GREY, "middle")
    s += _stem(X(77), oy, 120, BLUE, 4)
    s += text(X(77), oy - 130, "мін. втрати", 10, BLUE, "middle", "bold")
    s += text(X(77), oy - 116, "≈ 77 Ом", 9, GREY, "middle")
    s += _stem(X(50), oy, 170, GREEN, 5)
    s += circle(X(50), oy - 170, 7, GREEN, GREEN, 0)
    s += text(X(50), oy - 184, "50 Ом — компроміс", 11.5, GREEN, "middle", "bold")
    s += rect(560, 96, 300, 120, LGREY, GREY, 1.3, 9)
    s += text(710, 122, "Звідки 50:", 11, INK, "middle", "bold")
    s += text(710, 144, "√(30 × 77) ≈ 48", 11, INK, "middle", "bold")
    s += text(710, 164, "(середнє геометричне)", 9, GREY, "middle")
    s += text(710, 186, "75 Ом — для відео/ТБ", 10, AMBER, "middle", "bold")
    s += text(710, 202, "(там важать лише втрати)", 9, GREY, "middle")
    save("fig-41-5-5-why50.svg", s)


# ── Рис. 41.5.6 — стандартні лінії ───────────────────────────────────────────
def fig56_standards():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Стандартні опори ліній — і де вони", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен вид зв'язку має «свій» хвильовий опір; його треба знати й дотримуватися",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("50 Ом", "коаксіал RF, роз'єми SMA/BNC/N", "радіо, антени, ВЧ-плати", GREEN),
        ("75 Ом", "коаксіал відео", "ТБ, антена, відеосигнал", AMBER),
        ("100 Ом", "кручена пара (диф.)", "Ethernet, USB", BLUE),
        ("90 Ом", "кручена пара", "USB 2.0 (диф.)", BLUE),
    ]
    x0, y0 = 110, 90
    s += rect(x0, y0, 110, 32, "#f0f0f0", GREY, 1.3)
    s += rect(x0 + 110, y0, 320, 32, "#f0f0f0", GREY, 1.3)
    s += rect(x0 + 430, y0, 250, 32, "#f0f0f0", GREY, 1.3)
    s += text(x0 + 55, y0 + 22, "опір", 11, INK, "middle", "bold")
    s += text(x0 + 270, y0 + 22, "лінія", 11, INK, "middle", "bold")
    s += text(x0 + 555, y0 + 22, "де", 11, INK, "middle", "bold")
    yy = y0 + 32
    for z, line_, use, col in rows:
        s += rect(x0, yy, 110, 38, "#fff", "#e2e2e2", 1)
        s += rect(x0 + 110, yy, 320, 38, "#fff", "#e2e2e2", 1)
        s += rect(x0 + 430, yy, 250, 38, "#fff", "#e2e2e2", 1)
        s += text(x0 + 55, yy + 25, z, 12.5, col, "middle", "bold")
        s += text(x0 + 124, yy + 25, line_, 10.5, INK, "start")
        s += text(x0 + 444, yy + 25, use, 10.5, INK, "start")
        yy += 38
    s += text(W / 2, yy + 26, "Тонкість: у кабелі сигнал іде повільніше за c (коефіцієнт укорочення ~0.66–0.85) — довжина «електрично» інша.",
              10, GREY, "middle", style="italic")
    save("fig-41-5-6-standards.svg", s)


# ── Рис. 41.5.7 — узгодження на платі ────────────────────────────────────────
def fig57_pcb():
    W, H = 900, 330
    s = header(W, H)
    s += text(W / 2, 34, "На платі: ВЧ-доріжка теж лінія на 50 Ом", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "доріжку від чипа до антени роблять контрольованої ширини над суцільною землею — рівно 50 Ом",
              10.5, GREY, "middle", style="italic")
    # чип
    s += rect(90, 150, 90, 60, "#2b2b2b", INK, 1.5, 5)
    s += text(135, 185, "ВЧ-чип", 10, "#fff", "middle", "bold")
    # 50-омна доріжка
    s += rect(180, 172, 380, 16, "#d2a24a", "#9a7320", 1.5)
    s += text(370, 165, "доріжка 50 Ом (мікросмужка)", 10, AMBER, "middle", "bold")
    # антена
    s += line(560, 180, 620, 130, METAL, 4)
    s += text(630, 130, "антена 50 Ом", 10, GREEN, "start", "bold")
    # земля
    s += rect(90, 215, 600, 14, "#cfcfcf", GREY, 1)
    s += text(390, 250, "суцільний земляний шар (опорна площина)", 9.5, GREY, "middle")
    s += rect(60, 270, W - 120, 50, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 292, "Золоте правило ВЧ: джерело, лінія й антена — усі на одному опорі (50 Ом). Тоді нічого не відбивається.",
              11, INK, "middle", "bold")
    s += text(W / 2, 310, "А скільки саме відбивається при неузгодженні — міряють коефіцієнтом стійної хвилі (КСХ), це далі.",
              9.5, GREY, "middle", style="italic")
    save("fig-41-5-7-pcb.svg", s)


# ============================================================================
#  §41.6 — Відбиття й КСХ
# ============================================================================

# ── Рис. 41.6.1 — коефіцієнт відбиття Γ ──────────────────────────────────────
def fig61_gamma():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Коефіцієнт відбиття Γ: скільки хвилі вертається", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "Γ = (Z_н − Z₀) / (Z_н + Z₀): від 0 (усе пройшло) до ±1 (усе відбилось)",
              11, GREY, "middle", style="italic")
    cases = [
        ("узгоджено", "Z_н = Z₀", "Γ = 0", "нічого не відбито", GREEN),
        ("розрив", "Z_н = ∞", "Γ = +1", "усе відбито", RED),
        ("коротке", "Z_н = 0", "Γ = −1", "усе відбито (з інверсією)", RED),
    ]
    x = 60
    for title, z, g, res, col in cases:
        s += rect(x, 92, 250, 200, "#fbfbfb", col, 2, 10)
        s += text(x + 125, 120, title, 13, col, "middle", "bold")
        s += text(x + 125, 150, z, 12.5, INK, "middle", "bold")
        # хвиля вперед і назад
        s += sine(x + 25, 185, 200, 12, 3, BLUE, 1.8)
        if col == GREEN:
            s += rect(x + 222, 173, 18, 24, LGRN, GREEN, 1.4, 3)
        else:
            s += sine(x + 25, 215, 200, 9, 3, RED, 1.6)
            s += arrow(x + 60, 215, x + 30, 215, RED, 1.8)
        s += text(x + 125, 250, g, 14, col, "middle", "bold")
        s += text(x + 125, 276, res, 9.5, GREY, "middle")
        x += 270
    save("fig-41-6-1-gamma.svg", s)


# ── Рис. 41.6.2 — стояча хвиля ───────────────────────────────────────────────
def fig62_standing():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Звідки «стояча хвиля»: пряма + відбита", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "пряма й відбита хвилі складаються в нерухомий візерунок — пучности й вузли стоять на місці",
              11, GREY, "middle", style="italic")
    ox = 90
    axl = 720
    cy = 180
    # обвідні стоячої хвилі
    up, dn = [], []
    for i in range(241):
        t = i / 240
        x = ox + t * axl
        env = 0.55 + 0.45 * abs(math.cos(2 * math.pi * 2.5 * t))
        up.append((x, cy - env * 70))
        dn.append((x, cy + env * 70))
    s += _poly(up, BLUE, 2.2)
    s += _poly(dn, BLUE, 2.2)
    s += line(ox, cy, ox + axl, cy, FAINT, 1)
    # пучність / вузол
    s += text(ox + axl * 0.0 + 30, cy - 86, "пучність (V_max)", 10, RED, "middle", "bold")
    s += text(ox + axl * 0.2, cy + 100, "вузол (V_min)", 10, GREEN, "middle", "bold")
    s += line(ox + axl * 0.2, cy - 18, ox + axl * 0.2, cy + 18, GREEN, 2)
    s += rect(60, 300, W - 120, 44, LGREY, GREY, 1.3, 9)
    s += text(W / 2, 322, "Що більше відбиття, то глибша «брижа»: різниця між пучністю й вузлом росте.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 338, "Цю різницю й міряє КСХ.", 10, GREY, "middle", style="italic")
    save("fig-41-6-2-standing.svg", s)


# ── Рис. 41.6.3 — означення КСХ ──────────────────────────────────────────────
def fig63_swr_def():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "КСХ — коефіцієнт стійної хвилі (SWR)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "КСХ = V_max / V_min = (1+|Γ|)/(1−|Γ|); 1:1 — ідеал, ∞ — повне відбиття",
              11.5, GREY, "middle", style="italic")
    # шкала-«манометр»
    ox, oy = 130, 250
    axw = 640
    s += line(ox, oy, ox + axw, oy, INK, 3)
    marks = [(1, "1:1", GREEN), (1.5, "1.5", GREEN), (2, "2:1", AMBER), (3, "3:1", RED), (6, "∞", RED)]

    def X(v):
        return ox + min(v, 6) / 6 * axw
    for v, lab, col in marks:
        s += line(X(v), oy - 6, X(v), oy + 6, col, 2)
        s += text(X(v), oy + 24, lab, 11, col, "middle", "bold")
    # зони
    s += rect(ox, oy - 36, X(2) - ox, 24, "#eef6ef", GREEN, 1.2)
    s += text((ox + X(2)) / 2, oy - 19, "добре", 10, GREEN, "middle", "bold")
    s += rect(X(2), oy - 36, X(3) - X(2), 24, LAMB, AMBER, 1.2)
    s += text((X(2) + X(3)) / 2, oy - 19, "терпимо", 9.5, AMBER, "middle", "bold")
    s += rect(X(3), oy - 36, X(6) - X(3), 24, LRED, RED, 1.2)
    s += text((X(3) + X(6)) / 2, oy - 19, "погано", 10, RED, "middle", "bold")
    s += text(ox, oy - 60, "ідеальне узгодження", 10, GREEN, "start", style="italic")
    s += text(ox + axw, oy - 60, "повне відбиття", 10, RED, "end", style="italic")
    s += text(W / 2, 312, "Ціль для більшості систем — КСХ нижче 1.5–2. Антенні аналізатори показують саме це число.",
              11, INK, "middle", "bold")
    save("fig-41-6-3-swr-def.svg", s)


# ── Рис. 41.6.4 — таблиця КСХ ────────────────────────────────────────────────
def fig64_swr_table():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Що означає число КСХ на практиці", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "переклад КСХ у відбиту потужність і реальні втрати — здебільшого менші, ніж лякають",
              11, GREY, "middle", style="italic")
    rows = [
        ("1.0:1", "0 %", "0 дБ", "ідеально", GREEN),
        ("1.5:1", "4 %", "−0.18 дБ", "відмінно", GREEN),
        ("2.0:1", "11 %", "−0.5 дБ", "прийнятно", AMBER),
        ("3.0:1", "25 %", "−1.25 дБ", "погано", RED),
        ("5.0:1", "44 %", "−2.5 дБ", "дуже погано", RED),
    ]
    x0, y0 = 110, 86
    ws = [130, 170, 170, 210]
    heads = ["КСХ", "відбито потужн.", "втрати на відбитті", "вердикт"]
    cx = x0
    for h, w_ in zip(heads, ws):
        s += rect(cx, y0, w_, 34, "#f0f0f0", GREY, 1.3)
        s += text(cx + w_ / 2, y0 + 23, h, 10.5, INK, "middle", "bold")
        cx += w_
    yy = y0 + 34
    for swr, refl, loss, verd, col in rows:
        cx = x0
        vals = [(swr, INK, "bold"), (refl, INK, "normal"), (loss, BLUE, "bold"), (verd, col, "bold")]
        for (val, vcol, wt), w_ in zip(vals, ws):
            s += rect(cx, yy, w_, 40, "#fff", "#e2e2e2", 1)
            s += text(cx + w_ / 2, yy + 26, val, 11, vcol, "middle", ("bold" if wt == "bold" else "normal"))
            cx += w_
        yy += 40
    s += text(W / 2, yy + 26, "Тонко, але важливо: сама втрата на відбитті часто мала (КСХ 2 → лише 0.5 дБ). Головна біда — інше (далі).",
              10, GREY, "middle", style="italic")
    save("fig-41-6-4-swr-table.svg", s)


# ── Рис. 41.6.5 — чому неузгодження шкідливе ─────────────────────────────────
def fig65_why_bad():
    W, H = 900, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чим насправді небезпечне неузгодження", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "втрата дальності — це ще пів біди; гірше — загроза самому передавачу",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("📉", "Менше дальності", "Відбита потужність не дійшла до антени — мінус децибели бюджету (§40.6).", AMBER),
        ("🔥", "Загроза передавачу", "Відбита хвиля вертається в підсилювач і гріє його — потужні TX можуть згоріти.", RED),
        ("📵", "Передавач «душить» себе", "Захист бачить високий КСХ і САМ зрізає потужність — дальність падає ще більше.", BLUE),
    ]
    x = 45
    for ico, title, body, col in cards:
        s += rect(x, 86, 270, 210, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 126, ico, 23, INK, "middle")
        s += text(x + 135, 154, title, 12.5, col, "middle", "bold")
        words = body.split()
        ln, yy = "", 184
        for wd in words:
            if len(ln) + len(wd) > 30:
                s += text(x + 135, yy, ln.strip(), 10.2, INK, "middle")
                ln, yy = "", yy + 18
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 10.2, INK, "middle")
        x += 290
    save("fig-41-6-5-why-bad.svg", s)


# ── Рис. 41.6.6 — як виміряти ────────────────────────────────────────────────
def fig66_measure():
    W, H = 900, 350
    s = header(W, H)
    s += text(W / 2, 34, "Як виміряти узгодження", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "прилад показує КСХ або «зворотні втрати» по частоті — і де провал, там резонанс антени",
              11, GREY, "middle", style="italic")
    # графік зворотних втрат
    ox, oy = 120, 250
    axw, axh = 480, 150
    s += arrow(ox, oy - axh, ox, oy, INK, 2)
    s += arrow(ox, oy, ox + axw, oy, INK, 2)
    s += text(ox + axw, oy + 22, "частота", 10, INK, "end", "bold")
    s += text(ox - 14, oy - axh, "зворотні", 9.5, INK, "end")
    s += text(ox - 14, oy - axh + 14, "втрати", 9.5, INK, "end")
    pts = []
    for i in range(121):
        t = i / 120
        x = ox + t * axw
        dip = math.exp(-((t - 0.5) * 9) ** 2)
        y = (oy - axh + 16) + dip * (axh - 24)
        pts.append((x, y))
    s += _poly(pts, GREEN, 2.6)
    s += circle(ox + 0.5 * axw, oy - 8, 5, RED, RED, 0)
    s += text(ox + 0.5 * axw, oy - 18 + 40, "тут антена узгоджена", 9.5, RED, "middle", "bold")
    s += text(ox + 0.5 * axw, oy - axh - 4, "глибокий провал = добрий збіг", 10, GREEN, "middle", "bold")
    # прилади
    s += rect(640, 96, 220, 200, LGREY, GREY, 1.3, 10)
    s += text(750, 122, "чим міряють:", 11, INK, "middle", "bold")
    for i, t in enumerate(["• КСХ-метр (у розрив лінії)", "• антенний аналізатор", "• NanoVNA (дешевий VNA)", "  — КСХ і Γ по частоті"]):
        s += text(656, 150 + i * 26, t, 10, INK, "start")
    save("fig-41-6-6-measure.svg", s)


# ── Рис. 41.6.7 — як виправити ───────────────────────────────────────────────
def fig67_fix():
    W, H = 900, 320
    s = header(W, H)
    s += text(W / 2, 34, "Як полагодити неузгодження", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "три рівні дій — від найпростішого до тонкого налаштування",
              11.5, GREY, "middle", style="italic")
    steps = [
        ("1", "Правильна довжина", "Підстрой антену до резонансу (§41.2): часто КСХ падає сам.", GREEN),
        ("2", "Правильні 50 Ом", "Той самий опір по всій трасі: кабель, роз'єми, доріжка (§41.5).", BLUE),
        ("3", "Узгоджувальна ланка", "L-ланка, шлейф або балун «перетворюють» опір до Z₀.", AMBER),
    ]
    x = 50
    for n, title, body, col in steps:
        s += rect(x, 86, 270, 180, "#fbfbfb", col, 2, 12)
        s += circle(x + 32, 118, 16, col, col, 0)
        s += text(x + 32, 124, n, 15, "#fff", "middle", "bold")
        s += text(x + 56, 124, title, 12.5, col, "start", "bold")
        words = body.split()
        ln, yy = "", 162
        for wd in words:
            if len(ln) + len(wd) > 32:
                s += text(x + 135, yy, ln.strip(), 10.3, INK, "middle")
                ln, yy = "", yy + 19
            ln += wd + " "
        s += text(x + 135, yy, ln.strip(), 10.3, INK, "middle")
        s += text(x + 135, 246, "", 9, GREY, "middle")
        x += 290
    s += text(W / 2, 300, "Ціль — КСХ < 1.5…2 на робочій частоті. Тоді майже вся потужність іде в антену, а передавач у безпеці.",
              10.5, INK, "middle", "bold")
    save("fig-41-6-7-fix.svg", s)


# ============================================================================
#  §41.7 — На що дивитись у ВЧ-частині чужої плати
# ============================================================================

def _hatch(x, y, w, h, col=GREY, gap=10, sw=0.7):
    s = rect(x, y, w, h, "none", col, 1)
    d = 0
    while d < w + h:
        x1 = x + max(0, d - h)
        y1 = y + min(d, h)
        x2 = x + min(d, w)
        y2 = y + max(0, d - w)
        s += line(x1, y1, x2, y2, col, sw)
        d += gap
    return s


# ── Рис. 41.7.1 — ВЧ-ланцюг на платі ─────────────────────────────────────────
def fig71_rf_block():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "ВЧ-тракт на платі: від чипа до антени", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "один і той самий ланцюг ховається майже в кожному радіомодулі — навчися його впізнавати",
              11, GREY, "middle", style="italic")
    blocks = [
        ("Радіочип", "+ кварц", "#2b2b2b", "#fff"),
        ("Узгодження", "π/L-ланка", LAMB, AMBER),
        ("Фільтр/балун", "(не завжди)", LBLUE, BLUE),
        ("Доріжка 50 Ω", "над землею", LGRN, GREEN),
        ("Антена", "", "#eef2fb", INK),
    ]
    x = 40
    bw = 158
    y = 150
    for i, (nm, sub, fill, tcol) in enumerate(blocks):
        s += rect(x, y, bw, 70, fill, INK, 1.6, 8)
        s += text(x + bw / 2, y + 32, nm, 12, tcol, "middle", "bold")
        if sub:
            s += text(x + bw / 2, y + 52, sub, 9.5, (GREY if tcol != "#fff" else "#bbb"), "middle")
        if i < len(blocks) - 1:
            s += arrow(x + bw + 2, y + 35, x + bw + 14, y + 35, INK, 2)
        x += bw + 16
    s += rect(60, 252, W - 120, 60, LGRN, GREEN, 1.4, 9)
    s += text(W / 2, 276, "Радіочип → узгоджувальна ланка → (фільтр) → 50-омна доріжка → антена. Усе з цього розділу разом.",
              11, INK, "middle", "bold")
    s += text(W / 2, 298, "Уміючи прочитати цей ланцюг, ти розумієш ВЧ-частину будь-якого модуля — від ESP32 до приймача.",
              10.5, GREY, "middle", style="italic")
    save("fig-41-7-1-rf-block.svg", s)


# ── Рис. 41.7.2 — типи антен на платі ────────────────────────────────────────
def fig72_spot_antenna():
    W, H = 920, 330
    s = header(W, H)
    s += text(W / 2, 34, "Три типи антен, які ти побачиш на платі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "за виглядом одразу видно, як пристрій випромінює — і чи можна підключити зовнішню антену",
              11, GREY, "middle", style="italic")
    # PCB-антена (меандр)
    s += rect(50, 90, 270, 180, "#fbfbfb", BLUE, 1.6, 10)
    s += text(185, 116, "доріжка на платі (PCB)", 11.5, BLUE, "middle", "bold")
    mx, my = 110, 175
    pts = []
    for k in range(11):
        pts.append((mx + k * 16, my - (28 if k % 2 else 0)))
        pts.append((mx + k * 16, my - (0 if k % 2 else 28)))
    s += _poly(pts, "#d2a24a", 2.6)
    s += text(185, 230, "дешево, вбудовано;", 9.5, GREY, "middle")
    s += text(185, 246, "меандр або «літера F» (IFA)", 9.5, GREY, "middle")
    # чип-антена
    s += rect(335, 90, 250, 180, "#fbfbfb", GREEN, 1.6, 10)
    s += text(460, 116, "чип-антена (кераміка)", 11.5, GREEN, "middle", "bold")
    s += rect(425, 160, 70, 34, "#e7e0cf", "#9a8b66", 1.6, 3)
    s += text(460, 182, "LNA", 9, GREY, "middle")
    s += text(460, 230, "маленький білий/сірий", 9.5, GREY, "middle")
    s += text(460, 246, "прямокутник на краю", 9.5, GREY, "middle")
    # роз'єм
    s += rect(600, 90, 270, 180, "#fbfbfb", AMBER, 1.6, 10)
    s += text(735, 116, "роз'єм (U.FL / SMA)", 11.5, AMBER, "middle", "bold")
    s += circle(700, 175, 18, "none", METAL, 2.4)
    s += circle(700, 175, 5, METAL, INK, 1.5)
    s += line(718, 175, 770, 175, METAL, 3)
    s += line(770, 150, 770, 200, METAL, 4)
    s += text(735, 230, "зовнішня антена;", 9.5, GREY, "middle")
    s += text(735, 246, "кабель уже 50 Ом", 9.5, GREY, "middle")
    save("fig-41-7-2-spot-antenna.svg", s)


# ── Рис. 41.7.3 — узгоджувальна ланка ────────────────────────────────────────
def fig73_matching_cluster():
    W, H = 920, 330
    s = header(W, H)
    s += text(W / 2, 34, "Загадковий «кущик» біля антени — це узгодження", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "2–3 крихітні деталі між чипом і антеною — це π/L-ланка, що зводить опір до 50 Ом (§41.6)",
              11, GREY, "middle", style="italic")
    # доріжка
    s += rect(120, 175, 120, 12, "#d2a24a", "#9a7320", 1)
    s += text(110, 184, "від чипа", 9.5, INK, "end")
    s += rect(680, 175, 120, 12, "#d2a24a", "#9a7320", 1)
    s += text(810, 184, "до антени", 9.5, INK, "start")
    # π-ланка: shunt C — series L — shunt C
    s += line(240, 181, 680, 181, "#d2a24a", 10)
    # series L
    s += rect(420, 168, 40, 26, "#fff", BLUE, 1.8, 3)
    s += text(440, 160, "L", 11, BLUE, "middle", "bold")
    # shunt C1
    s += line(330, 181, 330, 230, INK, 2)
    s += rect(320, 230, 20, 12, "#fff", GREEN, 1.6)
    s += text(355, 240, "C1", 10, GREEN, "start", "bold")
    s += _hatch(300, 250, 60, 10, GREY, 6)
    # shunt C2
    s += line(560, 181, 560, 230, INK, 2)
    s += rect(550, 230, 20, 12, "#fff", GREEN, 1.6)
    s += text(585, 240, "C2", 10, GREEN, "start", "bold")
    s += _hatch(530, 250, 60, 10, GREY, 6)
    s += text(445, 130, "π-ланка: shunt-C · series-L · shunt-C", 11, INK, "middle", "bold")
    s += rect(60, 280, W - 120, 38, LAMB, AMBER, 1.3, 8)
    s += text(W / 2, 304, "Часто бачиш ТРИ посадкові місця, але впаяні не всі: зайві позначені «DNP» (не встановлювати) — це нормально.",
              10.5, INK, "middle", "bold")
    save("fig-41-7-3-matching-cluster.svg", s)


# ── Рис. 41.7.4 — заборонена зона під антеною ────────────────────────────────
def fig74_keepout():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Головне правило: під антеною — ПОРОЖНЬО", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "PCB-антена не випромінює, якщо під нею мідь чи земля; їй потрібна чиста «заборонена зона»",
              11, GREY, "middle", style="italic")
    # плата
    s += rect(120, 90, 680, 200, "#fdfdf5", "#cfcf9a", 1.6, 8)
    # земляний поллю (hatch) скрізь, крім кута антени
    s += _hatch(140, 110, 420, 160, GREEN, 11)
    s += text(350, 285, "суцільна земля (де треба)", 9.5, GREEN, "middle", "bold")
    # антена в куті — keep-out (чисто)
    s += rect(600, 110, 180, 160, "#ffffff", RED, 1.8, 4)
    s += text(690, 104, "заборонена зона (keep-out)", 9.5, RED, "middle", "bold")
    mx, my = 625, 200
    pts = []
    for k in range(8):
        pts.append((mx + k * 18, my - (30 if k % 2 else 0)))
        pts.append((mx + k * 18, my - (0 if k % 2 else 30)))
    s += _poly(pts, "#d2a24a", 2.6)
    s += text(690, 250, "антена на КРАЮ плати", 9.5, INK, "middle", "bold")
    s += rect(60, 300, W - 120, 1, "none", "none", 0)
    save("fig-41-7-4-keepout.svg", s)


# ── Рис. 41.7.5 — як це на схемі (Розділ 6) ──────────────────────────────────
def fig75_schematic():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Як ВЧ-частина виглядає на схемі (з Розділу 6)", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ті самі блоки, але символами: чип з виводом ANT, π-ланка, мітка 50 Ω, символ антени",
              11, GREY, "middle", style="italic")
    # чип
    s += rect(80, 130, 150, 130, "#fff", INK, 1.8, 4)
    s += text(155, 120, "радіочип", 10.5, INK, "middle", "bold")
    s += text(150, 175, "U1", 11, INK, "middle", "bold")
    s += text(222, 160, "ANT", 9, INK, "end")
    # кварц
    s += rect(110, 275, 36, 16, "#fff", BLUE, 1.4)
    s += text(128, 305, "кварц", 9, BLUE, "middle")
    s += line(128, 260, 128, 275, INK, 1.4)
    # лінія ANT
    s += line(230, 160, 320, 160, INK, 2)
    # π-ланка символами
    s += rect(330, 150, 30, 20, "#fff", AMBER, 1.6)  # series L
    s += text(345, 142, "L", 9, AMBER, "middle", "bold")
    s += line(300, 160, 300, 210, INK, 1.6)  # shunt C1
    s += text(300, 225, "C", 9, GREEN, "middle")
    s += line(290, 210, 310, 210, GREEN, 2)
    s += line(294, 216, 306, 216, GREEN, 2)
    s += line(420, 160, 420, 210, INK, 1.6)  # shunt C2
    s += text(420, 225, "C", 9, GREEN, "middle")
    s += line(410, 210, 430, 210, GREEN, 2)
    s += line(414, 216, 426, 216, GREEN, 2)
    s += line(360, 160, 520, 160, INK, 2)
    s += text(470, 148, "50 Ω", 9.5, RED, "middle", "bold")
    # антена символ
    s += line(520, 160, 560, 160, INK, 2)
    s += line(560, 145, 580, 175, INK, 2)
    s += line(560, 175, 580, 145, INK, 2)
    s += line(560, 145, 580, 145, INK, 2)
    s += text(570, 200, "ANT", 10, INK, "middle", "bold")
    # земля
    for gx in (300, 420):
        s += line(gx, 210, gx, 250, INK, 1.4)
        s += line(gx - 10, 250, gx + 10, 250, INK, 2)
        s += line(gx - 6, 255, gx + 6, 255, INK, 2)
    s += rect(630, 120, 250, 150, LGREY, GREY, 1.3, 9)
    s += text(755, 146, "Шукай на схемі:", 11, INK, "middle", "bold")
    for i, t in enumerate(["• вивід ANT / RF чипа", "• π-ланку (L і два C)", "• мітку 50 Ω на цепі", "• символ антени / роз'єм", "• кварц біля чипа"]):
        s += text(648, 172 + i * 22, t, 9.8, INK, "start")
    save("fig-41-7-5-schematic.svg", s)


# ── Рис. 41.7.6 — червоні прапорці ───────────────────────────────────────────
def fig76_red_flags():
    W, H = 920, 330
    s = header(W, H)
    s += text(W / 2, 34, "Червоні прапорці: типові помилки ВЧ-частини", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "побачив таке — насторожися: антена, найімовірніше, працюватиме погано",
              11, GREY, "middle", style="italic")
    flags = [
        ("Земля під PCB-антеною", "найчастіша й найгірша помилка"),
        ("Довга звивиста доріжка", "до антени — з вигинами й перехідними"),
        ("Антена біля металу/батареї", "розладнує й глушить її"),
        ("Нема суцільної землі", "під мікросмужкою немає опори"),
        ("Чужий кабель (75 Ω, «дріт»)", "замість 50-омного коаксіалу"),
        ("Антена в центрі плати", "затиснута між компонентами"),
    ]
    x0, y0 = 60, 84
    for i, (t, d) in enumerate(flags):
        cx = x0 + (i % 2) * 410
        cy = y0 + (i // 2) * 76
        s += rect(cx, cy, 390, 64, LRED, RED, 1.5, 9)
        s += text(cx + 26, cy + 28, "✗", 18, RED, "middle", "bold")
        s += text(cx + 48, cy + 26, t, 11.5, INK, "start", "bold")
        s += text(cx + 48, cy + 46, d, 9.8, GREY, "start")
    save("fig-41-7-6-red-flags.svg", s)


# ── Рис. 41.7.7 — чеклист огляду ВЧ-плати ────────────────────────────────────
def fig77_checklist():
    W, H = 920, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чеклист: оглядаємо ВЧ-частину за хвилину", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "вісім пунктів, що зводять увесь розділ у практичну перевірку чужої плати",
              11, GREY, "middle", style="italic")
    items = [
        "Радіочип і кварц поряд із ним",
        "Тип антени: PCB / чип / роз'єм",
        "Доріжка до антени — коротка, пряма, 50 Ω",
        "Узгоджувальна π/L-ланка (кущик деталей)",
        "Під антеною — порожньо (keep-out)",
        "Суцільна земля під мікросмужкою",
        "Екран-кришка над ВЧ-вузлом (часто)",
        "Чисте живлення чипа (ферит + конденсатори)",
    ]
    x0, y0 = 80, 88
    for i, t in enumerate(items):
        cx = x0 + (i % 2) * 420
        cy = y0 + (i // 2) * 56
        s += rect(cx, cy, 16, 16, "#fff", GREEN, 2, 3)
        s += line(cx + 3, cy + 8, cx + 7, cy + 13, GREEN, 2.2)
        s += line(cx + 7, cy + 13, cx + 14, cy + 2, GREEN, 2.2)
        s += text(cx + 26, cy + 13, t, 11.5, INK, "start")
    save("fig-41-7-7-checklist.svg", s)


if __name__ == "__main__":
    # — історія (секція 0) —
    figh_timeline()
    figh_antenna_leap()
    figh_transatlantic()
    figh_controversy()
    figh_collective()
    figh_court_myth()
    figh_legacy()
    # — §41.1 —
    fig11_open_circuit()
    fig12_shake_charges()
    fig13_dipole_current()
    fig14_transducer()
    fig15_rad_resistance()
    fig16_reciprocity()
    fig17_near_far()
    # — §41.2 —
    fig21_string()
    fig22_halfwave()
    fig23_quarterwave()
    fig24_length_table()
    fig25_off_resonance()
    fig26_loading()
    fig27_gallery()
    # — §41.3 —
    fig31_pattern()
    fig32_isotropic_dipole()
    fig33_gain()
    fig34_omni_directional()
    fig35_beamwidth()
    fig36_link()
    fig37_gallery()
    # — §41.4 —
    fig41_pol_recap()
    fig42_matching()
    fig43_angle_loss()
    fig44_depol()
    fig45_circular()
    fig46_circular_benefit()
    fig47_practical()
    # — §41.5 —
    fig51_not_wire()
    fig52_lines()
    fig53_z0()
    fig54_matching()
    fig55_why50()
    fig56_standards()
    fig57_pcb()
    # — §41.6 —
    fig61_gamma()
    fig62_standing()
    fig63_swr_def()
    fig64_swr_table()
    fig65_why_bad()
    fig66_measure()
    fig67_fix()
    # — §41.7 —
    fig71_rf_block()
    fig72_spot_antenna()
    fig73_matching_cluster()
    fig74_keepout()
    fig75_schematic()
    fig76_red_flags()
    fig77_checklist()
    print("done.")
