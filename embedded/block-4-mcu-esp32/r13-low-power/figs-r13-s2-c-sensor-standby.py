# -*- coding: utf-8 -*-
"""
Фігури для вставки 🔌 §4.13.2c — «Хто на платі не спить: standby-струми давачів».
Запуск: python figs-r13-s2-c-sensor-standby.py

Вивід → ./img/
  fig-r13-2c-1-standby-map.svg   — Рис. 4.13.2c.1
  fig-r13-2c-2-mode-states.svg   — Рис. 4.13.2c.2
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.2c.1 — Карта струму: сплячий МК + давачі у sleep vs normal
# Горизонтальна стовпчикова діаграма, лог-шкала µA
# ─────────────────────────────────────────────────────────────────────────────
def fig1_standby_map():
    W, H = 760, 400
    title_h = 38
    left_margin = 230
    right_margin = 40
    top = title_h + 30
    bottom = H - 60

    chart_w = W - left_margin - right_margin
    chart_h = bottom - top

    # Лог-шкала: від 0.05 µA до 300 µA
    log_min = math.log10(0.05)
    log_max = math.log10(400.0)

    def x_for(val):
        lv = math.log10(max(val, 0.05))
        frac = (lv - log_min) / (log_max - log_min)
        return left_margin + frac * chart_w

    # Рядки (label, value, color, is_sleep)
    rows = [
        ("ESP32 deep-sleep\n(МК спить)", 5.0, NEG, True),
        ("BME280 sleep\n(≈0.1 µA)", 0.1, FIELD, True),
        ("LIS3DH power-down\n(≈0.5 µA)", 0.5, FIELD, True),
        ("LIS3DH low-power\n10 Hz (≈2 µA)", 2.0, FIELD, True),
        ("BME280 forced\n(≈2.8 µA сер.)", 2.8, "#e67e22", False),
        ("BME280 normal\n(≈3.6 µA)", 3.6, POS, False),
        ("LIS3DH normal/HR\n(≈185 µA)", 185.0, POS, False),
    ]

    n = len(rows)
    bar_h = min(34, int(chart_h / n) - 8)
    spacing = chart_h / n

    parts = []

    # Фон
    parts.append(rect(left_margin, top, chart_w, chart_h, fill="#f9fafb", stroke=MUTED, sw=0.8, rx=4))

    # Сітка по лог-осі
    grid_vals = [0.1, 0.5, 1, 5, 10, 50, 100, 200]
    for gv in grid_vals:
        gx = x_for(gv)
        if left_margin <= gx <= left_margin + chart_w:
            parts.append(line(gx, top, gx, bottom, color="#d1d5db", sw=0.8, dash="3,3"))
            lbl = str(gv) if gv < 10 else str(int(gv))
            parts.append(text(gx, bottom + 16, lbl, size=10, color=MUTED, anchor="middle"))

    # Підпис осі
    parts.append(text(left_margin + chart_w / 2, bottom + 32, "Середній струм, µA (логарифмічна шкала)",
                      size=11, color=MUTED, anchor="middle"))

    # Смуги
    for i, (label, val, color, is_sleep) in enumerate(rows):
        cy = top + (i + 0.5) * spacing
        bx = left_margin + 2
        bw = max(x_for(val) - bx, 4)
        by = cy - bar_h / 2

        # Заливка смуги
        fill_c = "#eaf5f0" if is_sleep else "#fdecea"
        parts.append(rect(bx, by, bw, bar_h, fill=fill_c, stroke=color, sw=1.5, rx=3))

        # Значення справа від смуги
        vx = bx + bw + 6
        vlabel = ("%.1f" % val if val < 10 else "%d" % int(val)) + " µA"
        parts.append(text(vx, cy + 4, vlabel, size=10, color=color, anchor="start", bold=True))

        # Назва зліва
        lines_lbl = label.split("\n")
        fs = 11
        ly = cy - (len(lines_lbl) - 1) * fs * 0.65 + fs * 0.35
        for j, ln in enumerate(lines_lbl):
            dy = j * fs * 1.3
            parts.append(text(left_margin - 10, ly + dy, ln, size=fs, color=INK, anchor="end"))

    # Легенда
    leg_x = left_margin + chart_w - 200
    leg_y = top + 10
    parts.append(rect(leg_x - 8, leg_y - 8, 195, 52, fill=BG, stroke=MUTED, sw=0.8, rx=4))
    parts.append(rect(leg_x, leg_y + 2, 18, 13, fill="#eaf5f0", stroke=FIELD, sw=1.5, rx=2))
    parts.append(text(leg_x + 24, leg_y + 12, "sleep / power-down", size=11, color=INK, anchor="start"))
    parts.append(rect(leg_x, leg_y + 24, 18, 13, fill="#fdecea", stroke=POS, sw=1.5, rx=2))
    parts.append(text(leg_x + 24, leg_y + 34, "normal / active", size=11, color=INK, anchor="start"))

    # Стрілка-акцент: LIS3DH normal домінує
    arrow_x = x_for(185.0) + 22
    arrow_y = top + 6 * spacing + bar_h / 2 + 4
    tb, tw, th = textbox(arrow_x + 80, arrow_y - 18,
                         "ОДИН давач у normal\n> весь сплячий МК!",
                         size=11, fill="#fff3cd", stroke="#e67e22", sw=1.5, color="#7d4900", bold=True)
    parts.append(tb)
    parts.append(arrow(arrow_x + 10, arrow_y, arrow_x + 80 - tw / 2 - 4, arrow_y - 12, color="#e67e22"))

    render(os.path.join(OUT, "fig-r13-2c-1-standby-map.svg"), W, H,
           *parts,
           title="Рис. 4.13.2c.1. Карта струму: МК спить — давачі можуть ні")


# ─────────────────────────────────────────────────────────────────────────────
# Рис. 4.13.2c.2 — Стейт-машина режимів давача
# Три вузли: sleep/power-down, forced/one-shot, normal/continuous
# ─────────────────────────────────────────────────────────────────────────────
def fig2_mode_states():
    W, H = 720, 420
    parts = []

    # Координати вузлів
    nodes = {
        "sleep":   (130, 210),
        "forced":  (380, 80),
        "normal":  (380, 340),
    }

    node_labels = {
        "sleep":  "sleep / power-down\nBME: ≈0.1 µA\nLIS: ≈0.5 µA",
        "forced": "forced / one-shot\n(один вимір)\n≈ кілька µA сер.",
        "normal": "normal / continuous\nBME: ≈3.6 µA\nLIS: ≈185 µA",
    }
    node_colors = {
        "sleep":  FIELD,
        "forced": "#e67e22",
        "normal": POS,
    }
    node_fills = {
        "sleep":  "#eaf5f0",
        "forced": "#fef0e0",
        "normal": "#fdecea",
    }

    NODE_W, NODE_H = 188, 70

    # Малюємо вузли
    for key, (cx, cy) in nodes.items():
        bx = cx - NODE_W / 2
        by = cy - NODE_H / 2
        parts.append(rect(bx, by, NODE_W, NODE_H, fill=node_fills[key],
                          stroke=node_colors[key], sw=2, rx=10))
        lines_lbl = node_labels[key].split("\n")
        fs = 12
        ly = cy - (len(lines_lbl) - 1) * fs * 0.65 + fs * 0.35
        for j, ln in enumerate(lines_lbl):
            dy = j * fs * 1.3
            bold_flag = (j == 0)
            parts.append(text(cx, ly + dy, ln, size=fs, color=node_colors[key],
                               anchor="middle", bold=bold_flag))

    # Допоміжна: кінці ребер від країв вузлів
    def edge_pt(src_key, dst_key, offset=0):
        sx, sy = nodes[src_key]
        dx, dy = nodes[dst_key]
        # Визначаємо точку виходу з src і входу в dst (з боку прямокутника)
        angle = math.atan2(dy - sy, dx - sx)
        # Виходимо з src
        ex = sx + (NODE_W / 2 + 4) * math.cos(angle)
        ey = sy + (NODE_H / 2 + 4) * math.sin(angle)
        # Входимо в dst
        ix = dx - (NODE_W / 2 + 4) * math.cos(angle)
        iy = dy - (NODE_H / 2 + 4) * math.sin(angle)
        return (ex + offset * math.sin(angle), ey - offset * math.cos(angle),
                ix + offset * math.sin(angle), iy - offset * math.cos(angle))

    # sleep → forced (вгору-вправо), labeled
    ex, ey, ix, iy = edge_pt("sleep", "forced", offset=14)
    parts.append(arrow(ex, ey, ix, iy, color=FIELD))
    # підпис на середині
    mx, my = (ex + ix) / 2 - 10, (ey + iy) / 2 - 8
    tb, tw, th = textbox(mx, my, "BME: 0xF4←0x01\nLIS: 0x20←0x17", size=10,
                         fill="#f0faf4", stroke=FIELD, sw=1, color="#155724")
    parts.append(tb)

    # forced → sleep (зворотна петля з написом)
    ex2, ey2, ix2, iy2 = edge_pt("forced", "sleep", offset=-14)
    parts.append(arrow(ex2, ey2, ix2, iy2, color="#e67e22"))
    mx2, my2 = (ex2 + ix2) / 2 + 8, (ey2 + iy2) / 2 + 14
    tb2, tw2, th2 = textbox(mx2, my2,
                             "прокинувся на 1 вимір\nі сам заснув",
                             size=10, fill="#fef0e0", stroke="#e67e22", sw=1.2,
                             color="#7d4900", bold=True)
    parts.append(tb2)

    # sleep → normal (вниз-вправо)
    ex3, ey3, ix3, iy3 = edge_pt("sleep", "normal", offset=-14)
    parts.append(arrow(ex3, ey3, ix3, iy3, color=FIELD))
    mx3, my3 = (ex3 + ix3) / 2 - 8, (ey3 + iy3) / 2 + 10
    tb3, tw3, th3 = textbox(mx3, my3, "BME: 0xF4←0xB7\nLIS: 0x20←0x5F", size=10,
                             fill="#f0faf4", stroke=FIELD, sw=1, color="#155724")
    parts.append(tb3)

    # normal → sleep
    ex4, ey4, ix4, iy4 = edge_pt("normal", "sleep", offset=14)
    parts.append(arrow(ex4, ey4, ix4, iy4, color=POS))
    mx4, my4 = (ex4 + ix4) / 2 + 4, (ey4 + iy4) / 2 - 10
    tb4, tw4, th4 = textbox(mx4, my4, "BME: 0xF4←0x00\nLIS: 0x20←0x00", size=10,
                             fill="#fdecea", stroke=POS, sw=1, color="#7d0000")
    parts.append(tb4)

    # forced ↔ normal — прямий двосторонній (спрощений)
    fn_x1 = nodes["forced"][0] + NODE_W / 2 + 2
    fn_y1 = nodes["forced"][1]
    fn_x2 = nodes["normal"][0] + NODE_W / 2 + 2
    fn_y2 = nodes["normal"][1]
    parts.append(line(fn_x1, fn_y1, fn_x2, fn_y2, color=MUTED, sw=1.0, dash="4,4"))
    parts.append(text((fn_x1 + fn_x2) / 2 + 44, (fn_y1 + fn_y2) / 2,
                      "змінити ODR/mode", size=10, color=MUTED, anchor="middle"))

    # Легенда вгорі-право
    leg_x, leg_y = W - 170, 16
    parts.append(rect(leg_x - 6, leg_y - 6, 155, 72, fill=BG, stroke=MUTED, sw=0.7, rx=4))
    for i, (lcolor, lfill, lname) in enumerate([
        (FIELD,     "#eaf5f0", "sleep (економно)"),
        ("#e67e22", "#fef0e0", "forced (один вимір)"),
        (POS,       "#fdecea", "normal (ненажерливо)"),
    ]):
        ly = leg_y + 2 + i * 22
        parts.append(rect(leg_x, ly, 16, 13, fill=lfill, stroke=lcolor, sw=1.5, rx=2))
        parts.append(text(leg_x + 22, ly + 10, lname, size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "fig-r13-2c-2-mode-states.svg"), W, H,
           *parts,
           title="Рис. 4.13.2c.2. Режими давача: один байт у регістрі — різниця на порядки")


if __name__ == "__main__":
    fig1_standby_map()
    print("  fig-r13-2c-1-standby-map.svg — готово")
    fig2_mode_states()
    print("  fig-r13-2c-2-mode-states.svg — готово")
    print("Усі SVG записано в ./img/")
