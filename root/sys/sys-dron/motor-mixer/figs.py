# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Мікшер моторів».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: один мотор тягне І крутить ─────────────────────────────────────
# Першопричина всього мікшера: гвинт дає НЕ лише тягу вгору. За третім законом
# Ньютона повітря, яке лопать жене вниз, штовхає її вгору (тяга), а вісь,
# яка крутить лопать в один бік, отримує реактивний момент у протилежний.
# Тому кожен мотор — це водночас ДВА важелі: вертикальна тяга й момент рискання.
def fig_thrust_and_torque():
    W, H = 960, 470
    parts = []

    cx = W / 2 - 40
    hub_y = 250

    # вісь і втулка
    parts.append(line(cx, hub_y, cx, hub_y + 70, color=MUTED, sw=6))
    parts.append(circle(cx, hub_y, 16, fill="#eef2f7", stroke=INK, sw=2))

    # лопаті (диск гвинта зверху, спрощено еліпсом)
    parts.append('<ellipse cx="%.1f" cy="%.1f" rx="120" ry="22" fill="#eef2f7" '
                 'stroke="%s" stroke-width="2"/>' % (cx, hub_y, INK))
    parts.append(text(cx, hub_y - 32, "гвинт", size=13, color=MUTED))

    # обертання лопаті (дугова стрілка навколо втулки)
    parts.append('<path d="M %.1f %.1f A 46 46 0 1 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="3" marker-end="url(#arrow)"/>'
                 % (cx + 46, hub_y - 6, cx - 30, hub_y + 36, NEG))
    parts.append(text(cx - 70, hub_y + 8, "крутиться\n(скажімо, за\nгодинниковою)",
                      size=12, color=NEG, anchor="end"))

    # 1) тяга вгору
    parts.append(arrow(cx, hub_y - 12, cx, hub_y - 150, color=POS, sw=3.2))
    parts.append(text(cx + 16, hub_y - 120, "ТЯГА вгору", size=15, color=POS,
                      anchor="start", bold=True))
    parts.append(text(cx + 16, hub_y - 98, "повітря жене вниз →\nреакція штовхає апарат угору",
                      size=12, color=POS, anchor="start"))

    # 2) реактивний момент рискання (протилежний оберту)
    parts.append('<path d="M %.1f %.1f A 150 150 0 0 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="3" marker-end="url(#arrow)"/>'
                 % (cx + 150, hub_y + 70, cx - 60, hub_y + 170, POS))
    parts.append(text(cx + 60, hub_y + 165, "РЕАКТИВНИЙ МОМЕНТ", size=14, color=POS,
                      anchor="start", bold=True))
    parts.append(text(cx + 60, hub_y + 186,
                      "корпус хоче провернутися\nу ЗВОРОТНИЙ бік (рискання)",
                      size=12, color=POS, anchor="start"))

    # підсумок
    box, bw, bh = textbox(W / 2, H - 24,
                          "один мотор = ДВА важелі: вертикальна тяга (нагору) і момент рискання (від реакції осі). На цьому стоїть увесь мікшер",
                          size=12.5, pad=11, fill=FILL, bold=True)
    parts.append(box)

    render("img/thrust-and-torque.svg", W, H, *parts,
           title="Один мотор тягне І крутить: тяга вгору + реактивний момент")


# ── Фігура 2: чотири команди розкладаються на чотири мотори (квадро X) ────────
# Серце статті. Зверху — рама X із чотирма моторами та їхніми напрямками
# обертання (CW/CCW по черзі). Кожна команда (газ/крен/тангаж/рискання) —
# свій патерн знаків ПО моторах. Показуємо чотири маленькі схеми «який мотор
# додати, який зняти», щоб видно було: команда = розподіл по моторах.
def fig_mixing_matrix():
    W, H = 940, 640
    parts = []

    # ── велика схема рами X угорі ──
    cx, cy, R = W / 2, 150, 95
    # промені рами
    offs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]  # FL, FR, BR, BL екранно
    for dx, dy in offs:
        parts.append(line(cx, cy, cx + dx * R, cy + dy * R, color=INK, sw=5))
    parts.append(circle(cx, cy, 10, fill="#eef2f7", stroke=INK, sw=2))
    # напрям «вперед»
    parts.append(arrow(cx, cy - R - 6, cx, cy - R - 48, color=FIELD, sw=2.4))
    parts.append(text(cx + 12, cy - R - 36, "вперед (ніс)", size=12, color=FIELD,
                      anchor="start", bold=True))

    # мотори з номерами й напрямом обертання (CW=за год., CCW=проти)
    motors = [
        (cx - R, cy - R, "M3", "CCW", NEG),
        (cx + R, cy - R, "M1", "CW", POS),
        (cx + R, cy + R, "M2", "CCW", NEG),
        (cx - R, cy + R, "M4", "CW", POS),
    ]
    for mx, my, name, spin, col in motors:
        parts.append(circle(mx, my, 26, fill="#f7f9fb", stroke=INK, sw=2))
        parts.append(text(mx, my - 2, name, size=14, bold=True))
        parts.append(text(mx, my + 16, spin, size=11, color=col, bold=True))
    parts.append(text(cx - R - 36, cy, "діагональні\nпари крутяться\nв один бік",
                      size=11, color=MUTED, anchor="end"))

    # ── чотири маленькі схеми: патерн кожної команди ──
    def mini(ox, oy, title, signs, note):
        # signs: dict name -> "+"/"−"/"0"
        r = 40
        parts.append(text(ox, oy - r - 22, title, size=13, bold=True))
        cells = [(-1, -1, "M3"), (1, -1, "M1"), (1, 1, "M2"), (-1, 1, "M4")]
        for dx, dy, nm in cells:
            x, y = ox + dx * r, oy + dy * r
            parts.append(line(ox, oy, x, y, color="#c9cfd6", sw=3))
        for dx, dy, nm in cells:
            x, y = ox + dx * r, oy + dy * r
            s = signs[nm]
            if s == "+":
                parts.append(circle(x, y, 16, fill="#fdecea", stroke=POS, sw=2.2))
                parts.append(text(x, y + 6, "+", size=20, color=POS, bold=True))
            elif s == "−":
                parts.append(circle(x, y, 16, fill="#eaf0fd", stroke=NEG, sw=2.2))
                parts.append(text(x, y + 5, "−", size=20, color=NEG, bold=True))
            else:
                parts.append(circle(x, y, 16, fill="#f1f3f5", stroke=MUTED, sw=2))
                parts.append(text(x, y + 5, "0", size=15, color=MUTED, bold=True))
        parts.append(text(ox, oy + r + 30, note, size=11, color=MUTED))

    row_y = 380
    mini(150, row_y, "ГАЗ (висота)",
         {"M1": "+", "M2": "+", "M3": "+", "M4": "+"},
         "усі однаково ↑")
    mini(390, row_y, "КРЕН (вліво)",
         {"M1": "+", "M2": "+", "M3": "−", "M4": "−"},
         "праві ↑, ліві ↓")
    mini(630, row_y, "ТАНГАЖ (ніс ↓)",
         {"M1": "+", "M2": "−", "M3": "+", "M4": "−"},
         "передні ↑, задні ↓")
    mini(860 - 40, row_y, "РИСКАННЯ (вліво)",
         {"M1": "+", "M2": "−", "M3": "−", "M4": "+"},
         "одна пара спінів ↑")

    # підсумок-формула
    box = fitbox(70, H - 110, W - 140, 80,
                 "Команда мотора = базовий газ + (±крен) + (±тангаж) + (±рискання).\n"
                 "Знаки беруться з ГЕОМЕТРІЇ (де мотор) і НАПРЯМУ ОБЕРТАННЯ (для рискання).\n"
                 "Чотири рядки знаків — це і є матриця мікшера.",
                 size=13.5, fill="#eef6ff", stroke=NEG, sw=2, bold=False)
    parts.append(box)

    render("img/mixing-matrix.svg", W, H, *parts,
           title="Чотири команди → чотири мотори: патерн знаків = матриця мікшера")


# ── Фігура 3: рама X проти + (звідки різні знаки) ────────────────────────────
# Чому матриця для X і для «плюса» різна. У «плюсі» мотори стоять ПО осях,
# тож крен крутить лише бічну пару, тангаж — лише носо-хвостову (по одному
# плечу). У X кожен мотор зміщений по обох осях, тож у крен і тангаж тягнуть
# УСІ чотири — удвічі більше моментного важеля. Звідси й різні рядки матриці.
def fig_x_vs_plus():
    W, H = 920, 460
    parts = []

    def frame(ox, oy, rot, title, sub):
        R = 92
        import math
        a0 = math.radians(rot)
        # чотири промені
        angs = [a0 + math.radians(k) for k in (45, 135, 225, 315)] if rot == 0 else \
               [a0 + math.radians(k) for k in (0, 90, 180, 270)]
        pts = []
        for a in angs:
            x = ox + R * math.cos(a)
            y = oy - R * math.sin(a)
            pts.append((x, y))
            parts.append(line(ox, oy, x, y, color=INK, sw=5))
        parts.append(circle(ox, oy, 9, fill="#eef2f7", stroke=INK, sw=2))
        # «вперед» завжди вгору
        parts.append(arrow(ox, oy - R - 6, ox, oy - R - 40, color=FIELD, sw=2.2))
        parts.append(text(ox, oy - R - 52, "вперед", size=11, color=FIELD, bold=True))
        for x, y in pts:
            parts.append(circle(x, y, 20, fill="#f7f9fb", stroke=INK, sw=2))
        parts.append(text(ox, oy + R + 50, title, size=15, bold=True))
        parts.append(text(ox, oy + R + 72, sub, size=11.5, color=MUTED))
        return pts

    # ── «плюс»: мотори по осях ──
    px = 240
    pts_plus = frame(px, 180, 90, "Рама «+» (плюс)",
                     "мотори ПО осях: ніс, хвіст, боки")
    # підсвітити вісь крену (ліво-право пара)
    parts.append(text(px, 320, "крен → лише бічна пара\nтангаж → лише носо-хвостова",
                      size=12, color=INK))

    # ── X: мотори по діагоналях ──
    xx = W - 240
    pts_x = frame(xx, 180, 0, "Рама «X» (ікс)",
                  "мотори по КУТАХ: жоден не на осі")
    parts.append(text(xx, 320, "крен і тангаж → УСІ чотири мотори\n(удвічі більший важіль, рівніший огляд)",
                      size=12, color=INK))

    # підсумок
    box, bw, bh = textbox(W / 2, H - 30,
                          "геометрія задає знаки: у «плюсі» на кожну вісь працює пара моторів, у «X» — усі чотири.\n"
                          "Тому матриця мікшера для рами X і для рами «+» РІЗНА",
                          size=12.5, pad=11, fill=FILL, bold=True)
    parts.append(box)

    render("img/x-vs-plus.svg", W, H, *parts,
           title="Рама X проти «плюса»: чому знаки в матриці різні")


# ── Фігура 4: насичення й нормування ─────────────────────────────────────────
# Практичне серце. Сума «газ + моменти» може вилізти за стелю мотора (1.0) або
# впасти під нуль. Якщо просто обрізати кожен мотор окремо — патерн моментів
# спотвориться й апарат втратить керованість. Правильно: ПОСУНУТИ всі команди
# разом (зберегти різниці = моменти), пожертвувавши спільним газом.
def fig_saturation():
    W, H = 940, 470
    parts = []

    base = 110          # x базової лінії стовпчиків
    floor = H - 150
    scale = 200         # px на одиницю команди (0..1.4 показуємо)
    top = floor - 1.0 * scale
    ceil = floor - 1.0 * scale  # стеля 1.0
    zero = floor

    def col_group(ox, vals, label, clipped=False, shifted=False):
        names = ["M1", "M2", "M3", "M4"]
        bw = 30
        gap = 12
        for i, (nm, v) in enumerate(zip(names, vals)):
            x = ox + i * (bw + gap)
            vv = v
            over = v > 1.0
            under = v < 0.0
            disp = max(0.0, min(v, 1.4))
            y = floor - disp * scale
            fill = "#eef2f7"
            stroke = INK
            if (over or under) and not (clipped or shifted):
                stroke = POS
                fill = "#fdecea"
            parts.append(rect(x, y, bw, floor - y, fill=fill, stroke=stroke, sw=2, rx=3))
            parts.append(text(x + bw / 2, floor + 16, nm, size=11, color=MUTED))
            if over and not (clipped or shifted):
                parts.append(text(x + bw / 2, y - 6, "✗", size=14, color=POS, bold=True))
        # лінії стелі й нуля
        x1 = ox - 8
        x2 = ox + 4 * (bw + gap)
        parts.append(line(x1, ceil, x2, ceil, color=POS, sw=1.6, dash="5,5"))
        parts.append(line(x1, zero, x2, zero, color=NEG, sw=1.6, dash="5,5"))
        parts.append(text((x1 + x2) / 2, floor + 40, label, size=12.5, bold=True))

    # позначки стелі/нуля (один раз ліворуч)
    parts.append(text(base - 20, ceil + 4, "1.0", size=11, color=POS, anchor="end"))
    parts.append(text(base - 20, zero + 4, "0", size=11, color=NEG, anchor="end"))
    parts.append(text(base - 20, (ceil + zero) / 2, "межі\nмотора", size=10,
                      color=MUTED, anchor="end"))

    # 1) сирий розклад: M1 вилазить за 1.0
    col_group(base, [1.18, 0.95, 0.75, 0.55], "сирий розклад\n(M1 за стелею ✗)")

    # 2) наївне обрізання: M1=1.0, різниці спотворені
    col_group(base + 250, [1.00, 0.95, 0.75, 0.55],
              "наївно обрізали M1\n→ момент спотворено", clipped=True)
    parts.append(text(base + 250 + 80, floor - 1.0 * scale - 26,
                      "крен ≠ заданий", size=11.5, color=POS, bold=True))

    # 3) правильно: посунути всі вниз на надлишок (0.18) — різниці збережено
    sh = 0.18
    col_group(base + 540, [1.18 - sh, 0.95 - sh, 0.75 - sh, 0.55 - sh],
              "посунули ВСІ на надлишок\n→ моменти збережено", shifted=True)
    parts.append(arrow(base + 540 + 130, floor - 1.18 * scale,
                       base + 540 + 130, floor - 1.0 * scale, color=FIELD, sw=2.2))
    parts.append(text(base + 540 + 145, floor - 1.08 * scale,
                      "жертвуємо\nспільним газом", size=11, color=FIELD, anchor="start"))

    # підсумок
    box = fitbox(70, H - 70, W - 140, 46,
                 "Насичення лікують зсувом УСІХ команд разом (зберегти різниці = моменти), "
                 "а не обрізанням кожної окремо. Орієнтація важливіша за висоту.",
                 size=13, fill="#e9f7ef", stroke=FIELD, sw=2)
    parts.append(box)

    render("img/saturation.svg", W, H, *parts,
           title="Насичення й нормування: зберегти моменти, пожертвувати газом")


if __name__ == "__main__":
    fig_thrust_and_torque()
    fig_mixing_matrix()
    fig_x_vs_plus()
    fig_saturation()
    print("OK: thrust-and-torque, mixing-matrix, x-vs-plus, saturation")
