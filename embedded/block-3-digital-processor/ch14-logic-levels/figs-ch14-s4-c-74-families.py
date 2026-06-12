# -*- coding: utf-8 -*-
"""
Окремий генератор SVG для 🔌-вставки «Серія 74» (до теми 3.1.4, Модуль 3).
Самодостатній: палітра й хелпери скопійовані зі стилю figs.py розділу
(AUTHORING §9), щоб не чіпати головний figs.py. Вивід → ./img/.

Фігури нумеруються як у вставках (Рис. 3.1.4c.k):
  fig-14-4c-1-name-decoder.svg   — анатомія позначення «74HCT04»
  fig-14-4c-2-hct-window.svg     — чому HCT «розуміє» 5-вольтовий TTL (шкала рівнів)
  fig-14-4c-3-dip-wiring.svg     — DIP-14 розпіновка й підключення гекс-інвертора
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (як у figs.py розділу) ───────────────────────────────────────────
RED   = "#c0271e"   # HIGH / '1'
BLUE  = "#1f47b5"   # LOW / '0'
GREEN = "#1f8a3b"   # чисте / «спрацювало»
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
PALE_R = "#f6dcd9"  # бліда заливка «1»
PALE_B = "#dfe6f6"  # бліда заливка «0»
PALE_G = "#dcefe0"
PALE_A = "#f4ecd4"
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.1.4c.1 — анатомія позначення «74HCT04»
# ─────────────────────────────────────────────────────────────────────────────
def fig_name_decoder():
    W, H = 760, 430
    s = header(W, H)
    s += text(W / 2, 30, "Як читати позначення: SN 74 HCT 04 N", 19, INK, "middle", "bold")
    s += text(W / 2, 52, "одне ім'я несе чотири різні відповіді", 14, GREY, "middle", "normal", "italic")

    # велике позначення — кольорові блоки-поля
    y0 = 78
    boxh = 46
    fields = [
        ("SN",  72, GREY,  PALE_A, "виробник"),
        ("74",  64, BLUE,  PALE_B, "темп. серія"),
        ("HCT", 96, RED,   PALE_R, "сімейство"),
        ("04",  64, GREEN, PALE_G, "функція"),
        ("N",   54, INK,   FAINT,  "корпус"),
    ]
    x = 150
    centers = []
    for label, w, col, fill, _cap in fields:
        s += rect(x, y0, w, boxh, fill, col, 2.4, 6)
        s += text(x + w / 2, y0 + 31, label, 26, col, "middle", "bold")
        centers.append((x + w / 2, w, col, fill))
        x += w + 8
    block_right = x - 8

    # розкладені пояснення під кожним полем
    rows = [
        # (центр-індекс, заголовок, рядки опису)
        (0, "Префікс виробника",
            ["SN — Texas Instruments, CD — колишній RCA,",
             "MC — Motorola/onsemi. Те саме «тіло» —",
             "різні літери. Для логіки несуттєвий."]),
        (1, "Температурна серія",
            ["74 — комерційна, 0…+70 °C (наш випадок).",
             "54 — військова, −55…+125 °C, той самий",
             "кристал у суворішому корпусі та відборі."]),
        (2, "Логічне сімейство  ←  головне",
            ["Задає рівні, швидкість, живлення:",
             "HC — CMOS 2–6 В; HCT — HC із TTL-входом;",
             "LVC — швидке CMOS 1.65–3.6 В, вхід до 5 В."]),
        (3, "Код функції",
            ["Що всередині: 04 — шість інверторів,",
             "00 — чотири 2-вх. І-НЕ, 595 — зсувний",
             "регістр. Код однаковий у всіх сімействах."]),
        (4, "Суфікс корпусу",
            ["N — DIP (під пайку в плату/панельку),",
             "D — SO, PW — TSSOP (дрібні, під SMD).",
             "Лише форма; логіка та сама."]),
    ]
    # з'єднальні лінії-«вусики» від поля до картки опису
    card_y = 168
    card_w = 222
    card_h = 78
    cols = 3
    gap_x = (W - 40 - card_w * cols) / (cols - 1)
    positions = []
    for i in range(len(rows)):
        col_i = i % cols
        row_i = i // cols
        cx = 20 + col_i * (card_w + gap_x)
        cy = card_y + row_i * (card_h + 22)
        positions.append((cx, cy))

    for (idx, title, descr), (cx, cy) in zip(rows, positions):
        fc = centers[idx]
        col = fc[2]
        # картка
        s += rect(cx, cy, card_w, card_h, "#ffffff", col, 1.8, 6)
        s += text(cx + 10, cy + 21, title, 13.5, col, "start", "bold")
        for j, ln in enumerate(descr):
            s += text(cx + 10, cy + 39 + j * 16, ln, 12, INK, "start")
        # вусик від поля вниз до верху картки (лише для першого ряду — щоб не плутати)
        if cy < card_y + card_h:
            s += line(fc[0], y0 + boxh, fc[0], y0 + boxh + 8, col, 1.4)
            s += arrow(fc[0], y0 + boxh + 8, cx + card_w / 2, cy - 2, col, 1.4, "3,3")

    # підказка-правило знизу
    s += rect(20, H - 34, W - 40, 26, PALE_G, GREEN, 1.4, 6)
    s += text(W / 2, H - 16,
              "Правило: код функції (04) однаковий скрізь — змінюй літери сімейства, "
              "щоб обрати рівні й швидкість, не змінюючи логіку.",
              12.5, GREEN, "middle", "bold")
    save("fig-14-4c-1-name-decoder.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.1.4c.2 — чому HCT «розуміє» 5-вольтовий TTL (вертикальна шкала рівнів)
# ─────────────────────────────────────────────────────────────────────────────
def fig_hct_window():
    W, H = 760, 500
    s = header(W, H)
    s += text(W / 2, 28, "Чому HCT «розуміє» TTL, а чистий HC — ні", 19, INK, "middle", "bold")
    s += text(W / 2, 49, "усе вирішує висота вхідного порога «1» (VIH)", 14, GREY, "middle", "normal", "italic")

    # вертикальна вісь напруги 0..5 В
    ax = 120
    top, bot = 86, 408
    vmax = 5.0

    def Y(v):
        return bot - (v / vmax) * (bot - top)

    s += line(ax, top - 8, ax, bot, INK, 2)
    s += arrow(ax, top, ax, top - 22, INK, 2)
    s += text(ax - 12, top - 16, "В", 14, INK, "end", "bold")
    for v in range(0, 6):
        s += line(ax - 5, Y(v), ax, Y(v), INK, 1.6)
        s += text(ax - 10, Y(v) + 4, f"{v}.0", 12, INK, "end")

    # ── колонка 1: що ВИДАЄ 5 В TTL-вихід ────────────────────────────────────
    c1 = 188
    cw = 92
    # «1» TTL: від VOH(min)=2.4 до 5 (гарантований діапазон зверху)
    s += rect(c1, Y(5.0), cw, Y(2.4) - Y(5.0), PALE_R, RED, 1.6, 3)
    s += line(c1, Y(2.4), c1 + cw, Y(2.4), RED, 2.2)
    s += text(c1 + cw / 2, Y(2.4) - 6, "VOH min 2.4", 12, RED, "middle", "bold")
    s += text(c1 + cw / 2, (Y(5.0) + Y(2.4)) / 2 + 4, "«1»", 15, RED, "middle", "bold")
    # «0» TTL: 0..0.4
    s += rect(c1, Y(0.4), cw, Y(0.0) - Y(0.4), PALE_B, BLUE, 1.6, 3)
    s += text(c1 + cw / 2, Y(0.2) + 4, "«0»", 13, BLUE, "middle", "bold")
    s += text(c1 + cw / 2, bot + 22, "що ВИДАЄ", 12.5, INK, "middle", "bold")
    s += text(c1 + cw / 2, bot + 38, "5 В TTL-вихід", 12.5, INK, "middle")
    s += text(c1 + cw / 2, bot + 54, "(VOH гарантує", 11, GREY, "middle")
    s += text(c1 + cw / 2, bot + 68, "лише 2.4 В!)", 11, GREY, "middle")

    # ── колонка 2: що ВИМАГАЄ чистий HC-вхід ─────────────────────────────────
    c2 = 360
    s += rect(c2, Y(5.0), cw, Y(3.5) - Y(5.0), PALE_R, RED, 1.6, 3)
    s += line(c2, Y(3.5), c2 + cw, Y(3.5), RED, 2.6)
    s += text(c2 + cw / 2, Y(3.5) - 6, "VIH 3.5", 12, RED, "middle", "bold")
    s += text(c2 + cw / 2, (Y(5.0) + Y(3.5)) / 2 + 4, "«1»", 15, RED, "middle", "bold")
    s += rect(c2, Y(1.5), cw, Y(0.0) - Y(1.5), PALE_B, BLUE, 1.6, 3)
    s += text(c2 + cw / 2, Y(0.75) + 4, "«0»", 13, BLUE, "middle", "bold")
    s += text(c2 + cw / 2, bot + 22, "що ВИМАГАЄ", 12.5, INK, "middle", "bold")
    s += text(c2 + cw / 2, bot + 38, "вхід 74HC", 12.5, INK, "middle")

    # стрілка-провал: TTL 2.4 не дотягує до HC 3.5
    gx = c2 + cw + 18
    s += arrow(gx, Y(2.4), gx, Y(3.5), RED, 2.4)
    s += text(gx + 6, (Y(2.4) + Y(3.5)) / 2 + 4, "провал", 12, RED, "start", "bold")
    s += text(gx + 6, (Y(2.4) + Y(3.5)) / 2 + 19, "1.1 В", 11.5, RED, "start")
    # зона небезпеки між 2.4 і 3.5 на колонці HC
    s += rect(c2, Y(3.5), cw, Y(2.4) - Y(3.5), PALE_A, AMBER, 1.2, 3)
    s += text(c2 + cw / 2, (Y(3.5) + Y(2.4)) / 2 + 4, "??", 14, AMBER, "middle", "bold")

    # ── колонка 3: що ВИМАГАЄ HCT-вхід ───────────────────────────────────────
    c3 = 560
    s += rect(c3, Y(5.0), cw, Y(2.0) - Y(5.0), PALE_R, RED, 1.6, 3)
    s += line(c3, Y(2.0), c3 + cw, Y(2.0), RED, 2.6)
    s += text(c3 + cw / 2, Y(2.0) - 6, "VIH 2.0", 12, RED, "middle", "bold")
    s += text(c3 + cw / 2, (Y(5.0) + Y(2.0)) / 2 + 4, "«1»", 15, RED, "middle", "bold")
    s += rect(c3, Y(0.8), cw, Y(0.0) - Y(0.8), PALE_B, BLUE, 1.6, 3)
    s += text(c3 + cw / 2, Y(0.4) + 4, "«0»", 12, BLUE, "middle", "bold")
    s += text(c3 + cw / 2, bot + 22, "що ВИМАГАЄ", 12.5, INK, "middle", "bold")
    s += text(c3 + cw / 2, bot + 38, "вхід 74HCT", 12.5, GREEN, "middle", "bold")

    # зелений запас: від TTL 2.4 до HCT 2.0 — дотягує
    s += rect(c3, Y(2.4), cw, Y(2.0) - Y(2.4), PALE_G, GREEN, 1.2, 3)
    s += line(c3, Y(2.4), c3 + cw, Y(2.4), GREEN, 1.6, "3,3")
    s += text(c3 + cw / 2, (Y(2.4) + Y(2.0)) / 2 + 4, "запас", 11, GREEN, "middle", "bold")

    # горизонтальний рівень-«нитка» VOH 2.4 через усі колонки
    s += line(c1 + cw, Y(2.4), c3, Y(2.4), GREY, 1.4, "2,4")

    save("fig-14-4c-2-hct-window.svg", s)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 3.1.4c.3 — DIP-14 розпіновка гекс-інвертора 74x04 + підключення
# ─────────────────────────────────────────────────────────────────────────────
def fig_dip_wiring():
    W, H = 760, 440
    s = header(W, H)
    s += text(W / 2, 28, "DIP-14 «семишник» 74×04: розпіновка й підключення", 18, INK, "middle", "bold")
    s += text(W / 2, 48, "шість інверторів в одному корпусі — обираємо один", 13.5, GREY, "middle", "normal", "italic")

    # корпус
    bx, by, bw, bh = 250, 78, 170, 300
    s += rect(bx, by, bw, bh, "#f4f4f4", INK, 2.4, 8)
    # ключ-виїмка зверху
    s += f'<path d="M {bx + bw/2 - 16:.1f} {by:.1f} a16,16 0 0 0 32,0" fill="#ffffff" stroke="{INK}" stroke-width="2"/>\n'
    s += text(bx + bw / 2, by + 150, "74×04", 22, GREY, "middle", "bold")
    s += text(bx + bw / 2, by + 172, "(×04 = HC/HCT/LVC)", 11.5, GREY, "middle")

    # піни: 7 ліворуч (1..7 згори вниз), 7 праворуч (14..8 згори вниз)
    npins = 7
    pin_y0 = by + 30
    pin_dy = (bh - 60) / (npins - 1)
    pin_len = 22
    left_labels = ["1A", "1Y", "2A", "2Y", "3A", "3Y", "GND"]
    right_labels = ["Vcc", "6A", "6Y", "5A", "5Y", "4A", "4Y"]
    left_nums = [1, 2, 3, 4, 5, 6, 7]
    right_nums = [14, 13, 12, 11, 10, 9, 8]

    left_xy = {}
    right_xy = {}
    for i in range(npins):
        y = pin_y0 + i * pin_dy
        # ліво
        s += line(bx - pin_len, y, bx, y, INK, 2)
        s += rect(bx - pin_len - 4, y - 5, 6, 10, INK, INK, 1)
        s += text(bx - 6, y - 6, str(left_nums[i]), 10.5, GREY, "end")
        s += text(bx + 8, y + 4, left_labels[i], 12.5, INK, "start", "bold")
        left_xy[left_labels[i]] = (bx - pin_len - 4, y)
        # право
        s += line(bx + bw, y, bx + bw + pin_len, y, INK, 2)
        s += rect(bx + bw + pin_len - 2, y - 5, 6, 10, INK, INK, 1)
        s += text(bx + bw + 6, y - 6, str(right_nums[i]), 10.5, GREY, "start")
        s += text(bx + bw - 8, y + 4, right_labels[i], 12.5, INK, "end", "bold")
        right_xy[right_labels[i]] = (bx + bw + pin_len + 4, y)

    # позначка 1-го піна
    s += circle(bx + 16, pin_y0, 5, "none", INK, 1.6)

    # один інвертор-трикутник усередині (між 1A->1Y) як натяк
    ix = bx + bw / 2
    iy1 = pin_y0
    iy2 = pin_y0 + pin_dy
    s += f'<path d="M {ix-20:.1f} {iy1-9:.1f} L {ix-20:.1f} {iy2+9:.1f} L {ix+18:.1f} {(iy1+iy2)/2:.1f} Z" fill="#ffffff" stroke="{GREEN}" stroke-width="1.8"/>\n'
    s += circle(ix + 22, (iy1 + iy2) / 2, 3.4, "#ffffff", GREEN, 1.8)

    # ── живлення ──────────────────────────────────────────────────────────────
    vx, vy = right_xy["Vcc"]
    s += line(vx, vy, vx + 70, vy, RED, 2.4)
    s += line(vx + 70, vy, vx + 70, 70, RED, 2.4)
    s += text(vx + 74, 66, "Vcc  (3.3 чи 5 В)", 13, RED, "start", "bold")
    s += text(vx + 6, vy - 8, "пін 14", 10.5, GREY, "start")

    gx, gy = left_xy["GND"]
    s += line(gx, gy, gx - 70, gy, BLUE, 2.4)
    s += line(gx - 70, gy, gx - 70, 396, BLUE, 2.4)
    s += line(gx - 92, 396, gx - 48, 396, BLUE, 2.6)
    s += line(gx - 84, 402, gx - 56, 402, BLUE, 2.6)
    s += line(gx - 77, 408, gx - 63, 408, BLUE, 2.6)
    s += text(gx - 70, 426, "GND (пін 7)", 12.5, BLUE, "middle", "bold")

    # ── конденсатор розв'язки 0.1 мкФ між Vcc і GND, біля чипа ─────────────────
    capx = vx + 70
    capy = 110
    s += line(capx, 70, capx, capy, RED, 2)
    s += line(capx - 12, capy, capx + 12, capy, INK, 2.4)
    s += line(capx - 12, capy + 7, capx + 12, capy + 7, INK, 2.4)
    s += line(capx, capy + 7, capx, capy + 40, BLUE, 2)
    s += line(capx, capy + 40, gx - 70, capy + 40, BLUE, 2)
    s += text(capx + 8, capy + 2, "0.1 мкФ", 12, INK, "start", "bold")
    s += text(capx + 8, capy + 17, "розв'язка", 11, GREY, "start")

    # ── приклад: вхід 1A через підтяжку, вихід 1Y на світлодіод/далі ──────────
    ax_, ay = left_xy["1A"]
    s += arrow(ax_ - 96, ay, ax_, ay, INK, 2)
    s += text(ax_ - 100, ay - 8, "вхід 1A", 12.5, INK, "end", "bold")
    s += text(ax_ - 100, ay + 14, "(сигнал; не лишай", 10.5, GREY, "end")
    s += text(ax_ - 100, ay + 27, "висіти — підтяжка!)", 10.5, GREY, "end")

    yx, yy = left_xy["1Y"]
    s += arrow(yx, yy, yx - 96, yy, GREEN, 2.2)
    s += text(yx - 100, yy + 4, "вихід 1Y = NOT(1A)", 12.5, GREEN, "end", "bold")

    # підпис-зведення «перший байт» знизу праворуч
    box_x, box_y = vx + 70, 150
    s += rect(box_x, box_y, 230, 168, "#ffffff", GREY, 1.4, 6)
    s += text(box_x + 12, box_y + 22, "«Перший байт»", 13.5, INK, "start", "bold")
    lines = [
        "1. Vcc → пін 14, GND → пін 7.",
        "2. 0.1 мкФ між ними, впритул.",
        "3. Сигнал → 1A (пін 1).",
        "4. Знімай 1Y (пін 2): це NOT.",
        "5. Невжиті входи (2A…6A) —",
        "    на GND чи Vcc, не висіти.",
        "6. Vcc обох чипів однакова —",
        "    або став зсувач рівня.",
    ]
    for j, ln in enumerate(lines):
        s += text(box_x + 12, box_y + 44 + j * 15.5, ln, 11.5, INK, "start")

    save("fig-14-4c-3-dip-wiring.svg", s)


if __name__ == "__main__":
    fig_name_decoder()
    fig_hct_window()
    fig_dip_wiring()
    print("done.")
