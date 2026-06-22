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


if __name__ == "__main__":
    fig_recipe()
    fig_power_first()
    fig_signal_flow()
    fig_patterns()
    fig_worked()
    print("OK: фігури згенеровано у", IMG)
