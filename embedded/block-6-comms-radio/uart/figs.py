# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 35 — «UART і протоколи поверх нього» (Модуль 6).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле/висновок зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; для історії до розділу — секція 0 (Рис. 35.0.N).

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"   # додатний (+) / мітка-START
BLUE  = "#1f47b5"   # від'ємний (−)
GREEN = "#1f8a3b"   # висновок / поле
INK   = "#1b1b1b"   # основний текст/лінії
GREY  = "#8a8a8a"   # допоміжне
FAINT = "#e4e4e4"   # дуже бліде тло
AMBER = "#caa24a"   # акцент-дерево
METAL = "#9a9aa0"   # метал
SKIN  = "#e7c4a0"   # шкіра (рука)
PAPER = "#f4efe2"   # папір/стрічка
LRED  = "#fbecec"   # бліде червоне тло
LBLUE = "#e9eefb"   # бліде синє тло
LGRN  = "#eef6ef"   # бліде зелене тло
LGREY = "#f3f3f3"   # бліде сіре тло
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


def plus(cx, cy, r=12, color=RED, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)
            + line(cx, cy - r * 0.55, cx, cy + r * 0.55, color, w))


def minus(cx, cy, r=12, color=BLUE, w=2.5):
    return (circle(cx, cy, r, "none", color, w)
            + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w))


def ground(cx, y, color=INK):
    """Стандартний символ землі під точкою (cx, y)."""
    s = line(cx, y, cx, y + 12, color, 2)
    s += line(cx - 16, y + 12, cx + 16, y + 12, color, 2.4)
    s += line(cx - 10, y + 18, cx + 10, y + 18, color, 2.4)
    s += line(cx - 5, y + 24, cx + 5, y + 24, color, 2.4)
    return s


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── Рис. 35.0.1 — вертикальний таймлайн «ланцюг питань» ──────────────────────
def fig_timeline():
    W, H = 900, 690
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: від коду Морзе до кадру UART", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "кожен крок прибирав щось зайве — аж лишився старт-стоп-кадр, який ти задаєш як Serial.begin(baud)",
              12.5, GREY, "middle", style="italic")
    spine = 210
    top, bot = 96, H - 28
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("1837–44", "Морзе / Morse",
         "Крапка-тире: код ЗМІННОЇ довжини. Швидко — та потрібен вправний оператор і добре вухо", False, False),
        ("1870", "Бодо / Baudot",
         "5 однакових одиниць на знак: машинна РІВНОМІРНІСТЬ замість віртуозності руки", False, True),
        ("1874+", "розподільник / distributeur",
         "Один дріт — кілька операторів по черзі: народження поділу часу (TDM)", False, False),
        ("1901", "Маррей / Murray",
         "Клавіатура й перфострічка замість акордів; код-нащадок → ITA-2", False, False),
        ("1900–10-ті", "старт-стоп / Krum, Teletype",
         "Кадр САМ СЕБЕ синхронізує: СТАРТ-біт + дані + СТОП — без спільного дроту такту", False, False),
        ("Розділ 35", "UART",
         "Той самий кадр у кремнії: чому послідовно, асинхронно — і звідки слово «baud»", True, False),
    ]
    n = len(nodes)
    for i, (yr, who, q, dest, accent) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = GREY if dest else INK
        if accent:
            s += circle(spine, y, 10, "#fff", RED, 3)
            s += circle(spine, y, 4.5, RED, RED, 0)
        elif dest:
            s += rect(spine - 8, y - 8, 16, 16, "#fff", GREEN, 2.6, 3)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, (GREEN if dest else GREY), "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5,
                  (RED if accent else (GREEN if dest else col)), "start", "bold")
        s += text(spine + 26, y + 17, q, 12.5, (INK if not dest else GREY), "start", style="italic")
    save("fig-35-0-1-timeline.svg", s)


# ── Рис. 35.0.2 — Морзе (змінна довжина) проти Бодо (5 фіксованих одиниць) ────
def _morse_row(x0, y, pattern, unit=10, h=26, gap=6, color=INK):
    """pattern: рядок із '.' і '-'. Повертає (svg, ширина)."""
    s = ""
    x = x0
    for ch in pattern:
        w = unit if ch == "." else unit * 3
        s += rect(x, y - h / 2, w, h, color, color, 0)
        x += w + gap
    return s, (x - gap - x0)


def _baudot_row(x0, y, bits, cell=24, h=26, color=INK):
    """bits: список 0/1 (5 шт). Однакова ширина завжди. Повертає (svg, ширина)."""
    s = ""
    x = x0
    for b in bits:
        if b:
            s += rect(x, y - h / 2, cell, h, color, color, 0)
        else:
            s += rect(x, y - h / 2, cell, h, "#ffffff", GREY, 1.4)
        x += cell
    return s, (cell * len(bits))


def fig_morse_baudot():
    W, H = 920, 560
    s = header(W, H)
    s += text(W / 2, 36, "Чому Бодо переміг: змінна довжина проти п'яти однакових одиниць", 20, INK, "middle", "bold")
    s += text(W / 2, 58, "машині легко РАХУВАТИ однакові такти й важко ВПІЗНАВАТИ візерунок мінливої довжини",
              12.5, GREY, "middle", style="italic")

    letters = [
        ("E", ".",   [1, 0, 0, 0, 0]),
        ("T", "-",   [0, 0, 0, 0, 1]),
        ("A", ".-",  [1, 1, 0, 0, 0]),
        ("S", "...", [1, 0, 1, 0, 0]),
        ("O", "---", [0, 0, 0, 1, 1]),
    ]

    # ─ ліва панель: Морзе ─
    s += rect(34, 84, 410, 404, "none", FAINT, 2, 14)
    s += text(239, 110, "код Морзе — довжина «гуляє»", 15, INK, "middle", "bold")
    s += text(239, 130, "крапка = 1 одиниця, тире = 3; між знаками — паузи", 11.5, GREY, "middle", style="italic")
    ly = 168
    maxw = 0
    for name, mp, _ in letters:
        s += text(70, ly + 6, name, 16, INK, "end", "bold")
        body, wdt = _morse_row(86, ly, mp, unit=11, h=24, gap=7, color=INK)
        s += body
        maxw = max(maxw, wdt)
        ly += 54
    # «лінійка» під найдовшим/найкоротшим
    s += arrow(86, 460, 86 + 11, 460, GREY, 1.6)
    s += text(86 + 30, 464, "«E» — 1 одиниця", 11.5, GREY, "start")
    s += arrow(250, 478, 250 + 11 * 3 + 6 + 11 * 3 + 6 + 11 * 3, 478, GREY, 1.6)
    s += text(250, 474, "«O» — у 9 разів довше", 11.5, GREY, "start")

    # ─ права панель: Бодо ─
    s += rect(478, 84, 410, 404, "none", FAINT, 2, 14)
    s += text(683, 110, "5-одиничний код (Бодо–Маррей, ITA-2)", 14.5, INK, "middle", "bold")
    s += text(683, 130, "кожен знак — РІВНО 5 однакових клітин (мітка/пропуск)", 11.5, GREY, "middle", style="italic")
    ry = 168
    bx = 600
    # шапка-нумерація бітів
    for j in range(5):
        s += text(bx + 24 * j + 12, 150, str(j + 1), 11, GREY, "middle")
    for name, _, bits in letters:
        s += text(bx - 16, ry + 6, name, 16, INK, "end", "bold")
        body, wdt = _baudot_row(bx, ry, bits, cell=24, h=24, color=INK)
        s += body
        ry += 54
    s += text(683, 470, "ширина однакова → приймач лічить такти, а не «слухає» візерунок", 11.5, GREY, "middle", style="italic")

    s += rect(60, H - 44, W - 120, 30, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 24, "Фіксована довжина — перший крок до автомата: саме її успадкує кадр UART (5/7/8 біт даних).",
              13, INK, "middle", "bold")
    save("fig-35-0-2-morse-baudot.svg", s)


# ── Рис. 35.0.3 — клавіатура Бодо на 5 клавіш та «каданс» ─────────────────────
def fig_keyboard():
    W, H = 880, 520
    s = header(W, H)
    s += text(W / 2, 36, "Клавіатура Бодо: п'ять клавіш, акорд — і ритм, що його задає МАШИНА", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "ліва рука — 2 клавіші, права — 3; літера = комбінація натиснень у такт «кадансу»",
              12.5, GREY, "middle", style="italic")

    # приклад: літера 'A' = біти 1,1,0,0,0 → натиснуті клавіші 1 і 2
    bits = [1, 1, 0, 0, 0]
    keys_x = [250, 312, 430, 492, 554]
    ky = 250
    kw, kh = 50, 96
    groups = [(0, 2, "ліва рука"), (2, 5, "права рука")]
    for a, b, lbl in groups:
        gx0 = keys_x[a] - 8
        gx1 = keys_x[b - 1] + kw + 8
        s += rect(gx0, ky - 30, gx1 - gx0, kh + 60, "none", GREY, 1.4, 10)
        s += text((gx0 + gx1) / 2, ky - 38, lbl, 12.5, GREY, "middle", style="italic")
    for j, x in enumerate(keys_x):
        down = bits[j]
        fill = LRED if down else "#fbfbfb"
        stroke = RED if down else INK
        off = 10 if down else 0
        s += rect(x, ky + off, kw, kh - off, fill, stroke, 2.2, 7)
        s += text(x + kw / 2, ky + kh - 16, str(j + 1), 16, (RED if down else INK), "middle", "bold")
        s += text(x + kw / 2, ky + 0 + (off) + 22, "▼" if down else "", 14, RED, "middle", "bold")
    s += text((keys_x[0] + keys_x[-1] + kw) / 2, ky + kh + 40,
              "натиснуто клавіші 1 і 2  →  код 11000  →  літера «A»", 14, INK, "middle", "bold")

    # каданс зверху — рівномірні такти, що їх диктує апарат
    cy = 150
    s += text(150, cy - 18, "каданс (ритм апарата):", 13, INK, "start", "bold")
    x = 250
    for k in range(7):
        col = RED if k % 2 == 0 else GREY
        s += line(x, cy - 12, x, cy + 12, col, 3)
        x += 48
    s += arrow(250, cy + 26, 250 + 6 * 48, cy + 26, GREY, 1.6)
    s += text(250 + 3 * 48, cy + 44, "натиснути · відпустити · натиснути · …  (оператор підлаштовується ПІД машину)",
              12, GREY, "middle", style="italic")

    s += rect(60, H - 64, W - 120, 48, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 42, "Тут уперше не людина диктує темп, а апарат: дисципліна такту — прямий предок «тактованого» обміну.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, H - 24, "Розподільник на тому кінці читав ці 5 одиниць строго у свої моменти — звідси й сувора рівномірність.",
              12, GREY, "middle", style="italic")
    save("fig-35-0-3-keyboard.svg", s)


# ── Рис. 35.0.4 — розподільник: поділ часу (TDM) на одному дроті ──────────────
def _distributor(cx, cy, r, n, arm_idx, labels, lab_color=INK, title=""):
    s = circle(cx, cy, r, "#fff", INK, 2.4)
    s += circle(cx, cy, 5, INK, INK, 0)
    for k in range(n):
        a0 = -math.pi / 2 + 2 * math.pi * k / n
        a1 = -math.pi / 2 + 2 * math.pi * (k + 1) / n
        x0 = cx + r * math.cos(a0); y0 = cy + r * math.sin(a0)
        s += line(cx, cy, x0, y0, GREY, 1.4)
        am = (a0 + a1) / 2
        lx = cx + (r + 26) * math.cos(am); ly = cy + (r + 26) * math.sin(am)
        anchor = "middle"
        s += text(lx, ly + 4, labels[k], 12.5, lab_color, anchor, "bold")
    # рухома щітка
    aa = -math.pi / 2 + 2 * math.pi * (arm_idx + 0.5) / n
    ax = cx + (r - 6) * math.cos(aa); ay = cy + (r - 6) * math.sin(aa)
    s += arrow(cx, cy, ax, ay, RED, 3)
    if title:
        s += text(cx, cy + r + 52, title, 13, INK, "middle", "bold")
    return s


def fig_tdm():
    W, H = 920, 520
    s = header(W, H)
    s += text(W / 2, 36, "Розподільник Бодо: один дріт — кілька операторів по черзі (поділ часу)", 19, INK, "middle", "bold")
    s += text(W / 2, 58, "рухома щітка віддає лінію кожному на свій проміжок; обидва кінці обертаються В ОДНОМУ такті",
              12.5, GREY, "middle", style="italic")

    labA = ["A", "B", "C", "D"]
    s += _distributor(225, 260, 90, 4, 0, labA, INK,
                      "передавач: 4 оператори → сектори")
    s += text(225, 132, "передавальний бік", 13.5, INK, "middle", "bold")

    labB = ["A′", "B′", "C′", "D′"]
    s += _distributor(695, 260, 90, 4, 0, labB, INK,
                      "приймач: сектори → 4 принтери")
    s += text(695, 132, "приймальний бік", 13.5, INK, "middle", "bold")

    # один спільний дріт між щітками
    s += line(225 + 90 + 6, 260, 695 - 90 - 6, 260, INK, 2.6)
    s += rect(415, 244, 90, 32, "#fff", INK, 1.6, 8)
    s += text(460, 264, "ОДИН дріт", 13, INK, "middle", "bold")
    s += arrow(360, 230, 430, 230, RED, 2.2)
    s += text(395, 222, "5 одиниць «A»", 11.5, RED, "middle", "bold")
    s += arrow(560, 230, 500, 230, RED, 2.2)

    # синхронізація обертів (дуга-зв'язок)
    s += f'<path d="M 225,150 Q 460,70 695,150" fill="none" stroke="{GREEN}" stroke-width="2" stroke-dasharray="6,5"/>\n'
    s += text(460, 92, "обидва колеса крутяться синхронно (інакше A потрапить у принтер B′)",
              12, GREEN, "middle", "bold")

    s += rect(60, H - 64, W - 120, 48, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 42, "Так народився поділ часу (TDM): дорогу лінію ділять, даючи кожному канал на свій інтервал.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, H - 24, "Ціна — жорстка синхронність кінців. UART згодом обере інший шлях: синхронізуватися щознаку.",
              12, GREY, "middle", style="italic")
    save("fig-35-0-4-tdm.svg", s)


# ── допоміжне: цифровий сигнал як послідовність бітів ────────────────────────
def _wave(x0, y_hi, y_lo, unit, segs, color=INK, w=2.6):
    """
    segs: список (level, width_units). level: 1=високо(мітка), 0=низько(пропуск).
    Малює прямокутний сигнал. Повертає (svg, список (x_center, level, x_start, x_end)).
    """
    s = ""
    x = x0
    prev = None
    centers = []
    for level, wid in segs:
        y = y_hi if level else y_lo
        xe = x + wid * unit
        if prev is not None and prev != level:
            s += line(x, y_hi, x, y_lo, color, w)
        s += line(x, y, xe, y, color, w)
        centers.append(((x + xe) / 2, level, x, xe))
        prev = level
        x = xe
    return s, centers


def fig_startstop():
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 34, "Головна спадщина: старт-стоп-кадр телетайпа = кадр UART", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "СТАРТ-біт наново синхронізує приймач щознаку — тому спільний дріт такту НЕ потрібен",
              12.5, GREY, "middle", style="italic")

    x0 = 120
    unit = 56
    hi1, lo1 = 130, 178
    hi2, lo2 = 330, 378

    # ── верх: телетайп ITA-2 (старт + 5 даних + стоп 1.5) ──
    s += text(x0 - 64, (hi1 + lo1) / 2, "телетайп", 12.5, INK, "end", "bold")
    s += text(x0 - 64, (hi1 + lo1) / 2 + 16, "(ITA-2)", 11, GREY, "end")
    data_top = [1, 1, 0, 0, 0]  # «A»
    segs1 = [(1, 1.0), (0, 1.0)] + [(b, 1.0) for b in data_top] + [(1, 1.5), (1, 0.6)]
    body1, c1 = _wave(x0, hi1, lo1, unit, segs1, INK)
    s += body1
    # підписи елементів (верх)
    # індекси у c1: 0=спокій,1=старт,2..6=дані,7=стоп
    s += text(c1[1][0], lo1 + 22, "СТАРТ", 12, RED, "middle", "bold")
    s += line(c1[1][2], hi1 - 14, c1[1][2], lo1 + 8, RED, 1.4, dash="3,3")
    for j in range(5):
        cx = c1[2 + j][0]
        s += text(cx, lo1 + 22, "D%d" % (j + 1), 11.5, INK, "middle", "bold")
        s += text(cx, hi1 - 10, str(data_top[j]), 11, GREY, "middle")
    s += text(c1[7][0], lo1 + 22, "СТОП (≥1.5)", 11.5, INK, "middle", "bold")
    s += text(x0 - 8, hi1 - 6, "мітка (1)", 10.5, GREY, "end")
    s += text(x0 - 8, lo1 + 4, "пропуск (0)", 10.5, GREY, "end")

    # ── низ: сучасний UART (старт + 8 даних + парність + стоп) ──
    s += text(x0 - 64, (hi2 + lo2) / 2, "UART", 12.5, INK, "end", "bold")
    s += text(x0 - 64, (hi2 + lo2) / 2 + 16, "(§35.2)", 11, GREY, "end")
    data_bot = [1, 0, 0, 1, 1, 0, 1, 0]
    unit2 = 36
    segs2 = [(1, 1.0), (0, 1.0)] + [(b, 1.0) for b in data_bot] + [(0, 1.0), (1, 1.5)]
    body2, c2 = _wave(x0, hi2, lo2, unit2, segs2, INK)
    s += body2
    s += text(c2[1][0], lo2 + 22, "СТАРТ", 11.5, RED, "middle", "bold")
    s += line(c2[1][2], hi1 - 14, c2[1][2], lo2 + 8, RED, 1.4, dash="3,3")
    for j in range(8):
        cx = c2[2 + j][0]
        s += text(cx, lo2 + 22, "D%d" % j, 10.5, INK, "middle")
        # точка вибірки — посередині біта
        s += arrow(cx, lo2 + 40, cx, (hi2 + lo2) / 2 + 6, GREEN, 1.5)
    s += text(c2[10][0], lo2 + 22, "P", 10.5, BLUE, "middle", "bold")
    s += text(c2[11][0], lo2 + 22, "СТОП", 10.5, INK, "middle", "bold")
    s += text(x0 + 20, lo2 + 56, "↑ приймач бере відлік посередині кожного біта (за власним лічильником від СТАРТу)",
              11.5, GREEN, "start", style="italic")

    # вертикальна напрямна — однаковий СТАРТ
    s += text(c1[1][2] + 4, 92, "обидва кадри починаються однаково: спад «мітка→пропуск» = СТАРТ",
              12, RED, "start", "bold")

    s += rect(60, H - 70, W - 120, 54, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 47, "Асинхронний кадр UART — це майже незмінений старт-стоп-кадр телетайпа 1900-х.",
              13, INK, "middle", "bold")
    s += text(W / 2, H - 27, "Звідси: лише дроти TX/RX (без дроту такту), але обидві сторони мусять заздалегідь домовитися про baud.",
              12, GREY, "middle", style="italic")
    save("fig-35-0-5-startstop.svg", s)


# ── Рис. 35.0.6 — baud проти біт/с: телетайп 45.45 бод ───────────────────────
def fig_baud():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Що таке «baud»: одиниць за секунду — і чому це не завжди біт/с", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "одиниця названа на честь Бодо; класичний телетайп — 45.45 бод (≈ 60 слів/хв)",
              12.5, GREY, "middle", style="italic")

    # смуга одного знака = 7.5 одиниць
    x0, y = 80, 150
    unit = 88
    parts = [("СТАРТ", 1.0, LRED, RED), ("D1", 1.0, "#fff", INK), ("D2", 1.0, "#fff", INK),
             ("D3", 1.0, "#fff", INK), ("D4", 1.0, "#fff", INK), ("D5", 1.0, "#fff", INK),
             ("СТОП", 1.5, LBLUE, BLUE)]
    x = x0
    for lbl, wdt, fill, col in parts:
        s += rect(x, y, unit * wdt, 56, fill, col, 1.8)
        s += text(x + unit * wdt / 2, y + 33, lbl, 12.5, col, "middle", "bold")
        x += unit * wdt
    # розмір однієї одиниці
    s += arrow(x0, y + 80, x0 + unit, y + 80, GREY, 1.6)
    s += arrow(x0 + unit, y + 80, x0, y + 80, GREY, 1.6)
    s += text(x0 + unit / 2, y + 98, "1 одиниця ≈ 22 мс", 12, GREY, "middle", "bold")
    s += arrow(x0, y - 14, x, y - 14, INK, 1.6)
    s += arrow(x, y - 14, x0, y - 14, INK, 1.6)
    s += text((x0 + x) / 2, y - 22, "1 знак = 1 + 5 + 1.5 = 7.5 одиниць", 13, INK, "middle", "bold")

    # обчислення
    bx, by = 120, 300
    s += rect(bx, by, 660, 120, LGREY, GREY, 1.4, 10)
    s += text(bx + 20, by + 30, "1 бод = 1 одиниця/с  →  при 45.45 бод одна одиниця триває 1/45.45 ≈ 22 мс", 13.5, INK, "start", "bold")
    s += text(bx + 20, by + 56, "знак = 7.5 × 22 мс ≈ 165 мс  →  ≈ 6 знаків/с  →  ≈ 60 слів/хв (≈ 6 знаків/слово)", 13.5, INK, "start")
    s += text(bx + 20, by + 84, "для ДВОХ рівнів (мітка/пропуск) 1 бод = 1 біт/с — тому Serial.begin(9600) це й 9600 біт/с",
              13, GREEN, "start", "bold")

    s += rect(60, H - 40, W - 120, 28, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, H - 21, "Baud рахує СИМВОЛИ на лінії. Збігається з біт/с лише поки символ несе рівно 1 біт.",
              12.5, INK, "middle", "bold")
    save("fig-35-0-6-baud.svg", s)


# ============================================================================
#  §35.1 — Чому послідовно й чому асинхронно
# ============================================================================
BYTE = [1, 0, 1, 1, 0, 0, 1, 0]  # приклад байта, біти D7..D0


def _bitcell(x, y, w, h, b, on_fill="#dfe7fb", on_str=BLUE):
    if b:
        return rect(x, y, w, h, on_fill, on_str, 1.8)
    return rect(x, y, w, h, "#ffffff", GREY, 1.4)


def _stepline(x0, x1, edge, y_hi, y_lo, old, new, color=INK, w=2.6):
    """Один рядок-сигнал: рівень old до edge, перехід, рівень new після."""
    yo = y_hi if old else y_lo
    yn = y_hi if new else y_lo
    s = line(x0, yo, edge, yo, color, w)
    if old != new:
        s += line(edge, y_hi, edge, y_lo, color, w)
    s += line(edge, yn, x1, yn, color, w)
    return s


# ── Рис. 35.1.1 — паралельно проти послідовно ────────────────────────────────
def fig_parallel_serial():
    W, H = 920, 474
    s = header(W, H)
    s += text(W / 2, 34, "Паралельно чи послідовно: дроти проти часу", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "той самий байт 10110010 — або вісьмома дротами за один такт, або одним дротом за вісім",
              12.5, GREY, "middle", style="italic")

    # ─ ліва панель: паралельно ─
    s += rect(34, 80, 410, 354, "none", FAINT, 2, 14)
    s += text(239, 106, "паралельно: 8 дротів, 1 такт", 14.5, INK, "middle", "bold")
    x0, wlen, rh, gap, y0 = 132, 232, 22, 9, 140
    for i in range(8):
        b = BYTE[i]
        yy = y0 + i * (rh + gap)
        s += text(x0 - 14, yy + rh - 6, "D%d" % (7 - i), 11.5, INK, "end", "bold")
        s += line(x0, yy + rh / 2, x0 + wlen, yy + rh / 2, GREY, 1.4)
        s += _bitcell(x0 + wlen / 2 - 16, yy, 32, rh, b)
        s += text(x0 + wlen / 2, yy + rh - 6, str(b), 12.5, (BLUE if b else GREY), "middle", "bold")
    sx = x0 + wlen / 2
    s += line(sx, y0 - 12, sx, y0 + 8 * (rh + gap) - gap + 6, RED, 2, dash="4,4")
    s += text(sx + 10, y0 - 16, "усі біти — в мить t₀", 11, RED, "start", "bold")
    s += text(239, 420, "швидко, та 8 ліній + земля; на відстані дроги «розповзаються» (нижче)",
              10.5, GREY, "middle", style="italic")

    # ─ права панель: послідовно ─
    s += rect(478, 80, 410, 354, "none", FAINT, 2, 14)
    s += text(683, 106, "послідовно: 1 дріт, 8 інтервалів", 14.5, INK, "middle", "bold")
    sx0, cellw, sy = 526, 42, 232
    s += text(sx0 - 12, sy + 22, "лінія", 12, INK, "end", "bold")
    s += line(sx0 - 6, sy + 18, sx0, sy + 18, GREY, 1.4)
    for i in range(8):
        b = BYTE[i]
        xx = sx0 + i * cellw
        s += _bitcell(xx, sy, cellw, 36, b)
        s += text(xx + cellw / 2, sy + 23, str(b), 13, (BLUE if b else GREY), "middle", "bold")
    s += arrow(sx0, sy + 60, sx0 + 8 * cellw, sy + 60, INK, 1.8)
    s += text(sx0 + 8 * cellw, sy + 56, "час →", 12, INK, "start", "bold")
    s += text(683, 420, "одна лінія (+ земля); біти йдуть один за одним у часі",
              10.5, GREY, "middle", style="italic")
    save("fig-35-1-1-parallel-serial.svg", s)


# ── Рис. 35.1.2 — перекіс (skew) убиває паралель на швидкості ─────────────────
def fig_skew():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому паралель програє на швидкості: перекіс (skew)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "лінії стартують разом, але приходять урізнобій — момент вибірки ловить суміш старих і нових бітів",
              12.5, GREY, "middle", style="italic")

    rows = [("D0", 1, 0, 372), ("D1", 0, 1, 402), ("D2", 1, 0, 440), ("D3", 0, 1, 478)]
    x_start, x_end = 150, 760
    tx_edge = 250
    sample_x = 416
    for i, (name, old, new, edge) in enumerate(rows):
        yb = 128 + i * 64
        y_hi, y_lo = yb, yb + 30
        s += text(x_start - 12, (y_hi + y_lo) / 2 + 4, name, 12.5, INK, "end", "bold")
        s += _stepline(x_start, x_end, edge, y_hi, y_lo, old, new, INK, 2.6)
        # значення старе/нове
        s += text(x_start + 6, y_hi - 6 if old else y_lo + 16, str(old), 11, GREY, "start")
        s += text(x_end - 6, y_hi - 6 if new else y_lo + 16, str(new), 11, GREY, "end")
        # що бачить приймач на лінії вибірки
        seen = old if sample_x < edge else new
        s += circle(sample_x, (y_hi if seen else y_lo), 5, ("#fff"), RED, 2)

    # лінія «усі стартують разом» на передавачі
    s += line(tx_edge, 112, tx_edge, 470, GREEN, 2, dash="5,5")
    s += text(tx_edge, 104, "край на передавачі (всі РАЗОМ)", 11.5, GREEN, "middle", "bold")
    # момент вибірки приймача
    s += line(sample_x, 112, sample_x, 500, RED, 2)
    s += text(sample_x + 6, 500 - 2, "момент вибірки приймача", 11.5, RED, "start", "bold")

    s += rect(560, 360, 320, 92, LRED, RED, 1.6, 10)
    s += text(720, 384, "тут приймач читає 0,1,1,0", 12.5, INK, "middle", "bold")
    s += text(720, 404, "а мало бути 0,1,0,1", 12.5, INK, "middle")
    s += text(720, 424, "D2, D3 ще не «доїхали» → байт зіпсовано", 11, RED, "middle", "bold")
    s += text(720, 442, "що вищий темп — то коротший біт і гірший перекіс", 10.5, GREY, "middle", style="italic")
    save("fig-35-1-2-skew.svg", s)


# ── Рис. 35.1.3 — синхронно: окремий дріт такту ──────────────────────────────
def fig_sync():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 34, "Синхронно: окремий дріт такту каже, КОЛИ дивитися на дані", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "приймач бере відлік по фронту такту — момент кожного біта заданий явно (так роблять SPI, I2C)",
              12.5, GREY, "middle", style="italic")
    x0, unit = 150, 76
    bits = [1, 0, 1, 1, 0]
    # такт
    s += text(x0 - 16, 138, "ТАКТ", 12.5, INK, "end", "bold")
    clk = []
    for b in bits:
        clk += [(1, 0.5), (0, 0.5)]
    body, c = _wave(x0, 120, 156, unit, clk, INK, 2.4)
    s += body
    # дані
    s += text(x0 - 16, 238, "ДАНІ", 12.5, INK, "end", "bold")
    segs = [(b, 1.0) for b in bits]
    bodyd, cd = _wave(x0, 220, 256, unit, segs, INK, 2.6)
    s += bodyd
    # точки вибірки — на висхідних фронтах такту (початок кожного біта)
    for k in range(len(bits)):
        sx = x0 + k * unit
        s += line(sx, 120, sx, 256, GREEN, 1.2, dash="3,3")
        s += arrow(sx, 286, sx, 248, GREEN, 1.6)
        s += text(sx, 300, str(bits[k]), 12, GREEN, "middle", "bold")
    s += text(x0 + len(bits) * unit + 12, 238, "↑ відлік", 11.5, GREEN, "start", "bold")
    s += text(x0 + len(bits) * unit + 12, 254, "по фронту", 11, GREEN, "start")
    # дроти
    s += rect(60, 350, W - 120, 64, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 374, "Ціна: окремий дріт ТАКТУ (разом із даними й землею — три лінії).", 13, INK, "middle", "bold")
    s += text(W / 2, 396, "Зате приймачеві не треба власного точного годинника — момент біта приходить дротом.",
              12, GREY, "middle", style="italic")
    save("fig-35-1-3-sync.svg", s)


# ── Рис. 35.1.4 — асинхронно (UART): без дроту такту ─────────────────────────
def fig_async():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 34, "Асинхронно (UART): дроту такту немає — є домовленість і старт-біт", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "приймач веде час ВЛАСНИМ генератором; старт-біт лише запускає відлік щознаку",
              12.5, GREY, "middle", style="italic")
    x0, unit = 200, 60
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    segs = [(1, 1.0), (0, 1.0)] + [(b, 1.0) for b in bits] + [(1, 1.5)]
    body, c = _wave(x0, 150, 198, unit, segs, INK, 2.6)
    s += text(x0 - 16, 178, "ДАНІ (TX)", 12.5, INK, "end", "bold")
    s += body
    s += text(c[1][0], 218, "СТАРТ", 11.5, RED, "middle", "bold")
    s += line(c[1][2], 134, c[1][2], 206, RED, 1.4, dash="3,3")
    for j in range(8):
        s += text(c[2 + j][0], 218, "D%d" % j, 10.5, INK, "middle")
    s += text(c[10][0], 218, "СТОП", 11, INK, "middle", "bold")
    s += text(x0 - 16, 130, "спокій = 1", 10.5, GREY, "end")

    # генератор приймача
    gx, gy = 660, 300
    s += circle(gx, gy, 30, "#fff", INK, 2)
    s += text(gx, gy - 4, "f_rx", 13, INK, "middle", "bold")
    s += text(gx, gy + 14, "≈ baud", 10.5, GREY, "middle")
    s += arrow(gx - 30, gy, c[6][0], 206, GREEN, 1.8)
    s += text(gx + 36, gy, "власний годинник приймача", 12, GREEN, "start", "bold")
    s += text(gx + 36, gy + 18, "(не дріт, а домовлена швидкість)", 10.5, GREY, "start", style="italic")

    s += rect(60, 360, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 383, "Виграш: лише TX і RX (+ земля), без дроту такту — два пристрої, два дроти даних.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 403, "Ціна: обидві сторони мусять наперед збігтися у baud, а їхні годинники — бути «досить точними».",
              11.5, GREY, "middle", style="italic")
    save("fig-35-1-4-async.svg", s)


# ── Рис. 35.1.5 — як приймач ловить біти без дроту такту (передискретизація) ──
def fig_oversample():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Як приймач знаходить біти без дроту такту: передискретизація", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "швидкий внутрішній тактик (≈16× на біт): зловити спад СТАРТу, далі брати відлік ПОСЕРЕДИНІ кожного біта",
              12.5, GREY, "middle", style="italic")
    x0, unit = 150, 130
    # сигнал: спокій(0.4), старт(1), D0(1), D1(1), D2(1) — показуємо старт + 3 біти
    show = [(1, 0.4), (0, 1.0), (1, 1.0), (0, 1.0), (1, 1.0)]
    labels = [None, "СТАРТ", "D0=1", "D1=0", "D2=1"]
    body, c = _wave(x0, 130, 176, unit, show, INK, 2.8)
    s += body
    seglab = {1: "СТАРТ", 2: "D0=1", 3: "D1=0", 4: "D2=1"}
    for seg_i, lab in seglab.items():
        ylab = 122 if show[seg_i][0] else 168
        s += text(c[seg_i][0], ylab, lab, 10.5, INK, "middle", "bold")
    # дрібні тики ≈16× під кожним бітом (показуємо 8, підписуємо 16×)
    tick_y = 196
    for seg_i in range(1, 5):
        cx0 = c[seg_i][2]
        for t in range(8):
            tx = cx0 + (t + 0.5) * unit / 8
            s += line(tx, tick_y, tx, tick_y + 8, GREY, 1)
    s += text(x0 - 4, tick_y + 26, "внутрішні тики ≈16× на біт →", 11, GREY, "start")
    # детект спаду старту
    sxe = c[1][2]
    s += arrow(sxe, 104, sxe, 128, RED, 1.8)
    s += text(sxe, 98, "спад: «увага, СТАРТ»", 11, RED, "middle", "bold")
    # перевірка середини старту (синім) + вибірки посередині бітів (зеленим)
    for seg_i in (1, 2, 3, 4):
        cx = c[seg_i][0]
        col = BLUE if seg_i == 1 else GREEN
        s += line(cx, 116, cx, 184, col, 1.2, dash="3,3")
        ytip = 130 if show[seg_i][0] else 176
        s += arrow(cx, 236, cx, ytip, col, 1.6)
    s += text(c[1][0], 252, "перевірка середини", 9.5, BLUE, "middle", "bold")
    for seg_i in (2, 3, 4):
        s += text(c[seg_i][0], 252, "відлік", 10.5, GREEN, "middle", "bold")
        s += text(c[seg_i][0], 265, "по центру", 9.5, GREEN, "middle")

    s += rect(60, 360, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 383, "Вибірка ПОСЕРЕДИНІ біта — найдалі від обох країв, де сигнал найстабільніший.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 403, "Передискретизація 16× — типове число; вона ж дає змогу терпіти невеликий розсинхрон годинників.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-1-5-oversample.svg", s)


# ── Рис. 35.1.6 — фізичне з'єднання двох пристроїв (TX↔RX, спільний GND) ──────
def fig_wiring():
    W, H = 860, 430
    s = header(W, H)
    s += text(W / 2, 34, "Як це виглядає на столі: TX↔RX навхрест і спільна земля", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "вихід одного йде на вхід іншого; обидва напрямки працюють одночасно (повний дуплекс)",
              12.5, GREY, "middle", style="italic")

    def dev(x, y, name):
        out = rect(x, y, 150, 150, "#fbfbfb", INK, 2.2, 12)
        out += text(x + 75, y + 26, name, 14.5, INK, "middle", "bold")
        return out, dict(TX=(x + 150, y + 60), RX=(x + 150, y + 100), GND=(x + 150, y + 132),
                         TXl=(x, y + 60), RXl=(x, y + 100), GNDl=(x, y + 132))

    da, pa = dev(90, 130, "Пристрій A")
    db, pb = dev(620, 130, "Пристрій B")
    s += da + db
    for p in ("TX", "RX", "GND"):
        s += text(pa[p][0] - 8, pa[p][1] + 4, p, 11.5, INK, "end", "bold")
        s += text(pb["%sl" % p][0] + 8, pb["%sl" % p][1] + 4, p, 11.5, INK, "start", "bold")

    # A.TX -> B.RX (червоний), A.RX <- B.TX (синій), GND-GND
    ax_tx = pa["TX"]; bx_rx = (pb["RXl"][0], pb["RXl"][1])
    s += line(ax_tx[0], ax_tx[1], 420, ax_tx[1], RED, 2.4)
    s += line(420, ax_tx[1], 420, bx_rx[1], RED, 2.4)
    s += arrow(420, bx_rx[1], bx_rx[0], bx_rx[1], RED, 2.4)
    s += text(420, ax_tx[1] - 8, "A.TX → B.RX", 11.5, RED, "middle", "bold")

    ax_rx = pa["RXl"] if False else (pa["RX"][0], pa["RX"][1])
    bx_tx = (pb["RXl"][0], pb["TXl"][1])  # B.TX на лівому боці B
    bx_tx = (pb["TXl"][0], pb["TXl"][1])
    s += arrow(460, pa["RX"][1], pa["RX"][0], pa["RX"][1], BLUE, 2.4)
    s += line(460, pa["RX"][1], 460, bx_tx[1], BLUE, 2.4)
    s += line(460, bx_tx[1], bx_tx[0], bx_tx[1], BLUE, 2.4)
    s += text(440, pa["RX"][1] + 18, "B.TX → A.RX", 11.5, BLUE, "middle", "bold")

    s += line(pa["GND"][0], pa["GND"][1], 440, pa["GND"][1], INK, 2.2)
    s += line(440, pa["GND"][1], pb["GNDl"][0], pb["GNDl"][1], INK, 2.2)
    s += text(440, pa["GND"][1] + 18, "GND — GND (спільна опора)", 11.5, INK, "middle", "bold")

    s += rect(60, 320, W - 120, 56, LRED, RED, 1.6, 10)
    s += text(W / 2, 343, "Часта помилка новачка: з'єднати TX↔TX. Треба НАВХРЕСТ — вихід на вхід.", 12.5, INK, "middle", "bold")
    s += text(W / 2, 363, "І обов'язково спільна земля: без неї рівні «0/1» нема відносно чого міряти (§35.4).",
              11.5, GREY, "middle", style="italic")
    save("fig-35-1-6-wiring.svg", s)


# ── Рис. 35.1.7 — карта: послідовно/паралельно × синхронно/асинхронно ────────
def fig_map():
    W, H = 780, 540
    s = header(W, H)
    s += text(W / 2, 34, "Карта ліній зв'язку: дві осі рішень", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "де серед них UART — і чому саме «асинхронна послідовна»",
              12.5, GREY, "middle", style="italic")
    gx, gy, cw, ch = 180, 110, 280, 170
    # сітка 2×2
    for c in range(3):
        s += line(gx + c * cw, gy, gx + c * cw, gy + 2 * ch, GREY, 1.4)
    for r in range(3):
        s += line(gx, gy + r * ch, gx + 2 * cw, gy + r * ch, GREY, 1.4)
    # підписи осей
    s += text(gx + cw / 2, gy - 14, "ПОСЛІДОВНО (1 лінія)", 12.5, INK, "middle", "bold")
    s += text(gx + cw + cw / 2, gy - 14, "ПАРАЛЕЛЬНО (N ліній)", 12.5, INK, "middle", "bold")
    s += text(gx - 16, gy + ch / 2, "СИНХРОННО", 12.5, INK, "end", "bold")
    s += text(gx - 16, gy + ch / 2 + 16, "(є дріт такту)", 10.5, GREY, "end")
    s += text(gx - 16, gy + ch + ch / 2, "АСИНХРОННО", 12.5, INK, "end", "bold")
    s += text(gx - 16, gy + ch + ch / 2 + 16, "(нема дроту такту)", 10.5, GREY, "end")

    def cell(cx, cy, title, sub, hot=False):
        out = ""
        if hot:
            out += rect(cx + 6, cy + 6, cw - 12, ch - 12, LGRN, GREEN, 2.4, 8)
        out += text(cx + cw / 2, cy + ch / 2 - 6, title, 15, (GREEN if hot else INK), "middle", "bold")
        out += text(cx + cw / 2, cy + ch / 2 + 16, sub, 11.5, GREY, "middle", style="italic")
        return out

    # синхронно-послідовно
    s += cell(gx, gy, "шина з тактом", "дані + окремий дріт такту")
    # синхронно-паралельно
    s += cell(gx + cw, gy, "паралельний порт", "багато ліній + строб/такт")
    # асинхронно-послідовно — UART
    s += cell(gx, gy + ch, "UART", "старт-стоп, домовлений baud", hot=True)
    # асинхронно-паралельно
    s += cell(gx + cw, gy + ch, "майже не вживають", "перекіс ліній робить це марним")

    s += rect(60, gy + 2 * ch + 26, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, gy + 2 * ch + 49, "UART = асинхронна ПОСЛІДОВНА лінія: одна лінія на напрям, без дроту такту.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, gy + 2 * ch + 69, "Синхронні послідовні шини (з дротом такту) — наступні розділи модуля.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-1-7-map.svg", s)


# ============================================================================
#  §35.2 — Кадр UART: старт, дані, парність, стоп
# ============================================================================
# приклад: байт 0xB5 = 1011 0101 (b7..b0); на дроті LSB-first → D0..D7:
WIRE = [1, 0, 1, 0, 1, 1, 0, 1]   # b0,b1,…,b7
REG = [1, 0, 1, 1, 0, 1, 0, 1]    # b7,b6,…,b0  (для регістрового подання)


def _ones(bits):
    return sum(bits)


# ── Рис. 35.2.1 — повний кадр з підписами ────────────────────────────────────
def fig21_frame():
    W, H = 950, 470
    s = header(W, H)
    s += text(W / 2, 34, "Повний кадр UART: спокій · СТАРТ · дані (LSB→) · парність · СТОП", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "приклад: байт 0xB5, формат 8-біт, парність парна (even), 1 стоп",
              12.5, GREY, "middle", style="italic")
    x0, unit = 118, 62
    hi, lo = 150, 202
    par = _ones(WIRE) % 2            # even-parity bit
    segs = [(1, 1.0), (0, 1.0)] + [(b, 1.0) for b in WIRE] + [(par, 1.0), (1, 1.0), (1, 0.5)]
    body, c = _wave(x0, hi, lo, unit, segs, INK, 2.8)
    s += body
    # рівні
    s += text(x0 - 10, hi + 4, "1 (мітка)", 10.5, GREY, "end")
    s += text(x0 - 10, lo + 4, "0 (пропуск)", 10.5, GREY, "end")
    # підписи елементів
    s += text(c[0][0], hi - 12, "спокій", 11, GREY, "middle", style="italic")
    s += text(c[1][0], lo + 22, "СТАРТ", 12, RED, "middle", "bold")
    for j in range(8):
        cx = c[2 + j][0]
        s += text(cx, lo + 22, "D%d" % j, 11, INK, "middle", "bold")
        s += text(cx, (hi - 8 if WIRE[j] else lo + 38), str(WIRE[j]), 11, GREY, "middle")
    s += text(c[10][0], lo + 22, "P", 12, BLUE, "middle", "bold")
    s += text(c[10][0], lo + 38, str(par), 11, BLUE, "middle")
    s += text(c[11][0], lo + 22, "СТОП", 11.5, INK, "middle", "bold")
    s += text(c[12][0] + 6, hi - 12, "спокій", 11, GREY, "middle", style="italic")
    # дужка під даними
    bx0, bx1 = c[2][2], c[9][3]
    s += arrow((bx0 + bx1) / 2, 300, bx0, 300, GREY, 1.5)
    s += arrow((bx0 + bx1) / 2, 300, bx1, 300, GREY, 1.5)
    s += text((bx0 + bx1) / 2, 318, "8 біт даних — молодший (D0) першим", 12, INK, "middle", "bold")
    # старт-дужка
    s += line(c[1][2], 120, c[1][2], lo + 8, RED, 1.2, dash="3,3")
    s += text(c[1][2], 112, "перепад 1→0 будить приймач", 10.5, RED, "middle", "bold")

    s += rect(60, 360, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 383, "Кадр завжди: рівно 1 старт-біт, потім дані, (необов'язково) парність, потім ≥1 стоп-біт.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 403, "Поза кадром лінія простоює у «1» — тож наступний старт завжди видно як перепад униз.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-2-1-frame.svg", s)


# ── Рис. 35.2.2 — порядок бітів: молодший першим (LSB first) ──────────────────
def fig22_lsb():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Порядок бітів: на дроті молодший біт іде ПЕРШИМ (LSB first)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "у пам'яті байт пишуть старшим зліва (0xB5), а в лінію він іде «задом наперед»",
              12.5, GREY, "middle", style="italic")
    # регістр: b7..b0 зліва направо
    rx, ry, cw = 250, 110, 50
    s += text(rx - 14, ry + 34, "байт", 12.5, INK, "end", "bold")
    s += text(rx - 14, ry + 50, "0xB5", 12, GREY, "end")
    for i in range(8):
        b = REG[i]
        s += _bitcell(rx + i * cw, ry, cw, 48, b)
        s += text(rx + i * cw + cw / 2, ry + 30, str(b), 15, (BLUE if b else GREY), "middle", "bold")
        s += text(rx + i * cw + cw / 2, ry - 8, "b%d" % (7 - i), 11, INK, "middle")
    s += text(rx, ry + 70, "старший (MSB)", 10.5, GREY, "start")
    s += text(rx + 8 * cw, ry + 70, "молодший (LSB)", 10.5, GREY, "end")

    # дріт: слоти D0..D7 = b0..b7
    wx, wy = 250, 280
    s += text(wx - 14, wy + 30, "дріт", 12.5, INK, "end", "bold")
    s += text(wx - 14, wy + 46, "у часі →", 11, GREY, "end")
    for i in range(8):
        b = WIRE[i]
        s += _bitcell(wx + i * cw, wy, cw, 44, b)
        s += text(wx + i * cw + cw / 2, wy + 28, str(b), 15, (BLUE if b else GREY), "middle", "bold")
        s += text(wx + i * cw + cw / 2, wy - 6, "D%d" % i, 11, INK, "middle")
    # стрілки b0->D0 (хрест), b7->D7
    # b0 — у регістрі праворуч (i=7), D0 — на дроті ліворуч (i=0)
    s += arrow(rx + 7 * cw + cw / 2, ry + 52, wx + 0 * cw + cw / 2, wy - 10, RED, 2)
    s += text((rx + 7 * cw + wx) / 2 + 40, 230, "b0 → перший на дроті", 11.5, RED, "middle", "bold")
    s += arrow(rx + 0 * cw + cw / 2, ry + 52, wx + 7 * cw + cw / 2, wy - 10, GREEN, 2)
    s += text((rx + wx) / 2 + 150, 250, "b7 → останній", 11, GREEN, "middle", "bold")

    s += rect(60, 360, W - 120, 50, LRED, RED, 1.6, 10)
    s += text(W / 2, 390, "Тому на осцилографі біти йдуть «навпаки» до запису 0xB5 — не помилка, а саме LSB-first.",
              12.5, INK, "middle", "bold")
    save("fig-35-2-2-lsb.svg", s)


# ── Рис. 35.2.3 — кількість біт даних і запис «8N1» ──────────────────────────
def fig23_format():
    W, H = 900, 460
    s = header(W, H)
    s += text(W / 2, 34, "Формат кадру й запис «8N1»", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "три параметри кадру стискають у короткий код: біти даних, парність, стоп-біти",
              12.5, GREY, "middle", style="italic")

    # розшифровка 8N1
    s += text(170, 110, "8", 34, BLUE, "middle", "bold")
    s += text(220, 110, "N", 34, GREEN, "middle", "bold")
    s += text(265, 110, "1", 34, RED, "middle", "bold")
    s += line(170, 124, 170, 150, BLUE, 1.6)
    s += line(220, 124, 220, 150, GREEN, 1.6)
    s += line(265, 124, 265, 150, RED, 1.6)
    s += text(150, 168, "біт даних (5–9, типово 8)", 12.5, BLUE, "start", "bold")
    s += text(150, 190, "парність: N-нема / E-парна / O-непарна", 12.5, GREEN, "start", "bold")
    s += text(150, 212, "стоп-біти: 1 / 1.5 / 2", 12.5, RED, "start", "bold")

    # таблиця типових форматів
    bx, by = 470, 96
    rows = [
        ("8N1", "8 даних, без парності, 1 стоп", "стандарт де-факто (10 біт/байт)"),
        ("7E1", "7 даних, парна парність, 1 стоп", "класичний ASCII-текст"),
        ("8E1", "8 даних, парна парність, 1 стоп", "коли треба контроль помилок"),
        ("8N2", "8 даних, без парності, 2 стоп", "трохи більший запас на синхрон"),
    ]
    s += rect(bx, by, 390, 230, "#fbfbfb", GREY, 1.4, 10)
    s += text(bx + 16, by + 26, "типові формати", 13, INK, "start", "bold")
    yy = by + 52
    for code, what, note in rows:
        s += text(bx + 16, yy, code, 13.5, INK, "start", "bold")
        s += text(bx + 70, yy, what, 11.5, INK, "start")
        s += text(bx + 70, yy + 16, note, 10.5, GREY, "start", style="italic")
        yy += 44

    s += rect(60, 360, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 383, "Обидві сторони мусять збігтися у ВСІХ трьох параметрах, не лише у baud.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 403, "«115200 8N1» — повний опис лінії: швидкість + формат кадру.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-2-3-format.svg", s)


# ── Рис. 35.2.4 — як рахується біт парності ──────────────────────────────────
def fig24_parity():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Біт парності: підрахунок одиниць", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "парна (even) робить загальне число одиниць парним; непарна (odd) — непарним",
              12.5, GREY, "middle", style="italic")
    data = WIRE  # 0xB5 на дроті, п'ять одиниць
    n1 = _ones(data)
    cw, dx, dy = 56, 200, 110
    s += text(dx - 14, dy + 32, "дані", 12.5, INK, "end", "bold")
    for i in range(8):
        b = data[i]
        s += _bitcell(dx + i * cw, dy, cw, 46, b)
        s += text(dx + i * cw + cw / 2, dy + 30, str(b), 15, (BLUE if b else GREY), "middle", "bold")
    s += text(dx + 8 * cw + 16, dy + 30, "одиниць: %d (непарно)" % n1, 13, INK, "start", "bold")

    # дві гілки
    pe = n1 % 2          # even-parity bit
    po = 1 - pe          # odd-parity bit
    yb = 230
    s += rect(150, yb, 320, 86, LGRN, GREEN, 1.4, 10)
    s += text(310, yb + 24, "парна (even): P = %d" % pe, 13.5, GREEN, "middle", "bold")
    s += text(310, yb + 46, "5 + %d = %d одиниць — ПАРНО" % (pe, n1 + pe), 12, INK, "middle")
    s += text(310, yb + 66, "P = XOR усіх біт даних", 11, GREY, "middle", style="italic")
    s += rect(500, yb, 320, 86, LBLUE, BLUE, 1.4, 10)
    s += text(660, yb + 24, "непарна (odd): P = %d" % po, 13.5, BLUE, "middle", "bold")
    s += text(660, yb + 46, "5 + %d = %d одиниць — НЕПАРНО" % (po, n1 + po), 12, INK, "middle")
    s += text(660, yb + 66, "P = NOT XOR усіх біт даних", 11, GREY, "middle", style="italic")

    s += rect(60, 350, W - 120, 50, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 380, "Передавач додає P за правилом; приймач рахує одиниці сам і звіряє — не збіглося, є помилка.",
              12.5, INK, "middle", "bold")
    save("fig-35-2-4-parity.svg", s)


# ── Рис. 35.2.5 — що парність ловить, а що пропускає ─────────────────────────
def fig25_parity_limits():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Межа парності: ловить НЕПАРНЕ число помилок, пропускає парне", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "один перевернутий біт — видно; два — парність знову «сходиться», і помилку не помічено",
              12.5, GREY, "middle", style="italic")
    base = WIRE
    pe = _ones(base) % 2
    cw = 40
    cases = [
        ("без помилок", base, [], GREEN, "OK: парність сходиться"),
        ("1 біт перевернувся", base, [3], RED, "виявлено: парність НЕ сходиться"),
        ("2 біти перевернулись", base, [3, 6], "#b08900", "ПРОПУЩЕНО: парність знову сходиться"),
    ]
    y = 100
    for title, bits, flips, col, verdict in cases:
        cur = list(bits)
        for f in flips:
            cur[f] ^= 1
        s += text(120, y + 26, title, 12.5, INK, "start", "bold")
        x0 = 330
        for i in range(8):
            flipped = i in flips
            stroke = RED if flipped else (GREY if not cur[i] else BLUE)
            s += _bitcell(x0 + i * cw, y, cw, 36, cur[i], on_str=(RED if flipped else BLUE))
            s += text(x0 + i * cw + cw / 2, y + 24, str(cur[i]), 13, (RED if flipped else (BLUE if cur[i] else GREY)), "middle", "bold")
            if flipped:
                s += text(x0 + i * cw + cw / 2, y - 6, "↯", 13, RED, "middle", "bold")
        # біт парності (незмінний, від передавача)
        s += _bitcell(x0 + 8 * cw + 10, y, cw, 36, pe, on_str=GREEN)
        s += text(x0 + 8 * cw + 10 + cw / 2, y + 24, str(pe), 13, GREEN, "middle", "bold")
        s += text(x0 + 8 * cw + 10 + cw / 2, y - 6, "P", 11, GREEN, "middle", "bold")
        tot = (_ones(cur) + pe) % 2
        s += text(x0 + 9 * cw + 34, y + 24, verdict, 12, col, "start", "bold")
        y += 80

    s += rect(60, 348, W - 120, 52, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 378, "Парність — найдешевший контроль: 1 біт ловить будь-яке непарне число збоїв, та не виправляє їх.",
              12, INK, "middle", "bold")
    save("fig-35-2-5-parity-limits.svg", s)


# ── Рис. 35.2.6 — стоп-біти й кадри підряд ───────────────────────────────────
def fig26_stop():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Стоп-біт гарантує повернення у спокій — і чистий старт наступного кадру", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "1 / 1.5 / 2 стоп-біти: довший стоп дає приймачеві трохи більше запасу між знаками",
              12.5, GREY, "middle", style="italic")
    dat = [1, 0, 0, 1]   # короткий приклад (4 біти даних для наочності)

    def frame_segs(stop_w):
        return [(0, 1.0)] + [(b, 1.0) for b in dat] + [(1, stop_w)]

    # верх: два кадри підряд, 1 стоп
    x0, unit = 130, 50
    segs1 = [(1, 0.6)] + frame_segs(1.0) + frame_segs(1.0) + [(1, 0.5)]
    body1, c1 = _wave(x0, 120, 162, unit, segs1, INK, 2.6)
    s += text(x0 - 16, 146, "1 стоп", 12, INK, "end", "bold")
    s += body1
    # позначити старти/стопи
    s += text(c1[1][0], 182, "START", 9.5, RED, "middle", "bold")
    s += text(c1[6][0], 182, "STOP", 9.5, INK, "middle", "bold")
    s += text(c1[7][0], 182, "START", 9.5, RED, "middle", "bold")
    s += text(c1[12][0], 182, "STOP", 9.5, INK, "middle", "bold")
    s += text((c1[6][0] + c1[7][0]) / 2, 104, "стоп→старт: завжди є перепад вниз", 10.5, GREEN, "middle", "bold")

    # низ: один кадр, 2 стопи
    segs2 = [(1, 0.6)] + frame_segs(2.0) + [(1, 0.8)]
    body2, c2 = _wave(x0, 250, 292, unit, segs2, INK, 2.6)
    s += text(x0 - 16, 276, "2 стоп", 12, INK, "end", "bold")
    s += body2
    s += text(c2[1][0], 312, "START", 9.5, RED, "middle", "bold")
    sx = c2[6][2]
    s += arrow(sx, 330, sx + 2 * unit, 330, GREY, 1.5)
    s += arrow(sx + 2 * unit, 330, sx, 330, GREY, 1.5)
    s += text(sx + unit, 326, "2 одиниці стоп", 10.5, GREY, "middle", "bold")

    s += rect(60, 358, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 381, "Стоп-біт («1») гарантує, що перед кожним стартом лінія в спокої — інакше перепад старту зник би.",
              12, INK, "middle", "bold")
    s += text(W / 2, 401, "Більше стоп-біт = більший проміжок між знаками = трохи легше приймачеві за поганого синхрону.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-2-6-stop.svg", s)


# ── Рис. 35.2.7 — накладні витрати кадру й час байта ─────────────────────────
def fig27_overhead():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Накладні витрати: для 8N1 на 8 корисних біт припадає 10 на лінії", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "1 старт + 8 даних + 1 стоп = 10 біт/байт → корисна частка 80%",
              12.5, GREY, "middle", style="italic")
    x0, cw, y = 120, 66, 110
    cells = [("START", RED, LRED)] + [("D%d" % i, BLUE, "#dfe7fb") for i in range(8)] + [("STOP", INK, LGREY)]
    for i, (lab, col, fill) in enumerate(cells):
        s += rect(x0 + i * cw, y, cw, 50, fill, col, 1.8)
        s += text(x0 + i * cw + cw / 2, y + 30, lab, 11, col, "middle", "bold")
    # дужка «корисні 8»
    bx0 = x0 + 1 * cw
    bx1 = x0 + 9 * cw
    s += arrow((bx0 + bx1) / 2, y + 74, bx0, y + 74, GREEN, 1.6)
    s += arrow((bx0 + bx1) / 2, y + 74, bx1, y + 74, GREEN, 1.6)
    s += text((bx0 + bx1) / 2, y + 92, "8 корисних біт", 12, GREEN, "middle", "bold")
    s += arrow(x0, y - 10, x0 + 10 * cw, y - 10, INK, 1.6)
    s += arrow(x0 + 10 * cw, y - 10, x0, y - 10, INK, 1.6)
    s += text(x0 + 5 * cw, y - 16, "10 біт на лінії", 12, INK, "middle", "bold")

    bx, by = 150, 250
    s += rect(bx, by, 600, 120, LGREY, GREY, 1.4, 10)
    s += text(bx + 20, by + 30, "час байта = 10 / baud", 14, INK, "start", "bold")
    s += text(bx + 20, by + 58, "9600 8N1  : 10 / 9600   ≈ 1.04 мс/байт  →  ≈ 960 байт/с", 13, INK, "start")
    s += text(bx + 20, by + 84, "115200 8N1: 10 / 115200 ≈ 86.8 мкс/байт →  ≈ 11 520 байт/с", 13, INK, "start")
    s += text(bx + 20, by + 108, "(парність додала б 11-й біт — ще −9% швидкості)", 11, GREY, "start", style="italic")

    save("fig-35-2-7-overhead.svg", s)


# ============================================================================
#  §35.3 — Швидкість (baud) і розсинхрон (допуск на розбіжність такту)
# ============================================================================

# ── Рис. 35.3.1 — генератор baud: дільник тактової частоти ───────────────────
def fig31_baudgen():
    W, H = 920, 410
    s = header(W, H)
    s += text(W / 2, 34, "Звідки береться baud: дільник тактової частоти", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "периферійну частоту ділять на ЦІЛЕ число й на передискретизацію (типово 16×)",
              12.5, GREY, "middle", style="italic")

    def blk(x, w, t1, t2, col=INK, fill="#fbfbfb"):
        out = rect(x, 120, w, 70, fill, col, 2, 10)
        out += text(x + w / 2, 150, t1, 13.5, col, "middle", "bold")
        out += text(x + w / 2, 172, t2, 11, GREY, "middle")
        return out

    s += blk(70, 150, "f_periph", "напр. 16 МГц")
    s += arrow(220, 155, 268, 155, INK, 2.2)
    s += blk(270, 140, "÷ DIV", "ціле число")
    s += arrow(410, 155, 458, 155, INK, 2.2)
    s += blk(460, 160, "÷ 16", "передискретизація")
    s += arrow(620, 155, 668, 155, GREEN, 2.4)
    s += blk(670, 170, "baud", "біт за секунду", GREEN, LGRN)

    s += text(W / 2, 232, "baud = f_periph / (16 × DIV)", 17, INK, "middle", "bold")

    s += rect(150, 256, 620, 96, LGREY, GREY, 1.4, 10)
    s += text(170, 282, "приклад: ціль 9600 при 16 МГц", 13, INK, "start", "bold")
    s += text(170, 306, "DIV = 16 000 000 / (16 × 9600) = 104.17  →  округлюємо до 104", 12.5, INK, "start")
    s += text(170, 330, "реально = 16 000 000 / (16 × 104) = 9615 бод  →  похибка +0.16% (дрібниця)",
              12.5, GREEN, "start", "bold")
    s += text(W / 2, 384, "Ціле DIV рідко дає точну ціль — звідси похибка baud, що з'їдає частину допуску.",
              12, GREY, "middle", style="italic")
    save("fig-35-3-1-baudgen.svg", s)


# ── Рис. 35.3.2 — накопичення зсуву відліку вздовж кадру ─────────────────────
def fig32_drift():
    W, H = 960, 440
    s = header(W, H)
    s += text(W / 2, 34, "Розсинхрон накопичується: відлік «повзе» від старту до кінця кадру", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "приймач синхронізується лише на СТАРТі; далі похибка росте з кожним бітом (тут RX на +5%)",
              12.5, GREY, "middle", style="italic")
    labels = ["ST", "0", "1", "2", "3", "4", "5", "6", "7", "SP"]
    x0, unit = 120, 78
    yc, hh = 200, 44
    # клітини кадру
    for i, lab in enumerate(labels):
        xx = x0 + i * unit
        fill = LRED if lab == "ST" else (LGREY if lab == "SP" else "#ffffff")
        s += rect(xx, yc, unit, hh, fill, GREY, 1.3)
        s += text(xx + unit / 2, yc + hh + 16, lab, 11, INK, "middle", "bold")
    # центри бітів — ідеальні точки відліку TX (зелені)
    e = 0.05
    for k in range(len(labels)):
        cxx = x0 + (k + 0.5) * unit
        s += line(cxx, yc - 8, cxx, yc + hh + 4, GREEN, 1.2, dash="3,3")
        s += circle(cxx, yc - 16, 4, GREEN, GREEN, 0)
        # точка відліку RX (зсунута на (k+0.5)*e біта праворуч)
        rxx = x0 + (k + 0.5) * unit * (1 + e)
        s += circle(rxx, yc + hh + 30, 5, "#fff", RED, 2)
        if k in (0, 4, 9):
            s += arrow(cxx, yc + hh + 30, rxx - 5, yc + hh + 30, RED, 1.4)
    s += text(x0 - 8, yc - 16, "TX центри →", 10.5, GREEN, "end", "bold")
    s += text(x0 - 8, yc + hh + 34, "RX відлік →", 10.5, RED, "end", "bold")
    # стрілка-«зсув росте»
    s += text(x0 + 9.5 * unit + 6, yc + hh + 34, "на стоп-біті зсув ≈ 9.5×5% = 0.475 біта", 11, RED, "start", "bold")

    s += rect(60, 360, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 383, "Похибка на біті k ≈ (k + 0.5) × (розбіжність такту). Найбільша вона на ОСТАННЬОМУ біті кадру.",
              12, INK, "middle", "bold")
    s += text(W / 2, 403, "Синхронізація скидає її аж на наступному старті — тому довгі кадри вразливіші.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-3-2-drift.svg", s)


# ── Рис. 35.3.3 — бюджет допуску: лінійне зростання до ±0.5 біта ─────────────
def fig33_budget():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Бюджет допуску: відлік мусить лишитися в межах ±0.5 біта", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "похибка росте лінійно з номером біта; межа — пів-біта на останньому відліку (k≈9.5)",
              12.5, GREY, "middle", style="italic")
    # осі
    ox, oy = 130, 320
    axw, axh = 680, 220
    s += arrow(ox, oy, ox + axw, oy, INK, 1.8)
    s += arrow(ox, oy, ox, oy - axh, INK, 1.8)
    s += text(ox + axw, oy + 22, "номер біта k", 12, INK, "end")
    s += text(ox - 10, oy - axh, "зсув (у бітах)", 12, INK, "end")
    # шкала по x: 0..10
    for k in range(0, 11, 2):
        xx = ox + axw * k / 10
        s += line(xx, oy, xx, oy + 5, INK, 1.4)
        s += text(xx, oy + 20, str(k), 11, GREY, "middle")
    # лінія межі 0.5
    ylim = oy - axh * (0.5 / 0.6)
    s += line(ox, ylim, ox + axw, ylim, RED, 2, dash="6,4")
    s += text(ox + 6, ylim - 6, "межа = 0.5 біта (край вікна)", 11.5, RED, "start", "bold")
    s += rect(ox, oy - axh, axw, ylim - (oy - axh), "#fdeeee", "none", 0)
    # три прямі e=2/5/6 %
    def eline(e, col, lab):
        x_end = 10.0
        y_at = lambda k: oy - axh * ((0.5 + k) * e / 0.6)
        out = line(ox, oy - axh * (0.5 * e / 0.6), ox + axw, y_at(x_end), col, 2.4)
        out += text(ox + axw + 4, y_at(x_end) + 4, lab, 11.5, col, "start", "bold")
        return out
    s += eline(0.02, GREEN, "2%")
    s += eline(0.05, "#b08900", "5%")
    s += eline(0.06, RED, "6%")
    # позначка перетину 5.3% з межею при k≈9.5
    s += circle(ox + axw * 9.5 / 10, ylim, 5, "#fff", INK, 2)
    s += text(ox + axw * 9.5 / 10, ylim + 18, "≈5.3% × 9.5 = 0.5", 10.5, INK, "middle", "bold")

    s += rect(60, 372, W - 120, 50, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 392, "Гранична сумарна розбіжність ≈ 0.5 / 9.5 ≈ 5.3% для 8N1 — і її ДІЛЯТЬ передавач із приймачем.",
              12, INK, "middle", "bold")
    s += text(W / 2, 412, "Звідси практичне правило: кожна сторона має триматися в межах ≈ ±2%.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-3-3-budget.svg", s)


# ── Рис. 35.3.4 — три випадки: 2% безпечно, 5% на межі, 6% збій ──────────────
def fig34_cases():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Куди влучає відлік стоп-біта при різній розбіжності", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "зсув на стоп-біті = 9.5 × розбіжність; влучити треба в межах ±0.5 від центру",
              12.5, GREY, "middle", style="italic")
    cases = [("2%", 0.02, GREEN, "безпечно: глибоко в біті"),
             ("5%", 0.05, "#b08900", "на межі: 0.475 від центру"),
             ("6%", 0.06, RED, "ЗБІЙ: 0.57 — у сусідній біт → помилка кадру")]
    cx0, cw, y = 250, 360, 110
    for code, e, col, verdict in cases:
        # клітина стоп-біта з центром і краями
        s += rect(cx0, y, cw, 44, LGREY, GREY, 1.4)
        center = cx0 + cw / 2
        s += line(center, y - 8, center, y + 52, GREY, 1.4, dash="3,3")
        s += text(center, y - 12, "центр", 9.5, GREY, "middle")
        s += text(cx0 + 6, y + 26, "|край", 9.5, GREY, "start")
        s += text(cx0 + cw - 6, y + 26, "край|", 9.5, GREY, "end")
        # відлік RX: зсув = 9.5*e біта, у пікселях = 9.5*e*cw
        off = 9.5 * e * cw
        sx = center + off
        inside = abs(9.5 * e) < 0.5
        s += arrow(sx, y + 74, sx, y + 46, col, 2)
        s += circle(sx, y + 74, 5, "#fff", col, 2)
        s += text(cx0 - 14, y + 26, code, 14, col, "end", "bold")
        s += text(cx0 + cw + 16, y + 22, verdict, 11.5, col, "start", "bold")
        s += text(cx0 + cw + 16, y + 40, "зсув %.2f біта" % (9.5 * e), 10.5, GREY, "start")
        y += 96

    save("fig-35-3-4-cases.svg", s)


# ── Рис. 35.3.5 — чому «дивні» кварци: похибка baud при 115200 ───────────────
def fig35_crystals():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Чому існують «дивні» кварци: похибка baud при 115200", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "ціле DIV (×16): кратні до 115200 частоти дають 0%, «круглі» МГц — велику похибку",
              12.5, GREY, "middle", style="italic")
    rows = [
        ("14.7456 МГц", "8", "115200", "0.0%", GREEN, "✓ ідеально (= 115200×128)"),
        ("11.0592 МГц", "6", "115200", "0.0%", GREEN, "✓ ідеально"),
        ("20.000 МГц", "11", "113636", "−1.4%", "#b08900", "~ припустимо"),
        ("16.000 МГц", "9", "111111", "−3.5%", "#b08900", "~ ризик на повному кадрі"),
        ("12.000 МГц", "7", "107143", "−7.0%", RED, "✗ зависоко — збої"),
    ]
    bx, by, rw = 90, 96, 720
    s += rect(bx, by, rw, 40, "#f0f0f0", GREY, 1.4, 8)
    heads = [("кварц", 20), ("DIV", 230), ("реальний baud", 330), ("похибка", 500), ("вердикт", 600)]
    for h, dx in heads:
        s += text(bx + dx, by + 25, h, 12, INK, "start", "bold")
    yy = by + 40
    for cryst, div, real, err, col, verdict in rows:
        s += rect(bx, yy, rw, 40, "#ffffff", GREY, 1)
        s += text(bx + 20, yy + 25, cryst, 12.5, INK, "start", "bold")
        s += text(bx + 230, yy + 25, div, 12, INK, "start")
        s += text(bx + 330, yy + 25, real, 12, INK, "start")
        s += text(bx + 500, yy + 25, err, 12.5, col, "start", "bold")
        s += text(bx + 600, yy + 25, verdict, 11.5, col, "start")
        yy += 40

    s += rect(60, 360, W - 120, 50, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 390, "Кварци 1.8432 / 3.6864 / 7.3728 / 11.0592 / 14.7456 МГц — кратні до бодових частот, тож дають 0%.",
              11.5, INK, "middle", "bold")
    save("fig-35-3-5-crystals.svg", s)


# ── Рис. 35.3.6 — довжина кадру й джерело такту ──────────────────────────────
def fig36_clock_source():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Що звужує допуск: довжина кадру й джерело такту", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "коротший кадр терпить більший розсинхрон; точність годинника з'їдає бюджет",
              12.5, GREY, "middle", style="italic")

    # ліва панель: формат → останній біт → допуск
    s += rect(40, 84, 410, 250, "none", FAINT, 2, 12)
    s += text(245, 110, "допуск vs довжина кадру", 13.5, INK, "middle", "bold")
    fr = [("5N1", 6.5, "7.7%"), ("8N1", 9.5, "5.3%"), ("8E1", 10.5, "4.8%"), ("8N2", 10.5, "4.8%")]
    yy = 142
    s += text(70, yy - 6, "формат", 11, GREY, "start", "bold")
    s += text(210, yy - 6, "останній відлік", 11, GREY, "start", "bold")
    s += text(360, yy - 6, "допуск", 11, GREY, "start", "bold")
    for code, last, tol in fr:
        s += text(70, yy + 20, code, 12.5, INK, "start", "bold")
        s += text(230, yy + 20, "%.1f біта" % last, 12, INK, "start")
        s += text(360, yy + 20, tol, 12.5, GREEN, "start", "bold")
        yy += 38
    s += text(245, 322, "менше біт до кінця → більший допуск", 10.5, GREY, "middle", style="italic")

    # права панель: точність джерела
    s += rect(470, 84, 410, 250, "none", FAINT, 2, 12)
    s += text(675, 110, "точність джерела такту", 13.5, INK, "middle", "bold")
    src = [("кварц (crystal)", "±0.005% (±50 ppm)", GREEN, 150),
           ("керамічний резонатор", "±0.3…0.5%", "#b08900", 210),
           ("внутрішній RC", "±1…2% (з температурою)", RED, 270)]
    for name, acc, col, y in src:
        s += circle(500, y, 7, col, col, 0)
        s += text(516, y + 5, name, 12.5, INK, "start", "bold")
        s += text(516, y + 22, acc, 11.5, col, "start")
    s += text(675, 320, "RC сам може з'їсти весь бюджет — звідси кварц для точного UART",
              10.5, GREY, "middle", style="italic")

    s += rect(60, 352, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 375, "Бюджет ≈5% ділять: похибка baud TX + похибка baud RX + дрейф годинника + зерно передискретизації.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 395, "Тому два пристрої з внутрішнім RC на 115200 часто «не бачать» одне одного, а з кварцами — легко.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-3-6-clock-source.svg", s)


# ============================================================================
#  §35.4 — Рівні сигналу: TTL vs RS-232
# ============================================================================
FRAME8 = [1, 0, 1, 1, 0, 0, 1, 0]   # приклад біт даних для хвиль


def _frame_segs(data, inv=False):
    bits = [1] + [0] + list(data) + [1]   # спокій, старт, дані, стоп
    if inv:
        bits = [1 - b for b in bits]
    # ширини: спокій 0.8, решта 1.0
    segs = [(bits[0], 0.8)]
    for b in bits[1:]:
        segs.append((b, 1.0))
    return segs


# ── Рис. 35.4.1 — TTL/логічні рівні: спокій=VCC, старт=0 ──────────────────────
def fig41_ttl():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Логічні (TTL) рівні UART: «1» = VCC, «0» = 0 В", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "так виглядає лінія прямо на ніжці мікроконтролера — спокій високий, старт тягне вниз",
              12.5, GREY, "middle", style="italic")
    x0, unit = 150, 64
    hi, lo = 130, 230
    segs = _frame_segs(FRAME8)
    body, c = _wave(x0, hi, lo, unit, segs, INK, 2.8)
    s += body
    # вісь напруги
    s += line(x0 - 40, hi, x0 - 40, lo, INK, 1.6)
    s += line(x0 - 46, hi, x0 - 34, hi, INK, 1.6)
    s += line(x0 - 46, lo, x0 - 34, lo, INK, 1.6)
    s += text(x0 - 50, hi + 4, "VCC", 12, RED, "end", "bold")
    s += text(x0 - 50, lo + 4, "0 В", 12, BLUE, "end", "bold")
    # два варіанти VCC
    s += text(x0 - 50, hi - 12, "3.3 або 5 В", 11, GREY, "end")
    s += text(c[1][0], lo + 22, "СТАРТ", 11.5, RED, "middle", "bold")
    s += text(c[0][0], hi - 10, "спокій=1", 11, GREY, "middle", style="italic")
    s += text(c[10][0], hi - 10, "стоп=1", 11, GREY, "middle", style="italic")

    s += rect(60, 300, W - 120, 96, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 326, "Це «TTL-рівні» (logic-level): однополярні, неінвертовані — як усі цифрові сигнали (Розділ 14).",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 350, "Високий = VCC (3.3 чи 5 В), низький = 0. Саме такий UART дають ніжки RX/TX мікроконтролера.",
              12, INK, "middle")
    s += text(W / 2, 374, "Запам'ятай: рівень «1» прив'язаний до напруги живлення чипа — звідси вся подальша несумісність.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-4-1-ttl.svg", s)


# ── Рис. 35.4.2 — 3.3 В проти 5 В: де небезпека ──────────────────────────────
def fig42_3v3_5v():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "3.3 В проти 5 В: пряме з'єднання буває небезпечним", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "5-вольтовий вихід у 3.3-вольтовий вхід = перенапруга на ніжці; зворотний бік — буває замало",
              12.5, GREY, "middle", style="italic")

    def dev(x, y, name, v, col):
        out = rect(x, y, 150, 90, "#fbfbfb", col, 2, 10)
        out += text(x + 75, y + 36, name, 13, INK, "middle", "bold")
        out += text(x + 75, y + 60, v, 13, col, "middle", "bold")
        return out

    # випадок 1: 5V TX -> 3.3V RX (небезпека)
    s += text(160, 96, "5 В  →  3.3 В", 14, RED, "middle", "bold")
    s += dev(40, 120, "TX 5 В", "вихід 5 В", RED)
    s += dev(250, 120, "RX 3.3 В", "макс ≈3.6 В", BLUE)
    s += arrow(190, 165, 250, 165, RED, 2.4)
    s += text(220, 152, "5 В", 11, RED, "middle", "bold")
    s += text(325, 230, "⚡ перенапруга → ушкодження входу", 11.5, RED, "middle", "bold")
    s += text(325, 248, "(потрібен зсув рівнів: дільник / буфер)", 10.5, GREY, "middle", style="italic")

    # випадок 2: 3.3V TX -> 5V RX (часто ок, але буває замало)
    s += text(620, 96, "3.3 В  →  5 В", 14, "#b08900", "middle", "bold")
    s += dev(500, 120, "TX 3.3 В", "вихід 3.3 В", BLUE)
    s += dev(710, 120, "RX 5 В", "поріг VIH", "#b08900")
    s += arrow(650, 165, 710, 165, BLUE, 2.4)
    s += text(680, 152, "3.3 В", 11, BLUE, "middle", "bold")
    s += text(785, 230, "5 В TTL (VIH≈2.0): ок", 11, GREEN, "middle", "bold")
    s += text(785, 248, "5 В CMOS (VIH≈3.5): замало!", 11, RED, "middle", "bold")

    # шкала порогів
    bx, by, bw = 120, 300, 660
    s += rect(bx, by, bw, 40, "#f6f6f6", GREY, 1.3, 8)
    s += text(bx + 10, by + 25, "пороги входу (Розділ 14): «1» якщо вище VIH, «0» якщо нижче VIL — між ними невизначеність",
              11.5, INK, "start")
    s += rect(60, 356, W - 120, 44, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 382, "Правило: 5→3.3 майже завжди потребує зсуву рівнів; 3.3→5 часто працює, але перевір VIH приймача.",
              12, INK, "middle", "bold")
    save("fig-35-4-2-3v3-5v.svg", s)


# ── Рис. 35.4.3 — RS-232: біполярно й інвертовано ────────────────────────────
def fig43_rs232():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 34, "RS-232: той самий байт, але біполярно ТА інвертовано", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у старому комп'ютерному порту «1» — це від'ємна напруга, «0» — додатна; розмах ±12 В",
              12.5, GREY, "middle", style="italic")
    x0, unit = 170, 62

    # TTL зверху
    s += text(x0 - 50, 120, "TTL", 12.5, INK, "end", "bold")
    body1, c1 = _wave(x0, 100, 150, unit, _frame_segs(FRAME8), INK, 2.6)
    s += body1
    s += text(x0 - 50, 104, "3.3 В", 10.5, RED, "end")
    s += text(x0 - 50, 154, "0 В", 10.5, BLUE, "end")
    s += text(x0 + 10 * unit + 10, 100, "спокій = 1 = ВИСОКО", 10.5, GREY, "start")

    # RS-232 знизу (інвертовано + біполярно)
    midy = 300
    hi_r, lo_r = 250, 350   # hi=+12 (low logic), lo=-12... careful: we draw bits inverted
    s += text(x0 - 50, midy, "RS-232", 12.5, INK, "end", "bold")
    # вісь: 0 посередині
    s += line(x0 - 30, 250, x0 + 10 * unit, 250, GREY, 1, dash="2,4")  # +12 рівень? намалюємо нульову лінію окремо
    body2, c2 = _wave(x0, 250, 350, unit, _frame_segs(FRAME8, inv=True), INK, 2.6)
    s += body2
    # нульова лінія
    s += line(x0 - 30, 300, x0 + 10 * unit + 30, 300, GREY, 1.4, dash="5,4")
    s += text(x0 + 10 * unit + 34, 304, "0 В", 10.5, GREY, "start")
    s += text(x0 - 50, 254, "+12 В", 10.5, "#b08900", "end")
    s += text(x0 - 50, 354, "−12 В", 10.5, "#7a2bd6", "end")
    s += text(x0 + 10 * unit + 10, 350, "спокій = 1 = НИЗЬКО (−12 В)", 10.5, GREY, "start")

    # підписи інверсії
    s += text(c1[0][0], 88, "1", 12, RED, "middle", "bold")
    s += text(c2[0][0], 366, "1", 12, "#7a2bd6", "middle", "bold")
    s += arrow(c1[0][0] + 20, 120, c2[0][0] + 20, 250, GREEN, 1.6, dash="4,4")
    s += text(c1[0][0] + 70, 200, "та сама «1» —", 11, GREEN, "start", "bold")
    s += text(c1[0][0] + 70, 216, "догори дриґом", 11, GREEN, "start")

    s += rect(60, 396, W - 120, 50, LRED, RED, 1.6, 10)
    s += text(W / 2, 422, "RS-232 несумісний із TTL ТРИЧІ: інша полярність, інвертована логіка і ±12 В замість 0…3.3 В.",
              12.5, INK, "middle", "bold")
    save("fig-35-4-3-rs232.svg", s)


# ── Рис. 35.4.4 — запас завадостійкості: чому ±12 В ──────────────────────────
def fig44_margin():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо такий розмах: запас завадостійкості RS-232", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "велика інвертована напруга купує величезний запас — сигнал переживає довгий зашумлений кабель",
              12.5, GREY, "middle", style="italic")

    # RS-232 шкала зліва
    def vscale(cx, top, bot, vmax, ticks, title):
        out = line(cx, top, cx, bot, INK, 2)
        for v, lab in ticks:
            yy = bot - (v + vmax) / (2 * vmax) * (bot - top)
            out += line(cx - 6, yy, cx + 6, yy, INK, 1.4)
            out += text(cx - 12, yy + 4, lab, 10.5, GREY, "end")
        out += text(cx, top - 12, title, 12.5, INK, "middle", "bold")
        return out, lambda v: bot - (v + vmax) / (2 * vmax) * (bot - top)

    s += text(245, 92, "RS-232 (±)", 13.5, INK, "middle", "bold")
    sc, y_r = vscale(250, 120, 360, 15, [(15, "+15"), (3, "+3"), (0, "0"), (-3, "−3"), (-15, "−15")], "")
    s += sc
    # зона невизначеності ±3
    s += rect(220, y_r(3), 60, y_r(-3) - y_r(3), "#fdeeee", RED, 1.2)
    s += text(310, (y_r(3) + y_r(-3)) / 2 + 4, "невизначена зона ±3 В", 10.5, RED, "start")
    # передавач ±5..15
    s += rect(220, y_r(15), 60, y_r(5) - y_r(15), "#eef6ef", GREEN, 1.2)
    s += rect(220, y_r(-5), 60, y_r(-15) - y_r(-5), "#eef6ef", GREEN, 1.2)
    s += text(310, y_r(10) + 4, "«0»: +5…+15", 10.5, GREEN, "start")
    s += text(310, y_r(-10) + 4, "«1»: −5…−15", 10.5, GREEN, "start")
    s += arrow(200, y_r(3), 200, y_r(8), GREEN, 2)
    s += text(150, y_r(6) + 4, "запас", 10.5, GREEN, "end", "bold")

    # TTL шкала справа
    s += text(660, 92, "TTL 3.3 В", 13.5, INK, "middle", "bold")
    def vscale01(cx, top, bot, vmax, ticks):
        out = line(cx, top, cx, bot, INK, 2)
        for v, lab in ticks:
            yy = bot - v / vmax * (bot - top)
            out += line(cx - 6, yy, cx + 6, yy, INK, 1.4)
            out += text(cx - 12, yy + 4, lab, 10.5, GREY, "end")
        return out, lambda v: bot - v / vmax * (bot - top)
    sc2, y_t = vscale01(665, 120, 360, 3.3, [(3.3, "3.3"), (2.0, "VIH 2.0"), (0.8, "VIL 0.8"), (0, "0")])
    s += sc2
    s += rect(635, y_t(2.0), 60, y_t(0.8) - y_t(2.0), "#fdeeee", RED, 1.2)
    s += text(725, (y_t(2.0) + y_t(0.8)) / 2 + 4, "зона ≈1.2 В", 10.5, RED, "start")
    s += rect(635, y_t(3.3), 60, y_t(2.0) - y_t(3.3), "#eef6ef", GREEN, 1.2)
    s += rect(635, y_t(0.8), 60, y_t(0) - y_t(0.8), "#eef6ef", GREEN, 1.2)
    s += text(725, y_t(2.7) + 4, "«1»", 10.5, GREEN, "start")
    s += text(725, y_t(0.4) + 4, "«0»", 10.5, GREEN, "start")

    s += rect(60, 378, W - 120, 50, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 404, "RS-232 терпить кілька вольтів завад на кабелі; у TTL 3.3 В запас лічені сотні мілівольтів.",
              12, INK, "middle", "bold")
    save("fig-35-4-4-margin.svg", s)


# ── Рис. 35.4.5 — конвертер рівнів (MAX232) ──────────────────────────────────
def fig45_converter():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Конвертер рівнів (типу MAX232): місток між TTL і RS-232", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "перетворює напруги В ОБИДВА боки й інвертує; накачує ±10 В з одного 5-вольтового живлення",
              12.5, GREY, "middle", style="italic")
    # MCU
    s += rect(70, 150, 150, 110, "#fbfbfb", INK, 2, 10)
    s += text(145, 188, "МК", 14, INK, "middle", "bold")
    s += text(145, 212, "TTL 3.3/5 В", 11.5, BLUE, "middle", "bold")
    s += text(145, 232, "неінвертовано", 10.5, GREY, "middle")
    # конвертер
    s += rect(360, 130, 180, 150, LGRN, GREEN, 2.2, 12)
    s += text(450, 162, "MAX232", 15, GREEN, "middle", "bold")
    s += text(450, 184, "зсув рівнів", 11.5, INK, "middle")
    s += text(450, 204, "+ інверсія", 11.5, INK, "middle")
    s += text(450, 244, "зарядні помпи", 10.5, GREY, "middle", style="italic")
    s += text(450, 260, "→ ±10 В з 5 В", 10.5, GREY, "middle", style="italic")
    # RS-232 пристрій
    s += rect(680, 150, 150, 110, "#fbfbfb", INK, 2, 10)
    s += text(755, 188, "RS-232", 14, INK, "middle", "bold")
    s += text(755, 212, "±12 В", 11.5, "#b08900", "middle", "bold")
    s += text(755, 232, "інвертовано", 10.5, GREY, "middle")
    # стрілки обидва боки
    s += arrow(222, 190, 358, 190, BLUE, 2.2)
    s += arrow(358, 222, 222, 222, BLUE, 2.2)
    s += text(290, 180, "TTL", 10.5, BLUE, "middle", "bold")
    s += arrow(542, 190, 678, 190, "#b08900", 2.2)
    s += arrow(678, 222, 542, 222, "#b08900", 2.2)
    s += text(610, 180, "RS-232", 10.5, "#b08900", "middle", "bold")

    s += rect(60, 320, W - 120, 56, LRED, RED, 1.6, 10)
    s += text(W / 2, 343, "НІКОЛИ не з'єднуй ±12 В RS-232 прямо з ніжкою МК — спалиш вхід. Завжди через конвертер.",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 363, "Старі GPS, промислові давачі, модеми часто мають саме RS-232 — їм потрібен MAX232-місток.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-4-5-converter.svg", s)


# ── Рис. 35.4.6 — USB-to-serial міст: сучасна реальність ──────────────────────
def fig46_usb():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Сучасний «послідовний порт» — це USB-міст на TTL-рівнях", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у комп'ютерів давно нема RS-232; кабель до плати йде через чип-міст CP2102 / CH340 / FT232",
              12.5, GREY, "middle", style="italic")

    def blk(x, w, t1, t2, col=INK, fill="#fbfbfb"):
        out = rect(x, 150, w, 90, fill, col, 2, 10)
        out += text(x + w / 2, 188, t1, 13.5, col, "middle", "bold")
        out += text(x + w / 2, 210, t2, 11, GREY, "middle")
        return out

    s += blk(50, 150, "ПК", "віртуальний COM")
    s += arrow(202, 195, 252, 195, INK, 2.2)
    s += text(227, 184, "USB", 10.5, INK, "middle", "bold")
    s += blk(254, 200, "міст USB↔UART", "CP2102 / CH340 / FT232", GREEN, LGRN)
    s += arrow(456, 195, 506, 195, BLUE, 2.2)
    s += text(481, 184, "TTL 3.3 В", 10, BLUE, "middle", "bold")
    s += blk(508, 170, "UART МК", "RX / TX", BLUE)
    s += arrow(680, 195, 730, 195, INK, 2.2)
    s += blk(732, 140, "прошивка", "Serial", INK)

    s += rect(60, 280, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 305, "«COM-порт» у системі — віртуальний: міст ховає USB, а до МК доходить звичайний TTL-UART 3.3 В.",
              12, INK, "middle", "bold")
    s += text(W / 2, 327, "Тому на платі поряд із роз'ємом USB майже завжди сидить такий чип-міст — це і є «програматор/Serial».",
              11.5, GREY, "middle", style="italic")
    save("fig-35-4-6-usb.svg", s)


# ── Рис. 35.4.7 — що з чим з'єднується: матриця й типові помилки ─────────────
def fig47_matrix():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Що з чим з'єднується напряму, а що — лише через перетворювач", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "перед тим як зводити TX і RX, звір рівні — інакше «нічого» або «дим»",
              12.5, GREY, "middle", style="italic")
    rows = [
        ("TTL 3.3 В ↔ TTL 3.3 В", "напряму ✓", GREEN, "TX↔RX навхрест, спільна земля"),
        ("TTL 5 В ↔ TTL 3.3 В", "зсув рівнів ⚠", "#b08900", "5→3.3 обов'язково; 3.3→5 перевір VIH"),
        ("TTL ↔ RS-232", "конвертер ⚠", RED, "MAX232; прямо — спалиш вхід ±12 В"),
        ("RS-232 ↔ RS-232", "напряму ✓", GREEN, "та сама родина рівнів"),
    ]
    bx, by, rw = 90, 92, 720
    yy = by
    for pair, verdict, col, note in rows:
        s += rect(bx, yy, rw, 50, "#ffffff", GREY, 1.3, 6)
        s += text(bx + 16, yy + 30, pair, 13.5, INK, "start", "bold")
        s += text(bx + 320, yy + 30, verdict, 13, col, "start", "bold")
        s += text(bx + 480, yy + 30, note, 11, GREY, "start")
        yy += 58

    s += rect(60, 332, W - 120, 76, LRED, RED, 1.6, 10)
    s += text(W / 2, 356, "Три класичні помилки рівнів і дротів:", 12.5, INK, "middle", "bold")
    s += text(W / 2, 378, "1) TX↔TX замість навхрест   ·   2) забута спільна земля   ·   3) переплутані рівні/інверсія",
              12, INK, "middle")
    s += text(W / 2, 398, "Будь-яка з них дає «лінія є, а зв'язку нема» — перевіряй їх першими.",
              11, GREY, "middle", style="italic")
    save("fig-35-4-7-matrix.svg", s)


# ============================================================================
#  §35.5 — Буфери (FIFO) і керування потоком (RTS/CTS)
# ============================================================================
def _queue(x, y, n, fill_count, cw=34, h=34, fill=("#dfe7fb", BLUE), labels=None):
    """Горизонтальна черга з n клітин, перші fill_count заповнені."""
    s = ""
    for i in range(n):
        f, c = (fill if i < fill_count else ("#ffffff", GREY))
        s += rect(x + i * cw, y, cw, h, f, c, 1.4)
        if labels and i < len(labels):
            s += text(x + i * cw + cw / 2, y + h - 11, labels[i], 11, (BLUE if i < fill_count else GREY), "middle", "bold")
    return s


# ── Рис. 35.5.1 — проблема: перезапис без буфера (overrun) ───────────────────
def fig51_overrun():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Проблема: байти прибувають за власним розкладом, а процесор зайнятий", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "без буфера новий байт ПЕРЕЗАПИСУЄ непрочитаний старий — байт втрачено (overrun)",
              12.5, GREY, "middle", style="italic")
    x0, unit = 130, 150
    # вісь часу
    s += arrow(x0, 250, x0 + 600, 250, INK, 1.8)
    s += text(x0 + 600, 270, "час →", 12, INK, "start")
    # прибуття байтів
    arrivals = [("B0", 0), ("B1", 1), ("B2", 2), ("B3", 3)]
    for name, k in arrivals:
        xx = x0 + 40 + k * unit
        s += rect(xx - 18, 120, 36, 30, "#dfe7fb", BLUE, 1.6, 4)
        s += text(xx, 141, name, 12, BLUE, "middle", "bold")
        s += arrow(xx, 154, xx, 246, BLUE, 1.5, dash="3,3")
        s += text(xx, 112, "прийшов", 9.5, GREY, "middle")
    # CPU зайнятий між B0 і B2
    s += rect(x0 + 40, 290, 2 * unit, 30, "#fdeeee", RED, 1.6, 5)
    s += text(x0 + 40 + unit, 310, "CPU зайнятий (довга операція)", 11.5, RED, "middle", "bold")
    s += text(x0 + 40, 340, "прочитав B0", 10.5, GREEN, "start")
    # B1 втрачено
    xb1 = x0 + 40 + 1 * unit
    s += text(xb1, 200, "✗ B1 ПЕРЕЗАПИСАНО", 12, RED, "middle", "bold")
    s += text(xb1, 216, "(B2 ліг на його місце)", 10, RED, "middle")

    s += rect(60, 364, W - 120, 44, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 390, "Приймальний регістр тримає лише ОДИН байт. Не встиг прочитати — наступний його затирає.",
              12, INK, "middle", "bold")
    save("fig-35-5-1-overrun.svg", s)


# ── Рис. 35.5.2 — апаратний FIFO поглинає сплеск ─────────────────────────────
def fig52_fifo():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Апаратний FIFO: чергa поглинає сплеск, CPU забирає пачкою", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "перший прийшов — перший вийшов; між байтами вже не треба встигати по одному",
              12.5, GREY, "middle", style="italic")
    # лінія -> FIFO -> CPU
    s += text(110, 175, "лінія", 12.5, INK, "middle", "bold")
    s += arrow(150, 190, 250, 190, BLUE, 2.4)
    s += text(200, 178, "байти", 10.5, BLUE, "middle")
    # FIFO
    n = 8
    fx, fy = 260, 172
    s += _queue(fx, fy, n, 5, cw=40, h=40, labels=["B5", "B4", "B3", "B2", "B1", "", "", ""])
    s += text(fx + n * 40 / 2, fy - 14, "RX FIFO (апаратний)", 12.5, INK, "middle", "bold")
    s += text(fx + n * 40 / 2, fy + 60, "глибина типово 16 (UART 16550) … 128 (ESP32)", 10.5, GREY, "middle", style="italic")
    s += arrow(fx + n * 40 + 8, 190, fx + n * 40 + 90, 190, GREEN, 2.4)
    s += rect(fx + n * 40 + 92, 162, 120, 56, "#fbfbfb", INK, 2, 10)
    s += text(fx + n * 40 + 152, 190, "CPU", 14, INK, "middle", "bold")
    s += text(fx + n * 40 + 152, 234, "читає кілька за раз", 10.5, GREY, "middle")

    s += rect(60, 320, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 343, "FIFO дає CPU «фору»: можна на мить відволіктися — байти зачекають у черзі, а не зникнуть.",
              12, INK, "middle", "bold")
    s += text(W / 2, 363, "Але й він скінченний: переповнився — і далі знову втрати (overrun).",
              11.5, GREY, "middle", style="italic")
    save("fig-35-5-2-fifo.svg", s)


# ── Рис. 35.5.3 — два рівні буферизації: FIFO + кільцевий буфер ───────────────
def fig53_pipeline():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 34, "Два рівні буферизації: апаратний FIFO + програмний кільцевий буфер", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "переривання перекладає байти з малого FIFO у великий буфер у RAM; застосунок читає звідти",
              12.5, GREY, "middle", style="italic")

    def blk(x, w, t1, t2, col=INK, fill="#fbfbfb"):
        out = rect(x, 150, w, 86, fill, col, 2, 10)
        out += text(x + w / 2, 186, t1, 12.5, col, "middle", "bold")
        out += text(x + w / 2, 208, t2, 10.5, GREY, "middle")
        return out

    s += blk(40, 110, "лінія", "RX")
    s += arrow(152, 193, 192, 193, BLUE, 2.2)
    s += blk(194, 150, "FIFO", "малий, у периферії", BLUE)
    s += arrow(346, 193, 396, 193, RED, 2.2)
    s += text(371, 180, "ISR", 10, RED, "middle", "bold")
    s += blk(398, 200, "кільцевий буфер", "великий, у RAM", GREEN, LGRN)
    s += arrow(600, 193, 650, 193, INK, 2.2)
    s += text(625, 180, "read()", 9.5, INK, "middle", "bold")
    s += blk(652, 150, "застосунок", "Serial.read()", INK)

    s += text(471, 256, "переривання спорожняє FIFO в буфер «на льоту», поки CPU зайнятий іншим",
              11, GREY, "middle", style="italic")
    s += rect(60, 300, W - 120, 60, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 324, "Saме з кільцевого буфера й читає Serial.read(): драйвер ховає і FIFO, і переривання.",
              12, INK, "middle", "bold")
    s += text(W / 2, 345, "Чим більший буфер, тим довшу зайнятість CPU переживе потік без втрат.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-5-3-pipeline.svg", s)


# ── Рис. 35.5.4 — механіка кільцевого буфера (head/tail) ─────────────────────
def fig54_ring():
    W, H = 880, 460
    s = header(W, H)
    s += text(W / 2, 34, "Кільцевий буфер: покажчики запису (head) і читання (tail)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "ISR пише в head і просуває його; застосунок читає з tail; між ними — непрочитані байти",
              12.5, GREY, "middle", style="italic")
    cx, cy, R = 360, 250, 130
    n = 12
    head_i, tail_i = 9, 3
    for k in range(n):
        a = -math.pi / 2 + 2 * math.pi * k / n
        x = cx + R * math.cos(a); y = cy + R * math.sin(a)
        filled = (tail_i <= k < head_i)
        s += circle(x, y, 22, ("#dfe7fb" if filled else "#ffffff"), (BLUE if filled else GREY), 1.8)
    # head / tail стрілки
    def ptr(idx, col, lab, ro):
        a = -math.pi / 2 + 2 * math.pi * idx / n
        x = cx + R * math.cos(a); y = cy + R * math.sin(a)
        xo = cx + (R + ro) * math.cos(a); yo = cy + (R + ro) * math.sin(a)
        tx = xo + 0.55 * (x - xo); ty = yo + 0.55 * (y - yo)
        out = arrow(xo, yo, tx, ty, col, 2.4)
        out += text(xo, yo + (16 if math.sin(a) > 0 else -10), lab, 12, col, "middle", "bold")
        return out
    s += ptr(head_i, RED, "head (пише ISR)", 56)
    s += ptr(tail_i, GREEN, "tail (читає застосунок)", 56)
    s += text(cx, cy - 6, "непрочитані", 12, BLUE, "middle", "bold")
    s += text(cx, cy + 12, "байти", 12, BLUE, "middle", "bold")

    # стани
    s += rect(610, 150, 250, 60, LGREY, GREY, 1.3, 8)
    s += text(620, 174, "head == tail → буфер ПОРОЖНІЙ", 11, INK, "start", "bold")
    s += text(620, 196, "head «наздогнав» tail → ПОВНИЙ", 11, RED, "start", "bold")

    s += rect(60, 388, W - 120, 50, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 414, "«Кільце» бо після останньої клітини покажчик стрибає на першу — пам'ять використовується по колу.",
              11.5, INK, "middle", "bold")
    save("fig-35-5-4-ring.svg", s)


# ── Рис. 35.5.5 — апаратне керування потоком RTS/CTS ─────────────────────────
def fig55_rtscts():
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 34, "Апаратне керування потоком: RTS/CTS кажуть «стоп, я повний»", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "дві додаткові лінії навхрест: приймач знімає RTS, передавач бачить це по CTS і паузить",
              12.5, GREY, "middle", style="italic")

    def dev(x, name):
        out = rect(x, 110, 150, 150, "#fbfbfb", INK, 2.2, 12)
        out += text(x + 75, 134, name, 13.5, INK, "middle", "bold")
        return out
    s += dev(80, "Пристрій A")
    s += dev(690, "Пристрій B")
    pins = [("TX", 152, RED), ("RX", 182, BLUE), ("RTS", 218, "#b08900"), ("CTS", 248, GREEN)]
    for nm, y, col in pins:
        s += text(222, y + 4, nm, 11, col, "start", "bold")
        s += text(688, y + 4, nm, 11, col, "end", "bold")
    # навхрест прямими лініями: TX↔RX і RTS↔CTS
    s += arrow(230, 152, 688, 182, RED, 2)          # A.TX -> B.RX
    s += arrow(688, 152, 230, 182, BLUE, 2)         # B.TX -> A.RX
    s += arrow(230, 218, 688, 248, "#b08900", 2)    # A.RTS -> B.CTS
    s += arrow(688, 218, 230, 248, GREEN, 2)        # B.RTS -> A.CTS
    s += text(459, 138, "TX ↔ RX (навхрест)", 10.5, GREY, "middle", "bold")
    s += text(459, 280, "RTS ↔ CTS (навхрест) + спільна земля", 10.5, GREY, "middle", "bold")

    # таймлайн рукостискання
    ty = 340
    s += text(80, ty, "B майже повний → знімає RTS:", 11.5, INK, "start", "bold")
    bx = 360
    s += _wave(bx, ty - 14, ty + 6, 60, [(1, 1.0), (0, 1.6), (1, 1.0)], "#b08900", 2.4)[0]
    s += text(bx + 1.8 * 60, ty - 20, "«стоп»", 10, RED, "middle", "bold")
    s += text(80, ty + 40, "A бачить CTS → паузить TX:", 11.5, INK, "start", "bold")
    s += _wave(bx, ty + 26, ty + 46, 60, [(1, 1.2), (0, 1.4), (1, 0.8)], RED, 2.4)[0]
    s += text(bx + 1.9 * 60, ty + 20, "TX мовчить", 10, GREY, "middle", "bold")

    s += rect(60, ty + 60, W - 120, 28, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, ty + 79, "RTS/CTS — швидко й двійково-безпечно (службо ниток, не байтів), ціна — 2 зайві дроти.",
              11.5, INK, "middle", "bold")
    save("fig-35-5-5-rtscts.svg", s)


# ── Рис. 35.5.6 — програмне керування потоком XON/XOFF ───────────────────────
def fig56_xonxoff():
    W, H = 900, 410
    s = header(W, H)
    s += text(W / 2, 34, "Програмне керування потоком: XON/XOFF замість зайвих дротів", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "приймач шле назад спецбайти: XOFF (0x13) — «пауза», XON (0x11) — «можна далі»",
              12.5, GREY, "middle", style="italic")
    s += rect(80, 120, 150, 100, "#fbfbfb", INK, 2, 10)
    s += text(155, 156, "передавач", 12.5, INK, "middle", "bold")
    s += text(155, 178, "(швидкий)", 10.5, GREY, "middle")
    s += rect(670, 120, 150, 100, "#fbfbfb", INK, 2, 10)
    s += text(745, 156, "приймач", 12.5, INK, "middle", "bold")
    s += text(745, 178, "(повільний)", 10.5, GREY, "middle")
    # дані вперед
    s += arrow(232, 150, 668, 150, BLUE, 2.4)
    s += text(450, 138, "потік даних →", 11, BLUE, "middle", "bold")
    # XOFF/XON назад
    s += arrow(668, 195, 232, 195, "#b08900", 2.4)
    s += text(450, 213, "← XOFF (0x13) «стоп» / XON (0x11) «далі»", 11, "#b08900", "middle", "bold")

    s += rect(120, 250, 320, 96, LGRN, GREEN, 1.4, 10)
    s += text(280, 274, "плюси", 13, GREEN, "middle", "bold")
    s += text(140, 298, "• лише TX/RX/GND — жодних зайвих дротів", 11, INK, "start")
    s += text(140, 320, "• працює крізь будь-який послідовний канал", 11, INK, "start")
    s += rect(460, 250, 320, 96, LRED, RED, 1.4, 10)
    s += text(620, 274, "мінуси", 13, RED, "middle", "bold")
    s += text(480, 298, "• 0x11 і 0x13 не можна слати як ДАНІ", 11, INK, "start")
    s += text(480, 320, "→ непридатне для двійкових даних", 11, RED, "start", "bold")

    s += rect(60, 360, W - 120, 36, LGREY, GREY, 1.3, 8)
    s += text(W / 2, 383, "XON/XOFF добре для тексту, погано для бінарних потоків; RTS/CTS — навпаки.",
              12, INK, "middle", "bold")
    save("fig-35-5-6-xonxoff.svg", s)


# ── Рис. 35.5.7 — водяний знак і порівняння способів ─────────────────────────
def fig57_watermark():
    W, H = 920, 450
    s = header(W, H)
    s += text(W / 2, 34, "«Стоп» подають ЗАЗДАЛЕГІДЬ: водяний знак і байти в дорозі", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "поки сигнал «стоп» дійде, кілька байтів уже летять — тож зупиняти треба не на 100%, а раніше",
              12.5, GREY, "middle", style="italic")
    # буфер вертикально
    bx, by, bw, bh = 130, 100, 90, 240
    s += rect(bx, by, bw, bh, "#ffffff", INK, 2)
    # заповнення до high watermark
    hw_y = by + bh * 0.25
    lw_y = by + bh * 0.65
    s += rect(bx, hw_y, bw, by + bh - hw_y, "#dfe7fb", "none", 0)
    s += line(bx - 10, hw_y, bx + bw + 10, hw_y, "#b08900", 2.2, dash="5,4")
    s += text(bx + bw + 16, hw_y + 4, "верхній поріг → шлемо «стоп»", 11, "#b08900", "start", "bold")
    s += line(bx - 10, lw_y, bx + bw + 10, lw_y, GREEN, 2.2, dash="5,4")
    s += text(bx + bw + 16, lw_y + 4, "нижній поріг → шлемо «далі»", 11, GREEN, "start", "bold")
    s += text(bx + bw / 2, by + bh + 18, "буфер приймача", 11.5, INK, "middle", "bold")
    # байти в дорозі
    s += text(bx + bw + 16, by + 18, "запас зверху — на байти,", 10.5, GREY, "start")
    s += text(bx + bw + 16, by + 34, "що вже в дорозі після «стоп»", 10.5, GREY, "start")

    # порівняння
    tx, ty = 520, 110
    rows = [
        ("без контролю", "3 дроти (TX/RX/GND)", "просто, але потрібен великий буфер", GREEN),
        ("RTS/CTS", "5 дротів", "швидко, двійково-безпечно", "#b08900"),
        ("XON/XOFF", "3 дроти", "без дротів, та не для бінарних даних", RED),
    ]
    s += rect(tx, ty, 360, 150, "#fbfbfb", GREY, 1.4, 10)
    s += text(tx + 16, ty + 26, "три способи", 12.5, INK, "start", "bold")
    yy = ty + 52
    for name, wires, note, col in rows:
        s += text(tx + 16, yy, name, 12, col, "start", "bold")
        s += text(tx + 140, yy, wires, 10.5, INK, "start")
        s += text(tx + 16, yy + 16, note, 10, GREY, "start", style="italic")
        yy += 34

    s += rect(60, 380, W - 120, 56, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 404, "Більшість простих ліній ідуть БЕЗ контролю потоку: 3 дроти + досить великий буфер + швидке читання.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 424, "Контроль потоку вмикають, коли сплески перевищують буфер або передавач значно швидший.",
              11, GREY, "middle", style="italic")
    save("fig-35-5-7-watermark.svg", s)


# ============================================================================
#  §35.6 — Проєктування пакета: заголовок, довжина, CRC
# ============================================================================
def _byte_box(x, y, w, name, val, col, fill, h=46):
    s = rect(x, y, w, h, fill, col, 1.8, 4)
    s += text(x + w / 2, y - 8, name, 11, col, "middle", "bold")
    s += text(x + w / 2, y + h / 2 + 5, val, 12.5, INK, "middle", "bold")
    return s


def _crc8(data, poly=0x07, init=0x00):
    """CRC-8 (поліном 0x07), щоб у фігурах стояли СПРАВЖНІ значення."""
    crc = init
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc


def _bits_row(x, y, bits, cell=26, color=INK, faint=False):
    s = ""
    for i, b in enumerate(bits):
        c = GREY if (faint or b == " ") else color
        if b != " ":
            s += rect(x + i * cell, y, cell, cell, ("#dfe7fb" if b == "1" else "#ffffff"),
                      (GREY if b == "0" else BLUE), 1.3)
            s += text(x + i * cell + cell / 2, y + cell - 8, b, 12.5, (BLUE if b == "1" else GREY), "middle", "bold")
    return s


# ── Рис. 35.6.1 — сирий потік не має меж повідомлень ─────────────────────────
def fig61_noboundary():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Сирий UART возить байти, а не повідомлення", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у суцільному потоці немає де початок, де кінець і чи нічого не загубилося",
              12.5, GREY, "middle", style="italic")
    data = ["12", "41", "42", "07", "FF", "41", "42", "09", "3C"]
    x0, cw = 110, 70
    for i, b in enumerate(data):
        s += rect(x0 + i * cw, 130, cw - 6, 40, "#f4f4f4", GREY, 1.4, 4)
        s += text(x0 + i * cw + (cw - 6) / 2, 156, b, 13, INK, "middle", "bold")
    s += arrow(x0, 200, x0 + len(data) * cw - 6, 200, INK, 1.6)
    s += text(x0 + len(data) * cw, 204, "час →", 12, INK, "start")
    # дві можливі групування
    s += line(x0 + 2 * cw - 6, 120, x0 + 2 * cw - 6, 250, "#b08900", 1.6, dash="4,3")
    s += text(x0 + 2 * cw + 60, 244, "тут початок? чи тут?", 11.5, "#b08900", "middle", "bold")
    s += line(x0 + 5 * cw - 6, 120, x0 + 5 * cw - 6, 250, "#b08900", 1.6, dash="4,3")

    s += rect(60, 290, W - 120, 70, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 314, "Щоб із потоку байтів зібрати повідомлення, поверх UART будують власний ПАКЕТ:",
              12.5, INK, "middle", "bold")
    s += text(W / 2, 336, "із позначкою початку, довжиною й контрольною сумою — щоб знати межі й цілість.",
              12, GREY, "middle", style="italic")
    save("fig-35-6-1-noboundary.svg", s)


# ── Рис. 35.6.2 — анатомія пакета ────────────────────────────────────────────
def fig62_anatomy():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 34, "Анатомія пакета: SYNC · LEN · ID · дані · CRC", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "проста, надійна структура: позначка старту, довжина, тип, корисні дані й контроль",
              12.5, GREY, "middle", style="italic")
    x0, y = 70, 140
    fields = [
        ("SYNC", "0xAA", 90, RED, LRED),
        ("LEN", "0x03", 90, "#b08900", "#fbf3df"),
        ("ID", "0x12", 90, BLUE, LBLUE),
        ("DATA[0]", "0x41", 100, INK, "#eef4ff"),
        ("DATA[1]", "0x42", 100, INK, "#eef4ff"),
        ("DATA[2]", "0x43", 100, INK, "#eef4ff"),
        ("CRC", "0x6C", 90, GREEN, LGRN),
    ]
    x = x0
    xs = []
    for name, val, w, col, fill in fields:
        s += _byte_box(x, y, w, name, val, col, fill)
        xs.append((x, w))
        x += w + 6
    # дужка «CRC рахується по LEN..DATA»
    lx0 = xs[1][0]
    lx1 = xs[5][0] + xs[5][1]
    s += arrow((lx0 + lx1) / 2, y + 86, lx0, y + 86, GREEN, 1.6)
    s += arrow((lx0 + lx1) / 2, y + 86, lx1, y + 86, GREEN, 1.6)
    s += text((lx0 + lx1) / 2, y + 104, "CRC рахується по цих байтах", 12, GREEN, "middle", "bold")
    # пояснення полів
    notes = [
        ("SYNC — позначка початку (одна чи дві сталі)", RED),
        ("LEN — скільки байтів даних далі (знаємо, де кінець)", "#b08900"),
        ("ID/TYPE — що це за повідомлення (необов'язково)", BLUE),
        ("CRC — контроль цілості всього пакета", GREEN),
    ]
    yy = 270
    for t, col in notes:
        s += circle(120, yy - 4, 5, col, col, 0)
        s += text(134, yy, t, 12, INK, "start")
        yy += 26
    s += rect(60, 384, W - 120, 28, LGRN, GREEN, 1.3, 8)
    s += text(W / 2, 403, "Жодного «магічного» стандарту — структуру визначаєш ти; головне, щоб обидві сторони знали її однаково.",
              11.5, INK, "middle", "bold")
    save("fig-35-6-2-anatomy.svg", s)


# ── Рис. 35.6.3 — дві стратегії меж: роздільник vs довжина ────────────────────
def fig63_framing():
    W, H = 920, 440
    s = header(W, H)
    s += text(W / 2, 34, "Дві стратегії меж: роздільник проти поля довжини", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "роздільник простий для тексту, але двійкові дані можуть його містити; довжина цього уникає",
              12.5, GREY, "middle", style="italic")
    # роздільник
    s += text(80, 110, "роздільник (напр. '\\n')", 13, INK, "start", "bold")
    seq = ["48", "49", "0A", "4F", "0A"]
    x0, cw = 90, 70
    for i, b in enumerate(seq):
        col = RED if b == "0A" else GREY
        s += rect(x0 + i * cw, 124, cw - 6, 38, ("#fdeeee" if b == "0A" else "#f4f4f4"), col, 1.4, 4)
        s += text(x0 + i * cw + (cw - 6) / 2, 148, b, 12.5, (RED if b == "0A" else INK), "middle", "bold")
    s += text(x0 + 4 * cw + 30, 148, "← '\\n' = кінець", 11, RED, "start", "bold")
    # проблема
    s += rect(540, 110, 350, 86, LRED, RED, 1.4, 10)
    s += text(715, 134, "пастка двійкових даних", 12.5, RED, "middle", "bold")
    s += text(560, 156, "якщо 0x0A трапиться в ДАНИХ —", 11, INK, "start")
    s += text(560, 174, "приймач хибно вирішить, що пакет скінчився", 11, INK, "start")
    s += text(560, 190, "→ потрібне екранування (байт-стафінг, COBS)", 10.5, GREY, "start", style="italic")

    # довжина
    s += text(80, 250, "поле довжини", 13, INK, "start", "bold")
    seq2 = [("LEN=3", "#b08900"), ("D", BLUE), ("A", BLUE), ("T", BLUE)]
    for i, (b, col) in enumerate(seq2):
        s += rect(x0 + i * cw, 264, cw - 6, 38, ("#fbf3df" if i == 0 else "#eef4ff"), col, 1.4, 4)
        s += text(x0 + i * cw + (cw - 6) / 2, 288, b, 12, INK, "middle", "bold")
    s += text(x0 + 4 * cw + 10, 288, "читаємо рівно 3 байти — байт-у-байт байдуже які", 11, GREEN, "start", "bold")
    s += rect(540, 250, 350, 66, LGRN, GREEN, 1.4, 10)
    s += text(715, 274, "довжина не боїться вмісту", 12.5, GREEN, "middle", "bold")
    s += text(560, 296, "будь-який байт у даних — просто дані", 11, INK, "start")

    s += rect(60, 350, W - 120, 60, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 374, "Для тексту зручний роздільник (рядок = повідомлення); для двійкових даних — поле довжини.",
              12, INK, "middle", "bold")
    s += text(W / 2, 395, "Можна й поєднувати: SYNC для старту + LEN для кінця — тоді вміст байтів узагалі не важливий.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-6-3-framing.svg", s)


# ── Рис. 35.6.4 — sync-байт і ресинхронізація після збою ─────────────────────
def fig64_resync():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "SYNC-байт: як знайти початок після збою чи підключення посеред потоку", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "приймач відкидає «сміття», поки не побачить позначку SYNC — і лише тоді починає збирати пакет",
              12.5, GREY, "middle", style="italic")
    stream = [("…", GREY, "сміття"), ("3F", GREY, ""), ("91", GREY, ""),
              ("AA", RED, "SYNC!"), ("03", "#b08900", "LEN"), ("12", BLUE, "ID"),
              ("41", INK, ""), ("42", INK, ""), ("43", INK, ""), ("6C", GREEN, "CRC")]
    x0, cw = 80, 82
    for i, (b, col, lab) in enumerate(stream):
        junk = i < 3
        s += rect(x0 + i * cw, 130, cw - 8, 42, ("#f0f0f0" if junk else "#eef6ff"), col, 1.6, 4)
        s += text(x0 + i * cw + (cw - 8) / 2, 156, b, 12.5, (GREY if junk else INK), "middle", "bold")
        if lab:
            s += text(x0 + i * cw + (cw - 8) / 2, 120, lab, 10.5, col, "middle", "bold")
    # дужки
    s += arrow((x0 + 3 * cw - 8) / 1, 192, x0, 192, GREY, 1.4)
    s += text(x0 + 1.2 * cw, 210, "відкинуто (шукаємо SYNC)", 11, GREY, "middle", style="italic")
    sx0 = x0 + 3 * cw
    s += arrow((sx0 + x0 + 10 * cw - 8) / 2, 192, sx0, 192, GREEN, 1.5)
    s += arrow((sx0 + x0 + 10 * cw - 8) / 2, 192, x0 + 10 * cw - 8, 192, GREEN, 1.5)
    s += text((sx0 + x0 + 10 * cw) / 2, 210, "пакет від SYNC до CRC", 11.5, GREEN, "middle", "bold")

    s += rect(60, 300, W - 120, 70, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 324, "SYNC дає змогу САМОВІДНОВИТИСЯ: після будь-якого збою приймач просто чекає наступного SYNC.",
              12, INK, "middle", "bold")
    s += text(W / 2, 345, "Тому SYNC беруть рідкісним (часто двобайтовим, як 0xAA 0x55) — щоб менше плутати з даними.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-6-4-resync.svg", s)


# ── Рис. 35.6.5 — контрольна сума проти CRC ──────────────────────────────────
def fig65_checksum_crc():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Проста сума слабка: де вона сліпа, CRC бачить", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "XOR-сума не помічає перестановки байтів та багатьох викривлень — CRC ловить майже все",
              12.5, GREY, "middle", style="italic")
    # оригінал
    orig = ["41", "42", "43"]
    swap = ["43", "42", "41"]   # переставлено перший і третій
    def show(x, y, bytes_, title):
        out = text(x + 110, y - 12, title, 12.5, INK, "middle", "bold")
        for i, b in enumerate(bytes_):
            out += rect(x + i * 70, y, 60, 38, "#eef4ff", BLUE, 1.4, 4)
            out += text(x + i * 70 + 30, y + 24, b, 12.5, INK, "middle", "bold")
        return out
    s += show(110, 120, orig, "пакет А")
    s += show(110, 240, swap, "пакет Б (1-й і 3-й переставлено)")
    ob = [0x41, 0x42, 0x43]; sb = [0x43, 0x42, 0x41]
    xo = ob[0] ^ ob[1] ^ ob[2]; xs = sb[0] ^ sb[1] ^ sb[2]
    co = _crc8(ob); cs = _crc8(sb)
    # XOR суми
    s += text(360, 144, "XOR = 0x%02X" % xo, 13, "#b08900", "start", "bold")
    s += text(360, 264, "XOR = 0x%02X  ← ТА САМА!" % xs, 13, RED, "start", "bold")
    s += text(360, 286, "сума не бачить перестановки", 11, RED, "start", style="italic")
    # CRC
    s += text(620, 144, "CRC = 0x%02X" % co, 13, GREEN, "start", "bold")
    s += text(620, 264, "CRC = 0x%02X  ← інша!" % cs, 13, GREEN, "start", "bold")
    s += text(620, 286, "CRC ловить перестановку", 11, GREEN, "start", style="italic")

    s += rect(60, 330, W - 120, 80, LGREY, GREY, 1.4, 10)
    s += text(W / 2, 354, "Проста сума (XOR чи додавання) дешева, але сліпа до перестановок і компенсованих помилок.",
              12, INK, "middle", "bold")
    s += text(W / 2, 376, "CRC залежить від ПОРЯДКУ й позиції бітів — тому ловить пакетні збої, перестановки, більшість викривлень.",
              11.5, INK, "middle")
    s += text(W / 2, 396, "І парність (§35.2), і проста сума — лише бліді тіні CRC за силою виявлення.",
              11, GREY, "middle", style="italic")
    save("fig-35-6-5-checksum-crc.svg", s)


# ── Рис. 35.6.6 — як працює CRC: ділення за модулем 2 ────────────────────────
def fig66_crc_div():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Як працює CRC: ділення за модулем 2 (XOR-віднімання)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "дані з доданими нулями ділять на генератор; остача й є CRC (тут дані 1101, генератор 1011)",
              12.5, GREY, "middle", style="italic")
    x0, y0, cell = 200, 96, 30
    s += text(x0 - 16, y0 + 20, "1101·2³", 11.5, INK, "end", "bold")
    s += _bits_row(x0, y0, list("1101000"), cell)
    # покрокове ділення за модулем 2 (XOR), 4 кроки
    seq = [
        ("дільник", "1011   ", 0),
        ("=", "0110000", None),
        ("дільник", " 1011  ", 1),
        ("=", "0011100", None),
        ("дільник", "  1011 ", 2),
        ("=", "0001010", None),
        ("дільник", "   1011", 3),
        ("=", "0000001", None),
    ]
    yy = y0 + cell + 6
    for tag, bits, al in seq:
        col = GREY if tag == "дільник" else INK
        s += text(x0 - 16, yy + 20, tag, 10.5, col, "end")
        s += _bits_row(x0, yy, list(bits), cell, color=(GREY if tag == "дільник" else INK))
        yy += cell + 4
    s += text(x0 + 4 * cell, yy + 8, "остача (3 біти) = CRC = 001", 13, GREEN, "middle", "bold")
    s += text(x0 + 3.5 * cell, yy + 30, "передаємо: 1101 001", 12.5, INK, "middle", "bold")

    s += rect(60, 408, W - 120, 50, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 432, "Приймач ділить увесь прийнятий рядок на той самий генератор: остача 0 → ціле, не 0 → є помилка.",
              11.5, INK, "middle", "bold")
    save("fig-35-6-6-crc-div.svg", s)


# ── Рис. 35.6.7 — збирання й перевірка пакета на прийомі ─────────────────────
def fig67_receive():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 34, "Прийом пакета: знайти SYNC → довжина → дані → звірити CRC", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "лише цілий пакет іде в роботу; побитий — тихо відкидають і чекають наступного SYNC",
              12.5, GREY, "middle", style="italic")
    steps = [
        ("чекай SYNC", BLUE),
        ("читай LEN", "#b08900"),
        ("збери LEN\nбайтів даних", INK),
        ("читай CRC", GREEN),
        ("CRC сходиться?", INK),
    ]
    x0, bw, gap, y = 70, 150, 30, 150
    cx = []
    for i, (lab, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        cx.append(x + bw / 2)
        s += rect(x, y, bw, 70, "#fbfbfb", col, 2, 10)
        lines = lab.split("\n")
        for j, ln in enumerate(lines):
            s += text(x + bw / 2, y + 34 + (j - (len(lines) - 1) / 2) * 16, ln, 12, col, "middle", "bold")
        if i < len(steps) - 1:
            s += arrow(x + bw, y + 35, x + bw + gap, y + 35, INK, 2)
    # розгалуження від останнього
    lastx = x0 + 4 * (bw + gap) + bw / 2
    s += arrow(lastx, y + 70, lastx - 60, y + 120, GREEN, 2)
    s += arrow(lastx, y + 70, lastx + 60, y + 120, RED, 2)
    s += rect(lastx - 180, y + 122, 120, 40, LGRN, GREEN, 1.6, 8)
    s += text(lastx - 120, y + 147, "ТАК → у роботу", 11.5, GREEN, "middle", "bold")
    s += rect(lastx + 20, y + 122, 150, 40, LRED, RED, 1.6, 8)
    s += text(lastx + 95, y + 147, "НІ → відкинути, чекати SYNC", 10.5, RED, "middle", "bold")

    s += rect(60, 320, W - 120, 60, LGRN, GREEN, 1.4, 10)
    s += text(W / 2, 344, "Ця послідовність — по суті скінченний автомат; як зробити його неблокуючим — наступна тема.",
              12, INK, "middle", "bold")
    s += text(W / 2, 365, "Головне: рішення «вірити / не вірити» приймають ЛИШЕ після перевірки CRC цілого пакета.",
              11.5, GREY, "middle", style="italic")
    save("fig-35-6-7-receive.svg", s)


# ============================================================================
#  §35.7 — Розбір потоку автоматом без блокування
# ============================================================================
def _node(x, y, w, h, title, col, fill, sub=None):
    s = rect(x, y, w, h, fill, col, 2.2, 12)
    s += text(x + w / 2, y + (h / 2 + 5 if not sub else h / 2 - 4), title, 13, col, "middle", "bold")
    if sub:
        s += text(x + w / 2, y + h / 2 + 16, sub, 10, GREY, "middle")
    return s


# ── Рис. 35.7.1 — блокуючий проти неблокуючого прийому ───────────────────────
def fig71_blocking():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 34, "Блокуючий прийом заморожує МК; неблокуючий — ні", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "не можна «стояти й чекати» кожен байт — інакше решта програми не виконується",
              12.5, GREY, "middle", style="italic")
    # блокуючий
    s += text(80, 110, "блокуючий: while(!available());", 13, RED, "start", "bold")
    s += rect(80, 124, 760, 40, "#fdeeee", RED, 1.6, 6)
    s += text(110, 149, "CPU застряг у циклі очікування — інші задачі СТОЯТЬ", 12, RED, "start", "bold")
    s += arrow(80, 184, 840, 184, INK, 1.4)
    for k in range(3):
        s += rect(120 + k * 240, 170, 30, 28, "#dfe7fb", BLUE, 1.4, 3)
        s += text(135 + k * 240, 190, "B", 10.5, BLUE, "middle", "bold")
    s += text(840, 204, "час →", 11, INK, "start")

    # неблокуючий
    s += text(80, 250, "неблокуючий: if(available()) feed(read());", 13, GREEN, "start", "bold")
    tasks = ["feed", "ПІД", "лог", "feed", "дисплей", "feed", "ПІД"]
    x = 90
    for i, t in enumerate(tasks):
        col = GREEN if t == "feed" else INK
        fill = LGRN if t == "feed" else "#f1f1f1"
        w = 90
        s += rect(x, 270, w, 34, fill, col, 1.5, 6)
        s += text(x + w / 2, 292, t, 11.5, col, "middle", "bold")
        x += w + 8
    s += arrow(80, 322, 840, 322, INK, 1.4)
    s += text(460, 342, "feed() обробляє наявні байти й ОДРАЗУ повертається — між ними працює решта",
              11.5, GREEN, "middle", "bold")

    s += rect(60, 366, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 392, "Ключ: НЕ чекати байт, а реагувати на той, що вже прийшов, і вертати керування циклу.",
              12, INK, "middle", "bold")
    save("fig-35-7-1-blocking.svg", s)


# ── Рис. 35.7.2 — скінченний автомат прийому ─────────────────────────────────
def fig72_fsm():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 34, "Скінченний автомат прийому пакета", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен байт просуває автомат на один крок; стан зберігається між викликами",
              12.5, GREY, "middle", style="italic")
    nw, nh = 170, 64
    s += _node(60, 150, nw, nh, "WAIT_SYNC", BLUE, LBLUE, "чекаємо 0xAA")
    s += _node(330, 150, nw, nh, "GET_LEN", "#b08900", "#fbf3df", "беремо довжину")
    s += _node(600, 150, nw, nh, "GET_DATA", INK, "#eef4ff", "збираємо len байтів")
    s += _node(600, 320, nw, nh, "GET_CRC", GREEN, LGRN, "звіряємо CRC")
    # переходи
    s += arrow(230, 182, 330, 182, INK, 2)
    s += text(280, 172, "b==SYNC", 10.5, BLUE, "middle", "bold")
    s += arrow(500, 182, 600, 182, INK, 2)
    s += text(550, 172, "len=b", 10.5, "#b08900", "middle", "bold")
    # self-loop GET_DATA
    s += f'<path d="M 685,150 C 685,110 745,110 745,150" fill="none" stroke="{INK}" stroke-width="2" marker-end="url(#aInk)"/>\n'
    s += text(715, 104, "buf[idx++]=b; idx<len", 10, INK, "middle", "bold")
    # GET_DATA -> GET_CRC
    s += arrow(685, 214, 685, 320, INK, 2)
    s += text(770, 270, "idx==len", 10.5, INK, "middle", "bold")
    # GET_CRC -> WAIT_SYNC
    s += f'<path d="M 600,352 C 300,420 110,330 145,216" fill="none" stroke="{GREEN}" stroke-width="2" marker-end="url(#aGreen)"/>\n'
    s += text(360, 405, "звірити CRC; як ок — видати пакет → і завжди назад", 11, GREEN, "middle", "bold")
    # guard GET_LEN -> WAIT_SYNC
    s += f'<path d="M 360,214 C 300,280 200,280 150,216" fill="none" stroke="{RED}" stroke-width="1.8" stroke-dasharray="4,3" marker-end="url(#aRed)"/>\n'
    s += text(250, 290, "len>MAX → скидання", 10, RED, "middle", "bold")
    # self WAIT_SYNC
    s += f'<path d="M 75,150 C 75,110 135,110 135,150" fill="none" stroke="{BLUE}" stroke-width="1.6" marker-end="url(#aBlue)"/>\n'
    s += text(105, 104, "інакше: ігнор", 9.5, BLUE, "middle")
    save("fig-35-7-2-fsm.svg", s)


# ── Рис. 35.7.3 — стан, що живе між викликами ────────────────────────────────
def fig73_state():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Що робить автомат неблокуючим: пам'ять між викликами", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "feed() не чекає — він зберігає, де зупинився, у кількох змінних і одразу виходить",
              12.5, GREY, "middle", style="italic")
    s += rect(280, 100, 320, 200, "#fbfbfb", INK, 2, 12)
    s += text(440, 126, "стан між викликами feed()", 13, INK, "middle", "bold")
    vars_ = [
        ("st", "поточний стан автомата", BLUE),
        ("len", "очікувана довжина даних", "#b08900"),
        ("idx", "скільки даних уже зібрано", INK),
        ("buf[ ]", "накопичувач даних", INK),
        ("crc", "CRC, що рахується на льоту", GREEN),
    ]
    yy = 156
    for name, desc, col in vars_:
        s += text(304, yy, name, 12.5, col, "start", "bold")
        s += text(384, yy, desc, 11, GREY, "start")
        yy += 28
    # вхід-вихід
    s += arrow(160, 200, 278, 200, BLUE, 2.2)
    s += text(210, 188, "1 байт", 11, BLUE, "middle", "bold")
    s += arrow(602, 200, 720, 200, GREEN, 2.2)
    s += text(700, 188, "вихід", 10.5, GREEN, "middle", "bold")
    s += text(700, 224, "одразу", 10, GREY, "middle")

    s += rect(60, 320, W - 120, 44, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 346, "Ці змінні переживають між викликами — тому автомат «пам'ятає» половину зібраного пакета.",
              12, INK, "middle", "bold")
    save("fig-35-7-3-state.svg", s)


# ── Рис. 35.7.4 — покрокова трасування пакета ────────────────────────────────
def fig74_trace():
    W, H = 920, 430
    s = header(W, H)
    s += text(W / 2, 34, "Трасування: як автомат «з'їдає» пакет байт за байтом", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "приклад пакета AA 03 41 42 43 <CRC> — по одному переходу на кожен прийнятий байт",
              12.5, GREY, "middle", style="italic")
    rows = [
        ("0xAA", "WAIT_SYNC", "SYNC знайдено", "GET_LEN", BLUE),
        ("0x03", "GET_LEN", "len=3, idx=0", "GET_DATA", "#b08900"),
        ("0x41", "GET_DATA", "buf[0], idx=1", "GET_DATA", INK),
        ("0x42", "GET_DATA", "buf[1], idx=2", "GET_DATA", INK),
        ("0x43", "GET_DATA", "buf[2], idx=3=len", "GET_CRC", INK),
        ("CRC", "GET_CRC", "звірка → видати", "WAIT_SYNC", GREEN),
    ]
    bx, by, rw = 90, 96, 740
    s += rect(bx, by, rw, 34, "#f0f0f0", GREY, 1.3, 6)
    for h, dx in [("байт", 16), ("стан до", 130), ("дія", 320), ("стан після", 560)]:
        s += text(bx + dx, by + 22, h, 11.5, INK, "start", "bold")
    yy = by + 34
    for b, s0, act, s1, col in rows:
        s += rect(bx, yy, rw, 38, "#ffffff", GREY, 1)
        s += text(bx + 16, yy + 24, b, 12.5, col, "start", "bold")
        s += text(bx + 130, yy + 24, s0, 11.5, INK, "start")
        s += text(bx + 320, yy + 24, act, 11.5, INK, "start")
        s += text(bx + 560, yy + 24, s1, 11.5, col, "start", "bold")
        yy += 38

    s += rect(60, 364, W - 120, 46, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 390, "Шість байтів — шість викликів feed(); між ними МК вільний робити що завгодно інше.",
              12, INK, "middle", "bold")
    save("fig-35-7-4-trace.svg", s)


# ── Рис. 35.7.5 — інкрементний CRC ───────────────────────────────────────────
def fig75_inc_crc():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 34, "Інкрементний CRC: рахуємо на льоту, а не в кінці", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен прийнятий байт одразу домішуємо в поточний CRC — буферувати весь пакет не треба",
              12.5, GREY, "middle", style="italic")
    steps = [
        ("len=3", "crc = init(3)", "#b08900"),
        ("0x41", "crc = upd(crc, 0x41)", INK),
        ("0x42", "crc = upd(crc, 0x42)", INK),
        ("0x43", "crc = upd(crc, 0x43)", INK),
        ("CRC-байт", "crc == прийнятий?", GREEN),
    ]
    x = 70
    for i, (b, op, col) in enumerate(steps):
        s += rect(x, 130, 150, 70, ("#eef4ff" if col == INK else "#fbfbfb"), col, 1.8, 10)
        s += text(x + 75, 156, b, 12, col, "middle", "bold")
        s += text(x + 75, 178, op, 9.8, INK, "middle")
        if i < len(steps) - 1:
            s += arrow(x + 150, 165, x + 168, 165, INK, 2)
        x += 168
    s += text(W / 2, 240, "коли приходить CRC-байт, відповідь уже готова — лишається тільки порівняти",
              12, GREEN, "middle", "bold")

    s += rect(60, 300, W - 120, 60, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 324, "Інкрементний CRC економить і пам'ять (не зберігаємо весь пакет), і час (рахуємо паралельно з прийомом).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 345, "Той самий принцип годиться й для передачі: нарощуємо CRC, доки формуємо пакет.",
              11, GREY, "middle", style="italic")
    save("fig-35-7-5-inc-crc.svg", s)


# ── Рис. 35.7.6 — надійність: межі, таймаут, ресинхрон ───────────────────────
def fig76_robust():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 34, "Три запобіжники надійного автомата", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "автомат має не лише збирати пакет, а й гідно переживати збої",
              12.5, GREY, "middle", style="italic")
    panels = [
        ("межа довжини", "len > MAX?", "→ скинути в WAIT_SYNC", "інакше зловмисний/побитий\nLEN переповнить буфер", RED),
        ("таймаут", "застрягли посеред\nпакета надовго?", "→ скинути в WAIT_SYNC", "загублений байт інакше\nзаморозив би збирання", "#b08900"),
        ("CRC не зійшовся", "звірка не пройшла?", "→ відкинути, чекати SYNC", "у роботу — лише\nцілі пакети", GREEN),
    ]
    x = 60
    for title, cond, act, why, col in panels:
        s += rect(x, 96, 270, 210, "#fbfbfb", col, 2, 12)
        s += text(x + 135, 124, title, 13.5, col, "middle", "bold")
        for j, ln in enumerate(cond.split("\n")):
            s += text(x + 135, 154 + j * 16, ln, 11.5, INK, "middle", "bold")
        s += text(x + 135, 206, act, 11, INK, "middle")
        for j, ln in enumerate(why.split("\n")):
            s += text(x + 135, 240 + j * 15, ln, 10, GREY, "middle", style="italic")
        x += 290

    s += rect(60, 326, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 351, "Без цих трьох запобіжників один загублений байт здатен «повісити» прийом назавжди.",
              12, INK, "middle", "bold")
    save("fig-35-7-6-robust.svg", s)


# ── Рис. 35.7.7 — інтеграція в головний цикл ─────────────────────────────────
def fig77_integration():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 34, "Інтеграція в головний цикл: чуйність зберігається", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "feed() стоїть поряд з іншими задачами в loop(); кожна відпрацьовує й віддає керування",
              12.5, GREY, "middle", style="italic")
    cx, cy, R = 250, 230, 110
    s += circle(cx, cy, R, "none", INK, 2)
    tasks = [("читати UART\n→ feed()", GREEN), ("ПІД-крок", INK), ("оновити\nдисплей", INK), ("телеметрія", INK)]
    for i, (t, col) in enumerate(tasks):
        a = -math.pi / 2 + 2 * math.pi * i / len(tasks)
        x = cx + R * math.cos(a); y = cy + R * math.sin(a)
        s += circle(x, y, 8, (LGRN if col == GREEN else "#eef4ff"), col, 2)
        for j, ln in enumerate(t.split("\n")):
            tx = cx + (R + 46) * math.cos(a); ty = cy + (R + 46) * math.sin(a)
            s += text(tx, ty + j * 13 - 4, ln, 10.5, col, "middle", "bold")
    # стрілки по колу
    for i in range(len(tasks)):
        a0 = -math.pi / 2 + 2 * math.pi * (i + 0.18) / len(tasks)
        a1 = -math.pi / 2 + 2 * math.pi * (i + 0.82) / len(tasks)
        x0 = cx + R * math.cos(a0); y0 = cy + R * math.sin(a0)
        x1 = cx + R * math.cos(a1); y1 = cy + R * math.sin(a1)
        s += arrow(x0, y0, x1, y1, GREY, 1.6)
    s += text(cx, cy + 4, "loop()", 14, INK, "middle", "bold")

    s += rect(500, 150, 360, 160, "#fbfbfb", GREY, 1.4, 12)
    s += text(680, 176, "чому це працює", 13, INK, "middle", "bold")
    s += text(520, 204, "• feed() обробляє наявні байти й виходить", 11, INK, "start")
    s += text(520, 228, "• нікого не змушує чекати", 11, INK, "start")
    s += text(520, 252, "• буфер UART тримає байти між обертами", 11, INK, "start")
    s += text(520, 276, "• кожна задача отримує свій час", 11, INK, "start")

    s += rect(60, 330, W - 120, 40, LGRN, GREEN, 1.3, 10)
    s += text(W / 2, 355, "Неблокуючий розбір — частина того самого super-loop / millis-підходу (Розділи 24, 27).",
              12, INK, "middle", "bold")
    save("fig-35-7-7-integration.svg", s)


if __name__ == "__main__":
    # — історія (секція 0) —
    fig_timeline()
    fig_morse_baudot()
    fig_keyboard()
    fig_tdm()
    fig_startstop()
    fig_baud()
    # — §35.1 —
    fig_parallel_serial()
    fig_skew()
    fig_sync()
    fig_async()
    fig_oversample()
    fig_wiring()
    fig_map()
    # — §35.2 —
    fig21_frame()
    fig22_lsb()
    fig23_format()
    fig24_parity()
    fig25_parity_limits()
    fig26_stop()
    fig27_overhead()
    # — §35.3 —
    fig31_baudgen()
    fig32_drift()
    fig33_budget()
    fig34_cases()
    fig35_crystals()
    fig36_clock_source()
    # — §35.4 —
    fig41_ttl()
    fig42_3v3_5v()
    fig43_rs232()
    fig44_margin()
    fig45_converter()
    fig46_usb()
    fig47_matrix()
    # — §35.5 —
    fig51_overrun()
    fig52_fifo()
    fig53_pipeline()
    fig54_ring()
    fig55_rtscts()
    fig56_xonxoff()
    fig57_watermark()
    # — §35.6 —
    fig61_noboundary()
    fig62_anatomy()
    fig63_framing()
    fig64_resync()
    fig65_checksum_crc()
    fig66_crc_div()
    fig67_receive()
    # — §35.7 —
    fig71_blocking()
    fig72_fsm()
    fig73_state()
    fig74_trace()
    fig75_inc_crc()
    fig76_robust()
    fig77_integration()
    print("done.")
