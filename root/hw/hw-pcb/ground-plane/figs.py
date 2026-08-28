# -*- coding: utf-8 -*-
"""Фігури до статті «Шар землі (ground plane)» (hw-pcb/ground-plane).
Дві фігури:
  1. return-current-density.svg — Просторовий розподіл густини високочастотного зворотного струму під сигнальною доріжкою (лоренціан, зони h, 3h, 10h).
  2. ground-slot-antenna.svg    — Перетин розриву в шарі землі: роздуття петлі зворотного струму, паразитна індуктивність та випромінювання антени.

Запуск: python figs.py
"""
import sys, os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. return-current-density.svg — Return current density distribution (Lorentzian)
# ════════════════════════════════════════════════════════════════════════════
def fig_return_current_density():
    W, H = 880, 520
    f = []

    f.append(text(W / 2, 28, "РОЗПОДІЛ ГУСТИНИ ЗВОРОТНОГО СТРУМУ В ОПОРНОМУ ШАРІ ЗЕМЛІ", size=15, bold=True, color=INK))

    # Верхня частина: Графік функції J(x) = (I0 / (pi * h)) / (1 + (x/h)^2)
    gx0, gy0 = 80, 250   # Початок координат графіка (x=0 на осі X, gy0 — нуль по Y)
    gw, gh = 720, 170
    cx = gx0 + gw / 2    # Центр осі x (x = 0)
    cy_base = gy0        # Базова лінія (J = 0)
    scale_h = 36         # 1 h = 36 px
    max_j_px = 140       # Пік J(0) = 140 px

    # Фон графіка
    f.append(rect(gx0 - 30, gy0 - gh - 35, gw + 60, gh + 55, fill="#fdfefe", stroke="#d0d7de", sw=1.0, rx=6))

    # Зони інтегрування під кривою (зафарбовані смуги)
    x_1h = scale_h
    x_3h = 3 * scale_h
    x_6h = 6 * scale_h

    # Полігони заливки під кривою
    def get_curve_points(xmin, xmax, step=2):
        pts = []
        cur_x = xmin
        while cur_x <= xmax:
            norm_x = (cur_x - cx) / scale_h
            norm_j = 1.0 / (1.0 + norm_x * norm_x)
            py = cy_base - norm_j * max_j_px
            pts.append((cur_x, py))
            cur_x += step
        return pts

    # Малювання зон
    # Зовнішня зона 3h..6h
    pts_left3 = get_curve_points(cx - x_6h, cx - x_3h)
    poly_left3 = " ".join(["%.1f,%.1f" % (cx - x_6h, cy_base)] + ["%.1f,%.1f" % p for p in pts_left3] + ["%.1f,%.1f" % (cx - x_3h, cy_base)])
    f.append('<polygon points="%s" fill="#e8f4f8" opacity="0.8"/>' % poly_left3)

    pts_right3 = get_curve_points(cx + x_3h, cx + x_6h)
    poly_right3 = " ".join(["%.1f,%.1f" % (cx + x_3h, cy_base)] + ["%.1f,%.1f" % p for p in pts_right3] + ["%.1f,%.1f" % (cx + x_6h, cy_base)])
    f.append('<polygon points="%s" fill="#e8f4f8" opacity="0.8"/>' % poly_right3)

    # Зона 1h..3h
    pts_left2 = get_curve_points(cx - x_3h, cx - x_1h)
    poly_left2 = " ".join(["%.1f,%.1f" % (cx - x_3h, cy_base)] + ["%.1f,%.1f" % p for p in pts_left2] + ["%.1f,%.1f" % (cx - x_1h, cy_base)])
    f.append('<polygon points="%s" fill="#cce5f4" opacity="0.85"/>' % poly_left2)

    pts_right2 = get_curve_points(cx + x_1h, cx + x_3h)
    poly_right2 = " ".join(["%.1f,%.1f" % (cx + x_1h, cy_base)] + ["%.1f,%.1f" % p for p in pts_right2] + ["%.1f,%.1f" % (cx + x_3h, cy_base)])
    f.append('<polygon points="%s" fill="#cce5f4" opacity="0.85"/>' % poly_right2)

    # Центральна зона |x| <= 1h
    pts_mid = get_curve_points(cx - x_1h, cx + x_1h)
    poly_mid = " ".join(["%.1f,%.1f" % (cx - x_1h, cy_base)] + ["%.1f,%.1f" % p for p in pts_mid] + ["%.1f,%.1f" % (cx + x_1h, cy_base)])
    f.append('<polygon points="%s" fill="#90c7ea" opacity="0.9"/>' % poly_mid)

    # Сама лінія графіка J(x)
    all_pts = get_curve_points(cx - 300, cx + 300, step=1)
    polyline_str = " ".join(["%.1f,%.1f" % p for p in all_pts])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (polyline_str, NEG))

    # Осі графіка
    f.append(line(gx0 - 15, cy_base, gx0 + gw + 15, cy_base, color=LINE, sw=1.5))
    f.append(line(cx, cy_base + 5, cx, cy_base - max_j_px - 25, color=LINE, sw=1.2, dash="3,3"))

    # Позначки по осі X
    for kh, lbl in [(-3, "−3h"), (-1, "−h"), (0, "0"), (1, "+h"), (3, "+3h")]:
        px = cx + kh * scale_h
        f.append(line(px, cy_base - 3, px, cy_base + 4, color=LINE, sw=1.2))
        f.append(text(px, cy_base + 17, lbl, size=11, bold=(kh == 0), color=INK))

    # Підписи осей
    f.append(text(gx0 + gw + 20, cy_base + 4, "x (відстань від осі)", size=11, italic=True, color=MUTED, anchor="start"))
    f.append(text(cx + 10, cy_base - max_j_px - 15, "J(0) = I₀ / (π·h)", size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(cx + 10, cy_base - max_j_px - 3, "Густина струму J(x)", size=10, color=MUTED, anchor="start"))

    # Текстові мітки зон інтегрування
    f.append(text(cx, cy_base - max_j_px * 0.35, "50% струму", size=12, bold=True, color="#0b407a"))
    f.append(text(cx, cy_base - max_j_px * 0.35 + 15, "(смуга |x| ≤ h)", size=10, color="#0b407a"))

    f.append(text(cx - 2.0 * scale_h, cy_base - max_j_px * 0.18, "15%", size=11, bold=True, color="#125699"))
    f.append(text(cx + 2.0 * scale_h, cy_base - max_j_px * 0.18, "15%", size=11, bold=True, color="#125699"))
    f.append(text(cx + 2.1 * scale_h, cy_base - max_j_px * 0.18 + 14, "разом 80%", size=9, italic=True, color="#125699"))

    # Нижня частина: Поперечний переріз друкованої плати (Фізика)
    py_cs = 340
    f.append(rect(gx0 - 30, py_cs, gw + 60, 155, fill="#f8fafc", stroke="#d0d7de", sw=1.0, rx=6))
    f.append(text(gx0 - 15, py_cs + 22, "ПОПЕРЕЧНИЙ ПЕРЕРІЗ ДРУКОВАНОЇ ПЛАТИ (Microstrip)", size=12, bold=True, color=INK, anchor="start"))

    # Діелектрик плати (FR-4)
    diel_w = 400
    diel_x = cx - 110 - diel_w / 2
    diel_y = py_cs + 52
    diel_h = 42
    f.append(rect(diel_x, diel_y, diel_w, diel_h, fill="#eaf4dc", stroke="#82b366", sw=1.2, rx=2))
    f.append(text(diel_x + 15, diel_y + 25, "Діелектрик (FR-4, εᵣ ≈ 4.2)", size=10, color="#3d6b1d", anchor="start"))

    # Товщина діелектрика h
    dim_x = diel_x + 30
    f.append(line(dim_x, diel_y, dim_x, diel_y + diel_h, color="#3d6b1d", sw=1.2))
    f.append(line(dim_x - 4, diel_y, dim_x + 4, diel_y, color="#3d6b1d", sw=1.2))
    f.append(line(dim_x - 4, diel_y + diel_h, dim_x + 4, diel_y + diel_h, color="#3d6b1d", sw=1.2))
    f.append(text(dim_x - 8, diel_y + 25, "h", size=12, bold=True, color="#3d6b1d", anchor="end"))

    # Сигнальна доріжка зверху (Top layer)
    cs_cx = cx - 110
    trace_w = 40
    trace_h = 8
    f.append(rect(cs_cx - trace_w / 2, diel_y - trace_h, trace_w, trace_h, fill="#f8cecc", stroke=POS, sw=1.5, rx=1))
    f.append(text(cs_cx, diel_y - trace_h - 6, "Сигнальна доріжка (+I₀)", size=11, bold=True, color=POS))

    # Точка/хрестик у доріжці
    f.append(circle(cs_cx, diel_y - trace_h / 2, 3, fill=POS, stroke=POS, sw=1))

    # Опорний шар землі знизу (Ground Plane)
    gnd_h = 10
    gnd_y = diel_y + diel_h
    f.append(rect(diel_x, gnd_y, diel_w, gnd_h, fill="#dae8fc", stroke=NEG, sw=1.5, rx=1))
    f.append(text(diel_x + 15, gnd_y + 24, "Опорний шар землі (GND Plane)", size=10, bold=True, color=NEG, anchor="start"))

    # Стрілки концентрації зворотного струму в шарі землі
    f.append(circle(cs_cx, gnd_y + gnd_h / 2, 3.5, fill=NEG, stroke=NEG, sw=1))
    f.append(circle(cs_cx - 18, gnd_y + gnd_h / 2, 2.5, fill=NEG, stroke=NEG, sw=1))
    f.append(circle(cs_cx + 18, gnd_y + gnd_h / 2, 2.5, fill=NEG, stroke=NEG, sw=1))
    f.append(circle(cs_cx - 36, gnd_y + gnd_h / 2, 1.8, fill=NEG, stroke=NEG, sw=1))
    f.append(circle(cs_cx + 36, gnd_y + gnd_h / 2, 1.8, fill=NEG, stroke=NEG, sw=1))

    # Пояснювальний блок праворуч
    tb_exp, _, _ = textbox(cx + 240, py_cs + 82, "Зворотний струм стягується під доріжку:\n• Мінімізація площі петлі\n• Зниження індуктивності L_loop\n• Взаємне гасіння полів (+I та −I)", size=10, pad=8, fill="#ffffff", stroke="#d0d7de", sw=1.0, color=INK)
    f.append(tb_exp)

    render(os.path.join(IMG, "return-current-density.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. ground-slot-antenna.svg — Slot in ground plane, return current detour, EMI
# ════════════════════════════════════════════════════════════════════════════
def fig_ground_slot_antenna():
    W, H = 880, 500
    f = []

    f.append(text(W / 2, 28, "ПЕРЕТИН РОЗРИВУ В ШАРІ ЗЕМЛІ: РОЗДУТТЯ ПЕТЛІ ТА ВИПРОМІНЮВАННЯ", size=15, bold=True, color=INK))

    # Ліва панель: Ідеальний нерозривний шар землі
    lw, lh = 390, 420
    lx, ly = 35, 55

    f.append(rect(lx, ly, lw, lh, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    f.append(text(lx + lw / 2, ly + 25, "НЕРОЗРИВНИЙ ШАР ЗЕМЛІ (Правильно)", size=13, bold=True, color=FIELD))
    f.append(text(lx + lw / 2, ly + 43, "Мінімальна петля, ідеальна компенсація полів", size=10, color=MUTED))

    # Суцільна мідна площина
    gnd_lx, gnd_ly, gnd_lw, gnd_lh = lx + 25, ly + 65, lw - 50, 230
    f.append(rect(gnd_lx, gnd_ly, gnd_lw, gnd_lh, fill="#eaf2f8", stroke="#84a9c0", sw=1.2, rx=4))
    f.append(text(gnd_lx + gnd_lw / 2, gnd_ly + 18, "Суцільний шар GND (Solid Ground Plane)", size=10, bold=True, color="#486581"))

    # Сигнальна доріжка (пряма червона лінія)
    sig_y = gnd_ly + 115
    f.append(line(gnd_lx + 20, sig_y, gnd_lx + gnd_lw - 20, sig_y, color=POS, sw=3.0))
    f.append(arrow(gnd_lx + 40, sig_y, gnd_lx + 90, sig_y, color=POS, sw=2.2))
    f.append(circle(gnd_lx + 20, sig_y, 5, fill=POS, stroke=LINE, sw=1.2))
    f.append(circle(gnd_lx + gnd_lw - 20, sig_y, 5, fill=POS, stroke=LINE, sw=1.2))
    f.append(text(gnd_lx + 40, sig_y - 12, "Сигнал (+I)", size=11, bold=True, color=POS, anchor="start"))

    # Зворотний струм (пунктир під доріжкою)
    f.append(line(gnd_lx + gnd_lw - 20, sig_y + 12, gnd_lx + 20, sig_y + 12, color=NEG, sw=2.5, dash="4,3"))
    f.append(arrow(gnd_lx + gnd_lw - 60, sig_y + 12, gnd_lx + gnd_lw - 110, sig_y + 12, color=NEG, sw=2.0))
    f.append(text(gnd_lx + gnd_lw - 35, sig_y + 26, "Зворотний струм (−I) суворо під трасою", size=10, bold=True, color=NEG, anchor="end"))

    # Підсумок для ідеального шару
    tb1, _, _ = textbox(lx + lw / 2, ly + 350, "Площа петлі: S ≈ довжина · h (мінімум)\nПаразитна індуктивність: L_loop < 1–2 нГн\nВипромінювання EMI: придушене (гасіння полів)", size=11, pad=10, fill="#f4faf6", stroke=FIELD, sw=1.2, color="#1b4d2e")
    f.append(tb1)

    # Права панель: Розрив у шарі землі (Slot / Split)
    rx = lx + lw + 20
    f.append(rect(rx, ly, lw, lh, fill="#fdfefe", stroke=LINE, sw=1.2, rx=8))
    f.append(text(rx + lw / 2, ly + 25, "РОЗРИВ У ШАРІ ЗЕМЛІ (Катастрофа)", size=13, bold=True, color=POS))
    f.append(text(rx + lw / 2, ly + 43, "Роздуття петлі, стрибок імпедансу, випромінювання", size=10, color=MUTED))

    # Площина з розрізом
    gnd_rx, gnd_ry = rx + 25, ly + 65
    f.append(rect(gnd_rx, gnd_ry, gnd_lw, gnd_lh, fill="#eaf2f8", stroke="#84a9c0", sw=1.2, rx=4))

    # Виріз (щілина / slot у міді)
    slot_w, slot_h = 16, 150
    slot_x = gnd_rx + gnd_lw / 2 - slot_w / 2
    slot_y = gnd_ry + 40
    f.append(rect(slot_x, slot_y, slot_w, slot_h, fill="#ffffff", stroke=POS, sw=1.5, rx=2))
    f.append(text(slot_x + slot_w / 2, slot_y + slot_h / 2, "РОЗРИВ", size=9, bold=True, color=POS))

    # Сигнальна доріжка перетинає розріз
    f.append(line(gnd_rx + 20, sig_y, gnd_rx + gnd_lw - 20, sig_y, color=POS, sw=3.0))
    f.append(arrow(gnd_rx + 40, sig_y, gnd_rx + 90, sig_y, color=POS, sw=2.2))
    f.append(circle(gnd_rx + 20, sig_y, 5, fill=POS, stroke=LINE, sw=1.2))
    f.append(circle(gnd_rx + gnd_lw - 20, sig_y, 5, fill=POS, stroke=LINE, sw=1.2))
    f.append(text(gnd_rx + 40, sig_y - 12, "Сигнал (+I)", size=11, bold=True, color=POS, anchor="start"))

    # Зворотний струм змушений обходити щілину довкола її країв
    detour_top = [
        (gnd_rx + gnd_lw - 20, sig_y + 12),
        (slot_x + slot_w + 10, sig_y + 12),
        (slot_x + slot_w + 10, slot_y - 8),
        (slot_x - 10, slot_y - 8),
        (slot_x - 10, sig_y + 12),
        (gnd_rx + 20, sig_y + 12)
    ]
    detour_str = " ".join(["%.1f,%.1f" % p for p in detour_top])
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="4,3"/>' % (detour_str, NEG))
    f.append(arrow(slot_x + slot_w + 10, slot_y + 15, slot_x + slot_w + 10, slot_y - 4, color=NEG, sw=2.0))
    f.append(arrow(slot_x + 5, slot_y - 8, slot_x - 6, slot_y - 8, color=NEG, sw=2.0))
    f.append(text(slot_x + slot_w / 2, slot_y - 16, "Обхід розриву", size=10, bold=True, color=NEG))

    # Випромінювання антени (хвилі EMI)
    wave_cx, wave_cy = slot_x + slot_w / 2, sig_y - 30
    f.append('<path d="M %.1f,%.1f A 25,25 0 0,1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="2,2"/>' % (wave_cx - 15, wave_cy - 10, wave_cx + 15, wave_cy - 10, POS))
    f.append('<path d="M %.1f,%.1f A 40,40 0 0,1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="3,2"/>' % (wave_cx - 28, wave_cy - 20, wave_cx + 28, wave_cy - 20, POS))
    f.append('<path d="M %.1f,%.1f A 55,55 0 0,1 %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.0" stroke-dasharray="4,3"/>' % (wave_cx - 40, wave_cy - 30, wave_cx + 40, wave_cy - 30, POS))
    f.append(text(wave_cx, wave_cy - 48, "Випромінювання EMI (Щілинна антена)", size=10, bold=True, color=POS))

    # Підсумок для розриву
    tb2, _, _ = textbox(rx + lw / 2, ly + 350, "Площа петлі роздувається в 50–100 разів!\nПаразитна індуктивність зростає до 20–80 нГн\nСтрибок імпедансу, відбиття, завал фронту, EMI", size=11, pad=10, fill="#fdf3f2", stroke=POS, sw=1.2, color="#781d18")
    f.append(tb2)

    render(os.path.join(IMG, "ground-slot-antenna.svg"), W, H, *f)


if __name__ == "__main__":
    fig_return_current_density()
    fig_ground_slot_antenna()
    print("Фігури успішно згенеровано в теці img/")
