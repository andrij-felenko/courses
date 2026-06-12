# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 8 — «Магнетизм і електромагніти» (Модуль 1).
Чистий Python, без залежностей. Вивід → ./img/.
Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; sans-serif.
Спільні хелпери скопійовано з попередніх розділів (за §9 — кожен розділ самодостатній).
Нумерація: теми — Рис. 8.T.k (модуль 1 → перша цифра імені файла «8» = розділ 8).
Імена файлів: fig-8-<тема>-<k>-<slug>.svg.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+), північний полюс N
BLUE  = "#1f47b5"   # від'ємний (−), південний полюс S
GREEN = "#1f8a3b"   # поле (тут — магнітне поле B / силові лінії)
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
COPPER = "#cf8b5e"  # мідь (обмотки)
IRON  = "#9aa3ad"   # залізо/осердя
ORANGE = "#e08030"  # акцент/струм
PURPLE = "#7a3fb0"  # сила (механічна)
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
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'  <marker id="aPurple" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{PURPLE}"/></marker>\n'
        f'  <marker id="aCopper" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{COPPER}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         ORANGE: "aOrange", PURPLE: "aPurple", COPPER: "aCopper"}


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


def circle(cx, cy, r, fill="none", stroke=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polygon(points, fill=INK, stroke="none", sw=0):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, color=INK, w=2.4, fill="none", dash=None, marker=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{_MARK.get(marker, "aInk")})"' if marker else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{w}"{da}{mk}/>\n'


def save(name, body):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body + footer())
    print("wrote", name)


# ── магнітні примітиви ────────────────────────────────────────────────────────
def bar_magnet(x, y, w, h, n_left=True, label_n="N", label_s="S"):
    """Горизонтальний штабовий магніт; ліва половина — N (червона), права — S (синя)
    якщо n_left=True. Повертає рядок SVG."""
    out = ""
    half = w / 2
    if n_left:
        out += rect(x, y, half, h, "#fbe3e1", RED, 2.0)
        out += rect(x + half, y, half, h, "#e2e9f7", BLUE, 2.0)
        out += text(x + half / 2, y + h / 2 + 8, label_n, 22, RED, "middle", "bold")
        out += text(x + half + half / 2, y + h / 2 + 8, label_s, 22, BLUE, "middle", "bold")
    else:
        out += rect(x, y, half, h, "#e2e9f7", BLUE, 2.0)
        out += rect(x + half, y, half, h, "#fbe3e1", RED, 2.0)
        out += text(x + half / 2, y + h / 2 + 8, label_s, 22, BLUE, "middle", "bold")
        out += text(x + half + half / 2, y + h / 2 + 8, label_n, 22, RED, "middle", "bold")
    return out


def vbar_magnet(x, y, w, h, n_top=True):
    """Вертикальний штабовий магніт; верхня половина N якщо n_top."""
    out = ""
    half = h / 2
    if n_top:
        out += rect(x, y, w, half, "#fbe3e1", RED, 2.0)
        out += rect(x, y + half, w, half, "#e2e9f7", BLUE, 2.0)
        out += text(x + w / 2, y + half / 2 + 8, "N", 22, RED, "middle", "bold")
        out += text(x + w / 2, y + half + half / 2 + 8, "S", 22, BLUE, "middle", "bold")
    else:
        out += rect(x, y, w, half, "#e2e9f7", BLUE, 2.0)
        out += rect(x, y + half, w, half, "#fbe3e1", RED, 2.0)
        out += text(x + w / 2, y + half / 2 + 8, "S", 22, BLUE, "middle", "bold")
        out += text(x + w / 2, y + half + half / 2 + 8, "N", 22, RED, "middle", "bold")
    return out


def current_out(cx, cy, r=10, color=ORANGE, w=2.4):
    """Струм НА нас: кружок з крапкою (вістря стріли)."""
    out = circle(cx, cy, r, "#ffffff", color, w)
    out += circle(cx, cy, 2.4, color, color, 1)
    return out


def current_in(cx, cy, r=10, color=ORANGE, w=2.4):
    """Струм ВІД нас: кружок з хрестиком (хвіст стріли)."""
    d = r * 0.62
    out = circle(cx, cy, r, "#ffffff", color, w)
    out += line(cx - d, cy - d, cx + d, cy + d, color, w)
    out += line(cx - d, cy + d, cx + d, cy - d, color, w)
    return out


def arc(cx, cy, r, a0_deg, a1_deg, color=INK, w=2.4, marker=None, dash=None):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1_deg - a0_deg) > 180 else 0
    sweep = 1 if a1_deg > a0_deg else 0
    da = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{_MARK.get(marker, "aInk")})"' if marker else ""
    return (f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 {large} {sweep} {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{da}{mk}/>\n')


def _bezier_loop(x0, y0, cx1, cy1, cx2, cy2, x1, y1, color=GREEN, w=2.0, marker=None):
    mk = f' marker-end="url(#{_MARK.get(marker, "aGreen")})"' if marker else ""
    return (f'<path d="M {x0:.1f} {y0:.1f} C {cx1:.1f} {cy1:.1f} {cx2:.1f} {cy2:.1f} {x1:.1f} {y1:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{mk}/>\n')


def horiz_dipole_field(cx, cy, mag_w, mag_h, color=GREEN):
    """Силові лінії горизонтального диполя (N ліворуч, S праворуч): петлі від лівого кінця
    до правого, угорі й унизу, плюс пряма лінія крізь зовнішній простір."""
    out = ""
    nx = cx - mag_w / 2          # лівий кінець (N)
    sx = cx + mag_w / 2          # правий кінець (S)
    loops = [40, 80, 120, 165]   # вертикальний «виліт» петлі
    for k, h in enumerate(loops):
        # верхня петля: від N угору-направо й вниз до S
        out += _bezier_loop(nx, cy, nx - 0, cy - h, sx + 0, cy - h, sx, cy,
                            color, 2.0, marker=None)
        # стрілка посередині верхньої петлі (праворуч — поле виходить з N, тече до S зовні)
        midx = cx
        midy = cy - h * 0.92
        out += arrow(midx - 6, midy, midx + 6, midy, color, 2.0)
        # нижня петля
        out += _bezier_loop(nx, cy, nx - 0, cy + h, sx + 0, cy + h, sx, cy,
                            color, 2.0, marker=None)
        out += arrow(midx - 6, cy + h * 0.92, midx + 6, cy + h * 0.92, color, 2.0)
    return out


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.1 — Магніти й поле B: полюси, силові лінії, монополів немає.  Рис. 8.1.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 8.1.1 — силові лінії штабового магніту (картина поля B) ──────────────
def fig_dipole_lines():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 30, "Поле штабового магніту: лінії виходять з N, входять у S",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "густіше лінії — сильніше поле (біля полюсів); стрілка лінії показує напрям B у кожній точці",
              11.5, GREY, "middle", style="italic")
    cx, cy = W / 2, 270
    mw, mh = 200, 70
    s += horiz_dipole_field(cx, cy, mw, mh)
    s += bar_magnet(cx - mw / 2, cy - mh / 2, mw, mh)
    # позначити густину біля полюса
    s += text(cx - mw / 2 - 14, cy - 96, "лінії гущі біля полюсів → поле сильніше",
              11, GREEN, "end", "bold")
    s += arrow(cx - mw / 2 - 16, cy - 90, cx - mw / 2 - 4, cy - 40, GREEN, 1.6, dash="4,3")
    # маленька стрілка-компас у полі (напрям B)
    needx, needy = cx + 150, cy - 70
    s += line(needx - 18, needy + 6, needx + 18, needy - 6, INK, 5)
    s += polygon([(needx + 18, needy - 6), (needx + 10, needy - 12), (needx + 12, needy - 2)], RED)
    s += text(needx + 24, needy + 2, "стрілка вздовж B", 10.5, INK, "start", "bold")
    s += text(W / 2, H - 18, "Поле B — векторне (як E у §1.1.3): у кожній точці має напрям і величину. Лінії — спосіб це намалювати.",
              11.5, INK, "middle", "bold")
    save("fig-8-1-1-dipole-lines.svg", s)


# ── Рис. 8.1.2 — притягання/відштовхування полюсів ───────────────────────────
def fig_poles_force():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 30, "Правило полюсів: різнойменні притягуються, однойменні відштовхуються",
              18, INK, "middle", "bold")
    mw, mh = 150, 56
    # ── ЛІВО: N—S зближені → притягання ──
    y0 = 150
    s += text(225, 92, "різнойменні (N ↔ S)", 13, INK, "middle", "bold")
    s += bar_magnet(80, y0 - mh / 2, mw, mh, n_left=True)         # N S
    s += bar_magnet(80 + mw + 60, y0 - mh / 2, mw, mh, n_left=True)  # N S
    # сили назустріч
    s += arrow(80 + mw + 6, y0, 80 + mw + 52, y0, PURPLE, 3.2)
    s += arrow(80 + mw + 54, y0, 80 + mw + 8, y0, PURPLE, 3.2)
    s += text(225, y0 + 60, "ПРИТЯГАННЯ", 13, GREEN, "middle", "bold")
    s += text(225, y0 + 78, "S зустрічає N", 10.5, GREY, "middle")
    # ── ПРАВО: N—N → відштовхування ──
    s += text(690, 92, "однойменні (N ↔ N)", 13, INK, "middle", "bold")
    s += bar_magnet(545, y0 - mh / 2, mw, mh, n_left=True)        # N S
    s += bar_magnet(545 + mw + 60, y0 - mh / 2, mw, mh, n_left=False)  # S N
    # сили врозтіч
    s += arrow(545 + mw + 30, y0, 545 + mw - 16, y0, PURPLE, 3.2)
    s += arrow(545 + mw + 30, y0, 545 + mw + 76, y0, PURPLE, 3.2)
    s += text(690, y0 + 60, "ВІДШТОВХУВАННЯ", 13, RED, "middle", "bold")
    s += text(690, y0 + 78, "S зустрічає N", 10.5, GREY, "middle")
    s += text(W / 2, H - 18, "Сила діє між полюсами; та сама двійка знаків, що й у зарядів — але полюси нероздільні (див. далі).",
              11.5, INK, "middle", "bold")
    save("fig-8-1-2-poles-force.svg", s)


# ── Рис. 8.1.3 — розпил магніту: монополя не буде ────────────────────────────
def fig_no_monopole():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Чому немає монополя: ріж магніт скільки хочеш — щоразу новий N і S",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "полюс — не «частинка магнітного заряду», а кінець диполя; кожен уламок знову має два кінці",
              11.5, GREY, "middle", style="italic")
    mw, mh = 360, 60

    def seg_magnet(x, y, w):
        half = w / 2
        out = rect(x, y, half, mh, "#fbe3e1", RED, 1.8)
        out += rect(x + half, y, half, mh, "#e2e9f7", BLUE, 1.8)
        out += text(x + half / 2, y + mh / 2 + 7, "N", 17, RED, "middle", "bold")
        out += text(x + half + half / 2, y + mh / 2 + 7, "S", 17, BLUE, "middle", "bold")
        return out

    # рівень 1: цілий
    y1 = 95
    s += seg_magnet(W / 2 - mw / 2, y1, mw)
    s += text(W / 2 + mw / 2 + 16, y1 + mh / 2 + 5, "цілий магніт", 11.5, INK, "start", "bold")
    # стрілка «розрізати»
    s += arrow(W / 2, y1 + mh + 6, W / 2, y1 + mh + 34, INK, 2.4)
    s += text(W / 2 + 10, y1 + mh + 26, "розрізати посередині", 10.5, INK, "start", "bold")
    # рівень 2: дві половини
    y2 = 200
    w2 = mw / 2 - 14
    s += seg_magnet(W / 2 - mw / 2, y2, w2)
    s += seg_magnet(W / 2 + 14, y2, w2)
    s += text(W / 2 + mw / 2 + 16, y2 + mh / 2 + 5, "дві половини", 11.5, INK, "start", "bold")
    s += arrow(W / 2, y2 + mh + 6, W / 2, y2 + mh + 34, INK, 2.4)
    s += text(W / 2 + 10, y2 + mh + 26, "знову розрізати", 10.5, INK, "start", "bold")
    # рівень 3: чотири шматки
    y3 = 305
    w3 = mw / 4 - 12
    for k in range(4):
        x = W / 2 - mw / 2 + k * (w3 + 16)
        s += seg_magnet(x, y3, w3)
    s += text(W / 2 + mw / 2 + 16, y3 + mh / 2 + 5, "…і так до атома", 11.5, INK, "start", "bold")
    s += text(W / 2, H - 16, "Аж до атома: кожен уламок — повний диполь. Окремого «магнітного заряду» (монополя) ніхто не спостерігав.",
              11.5, INK, "middle", "bold")
    save("fig-8-1-3-no-monopole.svg", s)


# ── Рис. 8.1.4 — порівняння поля E (від заряду) і B (від диполя): є/нема джерела
def fig_e_vs_b():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 30, "Два векторні поля курсу: E має джерело-заряд, у B джерел немає",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "лінії E починаються й кінчаються на зарядах; лінії B завжди замкнені — ні початку, ні кінця",
              11.5, GREY, "middle", style="italic")
    # ── ЛІВО: поле точкового +заряду — лінії радіально назовні ──
    cxE, cyE = 240, 230
    s += text(cxE, 92, "ЕЛЕКТРИЧНЕ поле E", 13.5, RED, "middle", "bold")
    for a in range(0, 360, 30):
        ar = math.radians(a)
        x2 = cxE + 120 * math.cos(ar)
        y2 = cyE + 120 * math.sin(ar)
        x1 = cxE + 26 * math.cos(ar)
        y1 = cyE + 26 * math.sin(ar)
        s += arrow(x1, y1, x2, y2, RED, 1.8)
    s += circle(cxE, cyE, 20, "#fbe3e1", RED, 2.2)
    s += text(cxE, cyE + 6, "+", 22, RED, "middle", "bold")
    s += text(cxE, cyE + 150, "лінії ВИХОДЯТЬ із заряду (є початок)", 11, RED, "middle", "bold")
    # ── ПРАВО: поле магнітного диполя — замкнені петлі ──
    cxB, cyB = 660, 230
    s += text(cxB, 92, "МАГНІТНЕ поле B", 13.5, GREEN, "middle", "bold")
    mw, mh = 120, 44
    s += horiz_dipole_field(cxB, cyB, mw, mh)
    s += bar_magnet(cxB - mw / 2, cyB - mh / 2, mw, mh)
    s += text(cxB, cyB + 150, "лінії ЗАМКНЕНІ (нема ні початку, ні кінця)", 11, GREEN, "middle", "bold")
    s += text(W / 2, H - 16, "Це і є зміст «монополя немає»: магнітні лінії нікуди не «втикаються» — вони завжди утворюють петлю.",
              11.5, INK, "middle", "bold")
    save("fig-8-1-4-e-vs-b.svg", s)


# ── Рис. 8.1.5 — як вимірюють силу поля: тесла, гаус, орієнтири ───────────────
def fig_b_scale():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 30, "Чим міряють поле B: одиниця — тесла (Тл), орієнтири величини",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "1 Тл = 10 000 Гс (гаус); шкала логарифмічна — від поля Землі до МРТ та найсильніших лабораторних",
              11, GREY, "middle", style="italic")
    ax, ay, aw = 90, 300, 740
    s += line(ax, ay, ax + aw, ay, INK, 2.2)
    # логарифмічна шкала від 1e-5 до 1e2 Тл (7 декад)
    decades = [(-5, "10⁻⁵", "поле Землі ≈ 50 мкТл"),
               (-4, "10⁻⁴", ""),
               (-3, "10⁻³", "магніт на дверцятах"),
               (-2, "10⁻²", ""),
               (-1, "10⁻¹", "феритовий магніт ≈ 0.1–0.3 Тл"),
               (0, "10⁰", "неодимовий ≈ 0.5–1.4 Тл"),
               (1, "10¹", "МРТ-сканер ≈ 1.5–3 Тл"),
               (2, "10²", "найсильніші лаб. (десятки Тл)")]
    n = len(decades)
    for i, (e, lab, note) in enumerate(decades):
        x = ax + aw * i / (n - 1)
        s += line(x, ay - 7, x, ay + 7, INK, 2)
        s += text(x, ay + 26, lab, 12, INK, "middle", "bold")
        s += text(x, ay + 42, "Тл", 9.5, GREY, "middle")
        if note:
            yy = ay - 30 - (i % 4) * 42
            s += line(x, ay - 8, x, yy + 8, GREY, 1.1, "3,3")
            s += circle(x, yy, 4, GREEN, GREEN, 1)
            s += text(x, yy - 8, note, 10.5, INK, "middle", "bold")
    save("fig-8-1-5-b-scale.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.2 — Магнетизм матерії: домени й феромагнетики.  Рис. 8.2.k
# ════════════════════════════════════════════════════════════════════════════

def _domain_arrow(cx, cy, ang_deg, L=22, color=INK, w=3.0):
    a = math.radians(ang_deg)
    x2 = cx + L * math.cos(a)
    y2 = cy + L * math.sin(a)
    x1 = cx - L * math.cos(a)
    y1 = cy - L * math.sin(a)
    return arrow(x1, y1, x2, y2, color, w)


# ── Рис. 8.2.1 — спін електрона як крихітний магнітик ─────────────────────────
def fig_spin_magnet():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 30, "Звідки магнетизм у матерії: електрон сам — крихітний магніт",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "магнітний момент дає переважно власний спін електрона (плюс рух по орбіталі); атом — сума цих моментів",
              11, GREY, "middle", style="italic")
    # ── ліво: електрон зі спіном → стрілка моменту ──
    cx, cy = 200, 200
    s += circle(cx, cy, 26, "#e2e9f7", BLUE, 2.2)
    s += text(cx, cy + 6, "e⁻", 16, BLUE, "middle", "bold")
    s += arc(cx, cy, 40, 200, 520, INK, 1.8, marker="aInk")
    s += text(cx + 52, cy - 30, "спін", 11, INK, "start", "bold")
    s += arrow(cx, cy + 60, cx, cy - 62, GREEN, 3.0)
    s += text(cx + 8, cy - 56, "магнітний момент μ", 11, GREEN, "start", "bold")
    s += text(cx, cy + 96, "кожен електрон = мікромагніт", 11, INK, "middle", "bold")
    # ── право: атом, де моменти гасяться (пара ↑↓) проти незкомпенсованих ──
    bx = 470
    s += rect(bx, 110, 170, 170, "#fafafa", GREY, 1.4, 8)
    s += text(bx + 85, 132, "більшість речовин", 11.5, INK, "middle", "bold")
    # пари ↑↓
    for i, yy in enumerate((160, 200, 240)):
        s += _domain_arrow(bx + 55, yy, -90, 16, BLUE, 2.6)
        s += _domain_arrow(bx + 115, yy, 90, 16, BLUE, 2.6)
    s += text(bx + 85, 268, "моменти в парах гасяться → 0", 9.5, GREY, "middle")
    bx2 = 690
    s += rect(bx2, 110, 170, 170, "#eef7f0", GREEN, 1.6, 8)
    s += text(bx2 + 85, 132, "залізо, нікель, кобальт", 11.5, GREEN, "middle", "bold")
    for i, yy in enumerate((160, 200, 240)):
        s += _domain_arrow(bx2 + 55, yy, -90, 16, GREEN, 2.8)
        s += _domain_arrow(bx2 + 95, yy, -90, 16, GREEN, 2.8)
        s += _domain_arrow(bx2 + 135, yy, -90, 16, GREEN, 2.8)
    s += text(bx2 + 85, 268, "є незкомпенсовані спіни → атом магнітний", 9, GREEN, "middle")
    save("fig-8-2-1-spin-magnet.svg", s)


# ── Рис. 8.2.2 — домени: невпорядковані → вишикувані в полі ───────────────────
def fig_domains():
    W, H = 940, 470
    s = header(W, H)
    s += text(W / 2, 30, "Домени: чому залізо магнітне лише після намагнічування",
              18.5, INK, "middle", "bold")
    s += text(W / 2, 52, "у залізі атоми вже вишикувані в межах доменів; зовнішнє поле повертає й розширює «правильні» домени",
              11, GREY, "middle", style="italic")

    def domain_block(x, y, w, h, angles, title, sub):
        out = rect(x, y, w, h, "#ffffff", INK, 2.0, 6)
        out += text(x + w / 2, y - 10, title, 13, INK, "middle", "bold")
        # сітка доменів 3x3
        nx, ny = 3, 3
        dw, dh = w / nx, h / ny
        idx = 0
        for r in range(ny):
            for c in range(nx):
                cxw = x + c * dw + dw / 2
                cyw = y + r * dh + dh / 2
                ang = angles[idx % len(angles)]
                out += line(x + c * dw, y, x + c * dw, y + h, FAINT, 1)
                out += line(x, y + r * dh, x + w, y + r * dh, FAINT, 1)
                col = GREEN if abs(((ang + 180) % 360) - 180) < 1 else INK
                out += _domain_arrow(cxw, cyw, ang, 22, col, 3.0)
                idx += 1
        out += text(x + w / 2, y + h + 22, sub, 10.5, GREY, "middle", style="italic")
        return out

    import random
    random.seed(7)
    rand_ang = [random.choice([0, 45, 90, 135, 180, 225, 270, 315]) for _ in range(9)]
    s += domain_block(70, 120, 220, 200, rand_ang,
                      "не намагнічене", "домени дивляться врізнобіч → зовні поля немає")
    # зовнішнє поле H праворуч
    s += arrow(312, 220, 372, 220, ORANGE, 3.4)
    s += text(342, 206, "поле H", 11, ORANGE, "middle", "bold")
    # частково
    part = [0, 0, 45, 0, 0, 90, 0, 315, 0]
    s += domain_block(390, 120, 220, 200, part,
                      "у слабкому полі", "«правильні» домени ростуть, інші повертаються")
    s += arrow(632, 220, 692, 220, ORANGE, 3.4)
    s += text(662, 206, "сильніше", 11, ORANGE, "middle", "bold")
    aligned = [0] * 9
    s += domain_block(710, 120, 220, 200, aligned,
                      "насичення", "усі домени вздовж поля → магніт сильний")
    s += text(W / 2, H - 18, "Намагнічування — це не «вливання магнетизму», а вишиковування того, що вже є всередині.",
              11.5, INK, "middle", "bold")
    save("fig-8-2-2-domains.svg", s)


# ── Рис. 8.2.3 — три класи: феро-, пара-, діамагнетики ───────────────────────
def fig_magnetic_classes():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 30, "Три відповіді матерії на поле: феро-, пара- і діамагнетики",
              18, INK, "middle", "bold")
    cols = [
        ("ФЕРОМАГНЕТИКИ", "залізо, нікель, кобальт", GREEN,
         "сильно втягуються; лишаються магнітними", "μr ≈ сотні–тисячі"),
        ("ПАРАМАГНЕТИКИ", "алюміній, платина, кисень", ORANGE,
         "трохи втягуються; ефект зникає без поля", "μr ≈ 1.000…1"),
        ("ДІАМАГНЕТИКИ", "мідь, вода, графіт, золото", BLUE,
         "слабко виштовхуються з поля", "μr трохи < 1"),
    ]
    bw = 280
    for i, (title, mats, col, eff, mu) in enumerate(cols):
        x = 30 + i * (bw + 12)
        s += rect(x, 80, bw, 230, "#ffffff", col, 2.0, 10)
        s += text(x + bw / 2, 108, title, 13.5, col, "middle", "bold")
        s += text(x + bw / 2, 130, mats, 10.5, INK, "middle")
        # стрілочки: реакція на поле
        cyB = 185
        s += rect(x + 30, cyB - 28, bw - 60, 56, "#fafafa", GREY, 1.2, 6)
        s += text(x + bw / 2, cyB - 36, "у зовнішньому полі →", 9.5, GREY, "middle", style="italic")
        if col == GREEN:
            for k in range(5):
                s += _domain_arrow(x + 45 + k * 42, cyB, 0, 14, col, 3.0)
        elif col == ORANGE:
            angs = [0, 12, 0, -10, 5]
            for k in range(5):
                s += _domain_arrow(x + 45 + k * 42, cyB, angs[k], 12, col, 2.4)
        else:
            angs = [80, 100, 70, 110, 90]
            for k in range(5):
                s += _domain_arrow(x + 45 + k * 42, cyB, angs[k], 12, col, 2.0)
        s += text(x + bw / 2, 250, eff, 10.5, INK, "middle", "bold")
        s += text(x + bw / 2, 286, mu, 12, col, "middle", "bold", "italic")
    s += text(W / 2, H - 14, "Чому мідь не магнітна, а залізо — так: справа не в «металі взагалі», а в тому, як шикуються спіни.",
              11.5, INK, "middle", "bold")
    save("fig-8-2-3-magnetic-classes.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.3 — Постійні магніти: ферит і неодим; Кюрі; розмагнічування. Рис.8.3.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 8.3.1 — тверді vs м'які магнітні матеріали (петля широка/вузька) ─────
def fig_hard_soft():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 30, "Постійний магніт — це «тверда» магнітна пам'ять речовини",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "тверді матеріали утримують вишикувані домени навіть без поля; м'які — відпускають їх одразу",
              11, GREY, "middle", style="italic")

    def loop(cx, cy, wide, col, title, sub):
        out = ""
        ax, ay = cx, cy
        out += arrow(ax - 130, ay, ax + 130, ay, GREY, 1.4)   # H
        out += arrow(ax, ay + 95, ax, ay - 95, GREY, 1.4)     # B/M
        out += text(ax + 128, ay + 18, "H", 11, GREY, "middle", "bold", "italic")
        out += text(ax + 16, ay - 88, "M", 11, GREY, "middle", "bold", "italic")
        # петля гістерезису як два безьє
        wx = wide
        out += path(f"M {ax-120} {ay+55} C {ax-wx} {ay-70}, {ax+wx*0.2} {ay-78}, {ax+120} {ay-55} "
                    f"C {ax+wx} {ay+70}, {ax-wx*0.2} {ay+78}, {ax-120} {ay+55} Z",
                    col, 2.6)
        out += text(ax, cy - 110, title, 13, col, "middle", "bold")
        out += text(ax, cy + 118, sub, 10.5, INK, "middle", "bold")
        return out

    s += loop(240, 220, 70, GREEN, "ТВЕРДИЙ (ферит, неодим)",
              "широка петля → лишається намагніченим")
    s += text(240, 354, "годиться для постійного магніту", 10, GREY, "middle", style="italic")
    s += loop(680, 220, 8, BLUE, "М'ЯКИЙ (трансформаторне залізо)",
              "вузька петля → магнетизм зникає з полем")
    s += text(680, 354, "годиться для осердя електромагніту (§1.8.6)", 10, GREY, "middle", style="italic")
    save("fig-8-3-1-hard-soft.svg", s)


# ── Рис. 8.3.2 — температура Кюрі: вище неї магнетизм зникає ──────────────────
def fig_curie():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 30, "Температура Кюрі: нагрій магніт — і магнетизм зникне",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "теплові коливання атомів руйнують вишиковування спінів; вище T_C матеріал стає звичайним парамагнетиком",
              11, GREY, "middle", style="italic")
    ax, ay, aw, ah = 110, 300, 600, 200
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.5)
    s += arrow(ax, ay, ax, ay - ah - 12, GREY, 1.5)
    s += text(ax + aw + 6, ay + 20, "температура T", 11.5, GREY, "start", "bold")
    s += text(ax - 8, ay - ah - 4, "намагніченість M", 11.5, GREY, "end", "bold")
    # крива M(T): спадає, круто падає біля Tc
    Tc_frac = 0.74
    pts = []
    N = 120
    for i in range(N + 1):
        t = i / N
        if t < Tc_frac:
            m = (1 - (t / Tc_frac) ** 3) ** 0.5
        else:
            m = 0
        pts.append((ax + t * aw, ay - m * ah))
    s += polyline(pts, RED, 3.0)
    xc = ax + Tc_frac * aw
    s += line(xc, ay, xc, ay - ah - 6, GREEN, 1.6, "5,4")
    s += text(xc, ay - ah - 14, "T_C (точка Кюрі)", 12, GREEN, "middle", "bold")
    s += text(ax + 30, ay - ah + 24, "магніт працює", 11, INK, "start", "bold")
    s += text(xc + 20, ay - 30, "магнетизму немає", 11, GREY, "start", "bold")
    # орієнтири
    s += text(W / 2, H - 16, "Орієнтири: ферит ≈ 450 °C, неодим (NdFeB) ≈ 310–340 °C, залізо ≈ 770 °C, кобальт ≈ 1115 °C.",
              11, INK, "middle", "bold")
    save("fig-8-3-2-curie.svg", s)


# ── Рис. 8.3.3 — три способи розмагнітити ────────────────────────────────────
def fig_demagnetize():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 30, "Три способи зруйнувати магніт: нагрів, удар, зустрічне поле",
              18, INK, "middle", "bold")
    bw = 280
    # 1: нагрів
    x = 30
    s += rect(x, 80, bw, 230, "#ffffff", RED, 2.0, 10)
    s += text(x + bw / 2, 108, "НАГРІВ вище T_C", 13, RED, "middle", "bold")
    s += text(x + bw / 2, 150, "🔥", 26, RED, "middle")
    s += _domain_arrow(x + 80, 200, 20, 16, GREY, 2.4)
    s += _domain_arrow(x + 130, 195, 200, 16, GREY, 2.4)
    s += _domain_arrow(x + 180, 205, 110, 16, GREY, 2.4)
    s += text(x + bw / 2, 250, "теплові коливання збивають", 10, INK, "middle")
    s += text(x + bw / 2, 268, "домени врізнобіч", 10, INK, "middle")
    # 2: удар
    x = 330
    s += rect(x, 80, bw, 230, "#ffffff", ORANGE, 2.0, 10)
    s += text(x + bw / 2, 108, "СИЛЬНИЙ УДАР", 13, ORANGE, "middle", "bold")
    s += polygon([(x + bw / 2 - 20, 140), (x + bw / 2 + 4, 158), (x + bw / 2 - 6, 162),
                  (x + bw / 2 + 14, 184)], ORANGE)
    s += _domain_arrow(x + 80, 215, 60, 16, GREY, 2.4)
    s += _domain_arrow(x + 130, 210, 250, 16, GREY, 2.4)
    s += _domain_arrow(x + 180, 220, 140, 16, GREY, 2.4)
    s += text(x + bw / 2, 250, "струс зриває домени", 10, INK, "middle")
    s += text(x + bw / 2, 268, "з вишикуваного стану", 10, INK, "middle")
    # 3: зустрічне поле
    x = 630
    s += rect(x, 80, bw, 230, "#ffffff", BLUE, 2.0, 10)
    s += text(x + bw / 2, 108, "ЗУСТРІЧНЕ поле", 13, BLUE, "middle", "bold")
    s += arrow(x + bw / 2 + 40, 150, x + bw / 2 - 40, 150, BLUE, 3.2)
    s += text(x + bw / 2, 138, "H проти намагніченості", 9.5, BLUE, "middle", "bold")
    for k in range(4):
        s += _domain_arrow(x + 70 + k * 40, 210, 0 if k % 2 else 180, 14, GREY, 2.4)
    s += text(x + bw / 2, 250, "перевертає частину доменів", 10, INK, "middle")
    s += text(x + bw / 2, 268, "(коерцитивна сила H_c)", 10, INK, "middle")
    s += text(W / 2, H - 14, "Магніт не «розряджається» сам — псувати його доводиться ззовні. У спокої домени тримаються роками.",
              11.5, INK, "middle", "bold")
    save("fig-8-3-3-demagnetize.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.4 — Струм народжує поле: Ерстед і правило правої руки.  Рис. 8.4.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 8.4.1 — дослід Ерстеда: струм відхиляє компас ───────────────────────
def fig_oersted():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 30, "Дослід Ерстеда (1820): струм у дроті повертає магнітну стрілку",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "без струму стрілка дивиться на північ; пустиш струм — вона повертається поперек дроту",
              11, GREY, "middle", style="italic")

    def compass(cx, cy, ang_deg, label):
        out = circle(cx, cy, 30, "#fafafa", GREY, 1.6)
        a = math.radians(ang_deg)
        nx, ny = cx + 26 * math.sin(a), cy - 26 * math.cos(a)
        sx, sy = cx - 26 * math.sin(a), cy + 26 * math.cos(a)
        out += line(sx, sy, nx, ny, BLUE, 4)
        out += polygon([(nx, ny),
                        (nx - 6 * math.cos(a) - 4 * math.sin(a), ny - 6 * math.sin(a) + 4 * math.cos(a)),
                        (nx + 6 * math.cos(a) - 4 * math.sin(a), ny + 6 * math.sin(a) + 4 * math.cos(a))],
                       RED)
        out += text(cx, cy + 50, label, 10.5, INK, "middle", "bold")
        return out

    # ── ЛІВО: струму нема — стрілка на N ──
    s += text(240, 96, "СТРУМУ НЕМА", 13, GREY, "middle", "bold")
    s += line(120, 160, 360, 160, INK, 4)
    s += text(380, 165, "дріт", 10.5, INK, "start", "bold")
    s += text(120, 145, "↑ Пн", 11, GREEN, "middle", "bold")
    s += compass(240, 230, 0, "стрілка на північ")
    # ── ПРАВО: є струм — стрілка повертається ──
    s += text(690, 96, "Є СТРУМ I", 13, ORANGE, "middle", "bold")
    s += arrow(560, 160, 820, 160, ORANGE, 4)
    s += text(835, 165, "I", 12, ORANGE, "start", "bold", "italic")
    s += compass(690, 230, 68, "повернулась поперек")
    # стрілки поля навколо дроту
    s += text(W / 2, H - 16, "Висновок Ерстеда: електрика й магнетизм пов'язані — рухомий заряд створює магнітне поле.",
              11.5, INK, "middle", "bold")
    save("fig-8-4-1-oersted.svg", s)


# ── Рис. 8.4.2 — поле прямого провідника: концентричні кільця + права рука ───
def fig_wire_field():
    W, H = 940, 440
    s = header(W, H)
    s += text(W / 2, 30, "Поле навколо прямого дроту: концентричні кільця; правило правої руки",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "обхопи дріт правою рукою так, щоб великий палець показував струм I — пальці згинаються вздовж B",
              11, GREY, "middle", style="italic")
    # ── ЛІВО: погляд збоку — дріт вертикальний, кільця в перерізах ──
    wx = 230
    s += arrow(wx, 360, wx, 110, ORANGE, 4)
    s += text(wx + 8, 120, "I", 13, ORANGE, "start", "bold", "italic")
    for r in (40, 70, 100):
        # еліпс-кільце (перспектива) на двох рівнях
        for yy in (190, 290):
            s += f'<ellipse cx="{wx}" cy="{yy}" rx="{r}" ry="{r*0.32}" fill="none" stroke="{GREEN}" stroke-width="1.8"/>\n'
        # стрілка напряму на ближньому краї кільця (проти год. стрілки згори)
    s += arrow(wx + 70, 190 + 22, wx + 70 + 1, 190 + 22, GREEN, 2.2)
    s += arrow(wx - 70, 290 - 22, wx - 70 - 1, 290 - 22, GREEN, 2.2)
    s += text(wx, 392, "кільця охоплюють дріт", 10.5, INK, "middle", "bold")
    s += text(wx + 110, 240, "B", 13, GREEN, "start", "bold", "italic")
    # ── ПРАВО: переріз — крапка/хрест + кільце з напрямком ──
    cx, cy = 680, 240
    s += text(cx, 96, "переріз дроту", 12, INK, "middle", "bold")
    s += current_out(cx, cy, 14, ORANGE, 3)
    s += text(cx + 24, cy + 4, "I на нас", 10.5, ORANGE, "start", "bold")
    for r in (50, 85, 120):
        s += circle(cx, cy, r, "none", GREEN, 1.8)
    # стрілки проти годинникової (для струму на нас)
    for a in (30, 120, 210, 300):
        ar = math.radians(a)
        px, py = cx + 85 * math.cos(ar), cy + 85 * math.sin(ar)
        # дотична проти год. стрілки
        tx, ty = px - 16 * math.sin(ar), py + 16 * math.cos(ar)
        s += arrow(px, py, tx, ty, GREEN, 2.2)
    s += text(cx + 130, cy - 60, "B проти год. стрілки", 10.5, GREEN, "start", "bold")
    s += text(cx, cy + 150, "струм НА нас → поле проти годинникової", 10.5, INK, "middle", "bold")
    save("fig-8-4-2-wire-field.svg", s)


# ── Рис. 8.4.3 — поле витка/петлі: складання, диполь ─────────────────────────
def fig_loop_field():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 30, "Згорни дріт у виток — і поле всередині складається в одному напрямі",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "по обидва боки витка поле дивиться в один бік крізь отвір; зовні виток поводиться як маленький магніт",
              11, GREY, "middle", style="italic")
    cx, cy = W / 2, 230
    # виток у перерізі: дві крапки/хрести (верх і низ кільця)
    R = 120
    s += f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{R*0.9}" fill="none" stroke="{ORANGE}" stroke-width="3.2"/>\n'
    # струм: на верхньому краї — від нас, на нижньому — на нас
    s += current_in(cx, cy - R * 0.9, 13, ORANGE, 3)
    s += current_out(cx, cy + R * 0.9, 13, ORANGE, 3)
    s += text(cx + 16, cy - R * 0.9 - 6, "I", 12, ORANGE, "start", "bold", "italic")
    # поле крізь виток (вісь) — управо
    for yy in (cy - 40, cy, cy + 40):
        s += arrow(cx - 50, yy, cx + 70, yy, GREEN, 2.4)
    s += text(cx + 80, cy - 50, "B усередині", 11, GREEN, "start", "bold")
    # замикання поля зовні (петлі)
    s += arc(cx, cy, R + 70, -70, 70, GREEN, 1.8)
    s += arc(cx, cy, R + 70, 110, 250, GREEN, 1.8)
    # позначити еквівалентні полюси
    s += text(cx + R + 90, cy, "N", 18, RED, "start", "bold")
    s += text(cx - R - 90, cy, "S", 18, BLUE, "end", "bold")
    s += text(W / 2, H - 16, "Виток зі струмом = магнітний диполь: один бік поводиться як N, другий — як S (зв'язок із §1.8.1).",
              11.5, INK, "middle", "bold")
    save("fig-8-4-3-loop-field.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.5 — Електромагніт: котушка, осердя, ампер-витки.  Рис. 8.5.k
# ════════════════════════════════════════════════════════════════════════════

def _solenoid(cx, cy, length, radius, turns, color=COPPER, w=3.0):
    """Соленоїд: ряд еліпсів-витків уздовж горизонтальної осі."""
    out = ""
    step = length / turns
    x0 = cx - length / 2
    for i in range(turns):
        x = x0 + i * step + step / 2
        out += f'<ellipse cx="{x:.1f}" cy="{cy:.1f}" rx="{step*0.36:.1f}" ry="{radius:.1f}" fill="none" stroke="{color}" stroke-width="{w}"/>\n'
    return out


# ── Рис. 8.5.1 — соленоїд: багато витків → однорідне поле всередині ───────────
def fig_solenoid():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 30, "Соленоїд: складаємо поля багатьох витків в одне сильне й рівне",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "усередині довгої котушки поля витків додаються й вирівнюються; зовні картина — як у штабового магніту",
              11, GREY, "middle", style="italic")
    cx, cy = W / 2, 230
    L, R, N = 380, 70, 11
    # зовнішнє поле (петлі як у диполя)
    s += horiz_dipole_field(cx, cy, L, R * 2)
    s += _solenoid(cx, cy, L, R, N)
    # поле всередині — пряме, управо
    for yy in (cy - 35, cy, cy + 35):
        s += arrow(cx - L / 2 + 20, yy, cx + L / 2 - 20, yy, GREEN, 2.6)
    s += text(cx, cy - 8, "B усередині — рівне й сильне", 11, GREEN, "middle", "bold")
    # полюси
    s += text(cx + L / 2 + 20, cy + 5, "N", 18, RED, "start", "bold")
    s += text(cx - L / 2 - 20, cy + 5, "S", 18, BLUE, "end", "bold")
    # підведення струму
    s += arrow(cx - L / 2 - 60, cy - R - 20, cx - L / 2 - 6, cy - R - 6, ORANGE, 3)
    s += text(cx - L / 2 - 64, cy - R - 26, "I", 12, ORANGE, "end", "bold", "italic")
    s += text(W / 2, H - 16, "Більше витків N і більший струм I → сильніше поле. Напрям — за правою рукою (пальці = струм витків).",
              11.5, INK, "middle", "bold")
    save("fig-8-5-1-solenoid.svg", s)


# ── Рис. 8.5.2 — ампер-витки: повітря vs осердя ──────────────────────────────
def fig_ampere_turns():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 30, "Що задає силу електромагніту: ампер-витки (N·I) і осердя",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "однакова магніторушійна сила N·I; з феромагнітним осердям те саме N·I дає в сотні разів сильніше поле",
              11, GREY, "middle", style="italic")
    # ── ЛІВО: котушка з повітрям ──
    cx, cy = 250, 230
    s += _solenoid(cx, cy, 230, 46, 8)
    for yy in (cy - 18, cy + 18):
        s += arrow(cx - 90, yy, cx + 90, yy, GREEN, 2.0)
    s += text(cx, 100, "повітря всередині", 12, INK, "middle", "bold")
    s += text(cx, cy + 90, "N·I задано, поле — слабке", 10.5, INK, "middle", "bold")
    s += text(cx, cy + 110, "B = μ₀ · (N·I / ℓ)", 12, GREEN, "middle", "bold", "italic")
    # ── ПРАВО: котушка з залізним осердям ──
    cx2 = 690
    s += rect(cx2 - 115, cy - 16, 230, 32, "#c8ccd2", IRON, 2.0, 3)   # осердя
    s += _solenoid(cx2, cy, 230, 46, 8)
    for yy in (cy - 4, cy + 4):
        s += arrow(cx2 - 100, yy, cx2 + 100, yy, GREEN, 3.2)
    s += text(cx2, 100, "залізне осердя", 12, GREEN, "middle", "bold")
    s += text(cx2, cy + 90, "те саме N·I → поле в сотні разів", 10.5, INK, "middle", "bold")
    s += text(cx2, cy + 110, "B = μ₀·μr · (N·I / ℓ)", 12, GREEN, "middle", "bold", "italic")
    s += text(cx2 + 8, cy - 28, "осердя", 10, IRON, "start", "bold")
    s += text(W / 2, H - 14, "N·I (ампер-витки) — «скільки магнетизму» накачує котушка; осердя множить його (μr, докладно — §1.8.6).",
              11.5, INK, "middle", "bold")
    save("fig-8-5-2-ampere-turns.svg", s)


# ── Рис. 8.5.3 — тяга якоря: електромагніт як актуатор ───────────────────────
def fig_armature_pull():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 30, "Кероване поле тягне залізо: основа реле, соленоїда, клапана",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "поки тече струм — котушка намагнічує осердя, і воно притягує рухомий якір; струм зник — пружина повертає назад",
              11, GREY, "middle", style="italic")
    # ── ЛІВО: струм є, якір притягнуто ──
    def relay(x, y, energized):
        out = ""
        # осердя-стрижень
        out += rect(x, y, 30, 120, "#c8ccd2", IRON, 2.0, 3)
        out += _solenoid(x + 15, y + 60, 120, 26, 6)
        # повертаємо соленоїд горизонтально неможливо просто; намалюємо витки як лінії
        return out

    # котушка вертикальна
    def coil_v(cx, cy, h, turns, col=COPPER):
        out = ""
        step = h / turns
        for i in range(turns):
            yy = cy - h / 2 + i * step + step / 2
            out += f'<ellipse cx="{cx}" cy="{yy:.1f}" rx="34" ry="{step*0.34:.1f}" fill="none" stroke="{col}" stroke-width="3"/>\n'
        return out

    # ЛІВО — під напругою
    cx = 250
    s += rect(cx - 12, 110, 24, 150, "#c8ccd2", IRON, 2.0, 3)    # нерухоме осердя
    s += coil_v(cx, 185, 130, 6)
    # якір притягнутий (близько)
    s += rect(cx - 60, 96, 120, 16, "#9aa3ad", INK, 2.0, 3)
    s += text(cx, 88, "якір (притягнуто)", 10.5, GREEN, "middle", "bold")
    s += arrow(cx, 120, cx, 104, PURPLE, 3.0)
    s += text(cx + 40, 130, "сила тяги", 10, PURPLE, "start", "bold")
    s += current_out(cx - 50, 250, 9, ORANGE, 2.4)
    s += text(cx, 290, "СТРУМ Є → магніт тягне", 11.5, GREEN, "middle", "bold")
    # ПРАВО — без напруги, пружина повертає
    cx2 = 690
    s += rect(cx2 - 12, 110, 24, 150, "#c8ccd2", IRON, 2.0, 3)
    s += coil_v(cx2, 185, 130, 6, GREY)
    s += rect(cx2 - 60, 70, 120, 16, "#9aa3ad", INK, 2.0, 3)
    s += text(cx2, 62, "якір (відпущено)", 10.5, GREY, "middle", "bold")
    # пружина
    sp = [(cx2 + 70, 78)]
    for i in range(6):
        sp.append((cx2 + 70 + (10 if i % 2 else -10), 78 + (i + 1) * 7))
    s += polyline(sp, INK, 1.8)
    s += arrow(cx2, 86, cx2, 100, INK, 2.4)
    s += text(cx2 + 40, 110, "пружина", 10, INK, "start", "bold")
    s += text(cx2, 290, "СТРУМУ НЕМА → пружина відводить", 11.5, GREY, "middle", "bold")
    s += text(W / 2, H - 14, "Електричний сигнал → механічний рух. Деталі залізяччя (реле, соленоїд, клапан) — у вставці до теми.",
              11.5, INK, "middle", "bold")
    save("fig-8-5-3-armature-pull.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.6 — Осердя, насичення й гістерезис.  Рис. 8.6.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 8.6.1 — осердя вишиковує домени й підсилює поле ─────────────────────
def fig_core_amplify():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 30, "Чому залізо підсилює поле в тисячі разів",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "слабке поле котушки (H) повертає домени осердя; ті додають своє поле — і всередині B стає набагато більшим",
              11, GREY, "middle", style="italic")
    cx, cy = W / 2, 220
    # осердя-прямокутник у котушці
    s += rect(cx - 200, cy - 32, 400, 64, "#c8ccd2", IRON, 2.0, 4)
    s += _solenoid(cx, cy, 360, 60, 10)
    # маленьке поле котушки H (тонкі стрілки)
    s += arrow(cx - 170, cy - 46, cx - 130, cy - 46, ORANGE, 1.6)
    s += text(cx - 150, cy - 54, "H (від струму) — слабке", 10, ORANGE, "middle", "bold")
    # домени всередині осердя — вишикувані
    for k in range(7):
        s += _domain_arrow(cx - 150 + k * 50, cy, 0, 18, GREEN, 2.8)
    # сумарне B — товста стрілка
    s += arrow(cx - 180, cy + 50, cx + 180, cy + 50, GREEN, 4.2)
    s += text(cx, cy + 70, "B = μ₀·μr·H — у сотні–тисячі разів більше", 11.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 16, "μr (відносна проникність) — у скільки разів осердя множить поле: для трансформаторного заліза ~ 2000–8000.",
              11, INK, "middle", "bold")
    save("fig-8-6-1-core-amplify.svg", s)


# ── Рис. 8.6.2 — крива намагнічування й насичення ────────────────────────────
def fig_saturation():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 30, "Насичення: у заліза є межа — усі домени вже вишикувані",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "спершу B росте круто (домени легко повертаються), потім крива згинається — додавати струм майже марно",
              11, GREY, "middle", style="italic")
    ax, ay, aw, ah = 110, 320, 620, 220
    s += arrow(ax, ay, ax + aw + 12, ay, GREY, 1.5)
    s += arrow(ax, ay, ax, ay - ah - 12, GREY, 1.5)
    s += text(ax + aw + 6, ay + 20, "H ∝ N·I (струм котушки)", 11, GREY, "start", "bold")
    s += text(ax - 8, ay - ah - 4, "B (поле в осерді)", 11.5, GREY, "end", "bold")
    # крива насичення B = Bs * tanh(k*H)
    Bs = ah * 0.88
    pts = []
    N = 120
    for i in range(N + 1):
        t = i / N
        H = t * 4.2
        B = Bs * math.tanh(H)
        pts.append((ax + t * aw, ay - B))
    s += polyline(pts, GREEN, 3.0)
    # рівень насичення
    s += line(ax, ay - Bs, ax + aw, ay - Bs, ORANGE, 1.6, "5,4")
    s += text(ax + aw - 4, ay - Bs - 8, "B_sat (насичення)", 11, ORANGE, "end", "bold")
    # зони
    s += text(ax + 70, ay - 70, "лінійна зона:", 10.5, INK, "start", "bold")
    s += text(ax + 70, ay - 54, "B ∝ I, осердя «множить»", 9.5, GREY, "start")
    s += text(ax + aw - 200, ay - Bs + 36, "за насиченням:", 10.5, RED, "start", "bold")
    s += text(ax + aw - 200, ay - Bs + 52, "осердя більше не допомагає", 9.5, GREY, "start")
    s += text(W / 2, H - 14, "Тому в розрахунку котушок з осердям тримаються нижче B_sat: інакше зростання струму не дає віддачі.",
              11, INK, "middle", "bold")
    save("fig-8-6-2-saturation.svg", s)


# ── Рис. 8.6.3 — петля гістерезису з позначеннями ────────────────────────────
def fig_hysteresis_loop():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 30, "Гістерезис: осердя «пам'ятає» минуле поле",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "знявши струм (H=0), осердя лишається трохи намагніченим (B_r); щоб обнулити — потрібне зустрічне поле H_c",
              11, GREY, "middle", style="italic")
    cx, cy = W / 2, 250
    ax, ay = cx, cy
    s += arrow(ax - 230, ay, ax + 230, ay, GREY, 1.5)
    s += arrow(ax, ay + 165, ax, ay - 165, GREY, 1.5)
    s += text(ax + 226, ay + 20, "H", 12, GREY, "middle", "bold", "italic")
    s += text(ax + 18, ay - 156, "B", 12, GREY, "middle", "bold", "italic")
    # петля гістерезису (дві криві tanh зі зсувом)
    Bs = 130
    Hc = 70
    up = []
    dn = []
    for i in range(121):
        t = i / 120
        H = -200 + t * 400
        up.append((ax + H, ay - Bs * math.tanh((H + Hc) / 60)))
        dn.append((ax + H, ay - Bs * math.tanh((H - Hc) / 60)))
    s += polyline(up, GREEN, 2.8)
    s += polyline(dn, RED, 2.8)
    # точки: B_r (H=0), H_c (B=0)
    Br = Bs * math.tanh(Hc / 60)
    s += circle(ax, ay - Br, 4.5, GREEN, GREEN, 1)
    s += text(ax + 8, ay - Br - 6, "B_r (залишкова)", 11, GREEN, "start", "bold")
    s += circle(ax - Hc, ay, 4.5, RED, RED, 1)
    s += text(ax - Hc - 6, ay + 20, "H_c (коерцитивна)", 11, RED, "end", "bold")
    # площа = втрати
    s += text(ax, ay - 30, "площа петлі =", 11, INK, "middle", "bold")
    s += text(ax, ay - 14, "втрати тепла за цикл", 11, INK, "middle", "bold")
    # стрілки напряму обходу
    s += arrow(ax + 120, ay - Bs * math.tanh((120 - Hc) / 60) - 2,
               ax + 122, ay - Bs * math.tanh((122 - Hc) / 60) - 2, RED, 2)
    s += text(W / 2, H - 50, "Широка петля (тверді матеріали) — добре для постійного магніту, погано для осердя: щоцикл втрачається",
              11, INK, "middle", "bold")
    s += text(W / 2, H - 32, "енергія. Тому осердя трансформаторів роблять із «м'якого» заліза з тонкою петлею (зв'язок із §1.8.3).",
              11, INK, "middle", "bold")
    s += text(W / 2, H - 12, "⚠ Не плутати з гістерезисом тригера Шмітта (§2.8.8) — там пороги напруги, а не магнетизм.",
              10.5, GREY, "middle", "bold", "italic")
    save("fig-8-6-3-hysteresis-loop.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.7 — Сила Ампера: F = B·I·L.  Рис. 8.7.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 8.7.1 — провідник зі струмом у полі: виникає сила ───────────────────
def fig_ampere_force():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 30, "Поле штовхає провідник зі струмом: сила Ампера F = B·I·L",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "дріт зі струмом — це його власні кільця поля; зовнішнє поле з одного боку додається, з іншого — гаситься, і дріт «здуває»",
              11, GREY, "middle", style="italic")
    # магніт-вилка з полем угору між полюсами
    s += rect(120, 110, 60, 80, "#fbe3e1", RED, 2.0, 4)
    s += text(150, 158, "N", 22, RED, "middle", "bold")
    s += rect(120, 290, 60, 80, "#e2e9f7", BLUE, 2.0, 4)
    s += text(150, 338, "S", 22, BLUE, "middle", "bold")
    # поле B вгору між ними? для N зверху → B вниз. Зробимо N зверху, поле вниз.
    # перевизначимо: поле від N (зверху) до S (знизу) — вниз
    for xx in (220, 280, 340, 400, 460):
        s += arrow(xx, 200, xx, 280, GREEN, 1.8)
    s += text(490, 244, "B (униз)", 11, GREEN, "start", "bold")
    # провідник перпендикулярно (струм на нас) у полі
    s += current_out(340, 240, 14, ORANGE, 3)
    s += text(340, 215, "I (на нас)", 10.5, ORANGE, "middle", "bold")
    # сила вліво (F = I×B): струм на нас, B униз → F управо? за правою рукою I(out,+z)×B(down,-y)= +z × -y = +x?
    # домовимось показати числово несуперечливо: сила горизонтальна
    s += arrow(340, 240, 250, 240, PURPLE, 4)
    s += text(255, 226, "F = B·I·L", 12.5, PURPLE, "middle", "bold", "italic")
    # права рука: три осі
    hx, hy = 720, 230
    s += rect(620, 110, 280, 240, "#fafafa", GREY, 1.4, 10)
    s += text(760, 134, "правило правої руки (взаємно перпендикулярні)", 9.5, INK, "middle", "bold")
    s += arrow(hx, hy, hx + 90, hy, ORANGE, 3)      # I
    s += text(hx + 96, hy + 4, "I (струм)", 10.5, ORANGE, "start", "bold")
    s += arrow(hx, hy, hx, hy + 80, GREEN, 3)       # B
    s += text(hx + 4, hy + 92, "B (поле)", 10.5, GREEN, "start", "bold")
    s += arrow(hx, hy, hx - 64, hy - 56, PURPLE, 3)  # F
    s += text(hx - 70, hy - 60, "F (сила)", 10.5, PURPLE, "end", "bold")
    s += text(760, 340, "F ⟂ і до I, і до B", 10, GREY, "middle", style="italic")
    s += text(W / 2, H - 14, "Сила максимальна, коли струм перпендикулярний полю; уздовж поля (I ∥ B) сили немає зовсім.",
              11.5, INK, "middle", "bold")
    save("fig-8-7-1-ampere-force.svg", s)


# ── Рис. 8.7.2 — кут між I та B: F = B·I·L·sinθ ──────────────────────────────
def fig_force_angle():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 30, "Сила залежить від кута: F = B·I·L·sinθ",
              18, INK, "middle", "bold")
    cases = [
        ("θ = 90°", "I ⟂ B", "F = B·I·L", "максимум", 90, GREEN),
        ("θ = 45°", "навскіс", "F = 0.71·B·I·L", "менше", 45, ORANGE),
        ("θ = 0°", "I ∥ B", "F = 0", "сили немає", 0, RED),
    ]
    bw = 280
    for i, (lab, sub, f, note, ang, col) in enumerate(cases):
        x = 30 + i * (bw + 12)
        s += rect(x, 80, bw, 220, "#ffffff", col, 1.8, 10)
        s += text(x + bw / 2, 106, lab + "  (" + sub + ")", 12.5, col, "middle", "bold")
        cx, cy = x + bw / 2, 190
        # поле B (горизонтальне)
        s += arrow(cx - 80, cy, cx + 80, cy, GREEN, 2.4)
        s += text(cx + 86, cy + 4, "B", 11, GREEN, "start", "bold", "italic")
        # струм під кутом
        a = math.radians(ang)
        s += arrow(cx, cy, cx + 70 * math.cos(a - math.pi / 2), cy + 70 * math.sin(a - math.pi / 2),
                   ORANGE, 2.8)
        s += text(cx + 8, cy - 40, "I", 11, ORANGE, "start", "bold", "italic")
        s += text(x + bw / 2, 256, f, 12.5, INK, "middle", "bold", "italic")
        s += text(x + bw / 2, 280, note, 11, col, "middle", "bold")
    s += text(W / 2, H - 14, "Тому в моторах обмотку розташовують так, щоб струм ішов поперек поля — там сила найбільша.",
              11.5, INK, "middle", "bold")
    save("fig-8-7-2-force-angle.svg", s)


# ── Рис. 8.7.3 — рамка зі струмом обертається: зародок мотора ────────────────
def fig_torque_loop():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 30, "Дві сторони рамки — дві протилежні сили — обертальний момент",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "у полі один бік рамки штовхає вгору, протилежний — вниз; пара сил крутить рамку — це фізична основа мотора",
              11, GREY, "middle", style="italic")
    # полюси з полем зліва направо
    s += rect(90, 130, 50, 160, "#fbe3e1", RED, 2.0, 4)
    s += text(115, 218, "N", 20, RED, "middle", "bold")
    s += rect(780, 130, 50, 160, "#e2e9f7", BLUE, 2.0, 4)
    s += text(805, 218, "S", 20, BLUE, "middle", "bold")
    for yy in (160, 200, 240, 280):
        s += arrow(145, yy, 775, yy, GREEN, 1.5)
    s += text(460, 124, "B →", 12, GREEN, "middle", "bold")
    # рамка (вид зверху/перспектива): дві вертикальні сторони
    lx, rx = 380, 540
    s += rect(lx, 160, rx - lx, 120, "none", ORANGE, 3.0)
    # струм у рамці: ліва сторона вгору, права вниз (стрілки)
    s += arrow(lx, 280, lx, 160, ORANGE, 3)
    s += arrow(rx, 160, rx, 280, ORANGE, 3)
    s += text(lx - 28, 220, "I↑", 11, ORANGE, "middle", "bold")
    s += text(rx + 24, 220, "I↓", 11, ORANGE, "middle", "bold")
    # сили: ліва сторона (I вгору, B вправо) → F на нас/від нас; покажемо вертикально для наочності крутіння
    s += arrow(lx, 220, lx, 130, PURPLE, 3.5)
    s += text(lx, 122, "F", 12, PURPLE, "middle", "bold", "italic")
    s += arrow(rx, 220, rx, 310, PURPLE, 3.5)
    s += text(rx, 326, "F", 12, PURPLE, "middle", "bold", "italic")
    # дуга обертання
    s += arc((lx + rx) / 2, 220, 110, 200, 340, INK, 2.0, marker="aInk")
    s += text((lx + rx) / 2, 360, "пара сил → момент M = B·I·A·N (обертає рамку)", 11.5, INK, "middle", "bold")
    s += text(W / 2, H - 12, "Додай багато витків і колектор, що перемикає струм, — і рамка крутитиметься безперервно (це вже Модуль про мотори).",
              10.5, GREY, "middle", style="italic")
    save("fig-8-7-3-torque-loop.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.8 — Ефект Холла.  Рис. 8.8.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 8.8.1 — носії відхиляються → поперечна напруга ──────────────────────
def fig_hall_effect():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Ефект Холла: поле відхиляє носії вбік → з'являється поперечна напруга",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "сила Лоренца притискає рухомі заряди до одного краю пластинки; край заряджається, і між боками виникає U_H",
              11, GREY, "middle", style="italic")
    # пластинка
    px, py, pw, ph = 280, 170, 380, 130
    s += rect(px, py, pw, ph, "#eef2f5", INK, 2.2, 4)
    # струм уздовж пластинки (зліва направо)
    s += arrow(px - 70, py + ph / 2, px - 4, py + ph / 2, ORANGE, 3.5)
    s += text(px - 70, py + ph / 2 - 10, "I", 13, ORANGE, "start", "bold", "italic")
    s += arrow(px + pw + 4, py + ph / 2, px + pw + 70, py + ph / 2, ORANGE, 3.5)
    # поле B — на нас (з пластинки)
    for (mx, my) in [(px + 90, py + 30), (px + 190, py + 30), (px + 290, py + 30),
                     (px + 90, py + ph - 26), (px + 190, py + ph - 26), (px + 290, py + ph - 26)]:
        s += current_out(mx, my, 9, GREEN, 2.4)
    s += text(px + pw / 2, py - 12, "B — на нас (з площини)", 11, GREEN, "middle", "bold")
    # носії дрейфують і відхиляються вниз (сила Лоренца)
    for k in range(4):
        ex = px + 60 + k * 80
        s += circle(ex, py + ph / 2, 7, "#e2e9f7", BLUE, 1.6)
        s += text(ex, py + ph / 2 + 4, "−", 11, BLUE, "middle", "bold")
        s += arrow(ex, py + ph / 2 + 8, ex, py + ph / 2 + 34, BLUE, 1.8)
    s += text(px + pw + 80, py + ph - 8, "сила Лоренца тисне вниз", 10, BLUE, "start", "bold")
    # накопичення: низ −, верх +
    s += rect(px, py + ph - 6, pw, 6, "#cfe0f7", BLUE, 0)
    s += rect(px, py, pw, 6, "#fbe3e1", RED, 0)
    s += text(px - 10, py + 4, "+", 16, RED, "end", "bold")
    s += text(px - 10, py + ph, "−", 16, BLUE, "end", "bold")
    # напруга Холла впоперек
    s += arrow(px + pw + 30, py + 6, px + pw + 30, py + ph - 6, PURPLE, 2.6)
    s += arrow(px + pw + 30, py + ph - 6, px + pw + 30, py + 6, PURPLE, 2.6)
    s += text(px + pw + 38, py + ph / 2, "U_H", 13, PURPLE, "start", "bold", "italic")
    s += text(W / 2, H - 40, "Поперечна напруга U_H = (I·B)/(n·q·d) — пропорційна полю B. Виміряв U_H — дізнався B.",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 18, "На цьому стоять давачі поля, безконтактні вимикачі та струмові кліщі (фізика для давачів Модуля 5).",
              11, GREY, "middle", "bold")
    save("fig-8-8-1-hall-effect.svg", s)


# ── Рис. 8.8.2 — знак U_H розрізняє тип носіїв ───────────────────────────────
def fig_hall_sign():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 30, "Несподіваний бонус: знак напруги Холла каже, ХТО носій",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "за тих самих I та B електрони й «дірки» збираються на ПРОТИЛЕЖНИХ краях — звідси й знак U_H різний",
              11, GREY, "middle", style="italic")

    def plate(x, label, carrier_sign, top_sign, color):
        pw, ph, py = 300, 110, 170
        out = rect(x, py, pw, ph, "#eef2f5", INK, 2.0, 4)
        out += arrow(x - 50, py + ph / 2, x - 4, py + ph / 2, ORANGE, 3)
        out += text(x - 50, py + ph / 2 - 10, "I", 12, ORANGE, "start", "bold", "italic")
        out += current_out(x + pw / 2, py + 28, 8, GREEN, 2.2)
        out += text(x + pw / 2 + 16, py + 30, "B", 10.5, GREEN, "start", "bold")
        # носій
        cs = RED if carrier_sign == "+" else BLUE
        out += circle(x + 70, py + ph / 2, 8, "#fff", cs, 1.6)
        out += text(x + 70, py + ph / 2 + 4, carrier_sign, 12, cs, "middle", "bold")
        out += arrow(x + 70, py + ph / 2 + 8, x + 70, py + ph / 2 + 30, cs, 1.8)
        # заряджені краї
        ts = RED if top_sign == "+" else BLUE
        bs = BLUE if top_sign == "+" else RED
        out += text(x - 10, py + 6, top_sign, 15, ts, "end", "bold")
        out += text(x - 10, py + ph, "−" if top_sign == "+" else "+", 15, bs, "end", "bold")
        out += text(x + pw / 2, py - 10, label, 12, color, "middle", "bold")
        return out

    s += plate(120, "носії — електрони (−)", "−", "+", BLUE)
    s += plate(520, "носії — «дірки» (+)", "+", "−", RED)
    s += text(W / 2, H - 16, "Саме ефект Холла дав перший прямий доказ, що в металах струм несуть від'ємні заряди (історія до теми).",
              11.5, INK, "middle", "bold")
    save("fig-8-8-2-hall-sign.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.9 — Магнітне поле Землі й компас.  Рис. 8.9.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 8.9.1 — Земля як великий магніт; полюси переплутані ──────────────────
def fig_earth_field():
    W, H = 900, 480
    s = header(W, H)
    s += text(W / 2, 30, "Земля — велетенський магніт; його полюси й географічні переплутані",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "стрілка компаса дивиться північним кінцем на географічну Пн — отже, ТАМ магнітний ПІВДЕННИЙ полюс Землі",
              11, GREY, "middle", style="italic")
    cx, cy, R = W / 2, 280, 150
    s += circle(cx, cy, R, "#eef5fb", "#7fa9c9", 2.0)
    s += line(cx, cy - R - 28, cx, cy + R + 28, GREY, 1.6, "5,4")
    s += text(cx, cy - R - 34, "географічна Пн", 11, INK, "middle", "bold")
    s += text(cx, cy + R + 44, "географічна Пд", 11, INK, "middle", "bold")
    a = math.radians(11)
    mlen = R * 0.82
    mx1, my1 = cx - mlen * math.sin(a), cy - mlen * math.cos(a)
    mx2, my2 = cx + mlen * math.sin(a), cy + mlen * math.cos(a)
    s += line(mx1, my1, mx2, my2, GREY, 14)
    s += circle(mx1, my1, 16, "#e2e9f7", BLUE, 2)
    s += text(mx1, my1 + 5, "S", 14, BLUE, "middle", "bold")
    s += circle(mx2, my2, 16, "#fbe3e1", RED, 2)
    s += text(mx2, my2 + 5, "N", 14, RED, "middle", "bold")
    s += text(mx1 - 40, my1 - 10, "магнітний S Землі", 9.5, BLUE, "end", "bold")
    s += text(mx2 + 40, my2 + 14, "магнітний N Землі", 9.5, RED, "start", "bold")
    for rr in (R + 36, R + 74):
        s += arc(cx, cy, rr, -110, 110, GREEN, 1.6)
        s += arc(cx, cy, rr, 110, 250, GREEN, 1.6)
    nx, ny = cx + 0, cy - R - 4
    s += circle(nx, ny - 6, 16, "#fff", GREY, 1.4)
    s += line(nx, ny + 8, nx, ny - 20, BLUE, 4)
    s += polygon([(nx, ny - 20), (nx - 5, ny - 12), (nx + 5, ny - 12)], RED)
    s += text(nx + 22, ny - 6, "компас: N угору", 9.5, INK, "start", "bold")
    s += text(W / 2, H - 14, "«Північний полюс компаса» притягується до магнітного півдня Землі — бо різнойменні полюси тягнуться (§1.8.1).",
              11, INK, "middle", "bold")
    save("fig-8-9-1-earth-field.svg", s)


# ── Рис. 8.9.2 — магнітне відмінювання: справжня vs магнітна Пн ───────────────
def fig_declination():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 30, "Стрілка показує на магнітну, а не географічну північ: відмінювання",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "магнітні полюси не збігаються з географічними й повільно дрейфують; різниця кутів — «відмінювання» (declination)",
              11, GREY, "middle", style="italic")
    cx, cy = W / 2, 210
    s += circle(cx, cy, 14, "#fff", GREY, 1.4)
    s += arrow(cx, cy, cx, cy - 130, GREEN, 2.6)
    s += text(cx, cy - 140, "географічна Пн", 11, GREEN, "middle", "bold")
    a = math.radians(18)
    s += arrow(cx, cy, cx + 130 * math.sin(a), cy - 130 * math.cos(a), BLUE, 2.6)
    s += text(cx + 130 * math.sin(a) + 10, cy - 130 * math.cos(a), "магнітна Пн (стрілка)", 11, BLUE, "start", "bold")
    s += arc(cx, cy, 70, -90, -90 + 18, ORANGE, 2.0, marker="aOrange")
    s += text(cx + 50, cy - 84, "δ — відмінювання", 11, ORANGE, "start", "bold")
    s += text(W / 2, H - 16, "Тому для точної навігації до показу компаса додають місцеве відмінювання (з карт/таблиць).",
              11.5, INK, "middle", "bold")
    save("fig-8-9-2-declination.svg", s)


# ── Рис. 8.9.3 — компас бреше біля струму й заліза ───────────────────────────
def fig_compass_lies():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 30, "Чому компас «бреше» біля дротів і заліза",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "поле Землі слабке (~50 мкТл); поруч сильніше місцеве поле струму чи намагніченого заліза перетягує стрілку на себе",
              11, GREY, "middle", style="italic")

    def compass(cx, cy, ang_deg):
        out = circle(cx, cy, 26, "#fff", GREY, 1.5)
        a = math.radians(ang_deg)
        out += line(cx - 22 * math.sin(a), cy + 22 * math.cos(a),
                    cx + 22 * math.sin(a), cy - 22 * math.cos(a), BLUE, 4)
        out += polygon([(cx + 22 * math.sin(a), cy - 22 * math.cos(a)),
                        (cx + 22 * math.sin(a) - 6, cy - 22 * math.cos(a) + 4),
                        (cx + 22 * math.sin(a) + 6, cy - 22 * math.cos(a) + 4)], RED)
        return out

    s += text(180, 100, "лише поле Землі", 12.5, GREEN, "middle", "bold")
    s += arrow(180, 250, 180, 150, GREEN, 1.8)
    s += text(180, 138, "B Землі (слабке)", 9.5, GREEN, "middle", "bold")
    s += compass(180, 200, 0)
    s += text(180, 295, "стрілка чесно на Пн", 10.5, INK, "middle", "bold")
    s += text(660, 100, "поряд дріт зі струмом", 12.5, ORANGE, "middle", "bold")
    s += arrow(560, 150, 560, 280, ORANGE, 4)
    s += text(548, 150, "I", 12, ORANGE, "end", "bold", "italic")
    s += circle(560, 215, 50, "none", GREEN, 1.6)
    s += arrow(610, 215, 610, 245, GREEN, 2.0)
    s += text(622, 235, "сильне місцеве B", 9.5, GREEN, "start", "bold")
    s += compass(660, 215, 72)
    s += text(660, 300, "стрілку перетягло поперек дроту", 10, RED, "middle", "bold")
    s += text(W / 2, H - 14, "Звідси практичне правило: вимірюючи поле Землі чи користуючись компасом, тримайся далі від струмів і сталі.",
              11.5, INK, "middle", "bold")
    save("fig-8-9-3-compass-lies.svg", s)


# ════════════════════════════════════════════════════════════════════════════
#  Тема 1.8.10 — Електромагнітна індукція: Фарадей, Ленц, вихрові струми. Рис.8.10.k
# ════════════════════════════════════════════════════════════════════════════

# ── Рис. 8.10.1 — магніт у котушці: рух → ЕРС ────────────────────────────────
def fig_induction():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 30, "Дослід Фарадея: рухаєш магніт крізь котушку — з'являється струм",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "важлива саме ЗМІНА потоку: магніт стоїть — стрілка на нулі; рухається — стрілка відхиляється",
              11, GREY, "middle", style="italic")

    def coil_galv(cx, cy, sign):
        out = _solenoid(cx, cy, 150, 44, 6)
        out += line(cx - 75, cy + 44, cx - 75, cy + 95, INK, 2)
        out += line(cx + 75, cy + 44, cx + 75, cy + 95, INK, 2)
        out += line(cx - 75, cy + 95, cx + 75, cy + 95, INK, 2)
        gx, gy = cx, cy + 95
        out += circle(gx, gy, 22, "#fff", INK, 2)
        out += text(gx, gy + 5, "G", 14, INK, "middle", "bold")
        ang = {"+": -35, "0": 0, "-": 35}[sign]
        a = math.radians(ang)
        out += line(gx, gy, gx + 16 * math.sin(a), gy - 16 * math.cos(a), RED, 2.4)
        return out

    cx = 230
    s += coil_galv(cx, 180, "+")
    s += vbar_magnet(cx - 90, 150, 30, 70, n_top=False)
    s += arrow(cx - 75, 130, cx - 30, 160, PURPLE, 3)
    s += text(cx - 110, 120, "вдвигаємо", 10.5, PURPLE, "middle", "bold")
    s += text(cx, 310, "потік РОСТЕ → струм є", 11, GREEN, "middle", "bold")
    cx2 = 560
    s += coil_galv(cx2, 180, "0")
    s += vbar_magnet(cx2 - 15, 120, 30, 70, n_top=False)
    s += text(cx2, 310, "магніт СТОЇТЬ → струму немає", 11, GREY, "middle", "bold")
    cx3 = 850
    s += coil_galv(cx3, 180, "-")
    s += vbar_magnet(cx3 - 15, 95, 30, 70, n_top=False)
    s += arrow(cx3 - 30, 150, cx3 - 5, 110, PURPLE, 3)
    s += text(cx3 + 30, 120, "висмикуємо", 10.5, PURPLE, "middle", "bold")
    s += text(cx3, 310, "потік ПАДАЄ → струм у ІНШИЙ бік", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 36, "Закон Фарадея: ЕРС = −dΦ/dt — наведена напруга дорівнює швидкості зміни магнітного потоку Φ крізь котушку.",
              12, INK, "middle", "bold")
    s += text(W / 2, H - 14, "Більше витків, сильніший магніт, швидший рух → більша ЕРС. Нерухоме поле струму не наводить.",
              11, GREY, "middle", "bold")
    save("fig-8-10-1-induction.svg", s)


# ── Рис. 8.10.2 — правило Ленца ──────────────────────────────────────────────
def fig_lenz():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 30, "Правило Ленца: наведений струм завжди ПРОТИДІЄ зміні, що його породила",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "це не примха, а закон збереження енергії: інакше струм підсилював би себе сам і давав енергію з нічого",
              11, GREY, "middle", style="italic")
    cx = 260
    s += circle(cx, 220, 60, "none", COPPER, 3)
    s += text(cx, 130, "магніт наближається", 11.5, INK, "middle", "bold")
    s += rect(cx - 170, 200, 70, 40, "#fbe3e1", RED, 2)
    s += text(cx - 152, 224, "N", 16, RED, "middle", "bold")
    s += arrow(cx - 95, 220, cx - 65, 220, PURPLE, 3)
    s += text(cx - 80, 196, "рух →", 9.5, PURPLE, "middle", "bold")
    s += text(cx - 6, 224, "N", 16, RED, "middle", "bold")
    s += arc(cx, 220, 76, 200, 340, ORANGE, 2.2, marker="aOrange")
    s += text(cx + 64, 300, "струм такий, щоб", 9.5, ORANGE, "middle", "bold")
    s += text(cx + 64, 314, "відштовхнути магніт", 9.5, ORANGE, "middle", "bold")
    cx2 = 680
    s += circle(cx2, 220, 60, "none", COPPER, 3)
    s += text(cx2, 130, "магніт віддаляється", 11.5, INK, "middle", "bold")
    s += rect(cx2 - 200, 200, 70, 40, "#fbe3e1", RED, 2)
    s += text(cx2 - 165, 224, "N", 16, RED, "middle", "bold")
    s += arrow(cx2 - 125, 220, cx2 - 155, 220, PURPLE, 3)
    s += text(cx2 - 140, 196, "← рух", 9.5, PURPLE, "middle", "bold")
    s += text(cx2 - 6, 224, "S", 16, BLUE, "middle", "bold")
    s += arc(cx2, 220, 76, 340, 200, ORANGE, 2.2, marker="aOrange")
    s += text(cx2 + 64, 300, "струм такий, щоб", 9.5, ORANGE, "middle", "bold")
    s += text(cx2 + 64, 314, "притягнути магніт назад", 9.5, ORANGE, "middle", "bold")
    s += text(W / 2, H - 14, "Хоч так, хоч так — котушка «опирається» руху. Тому крутити генератор під навантаженням важче (звідки й береться енергія).",
              11, INK, "middle", "bold")
    save("fig-8-10-2-lenz.svg", s)


# ── Рис. 8.10.3 — генератор: «мотор навпаки» ─────────────────────────────────
def fig_generator_inverse():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 30, "Генератор — це «мотор навпаки»: те саме залізо, обернений потік енергії",
              18, INK, "middle", "bold")
    bw = 380
    s += rect(40, 80, bw, 220, "#eef7f0", GREEN, 2.0, 12)
    s += text(40 + bw / 2, 108, "МОТОР", 14, GREEN, "middle", "bold")
    s += text(40 + bw / 2, 130, "(сила Ампера, §1.8.7)", 10, GREY, "middle", style="italic")
    s += arrow(70, 200, 150, 200, ORANGE, 3)
    s += text(110, 188, "струм", 10, ORANGE, "middle", "bold")
    s += circle(230, 200, 44, "none", INK, 2.4)
    s += arc(230, 200, 44, 200, 480, INK, 2.2, marker="aInk")
    s += arrow(290, 200, 370, 200, PURPLE, 3)
    s += text(335, 188, "обертання", 10, PURPLE, "middle", "bold")
    s += text(40 + bw / 2, 286, "електрика → рух", 11.5, INK, "middle", "bold")
    x0 = 500
    s += rect(x0, 80, bw, 220, "#eef2fb", BLUE, 2.0, 12)
    s += text(x0 + bw / 2, 108, "ГЕНЕРАТОР", 14, BLUE, "middle", "bold")
    s += text(x0 + bw / 2, 130, "(індукція, §1.8.10)", 10, GREY, "middle", style="italic")
    s += arrow(x0 + 70, 200, x0 + 30, 200, PURPLE, 3)
    s += text(x0 + 50, 188, "обертання", 10, PURPLE, "middle", "bold")
    s += circle(x0 + 150, 200, 44, "none", INK, 2.4)
    s += arc(x0 + 150, 200, 44, 200, 480, INK, 2.2, marker="aInk")
    s += arrow(x0 + 250, 200, x0 + 330, 200, ORANGE, 3)
    s += text(x0 + 295, 188, "струм", 10, ORANGE, "middle", "bold")
    s += text(x0 + bw / 2, 286, "рух → електрика", 11.5, INK, "middle", "bold")
    s += text(W / 2, 200, "⇄", 26, GREY, "middle", "bold")
    s += text(W / 2, H - 14, "Та сама обмотка в полі: подаси струм — крутиться (мотор); крутиш — дає струм (генератор). Дві сторони однієї фізики.",
              11.5, INK, "middle", "bold")
    save("fig-8-10-3-generator-inverse.svg", s)


# ── Рис. 8.10.4 — вихрові струми ─────────────────────────────────────────────
def fig_eddy_currents():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 30, "Вихрові струми: індукція прямо в суцільному металі",
              18, INK, "middle", "bold")
    s += text(W / 2, 52, "змінне поле наводить замкнені струми в товщі металу; за Ленцем вони гальмують рух і гріють метал",
              11, GREY, "middle", style="italic")
    px, py, pw, ph = 110, 140, 250, 180
    s += rect(px, py, pw, ph, "#dfe4ea", IRON, 2.0, 4)
    s += text(px + pw / 2, py - 12, "суцільний метал", 11.5, INK, "middle", "bold")
    s += current_out(px + pw / 2, py + 40, 11, GREEN, 2.6)
    s += text(px + pw / 2 + 18, py + 42, "B(t) змінне", 10, GREEN, "start", "bold")
    for (ex, ey) in [(px + 70, py + 110), (px + 175, py + 110)]:
        s += arc(ex, ey, 32, 0, 320, ORANGE, 2.4, marker="aOrange")
    s += text(px + pw / 2, py + ph + 22, "великі вихори → сильний нагрів і гальмування", 9.5, RED, "middle", "bold")
    qx, qy, qw, qh = 560, 140, 250, 180
    s += text(qx + qw / 2, qy - 12, "набір тонких пластин (шихтування)", 11, INK, "middle", "bold")
    nlam = 7
    lw = qw / nlam
    for k in range(nlam):
        s += rect(qx + k * lw, qy, lw - 3, qh, "#dfe4ea", IRON, 1.4, 2)
        s += arc(qx + k * lw + lw / 2 - 1, qy + qh / 2, 12, 0, 300, ORANGE, 1.6, marker="aOrange")
    s += current_out(qx + qw / 2, qy + 32, 9, GREEN, 2.2)
    s += text(qx + qw / 2, qy + qh + 22, "ізоляція рве петлі → вихори дрібні, втрати малі", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 36, "Користь: гальмо без тертя (атракціони, лічильники), індукційна плита, плавка металу.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, H - 14, "Шкода: марний нагрів осердя трансформатора — тому його й «шихтують» тонкими ізольованими пластинами.",
              11, GREY, "middle", "bold")
    save("fig-8-10-4-eddy-currents.svg", s)


if __name__ == "__main__":
    # Тема 1.8.1
    fig_dipole_lines()
    fig_poles_force()
    fig_no_monopole()
    fig_e_vs_b()
    fig_b_scale()
    # Тема 1.8.2
    fig_spin_magnet()
    fig_domains()
    fig_magnetic_classes()
    # Тема 1.8.3
    fig_hard_soft()
    fig_curie()
    fig_demagnetize()
    # Тема 1.8.4
    fig_oersted()
    fig_wire_field()
    fig_loop_field()
    # Тема 1.8.5
    fig_solenoid()
    fig_ampere_turns()
    fig_armature_pull()
    # Тема 1.8.6
    fig_core_amplify()
    fig_saturation()
    fig_hysteresis_loop()
    # Тема 1.8.7
    fig_ampere_force()
    fig_force_angle()
    fig_torque_loop()
    # Тема 1.8.8
    fig_hall_effect()
    fig_hall_sign()
    # Тема 1.8.9
    fig_earth_field()
    fig_declination()
    fig_compass_lies()
    # Тема 1.8.10
    fig_induction()
    fig_lenz()
    fig_generator_inverse()
    fig_eddy_currents()
    print("OK")

