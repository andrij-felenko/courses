# -*- coding: utf-8 -*-
"""
SVG-фігури для ⚙️-вставки §3.10.6a — «Scan chain: тестер через кілька ніжок».

ОКРЕМИЙ генератор лише цієї вставки (головний figs.py розділу НЕ чіпаємо).
Чистий Python без залежностей. Вивід → ./img/.
Стиль за AUTHORING §9: білий фон; «1»/«+» червоний, «0»/«−» синій;
висновок/поле — зелене; стрілки через marker; шрифт sans-serif.
Нумерація підписів — §3.10.6a.k → файли fig-r10-s6a-k-*.

Фігури (порядок — за викладом у тексті вставки):
  fig-r10-s6a-1-mux-cell.svg   — один тригер: робочий режим vs. scan-режим (MUX перед D),
                                 і як уся низка тригерів стає одним довгим зсувним регістром
  fig-r10-s6a-2-few-pins.svg   — чому кількох ніжок досить: контрольованість + спостережуваність
                                 мільярда вузлів через 4–5 виводів TAP (простір → час)
  fig-r10-s6a-3-cycle.svg      — тестовий цикл: засунути вектор → ОДИН робочий такт (capture)
                                 → виштовхнути відповідь і порівняти; перекриття shift-in/out
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
VIOL  = "#7a3ea8"
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'  <marker id="aAmber" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{AMBER}"/></marker>\n'
        f'  <marker id="aViol" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{VIOL}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen",
         GREY: "aGrey", AMBER: "aAmber", VIOL: "aViol"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def poly(pts, color=INK, w=2, dash=None, fill="none"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{p}" fill="{fill}" stroke="{color}" stroke-width="{w}"{d}/>\n'


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def mono(x, y, s, size=13, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def ff(x, y, w=72, h=66, label="FF", clk=True, hi=False, sub=""):
    """Прямокутник тригера з трикутничком тактового входу (як у §3.3)."""
    col = VIOL if hi else INK
    s = rect(x, y, w, h, "#faf6ff" if hi else "#fcfcfc", col, 2.2 if hi else 1.8, 6)
    s += text(x + w / 2, y + h * 0.42, label, 13.5, col, "middle", "bold")
    if sub:
        s += text(x + w / 2, y + h * 0.42 + 16, sub, 10, GREY, "middle")
    # вхід D зліва, вихід Q справа
    s += text(x + 7, y + 18, "D", 11, GREY, "start")
    s += text(x + w - 7, y + 18, "Q", 11, GREY, "end")
    if clk:
        # трикутничок тактового входу в нижньому лівому куті
        s += poly([(x, y + h - 16), (x + 12, y + h - 10), (x, y + h - 4)], col, 1.6)
    return s


def mux2(x, y, w=30, h=54, sel_hi=False):
    """Трапеція-MUX 2→1: широкий бік ліворуч (два входи), вузький праворуч (вихід)."""
    col = AMBER
    pts = [(x, y), (x + w, y + h * 0.22), (x + w, y + h * 0.78), (x, y + h)]
    p = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    s = f'<polygon points="{p}" fill="#fff8ec" stroke="{col}" stroke-width="2"/>\n'
    s += text(x + w / 2 + 1, y + h / 2 + 4, "M", 11, col, "middle", "bold")
    return s


# ── Фігура 1: один тригер у двох режимах + уся низка як зсувний регістр ─────────
def fig1_mux_cell():
    W, H = 980, 690
    b = header(W, H)
    b += text(W / 2, 30,
              "Один тригер у двох режимах: робота — і scan (вся логіка стає одним зсувним регістром)",
              16, INK, "middle", "bold")
    b += text(W / 2, 50,
              "Перед кожним тригером ставлять MUX. Сигнал scan_en вибирає, ЗВІДКИ тригер бере наступний стан.",
              11.5, GREY, "middle", style="italic")

    # ── ліворуч: scan-комірка зблизька (MUX + тригер) ──
    bx, by = 40, 86
    b += rect(bx, by, 430, 250, "#fcfcfc", GREY, 1.4, 12)
    b += text(bx + 16, by + 24, "Scan-комірка (scan flip-flop)", 13, INK, "start", "bold")

    fx, fy = bx + 250, by + 120
    mx, my = bx + 150, fy + 6
    b += ff(fx, fy, 74, 66, "FF", hi=True)

    # два входи MUX
    # D0 — робочий (з логіки)
    b += text(bx + 20, my + 12, "робочий вхід", 10, BLUE, "start", "bold")
    b += text(bx + 20, my + 26, "(від логіки)", 9.5, GREY, "start")
    b += arrow(bx + 20, my + 17, mx, my + 13, BLUE, 2)
    # D1 — scan-вхід (від попередньої комірки)
    b += text(bx + 20, my + 50, "scan-вхід", 10, RED, "start", "bold")
    b += text(bx + 20, my + 64, "(Q сусіда зліва)", 9.5, GREY, "start")
    b += arrow(bx + 20, my + 55, mx, my + 41, RED, 2)

    b += mux2(mx, my, 30, 54)
    b += text(mx + 15, my + 72, "MUX", 9.5, AMBER, "middle", "bold")
    # вихід MUX → D тригера
    b += arrow(mx + 30, my + 27, fx, fy + 18, INK, 2)
    # scan_en у селектор
    b += arrow(mx + 15, my + 86, mx + 15, my + 56, AMBER, 1.8)
    b += text(mx + 15, my + 100, "scan_en", 10, AMBER, "middle", "bold")
    # вихід Q далі
    b += arrow(fx + 74, fy + 18, fx + 120, fy + 18, INK, 2)
    b += text(fx + 120, fy + 14, "Q →", 11, INK, "end")
    b += text(fx + 97, fy + 36, "у логіку", 9, BLUE, "middle")
    b += text(fx + 97, fy + 48, "і в сусіда", 9, RED, "middle")
    # такт
    b += arrow(fx + 10, fy + 92, fx + 10, fy + 58, INK, 1.6)
    b += text(fx + 10, fy + 106, "clk", 9.5, GREY, "middle")

    b += text(bx + 16, by + 250 - 12,
              "Ціна: один MUX і один дріт на кожен тригер (≈кілька % площі).",
              10.5, GREY, "start", style="italic")

    # ── праворуч: два режими як перемикач ──
    rx0 = 500
    b += rect(rx0, 86, W - rx0 - 40, 250, "#fcfcfc", GREY, 1.4, 12)
    b += text(rx0 + 16, 86 + 24, "Що вибирає scan_en", 13, INK, "start", "bold")
    # режим 0
    b += rect(rx0 + 16, 122, W - rx0 - 72, 92, "#eef3ff", BLUE, 1.6, 9)
    b += text(rx0 + 30, 144, "scan_en = 0  →  РОБОЧИЙ режим", 12.5, BLUE, "start", "bold")
    b += text(rx0 + 30, 166, "тригер бере стан від логіки схеми —", 11, INK, "start")
    b += text(rx0 + 30, 184, "чіп працює як завжди (§3.3.3, §3.5).", 11, INK, "start")
    b += text(rx0 + 30, 204, "scan-вхід ігнорується.", 10, GREY, "start", style="italic")
    # режим 1
    b += rect(rx0 + 16, 226, W - rx0 - 72, 96, "#fdecea", RED, 1.6, 9)
    b += text(rx0 + 30, 248, "scan_en = 1  →  SCAN режим", 12.5, RED, "start", "bold")
    b += text(rx0 + 30, 270, "вхід кожного тригера = вихід сусіда;", 11, INK, "start")
    b += text(rx0 + 30, 288, "усі тригери = ОДИН довгий зсувний", 11, INK, "start")
    b += text(rx0 + 30, 306, "регістр (рух бітів — як у §3.3.4).", 11, INK, "start")

    # ── низ: уся низка тригерів зшита в ланцюг ──
    cy = 400
    b += text(W / 2, cy - 24,
              "Scan-режим: розкидані по чіпу тригери з'єднані в одну стрічку від ніжки scan-in до ніжки scan-out",
              13, INK, "middle", "bold")
    n = 6
    fw = 70
    gap = (W - 160 - n * fw) / (n - 1)
    x0 = 100
    # scan-in
    b += text(x0 - 70, cy + 30, "scan-in", 12, RED, "start", "bold")
    b += arrow(x0 - 70, cy + 38, x0, cy + 28, RED, 2.2)
    prev_qx = None
    for i in range(n):
        x = x0 + i * (fw + gap)
        faint = i in (3, 4)  # натяк «...і ще мільйони...»
        if i == 3:
            b += text(x + fw / 2 + gap / 2, cy + 32, ". . .", 22, GREY, "middle", "bold")
            b += text(x + fw / 2 + gap / 2, cy + 52, "ще мільйони", 9.5, GREY, "middle")
            continue
        if i == 4:
            continue
        b += ff(x, cy, fw, 60, f"FF{i if i < 3 else 'N'}", hi=True)
        # дріт від попереднього Q до цього scan-входу
        if prev_qx is not None:
            b += arrow(prev_qx, cy + 18, x, cy + 18, RED, 2)
        prev_qx = x + fw
    # scan-out
    b += arrow(prev_qx, cy + 18, prev_qx + 60, cy + 28, RED, 2.2)
    b += text(prev_qx + 64, cy + 30, "scan-out", 12, RED, "start", "bold")
    # спільний scan_en та clk знизу
    b += line(x0, cy + 88, prev_qx, cy + 88, AMBER, 1.6, "5 4")
    b += text(x0, cy + 104, "scan_en (спільний на всі)", 10, AMBER, "start", "bold")
    b += line(x0, cy + 118, prev_qx, cy + 118, GREY, 1.4, "3 3")
    b += text(x0, cy + 134, "clk (спільний)", 10, GREY, "start")

    # висновок
    yb = 580
    b += rect(60, yb, W - 120, 70, "#f0fff2", GREEN, 1.8, 10)
    b += text(80, yb + 26, "Суть прийому:", 12.5, GREEN, "start", "bold")
    b += text(80, yb + 48,
              "тригери — це і так пам'ять стану (§3.3). Додавши перед кожним MUX, ми дістаємо ДРУГИЙ режим: "
              "перемкнути scan_en = 1 — і весь стан чіпа можна вписати ззовні та зчитати назад через дві ніжки.",
              11, INK, "start")
    save("fig-r10-s6a-1-mux-cell.svg", b)


# ── Фігура 2: тестовий цикл shift-in → capture → shift-out ─────────────────────
def fig2_cycle():
    W, H = 980, 680
    b = header(W, H)
    b += text(W / 2, 30,
              "Один тест: засунути вектор — ОДИН робочий такт — виштовхнути й порівняти відповідь",
              16, INK, "middle", "bold")
    b += text(W / 2, 50,
              "Між двома стінками тригерів сидить комбінаційна логіка. Scan керує її входами й бачить її виходи.",
              11.5, GREY, "middle", style="italic")

    # ── схема: вхідні scan-FF → хмара логіки → вихідні scan-FF ──
    sy = 86
    b += rect(60, sy, W - 120, 150, "#fcfcfc", GREY, 1.3, 12)
    # вхідні тригери
    inx = 110
    yA = sy + 28
    for i in range(3):
        b += ff(inx, yA + i * 36, 56, 30, "", clk=False, hi=True)
    b += text(inx + 28, yA - 8, "вхідні scan-тригери", 10, VIOL, "middle", "bold")
    b += text(inx + 28, yA + 3 * 36 + 12, "(подають вектор у логіку)", 9, GREY, "middle")
    # хмара логіки
    cloudx = 360
    b += rect(cloudx, sy + 30, 250, 96, "#eef3ff", BLUE, 1.8, 40)
    b += text(cloudx + 125, sy + 72, "комбінаційна логіка", 13, BLUE, "middle", "bold")
    b += text(cloudx + 125, sy + 92, "(вентилі §3.2 — те, що тестуємо)", 10, GREY, "middle")
    # стрілки вхід→хмара
    for i in range(3):
        b += arrow(inx + 56, yA + i * 36 + 15, cloudx, sy + 50 + i * 22, BLUE, 1.6)
    # вихідні тригери
    outx = 720
    for i in range(3):
        b += ff(outx, yA + i * 36, 56, 30, "", clk=False, hi=True)
    b += text(outx + 28, yA - 8, "вихідні scan-тригери", 10, VIOL, "middle", "bold")
    b += text(outx + 28, yA + 3 * 36 + 12, "(ловлять результат)", 9, GREY, "middle")
    for i in range(3):
        b += arrow(cloudx + 250, sy + 50 + i * 22, outx, yA + i * 36 + 15, BLUE, 1.6)

    # ── три фази як стрічка часу ──
    ty = 290
    b += text(W / 2, ty - 8, "Порядок дій тестера", 13, INK, "middle", "bold")
    phases = [
        ("1. SHIFT-IN", RED,
         ["scan_en = 1", "багато тактів: вектор", "вштовхується біт за бітом"],
         "довго: ~стільки тактів,\nскільки тригерів у ланцюзі"),
        ("2. CAPTURE", GREEN,
         ["scan_en = 0", "РІВНО один робочий такт", "виходи логіки сідають у тригери"],
         "коротко: один такт —\nреакція логіки зафіксована"),
        ("3. SHIFT-OUT", BLUE,
         ["scan_en = 1", "багато тактів: відповідь", "виштовхується назовні"],
         "довго; одночасно засуваємо\nвже наступний вектор"),
    ]
    pw = (W - 120 - 2 * 20) / 3
    ph = 150
    cx = 60
    for i, (nm, col, lines, note) in enumerate(phases):
        x = cx + i * (pw + 20)
        b += rect(x, ty, pw, ph, "#fcfcfc", col, 2, 10)
        b += rect(x, ty, pw, 28, col, col, 0, 10)
        b += text(x + 14, ty + 20, nm, 13, "#fff", "start", "bold")
        for k, ln in enumerate(lines):
            b += mono(x + 14, ty + 52 + k * 22, ln, 11.5, INK)
        for k, ln in enumerate(note.split("\n")):
            b += text(x + 14, ty + ph - 30 + k * 14, ln, 9.5, col, "start", style="italic")
        if i < 2:
            b += arrow(x + pw + 2, ty + ph / 2, x + pw + 18, ty + ph / 2, INK, 2.2)

    # ── перекриття shift-out / shift-in (конвеєр) ──
    oy = 480
    b += text(W / 2, oy - 6,
              "Чому тести не повзуть: вихід одного вектора й вхід наступного зсуваються ОДНИМ рухом",
              12.5, INK, "middle", "bold")
    barx, barw = 120, W - 240
    # шкала
    b += line(barx, oy + 16, barx + barw, oy + 16, GREY, 1.2)
    segs = [("вектор A: shift-in", RED, 0.0, 0.34),
            ("cap", GREEN, 0.34, 0.40),
            ("A:out ∥ B:in", VIOL, 0.40, 0.74),
            ("cap", GREEN, 0.74, 0.80),
            ("B:out ∥ C:in", VIOL, 0.80, 1.0)]
    for nm, col, a, c in segs:
        xa = barx + a * barw
        xc = barx + c * barw
        b += rect(xa, oy + 22, xc - xa - 2, 30, "#fff", col, 1.8, 5)
        b += text((xa + xc) / 2, oy + 41, nm, 9.5, col, "middle", "bold")
    b += text(barx, oy + 70, "Час →", 10, GREY, "start")
    b += text(barx + barw, oy + 70,
              "довгі фази зсуву перекриваються — тестер працює майже без простою.",
              10, GREY, "end", style="italic")

    # висновок
    yb = 590
    b += rect(60, yb, W - 120, 64, "#f0fff2", GREEN, 1.8, 10)
    b += text(80, yb + 24, "Перевірка одним порівнянням:", 12.5, GREEN, "start", "bold")
    b += text(80, yb + 46,
              "тестер заздалегідь знає, який біт-рядок мусить вийти на справному чіпі. Зчитав інше — кристал бракований. "
              "Жодного «ручного» доступу до внутрішніх вузлів не треба.",
              11, INK, "start")
    save("fig-r10-s6a-3-cycle.svg", b)


# ── Фігура 2: чому кількох ніжок досить ────────────────────────────────────────
def fig3_few_pins():
    W, H = 980, 660
    b = header(W, H)
    b += text(W / 2, 30,
              "Чому кількох ніжок досить на мільярд транзисторів",
              16, INK, "middle", "bold")
    b += text(W / 2, 50,
              "Дві проблеми тестування — дістатися до вузла й побачити вузол — scan вирішує зсувом по ланцюгу.",
              11.5, GREY, "middle", style="italic")

    # ── ліва колонка: дві властивості ──
    bx = 50
    b += rect(bx, 80, 430, 150, "#eef3ff", BLUE, 1.6, 10)
    b += text(bx + 16, 104, "Контрольованість (controllability)", 13, BLUE, "start", "bold")
    b += text(bx + 16, 126, "щоб перевірити вузол усередині, треба вміти", 11, INK, "start")
    b += text(bx + 16, 144, "ЗАДАТИ йому потрібне 0/1. Без scan глибокий", 11, INK, "start")
    b += text(bx + 16, 162, "вузол керується лише довгою послідовністю", 11, INK, "start")
    b += text(bx + 16, 180, "входів — комбінаторний жах.", 11, INK, "start")
    b += text(bx + 16, 204, "Scan: засовуємо потрібний стан прямо в тригери.", 11, BLUE, "start", "bold")

    b += rect(bx, 244, 430, 150, "#fdecea", RED, 1.6, 10)
    b += text(bx + 16, 268, "Спостережуваність (observability)", 13, RED, "start", "bold")
    b += text(bx + 16, 290, "і треба ще ПОБАЧИТИ, що вузол видав. Без scan", 11, INK, "start")
    b += text(bx + 16, 308, "внутрішній результат тоне в наступній логіці й", 11, INK, "start")
    b += text(bx + 16, 326, "ніколи не доходить до жодної ніжки.", 11, INK, "start")
    b += text(bx + 16, 350, "Scan: тригер ловить результат, далі його", 11, RED, "start", "bold")
    b += text(bx + 16, 368, "виштовхуємо назовні й читаємо.", 11, RED, "start", "bold")

    # ── права колонка: TAP — кілька ніжок ──
    px = 520
    chip = rect(px, 90, W - px - 50, 300, "#fafafa", INK, 2, 14)
    b += chip
    b += text(px + (W - px - 50) / 2, 116, "Кристал: мільярди вузлів усередині", 12.5, INK, "middle", "bold")
    # дрібна сітка «логіки» всередині
    import random
    random.seed(7)
    gx0, gy0 = px + 30, 134
    for r in range(5):
        for c in range(12):
            x = gx0 + c * 28
            y = gy0 + r * 24
            v = random.random()
            col = RED if v > 0.66 else (BLUE if v > 0.33 else FAINT)
            b += rect(x, y, 16, 14, "#fff", col, 1.2, 3)
    b += text(px + (W - px - 50) / 2, gy0 + 5 * 24 + 18,
              "ланцюг проходить крізь усі тригери (точки доступу)", 10, GREY, "middle", style="italic")

    # ніжки TAP
    py = 332
    pins = [("TCK", GREY, "такт тесту"),
            ("TMS", AMBER, "режим"),
            ("TDI", RED, "вхід даних"),
            ("TDO", BLUE, "вихід даних")]
    pwd = (W - px - 70) / 4
    for i, (nm, col, ru) in enumerate(pins):
        x = px + 20 + i * pwd
        b += rect(x, py, pwd - 14, 40, "#fff", col, 2, 6)
        b += mono(x + (pwd - 14) / 2, py + 18, nm, 12.5, col, "middle", "bold")
        b += text(x + (pwd - 14) / 2, py + 33, ru, 9, GREY, "middle")
    b += text(px + (W - px - 50) / 2, py + 56,
              "4 ніжки (+опц. TRST) = стандартний порт JTAG / IEEE 1149.1", 10.5, INK, "middle", "bold")

    # стрілка-міст «багато ↔ мало»
    b += text((480 + 520) / 2, 230, "≡", 26, GREEN, "middle", "bold")

    # нижній банер-висновок із числом
    yb = 420
    b += rect(50, yb, W - 100, 170, "#f0fff2", GREEN, 1.8, 12)
    b += text(72, yb + 28, "Розмін, що робить тестування можливим:", 13, GREEN, "start", "bold")
    rows = [
        "• Прямих ніжок-«щупів» на кожен вузол не вистачить ніколи: вузлів мільярди, ніжок — сотні.",
        "• Scan перетворює ПРОСТІР (мільярди вузлів) на ЧАС (стільки тактів зсуву, скільки тригерів).",
        "• Платимо тактами на засування/виштовхування — а доступ дістаємо через ті самі 4 виводи.",
        "• Той самий порт потім служить і для внутрішньосхемної налагодки (debug), не лише для заводського тесту.",
    ]
    for i, r in enumerate(rows):
        b += text(72, yb + 56 + i * 26, r, 11.5, INK, "start")
    b += text(W - 72, yb + 162,
              "простір → час: ось чому «кількох ніжок досить»", 10.5, GREEN, "end", style="italic")
    save("fig-r10-s6a-2-few-pins.svg", b)


if __name__ == "__main__":
    fig1_mux_cell()
    fig3_few_pins()   # → fig ...-2-few-pins (друга за викладом)
    fig2_cycle()      # → fig ...-3-cycle    (третя за викладом)
    print("r10-s6-a-scan-chain figures done.")
