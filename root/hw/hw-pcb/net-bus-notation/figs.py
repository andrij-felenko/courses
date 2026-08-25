# -*- coding: utf-8 -*-
"""Фігури до статті «Шини і векторні ланцюги». Чистий Python, SVG через svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WIRE = "#1a1a1a"     # скалярний ланцюг (один дріт)
WSW = 2.0            # товщина дроту
BUS = "#1a1a1a"      # шина-вектор
BSW = 5.5            # товщина шини


def dot(cx, cy, r=4.2):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, WIRE)


def pin(cx, cy, r=3.0):
    return circle(cx, cy, r, fill=BG, stroke=WIRE, sw=1.6)


def tag(x, y, s, size=12, anchor="middle", fill="#eef2ff", stroke=NEG):
    """Прямокутна мітка члена/ланцюга коло точки (x,y)."""
    w = text_width(s, size, True) + 14
    h = size + 10
    bx = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    out = rect(bx, y - h / 2, w, h, fill=fill, stroke=stroke, sw=1.4, rx=4)
    out += text(bx + w / 2, y + size * 0.35, s, size=size, color=INK, bold=True)
    return out


# ── Фігура 1: скаляр проти вектора ──────────────────────────────────────────
def fig_scalar_vs_vector():
    W, H = 720, 320
    parts = []
    # ── ліворуч: скалярний ланцюг — один дріт, одне значення ──
    parts.append(textbox(170, 40, "СКАЛЯРНИЙ ЛАНЦЮГ", size=13, bold=True,
                         fill="#eef2ff", stroke=NEG, color=NEG)[0])
    parts.append(pin(60, 110)); parts.append(pin(300, 110))
    parts.append(line(60, 110, 300, 110, color=WIRE, sw=WSW))
    parts.append(text(180, 96, "CLK", size=14, bold=True))
    parts.append(mtext(180, 150, ["один дріт = один вузол", "= одне значення 0/1"],
                       size=12, color=MUTED))
    # ── праворуч: векторний ланцюг — товста лінія, що розгортається у 8 ──
    ox = 400
    parts.append(textbox(ox + 130, 40, "ВЕКТОРНИЙ ЛАНЦЮГ (ШИНА)", size=13, bold=True,
                         fill="#fff7e6", stroke="#b9770e", color="#b9770e")[0])
    # товста шина
    parts.append(line(ox - 20, 110, ox + 90, 110, color=BUS, sw=BSW))
    parts.append(text(ox + 35, 96, "D[7..0]", size=14, bold=True))
    # розгортання: «віяло» з 8 тонких ліній праворуч від зламу
    base_x = ox + 90
    for i in range(8):
        yy = 70 + i * 22
        parts.append(line(base_x, 110, base_x + 24, yy if i < 4 else yy, color=WIRE, sw=1.4))
    # перелік членів
    members = "D7 D6 D5 D4 D3 D2 D1 D0".split()
    for i, m in enumerate(members):
        parts.append(text(base_x + 60, 74 + i * 22, m, size=11.5, color=INK, anchor="start"))
    parts.append('<path d="M %d 110 L %d 70 L %d 224 Z" fill="none" stroke="%s" '
                 'stroke-width="1.2" stroke-dasharray="3,3"/>'
                 % (base_x, base_x + 24, base_x + 24, MUTED))
    parts.append(mtext(ox + 60, 270, ["одне ім'я тримає 8 ланцюгів:", "D[0], D[1], … D[7]"],
                       size=12, color=MUTED))
    # роздільник
    parts.append(line(360, 60, 360, 250, color="#dddddd", sw=1))
    return render(os.path.join(IMG, "scalar-vs-vector.svg"), W, H, *parts)


# ── Фігура 2: зрив члена з шини за іменем ────────────────────────────────────
def fig_bus_ripper():
    W, H = 720, 330
    parts = []
    bx0, bx1, by = 90, 470, 80
    parts.append(line(bx0, by, bx1, by, color=BUS, sw=BSW))
    parts.append(text(bx0 - 6, by - 14, "D[7..0]", size=15, bold=True, anchor="start"))
    # чотири зриви з мітками членів до пінів мікросхеми
    members = [(150, "D0"), (250, "D1"), (350, "D2"), (450, "D7")]
    for x, name in members:
        parts.append(line(x, by, x + 22, by + 22, color=WIRE, sw=WSW))     # 45° bus entry
        parts.append(line(x + 22, by + 22, x + 22, 215, color=WIRE, sw=WSW))
        parts.append(pin(x + 22, 215))
        parts.append(tag(x + 22, by + 46, name, size=12))
    # «корпус» приймача праворуч від пінів
    parts.append(rect(120, 230, 380, 40, fill=FILL, stroke=INK, sw=1.6, rx=6))
    parts.append(text(310, 255, "входи даних мікросхеми", size=12.5, color=INK))
    note = ("45° «зрив» (bus entry) — ЛИШЕ графіка, сам нічого не з'єднує.\n"
            "З'єднує МІТКА члена: D0 на шині = D0 на піні. Інакше редактор не знає, яку з 8 ліній брати.")
    parts.append(textbox(W / 2, 300, note, size=12, fill=FILL, stroke=MUTED)[0])
    return render(os.path.join(IMG, "bus-ripper.svg"), W, H, *parts)


# ── Фігура 3: порядок індексів — D[7..0] проти D[0..7] ──────────────────────
def fig_index_order():
    W, H = 720, 300
    parts = []
    # вісім однакових фізичних ліній посередині
    n = 8
    y0, dy = 70, 22
    midL, midR = 300, 420
    for i in range(n):
        yy = y0 + i * dy
        parts.append(line(midL, yy, midR, yy, color=WIRE, sw=WSW))
    # ── ліворуч: підпис D[7..0] — старший зверху ──
    left_idx = [7, 6, 5, 4, 3, 2, 1, 0]
    parts.append(textbox(170, 40, "D[7..0]  — старший перший", size=13, bold=True,
                         fill="#eef2ff", stroke=NEG, color=NEG)[0])
    for i in range(n):
        yy = y0 + i * dy
        parts.append(text(midL - 14, yy + 4, "D%d" % left_idx[i], size=12, color=INK, anchor="end"))
    parts.append(text(midL - 70, y0 - 2, "D7 = MSB", size=11, color=MUTED, anchor="end"))
    parts.append(text(midL - 70, y0 + (n - 1) * dy + 6, "D0 = LSB", size=11, color=MUTED, anchor="end"))
    # ── праворуч: підпис D[0..7] — той самий жмут, інший напрям читання ──
    right_idx = [0, 1, 2, 3, 4, 5, 6, 7]
    parts.append(textbox(560, 40, "D[0..7]  — той самий жмут", size=13, bold=True,
                         fill="#fff7e6", stroke="#b9770e", color="#b9770e")[0])
    for i in range(n):
        yy = y0 + i * dy
        parts.append(text(midR + 14, yy + 4, "D%d" % right_idx[i], size=12, color=INK, anchor="start"))
    note = ("Важить не порядок у записі, а зв'язка індекс ↔ фізична лінія.\n"
            "D[3] — та сама лінія, хоч D[7..0], хоч D[0..7]. Старшинство біта визначає схема, не напрям читання.")
    parts.append(textbox(W / 2, 270, note, size=12, fill=FILL, stroke=MUTED)[0])
    return render(os.path.join(IMG, "index-order.svg"), W, H, *parts)


# ── Фігура 4: підшина (зріз) і склеювання (конкатенація) ────────────────────
def fig_merge_split():
    W, H = 720, 340
    parts = []
    # ── ЗРІЗ: A[15..0] розпадається на A[15..8] + A[7..0] ──
    parts.append(textbox(180, 36, "ЗРІЗ (підшина)", size=13, bold=True,
                         fill="#eafaf1", stroke=FIELD, color="#1e8449")[0])
    parts.append(line(60, 90, 200, 90, color=BUS, sw=BSW))
    parts.append(text(130, 76, "A[15..0]", size=13, bold=True))
    # розгалуження на дві півшини
    parts.append(line(200, 90, 240, 65, color=BUS, sw=BSW))
    parts.append(line(200, 90, 240, 115, color=BUS, sw=BSW))
    parts.append(line(240, 65, 330, 65, color=BUS, sw=BSW))
    parts.append(line(240, 115, 330, 115, color=BUS, sw=BSW))
    parts.append(tag(285, 50, "A[15..8]", size=11, fill="#eafaf1", stroke=FIELD))
    parts.append(tag(285, 132, "A[7..0]", size=11, fill="#eafaf1", stroke=FIELD))
    parts.append(text(360, 95, "16 = 8 + 8", size=12, color=MUTED, anchor="start"))
    # роздільник
    parts.append(line(W / 2, 30, W / 2, 250, color="#dddddd", sw=1))
    # ── СКЛЕЮВАННЯ: {CTRL, D[6..0]} → BUS[7..0] ──
    ox = 380
    parts.append(textbox(ox + 130, 36, "СКЛЕЮВАННЯ (конкатенація)", size=13, bold=True,
                         fill="#eef2ff", stroke=NEG, color=NEG)[0])
    parts.append(line(ox + 40, 70, ox + 130, 70, color=WIRE, sw=WSW))
    parts.append(text(ox + 40, 60, "CTRL", size=11, color=INK, anchor="start"))
    parts.append(line(ox + 40, 120, ox + 130, 120, color=BUS, sw=BSW))
    parts.append(text(ox + 40, 110, "D[6..0]", size=11, bold=True, anchor="start"))
    # зливаються в одну шину праворуч
    parts.append(line(ox + 130, 70, ox + 170, 95, color=BUS, sw=BSW))
    parts.append(line(ox + 130, 120, ox + 170, 95, color=BUS, sw=BSW))
    parts.append(line(ox + 170, 95, ox + 270, 95, color=BUS, sw=BSW))
    parts.append(tag(ox + 225, 78, "{CTRL, D[6..0]}", size=10.5, fill="#eef2ff", stroke=NEG))
    parts.append(text(ox + 175, 130, "1 + 7 = 8", size=12, color=MUTED, anchor="start"))
    note = ("Розрядність мусить збігатися: зліва й справа однакова кількість ліній.\n"
            "Інакше частина ланцюгів лишається без пари — типова тиха помилка шин.")
    parts.append(textbox(W / 2, 300, note, size=12, fill=FILL, stroke=MUTED)[0])
    return render(os.path.join(IMG, "merge-split.svg"), W, H, *parts)


# ── Фігура 5 (вставка proj): конвеєр розгортання шини ────────────────────────
def fig_expand_pipeline():
    W, H = 740, 380
    parts = []
    parts.append(text(W / 2, 30, "Як редактор розгортає D[7..0] у поіменні ланцюги",
                      size=14, bold=True))
    # крок 1 — запис шини
    parts.append(textbox(120, 80, "D[7..0]", size=16, bold=True,
                         fill="#fff7e6", stroke="#b9770e", color="#b9770e", min_w=120)[0])
    parts.append(text(120, 112, "запис шини", size=11, color=MUTED))
    parts.append(arrow(190, 80, 250, 80, color=INK))
    # крок 2 — парсер діапазону
    parts.append(textbox(360, 80, ["парсер діапазону", "prefix=\"D\"  lo=7  hi=0", "крок = (lo<=hi)?+1:-1"],
                         size=11, fill=FILL, stroke=NEG, color=INK, min_w=210)[0])
    parts.append(arrow(360, 118, 360, 158, color=INK))
    # крок 3 — генерація імен членів (8 рядків)
    members = ["D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0"]
    bx, by = 250, 175
    parts.append(rect(bx, by, 220, 150, fill="#eef2ff", stroke=NEG, sw=1.4, rx=6))
    parts.append(text(bx + 110, by + 20, "члени-скаляри (нетлист)", size=11.5, bold=True, color=NEG))
    for i, m in enumerate(members):
        yy = by + 40 + i * 13.5
        parts.append(text(bx + 26, yy, "%s" % m, size=11, color=INK, anchor="start"))
        parts.append(text(bx + 90, yy, "→ біт %d" % (7 - i), size=10.5, color=MUTED, anchor="start"))
    # крок 4 — мапа ім'я → піни
    parts.append(arrow(470, 250, 540, 250, color=INK))
    maprows = ["D7 → U3.12", "D6 → U3.11", "...", "D0 → U3.5"]
    parts.append(rect(545, 175, 175, 150, fill="#eafaf1", stroke="#1e8449", sw=1.4, rx=6))
    parts.append(text(545 + 87, 175 + 20, "мапа ім'я → піни", size=11.5, bold=True, color="#1e8449"))
    for i, r in enumerate(maprows):
        parts.append(text(545 + 20, 175 + 44 + i * 22, r, size=11, color=INK, anchor="start"))
    note = ("Вектора в нетлисті НЕМАЄ — лише 8 скалярів. Розгортання раз і назавжди\n"
            "перетворює один запис на 8 імен; далі кожен член живе як звичайний ланцюг.")
    parts.append(textbox(W / 2, 358, note, size=10.5, fill=FILL, stroke=MUTED)[0])
    return render(os.path.join(IMG, "expand-pipeline.svg"), W, H, *parts)


# ── Фігура 6 (вставка proj): звірка розрядності і висячий член ───────────────
def fig_width_check():
    W, H = 740, 320
    parts = []
    # ліворуч: збіг ширин — усе зчеплено
    parts.append(textbox(180, 36, "ширини збіглися: 8 = 8", size=12.5, bold=True,
                         fill="#eafaf1", stroke="#1e8449", color="#1e8449")[0])
    lx = 90
    src = ["D7", "D6", "D5", "D4", "D3", "D2", "D1", "D0"]
    dst = ["7", "6", "5", "4", "3", "2", "1", "0"]
    for i in range(8):
        yy = 70 + i * 22
        parts.append(text(lx, yy + 4, src[i], size=11, color=INK, anchor="end"))
        parts.append(line(lx + 8, yy, lx + 150, yy, color=WIRE, sw=WSW))
        parts.append(text(lx + 168, yy + 4, "Q" + dst[i], size=11, color=INK, anchor="start"))
    # роздільник
    parts.append(line(W / 2, 30, W / 2, 268, color="#dddddd", sw=1))
    # праворуч: неспівпадіння — один член висить
    ox = 400
    parts.append(textbox(ox + 150, 36, "ширини НЕ збіглися: 7 ≠ 8", size=12.5, bold=True,
                         fill="#fdecea", stroke=POS, color=POS)[0])
    src2 = ["D6", "D5", "D4", "D3", "D2", "D1", "D0"]   # лише 7
    for i in range(8):
        yy = 70 + i * 22
        parts.append(text(ox + 175, yy + 4, "Q%d" % (7 - i), size=11, color=INK, anchor="start"))
        parts.append(line(ox + 16, yy, ox + 165, yy, color=WIRE, sw=WSW) if i > 0 else "")
        if i > 0:
            parts.append(text(ox + 8, yy + 4, src2[i - 1], size=11, color=INK, anchor="end"))
    # верхній вхід Q7 лишається без пари
    yy0 = 70
    parts.append(line(ox + 100, yy0, ox + 165, yy0, color=POS, sw=WSW, dash="4,3"))
    parts.append('<circle cx="%.1f" cy="%.1f" r="6" fill="none" stroke="%s" stroke-width="2"/>'
                 % (ox + 100, yy0, POS))
    parts.append(text(ox + 90, yy0 + 4, "?", size=13, bold=True, color=POS, anchor="end"))
    parts.append(text(ox + 150, yy0 - 14, "Q7 висить", size=11, bold=True, color=POS))
    note = ("ERC ловить це ще до плати: при склеюванні/з'єднанні шин кількість\n"
            "ліній зліва й справа мусить збігтися, інакше член лишається без пари.")
    parts.append(textbox(W / 2, 298, note, size=10.5, fill=FILL, stroke=MUTED)[0])
    return render(os.path.join(IMG, "width-check.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_scalar_vs_vector()
    fig_bus_ripper()
    fig_index_order()
    fig_merge_split()
    fig_expand_pipeline()
    fig_width_check()
    print("figs done")
