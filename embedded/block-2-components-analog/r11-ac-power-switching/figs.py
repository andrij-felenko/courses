# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 2.11 — «Силова комутація змінного струму» (Модуль 2).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене; стрілки через
marker; шрифт sans-serif. Підписи за темою (Рис. M.R.T.k). Допоміжні функції
скопійовано з попередніх розділів модуля для єдиного вигляду.
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
COPP  = "#b5732e"
SUN   = "#e0a32e"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
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
    return circle(cx, cy, r, "none", color, w) + line(cx - r * 0.55, cy, cx + r * 0.55, cy, color, w)


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _poly(pts, col, wv=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{wv}"{d}/>\n'


def _fill_poly(pts, fill, stroke="none", wv=0):
    sw = f' stroke="{stroke}" stroke-width="{wv}"' if stroke != "none" else ' stroke="none"'
    return f'<path d="M {" L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)} Z" fill="{fill}"{sw}/>\n'


def _frame(x, y, w, h, title=""):
    s = rect(x, y, w, h, "#ffffff", "#c9d3dc", 1.4, 6)
    if title:
        s += text(x + w / 2, y - 6, title, 12, INK, "middle", "bold")
    return s


def _axes(ox, oy, w, h, xlab, ylab, up_down=False):
    """Осі. up_down=True — вертикальна вісь у обидва боки від oy (для синусоїди ±)."""
    if up_down:
        s = arrow(ox, oy + h / 2 + 8, ox, oy - h / 2 - 14, INK, 1.8)
    else:
        s = arrow(ox, oy, ox, oy - h - 14, INK, 1.8)
    s += arrow(ox, oy, ox + w + 14, oy, INK, 1.8)
    s += text(ox + w + 18, oy + 4, xlab, 12.5, INK, "start", "bold")
    s += text(ox - 6, oy - (h / 2 if up_down else h) - 20, ylab, 12.5, INK, "middle", "bold")
    return s


def _sine_pts(ox, oy, w, amp, cycles, phase=0.0, rect_=False):
    pts = []
    n = int(w)
    for j in range(0, n + 1):
        t = j / w
        v = math.sin(2 * math.pi * cycles * t + phase)
        if rect_:
            v = abs(v)
        pts.append((ox + j, oy - amp * v))
    return pts


# ── символ тиристора (SCR) ───────────────────────────────────────────────────
def _scr_sym(cx, cy, col=INK):
    """Анод зверху, катод знизу, затвор зліва внизу. cx,cy — центр трикутника."""
    t = line(cx, cy - 40, cx, cy - 14, col, 2.2)                 # анод-лід
    t += _fill_poly([(cx - 13, cy - 14), (cx + 13, cy - 14), (cx, cy + 8)], "#dfe7f0", col, 1.8)  # трикутник
    t += line(cx - 15, cy + 8, cx + 15, cy + 8, col, 2.6)        # катодна планка
    t += line(cx, cy + 8, cx, cy + 40, col, 2.2)                 # катод-лід
    t += line(cx - 15, cy + 6, cx - 36, cy + 22, col, 2)         # затвор
    t += text(cx, cy - 44, "A", 11, col, "middle", "bold")
    t += text(cx, cy + 54, "K", 11, col, "middle", "bold")
    t += text(cx - 40, cy + 26, "G", 11, GREEN, "end", "bold")
    return t


# ── символ симістора (TRIAC) ─────────────────────────────────────────────────
def _triac_sym(cx, cy, col=INK):
    """Два зустрічні трикутники, затвор зліва. Виводи MT2 зверху, MT1 знизу."""
    t = line(cx, cy - 42, cx, cy - 22, col, 2.2)
    t += _fill_poly([(cx - 14, cy - 22), (cx + 14, cy - 22), (cx, cy - 2)], "#dfe7f0", col, 1.8)
    t += _fill_poly([(cx - 14, cy + 22), (cx + 14, cy + 22), (cx, cy + 2)], "#dfe7f0", col, 1.8)
    t += line(cx, cy + 22, cx, cy + 42, col, 2.2)
    t += line(cx + 14, cy - 22, cx + 14, cy - 2, col, 2.6)
    t += line(cx - 14, cy + 22, cx - 14, cy + 2, col, 2.6)
    t += line(cx - 14, cy + 16, cx - 38, cy + 30, col, 2)        # затвор
    t += text(cx, cy - 46, "MT2", 10.5, col, "middle", "bold")
    t += text(cx, cy + 56, "MT1", 10.5, col, "middle", "bold")
    t += text(cx - 42, cy + 34, "G", 11, GREEN, "end", "bold")
    return t


def _diode_v(cx, cy, col=INK, up=True):
    """Вертикальний діод. up=True — провідність угору (анод знизу)."""
    if up:
        t = _fill_poly([(cx - 11, cy + 11), (cx + 11, cy + 11), (cx, cy - 9)], "#dfe7f0", col, 1.6)
        t += line(cx - 11, cy - 9, cx + 11, cy - 9, col, 2.4)
    else:
        t = _fill_poly([(cx - 11, cy - 11), (cx + 11, cy - 11), (cx, cy + 9)], "#dfe7f0", col, 1.6)
        t += line(cx - 11, cy + 9, cx + 11, cy + 9, col, 2.4)
    return t


def _res_h(cx, cy, w=46, h=14, col=INK, lab=""):
    t = rect(cx - w / 2, cy - h / 2, w, h, "#ffffff", col, 1.8)
    if lab:
        t += text(cx, cy - h / 2 - 5, lab, 10, col, "middle", "bold")
    return t


def _res_v(cx, cy, h=46, w=14, col=INK, lab=""):
    t = rect(cx - w / 2, cy - h / 2, w, h, "#ffffff", col, 1.8)
    if lab:
        t += text(cx + w / 2 + 6, cy + 4, lab, 10, col, "start", "bold")
    return t


def _cap_v(cx, cy, gap=7, plate=14, col=INK, lab=""):
    t = (line(cx - plate, cy - gap, cx + plate, cy - gap, col, 2.4)
         + line(cx - plate, cy + gap, cx + plate, cy + gap, col, 2.4))
    if lab:
        t += text(cx + plate + 6, cy + 4, lab, 10, col, "start", "bold")
    return t


def _ac_source(cx, cy, r=22, col=INK):
    t = circle(cx, cy, r, "#ffffff", col, 2)
    pts = []
    for j in range(0, 31):
        x = cx - r * 0.62 + j / 30 * (r * 1.24)
        y = cy - r * 0.5 * math.sin(2 * math.pi * (j / 30))
        pts.append((x, y))
    t += _poly(pts, col, 2)
    return t


def _bulb(cx, cy, r=18, col=INK, glow=True):
    fill = "#fff6cf" if glow else "#eef2f6"
    t = circle(cx, cy, r, fill, col, 2)
    t += line(cx - r * 0.5, cy + r * 0.5, cx + r * 0.5, cy - r * 0.5, col, 1.6)
    t += line(cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5, col, 1.6)
    return t


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 2.11.0.k — історія (до розділу): від тиратрона до тиристора
# ─────────────────────────────────────────────────────────────────────────────
def fig_t0_timeline():
    W, H = 940, 250
    s = header(W, H)
    s += text(W / 2, 30, "Від газового тиратрона до кремнієвого тиристора", 17, INK, "middle", "bold")
    boxes = [
        (20, "1920-ті · тиратрон", ["ртутна/газова лампа —", "вмикається сіткою"], "#fdf1dc"),
        (250, "1956 · Bell Labs", ["Молл, Шоклі та ін.:", "теорія PNPN-структури"], "#fdf1dc"),
        (480, "1957 · General Electric", ["перший комерційний", "кремнієвий SCR"], LGRN),
        (710, "1960-ті →", ["силова електроніка:", "приводи, світло, тепло"], LGRN),
    ]
    bw, by, bh = 210, 80, 104
    for bx, lab, lines, fill in boxes:
        s += text(bx + bw / 2, by - 8, lab, 11, INK, "middle", "bold")
        border = "#9bb0c2" if fill == LGRN else "#d8b46a"
        s += rect(bx, by, bw, bh, fill, border, 1.6, 8)
        for k, ln in enumerate(lines):
            s += text(bx + bw / 2, by + 42 + k * 22, ln, 11, INK, "middle")
    for x0 in (232, 462, 692):
        s += arrow(x0, by + bh / 2, x0 + 16, by + bh / 2, GREY, 2)
    s += text(W / 2, H - 14,
              "Газова лампа вміла те саме — вмикати велику потужність слабким сигналом, — але тиристор зробив це твердотільним і надійним.",
              11, GREY, "middle", style="italic")
    save("fig-11-0-1-timeline.svg", s)


def fig_t0_thyratron_vs_scr():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 28, "Та сама ідея «защіпки», два втілення", 16, INK, "middle", "bold")

    def panel(ox, title, gas):
        t = _frame(ox, 52, 320, 240, title)
        cx = ox + 160
        if gas:
            t += _fill_poly([(cx - 38, 100), (cx + 38, 100), (cx + 30, 210), (cx - 30, 210)],
                            "#f3eede", "#9a7b2e", 1.8)
            for (gx, gy) in [(cx - 18, 150), (cx + 16, 140), (cx - 4, 175), (cx + 22, 185), (cx - 24, 195)]:
                t += circle(gx, gy, 4, "#f6d68a", SUN, 1.2)
            t += text(cx, 158, "газ / пара", 10, "#9a7b2e", "middle", "bold")
            t += line(cx, 80, cx, 100, INK, 2.2) + text(cx, 74, "анод", 9, INK, "middle")
            t += line(cx, 210, cx, 232, INK, 2.2) + text(cx, 246, "катод (нитка)", 9, INK, "middle")
            t += line(cx - 38, 130, cx - 70, 130, GREEN, 2) + text(cx - 74, 134, "сітка", 9.5, GREEN, "end", "bold")
            t += text(cx, 272, "скляна лампа, розжарення, прогрів", 9, GREY, "middle", style="italic")
        else:
            t += _scr_sym(cx, 150, INK)
            t += text(cx, 272, "кремнієвий кристал, холодний, миттєвий", 9, GREY, "middle", style="italic")
        return t

    s += panel(30, "тиратрон (1920-ті)", True)
    s += panel(410, "тиристор / SCR (1957)", False)
    s += text(W / 2, H - 8,
              "Обидва: слабкий сигнал на керівний електрод запускає велику дугу/струм, і той тримається сам. Кремній прибрав скло, прогрів і крихкість.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-0-2-thyratron-vs-scr.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.1 — чому ключі з §2.6/§2.7 не пасують мережі
# ─────────────────────────────────────────────────────────────────────────────
def fig111_bipolar_sine():
    W, H = 760, 330
    s = header(W, H)
    s += text(W / 2, 28, "Мережа — двополярна синусоїда; ключ на 3.3 В живе в маленькому віконці", 13.5, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 175, 560, 230
    s += _axes(ox, oy, ww, hh, "t", "U", up_down=True)
    # синусоїда 230 В RMS → ±325 В пік
    amp = 95
    pts = _sine_pts(ox, oy, ww, amp, 2.0)
    s += _poly(pts, RED, 2.6)
    # рівні
    s += line(ox, oy - amp, ox + ww, oy - amp, GREY, 1.2, "5 4")
    s += text(ox - 8, oy - amp + 4, "+325 В", 10.5, RED, "end", "bold")
    s += line(ox, oy + amp, ox + ww, oy + amp, GREY, 1.2, "5 4")
    s += text(ox - 8, oy + amp + 4, "−325 В", 10.5, BLUE, "end", "bold")
    s += line(ox, oy, ox + ww, oy, INK, 1, "2 3")
    # вікно живлення логіки 0..3.3 В — тоненька смужка біля нуля
    s += rect(ox, oy - 4, ww, 4, "#cdeccd", GREEN, 0)
    s += text(ox + ww + 16, oy - 2, "0…3.3 В", 10, GREEN, "start", "bold")
    s += arrow(ox + 470, oy - 70, ox + ww - 2, oy - 2.5, GREEN, 1.6)
    s += text(ox + 360, oy - 80, "увесь діапазон логіки", 10, GREEN, "middle", "bold")
    # півперіоди
    s += text(ox + 70, oy - amp - 16, "додатна півхвиля", 10, RED, "middle")
    s += text(ox + 210, oy + amp + 22, "від'ємна півхвиля", 10, BLUE, "middle")
    s += text(W / 2, H - 10,
              "Напруга 230 В (RMS) — це розмах майже 650 В і дві полярності. Кремнієвий перехід тримає десятки вольт однієї полярності; різниця — у сотні разів.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-1-1-bipolar-sine.svg", s)


def fig111_three_problems():
    W, H = 880, 290
    s = header(W, H)
    s += text(W / 2, 30, "Три причини, чому транзистор із §2.6/§2.7 не стане в розетку", 15, INK, "middle", "bold")
    cards = [
        ("полярність", ["синусоїда йде", "в обидва боки;", "перехід проводить", "лише в один"], RED),
        ("напруга", ["пік ±325 В;", "Vds(max) ключа —", "десятки вольт →", "миттєвий пробій"], SUN),
        ("ізоляція", ["логіка й мережа", "мусять бути", "гальванічно", "розділені"], BLUE),
    ]
    cw, gap = 260, 30
    for i, (head, lines, col) in enumerate(cards):
        x = 30 + i * (cw + gap)
        s += rect(x, 60, cw, 168, "#ffffff", col, 1.8, 10)
        s += rect(x, 60, cw, 34, "#f4f6f8", col, 1.8, 10)
        s += text(x + cw / 2, 83, head, 14, col, "middle", "bold")
        for k, ln in enumerate(lines):
            s += text(x + cw / 2, 120 + k * 24, ln, 11.5, INK, "middle")
    s += text(W / 2, H - 12,
              "Потрібен інший клас приладів: двополярні, на сотні вольт, із розв'язкою керування. Це й є силова комутація змінного струму.",
              10, GREY, "middle", style="italic")
    save("fig-11-1-2-three-problems.svg", s)


def fig111_isolation_barrier():
    W, H = 800, 300
    s = header(W, H)
    s += text(W / 2, 28, "Два світи з різним «нулем»: бар'єр ізоляції між ними", 15, INK, "middle", "bold")
    # ліва сторона — логіка
    s += rect(40, 70, 300, 170, LBLUE, "#9bb0c2", 1.6, 10)
    s += text(190, 96, "сторона логіки", 12.5, BLUE, "middle", "bold")
    s += text(190, 120, "МК, 3.3 В, USB у руках", 10.5, INK, "middle")
    s += rect(90, 140, 200, 36, "#ffffff", INK, 1.4, 6) + text(190, 163, "GND логіки", 11, INK, "middle", "bold")
    s += text(190, 205, "тут безпечно торкатись", 10, GREEN, "middle", "bold")
    # права сторона — мережа
    s += rect(460, 70, 300, 170, LRED, "#d8a0a0", 1.6, 10)
    s += text(610, 96, "сторона мережі", 12.5, RED, "middle", "bold")
    s += text(610, 120, "230 В, фаза й нейтраль", 10.5, INK, "middle")
    s += rect(510, 140, 200, 36, "#ffffff", INK, 1.4, 6) + text(610, 163, "«нуль» мережі ≠ GND", 10.5, INK, "middle", "bold")
    s += text(610, 205, "торкатись — небезпечно", 10, RED, "middle", "bold")
    # бар'єр
    s += line(400, 60, 400, 250, INK, 2, "6 5")
    s += rect(372, 130, 56, 50, "#fff3b0", SUN, 1.6, 6)
    s += text(400, 150, "бар'єр", 9.5, INK, "middle", "bold")
    s += text(400, 166, "ізоляції", 9.5, INK, "middle", "bold")
    s += arrow(300, 115, 372, 145, GREEN, 1.6, "4 3") + text(330, 108, "сигнал", 9, GREEN, "middle", "bold")
    s += arrow(428, 145, 500, 115, GREEN, 1.6, "4 3")
    s += text(W / 2, H - 12,
              "Сигнал має перетнути бар'єр (світлом, полем чи магнітом), але струм — ні. Без цього дотик до плати = дотик до мережі.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-1-3-isolation-barrier.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.2 — тиристор (SCR)
# ─────────────────────────────────────────────────────────────────────────────
def fig112_pnpn_two_bjt():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 28, "Чотири шари PNPN = два транзистори, зчеплені в защіпку", 15, INK, "middle", "bold")
    # ліворуч: стовпчик шарів
    cx = 150
    layers = [("p", "#f6dede", "анод A"), ("n", "#dfe7f0", ""), ("p", "#f6dede", "затвор G"), ("n", "#dfe7f0", "катод K")]
    y0, lh = 80, 56
    for i, (lab, fill, term) in enumerate(layers):
        y = y0 + i * lh
        s += rect(cx - 60, y, 120, lh, fill, INK, 1.6)
        s += text(cx, y + lh / 2 + 5, lab, 16, INK, "middle", "bold")
        if term and "анод" in term:
            s += line(cx, y, cx, y - 24, INK, 2.2) + text(cx, y - 30, term, 10.5, RED, "middle", "bold")
        elif term and "катод" in term:
            s += line(cx, y + lh, cx, y + lh + 24, INK, 2.2) + text(cx, y + lh + 38, term, 10.5, BLUE, "middle", "bold")
        if term and "затвор" in term:
            s += line(cx - 60, y + lh / 2, cx - 96, y + lh / 2, GREEN, 2) + text(cx - 100, y + lh / 2 + 4, term, 10, GREEN, "end", "bold")
    s += text(cx, y0 + 4 * lh + 60, "PNPN", 13, INK, "middle", "bold")
    # стрілка «розрізати по діагоналі»
    s += arrow(cx + 80, y0 + 2 * lh, cx + 170, y0 + 2 * lh, GREY, 2)
    s += text(cx + 125, y0 + 2 * lh - 10, "розщепити", 9.5, GREY, "middle", "bold")
    # праворуч: два транзистори навхрест
    bx = 560
    # PNP (зверху) + NPN (знизу), з'єднані навхрест
    s += text(bx, 64, "еквівалент: PNP + NPN", 12.5, INK, "middle", "bold")
    # PNP
    s += line(bx - 70, 110, bx - 30, 110, RED, 2) + text(bx - 76, 114, "A", 10, RED, "end", "bold")
    s += line(bx - 30, 92, bx - 30, 128, INK, 3)
    s += line(bx - 30, 100, bx + 6, 84, INK, 2) + line(bx - 30, 120, bx + 6, 136, INK, 2)
    s += arrow(bx + 6, 84, bx - 18, 96, INK, 1.8)
    s += text(bx + 12, 84, "Q1 (PNP)", 9.5, INK, "start", "bold")
    # NPN
    s += line(bx - 70, 210, bx - 30, 210, BLUE, 2) + text(bx - 76, 214, "K", 10, BLUE, "end", "bold")
    s += line(bx - 30, 192, bx - 30, 228, INK, 3)
    s += line(bx - 30, 200, bx + 6, 184, INK, 2) + line(bx - 30, 220, bx + 6, 236, INK, 2)
    s += arrow(bx - 18, 224, bx + 6, 236, INK, 1.8)
    s += text(bx + 12, 240, "Q2 (NPN)", 9.5, INK, "start", "bold")
    # перехресні з'єднання: колектор Q1 -> база Q2, колектор Q2 -> база Q1
    s += line(bx + 6, 136, bx + 40, 136, GREEN, 1.8) + line(bx + 40, 136, bx + 40, 200, GREEN, 1.8) + line(bx + 40, 200, bx - 30, 200, GREEN, 1.8)
    s += line(bx + 6, 184, bx + 64, 184, RED, 1.8) + line(bx + 64, 184, bx + 64, 110, RED, 1.8) + line(bx + 64, 110, bx - 30, 110, RED, 1.8)
    s += line(bx - 30, 210, bx - 30, 220, INK, 1)  # затвор у базу Q2
    s += arrow(bx - 96, 210, bx - 70, 210, GREEN, 2) + text(bx - 100, 214, "G", 11, GREEN, "end", "bold")
    s += text(bx + 86, 150, "колектор кожного", 9, GREEN, "start")
    s += text(bx + 86, 166, "живить базу іншого", 9, GREEN, "start")
    s += text(W / 2, H - 14,
              "Колектор верхнього транзистора годує базу нижнього і навпаки — додатний зворотний зв'язок. Раз відкрилися, тримають одне одного відкритими.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-2-1-pnpn-two-bjt.svg", s)


def fig112_latch_loop():
    W, H = 800, 300
    s = header(W, H)
    s += text(W / 2, 30, "Защіпка: імпульс у затвор запускає самопідтримний цикл", 15, INK, "middle", "bold")
    # цикл зі стрілок
    cx, cy, r = 400, 165, 92
    steps = [
        ("імпульс у затвор", -90),
        ("Q2 трохи відкрився", -18),
        ("струм у базу Q1", 54),
        ("Q1 відкрив Q2 ще", 126),
        ("обидва насичені", 198),
    ]
    nodes = []
    for lab, ang in steps:
        a = math.radians(ang)
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        nodes.append((x, y, lab))
    for i, (x, y, lab) in enumerate(nodes):
        col = GREEN if i == 0 else (RED if i == len(nodes) - 1 else INK)
        s += circle(x, y, 7, "#ffffff", col, 2)
        # підпис назовні
        a = math.atan2(y - cy, x - cx)
        lx, ly = cx + (r + 36) * math.cos(a), cy + (r + 36) * math.sin(a)
        anc = "middle"
        s += text(lx, ly + 4, lab, 10, col, anc, "bold")
    # дуги
    for i in range(len(nodes)):
        x1, y1, _ = nodes[i]
        x2, y2, _ = nodes[(i + 1) % len(nodes)]
        s += arrow(x1 + (x2 - x1) * 0.18, y1 + (y2 - y1) * 0.18,
                   x1 + (x2 - x1) * 0.82, y1 + (y2 - y1) * 0.82, GREY, 2)
    s += text(cx, cy + 4, "ЗАМКНУТО", 12, RED, "middle", "bold")
    s += text(W / 2, H - 12,
              "Затвор потрібен лише на старт. Далі транзистори тримають одне одного — затвор можна відпустити, прилад лишається відкритим.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-2-2-latch-loop.svg", s)


def fig112_holding_current():
    W, H = 820, 330
    s = header(W, H)
    s += text(W / 2, 28, "Вимикається сам: коли струм падає нижче утримуючого Iн", 14.5, INK, "middle", "bold")
    ox, oy, ww, hh = 80, 250, 580, 200
    s += _axes(ox, oy, ww, hh, "t", "I через тиристор", up_down=False)
    # півхвиля випрямленого струму (синус, обрізаний знизу нулем)
    amp = 150
    pts = []
    for j in range(0, int(ww) + 1):
        v = math.sin(math.pi * (j / ww))  # одна півхвиля 0..pi
        pts.append((ox + j, oy - amp * v))
    s += _poly(pts, RED, 2.6)
    # рівень утримуючого струму
    ih = 22
    s += line(ox, oy - ih, ox + ww, oy - ih, GREEN, 1.6, "6 4")
    s += text(ox + ww + 14, oy - ih + 4, "Iн (утрим.)", 10, GREEN, "start", "bold")
    # точки вмикання й вимикання
    # запуск на початку
    s += circle(ox + 18, oy - amp * math.sin(math.pi * (18 / ww)), 6, "#cdeccd", GREEN, 2)
    s += arrow(ox + 18, oy + 36, ox + 18, oy - amp * math.sin(math.pi * (18 / ww)) + 8, GREEN, 1.8)
    s += text(ox + 18, oy + 52, "імпульс затвора → ON", 9.5, GREEN, "middle", "bold")
    # вимикання, де крива перетинає Iн (ближче до кінця)
    # знайти j, де amp*sin == ih на спадній ділянці
    joff = None
    for j in range(int(ww), 0, -1):
        if amp * math.sin(math.pi * (j / ww)) >= ih:
            joff = j
            break
    xoff = ox + joff
    s += circle(xoff, oy - ih, 6, "#fbecec", RED, 2)
    s += line(xoff, oy - ih, xoff, oy + 8, RED, 1.4, "3 3")
    s += arrow(xoff + 70, oy - 80, xoff + 4, oy - ih - 4, RED, 1.8)
    s += text(xoff + 74, oy - 86, "I < Iн → защіпка зривається → OFF", 9.5, RED, "start", "bold")
    # зона провідності
    s += rect(ox + 18, oy - 4, joff - 18, 4, "#e9f6ee", GREEN, 0)
    s += text(ox + joff / 2, oy + 22, "проводить", 9.5, GREEN, "middle", "bold")
    s += text(ox + ww * 0.92, oy + 22, "закрито", 9, BLUE, "middle", "bold")
    s += text(W / 2, H - 10,
              "У мережі струм щопівперіоду сам сходить до нуля — тож тиристор гасне природно наприкінці кожної півхвилі. Не треба окремо «вимикати».",
              9.5, GREY, "middle", style="italic")
    save("fig-11-2-3-holding-current.svg", s)


def fig112_iv_curve():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 28, "ВАХ тиристора: дві стійкі гілки й перемикання між ними", 14.5, INK, "middle", "bold")
    ox, oy, ww, hh = 360, 200, 300, 150
    # осі по центру
    s += arrow(ox - 300, oy, ox + ww, oy, INK, 1.8) + text(ox + ww + 6, oy + 4, "U(A-K)", 11, INK, "start", "bold")
    s += arrow(ox, oy + 120, ox, oy - hh - 14, INK, 1.8) + text(ox - 6, oy - hh - 20, "I", 12, INK, "middle", "bold")
    # пряма гілка: спершу майже не проводить (висока напруга), потім «defl» вниз і круто вгору при малій напрузі
    # блокуюча ділянка
    pts_block = [(ox, oy), (ox + 150, oy - 6), (ox + 250, oy - 26)]
    s += _poly(pts_block, GREY, 2.4)
    s += text(ox + 250, oy - 36, "блокує (вимкнено)", 9, GREY, "middle")
    # точка перемикання Vbo
    s += circle(ox + 250, oy - 26, 5, "#fff3b0", SUN, 2)
    s += text(ox + 256, oy - 14, "Vbo", 10, SUN, "start", "bold")
    s += text(ox + 250, oy + 18, "↑ або імпульс затвора", 8.5, GREEN, "middle", "bold")
    # негативний нахил (пунктир) до низької напруги
    s += _poly([(ox + 250, oy - 26), (ox + 70, oy - 70)], RED, 1.6, "4 3")
    # провідна гілка — круто вгору при малій напрузі
    pts_on = [(ox + 30, oy - 60), (ox + 36, oy - hh)]
    s += _poly(pts_on, GREEN, 2.8)
    s += text(ox + 50, oy - hh + 6, "проводить (увімкнено)", 9.5, GREEN, "start", "bold")
    s += text(ox + 30, oy - 50, "Vt ≈ 1…1.5 В", 9, GREEN, "end", "bold")
    # утримуючий струм на провідній гілці
    s += circle(ox + 32, oy - 60, 5, "#cdeccd", GREEN, 2) + text(ox + 18, oy - 70, "Iн", 9.5, GREEN, "end", "bold")
    # зворотна гілка: блокує до пробою
    s += _poly([(ox, oy), (ox - 250, oy + 8)], BLUE, 2.4)
    s += text(ox - 150, oy + 24, "зворотна: блокує", 9, BLUE, "middle")
    s += _poly([(ox - 250, oy + 8), (ox - 256, oy + 60)], BLUE, 1.6, "4 3")
    s += text(ox - 256, oy + 74, "лавинний пробій", 8.5, BLUE, "middle")
    s += text(W / 2, H - 10,
              "Затвор не «прочиняє» прилад плавно, як транзистор: він перекидає його з блокуючої гілки на провідну. Між ними — нестійка ділянка, прилад на ній не затримується.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-2-4-iv-curve.svg", s)


def fig112_half_wave_circuit():
    W, H = 720, 300
    s = header(W, H)
    s += text(W / 2, 26, "Тиристор у мережі: керована півхвиля на навантаженні", 14.5, INK, "middle", "bold")
    lx, rx, ty, by = 110, 610, 80, 230
    midy = (ty + by) / 2
    # джерело AC ліворуч, у розрив лівої вертикалі
    s += _ac_source(lx, midy, 24, INK) + text(lx - 30, midy + 4, "~230 В", 10, INK, "end", "bold")
    s += line(lx, ty, lx, midy - 24, INK, 2)          # від верхнього кута до джерела
    s += line(lx, midy + 24, lx, by, INK, 2)          # від джерела до нижнього кута
    # верхній провід із тиристором (анод зліва, катод справа)
    sx = 320                                           # центр символу SCR
    s += line(lx, ty, sx - 26, ty, INK, 2)
    # горизонтальний тиристор: трикутник вістрям праворуч + катодна планка
    s += _fill_poly([(sx - 26, ty - 13), (sx - 26, ty + 13), (sx, ty)], "#dfe7f0", INK, 1.8)
    s += line(sx, ty - 13, sx, ty + 13, INK, 2.6)
    s += text(sx - 30, ty - 18, "A", 10, RED, "end", "bold") + text(sx + 6, ty - 18, "K", 10, BLUE, "start", "bold")
    s += line(sx, ty, 470, ty, INK, 2)
    # затвор донизу до блоку запуску
    s += line(sx - 12, ty + 7, sx - 12, by - 44, GREEN, 2)
    s += rect(sx - 62, by - 44, 100, 38, "#eef6ef", GREEN, 1.6, 6) + text(sx - 12, by - 21, "запуск", 10, GREEN, "middle", "bold")
    s += text(sx - 12, by - 4, "(від МК через розв'язку)", 8, GREY, "middle")
    # лампа праворуч у вертикалі
    s += line(470, ty, rx, ty, INK, 2)
    s += line(rx, ty, rx, midy - 18, INK, 2)
    s += _bulb(rx, midy, 18, INK, True) + text(rx + 26, midy + 4, "лампа", 10, INK, "start")
    s += line(rx, midy + 18, rx, by, INK, 2)
    # нижній провід
    s += line(lx, by, rx, by, INK, 2)
    s += text(W / 2, H - 8,
              "Поки нема імпульсу — тиристор закритий, лампа темна. Дали імпульс у затвор — він замкнувся й проводить до кінця додатної півхвилі, де гасне сам. Від'ємні півхвилі тиристор блокує.",
              9, GREY, "middle", style="italic")
    save("fig-11-2-5-half-wave-circuit.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.3 — симістор (TRIAC)
# ─────────────────────────────────────────────────────────────────────────────
def fig113_two_scr():
    W, H = 800, 320
    s = header(W, H)
    s += text(W / 2, 28, "Симістор = два зустрічні тиристори в одному кристалі", 15, INK, "middle", "bold")
    # ліворуч: два антипаралельні SCR
    s += _frame(40, 56, 360, 236, "два SCR назустріч")
    s += _scr_sym(150, 150, INK)
    # другий — перевернутий
    cx2 = 250
    s += line(cx2, 150 + 40, cx2, 150 + 14, INK, 2.2)
    s += _fill_poly([(cx2 - 13, 150 + 14), (cx2 + 13, 150 + 14), (cx2, 150 - 8)], "#dfe7f0", INK, 1.8)
    s += line(cx2 - 15, 150 - 8, cx2 + 15, 150 - 8, INK, 2.6)
    s += line(cx2, 150 - 8, cx2, 150 - 40, INK, 2.2)
    # з'єднати їх паралельно навхрест
    s += line(150, 150 - 40, cx2, 150 + 40, GREY, 1.6, "4 3")
    s += line(150, 150 + 40, cx2, 150 - 40, GREY, 1.6, "4 3")
    s += text(200, 250, "обидві полярності", 10, INK, "middle", "bold")
    # праворуч: символ TRIAC
    s += _frame(440, 56, 320, 236, "символ симістора")
    s += _triac_sym(580, 165, INK)
    s += text(600, 165, "  один затвор", 10, GREEN, "start", "bold")
    s += text(580, 270, "MT1 / MT2 рівноправні", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 8,
              "Тиристор пропускає одну полярність. Симістор (TRIAC, TRIode for Alternating Current) — це немовби два тиристори назустріч, тож проводить обидві півхвилі.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-3-1-two-scr.svg", s)


def fig113_both_halves():
    W, H = 800, 330
    s = header(W, H)
    s += text(W / 2, 28, "Обидві півхвилі: симістор керує всім періодом", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 80, 175, 600, 240
    s += _axes(ox, oy, ww, hh, "t", "U навант.", up_down=True)
    amp = 90
    # повна синусоїда блідо
    s += _poly(_sine_pts(ox, oy, ww, amp, 2.0), FAINT, 2.2)
    # симістор відкривається із затримкою на КОЖНІЙ півхвилі — фазове відсікання
    alpha = 0.28  # частка періоду до запуску
    period = ww / 2.0
    pts = []
    for j in range(0, int(ww) + 1):
        ph = (j % period) / period  # 0..1 у межах півперіоду
        v = math.sin(2 * math.pi * 2.0 * (j / ww))
        if ph < alpha:
            v = 0.0
        pts.append((ox + j, oy - amp * v))
    s += _poly(pts, RED, 2.6)
    # позначки запуску на обох півхвилях
    for k in range(2):
        xt = ox + (k + alpha) * period
        s += circle(xt, oy, 5, "#cdeccd", GREEN, 2)
        s += text(xt, oy + (20 if k == 0 else 34), "запуск", 9, GREEN, "middle", "bold")
    s += text(ox + 70, oy - amp - 12, "додатна — проводить", 9.5, RED, "middle")
    s += text(ox + 230, oy + amp + 22, "від'ємна — теж проводить", 9.5, BLUE, "middle")
    s += text(W / 2, H - 10,
              "На відміну від тиристора, який міг би вкрасти лише додатні півхвилі, симістор віддає навантаженню обидві — повну потужність мережі за потреби.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-3-2-both-halves.svg", s)


def fig113_quadrants():
    W, H = 720, 360
    s = header(W, H)
    s += text(W / 2, 28, "Квадранти запуску: знак MT2 × знак затвора", 15, INK, "middle", "bold")
    cx, cy, L = 360, 195, 130
    s += line(cx - L - 20, cy, cx + L + 20, cy, INK, 1.6) + text(cx + L + 24, cy + 4, "U(MT2)", 10, INK, "start", "bold")
    s += line(cx, cy + L + 20, cx, cy - L - 20, INK, 1.6) + text(cx + 6, cy - L - 22, "U(G)", 10, GREEN, "start", "bold")
    quads = [
        (cx + L / 2, cy - L / 2, "I", "MT2 +, G +", GREEN, "найчутливіший"),
        (cx - L / 2, cy - L / 2, "II", "MT2 −, G +", SUN, "трохи гірше"),
        (cx - L / 2, cy + L / 2, "III", "MT2 −, G −", SUN, "трохи гірше"),
        (cx + L / 2, cy + L / 2, "IV", "MT2 +, G −", RED, "найгірший"),
    ]
    for x, y, num, cond, col, note in quads:
        s += text(x, y - 16, "Квадрант " + num, 12, col, "middle", "bold")
        s += text(x, y + 4, cond, 10.5, INK, "middle")
        s += text(x, y + 22, note, 9, col, "middle", style="italic")
    s += text(W / 2, H - 14,
              "Симістор запускається в усіх чотирьох комбінаціях полярностей, але неоднаково легко. Квадрант IV — найвередливіший; драйвери часто його уникають.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-3-3-quadrants.svg", s)


def fig113_diac():
    W, H = 800, 330
    s = header(W, H)
    s += text(W / 2, 28, "DIAC у колі затвора: чекає порогу — і б'є чітким імпульсом", 14, INK, "middle", "bold")
    # RC + DIAC -> gate
    lx = 90
    s += line(lx, 90, lx, 240, INK, 2) + text(lx - 6, 84, "MT2 (фаза)", 9.5, INK, "end", "bold")
    # R від фази до вузла
    s += line(lx, 130, 200, 130, INK, 2)
    s += _res_h(250, 130, 60, 14, INK, "R (потенціометр)")
    s += line(280, 130, 360, 130, INK, 2)
    node = 360
    # C від вузла до MT1
    s += line(node, 130, node, 180, INK, 2)
    s += _cap_v(node, 196, 7, 16, INK, "C")
    s += line(node, 212, node, 240, INK, 2)
    s += line(lx, 240, 560, 240, INK, 2) + text(420, 256, "MT1", 9.5, INK, "middle", "bold")
    # DIAC від вузла до затвора
    s += line(node, 130, 440, 130, INK, 2)
    # символ DIAC: два зустрічні трикутники без затвора
    dcx = 470
    s += _fill_poly([(dcx - 14, 124), (dcx - 14, 136), (dcx + 4, 130)], "#dfe7f0", INK, 1.6)
    s += _fill_poly([(dcx + 14, 124), (dcx + 14, 136), (dcx - 4, 130)], "#dfe7f0", INK, 1.6)
    s += text(dcx, 112, "DIAC", 9.5, INK, "middle", "bold")
    # вихід DIAC іде у затвор симістора (зелена лінія керування)
    diac_out = dcx + 14
    s += line(diac_out, 130, 540, 130, GREEN, 2)
    s += line(540, 130, 562, 205, GREEN, 2)        # вниз у затвор
    s += text(548, 124, "у затвор", 8.5, GREEN, "start", "bold")
    # симістор праворуч; MT2 -> верхня фазова шина, MT1 -> нижня
    s += _triac_sym(600, 175, INK)
    s += line(600, 175 - 42, 600, 110, INK, 2) + line(600, 110, lx, 110, INK, 2)  # MT2 -> фаза (ліва шина)
    s += line(600, 175 + 42, 600, 240, INK, 2)     # MT1 -> нижня шина
    s += text(W / 2, H - 26,
              "Поки напруга на C мала — DIAC закритий, у затвор нічого не йде. Дійшла до Vbo (~32 В) — DIAC лавиною відмикається й розряджає C різким імпульсом.",
              9.5, GREY, "middle", style="italic")
    s += text(W / 2, H - 10,
              "Так RC задає кут запуску, а DIAC робить фронт різким і однаковим для обох полярностей — це класична схема димера.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-3-4-diac.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.4 — фазове керування (димер)
# ─────────────────────────────────────────────────────────────────────────────
def fig114_firing_angle():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 26, "Кут відсікання α: коли в межах півхвилі дали запуск", 15, INK, "middle", "bold")

    def panel(ox, oy, alpha_frac, title):
        ww, amp = 320, 70
        t = arrow(ox, oy + amp + 8, ox, oy - amp - 14, INK, 1.6)
        t += arrow(ox, oy, ox + ww + 12, oy, INK, 1.6)
        t += text(ox + ww / 2, oy - amp - 18, title, 11.5, INK, "middle", "bold")
        # блідий повний синус (дві півхвилі додатні — випрямлено для наочності фази)
        full = []
        for j in range(0, ww + 1):
            v = math.sin(math.pi * ((j % (ww / 2)) / (ww / 2)))
            full.append((ox + j, oy - amp * v))
        t += _poly(full, FAINT, 2)
        # відсічена частина (проводить від alpha до кінця кожної півхвилі)
        cut = []
        period = ww / 2
        for j in range(0, ww + 1):
            ph = (j % period) / period
            v = math.sin(math.pi * ph)
            if ph < alpha_frac:
                v = 0.0
            cut.append((ox + j, oy - amp * v))
        t += _poly(cut, RED, 2.6)
        # лінія запуску
        xt = ox + alpha_frac * period
        t += line(xt, oy, xt, oy - amp - 6, GREEN, 1.5, "4 3")
        t += text(xt, oy + 16, "α", 12, GREEN, "middle", "bold")
        # підпис відсотка
        return t

    s += panel(60, 130, 0.1, "α малий → майже повна потужність")
    s += panel(470, 130, 0.5, "α = 90° → половина потужності")
    s += panel(60, 300, 0.85, "α великий → тьмяно")
    # текстовий блок праворуч-знизу
    s += rect(440, 230, 380, 100, LGRN, GREEN, 1.4, 8)
    s += text(630, 256, "Що пізніше запуск (більший α),", 11, INK, "middle")
    s += text(630, 278, "то менший шмат півхвилі дістається", 11, INK, "middle")
    s += text(630, 300, "навантаженню → менша середня потужність.", 11, INK, "middle")
    s += text(W / 2, H - 8,
              "Димер не «прикручує» напругу — він щопівперіоду відкриває симістор пізніше чи раніше, віддаючи навантаженню більший або менший шмат синусоїди.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-4-1-firing-angle.svg", s)


def fig114_power_vs_angle():
    W, H = 740, 360
    s = header(W, H)
    s += text(W / 2, 28, "Потужність від кута: 90° — це рівно половина", 15, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 290, 560, 230
    s += _axes(ox, oy, ww, hh, "α, градуси", "P / Pмакс", up_down=False)
    # P(α) = (1/π)*(π-α + sin(2α)/2) нормовано від 0 до 1 (для α 0..180)
    pts = []
    for k in range(0, 181, 2):
        a = math.radians(k)
        frac = (math.pi - a + math.sin(2 * a) / 2) / math.pi
        x = ox + (k / 180) * ww
        y = oy - frac * (hh - 10)
        pts.append((x, y))
    s += _poly(pts, RED, 2.8)
    # позначки осі X
    for k in (0, 45, 90, 135, 180):
        x = ox + (k / 180) * ww
        s += line(x, oy, x, oy + 5, INK, 1.4)
        s += text(x, oy + 20, str(k), 10, INK, "middle")
    # позначки осі Y
    for fr, lab in [(0.0, "0"), (0.5, "0.5"), (1.0, "1.0")]:
        y = oy - fr * (hh - 10)
        s += line(ox - 5, y, ox, y, INK, 1.4) + text(ox - 9, y + 4, lab, 10, INK, "end")
        s += line(ox, y, ox + ww, y, FAINT, 1, "4 4")
    # точка 90° → 0.5
    a90 = math.radians(90)
    fr90 = (math.pi - a90 + math.sin(2 * a90) / 2) / math.pi
    x90 = ox + 0.5 * ww
    y90 = oy - fr90 * (hh - 10)
    s += circle(x90, y90, 6, "#fff3b0", SUN, 2)
    s += line(x90, y90, x90, oy, GREEN, 1.4, "3 3") + line(ox, y90, x90, y90, GREEN, 1.4, "3 3")
    s += text(x90 + 10, y90 - 8, "90° → 50%", 11, GREEN, "start", "bold")
    s += text(W / 2, H - 10,
              "Залежність нелінійна: половина потужності припадає рівно на середину півперіоду (90°), а не на «половину ходу» регулятора. Звідси нерівномірність дешевих димерів.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-4-2-power-vs-angle.svg", s)


def fig114_lamp_vs_smps():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 28, "Чому лампа димерується, а імпульсний блок — ні", 15, INK, "middle", "bold")

    def panel(ox, title, ok, body):
        col = GREEN if ok else RED
        t = rect(ox, 58, 360, 200, "#ffffff", col, 1.8, 10)
        t += rect(ox, 58, 360, 36, "#f4f6f8", col, 1.8, 10)
        t += text(ox + 180, 82, title, 13, col, "middle", "bold")
        y = 118
        for ln in body:
            t += text(ox + 180, y, ln, 11, INK, "middle")
            y += 24
        t += text(ox + 180, 244, "OK ✓" if ok else "погано ✗", 12, col, "middle", "bold")
        return t

    s += panel(30, "лампа розжарення (опір)", True, [
        "споживає миттєву напругу як є;",
        "грубо: менший шмат синусоїди →",
        "менше тепла → тьмяніше світло.",
        "інерції нитки достатньо,",
        "щоб не мерехтіти."])
    s += panel(430, "імпульсний блок (SMPS)", False, [
        "на вході — діодний міст + конденсатор;",
        "качає струм короткими голками",
        "біля піка синусоїди.",
        "відсік ту частину — блок або гасне,",
        "або тягне ще різкіше → нагрів, шум."])
    s += text(W / 2, H - 10,
              "Фазове керування любить резистивне навантаження. З електронікою, що сама перетворює напругу, проста відсічка б'ється — для неї роблять окремі «димеровані» драйвери.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-4-3-lamp-vs-smps.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.5 — перехід через нуль
# ─────────────────────────────────────────────────────────────────────────────
def fig115_random_vs_zero():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 26, "Де комутувати: будь-де (random-phase) чи в нулі (zero-cross)", 14.5, INK, "middle", "bold")

    def panel(ox, oy, zero, title):
        ww, amp = 340, 64
        t = arrow(ox, oy + amp + 8, ox, oy - amp - 12, INK, 1.6)
        t += arrow(ox, oy, ox + ww + 12, oy, INK, 1.6)
        t += text(ox + ww / 2, oy - amp - 16, title, 11.5, INK, "middle", "bold")
        t += _poly(_sine_pts(ox, oy, ww, amp, 2.0), FAINT, 2)
        # точка вмикання
        if zero:
            xt = ox + ww * (1.0 / 2)  # у нулі (середина періоду, де синус = 0)
            # знайти найближчий перехід нуля
            xt = ox + ww * 0.5
        else:
            xt = ox + ww * 0.37  # десь на схилі
        # провідна частина — від xt
        cut = []
        n = int(ww)
        for j in range(0, n + 1):
            x = ox + j
            v = math.sin(2 * math.pi * 2.0 * (j / ww))
            if x < xt:
                v = 0.0
            cut.append((x, oy - amp * v))
        t += _poly(cut, RED, 2.6)
        # стрибок напруги в момент комутації
        vstep = math.sin(2 * math.pi * 2.0 * ((xt - ox) / ww))
        t += line(xt, oy, xt, oy - amp * vstep, GREEN if zero else RED, 2.6)
        t += circle(xt, oy - amp * vstep, 5, "#ffffff", GREEN if zero else RED, 2)
        if zero:
            t += text(xt, oy + 18, "вмикання в 0 В", 9.5, GREEN, "middle", "bold")
            t += text(xt, oy + 34, "стрибка нема", 9, GREEN, "middle")
        else:
            t += text(xt, oy + 18, "вмикання на піку", 9.5, RED, "middle", "bold")
            t += text(xt, oy - amp * vstep - 8, "різкий стрибок!", 9, RED, "middle", "bold")
        return t

    s += panel(60, 140, False, "random-phase: будь-де")
    s += panel(480, 140, True, "zero-cross: у переході нуля")
    # спектр завад — дві смужки
    s += rect(60, 245, 340, 90, "#fbecec", "#d8a0a0", 1.4, 8)
    s += text(230, 268, "різкий фронт → широкий спектр", 11, RED, "middle", "bold")
    for i in range(9):
        h0 = 30 - i * 2
        s += rect(90 + i * 30, 322 - h0, 12, h0, "#e7a6a6", RED, 0)
    s += text(230, 332, "багато ВЧ-завад (EMI)", 9, RED, "middle")
    s += rect(480, 245, 340, 90, "#eef6ef", GREEN, 1.4, 8)
    s += text(650, 268, "плавний старт у нулі → чисто", 11, GREEN, "middle", "bold")
    for i in range(3):
        h0 = 26 - i * 8
        s += rect(560 + i * 40, 322 - h0, 14, h0, "#a7d4b4", GREEN, 0)
    s += text(650, 332, "майже без завад", 9, GREEN, "middle")
    s += text(W / 2, H - 6,
              "Вмикати струм у момент, коли напруга й так нуль, — це м'який старт без стрибка, а отже без сплеску завад. Саме так працює zero-cross-комутація.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-5-1-random-vs-zero.svg", s)


def fig115_zero_detector():
    W, H = 800, 320
    s = header(W, H)
    s += text(W / 2, 28, "Детектор нуля: з синусоїди роблять імпульс щопівперіоду", 14.5, INK, "middle", "bold")
    ox, oy, ww, amp = 80, 150, 640, 70
    s += arrow(ox, oy + amp + 10, ox, oy - amp - 14, INK, 1.6)
    s += arrow(ox, oy, ox + ww + 12, oy, INK, 1.6)
    s += text(ox + ww + 16, oy + 4, "t", 11, INK, "start", "bold")
    s += _poly(_sine_pts(ox, oy, ww, amp, 3.0), RED, 2.4)
    s += text(ox + 120, oy - amp - 4, "напруга мережі", 10, RED, "start", "bold")
    # вертикальні маркери у переходах нуля
    zeros = []
    for k in range(0, 7):
        xt = ox + ww * (k / 6)
        zeros.append(xt)
        s += line(xt, oy - amp, xt, oy + amp + 40, FAINT, 1, "3 3")
    # імпульси внизу
    base = oy + amp + 60
    s += line(ox, base, ox + ww + 12, base, INK, 1.4)
    s += text(ox - 8, base + 4, "0", 9, INK, "end")
    for xt in zeros:
        s += line(xt - 4, base, xt - 4, base - 32, BLUE, 2.4)
        s += line(xt - 4, base - 32, xt + 4, base - 32, BLUE, 2.4)
        s += line(xt + 4, base - 32, xt + 4, base, BLUE, 2.4)
    s += text(ox + ww * 0.5, base + 24, "логічні імпульси «тут нуль» → у мікроконтролер", 10.5, BLUE, "middle", "bold")
    s += text(W / 2, H - 8,
              "Оптопара на змінному вході спалахує двічі за період — рівно в переходах нуля. Ці імпульси дають МК точку відліку для фази й синхронну комутацію.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-5-2-zero-detector.svg", s)


def fig115_burst_control():
    W, H = 820, 300
    s = header(W, H)
    s += text(W / 2, 28, "Burst-керування: пропускаємо цілі півперіоди (для інерційних навантажень)", 12.5, INK, "middle", "bold")
    ox, oy, ww, amp = 70, 150, 680, 60
    s += arrow(ox, oy + amp + 8, ox, oy - amp - 12, INK, 1.6)
    s += arrow(ox, oy, ox + ww + 12, oy, INK, 1.6)
    # 12 півперіодів; увімкнені 8 з 12 (≈67%)
    nhalf = 12
    on_mask = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
    hw = ww / nhalf if (nhalf := nhalf) else ww
    for k in range(nhalf):
        x0 = ox + k * hw
        pts = []
        for j in range(0, int(hw) + 1):
            v = math.sin(math.pi * (j / hw)) * (1 if k % 2 == 0 else -1)
            pts.append((x0 + j, oy - amp * v))
        if on_mask[k]:
            s += _poly(pts, RED, 2.4)
        else:
            s += _poly(pts, FAINT, 2)
    # рамки on/off
    s += rect(ox, oy + amp + 16, hw * 8, 4, "#e9f6ee", GREEN, 0)
    s += text(ox + hw * 4, oy + amp + 36, "8 півперіодів увімкнено", 10, GREEN, "middle", "bold")
    s += rect(ox + hw * 8, oy + amp + 16, hw * 4, 4, "#f4f4f4", GREY, 0)
    s += text(ox + hw * 10, oy + amp + 36, "4 — пропущено", 10, GREY, "middle", "bold")
    s += text(ox + ww * 0.5, oy - amp - 14, "≈ 67% потужності, але кожна півхвиля ціла", 10.5, INK, "middle", "bold")
    s += text(W / 2, H - 10,
              "Замість різати кожну півхвилю, віддаємо одні півперіоди повністю, інші зовсім пропускаємо. Фронтів мало → завад мало; годиться там, де навантаження інерційне (нагрівач).",
              9.5, GREY, "middle", style="italic")
    save("fig-11-5-3-burst-control.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.6 — твердотільне реле (SSR)
# ─────────────────────────────────────────────────────────────────────────────
def fig116_ssr_inside():
    W, H = 880, 340
    s = header(W, H)
    s += text(W / 2, 28, "Усередині SSR: світлодіод керування → оптотриак → силовий симістор", 13.5, INK, "middle", "bold")
    # корпус
    s += rect(40, 60, 800, 220, "#fbfbfb", "#c9d3dc", 1.6, 10)
    s += text(60, 80, "корпус SSR", 11, GREY, "start", "bold")
    # вхід керування
    s += text(120, 110, "вхід 3…32 В DC", 11, BLUE, "middle", "bold")
    s += line(70, 150, 110, 150, INK, 2) + plus(70, 150, 9, RED, 2)
    s += _res_h(140, 150, 40, 12, INK, "R")
    s += line(160, 150, 195, 150, INK, 2)
    # LED
    s += _fill_poly([(195, 140), (195, 160), (213, 150)], "#fde9c8", COPP, 1.6)
    s += line(213, 140, 213, 160, COPP, 2.4)
    s += arrow(204, 134, 214, 124, SUN, 1.5) + arrow(210, 136, 220, 126, SUN, 1.5)
    s += text(204, 178, "LED", 9, COPP, "middle", "bold")
    s += line(213, 150, 213, 200, INK, 2) + line(70, 150, 70, 200, INK, 2) + line(70, 200, 213, 200, INK, 2)
    # бар'єр
    s += line(250, 70, 250, 270, SUN, 2, "6 5")
    s += text(250, 64, "оптична розв'язка", 9.5, "#9a7b2e", "middle", "bold")
    # світло крізь бар'єр
    s += arrow(220, 150, 290, 150, SUN, 1.8, "4 3") + text(255, 142, "світло", 9, "#9a7b2e", "middle", "bold")
    # детектор нуля (для zero-cross версії)
    s += rect(290, 122, 90, 56, "#eef6ef", GREEN, 1.4, 6)
    s += text(335, 144, "детектор", 9, GREEN, "middle", "bold")
    s += text(335, 160, "нуля", 9, GREEN, "middle", "bold")
    # оптотріак / driver
    s += line(380, 150, 420, 150, INK, 2)
    # силовий симістор
    s += _triac_sym(470, 165, INK)
    s += text(470, 110, "силовий TRIAC / MOSFET", 9.5, INK, "middle", "bold")
    # вихід — у навантаження й мережу
    s += line(470, 165 - 42, 470, 110, INK, 2)
    s += line(470, 110, 760, 110, INK, 2)
    s += _bulb(760, 150, 16, INK, True) + text(760, 178, "навантаження", 9, INK, "middle")
    s += line(760, 166, 760, 230, INK, 2)
    s += line(470, 165 + 42, 470, 230, INK, 2)
    # нижній провід з мережевим джерелом інлайн
    s += line(470, 230, 600, 230, INK, 2)
    s += _ac_source(620, 230, 16, RED)
    s += line(640, 230, 760, 230, INK, 2)
    s += text(620, 256, "~ мережа 230 В", 10, RED, "middle", "bold")
    s += text(W / 2, H - 12,
              "Слабкий струм у світлодіод запалює його; світло крізь прозорий бар'єр відмикає силовий ключ. Сторона керування й сторона мережі ніде не з'єднані міддю.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-6-1-ssr-inside.svg", s)


def fig116_emr_vs_ssr():
    W, H = 840, 330
    s = header(W, H)
    s += text(W / 2, 28, "Електромеханічне реле проти твердотільного", 15, INK, "middle", "bold")
    heads = ["", "реле (EMR, §2.6.9)", "SSR"]
    rows = [
        ("комутація", "металеві контакти", "напівпровідник"),
        ("керування", "котушка, десятки мА", "світлодіод, одиниці мА"),
        ("іскра / дребезг", "так, контакти горять", "немає рухомих частин"),
        ("ресурс", "сотні тисяч циклів", "практично необмежений"),
        ("швидкість", "мілісекунди", "мікросекунди, можна ШІМ-цикли"),
        ("спад напруги", "майже 0 (метал)", "1…1.6 В → тепло, радіатор"),
        ("витік у OFF", "нуль (повний розрив)", "невеликий струм витоку"),
    ]
    x0, y0 = 40, 56
    cw = [180, 300, 300]
    rh = 34
    # заголовки
    cx = x0
    for i, hd in enumerate(heads):
        fill = "#eef2f6" if i == 0 else (LRED if i == 1 else LGRN)
        s += rect(cx, y0, cw[i], rh, fill, "#c9d3dc", 1.2)
        if hd:
            s += text(cx + cw[i] / 2, y0 + 22, hd, 11.5, RED if i == 1 else GREEN, "middle", "bold")
        cx += cw[i]
    # рядки
    for r, (a, b, c) in enumerate(rows):
        y = y0 + (r + 1) * rh
        cx = x0
        vals = [a, b, c]
        for i, v in enumerate(vals):
            fill = "#f7f9fb" if i == 0 else "#ffffff"
            s += rect(cx, y, cw[i], rh, fill, "#dde3e9", 1)
            wt = "bold" if i == 0 else "normal"
            s += text(cx + (8 if i == 0 else cw[i] / 2), y + 22, v, 10.5, INK,
                      "start" if i == 0 else "middle", wt)
            cx += cw[i]
    save("fig-11-6-2-emr-vs-ssr.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.7 — IGBT
# ─────────────────────────────────────────────────────────────────────────────
def fig117_hybrid():
    W, H = 860, 330
    s = header(W, H)
    s += text(W / 2, 28, "IGBT: польовий затвор спереду, біполярний вихід ззаду", 15, INK, "middle", "bold")
    # ліворуч MOSFET-вхід
    s += _frame(40, 56, 240, 236, "вхід — як у MOSFET")
    # символ затвора-конденсатора
    s += rect(90, 120, 120, 22, "#cfd6dd", INK, 1.6) + text(150, 135, "затвор", 9.5, INK, "middle", "bold")
    s += rect(90, 142, 120, 14, "#fff3b0", SUN, 1.4) + text(150, 153, "оксид", 8, INK, "middle")
    s += rect(90, 156, 120, 30, "#e3edfb", INK, 1.6) + text(150, 176, "канал", 9.5, INK, "middle")
    for i in range(4):
        s += arrow(105 + i * 30, 142, 105 + i * 30, 168, BLUE, 1.5, "3 2")
    s += text(150, 210, "керує НАПРУГА", 10.5, GREEN, "middle", "bold")
    s += text(150, 230, "струм затвора ≈ 0", 9.5, INK, "middle")
    s += text(150, 256, "(легко гнати від логіки)", 8.5, GREY, "middle", style="italic")
    # стрілка
    s += arrow(290, 174, 340, 174, GREY, 2.4) + text(315, 164, "+", 14, GREY, "middle", "bold")
    # праворуч BJT-вихід
    s += _frame(350, 56, 240, 236, "вихід — як у BJT")
    s += _fill_poly([(420, 120), (500, 120), (500, 200), (420, 200)], "#f6dede", INK, 1.4)
    s += text(460, 136, "p", 11, INK, "middle", "bold")
    s += text(460, 192, "n", 11, BLUE, "middle", "bold")
    s += line(460, 110, 460, 120, INK, 2)
    s += line(460, 200, 460, 210, INK, 2)
    # «провідність накачана дірками» — точки
    for (px, py) in [(440, 150), (470, 158), (455, 170), (480, 148), (435, 178)]:
        s += circle(px, py, 4, "#f3c6c6", RED, 1.2)
    s += text(460, 230, "провідність БІПОЛЯРНА", 10.5, RED, "middle", "bold")
    s += text(460, 250, "низький спад навіть при 600+ В", 8.5, INK, "middle")
    # підписи виводів
    s += text(150, 100, "G", 12, GREEN, "middle", "bold")
    s += text(460, 96, "колектор (C)", 9, INK, "middle", "bold")
    s += text(460, 274, "емітер (E)", 9, INK, "middle", "bold")
    s += text(W / 2, H - 12,
              "Затвором IGBT керують напругою, легко, як MOSFET. А силова частина проводить біполярно: впорскування дірок дає малий спад на сотнях вольт — чого MOSFET там не вміє.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7-1-hybrid.svg", s)


def fig117_mosfet_vs_igbt():
    W, H = 760, 360
    s = header(W, H)
    s += text(W / 2, 28, "Де межа: спад напруги від струму, MOSFET проти IGBT", 14.5, INK, "middle", "bold")
    ox, oy, ww, hh = 90, 290, 560, 230
    s += _axes(ox, oy, ww, hh, "струм I", "спад напруги U(on)", up_down=False)
    # MOSFET: U = I * Rds(on) — пряма від 0
    s += _poly([(ox, oy), (ox + ww, oy - (hh - 10))], BLUE, 2.8)
    s += text(ox + ww - 6, oy - (hh - 10) + 14, "MOSFET: U = I·Rds(on)", 10.5, BLUE, "end", "bold")
    s += text(ox + ww * 0.7, oy - (hh - 10) * 0.78, "круто росте з I", 9, BLUE, "middle")
    # IGBT: U = Vce0 + I*r — починається з ~0.8 В, далі полого
    v0 = 0.18 * (hh - 10)
    s += _poly([(ox, oy - v0), (ox + ww, oy - v0 - 0.42 * (hh - 10))], RED, 2.8)
    s += text(ox + ww - 6, oy - v0 - 0.42 * (hh - 10) - 8, "IGBT: Vce0 + I·r", 10.5, RED, "end", "bold")
    s += text(ox - 6, oy - v0 + 4, "≈0.8 В", 9, RED, "end", "bold")
    s += text(ox + ww * 0.6, oy - v0 - 0.42 * (hh - 10) * 0.6 + 16, "полого: майже сталий спад", 9, RED, "middle")
    # точка перетину
    # MOSFET: y = (I/ww)*(hh-10) descent; IGBT: y = v0 + (I/ww)*0.42*(hh-10)
    # рівність спадів: I_m * k = v0 + I*0.42k -> при k=(hh-10)
    k = hh - 10
    Ix = v0 / (k - 0.42 * k)
    xx = ox + Ix * ww
    yy = oy - Ix * k
    if ox < xx < ox + ww:
        s += circle(xx, yy, 6, "#fff3b0", SUN, 2)
        s += line(xx, yy, xx, oy, GREY, 1.3, "3 3")
        s += text(xx, oy + 18, "межа", 10, SUN, "middle", "bold")
    s += text(ox + (xx - ox) / 2, oy + 38, "← тут вигідніший MOSFET", 9.5, BLUE, "middle", "bold")
    s += text(xx + (ox + ww - xx) / 2, oy + 38, "тут вигідніший IGBT →", 9.5, RED, "middle", "bold")
    # підпис напруги/частоти
    s += rect(ox + 30, oy - hh - 4, 300, 44, "#eef2f6", "#c9d3dc", 1.2, 6)
    s += text(ox + 180, oy - hh + 14, "груба межа: десь сотні В і кА·А струму,", 9.5, INK, "middle")
    s += text(ox + 180, oy - hh + 30, "плюс MOSFET любить вищі частоти", 9.5, INK, "middle")
    s += text(W / 2, H - 10,
              "На малих напругах і високих частотах виграє MOSFET (малий Rds(on), швидке перемикання). На сотнях вольт і великих струмах — IGBT: його спад майже не росте зі струмом.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-7-2-mosfet-vs-igbt.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.8 — снабери й dv/dt
# ─────────────────────────────────────────────────────────────────────────────
def fig118_dvdt_selftrigger():
    W, H = 820, 340
    s = header(W, H)
    s += text(W / 2, 26, "Самовмикання: різкий стрибок напруги тече крізь внутрішню ємність", 13.5, INK, "middle", "bold")
    # ліворуч індуктивне навантаження: струм відстає, напруга стрибає в нулі струму
    ox, oy, ww, amp = 70, 150, 320, 60
    s += arrow(ox, oy + amp + 8, ox, oy - amp - 12, INK, 1.6)
    s += arrow(ox, oy, ox + ww + 12, oy, INK, 1.6)
    s += text(ox + ww / 2, oy - amp - 16, "індуктивне навантаження", 11, INK, "middle", "bold")
    # струм (синус) і напруга (косинус) зсунуті
    s += _poly(_sine_pts(ox, oy, ww, amp * 0.8, 1.0, 0), BLUE, 2.2)
    s += text(ox + 40, oy + amp - 2, "струм", 9, BLUE, "start", "bold")
    # у момент, коли струм=0, тиристор гасне, а напруга мережі вже велика → стрибок
    s += _poly(_sine_pts(ox, oy, ww, amp, 1.0, math.pi / 2), RED, 2.2)
    s += text(ox + 150, oy - amp + 2, "напруга", 9, RED, "start", "bold")
    # точка: струм=0 в кінці півхвилі, напруга велика
    xz = ox + ww * 0.5
    s += line(xz, oy, xz, oy - amp, GREEN, 1.6, "3 3")
    s += circle(xz, oy, 4, "#ffffff", GREEN, 2)
    s += text(xz + 6, oy + 18, "струм=0 → OFF,", 9, GREEN, "start", "bold")
    s += text(xz + 6, oy + 32, "а напруга вже висока", 9, GREEN, "start")
    s += text(xz + 6, oy - amp - 2, "велике dv/dt", 9.5, RED, "start", "bold")
    # праворуч: механізм через ємність
    bx = 470
    s += _frame(bx, 60, 320, 220, "чому це вмикає симістор")
    s += _triac_sym(bx + 90, 150, INK)
    # внутрішня ємність між MT1 і затвором
    s += _cap_v(bx + 90 + 40, 150, 6, 12, RED, "")
    s += text(bx + 150, 150, "внутр. ємність", 9, RED, "start", "bold")
    s += arrow(bx + 90 + 14, 120, bx + 90 + 30, 150, RED, 1.6)
    s += text(bx + 220, 200, "i = C · dv/dt", 13, RED, "middle", "bold")
    s += text(bx + 160, 224, "різкий стрибок напруги жене", 9, INK, "middle")
    s += text(bx + 160, 240, "струм у затвор → хибний запуск", 9, INK, "middle")
    s += text(W / 2, H - 10,
              "На індуктивному навантаженні струм відстає, і коли симістор гасне, до нього миттю прикладається висока напруга. Це dv/dt проштовхує струм крізь внутрішню ємність у затвор — і прилад вмикається сам.",
              9, GREY, "middle", style="italic")
    save("fig-11-8-1-dvdt-selftrigger.svg", s)


def fig118_snubber():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 28, "RC-снабер: гасить стрибок напруги паралельно ключу", 14.5, INK, "middle", "bold")
    # симістор з паралельним RC
    cx = 250
    s += _triac_sym(cx, 175, INK)
    s += line(cx, 175 - 42, cx, 90, INK, 2) + text(cx, 82, "до мережі/навантаження", 9.5, INK, "middle")
    s += line(cx, 175 + 42, cx, 260, INK, 2)
    # паралельна гілка RC
    bx = cx + 130
    s += line(cx, 100, bx, 100, INK, 2)
    s += line(bx, 100, bx, 130, INK, 2)
    s += _res_v(bx, 152, 44, 14, INK, "R (десятки Ом)")
    s += line(bx, 174, bx, 190, INK, 2)
    s += _cap_v(bx, 200, 7, 16, INK, "C (~0.1 мкФ)")
    s += line(bx, 216, bx, 250, INK, 2)
    s += line(bx, 250, cx, 250, INK, 2)
    s += rect(bx - 60, 120, 130, 100, "none", GREEN, 1.4, 8)
    s += text(bx + 4, 116, "снабер", 10, GREEN, "start", "bold")
    # пояснення праворуч
    s += rect(450, 80, 290, 180, "#ffffff", "#c9d3dc", 1.4, 8)
    s += text(595, 104, "що робить снабер", 12, INK, "middle", "bold")
    lines = ["C приймає різкий стрибок напруги,",
             "сповільнюючи dv/dt на ключі;",
             "R обмежує струм розряду C",
             "у момент вмикання (щоб не бити",
             "ключ голкою струму);",
             "разом — обмежують і dv/dt, і di/dt."]
    y = 130
    for ln in lines:
        s += text(595, y, ln, 10, INK, "middle")
        y += 22
    s += text(W / 2, H - 10,
              "Конденсатор не дає напрузі стрибнути миттєво (§2.1: U на C не змінюється стрибком), а резистор стримує струм його розряду. Це той самий RC-снабер, що й на DC-контактах (§2.2.5), лише розрахований на мережу.",
              9, GREY, "middle", style="italic")
    save("fig-11-8-2-snubber.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Тема 2.11.9 — безпека
# ─────────────────────────────────────────────────────────────────────────────
def fig119_defense_layers():
    W, H = 860, 320
    s = header(W, H)
    s += text(W / 2, 28, "Рубежі захисту між розеткою і платою", 16, INK, "middle", "bold")
    stages = [
        ("розетка", "~230 В", "#f6dede", RED),
        ("запобіжник", "рве при\nнадструмі", "#fff3b0", SUN),
        ("варистор (MOV)", "зрізає\nкидки напруги", "#fff3b0", SUN),
        ("ізоляція", "оптопара /\nтрансформатор", "#e3edfb", BLUE),
        ("логіка", "3.3 В,\nбезпечно", "#eef6ef", GREEN),
    ]
    bw, gap, by, bh = 140, 28, 90, 110
    x = 30
    centers = []
    for name, sub, fill, col in stages:
        s += rect(x, by, bw, bh, fill, col, 1.8, 10)
        s += text(x + bw / 2, by + 28, name, 12, col, "middle", "bold")
        for k, ln in enumerate(sub.split("\n")):
            s += text(x + bw / 2, by + 56 + k * 18, ln, 10, INK, "middle")
        centers.append(x + bw / 2)
        x += bw + gap
    for i in range(len(centers) - 1):
        s += arrow(centers[i] + bw / 2, by + bh / 2, centers[i + 1] - bw / 2, by + bh / 2, GREY, 2)
    # підписи зон
    s += line(30 + 3 * (bw + gap) - gap / 2, by - 10, 30 + 3 * (bw + gap) - gap / 2, by + bh + 30, INK, 1.4, "5 4")
    s += text(30 + 1.5 * (bw + gap), by + bh + 24, "бік мережі — небезпечно", 10.5, RED, "middle", "bold")
    s += text(30 + 4 * (bw + gap) - bw / 2, by + bh + 24, "бік логіки — безпечно", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 10,
              "Жоден рубіж не зайвий: запобіжник проти струму, варистор проти сплесків, ізоляція проти контакту. Лише за ними починається світ безпечної логіки.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-9-1-defense-layers.svg", s)


def fig119_one_hand():
    W, H = 760, 320
    s = header(W, H)
    s += text(W / 2, 28, "Правило однієї руки: не давати струму шляху крізь серце", 14.5, INK, "middle", "bold")

    def body(cx, cy):
        t = circle(cx, cy - 70, 16, "#fde7c8", COPP, 1.8)         # голова
        t += rect(cx - 22, cy - 54, 44, 84, "#fde7c8", COPP, 1.8, 10)  # тулуб
        t += circle(cx, cy - 16, 7, "#f3a6a6", RED, 1.6)          # серце
        t += text(cx, cy - 12, "♥", 10, RED, "middle")
        t += line(cx, cy + 30, cx - 14, cy + 90, COPP, 5)         # ноги
        t += line(cx, cy + 30, cx + 14, cy + 90, COPP, 5)
        return t

    # ліворуч — погано (дві руки)
    s += _frame(40, 56, 320, 240, "ОБИДВІ руки → погано")
    s += body(150, 150)
    s += line(150 - 22, 150 - 40, 110, 150 + 10, COPP, 5)   # ліва рука
    s += line(150 + 22, 150 - 40, 190, 150 + 10, COPP, 5)   # права рука
    s += plus(110, 150 + 16, 9, RED, 2) + text(96, 150 + 40, "фаза", 9, RED, "middle", "bold")
    s += minus(190, 150 + 16, 9, BLUE, 2) + text(206, 150 + 40, "земля", 9, BLUE, "middle", "bold")
    # шлях струму крізь серце
    s += _poly([(110, 150 + 16), (135, 150 - 16), (165, 150 - 16), (190, 150 + 16)], RED, 2.4, "4 3")
    s += text(150, 150 - 40, "струм крізь серце!", 9.5, RED, "middle", "bold")
    s += text(150, 280, "рука–рука = найгірший шлях", 9.5, RED, "middle", "bold")
    # праворуч — краще (одна рука)
    s += _frame(400, 56, 320, 240, "ОДНА рука → краще")
    s += body(540, 150)
    s += line(540 - 22, 150 - 40, 500, 150 + 10, COPP, 5)   # ліва рука працює
    # права рука за спиною (в кишені)
    s += line(540 + 22, 150 - 40, 560, 150 - 6, COPP, 5)
    s += text(575, 150 - 4, "рука в кишені", 8.5, GREEN, "start", "bold")
    s += plus(500, 150 + 16, 9, RED, 2) + text(486, 150 + 40, "торкнувся", 9, RED, "middle")
    s += text(540, 280, "немає замкненого кола крізь тіло", 9.5, GREEN, "middle", "bold")
    s += text(W / 2, H - 8,
              "Працюй під напругою однією рукою, другу — за спину. Тоді навіть випадковий дотик не дасть струму пройти від руки до руки крізь грудну клітку.",
              9.5, GREY, "middle", style="italic")
    save("fig-11-9-2-one-hand.svg", s)


def fig119_mov_fuse():
    W, H = 760, 300
    s = header(W, H)
    s += text(W / 2, 28, "Запобіжник і варистор: різні біди — різні рубежі", 15, INK, "middle", "bold")
    # ліворуч — запобіжник проти надструму
    s += _frame(40, 56, 320, 220, "запобіжник — проти НАДСТРУМУ")
    s += line(70, 130, 130, 130, INK, 2)
    s += rect(130, 122, 90, 16, "#ffffff", INK, 1.6) + text(175, 134, "плавка", 8.5, INK, "middle")
    s += line(220, 130, 290, 130, INK, 2)
    s += arrow(175, 160, 175, 142, RED, 2) + text(175, 178, "забагато струму → згоряє → розрив", 8.5, RED, "middle", "bold")
    s += text(200, 210, "захищає від короткого", 9.5, INK, "middle")
    s += text(200, 230, "замикання і перевантаження", 9.5, INK, "middle")
    s += text(200, 254, "(струм)", 9, GREY, "middle", style="italic")
    # праворуч — варистор проти перенапруги
    s += _frame(400, 56, 320, 220, "варистор — проти ПЕРЕНАПРУГИ")
    # символ варистора: резистор з косою рискою
    s += line(530, 100, 530, 130, INK, 2) + text(530, 94, "фаза", 9, RED, "middle")
    s += rect(516, 130, 28, 50, "#ffffff", INK, 1.6)
    s += line(508, 184, 552, 138, INK, 1.6)
    s += text(560, 158, "MOV", 9.5, INK, "start", "bold")
    s += line(530, 180, 530, 210, INK, 2) + text(530, 226, "нейтраль", 9, INK, "middle")
    s += text(620, 130, "кидок 1000+ В →", 8.5, BLUE, "middle", "bold")
    s += text(620, 146, "опір падає →", 8.5, BLUE, "middle")
    s += text(620, 162, "поглинає енергію", 8.5, BLUE, "middle")
    s += text(560, 250, "захищає від блискавки й сплесків", 9, GREY, "middle", style="italic")
    s += text(W / 2, H - 8,
              "Запобіжник стежить за струмом і рве коло, коли його забагато. Варистор стежить за напругою й «коротить» кидок, поки той не дійшов до плати. Часто стоять разом — варистор за запобіжником.",
              9, GREY, "middle", style="italic")
    save("fig-11-9-3-mov-fuse.svg", s)


if __name__ == "__main__":
    # історія до розділу
    fig_t0_timeline()
    fig_t0_thyratron_vs_scr()
    # 2.11.1
    fig111_bipolar_sine()
    fig111_three_problems()
    fig111_isolation_barrier()
    # 2.11.2
    fig112_pnpn_two_bjt()
    fig112_latch_loop()
    fig112_holding_current()
    fig112_iv_curve()
    fig112_half_wave_circuit()
    # 2.11.3
    fig113_two_scr()
    fig113_both_halves()
    fig113_quadrants()
    fig113_diac()
    # 2.11.4
    fig114_firing_angle()
    fig114_power_vs_angle()
    fig114_lamp_vs_smps()
    # 2.11.5
    fig115_random_vs_zero()
    fig115_zero_detector()
    fig115_burst_control()
    # 2.11.6
    fig116_ssr_inside()
    fig116_emr_vs_ssr()
    # 2.11.7
    fig117_hybrid()
    fig117_mosfet_vs_igbt()
    # 2.11.8
    fig118_dvdt_selftrigger()
    fig118_snubber()
    # 2.11.9
    fig119_defense_layers()
    fig119_one_hand()
    fig119_mov_fuse()
    print("done")
