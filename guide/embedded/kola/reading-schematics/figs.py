# -*- coding: utf-8 -*-
"""Фігури до статті «Як читати схему».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Символи схеми малюються лінійними примітивами svgkit; рамки з текстом —
через textbox()/fitbox(), тож написи гарантовано не вилазять за межі."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

RAIL_SW = 3.0          # шина живлення / земля
WIRE_SW = 2.0          # звичайний провід


def wire(x1, y1, x2, y2, sw=WIRE_SW, color=INK):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" stroke-linecap="round"/>' % (x1, y1, x2, y2, color, sw))


def dot(cx, cy, r=3.2, color=INK):
    return circle(cx, cy, r, fill=color, stroke=color, sw=1)


# ── Символи (центр символу — навколо (cx,cy)) ───────────────────────────────
def sym_resistor_v(cx, cy, h=26):
    """Резистор вертикально (IEC-прямокутник), виводи зверху й знизу."""
    bw = 20
    return rect(cx - bw / 2, cy - h / 2, bw, h, fill=BG, stroke=INK, sw=2, rx=2)


def sym_resistor_h(cx, cy, w=46):
    """Резистор горизонтально (IEC-прямокутник)."""
    bh = 16
    return rect(cx - w / 2, cy - bh / 2, w, bh, fill=BG, stroke=INK, sw=2, rx=2)


def sym_ground(cx, cy):
    out = wire(cx, cy - 16, cx, cy)
    out += wire(cx - 13, cy, cx + 13, cy, sw=2.4)
    out += wire(cx - 8, cy + 5, cx + 8, cy + 5, sw=2.4)
    out += wire(cx - 3, cy + 10, cx + 3, cy + 10, sw=2.4)
    return out


def sym_cap(cx, cy):
    """Неполярний конденсатор, виводи зверху й знизу."""
    g = 4
    out = wire(cx - 14, cy - g, cx + 14, cy - g, sw=2.4)
    out += wire(cx - 14, cy + g, cx + 14, cy + g, sw=2.4)
    return out


def sym_button(cx, cy):
    """Кнопка: два контакти й місток над ними."""
    out = dot(cx, cy - 6, r=3) + dot(cx, cy + 6, r=3)
    out += wire(cx - 13, cy - 8, cx + 13, cy - 8, sw=2.2)
    out += wire(cx, cy - 8, cx, cy - 15, sw=2)
    return out


def sym_led(cx, cy, scale=1.0):
    """Світлодіод: трикутник + катод + дві стрілочки світла."""
    t = 14 * scale
    out = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#fff7e6" '
           'stroke="%s" stroke-width="2"/>'
           % (cx - t, cy - t, cx - t, cy + t, cx + t, cy, INK))
    out += wire(cx + t, cy - t, cx + t, cy + t, sw=2.4)
    out += arrow(cx + t - 2, cy - t + 2, cx + t + 6, cy - t - 6, color=POS, sw=1.5)
    out += arrow(cx + t + 5, cy - t + 5, cx + t + 13, cy - t - 3, color=POS, sw=1.5)
    return out


# ── 1) Рецепт читання у п'ять кроків ────────────────────────────────────────
def fig_recipe():
    rows = [
        (POS,   "Живлення й земля",  "знайди +V (угорі) і GND (внизу) — зорієнтуйся"),
        (NEG,   "Блоки",            "виділи частини й що кожна РОБИТЬ"),
        (FIELD, "Потік сигналу",    "простеж шлях: вхід → обробка → вихід"),
        ("#e08030", "Вузол за вузлом", "читай з'єднання по одному, «зафарбовуючи» вузли"),
        (INK,   "Номінали",         "звір значення — вони підказують призначення"),
    ]
    W, H = 760, 360
    top, rh, gap = 78, 50, 8
    frags = []
    for i, (col, head, sub) in enumerate(rows):
        y = top + i * (rh + gap)
        frags.append(circle(70, y + rh / 2, 17, fill=col, stroke=INK, sw=2))
        frags.append(text(70, y + rh / 2 + 5, str(i + 1), size=14, color=BG, bold=True))
        frags.append(rect(100, y, W - 140, rh, fill=FILL, stroke=col, sw=1.6, rx=10))
        frags.append(text(120, y + 21, head, size=13, color=INK, anchor="start", bold=True))
        frags.append(text(120, y + 39, sub, size=11, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "recipe.svg"), W, H, *frags,
           title="Рецепт читання будь-якої схеми")


# ── 2) Спершу живлення й земля (повна схема-приклад) ─────────────────────────
def schematic(frags, ox=0):
    """Намалювати спільну схему «кнопка → МК → світлодіод» зі зсувом ox по X.
    Повертає координати ключових точок для підписів-винесень."""
    RAILY_T, RAILY_B = 110, 300
    xL, xR = 80 + ox, 700 + ox
    frags.append(wire(xL, RAILY_T, xR, RAILY_T, sw=RAIL_SW, color=POS))   # +V
    frags.append(wire(xL, RAILY_B, xR, RAILY_B, sw=RAIL_SW))             # GND
    frags.append(sym_ground(120 + ox, RAILY_B))

    # МК
    mcx = 405 + ox
    frags.append(rect(mcx - 75, 170, 150, 90, fill="#eef2fb", stroke=NEG, sw=2, rx=8))
    frags.append(text(mcx, 206, "МК", size=15, color=NEG, bold=True))
    frags.append(text(mcx, 228, "(контролер)", size=10, color=INK))
    frags.append(wire(mcx, 170, mcx, RAILY_T))
    frags.append(wire(mcx, 260, mcx, RAILY_B))

    # підтяжка + кнопка (вхід)
    px = 200 + ox
    frags.append(wire(px, RAILY_T, px, 150))
    frags.append(sym_resistor_v(px, 167, h=34))
    frags.append(text(px - 16, 172, "R↑", size=10, color=INK, anchor="end", bold=True))
    frags.append(wire(px, 184, px, 205))
    frags.append(dot(px, 205))
    frags.append(wire(px, 205, mcx - 75, 205))
    frags.append(text((px + mcx - 75) / 2, 197, "вхід", size=10, color=MUTED))
    frags.append(wire(px, 205, px, 224))
    frags.append(sym_button(px, 230))
    frags.append(wire(px, 242, px, RAILY_B))
    frags.append(text(px + 26, 244, "кнопка", size=10, color=MUTED, anchor="start"))

    # розв'язувальний конденсатор біля МК
    dcx = 300 + ox
    frags.append(wire(dcx, RAILY_T, dcx, 188))
    frags.append(sym_cap(dcx, 192))
    frags.append(wire(dcx, 196, dcx, RAILY_B))
    frags.append(text(dcx + 18, 192, "C", size=10, color=INK, anchor="start", bold=True))

    # вихід: резистор + світлодіод
    ledx = 600 + ox
    frags.append(wire(mcx + 75, 205, ledx - 60, 205))
    frags.append(sym_resistor_h(ledx - 35, 205, w=46))
    frags.append(text(ledx - 35, 192, "R", size=10, color=INK, bold=True))
    frags.append(text((mcx + 75 + ledx - 60) / 2, 197, "вихід", size=10, color=MUTED))
    frags.append(wire(ledx - 12, 205, ledx, 205))
    frags.append(sym_led(ledx + 6, 205, scale=0.8))
    frags.append(wire(ledx + 6, 217, ledx + 6, RAILY_B))
    frags.append(text(ledx + 26, 234, "LED", size=10, color=INK, anchor="start", bold=True))
    return dict(railT=RAILY_T, railB=RAILY_B, xR=xR, px=px, dcx=dcx, ledx=ledx, mcx=mcx)


def fig_power_first():
    W, H = 760, 360
    frags = []
    p = schematic(frags)
    # винесення на «+V» і «GND»
    frags.append(text(p["xR"], p["railT"] - 8, "+5 В", size=12, color=POS, anchor="end", bold=True))
    frags.append(text(p["mcx"] + 130, p["railB"] - 6, "GND", size=12, color=INK, anchor="end", bold=True))
    render(os.path.join(IMG, "power-first.svg"), W, H, *frags,
           title="Спершу знайди живлення й землю")


# ── 3) Потік сигналу: вхід → обробка → вихід ────────────────────────────────
def fig_signal_flow():
    W, H = 760, 250
    frags = []
    boxes = [(NEG, "ВХІД", "кнопка / давач"),
             (FIELD, "ОБРОБКА", "контролер"),
             ("#e08030", "ВИХІД", "світлодіод / мотор")]
    bw, bh, y = 190, 90, 110
    xs = [60, 285, 510]
    for (col, head, sub), x in zip(boxes, xs):
        frags.append(rect(x, y, bw, bh, fill=FILL, stroke=col, sw=2, rx=12))
        frags.append(text(x + bw / 2, y + 40, head, size=14, color=col, bold=True))
        frags.append(text(x + bw / 2, y + 64, sub, size=11, color=INK))
    for x, lab in ((xs[0] + bw, "сигнал"), (xs[1] + bw, "дія")):
        frags.append(arrow(x + 4, y + bh / 2, x + 31, y + bh / 2, color=INK, sw=2.4))
        frags.append(text(x + 18, y + bh / 2 - 10, lab, size=9, color=MUTED, italic=True))
    frags.append(text(W / 2, 235,
                      "Більшість схем читаються як розповідь: щось приходить, обробляється, щось відбувається.",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "signal-flow.svg"), W, H, *frags,
           title="Простеж сигнал зліва направо")


# ── 4) Чотири патерни ───────────────────────────────────────────────────────
def fig_patterns():
    W, H = 760, 400
    frags = []
    cw, ch = 330, 150
    cells = [(60, 80), (370, 80), (60, 250), (370, 250)]
    titles = [(NEG, "Дільник напруги"), (FIELD, "Струмообмежувальний R"),
              ("#e08030", "Підтяжка (pull-up)"), (POS, "Розв'язувальний C")]
    for (x, y), (col, t) in zip(cells, titles):
        frags.append(rect(x, y, cw, ch, fill=FILL, stroke=INK, sw=1.4, rx=10))
        frags.append(text(x + cw / 2, y + 24, t, size=12, color=col, bold=True))

    # 1 дільник
    x, y = 60, 80
    cx = x + 60
    frags.append(text(cx, y + 50, "+V", size=9.5, color=POS, bold=True))
    frags.append(wire(cx, y + 56, cx, y + 70))
    frags.append(sym_resistor_v(cx, y + 84, h=24))
    frags.append(wire(cx, y + 96, cx, y + 105))
    frags.append(dot(cx, y + 105, color=FIELD))
    frags.append(wire(cx, y + 105, cx + 40, y + 105, color="#cf8b5e"))
    frags.append(text(cx + 46, y + 109, "V_вих", size=9, color=FIELD, anchor="start", bold=True))
    frags.append(sym_resistor_v(cx, y + 122, h=24))
    frags.append(wire(cx, y + 105, cx, y + 110))
    frags.append(wire(cx, y + 134, cx, y + 140))
    frags.append(sym_ground(cx, y + 140))
    frags.append(text(x + 230, y + 80, "ділить напругу;", size=9.5, color=MUTED))
    frags.append(text(x + 230, y + 96, "читати давачі", size=9.5, color=MUTED))

    # 2 струмообмежувальний R
    x, y = 370, 80
    yy = y + 70
    frags.append(wire(x + 60, yy, x + 90, yy, color="#cf8b5e"))
    frags.append(sym_resistor_h(x + 113, yy, w=46))
    frags.append(text(x + 113, yy - 13, "R", size=11, color=INK, bold=True, italic=True))
    frags.append(wire(x + 136, yy, x + 165, yy, color="#cf8b5e"))
    frags.append(sym_led(x + 180, yy, scale=0.8))
    frags.append(text(x + 200, yy + 28, "перед LED", size=9.5, color=MUTED, anchor="start"))
    frags.append(text(x + cw / 2, y + 120, "тримає струм безпечним", size=9.5, color=MUTED))

    # 3 підтяжка
    x, y = 60, 250
    cx = x + 60
    frags.append(text(cx, y + 44, "+V", size=9.5, color=POS, bold=True))
    frags.append(wire(cx, y + 50, cx, y + 62))
    frags.append(sym_resistor_v(cx, y + 76, h=24))
    frags.append(wire(cx, y + 88, cx, y + 100))
    frags.append(dot(cx, y + 100))
    frags.append(wire(cx, y + 100, cx + 45, y + 100, color="#cf8b5e"))
    frags.append(text(cx + 51, y + 104, "→ вхід", size=9, color=MUTED, anchor="start"))
    frags.append(text(x + 240, y + 84, "тримає вхід у «1»,", size=9.5, color=MUTED))
    frags.append(text(x + 240, y + 100, "доки кнопка не дасть «0»", size=9.5, color=MUTED))

    # 4 розв'язувальний C
    x, y = 370, 250
    cx = x + 90
    frags.append(text(cx, y + 44, "+V", size=9.5, color=POS, bold=True))
    frags.append(wire(cx, y + 50, cx, y + 72))
    frags.append(sym_cap(cx, y + 78))
    frags.append(wire(cx, y + 84, cx, y + 100))
    frags.append(sym_ground(cx, y + 100))
    frags.append(text(x + 220, y + 78, "біля живлення чипа;", size=9.5, color=MUTED))
    frags.append(text(x + 220, y + 94, "згладжує стрибки", size=9.5, color=MUTED))

    render(os.path.join(IMG, "patterns.svg"), W, H, *frags,
           title="Упізнавайте знайомі патерни")


# ── 5) Наскрізний приклад (та сама схема + винесення-пояснення) ──────────────
def fig_worked():
    W, H = 760, 400
    frags = []
    p = schematic(frags)
    frags.append(text(p["xR"], p["railT"] - 8, "+5 В", size=11, color=POS, anchor="end", bold=True))
    notes = [
        (150, 345, p["px"], 188, "R↑ тримає вхід у «1»"),
        (270, 372, p["px"], 245, "кнопка дає вхід «0»"),
        (380, 345, p["dcx"], 196, "C згладжує живлення"),
        (610, 358, 565, 205, "R обмежує струм LED"),
    ]
    for tx, ty, ax, ay, lab in notes:
        frags.append(wire(tx, ty - 12, ax, ay, sw=1.4, color=MUTED))
        frags.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                     'stroke-width="1.4" marker-end="url(#arrow)"/>' % (tx, ty - 12, ax, ay, MUTED))
        frags.append(text(tx, ty, lab, size=9.5, color=INK, bold=True))
    render(os.path.join(IMG, "worked.svg"), W, H, *frags,
           title="Читаємо приклад: кнопка → МК → світлодіод")


# ══════════════════════════════════════════════════════════════════════════
#  ДЕТАЛЬНА стаття (reading-schematics-d): додаткові фігури
# ══════════════════════════════════════════════════════════════════════════

# ── D1) Анатомія позначення на схемі (refdes, номінал, піни, вивід) ──────────
def fig_anatomy():
    """Один резистор і одна мікросхема, розписані винесеннями: що є що."""
    W, H = 760, 400
    frags = []
    # --- резистор із повним обвісом ---
    rx, ry = 175, 150
    frags.append(wire(rx, ry - 55, rx, ry - 22))
    frags.append(sym_resistor_v(rx, ry, h=44))
    frags.append(wire(rx, ry + 22, rx, ry + 55))
    frags.append(dot(rx, ry - 55, r=3))
    frags.append(dot(rx, ry + 55, r=3))
    frags.append(text(rx - 30, ry - 14, "R7", size=13, color=NEG, anchor="end", bold=True))
    frags.append(text(rx + 30, ry + 4, "10k", size=13, color="#e08030", anchor="start", bold=True))
    frags.append(text(rx - 30, ry + 60, "1", size=10, color=MUTED, anchor="end"))
    frags.append(text(rx - 30, ry - 50, "2", size=10, color=MUTED, anchor="end"))
    # винесення до резистора
    def call(tx, ty, ax, ay, lab, col=INK):
        f = wire(tx, ty, ax, ay, sw=1.2, color=MUTED)
        f += text(tx, ty - 4 if ty < ay else ty + 12, lab, size=10, color=col, bold=True)
        return f
    frags.append(call(70, 120, rx - 28, ry - 12, "позначення", NEG))
    frags.append(text(70, 134, "(refdes)", size=9, color=MUTED, bold=False))
    frags.append(call(70, 300, rx + 26, ry + 2, "номінал", "#e08030"))
    frags.append(call(300, 300, rx, ry + 40, "вивід / контакт", INK))
    frags.append(text(300, 326, "(pin, вузол)", size=9, color=MUTED))
    # --- мікросхема (IC) ---
    ux, uy, uw, uh = 500, 110, 150, 180
    frags.append(rect(ux, uy, uw, uh, fill="#eef2fb", stroke=NEG, sw=2, rx=6))
    frags.append(text(ux + uw / 2, uy + 30, "U3", size=14, color=NEG, bold=True))
    frags.append(text(ux + uw / 2, uy + 50, "MCP6001", size=11, color=INK))
    pins_l = [("1", "IN−"), ("2", "IN+"), ("3", "GND")]
    pins_r = [("5", "OUT"), ("6", "V+"), ("7", "NC")]
    for i, (n, nm) in enumerate(pins_l):
        yy = uy + 80 + i * 32
        frags.append(wire(ux - 26, yy, ux, yy))
        frags.append(dot(ux - 26, yy, r=3))
        frags.append(text(ux - 30, yy - 3, n, size=9, color=MUTED, anchor="end"))
        frags.append(text(ux + 8, yy + 4, nm, size=10, color=INK, anchor="start"))
    for i, (n, nm) in enumerate(pins_r):
        yy = uy + 80 + i * 32
        frags.append(wire(ux + uw, yy, ux + uw + 26, yy))
        frags.append(dot(ux + uw + 26, yy, r=3))
        frags.append(text(ux + uw + 30, yy - 3, n, size=9, color=MUTED, anchor="start"))
        frags.append(text(ux + uw - 8, yy + 4, nm, size=10, color=INK, anchor="end"))
    frags.append(call(600, 355, ux + uw - 10, uy + 92, "назва виводу", INK))
    frags.append(text(600, 381, "(функція піна)", size=9, color=MUTED))
    frags.append(call(470, 355, ux + 4, uy + 108, "№ піна", MUTED))
    render(os.path.join(IMG, "anatomy.svg"), W, H, *frags,
           title="Анатомія позначення: як компонент підписаний на схемі")


# ── D2) Мітки вузлів, шини, off-page — як з'єднують без дротів ───────────────
def fig_labels_buses():
    W, H = 760, 380
    frags = []
    # (a) мітка вузла: два фрагменти з однаковою назвою SDA — електрично одне
    ay = 90
    frags.append(text(150, 58, "Мітка вузла (net label)", size=12, color=NEG, bold=True))
    frags.append(wire(60, ay, 130, ay))
    frags.append(dot(130, ay, r=3))
    frags.append(rect(130, ay - 12, 46, 24, fill="#fff7e6", stroke="#e08030", sw=1.5, rx=4))
    frags.append(text(153, ay + 5, "SDA", size=11, color="#e08030", bold=True))
    frags.append(rect(250, ay - 12, 46, 24, fill="#fff7e6", stroke="#e08030", sw=1.5, rx=4))
    frags.append(text(273, ay + 5, "SDA", size=11, color="#e08030", bold=True))
    frags.append(dot(296, ay, r=3))
    frags.append(wire(296, ay, 366, ay))
    frags.append(text(213, ay + 34, "однакова назва = один вузол,", size=9.5, color=MUTED))
    frags.append(text(213, ay + 48, "хоч дроту між ними немає", size=9.5, color=MUTED))

    # (b) шина: багато ліній зібрані в товсту
    by = 120
    frags.append(text(560, 58, "Шина (bus)", size=12, color=FIELD, bold=True))
    for i in range(4):
        yy = by + i * 16
        frags.append(wire(430, yy, 470, yy, sw=1.6))
        frags.append(text(424, yy + 4, "D%d" % i, size=9, color=MUTED, anchor="end"))
        frags.append(wire(470, yy, 500, by + 24, sw=1.4))
    frags.append(wire(500, by + 24, 620, by + 24, sw=5.0, color=FIELD))
    frags.append(text(560, by + 18, "D[0..3]", size=10, color=FIELD, bold=True))
    for i in range(4):
        yy = by + i * 16
        frags.append(wire(620, by + 24, 650, yy, sw=1.4))
        frags.append(wire(650, yy, 690, yy, sw=1.6))
    frags.append(text(560, by + 60, "жмут проводів — однією товстою лінією", size=9.5, color=MUTED))

    # (c) off-page / hierarchy: п'ятикутник-конектор
    oy = 250
    frags.append(text(200, 220, "Міжаркушевий конектор (off-page)", size=12, color=POS, bold=True))
    frags.append(wire(70, oy, 150, oy))
    # п'ятикутник, що вказує праворуч
    frags.append('<polygon points="150,%d 210,%d 234,%d 210,%d 150,%d" fill="#fdecea" '
                 'stroke="%s" stroke-width="1.8"/>' % (oy - 13, oy - 13, oy, oy + 13, oy + 13, POS))
    frags.append(text(186, oy + 5, "VBAT", size=10, color=POS, bold=True))
    frags.append(text(300, oy - 6, "той самий сигнал", size=9.5, color=MUTED, anchor="start"))
    frags.append(text(300, oy + 10, "виходить на інший аркуш", size=9.5, color=MUTED, anchor="start"))
    frags.append(text(300, oy + 26, "великого проєкту", size=9.5, color=MUTED, anchor="start"))
    # приймальний конектор на «іншому аркуші»
    frags.append('<polygon points="620,%d 560,%d 536,%d 560,%d 620,%d" fill="#fdecea" '
                 'stroke="%s" stroke-width="1.8"/>' % (oy - 13, oy - 13, oy, oy + 13, oy + 13, POS))
    frags.append(text(584, oy + 5, "VBAT", size=10, color=POS, bold=True))
    frags.append(wire(620, oy, 690, oy))
    frags.append(text(578, oy + 34, "аркуш 2", size=9, color=MUTED))
    render(os.path.join(IMG, "labels-buses.svg"), W, H, *frags,
           title="З'єднання без дротів: мітки, шини, міжаркушеві конектори")


# ── D3) Номінали не з голови: два виведення (дільник + rise-time підтяжки) ───
def fig_values_derivation():
    W, H = 760, 430
    frags = []
    # ЛІВО: дільник → формула
    frags.append(text(190, 58, "Дільник: номінал ⇄ напруга", size=12.5, color=NEG, bold=True))
    cx = 150
    frags.append(text(cx, 92, "+3.3 В", size=10, color=POS, bold=True))
    frags.append(wire(cx, 98, cx, 112))
    frags.append(sym_resistor_v(cx, 128, h=28))
    frags.append(text(cx + 26, 124, "R1 20k", size=10, color=INK, anchor="start"))
    frags.append(wire(cx, 142, cx, 158))
    frags.append(dot(cx, 158, color=FIELD))
    frags.append(wire(cx, 158, cx + 60, 158, color="#cf8b5e"))
    frags.append(text(cx + 66, 162, "V_вих", size=10, color=FIELD, anchor="start", bold=True))
    frags.append(sym_resistor_v(cx, 186, h=28))
    frags.append(text(cx + 26, 190, "R2 10k", size=10, color=INK, anchor="start"))
    frags.append(wire(cx, 158, cx, 172))
    frags.append(wire(cx, 200, cx, 214))
    frags.append(sym_ground(cx, 214))
    box = ["V_вих = Vжив · R2/(R1+R2)",
           "     = 3.3 · 10k/30k",
           "     = 1.10 В"]
    frags.append(fitbox(40, 250, 300, 90, "\n".join(box), size=12,
                        fill="#eef2fb", stroke=NEG, sw=1.5))
    frags.append(text(190, 360, "великі опори → малий струм витоку,", size=9.5, color=MUTED))
    frags.append(text(190, 376, "але чутливіші до навантаження входу", size=9.5, color=MUTED))

    # ПРАВО: rise-time підтяжки на шині I2C
    frags.append(text(560, 58, "Підтяжка: R ⇄ швидкодія", size=12.5, color="#e08030", bold=True))
    px = 520
    frags.append(text(px, 92, "+3.3 В", size=10, color=POS, bold=True))
    frags.append(wire(px, 98, px, 112))
    frags.append(sym_resistor_v(px, 128, h=28))
    frags.append(text(px + 26, 124, "Rp", size=10, color=INK, anchor="start"))
    frags.append(wire(px, 142, px, 168))
    frags.append(dot(px, 168, color="#cf8b5e"))
    frags.append(wire(px, 168, px + 90, 168, color="#cf8b5e"))
    frags.append(text(px + 96, 172, "лінія SCL/SDA", size=9, color=MUTED, anchor="start"))
    # ємність шини донизу
    frags.append(wire(px, 168, px, 190))
    frags.append(sym_cap(px, 196))
    frags.append(text(px + 20, 196, "C_шини", size=9, color=INK, anchor="start"))
    frags.append(wire(px, 200, px, 214))
    frags.append(sym_ground(px, 214))
    box2 = ["t_rise ≈ 0.85 · Rp · C",
            "300 нс = 0.85 · Rp · 400пФ",
            "Rp_max ≈ 880 Ом"]
    frags.append(fitbox(410, 250, 310, 90, "\n".join(box2), size=12,
                        fill="#fff7e6", stroke="#e08030", sw=1.5))
    frags.append(text(560, 360, "більший R економить струм, але фронт", size=9.5, color=MUTED))
    frags.append(text(560, 376, "повільніший — стеля залежить від швидкості шини", size=9, color=MUTED))
    render(os.path.join(IMG, "values-derivation.svg"), W, H, *frags,
           title="Номінал — це розрахунок: два приклади читання значень")


# ── D4) Розширений наскрізний приклад: LDO → MCU → давач I2C → MOSFET-ключ ──
def fig_worked_full():
    W, H = 900, 470
    frags = []
    RT, RB = 90, 410
    xL, xR = 60, 840
    # шини
    frags.append(wire(xL, RT, xR, RT, sw=RAIL_SW, color=POS))
    frags.append(wire(xL, RB, xR, RB, sw=RAIL_SW))
    frags.append(text(xR, RT - 8, "+3.3 В", size=12, color=POS, anchor="end", bold=True))
    frags.append(sym_ground(90, RB))
    frags.append(text(120, RB + 18, "GND", size=10, color=INK, anchor="start", bold=True))
    # блок LDO ліворуч (вхід живлення)
    lx = 120
    frags.append(rect(lx - 45, 150, 90, 70, fill=FILL, stroke=POS, sw=1.8, rx=6))
    frags.append(text(lx, 178, "LDO", size=12, color=POS, bold=True))
    frags.append(text(lx, 196, "5→3.3 В", size=9, color=INK))
    frags.append(text(lx, 132, "U1", size=10, color=NEG, bold=True))
    frags.append(wire(lx, 150, lx, RT))
    frags.append(wire(lx, 220, lx, RB))
    # вх. конденсатор і вих. конденсатор
    frags.append(wire(lx - 80, RT, lx - 80, 175))
    frags.append(sym_cap(lx - 80, 181))
    frags.append(wire(lx - 80, 185, lx - 80, RB))
    frags.append(text(lx - 76, 168, "C1", size=9, color=MUTED, anchor="start"))
    # МК у центрі
    mcx = 430
    frags.append(rect(mcx - 90, 150, 180, 180, fill="#eef2fb", stroke=NEG, sw=2, rx=8))
    frags.append(text(mcx, 178, "МК (U2)", size=14, color=NEG, bold=True))
    frags.append(text(mcx, 198, "ESP32", size=10, color=INK))
    frags.append(wire(mcx - 20, 150, mcx - 20, RT))
    frags.append(wire(mcx - 20, 330, mcx - 20, RB))
    # розв'язка біля МК
    frags.append(wire(mcx + 40, RT, mcx + 40, 138))
    frags.append(sym_cap(mcx + 40, 144))
    frags.append(wire(mcx + 40, 148, mcx + 40, 150))
    frags.append(text(mcx + 46, 140, "C4 100n", size=9, color=MUTED, anchor="start"))
    # I2C давач праворуч від МК, дві підтяжки
    sx = 690
    frags.append(rect(sx - 45, 150, 90, 70, fill=FILL, stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(sx, 178, "давач", size=11, color=FIELD, bold=True))
    frags.append(text(sx, 196, "U4 (I2C)", size=9, color=INK))
    frags.append(wire(sx, 150, sx, RT))
    frags.append(wire(sx, 220, sx, RB))
    # дві лінії I2C з підтяжками
    for k, (nm, yoff) in enumerate([("SDA", 250), ("SCL", 285)]):
        yy = yoff
        frags.append(wire(mcx + 90, yy, sx - 45, yy, color="#cf8b5e"))
        frags.append(text((mcx + 90 + sx - 45) / 2, yy - 6, nm, size=9, color="#e08030"))
        pux = mcx + 130 + k * 40
        frags.append(wire(pux, RT, pux, yy - 20))
        frags.append(sym_resistor_v(pux, yy - 34, h=22))
        frags.append(wire(pux, yy - 20, pux, yy))
        frags.append(dot(pux, yy))
    frags.append(text(mcx + 150, 232, "Rp ×2 (4.7k)", size=9, color=MUTED))
    # вихід: MOSFET-ключ на мотор/навантаження (низька сторона)
    qx = 690
    frags.append(wire(mcx + 90, 315, qx - 40, 315, color="#cf8b5e"))
    frags.append(text((mcx + 90 + qx - 40) / 2, 309, "GPIO→", size=9, color="#e08030"))
    # резистор у затвор
    frags.append(sym_resistor_h(qx - 22, 315, w=34))
    frags.append(text(qx - 22, 303, "Rg", size=9, color=INK))
    # символ навантаження (котушка-реле як прямокутник) + MOSFET-прямокутник
    frags.append(rect(qx - 5, 300, 34, 40, fill="#eef2fb", stroke=NEG, sw=1.6, rx=4))
    frags.append(text(qx + 12, 324, "Q1", size=9, color=NEG, bold=True))
    frags.append(wire(qx + 12, 300, qx + 12, 250))
    frags.append(rect(qx - 6, 218, 36, 30, fill=FILL, stroke="#e08030", sw=1.6, rx=4))
    frags.append(text(qx + 12, 237, "M", size=11, color="#e08030", bold=True))
    frags.append(wire(qx + 12, 218, qx + 12, RT))
    frags.append(wire(qx + 12, 340, qx + 12, RB))
    # flyback-діод паралельно навантаженню
    frags.append(text(qx + 40, 234, "навантаження", size=9, color=MUTED, anchor="start"))
    # підписи блоків унизу
    labels = [(lx, "① живлення"), (mcx, "② обробка"),
              ((mcx + sx) / 2, "③ шина I2C"), (qx + 10, "④ силовий вихід")]
    for x, lab in labels:
        frags.append(text(x, RB + 40, lab, size=10, color=INK, bold=True))
    render(os.path.join(IMG, "worked-full.svg"), W, H, *frags,
           title="Реальніша схема, прочитана за рецептом")


# ── D5) Від схеми до плати: схема → нетлист → PCB ────────────────────────────
def fig_schematic_to_pcb():
    W, H = 760, 300
    frags = []
    # три панелі-етапи + стрілки
    panels = [(40, NEG, "СХЕМА", "хто з ким\nз'єднаний (логіка)"),
              (290, "#e08030", "НЕТЛИСТ", "список вузлів\nі виводів (текст)"),
              (540, FIELD, "ПЛАТА", "де фізично\nлежить кожна деталь")]
    pw, ph, py = 180, 150, 80
    for x, col, head, sub in panels:
        frags.append(rect(x, py, pw, ph, fill=FILL, stroke=col, sw=1.8, rx=10))
        frags.append(text(x + pw / 2, py + 28, head, size=13, color=col, bold=True))
    # стрілки між панелями
    for x, lab in ((40 + pw, "анотація"), (290 + pw, "розведення")):
        frags.append(arrow(x + 6, py + ph / 2, x + 44, py + ph / 2, color=INK, sw=2.2))
        frags.append(text(x + 25, py + ph / 2 - 10, lab, size=9, color=MUTED, italic=True))
    # мінісхема в 1-й панелі
    x = 40
    frags.append(text(x + 55, py + 66, "+V", size=9, color=POS, bold=True))
    frags.append(wire(x + 55, py + 70, x + 55, py + 80))
    frags.append(sym_resistor_v(x + 55, py + 92, h=18))
    frags.append(wire(x + 55, py + 101, x + 55, py + 112))
    frags.append(dot(x + 55, py + 112, r=2.6, color=FIELD))
    frags.append(wire(x + 55, py + 112, x + 100, py + 112, color="#cf8b5e"))
    frags.append(text(x + 106, py + 116, "N1", size=9, color=FIELD, anchor="start", bold=True))
    frags.append(sym_led(x + 118, py + 112, scale=0.5))
    # нетлист-текст у 2-й панелі
    x = 290
    net = ["N1: R1.2  D1.1", "+V: R1.1  U2.8", "GND: D1.2 U2.4"]
    for i, ln in enumerate(net):
        frags.append(text(x + 16, py + 62 + i * 22, ln, size=10, color=INK, anchor="start"))
    # PCB у 3-й панелі: доріжки й падки
    x = 540
    frags.append(rect(x + 30, py + 55, 30, 20, fill="#d9e6d2", stroke=FIELD, sw=1.4, rx=2))
    frags.append(text(x + 45, py + 69, "R1", size=9, color=INK))
    frags.append(rect(x + 110, py + 95, 30, 20, fill="#d9e6d2", stroke=FIELD, sw=1.4, rx=2))
    frags.append(text(x + 125, py + 109, "D1", size=9, color=INK))
    frags.append(wire(x + 60, py + 65, x + 90, py + 65, sw=3, color="#b06a30"))
    frags.append(wire(x + 90, py + 65, x + 110, py + 100, sw=3, color="#b06a30"))
    frags.append(dot(x + 60, py + 65, r=3, color="#b06a30"))
    frags.append(dot(x + 110, py + 100, r=3, color="#b06a30"))
    frags.append(text(W / 2, py + ph + 34,
                      "Логіку з'єднань (схему) читають окремо від фізичного розташування (плати) — нетлист їх пов'язує.",
                      size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "schematic-to-pcb.svg"), W, H, *frags,
           title="Схема → нетлист → плата: три погляди на одне коло")


# ── Вставка comp-eda: конвеєр редактора схем і плат ─────────────────────────
def fig_eda_pipeline():
    """Наскрізний конвеєр EDA: схема → нетлист → плата → виробничі файли.
    Дві доріжки: ЛОГІКА (схема, refdes, нетлист, ERC) і ФІЗИКА (корпуси,
    ratsnest, доріжки, DRC) — зшиті нетлистом і refdes."""
    W, H = 820, 470
    frags = []
    # дві смуги-доріжки
    frags.append(rect(24, 60, W - 48, 150, fill="#eef4fb", stroke=NEG, sw=1.4, rx=12))
    frags.append(rect(24, 240, W - 48, 150, fill="#eef7ee", stroke=FIELD, sw=1.4, rx=12))
    frags.append(text(40, 82, "ЛОГІКА — редактор схеми", size=12, color=NEG, anchor="start", bold=True))
    frags.append(text(40, 262, "ФІЗИКА — редактор плати", size=12, color=FIELD, anchor="start", bold=True))

    # верхня доріжка: захоплення → refdes → нетлист → ERC
    top_y, bw, bh = 105, 150, 74
    xs = [50, 250, 450, 640]
    top = [
        ("Захоплення схеми", "символи з бібліотек,\nз'єднання в кола"),
        ("Анотація refdes", "R1, C1, U1 —\nунікальні мітки"),
        ("Нетлист", "список кіл:\nхто з ким з'єднаний"),
        ("ERC", "перевірка\nелектричних правил"),
    ]
    for i, (head, sub) in enumerate(top):
        x = xs[i]
        col = NEG if i < 3 else "#8e44ad"
        frags.append(rect(x, top_y, bw, bh, fill=BG, stroke=col, sw=1.8, rx=8))
        frags.append(text(x + bw / 2, top_y + 22, head, size=12, color=INK, bold=True))
        for j, ln in enumerate(sub.split("\n")):
            frags.append(text(x + bw / 2, top_y + 40 + j * 15, ln, size=9.5, color=MUTED))
        if i < 3:
            frags.append(arrow(x + bw, top_y + bh / 2, xs[i + 1], top_y + bh / 2, color=INK, sw=2))

    # нетлист «падає» вниз у фізику
    frags.append(arrow(xs[2] + bw / 2, top_y + bh, xs[2] + bw / 2, 240 + 34, color=POS, sw=2.4))
    frags.append(text(xs[2] + bw / 2 + 8, 226, "нетлист передається", size=10, color=POS, anchor="start", bold=True))

    # нижня доріжка: корпуси → ratsnest → доріжки → DRC
    bot_y = 285
    bot = [
        ("Прив'язка корпусів", "кожному символу —\nсвій footprint"),
        ("Ratsnest", "прямі «повітряні»\nлінії зв'язків"),
        ("Розведення", "доріжки замість\nповітряних ліній"),
        ("DRC", "перевірка\nправил плати"),
    ]
    for i, (head, sub) in enumerate(bot):
        x = xs[i]
        col = FIELD if i < 3 else "#8e44ad"
        frags.append(rect(x, bot_y, bw, bh, fill=BG, stroke=col, sw=1.8, rx=8))
        frags.append(text(x + bw / 2, bot_y + 22, head, size=12, color=INK, bold=True))
        for j, ln in enumerate(sub.split("\n")):
            frags.append(text(x + bw / 2, bot_y + 40 + j * 15, ln, size=9.5, color=MUTED))
        if i < 3:
            frags.append(arrow(x + bw, bot_y + bh / 2, xs[i + 1], bot_y + bh / 2, color=INK, sw=2))

    # виробничі файли на виході
    out_y = 410
    frags.append(fitbox(xs[2], out_y, bw + (xs[3] + bw - xs[2] - bw), 40,
                        "Вивід: BOM + Gerber", size=12, fill="#fdf3e6",
                        stroke="#e08030", bold=True))
    frags.append(arrow(xs[3] - 40, bot_y + bh, xs[2] + bw + 20, out_y, color="#e08030", sw=2))

    frags.append(text(W / 2, H - 12,
                      "Дві доріжки одного інструмента: логіку (що з'єднано) і фізику (де це лежить) зшивають нетлист і спільні refdes.",
                      size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "eda-pipeline.svg"), W, H, *frags,
           title="Конвеєр редактора схем і плат")


# ── Вставка comp-eda: refdes як спільний ключ логіки й фізики ────────────────
def fig_refdes_link():
    """Один refdes (R1) пов'язує символ на схемі, рядок у нетлисті й корпус
    на платі — три різні погляди на ту саму деталь."""
    W, H = 780, 300
    frags = []
    py, ph = 60, 190
    titles = ["Схема (символ)", "Нетлист (текст)", "Плата (корпус)"]
    xs = [30, 285, 540]
    pw = 220
    for i, t in enumerate(titles):
        frags.append(rect(xs[i], py, pw, ph, fill=FILL, stroke=LINE, sw=1.4, rx=10))
        frags.append(text(xs[i] + pw / 2, py + 22, t, size=12, color=INK, bold=True))

    # 1) символ резистора R1
    x = xs[0]
    cx = x + pw / 2
    frags.append(wire(cx, py + 45, cx, py + 70))
    frags.append(sym_resistor_v(cx, py + 95, h=40))
    frags.append(wire(cx, py + 115, cx, py + 140))
    frags.append(text(cx + 26, py + 92, "R1", size=13, color=POS, anchor="start", bold=True))
    frags.append(text(cx + 26, py + 110, "10k", size=10, color=MUTED, anchor="start"))
    frags.append(dot(cx, py + 70, r=2.8, color=INK))
    frags.append(text(cx - 30, py + 66, "N1", size=9, color=FIELD, anchor="end"))
    frags.append(dot(cx, py + 140, r=2.8, color=INK))
    frags.append(text(cx - 30, py + 145, "GND", size=9, color=MUTED, anchor="end"))

    # 2) нетлист-рядок
    x = xs[1]
    lines = ["N1:   R1.1  U1.7", "GND:  R1.2  U1.4", "...", "R1  →  R_0603", "value = 10k"]
    for i, ln in enumerate(lines):
        col = POS if "R1" in ln and i != 2 else INK
        frags.append(text(x + 18, py + 55 + i * 26, ln, size=11, color=col, anchor="start"))

    # 3) корпус на платі
    x = xs[2]
    fx, fy = x + pw / 2 - 34, py + 80
    frags.append(rect(fx, fy, 68, 34, fill="#d9e6d2", stroke=FIELD, sw=1.6, rx=3))
    frags.append(rect(fx - 12, fy + 6, 12, 22, fill="#c9a27a", stroke="#8a6d4a", sw=1, rx=2))
    frags.append(rect(fx + 68, fy + 6, 12, 22, fill="#c9a27a", stroke="#8a6d4a", sw=1, rx=2))
    frags.append(text(x + pw / 2, fy + 22, "R1", size=13, color=POS, bold=True))
    frags.append(text(x + pw / 2, fy + 58, "footprint R_0603", size=10, color=MUTED))

    # спільний ключ R1
    frags.append(arrow(xs[0] + pw, py + 95, xs[1] + 10, py + 95, color=POS, sw=1.8))
    frags.append(arrow(xs[1] + pw, py + 95, xs[2] + 10, py + 95, color=POS, sw=1.8))
    frags.append(text(W / 2, H - 14,
                      "Мітка R1 — спільний ключ: та сама деталь як символ, як рядок нетлиста і як корпус на платі.",
                      size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "refdes-link.svg"), W, H, *frags,
           title="refdes зшиває логіку й фізику")


def fig_standards_lineage():
    """Родовід двох незалежних гілок стандартів схеми: refdes-літери
    (MIL-STD-16 → IEEE 200/ANSI Y32.16 → ASME Y14.44) і графічні символи
    (IEEE 315/ANSI Y32.2 проти IEC 60617). Показує спільний військовий
    корінь і те, що це ДВІ різні речі: як звати деталь vs як її малювати."""
    W, H = 720, 470
    frags = []

    # ── ліва гілка: позначення (refdes) ──────────────────────────────────
    lx = 180
    frags.append(fitbox(lx - 130, 60, 260, 34,
                        "Як деталь звати   (refdes: R, C, U…)",
                        size=13, bold=True, fill="#eef2f9", stroke=NEG, rx=6))
    # вузли гілки: (текст, рік/примітка, колір-акценту)
    lnodes = [
        (["MIL-STD-16", "військовий стандарт США, від 1950-х"], "#eef2f9", NEG),
        (["IEEE 200-1975", "= ANSI Y32.16-1975", "(згодом withdrawn)"], "#eef2f9", NEG),
        (["ASME Y14.44-2008", "чинний"], "#e7f4ec", FIELD),
    ]
    ly = 120
    prev = None
    for txt, fill, stroke in lnodes:
        box = fitbox(lx - 130, ly, 260, 56, "\n".join(txt),
                     size=12, fill=fill, stroke=stroke, sw=1.8, rx=6)
        frags.append(box)
        if prev is not None:
            frags.append(arrow(lx, prev + 56, lx, ly, color=MUTED, sw=1.8))
        prev = ly
        ly += 108

    # ── права гілка: графічні символи ────────────────────────────────────
    rx = 540
    frags.append(fitbox(rx - 130, 60, 260, 34,
                        "Яким значком малювати",
                        size=13, bold=True, fill="#fdf1e7", stroke=POS, rx=6))
    # дві паралельні традиції — без спільного кореня між собою
    frags.append(fitbox(rx - 130, 120, 260, 78,
                        "IEEE 315-1975\n= ANSI Y32.2-1975\nрезистор — зигзаг\n(США, Канада)",
                        size=12, fill="#fdf1e7", stroke=POS, sw=1.8, rx=6))
    frags.append(fitbox(rx - 130, 246, 260, 78,
                        "IEC 60617\n(раніше IEC 617)\nрезистор — прямокутник\n(Європа, міжнародний)",
                        size=12, fill="#eef2f9", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(rx, 360, "співіснують і досі — та сама фізика,",
                      size=11, color=MUTED, italic=True))
    frags.append(text(rx, 376, "два обриси; читач мусить знати обидва",
                      size=11, color=MUTED, italic=True))

    # ── підпис-роздільник між гілками ────────────────────────────────────
    frags.append(line(360, 56, 360, 400, color="#d0d5dd", sw=1.4, dash="5 6"))
    frags.append(text(W / 2, H - 16,
                      "Дві незалежні осі: ЛІВОРУЧ — як деталь звати (літера-клас), ПРАВОРУЧ — яким значком її малюють.",
                      size=10.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "standards-lineage.svg"), W, H, *frags,
           title="Родовід позначень і символів схеми")


if __name__ == "__main__":
    fig_recipe()
    fig_power_first()
    fig_signal_flow()
    fig_patterns()
    fig_worked()
    fig_anatomy()
    fig_labels_buses()
    fig_values_derivation()
    fig_worked_full()
    fig_schematic_to_pcb()
    fig_eda_pipeline()
    fig_refdes_link()
    fig_standards_lineage()
    print("OK: фігури згенеровано у", IMG)
