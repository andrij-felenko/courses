# -*- coding: utf-8 -*-
"""
Фігури для компонентної вставки 🔌 до §4.8.4
«Джерела опорної напруги: TL431 і REF-класи — стабільні мілівольти»

Рис. 4.8.4c.1 — Внутрішня будова TL431 і базове shunt-вмикання
Рис. 4.8.4c.2 — Дві топології опори (shunt / series) і шкала-сходинка ppm/точності

Запуск: python figs-ch26-s4-c-voltage-reference.py
Вивід: ./img/fig-26-4c-1-tl431.svg, ./img/fig-26-4c-2-shunt-vs-series.svg
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.4c.1 — Усередині TL431 і базове shunt-вмикання
# ═══════════════════════════════════════════════════════════════════════════════
def fig_tl431():
    W, H = 900, 480
    frags = []

    # ── заголовок ──────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 30, "TL431: внутрішня будова й shunt-вмикання", 17, INK,
                      anchor="middle", bold=True))
    frags.append(text(W / 2, 52, "петля зворотного зв'язку сама тримає REF = 2.495 В; "
                      "дільник R1/R2 програмує будь-який Vout",
                      11, MUTED, anchor="middle"))

    # ── ліво: внутрішня блок-схема TL431 ──────────────────────────────────────
    # Зовнішній прямокутник (корпус мікросхеми)
    ic_x, ic_y, ic_w, ic_h = 60, 80, 340, 300
    frags.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#f0f4ff", stroke=NEG, sw=2, rx=10))
    frags.append(text(ic_x + ic_w / 2, ic_y + 16, "TL431", 13, NEG, anchor="middle", bold=True))

    # Блок 1: bandgap-ядро
    bg_cx, bg_cy = ic_x + 80, ic_y + 95
    box1, bw1, bh1 = textbox(bg_cx, bg_cy, "bandgap\nядро\n2.495 В",
                              size=12, pad=9, fill="#fff3e0", stroke="#e07b00", sw=1.8)
    frags.append(box1)

    # Блок 2: підсилювач похибки
    ea_cx, ea_cy = ic_x + 240, ic_y + 95
    box2, bw2, bh2 = textbox(ea_cx, ea_cy, "підсилювач\nпохибки\n(error amp)",
                              size=12, pad=9, fill="#e8f5e9", stroke=FIELD, sw=1.8)
    frags.append(box2)

    # Блок 3: вихідний транзистор
    tr_cx, tr_cy = ic_x + 240, ic_y + 220
    box3, bw3, bh3 = textbox(tr_cx, tr_cy, "вихідний\nтранзистор\n(cathode)",
                              size=12, pad=9, fill="#fdecea", stroke=POS, sw=1.8)
    frags.append(box3)

    # З'єднання: bandgap → error amp (стрілка вправо)
    frags.append(line(bg_cx + bw1 / 2, bg_cy, ea_cx - bw2 / 2, ea_cy,
                      color="#e07b00", sw=1.8))
    frags.append(text((bg_cx + bw1 / 2 + ea_cx - bw2 / 2) / 2, bg_cy - 10,
                      "2.495 В", 9, "#e07b00", anchor="middle"))

    # error amp → transistor (стрілка вниз)
    frags.append(arrow(ea_cx, ea_cy + bh2 / 2, ea_cx, tr_cy - bh3 / 2,
                       color=FIELD, sw=1.8))

    # REF-вивід (вхід до error amp зліва)
    ref_x = ea_cx - bw2 / 2 - 1
    ref_y = ea_cy + 10
    frags.append(line(ic_x - 1, ref_y, ref_x, ref_y, color=NEG, sw=1.8))
    frags.append(text(ic_x - 6, ref_y + 4, "REF", 11, NEG, anchor="end", bold=True))

    # CATHODE-вивід (вверх від транзистора)
    cat_x = ic_x + ic_w + 1
    cat_y = tr_cy
    frags.append(line(tr_cx + bw3 / 2, cat_y, cat_x, cat_y, color=POS, sw=1.8))
    frags.append(text(cat_x + 4, cat_y + 4, "CATHODE (K)", 11, POS, anchor="start", bold=True))

    # ANODE-вивід (вниз)
    an_x = ic_x + ic_w / 2
    an_y = ic_y + ic_h + 1
    frags.append(line(an_x, tr_cy + bh3 / 2, an_x, an_y, color=INK, sw=1.8))
    frags.append(text(an_x, an_y + 14, "ANODE (A) = земля", 11, INK, anchor="middle"))

    # петля зворотного зв'язку: від REF-вузла через мікросхему назад до error amp
    fb_x = ic_x - 30
    frags.append(line(ic_x - 1, ref_y, fb_x, ref_y, color=NEG, sw=1.5, dash="4,3"))
    frags.append(line(fb_x, ref_y, fb_x, ic_y + ic_h + 30, color=NEG, sw=1.5, dash="4,3"))
    frags.append(text(fb_x - 4, ic_y + ic_h + 44, "петля ЗЗ", 9, NEG, anchor="end"))

    # ── право: схема вмикання ──────────────────────────────────────────────────
    sx = 480  # x-початок схеми
    # Vsupply
    vs_x, vs_y = sx + 50, 90
    frags.append(text(vs_x, vs_y - 4, "Vsupply (5 В)", 12, INK, anchor="middle", bold=True))

    # Rs (баластний резистор)
    rs_x = vs_x
    rs_top = vs_y + 6
    rs_bot = vs_y + 80
    frags.append(line(rs_x, rs_top, rs_x, rs_bot, color=INK, sw=2))
    # символ резистора — зиґзаґ
    zz_pts = [(rs_x, rs_top + 15)]
    nz = 5
    for i in range(nz * 2):
        dx = 10 * (1 if i % 2 == 0 else -1)
        dy = (rs_bot - rs_top - 30) / (nz * 2)
        prev = zz_pts[-1]
        zz_pts.append((prev[0] + dx, prev[1] + dy))
    zz_pts.append((rs_x, rs_bot - 15))
    frags.append("".join(
        line(zz_pts[i][0], zz_pts[i][1], zz_pts[i + 1][0], zz_pts[i + 1][1],
             color=INK, sw=1.5)
        for i in range(len(zz_pts) - 1)
    ))
    rs_box, _, _ = textbox(rs_x + 30, (rs_top + rs_bot) / 2, "Rs", size=12, pad=6,
                           fill="#fff", stroke=MUTED, sw=1)
    frags.append(rs_box)

    # вузол між Rs і катодом (K)
    node_x, node_y = rs_x, rs_bot
    frags.append(circle(node_x, node_y, 3.5, fill=POS, stroke=POS, sw=1))

    # Лінія від вузла до катода (вправо → вниз до катода TL431-прямокутника)
    # Позначення TL431 (праве поле)
    tl_cx, tl_cy = sx + 170, 255
    tl_box, tl_w, tl_h = textbox(tl_cx, tl_cy, "TL431", size=14, pad=12,
                                  fill="#e8eaf6", stroke=NEG, sw=2)
    frags.append(tl_box)
    frags.append(text(tl_cx, tl_cy + 3, "K     A", 11, NEG, anchor="middle"))

    # провід катод: вузол → TL431 ліворуч верх
    frags.append(line(node_x, node_y, tl_cx - tl_w / 2, tl_cy - 12, color=POS, sw=1.8))
    frags.append(text(tl_cx - tl_w / 2 - 4, tl_cy - 14, "K", 10, POS, anchor="end", bold=True))

    # земля: від анода TL431 вниз
    gnd_x = tl_cx
    gnd_y = tl_cy + tl_h / 2
    frags.append(line(gnd_x, gnd_y, gnd_x, gnd_y + 40, color=INK, sw=1.8))
    # символ землі
    for i, hw in enumerate([16, 10, 5]):
        gy = gnd_y + 40 + i * 7
        frags.append(line(gnd_x - hw, gy, gnd_x + hw, gy, color=INK, sw=2.2 - i * 0.4))
    frags.append(text(gnd_x, gnd_y + 40 + 30, "GND", 10, INK, anchor="middle"))

    # Дільник R1/R2: від катода вправо, потім вниз до REF, звідти до землі
    dv_x = tl_cx + 90
    frags.append(line(node_x, node_y, dv_x, node_y, color=INK, sw=1.8))
    frags.append(line(dv_x, node_y, dv_x, node_y + 80, color=INK, sw=1.8))

    # R1 (верхній)
    r1_cy = node_y + 40
    r1_box, _, _ = textbox(dv_x + 28, r1_cy, "R1", size=12, pad=6, fill="#fff3e0",
                            stroke="#e07b00", sw=1.5)
    frags.append(r1_box)
    frags.append(line(dv_x, node_y, dv_x, node_y + 80, color=INK, sw=1.8))

    # REF-вузол посередині
    ref_node_x, ref_node_y = dv_x, node_y + 80
    frags.append(circle(ref_node_x, ref_node_y, 3.5, fill=NEG, stroke=NEG, sw=1))
    frags.append(text(ref_node_x + 8, ref_node_y + 4, "REF", 11, NEG, anchor="start", bold=True))

    # REF → TL431 REF-вивід (горизонтальна лінія вліво)
    frags.append(line(ref_node_x, ref_node_y, tl_cx + tl_w / 2, tl_cy, color=NEG, sw=1.8))

    # R2 (нижній)
    r2_cy = ref_node_y + 45
    frags.append(line(dv_x, ref_node_y, dv_x, ref_node_y + 90, color=INK, sw=1.8))
    r2_box, _, _ = textbox(dv_x + 28, r2_cy, "R2", size=12, pad=6, fill="#e8f5e9",
                            stroke=FIELD, sw=1.5)
    frags.append(r2_box)

    # земля від R2
    frags.append(line(dv_x, ref_node_y + 90, dv_x, ref_node_y + 100, color=INK, sw=1.8))
    for i, hw in enumerate([14, 9, 4]):
        gy = ref_node_y + 100 + i * 7
        frags.append(line(dv_x - hw, gy, dv_x + hw, gy, color=INK, sw=2.2 - i * 0.4))

    # формула Vout
    frags.append(text(dv_x + 85, node_y + 30,
                      "Vout = 2.495 × (1 + R1/R2)", 11, INK, anchor="start", bold=True))

    # ── нижня підказка (рамка) ──────────────────────────────────────────────────
    hint, _, _ = textbox(W / 2, H - 36,
                         "Петля тримає REF = 2.495 В; транзистор «зливає» рівно стільки струму, скільки треба. "
                         "Двома резисторами програмується будь-який Vout.",
                         size=11, pad=10, fill="#fffde7", stroke="#bbb", sw=1.2, min_w=800)
    frags.append(hint)

    render(os.path.join(OUT, "fig-26-4c-1-tl431.svg"), W, H, *frags,
           title=None)
    print("wrote fig-26-4c-1-tl431.svg")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.8.4c.2 — Shunt vs series + шкала ppm/точності
# ═══════════════════════════════════════════════════════════════════════════════
def fig_shunt_vs_series():
    W, H = 920, 500
    frags = []

    frags.append(text(W / 2, 30, "Дві топології опори і шкала точності", 17, INK,
                      anchor="middle", bold=True))
    frags.append(text(W / 2, 52, "shunt потребує баластного резистора; series — як LDO, мкА спокою; "
                      "tempco і початкова точність визначають стелю АЦП",
                      11, MUTED, anchor="middle"))

    # ══ ЛІВО: shunt-топологія ══════════════════════════════════════════════════
    lx = 120  # центр лівої схеми
    ly_top = 90
    col_sh = "#7b1fa2"  # фіолетовий для shunt

    frags.append(text(lx, ly_top, "SHUNT (TL431, LM4040)", 12, col_sh,
                      anchor="middle", bold=True))
    frags.append(text(lx, ly_top + 16, "— потребує баластного Rs", 10, MUTED, anchor="middle"))

    # Vsupply
    frags.append(text(lx, ly_top + 40, "Vsupply", 11, INK, anchor="middle", bold=True))
    # провід вниз через Rs
    frags.append(line(lx, ly_top + 50, lx, ly_top + 90, color=INK, sw=2))
    # Rs позначення
    rs_box, _, _ = textbox(lx, ly_top + 110, "Rs\n(баласт)", size=11, pad=7,
                           fill="#ede7f6", stroke=col_sh, sw=1.5)
    frags.append(rs_box)
    frags.append(line(lx, ly_top + 130, lx, ly_top + 160, color=INK, sw=2))

    # вузол (Vout)
    vout_y = ly_top + 160
    frags.append(circle(lx, vout_y, 4, fill=col_sh, stroke=col_sh, sw=1))
    frags.append(text(lx + 10, vout_y - 6, "Vout", 11, col_sh, anchor="start", bold=True))
    frags.append(text(lx + 10, vout_y + 8, "(до навантаження)", 9, MUTED, anchor="start"))

    # Opора-блок
    ref_box, ref_w, ref_h = textbox(lx, vout_y + 60, "Опора\n(shunt)", size=12, pad=10,
                                    fill="#ede7f6", stroke=col_sh, sw=1.8)
    frags.append(ref_box)
    frags.append(line(lx, vout_y, lx, vout_y + 60 - ref_h / 2, color=col_sh, sw=1.8))

    # земля
    frags.append(line(lx, vout_y + 60 + ref_h / 2, lx, vout_y + 60 + ref_h / 2 + 30,
                      color=INK, sw=1.8))
    for i, hw in enumerate([14, 9, 4]):
        gy = vout_y + 60 + ref_h / 2 + 30 + i * 7
        frags.append(line(lx - hw, gy, lx + hw, gy, color=INK, sw=2.2 - i * 0.4))

    frags.append(text(lx, vout_y + 60 + ref_h / 2 + 60,
                      "Постійно тече струм\nчерез Rs → тепло", 9, POS, anchor="middle"))

    # ══ СЕРЕДИНА: series-топологія ════════════════════════════════════════════
    mx = 310
    col_se = "#00695c"  # темно-зелений для series

    frags.append(text(mx, ly_top, "SERIES (REF30xx, ADR)", 12, col_se,
                      anchor="middle", bold=True))
    frags.append(text(mx, ly_top + 16, "— як LDO: вхід–вихід–земля", 10, MUTED, anchor="middle"))

    # Vin
    frags.append(text(mx, ly_top + 40, "Vin", 11, INK, anchor="middle", bold=True))
    frags.append(line(mx, ly_top + 50, mx, ly_top + 80, color=INK, sw=2))

    # Мікросхема series
    ser_box, ser_w, ser_h = textbox(mx, ly_top + 120, "Series\nREF\n(3 виводи)", size=12, pad=10,
                                    fill="#e0f2f1", stroke=col_se, sw=1.8)
    frags.append(ser_box)
    frags.append(line(mx, ly_top + 80, mx, ly_top + 120 - ser_h / 2, color=INK, sw=2))

    # Vout (праворуч від мікросхеми)
    so_x = mx + ser_w / 2
    so_y = ly_top + 120
    frags.append(line(so_x, so_y, so_x + 50, so_y, color=col_se, sw=1.8))
    frags.append(text(so_x + 55, so_y + 4, "Vout", 11, col_se, anchor="start", bold=True))

    # земля (вниз)
    frags.append(line(mx, ly_top + 120 + ser_h / 2, mx, ly_top + 120 + ser_h / 2 + 30,
                      color=INK, sw=1.8))
    for i, hw in enumerate([14, 9, 4]):
        gy = ly_top + 120 + ser_h / 2 + 30 + i * 7
        frags.append(line(mx - hw, gy, mx + hw, gy, color=INK, sw=2.2 - i * 0.4))

    frags.append(text(mx, ly_top + 120 + ser_h / 2 + 60,
                      "Мікроампери спокою →\nідеально для батарей", 9, col_se, anchor="middle"))

    # ══ ПРАВО: шкала-сходинка точності/ppm ════════════════════════════════════
    sc_x = 500   # ліва межа шкали
    sc_w = 350
    sc_y_top = 78
    sc_y_bot = 450

    frags.append(text(sc_x + sc_w / 2, sc_y_top - 10, "Шкала точності опор",
                      13, INK, anchor="middle", bold=True))

    # вертикальна вісь
    frags.append(line(sc_x + 10, sc_y_top, sc_x + 10, sc_y_bot, color=MUTED, sw=1.5))
    frags.append(text(sc_x + 10, sc_y_top - 4, "кращі ↑", 9, MUTED, anchor="middle"))
    frags.append(text(sc_x + 10, sc_y_bot + 12, "простіші ↓", 9, MUTED, anchor="middle"))

    # сходинки (від гіршого знизу до кращого вгорі)
    steps = [
        # (y_center, label_short, detail, bar_color, bar_fill)
        (sc_y_bot - 44,
         "TL431",
         "0.5–2 %   |   десятки ppm/°C\nдешево, масово (БЖ, зарядки)",
         "#7b1fa2", "#ede7f6"),
        (sc_y_bot - 160,
         "LM4040 / REF30",
         "~0.2 %   |   ~50–100 ppm/°C\nшум ~35 мкВ rms, ~50 мкА",
         "#1565c0", "#e3f2fd"),
        (sc_y_bot - 270,
         "REF5xxx / ADR4xxx",
         "~0.05–0.1 %   |   ~10–25 ppm/°C\nнизький шум, прецизійні задачі",
         col_se, "#e0f2f1"),
        (sc_y_bot - 368,
         "ADR/AD586-клас",
         "~0.05 %   |   ~5 ppm/°C\nлабораторна метрологія, дорого",
         POS, "#fdecea"),
    ]

    bar_x = sc_x + 30
    bar_w = sc_w - 40

    for i, (cy, lbl, detail, stroke_c, fill_c) in enumerate(steps):
        # горизонтальна смуга
        bh = 70
        by = cy - bh / 2
        frags.append(rect(bar_x, by, bar_w, bh, fill=fill_c, stroke=stroke_c, sw=1.8, rx=8))
        # назва
        frags.append(text(bar_x + 10, by + 22, lbl, 12, stroke_c,
                          anchor="start", bold=True))
        # деталі
        for j, dline in enumerate(detail.split("\n")):
            frags.append(text(bar_x + 10, by + 40 + j * 15, dline, 10, INK, anchor="start"))

        # стрілка вгору між сходинками
        if i < len(steps) - 1:
            next_cy = steps[i + 1][0]
            mid_y = (cy - bh / 2 + next_cy + bh / 2) / 2
            frags.append(text(sc_x + sc_w - 10, mid_y + 4, "точніше →", 9, MUTED,
                              anchor="end"))

    # зв'язок із §4.8.4
    hint2, _, _ = textbox(W / 2, H - 34,
                          "Менший tempco і шум опори = вища стеля точності АЦП (§4.8.4). "
                          "Вибір: скільки ppm реально треба — не переплачуй за зайве.",
                          size=11, pad=10, fill="#fffde7", stroke="#bbb", sw=1.2, min_w=860)
    frags.append(hint2)

    render(os.path.join(OUT, "fig-26-4c-2-shunt-vs-series.svg"), W, H, *frags,
           title=None)
    print("wrote fig-26-4c-2-shunt-vs-series.svg")


if __name__ == "__main__":
    fig_tl431()
    fig_shunt_vs_series()
    print("Done.")
