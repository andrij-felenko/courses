# -*- coding: utf-8 -*-
"""Фігури до статті «Шлях зворотного струму» (hw-pcb/current-return-path).
П'ять фігур:
  1. dc-vs-rf-return.svg              — Постійний струм (шлях найменшого R) проти високочастотного (шлях найменшого L)
  2. current-density-lorentz.svg       — Розподіл густини зворотного струму в опорній площині (лоренціан, смуги h і 3h)
  3. split-plane-detour.svg           — Перетин доріжкою розрізу в площині землі: роздуття петлі та випромінювання
  4. layer-transition-return-via.svg  — Перехід між шарами: без return via (велика петля) проти з виділеним return via
  5. differential-pair-return.svg     — Зворотний струм диференційної пари над площиною та розпад на синфазну моду

Запуск: python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ════════════════════════════════════════════════════════════════════════════
# 1. dc-vs-rf-return.svg — DC vs RF return path
# ════════════════════════════════════════════════════════════════════════════
def fig_dc_vs_rf():
    W, H = 840, 400
    f = []

    f.append(text(W / 2, 28, "ШЛЯХ ЗВОРОТНОГО СТРУМУ: ПОСТІЙНИЙ СТРУМ ПРОТИ ВИСОКОЧАСТОТНОГО", size=14, bold=True, color=INK))

    # Ліва панель: DC
    lx, ly, lw, lh = 30, 50, 375, 325
    f.append(rect(lx, ly, lw, lh, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(lx + lw / 2, ly + 25, "Постійний струм (DC / низька частота)", size=13, bold=True, color=INK))
    f.append(text(lx + lw / 2, ly + 43, "Z ≈ R  —  шлях найменшого активного опору", size=11, color=MUTED))

    p_src_x, p_src_y = lx + 50, ly + 105
    p_dst_x, p_dst_y = lx + lw - 50, ly + 230

    # Опорна площина (фон)
    f.append(rect(lx + 20, ly + 65, lw - 40, 200, fill="#eaf2f8", stroke="#9fc2d6", sw=1.2, rx=4))
    f.append(text(lx + lw / 2, ly + 80, "Суцільна площина землі (GND Plane)", size=10, color="#5b8296"))

    # Широкий розлив струму (веєр прямих ліній між навантаженням і джерелом)
    f.append(line(p_dst_x, p_dst_y, p_src_x, p_src_y, color=NEG, sw=2.5, dash="4,4"))
    f.append(arrow(p_dst_x - 40, ly + 190, p_src_x + 40, ly + 140, color=NEG, sw=2.0))
    f.append(text(lx + lw / 2 - 25, ly + 175, "Зворот розтікається по прямій", size=10, bold=True, color=NEG))

    # Сигнальна доріжка зверху (червона з вигином)
    f.append(line(p_src_x, p_src_y, lx + lw - 100, p_src_y, color=POS, sw=3.0))
    f.append(line(lx + lw - 100, p_src_y, lx + lw - 100, p_dst_y, color=POS, sw=3.0))
    f.append(line(lx + lw - 100, p_dst_y, p_dst_x, p_dst_y, color=POS, sw=3.0))
    f.append(arrow(lx + 80, p_src_y, lx + 140, p_src_y, color=POS, sw=2.2))
    f.append(text(lx + 130, p_src_y - 12, "Сигнал (доріжка)", size=10, bold=True, color=POS))

    # Вузли
    f.append(circle(p_src_x, p_src_y, 6, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(p_src_x, p_src_y - 12, "Джерело", size=10, bold=True, color=INK))
    f.append(circle(p_dst_x, p_dst_y, 6, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(p_dst_x, p_dst_y + 18, "Навантаження", size=10, bold=True, color=INK))

    f.append(text(lx + lw / 2, ly + 285, "Петля струму ВЕЛИКА, але на DC індуктивність", size=10, color=INK))
    f.append(text(lx + lw / 2, ly + 302, "не створює реактивного спадання напруги", size=10, color=MUTED))

    # Права панель: RF/High Frequency
    rx = lx + lw + 30
    f.append(rect(rx, ly, lw, lh, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(rx + lw / 2, ly + 25, "Висока частота (RF / фронти > 50–100 кГц)", size=13, bold=True, color=INK))
    f.append(text(rx + lw / 2, ly + 43, "Z ≈ jωL  —  шлях найменшої індуктивності", size=11, color=MUTED))

    # Опорна площина
    f.append(rect(rx + 20, ly + 65, lw - 40, 200, fill="#eaf2f8", stroke="#9fc2d6", sw=1.2, rx=4))
    f.append(text(rx + lw / 2, ly + 80, "Суцільна площина землі (GND Plane)", size=10, color="#5b8296"))

    p_src_rx, p_src_ry = rx + 50, ly + 105
    p_dst_rx, p_dst_ry = rx + lw - 50, ly + 230

    # Зворотний струм суворо під сигнальною доріжкою (синя смуга прямо під трасою)
    f.append(line(p_dst_rx, p_dst_ry, rx + lw - 100, p_dst_ry, color=NEG, sw=2.5, dash="4,3"))
    f.append(line(rx + lw - 100, p_dst_ry, rx + lw - 100, p_src_ry, color=NEG, sw=2.5, dash="4,3"))
    f.append(line(rx + lw - 100, p_src_ry, p_src_rx, p_src_ry, color=NEG, sw=2.5, dash="4,3"))
    f.append(arrow(rx + lw - 100, ly + 180, rx + lw - 100, ly + 140, color=NEG, sw=2.0))
    f.append(text(rx + lw - 108, ly + 160, "Зворот під трасою", size=10, bold=True, color=NEG, anchor="end"))

    # Сигнальна доріжка зверху (червона з вигином)
    f.append(line(p_src_rx, p_src_ry, rx + lw - 100, p_src_ry, color=POS, sw=3.0))
    f.append(line(rx + lw - 100, p_src_ry, rx + lw - 100, p_dst_ry, color=POS, sw=3.0))
    f.append(line(rx + lw - 100, p_dst_ry, p_dst_rx, p_dst_ry, color=POS, sw=3.0))
    f.append(arrow(rx + 80, p_src_ry, rx + 140, p_src_ry, color=POS, sw=2.2))
    f.append(text(rx + 130, p_src_ry - 12, "Сигнал (доріжка)", size=10, bold=True, color=POS))

    # Вузли
    f.append(circle(p_src_rx, p_src_ry, 6, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(p_src_rx, p_src_ry - 12, "Джерело", size=10, bold=True, color=INK))
    f.append(circle(p_dst_rx, p_dst_ry, 6, fill=POS, stroke=LINE, sw=1.5))
    f.append(text(p_dst_rx, p_dst_ry + 18, "Навантаження", size=10, bold=True, color=INK))

    f.append(text(rx + lw / 2, ly + 285, "Петля МІНІМАЛЬНА: взаємна індуктивність M", size=10, bold=True, color=FIELD))
    f.append(text(rx + lw / 2, ly + 302, "компенсує магнітний потік (L_loop = L1+L2−2M → min)", size=10, color=MUTED))

    render(os.path.join(IMG, "dc-vs-rf-return.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. current-density-lorentz.svg — Lorentzian distribution in ground plane
# ════════════════════════════════════════════════════════════════════════════
def fig_lorentz():
    W, H = 800, 370
    f = []

    f.append(text(W / 2, 26, "РОЗПОДІЛ ГУСТИНИ ВИСОКОЧАСТОТНОГО ЗВОРОТНОГО СТРУМУ В ПЛОЩИНІ", size=14, bold=True, color=INK))

    cx = W / 2
    tr_w, tr_h = 50, 14
    tr_y = 65
    f.append(rect(cx - tr_w / 2, tr_y, tr_w, tr_h, fill="#ffcccc", stroke=POS, sw=2, rx=2))
    f.append(text(cx, tr_y + 11, "Сигнал (+I)", size=10, bold=True, color=POS))

    # Діелектрик між шарами
    diel_y = tr_y + tr_h
    diel_h = 45
    f.append(rect(cx - 270, diel_y, 540, diel_h, fill="#f9f9e8", stroke="#d8d8a0", sw=1.2, rx=2))
    f.append(text(cx - 200, diel_y + 27, "Діелектрик плати (FR-4, товщина h)", size=11, color="#8a8a50"))

    # Висота h
    f.append(line(cx + 140, diel_y, cx + 140, diel_y + diel_h, color=LINE, sw=1.5))
    f.append(line(cx + 135, diel_y, cx + 145, diel_y, color=LINE, sw=1.5))
    f.append(line(cx + 135, diel_y + diel_h, cx + 145, diel_y + diel_h, color=LINE, sw=1.5))
    f.append(text(cx + 155, diel_y + 27, "h", size=12, bold=True, color=INK))

    # Опорна площина землі (GND plane)
    gnd_y = diel_y + diel_h
    gnd_h = 14
    f.append(rect(cx - 270, gnd_y, 540, gnd_h, fill="#d6e4f0", stroke="#4a89dc", sw=1.5, rx=2))
    f.append(text(cx - 200, gnd_y + 11, "Площина землі (GND, зворот −I)", size=10, bold=True, color="#2b5994"))

    # Графік густини струму J(x) під площиною
    base_y = gnd_y + gnd_h + 120
    # Вісь X
    f.append(line(cx - 280, base_y, cx + 280, base_y, color=LINE, sw=1.5))
    f.append(arrow(cx + 270, base_y, cx + 285, base_y, color=LINE, sw=1.5))
    f.append(text(cx + 295, base_y + 4, "x", size=12, bold=True, color=INK))

    # Вісь Y (по центру під доріжкою)
    f.append(line(cx, base_y, cx, base_y - 110, color=LINE, sw=1.5, dash="3,3"))
    f.append(arrow(cx, base_y - 95, cx, base_y - 112, color=LINE, sw=1.5))
    f.append(text(cx, base_y - 118, "Густина струму J(x)", size=11, bold=True, color=INK))

    # Лоренціан
    hp = 38.0
    pts = []
    for xi in range(-260, 261, 5):
        val = 90.0 / (1.0 + (xi / hp) ** 2)
        pts.append((cx + xi, base_y - val))

    poly_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    f.append(f'<polygon points="{cx - 260:.1f},{base_y:.1f} {poly_pts} {cx + 260:.1f},{base_y:.1f}" fill="#d9e8fb" stroke="none"/>')
    f.append(f'<polyline points="{poly_pts}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Смуга ±h (50% струму)
    f.append(line(cx - hp, base_y, cx - hp, base_y - 45, color="#2b5994", sw=1.2, dash="3,3"))
    f.append(line(cx + hp, base_y, cx + hp, base_y - 45, color="#2b5994", sw=1.2, dash="3,3"))
    f.append(text(cx, base_y - 25, "50 % струму", size=10, bold=True, color=NEG))
    f.append(text(cx - hp, base_y + 15, "−h", size=10, color=MUTED))
    f.append(text(cx + hp, base_y + 15, "+h", size=10, color=MUTED))

    # Смуга ±3h (80% струму)
    f.append(line(cx - 3 * hp, base_y, cx - 3 * hp, base_y - 10, color="#8a8a8a", sw=1.2, dash="2,2"))
    f.append(line(cx + 3 * hp, base_y, cx + 3 * hp, base_y - 10, color="#8a8a8a", sw=1.2, dash="2,2"))
    f.append(text(cx - 3 * hp, base_y + 15, "−3h", size=10, color=MUTED))
    f.append(text(cx + 3 * hp, base_y + 15, "+3h", size=10, color=MUTED))
    f.append(text(cx + 2.0 * hp, base_y - 15, "80 % у смузі ±3h", size=10, bold=True, color="#2b5994"))

    # Формула збоку
    f.append(text(cx - 190, base_y - 75, "J(x) = I₀ / (π·h · (1 + (x/h)²))", size=11, bold=True, color=INK))
    f.append(text(cx - 190, base_y - 58, "Лоренцівський профіль густини", size=10, color=MUTED))

    render(os.path.join(IMG, "current-density-lorentz.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. split-plane-detour.svg — Crossing a split ground plane
# ════════════════════════════════════════════════════════════════════════════
def fig_split_plane():
    W, H = 840, 380
    f = []

    f.append(text(W / 2, 26, "ПЕРЕТИН РОЗРІЗУ В ПЛОЩИНІ ЗЕМЛІ: РОЗДУТТЯ ПЕТЛІ ТА EMI", size=14, bold=True, color=INK))

    gnd1_x, gnd1_w = 40, 350
    gnd_y, gnd_h = 60, 240
    slot_w = 40
    gnd2_x, gnd2_w = gnd1_x + gnd1_w + slot_w, 350

    # GND1
    f.append(rect(gnd1_x, gnd_y, gnd1_w, gnd_h, fill="#e8f0f8", stroke="#7da0c2", sw=1.5, rx=6))
    f.append(text(gnd1_x + 90, gnd_y + 24, "Площина GND 1", size=12, bold=True, color="#355e8a"))

    # GND2
    f.append(rect(gnd2_x, gnd_y, gnd2_w, gnd_h, fill="#e8f0f8", stroke="#7da0c2", sw=1.5, rx=6))
    f.append(text(gnd2_x + gnd2_w - 90, gnd_y + 24, "Площина GND 2", size=12, bold=True, color="#355e8a"))

    # Щілина (Slot / Split)
    slot_x = gnd1_x + gnd1_w
    f.append(rect(slot_x, gnd_y, slot_w, gnd_h, fill="#fff5f5", stroke=POS, sw=1.5, rx=2))
    f.append(mtext(slot_x + slot_w / 2, gnd_y + 110, ["РОЗРІЗ", "У МІДІ", "(ЩІЛИНА)"], size=10, bold=True, color=POS))

    # Доріжка сигналу прямо
    sig_y = gnd_y + 70
    f.append(line(gnd1_x + 30, sig_y, gnd2_x + gnd2_w - 30, sig_y, color=POS, sw=3.5))
    f.append(arrow(gnd1_x + 70, sig_y, gnd1_x + 120, sig_y, color=POS, sw=2.5))
    f.append(arrow(gnd2_x + 100, sig_y, gnd2_x + 150, sig_y, color=POS, sw=2.5))
    f.append(text(gnd1_x + 140, sig_y - 12, "Швидкісний сигнал (прямий шлях)", size=11, bold=True, color=POS))

    # Зворотний струм: обхід навколо щілини
    detour_y = gnd_y + gnd_h - 20
    f.append(line(gnd2_x + gnd2_w - 50, sig_y, gnd2_x + 15, sig_y, color=NEG, sw=2.8, dash="5,4"))
    f.append(line(gnd2_x + 15, sig_y, gnd2_x + 15, detour_y, color=NEG, sw=2.8, dash="5,4"))
    f.append(line(gnd2_x + 15, detour_y, gnd1_x + gnd1_w - 15, detour_y, color=NEG, sw=2.8, dash="5,4"))
    f.append(line(gnd1_x + gnd1_w - 15, detour_y, gnd1_x + gnd1_w - 15, sig_y, color=NEG, sw=2.8, dash="5,4"))
    f.append(line(gnd1_x + gnd1_w - 15, sig_y, gnd1_x + 50, sig_y, color=NEG, sw=2.8, dash="5,4"))

    # Стрілки обходу
    f.append(arrow(gnd2_x + 15, sig_y + 30, gnd2_x + 15, sig_y + 80, color=NEG, sw=2.2))
    f.append(arrow(gnd2_x + 10, detour_y, gnd1_x + gnd1_w - 10, detour_y, color=NEG, sw=2.2))
    f.append(arrow(gnd1_x + gnd1_w - 15, detour_y - 30, gnd1_x + gnd1_w - 15, detour_y - 80, color=NEG, sw=2.2))

    f.append(text(gnd2_x + 90, gnd_y + 160, "Зворотний струм огинає розріз", size=10, bold=True, color=NEG))

    # Напис роздутої петлі
    f.append(mtext(slot_x + slot_w / 2, gnd_y + 190, ["РОЗДУТА", "ПЛОЩА", "ПЕТЛІ (A)"], size=10, bold=True, color="#c0392b"))

    # Напис EMI
    f.append(text(slot_x + slot_w / 2, sig_y - 25, "Випромінювання EMI (радіозавади)", size=10, bold=True, color=POS))

    # Пояснення знизу
    f.append(text(W / 2, H - 40, "Наслідки: стрибок імпедансу Z₀ (дзвін), паразитна індуктивність ΔL (10–30 нГн)", size=11, bold=True, color=INK))
    f.append(text(W / 2, H - 22, "та випромінювання щілинної антени (провал сертифікації EMC / EMI)", size=11, color=MUTED))

    render(os.path.join(IMG, "split-plane-detour.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. layer-transition-return-via.svg — Layer transition with/without return via
# ════════════════════════════════════════════════════════════════════════════
def fig_layer_transition():
    W, H = 840, 400
    f = []

    f.append(text(W / 2, 26, "ПЕРЕХІД СИГНАЛУ МІЖ ШАРАМИ (VIA TRANSITION): БЕЗ І З RETURN VIA", size=14, bold=True, color=INK))

    # Ліва панель: Погано (без return via)
    lx, ly, lw, lh = 30, 50, 375, 325
    f.append(rect(lx, ly, lw, lh, fill="#fffafa", stroke="#e0a0a0", sw=1.5, rx=8))
    f.append(text(lx + lw / 2, ly + 25, "ПОМИЛКА: Немає зворотного via", size=12, bold=True, color=POS))

    y_l1 = ly + 65
    y_l2 = ly + 115
    y_l3 = ly + 165
    y_l4 = ly + 215

    # Лінії шарів
    f.append(line(lx + 20, y_l2, lx + lw - 20, y_l2, color="#5b8296", sw=3.0))
    f.append(text(lx + 45, y_l2 - 6, "L2: GND 1", size=10, bold=True, color="#2b5994"))

    f.append(line(lx + 20, y_l3, lx + lw - 20, y_l3, color="#b08050", sw=3.0))
    f.append(text(lx + 45, y_l3 - 6, "L3: GND 2", size=10, bold=True, color="#805020"))

    # Сигнальна лінія L1 -> Via -> L4
    f.append(line(lx + 50, y_l1, lx + 180, y_l1, color=POS, sw=2.5))
    f.append(line(lx + 180, y_l1, lx + 180, y_l4, color=POS, sw=3.5))
    f.append(line(lx + 180, y_l4, lx + lw - 50, y_l4, color=POS, sw=2.5))
    f.append(circle(lx + 180, y_l1, 4, fill=POS, stroke=LINE, sw=1.2))
    f.append(circle(lx + 180, y_l4, 4, fill=POS, stroke=LINE, sw=1.2))
    f.append(text(lx + 180, y_l1 - 10, "Сигнальний via", size=10, bold=True, color=POS))

    # Зворотний струм
    f.append(line(lx + 50, y_l2 + 6, lx + 165, y_l2 + 6, color=NEG, sw=2.2, dash="3,2"))
    f.append(line(lx + 165, y_l2 + 6, lx + lw - 40, y_l2 + 6, color=NEG, sw=2.2, dash="4,3"))
    f.append(line(lx + lw - 40, y_l2 + 6, lx + lw - 40, y_l3 - 6, color=NEG, sw=2.2, dash="4,3"))
    f.append(line(lx + lw - 40, y_l3 - 6, lx + 195, y_l3 - 6, color=NEG, sw=2.2, dash="4,3"))
    f.append(line(lx + 195, y_l3 - 6, lx + lw - 50, y_l3 - 6, color=NEG, sw=2.2, dash="3,2"))

    # Далекий перехід
    f.append(rect(lx + lw - 55, y_l2 - 5, 25, y_l3 - y_l2 + 10, fill="#f0f0f0", stroke=LINE, sw=1.2))
    f.append(mtext(lx + lw - 42, y_l2 + 28, ["Далекий", "via / C"], size=10, color=MUTED))

    f.append(text(lx + lw / 2, ly + 255, "Величезна розірвана петля між шарами!", size=10, bold=True, color=POS))
    f.append(text(lx + lw / 2, ly + 275, "Індуктивність переходу зростає до 2–5 нГн,", size=10, color=INK))
    f.append(text(lx + lw / 2, ly + 292, "викликаючи стрибок імпедансу та crosstalk", size=10, color=MUTED))

    # Права панель: ПРАВИЛЬНО
    rx = lx + lw + 30
    f.append(rect(rx, ly, lw, lh, fill="#f7fbf8", stroke="#80c090", sw=1.5, rx=8))
    f.append(text(rx + lw / 2, ly + 25, "ПРАВИЛЬНО: Земляний Return Via поруч", size=12, bold=True, color=FIELD))

    f.append(line(rx + 20, y_l2, rx + lw - 20, y_l2, color="#5b8296", sw=3.0))
    f.append(text(rx + 45, y_l2 - 6, "L2: GND 1", size=10, bold=True, color="#2b5994"))

    f.append(line(rx + 20, y_l3, rx + lw - 20, y_l3, color="#b08050", sw=3.0))
    f.append(text(rx + 45, y_l3 - 6, "L3: GND 2", size=10, bold=True, color="#805020"))

    # Сигнальний Via
    f.append(line(rx + 50, y_l1, rx + 160, y_l1, color=POS, sw=2.5))
    f.append(line(rx + 160, y_l1, rx + 160, y_l4, color=POS, sw=3.5))
    f.append(line(rx + 160, y_l4, rx + lw - 50, y_l4, color=POS, sw=2.5))
    f.append(circle(rx + 160, y_l1, 4, fill=POS, stroke=LINE, sw=1.2))
    f.append(circle(rx + 160, y_l4, 4, fill=POS, stroke=LINE, sw=1.2))
    f.append(text(rx + 145, y_l1 - 10, "Signal Via", size=10, bold=True, color=POS))

    # Земляний Return Via поруч (< 0.5 мм)
    f.append(line(rx + 205, y_l2, rx + 205, y_l3, color=FIELD, sw=4.0))
    f.append(circle(rx + 205, y_l2, 4, fill=FIELD, stroke=LINE, sw=1.2))
    f.append(circle(rx + 205, y_l3, 4, fill=FIELD, stroke=LINE, sw=1.2))
    f.append(text(rx + 225, y_l2 - 10, "Return Via (GND)", size=10, bold=True, color=FIELD))

    # Зворотний струм переходить локально
    f.append(line(rx + 50, y_l2 + 6, rx + 160, y_l2 + 6, color=NEG, sw=2.2, dash="3,2"))
    f.append(line(rx + 160, y_l2 + 6, rx + 205, y_l2, color=NEG, sw=2.2, dash="2,2"))
    f.append(line(rx + 205, y_l3, rx + 160, y_l3 - 6, color=NEG, sw=2.2, dash="2,2"))
    f.append(line(rx + 160, y_l3 - 6, rx + lw - 50, y_l3 - 6, color=NEG, sw=2.2, dash="3,2"))

    f.append(text(rx + lw / 2, ly + 255, "Мінімальна площа петлі та стабільний імпеданс!", size=10, bold=True, color=FIELD))
    f.append(text(rx + lw / 2, ly + 275, "Індуктивність переходу < 0.3 нГн,", size=10, color=INK))
    f.append(text(rx + lw / 2, ly + 292, "немає дзвону та наводок на сусідні шари", size=10, color=MUTED))

    render(os.path.join(IMG, "layer-transition-return-via.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. differential-pair-return.svg — Differential pair return current in ground plane
# ════════════════════════════════════════════════════════════════════════════
def fig_diff_pair():
    W, H = 800, 370
    f = []

    f.append(text(W / 2, 26, "ЗВОРОТНИЙ СТРУМ ДИФЕРЕНЦІЙНОЇ ПАРИ В ОПОРНІЙ ПЛОЩИНІ", size=14, bold=True, color=INK))

    cx = W / 2
    spacing = 60
    d_plus_x = cx - spacing / 2
    d_minus_x = cx + spacing / 2
    tr_w, tr_h = 40, 14
    tr_y = 65

    # D+ Trace
    f.append(rect(d_plus_x - tr_w / 2, tr_y, tr_w, tr_h, fill="#ffcccc", stroke=POS, sw=1.8, rx=2))
    f.append(text(d_plus_x, tr_y + 11, "D+ (+I)", size=10, bold=True, color=POS))

    # D- Trace
    f.append(rect(d_minus_x - tr_w / 2, tr_y, tr_w, tr_h, fill="#cce5ff", stroke=NEG, sw=1.8, rx=2))
    f.append(text(d_minus_x, tr_y + 11, "D− (−I)", size=10, bold=True, color=NEG))

    # Діелектрик
    diel_y = tr_y + tr_h
    diel_h = 45
    f.append(rect(cx - 270, diel_y, 540, diel_h, fill="#f9f9e8", stroke="#d8d8a0", sw=1.2, rx=2))

    # Зв'язок між лініями
    f.append(line(d_plus_x + tr_w / 2 + 2, tr_y + 7, d_minus_x - tr_w / 2 - 2, tr_y + 7, color="#9a59b5", sw=1.5, dash="3,2"))
    f.append(text(cx, tr_y - 8, "Зв'язок пари", size=9, color="#7d3c98"))

    # Опорна площина землі (GND)
    gnd_y = diel_y + diel_h
    gnd_h = 14
    f.append(rect(cx - 270, gnd_y, 540, gnd_h, fill="#d6e4f0", stroke="#4a89dc", sw=1.5, rx=2))
    f.append(text(cx - 190, gnd_y + 11, "Площина землі (GND)", size=10, bold=True, color="#2b5994"))

    # Густина зворотного струму під площиною
    base_y = gnd_y + gnd_h + 105
    f.append(line(cx - 270, base_y, cx + 270, base_y, color=LINE, sw=1.5))
    f.append(arrow(cx + 260, base_y, cx + 275, base_y, color=LINE, sw=1.5))
    f.append(text(cx + 285, base_y + 4, "x", size=11, bold=True, color=INK))

    hp = 30.0
    pts_diff = []
    for xi in range(-250, 251, 5):
        x_abs = cx + xi
        j_plus = 65.0 / (1.0 + ((x_abs - d_plus_x) / hp) ** 2)
        j_minus = -65.0 / (1.0 + ((x_abs - d_minus_x) / hp) ** 2)
        j_tot = j_plus + j_minus
        pts_diff.append((x_abs, base_y - j_tot))

    poly_diff = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts_diff)
    f.append(f'<polyline points="{poly_diff}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    f.append(text(d_plus_x, base_y - 65, "Зворот D+ (−I)", size=10, bold=True, color=NEG))
    f.append(text(d_minus_x, base_y + 25, "Зворот D− (+I)", size=10, bold=True, color=POS))

    # Висновок знизу
    f.append(text(W / 2, H - 45, "Міф: «Зворотний струм диференційної пари тече лише між провідниками».", size=11, bold=True, color=POS))
    f.append(text(W / 2, H - 28, "Реальність: більшість струму повертається ЧЕРЕЗ ПЛОЩИНУ прямо під кожною лінією.", size=11, bold=True, color=INK))
    f.append(text(W / 2, H - 12, "Розріз площини під парою знищує баланс і створює потужний синфазний шум (Common-Mode EMI).", size=10, color=MUTED))

    render(os.path.join(IMG, "differential-pair-return.svg"), W, H, *f)


def main():
    fig_dc_vs_rf()
    fig_lorentz()
    fig_split_plane()
    fig_layer_transition()
    fig_diff_pair()
    print("Всі 5 фігур успішно згенеровано.")


if __name__ == '__main__':
    main()
