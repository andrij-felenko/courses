# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми guard-ring-pcb (Охоронне кільце на платі)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_leakage_mechanism():
    """Фігура 1: Фізика поверхневих та об'ємних витоків на друкованій платі."""
    w, h = 820, 360
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w / 2, 25, "Шляхи паразитного витоку струму на друкованій платі FR-4", size=16, bold=True))

    sub_x, sub_y, sub_w, sub_h = 60, 140, 700, 150
    out.append(rect(sub_x, sub_y, sub_w, sub_h, fill="#e8edf2", stroke="#7f8c8d", sw=2, rx=4))
    out.append(text(sub_x + 100, sub_y + 120, "Склотекстоліт FR-4 (об'ємний питомий опір ρ_v ≈ 10¹²...10¹⁴ Ом·см)", size=13, color=MUTED, anchor="start"))

    # Провідники (Мідні доріжки)
    tr1_x, tr_y, tr_w, tr_h = 100, sub_y - 24, 130, 24
    tr2_x = 345
    tr3_x = 590

    # Поверхнева плівка вологи та іонного забруднення ТІЛЬКИ між доріжками (без накладання)
    film_h = 6
    film_y = sub_y - film_h
    out.append(rect(tr1_x + tr_w, film_y, tr2_x - (tr1_x + tr_w), film_h, fill="#d4e6f1", stroke="#5dade2", sw=1, rx=0))
    out.append(rect(tr2_x + tr_w, film_y, tr3_x - (tr2_x + tr_w), film_h, fill="#d4e6f1", stroke="#5dade2", sw=1, rx=0))
    out.append(text(sub_x + sub_w - 20, film_y - 14, "Плівка вологи, іонів солей та флюсу (R_s ≈ 10⁷...10¹⁰ Ом/кв)", size=12, color=NEG, anchor="end", italic=True))

    # 1. Шина живлення (+15 В)
    out.append(rect(tr1_x, tr_y, tr_w, tr_h, fill="#fadbd8", stroke=POS, sw=2, rx=3))
    out.append(text(tr1_x + tr_w / 2, tr_y + 16, "Шина +15 В (V_cc)", size=13, color=POS, bold=True))

    # 2. Чутливий вузол High-Z (IN-, 0 В або V_in)
    out.append(rect(tr2_x, tr_y, tr_w, tr_h, fill="#fef9e7", stroke="#f39c12", sw=2, rx=3))
    out.append(text(tr2_x + tr_w / 2, tr_y + 16, "Вузол High-Z (IN⁻)", size=13, color="#b7950b", bold=True))

    # 3. Земляна шина (GND, 0 В)
    out.append(rect(tr3_x, tr_y, tr_w, tr_h, fill="#d5f5e3", stroke=FIELD, sw=2, rx=3))
    out.append(text(tr3_x + tr_w / 2, tr_y + 16, "Шина GND (0 В)", size=13, color=FIELD, bold=True))

    # Струми витоку
    out.append(arrow(tr1_x + tr_w + 10, tr_y + 12, tr2_x - 10, tr_y + 12, color=POS, sw=2.5))
    tb_body, _, _ = textbox(287, tr_y - 30, "I_поверхневий ≈ 1.5 нА\n(ΔU = 15 В, R_s = 10¹⁰ Ом)", size=11, fill="#fdf2e9", stroke=POS, color=POS, pad=6)
    out.append(tb_body)

    out.append(f'<path d="M {tr1_x + tr_w/2} {tr_y + tr_h} C {tr1_x + tr_w/2 + 40} {sub_y + 80}, {tr2_x + tr_w/2 - 40} {sub_y + 80}, {tr2_x + tr_w/2} {tr_y + tr_h}" fill="none" stroke="{POS}" stroke-width="2" stroke-dasharray="4,4" />')
    tb_bulk, _, _ = textbox(287, sub_y + 60, "I_об'ємний (крізь FR-4)", size=11, fill="#f4f6f8", stroke="#7f8c8d", color=MUTED, pad=5)
    out.append(tb_bulk)

    out.append(line(sub_x, sub_y + sub_h + 15, sub_x + sub_w, sub_y + sub_h + 15, color="#bdc3c7", sw=1))
    out.append(text(w / 2, sub_y + sub_h + 35, "Без захисного кільця паразитний струм 1.5 нА повністю затоплює слабкий сигнал у 1 пА (похибка 150 000%)", size=13, color=POS, bold=True))

    out.append("</svg>")
    path = os.path.join(IMG_DIR, "leakage-mechanism.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"Generated {path}")


def fig_guard_principle():
    """Фігура 2: Фізичний принцип дії охоронного кільця (еквіпотенційний бар'єр)."""
    w, h = 820, 370
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w / 2, 25, "Принцип еквіпотенційного екранування (Guard Ring)", size=16, bold=True))

    sub_x, sub_y, sub_w, sub_h = 50, 140, 720, 140
    out.append(rect(sub_x, sub_y, sub_w, sub_h, fill="#e8edf2", stroke="#7f8c8d", sw=2, rx=4))

    tr_y, tr_h = sub_y - 26, 26

    out.append(rect(70, tr_y, 110, tr_h, fill="#fadbd8", stroke=POS, sw=2, rx=3))
    out.append(text(125, tr_y + 17, "+15 В (V_cc)", size=13, color=POS, bold=True))

    out.append(rect(240, tr_y, 100, tr_h, fill="#d4e6f1", stroke=NEG, sw=2, rx=3))
    out.append(text(290, tr_y + 17, "Guard (0 В)", size=13, color=NEG, bold=True))

    out.append(rect(400, tr_y, 110, tr_h, fill="#fef9e7", stroke="#f39c12", sw=2, rx=3))
    out.append(text(455, tr_y + 17, "High-Z (0 В)", size=13, color="#b7950b", bold=True))

    out.append(rect(570, tr_y, 100, tr_h, fill="#d4e6f1", stroke=NEG, sw=2, rx=3))
    out.append(text(620, tr_y + 17, "Guard (0 В)", size=13, color=NEG, bold=True))

    out.append(f'<path d="M 290 {tr_y} L 290 {tr_y - 22} L 620 {tr_y - 22} L 620 {tr_y}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="3,3" />')
    out.append(text(455, tr_y - 28, "Суцільне охоронне кільце (V_guard = V_node)", size=12, color=NEG, bold=True))

    out.append(arrow(185, tr_y + 13, 235, tr_y + 13, color=POS, sw=2.2))
    tb_ext, _, _ = textbox(205, tr_y + 60, "I_зовн стікає в Guard\n(ΔV = 15 В)", size=11, fill="#fadbd8", stroke=POS, color=POS, pad=5)
    out.append(tb_ext)

    out.append(arrow(290, tr_y + tr_h, 290, sub_y + 75, color=NEG, sw=2))
    tb_buf, _, _ = textbox(290, sub_y + 95, "Низькоімпедансний\nвитік у джерело Guard", size=11, fill="#d4e6f1", stroke=NEG, color=NEG, pad=5)
    out.append(tb_buf)

    out.append(line(345, tr_y + 13, 395, tr_y + 13, color=FIELD, sw=2))
    tb_zero, _, _ = textbox(370, tr_y + 60, "ΔV = V_in - V_guard = 0 В\n⇒ I_витік = 0 / R = 0 А!", size=11, fill="#d5f5e3", stroke=FIELD, color=FIELD, bold=True, pad=5)
    out.append(tb_zero)

    out.append(line(sub_x, sub_y + sub_h + 15, sub_x + sub_w, sub_y + sub_h + 15, color="#bdc3c7", sw=1))
    out.append(text(w / 2, sub_y + sub_h + 35, "Охоронне кільце перехоплює весь зовнішній струм, усуваючи градієнт напруги біля чутливого вузла", size=13, color=INK, bold=True))

    out.append("</svg>")
    path = os.path.join(IMG_DIR, "guard-principle.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"Generated {path}")


def fig_opamp_topologies():
    """Фігура 3: Схемотехнічні топології підключення Guard (TIA, повторювач, підсилювач з драйвером)."""
    w, h = 900, 380
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w / 2, 25, "Схемотехнічні конфігурації підключення охоронного кільця", size=16, bold=True))

    pan_w, pan_h = 270, 300
    p1_x, p2_x, p3_x = 25, 315, 605
    pan_y = 50

    for px, title, sub in [
        (p1_x, "А. Інвертуючий ОП (TIA)", "Віртуальна земля: Guard → GND"),
        (p2_x, "Б. Повторювач напруги", "Вхід плаває: Guard → Вихід / IN⁻"),
        (p3_x, "В. Підсилювач (G > 1)", "Окремий Guard Driver буфер"),
    ]:
        out.append(rect(px, pan_y, pan_w, pan_h, fill="#fafbfc", stroke="#bdc3c7", sw=1.5, rx=6))
        out.append(text(px + pan_w / 2, pan_y + 22, title, size=13, color=INK, bold=True))
        out.append(text(px + pan_w / 2, pan_y + 40, sub, size=11, color=MUTED, italic=True))

    # ── Панель А: Інвертуючий TIA ──
    op_x, op_y = p1_x + 155, pan_y + 150
    out.append(f'<polygon points="{op_x},{op_y-35} {op_x},{op_y+35} {op_x+60},{op_y}" fill="#ffffff" stroke="{LINE}" stroke-width="1.8"/>')
    out.append(text(op_x + 12, op_y - 14, "−", size=16, bold=True))
    out.append(text(op_x + 12, op_y + 18, "+", size=16, bold=True))

    out.append(line(p1_x + 25, op_y - 15, op_x, op_y - 15, color=LINE, sw=1.8))
    out.append(text(p1_x + 20, op_y - 15, "I_in", size=12, color=INK, anchor="end"))
    out.append(circle(p1_x + 85, op_y - 15, 3, fill="#f39c12", stroke="#b7950b"))
    out.append(text(p1_x + 55, op_y - 25, "High-Z (0 В)", size=10, color="#b7950b", bold=True))

    out.append(f'<path d="M {p1_x+85} {op_y-15} L {p1_x+85} {op_y-60} L {op_x+20} {op_y-60}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
    out.append(rect(op_x + 20, op_y - 68, 35, 16, fill="#ffffff", stroke=LINE, sw=1.5))
    out.append(text(op_x + 37, op_y - 56, "Rf", size=10, color=INK))
    out.append(f'<path d="M {op_x+55} {op_y-60} L {op_x+75} {op_y-60} L {op_x+75} {op_y}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')

    out.append(line(op_x + 60, op_y, op_x + 95, op_y, color=LINE, sw=1.8))
    out.append(text(op_x + 98, op_y - 5, "V_out", size=11, color=INK, anchor="start"))

    out.append(line(op_x - 30, op_y + 18, op_x, op_y + 18, color=LINE, sw=1.5))
    out.append(line(op_x - 30, op_y + 18, op_x - 30, op_y + 40, color=LINE, sw=1.5))
    out.append(line(op_x - 40, op_y + 40, op_x - 20, op_y + 40, color=LINE, sw=1.8))
    out.append(line(op_x - 36, op_y + 44, op_x - 24, op_y + 44, color=LINE, sw=1.5))
    out.append(line(op_x - 33, op_y + 48, op_x - 27, op_y + 48, color=LINE, sw=1.2))

    out.append(f'<path d="M {op_x-30} {op_y+18} L {p1_x+35} {op_y+18} L {p1_x+35} {op_y-5} L {p1_x+115} {op_y-5} L {p1_x+115} {op_y-38} L {p1_x+35} {op_y-38}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="3,3"/>')
    tb_g1, _, _ = textbox(p1_x + pan_w / 2, pan_y + 255, "Guard з'єднано з GND\n(V_guard = 0 В ≈ V_IN⁻)", size=11, fill="#d4e6f1", stroke=NEG, color=NEG, pad=5)
    out.append(tb_g1)

    # ── Панель Б: Повторювач напруги ──
    op2_x, op2_y = p2_x + 140, pan_y + 150
    out.append(f'<polygon points="{op2_x},{op2_y-35} {op2_x},{op2_y+35} {op2_x+60},{op2_y}" fill="#ffffff" stroke="{LINE}" stroke-width="1.8"/>')
    out.append(text(op2_x + 12, op2_y - 14, "−", size=16, bold=True))
    out.append(text(op2_x + 12, op2_y + 18, "+", size=16, bold=True))

    out.append(line(p2_x + 30, op2_y + 18, op2_x, op2_y + 18, color=LINE, sw=1.8))
    out.append(text(p2_x + 25, op2_y + 18, "V_in", size=12, color=INK, anchor="end"))
    out.append(circle(p2_x + 65, op2_y + 18, 3, fill="#f39c12", stroke="#b7950b"))
    out.append(text(p2_x + 65, op2_y + 36, "High-Z", size=10, color="#b7950b", bold=True))

    out.append(line(op2_x + 60, op2_y, op2_x + 85, op2_y, color=LINE, sw=1.8))
    out.append(f'<path d="M {op2_x+75} {op2_y} L {op2_x+75} {op2_y-50} L {op2_x-20} {op2_y-50} L {op2_x-20} {op2_y-14} L {op2_x} {op2_y-14}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')

    out.append(f'<path d="M {op2_x-20} {op2_y-50} L {p2_x+40} {op2_y-50} L {p2_x+40} {op2_y+4} L {p2_x+95} {op2_y+4} L {p2_x+95} {op2_y+48} L {p2_x+40} {op2_y+48}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="3,3"/>')
    tb_g2, _, _ = textbox(p2_x + pan_w / 2, pan_y + 255, "Guard з'єднано з V_out\n(V_guard = V_out = V_in)", size=11, fill="#d4e6f1", stroke=NEG, color=NEG, pad=5)
    out.append(tb_g2)

    # ── Панель В: Підсилювач з Guard Driver ──
    op3_x, op3_y = p3_x + 130, pan_y + 115
    out.append(f'<polygon points="{op3_x},{op3_y-30} {op3_x},{op3_y+30} {op3_x+50},{op3_y}" fill="#ffffff" stroke="{LINE}" stroke-width="1.8"/>')
    out.append(text(op3_x + 10, op3_y - 12, "−", size=14, bold=True))
    out.append(text(op3_x + 10, op3_y + 14, "+", size=14, bold=True))

    out.append(line(p3_x + 25, op3_y + 14, op3_x, op3_y + 14, color=LINE, sw=1.8))
    out.append(text(p3_x + 20, op3_y + 14, "V_in", size=11, color=INK, anchor="end"))
    out.append(circle(p3_x + 55, op3_y + 14, 3, fill="#f39c12", stroke="#b7950b"))

    buf_x, buf_y = p3_x + 130, pan_y + 195
    out.append(f'<polygon points="{buf_x},{buf_y-25} {buf_x},{buf_y+25} {buf_x+45},{buf_y}" fill="#e8f8f5" stroke="{NEG}" stroke-width="1.5"/>')
    out.append(text(buf_x + 8, buf_y - 10, "−", size=13, color=NEG, bold=True))
    out.append(text(buf_x + 8, buf_y + 10, "+", size=13, color=NEG, bold=True))
    out.append(text(buf_x + 24, buf_y + 2, "Buf", size=10, color=NEG, bold=True))

    out.append(f'<path d="M {p3_x+55} {op3_y+14} L {p3_x+55} {buf_y+10} L {buf_x} {buf_y+10}" fill="none" stroke="{LINE}" stroke-width="1.3"/>')
    out.append(f'<path d="M {buf_x+45} {buf_y} L {buf_x+58} {buf_y} L {buf_x+58} {buf_y-18} L {buf_x-10} {buf_y-18} L {buf_x-10} {buf_y-10} L {buf_x} {buf_y-10}" fill="none" stroke="{NEG}" stroke-width="1.3"/>')

    out.append(f'<path d="M {buf_x+58} {buf_y} L {buf_x+75} {buf_y} L {buf_x+75} {buf_y+35} L {p3_x+35} {buf_y+35} L {p3_x+35} {op3_y-4} L {p3_x+75} {op3_y-4} L {p3_x+75} {op3_y+24} L {p3_x+35} {op3_y+24}" fill="none" stroke="{NEG}" stroke-width="2" stroke-dasharray="3,3"/>')
    tb_g3, _, _ = textbox(p3_x + pan_w / 2, pan_y + 270, "Guard живиться від буфера\n(розвантажує вхід при G > 1)", size=11, fill="#d4e6f1", stroke=NEG, color=NEG, pad=5)
    out.append(tb_g3)

    out.append("</svg>")
    path = os.path.join(IMG_DIR, "opamp-topologies.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"Generated {path}")


def fig_pcb_guard_layout():
    """Фігура 4: Пошарова топологія плати: Guard Ring, віаси, маска та внутрішній екран."""
    w, h = 860, 420
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w / 2, 25, "Прецизійна топологія друкованої плати: Guard Ring та зшивання", size=16, bold=True))

    v1_x, v1_y, v1_w, v1_h = 40, 55, 360, 340
    v2_x, v2_y, v2_w, v2_h = 440, 55, 380, 340

    out.append(rect(v1_x, v1_y, v1_w, v1_h, fill="#fafbfc", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(v1_x + v1_w / 2, v1_y + 22, "Вид зверху (Top Layer)", size=13, color=INK, bold=True))

    out.append(rect(v2_x, v2_y, v2_w, v2_h, fill="#fafbfc", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(v2_x + v2_w / 2, v2_y + 22, "Поперечний розріз (Cross-section)", size=13, color=INK, bold=True))

    # ── Вид зверху ──
    out.append(rect(v1_x + 20, v1_y + 45, v1_w - 40, v1_h - 65, fill="#eaeded", stroke="#95a5a6", sw=1.5, rx=4))
    out.append(text(v1_x + 35, v1_y + 65, "Зовнішній полігон GND / V_cc", size=11, color=MUTED, anchor="start"))

    mask_x, mask_y, mask_w, mask_h = v1_x + 40, v1_y + 80, v1_w - 80, v1_h - 110
    out.append(rect(mask_x, mask_y, mask_w, mask_h, fill="#fcf3cf", stroke="#f39c12", sw=1.5, rx=4))
    out.append(text(v1_x + v1_w / 2, mask_y + 16, "Вікно розкриття паяльної маски", size=10, color="#b7950b", bold=True))

    g_x, g_y, g_w, g_h = v1_x + 60, v1_y + 105, v1_w - 120, v1_h - 150
    out.append(rect(g_x, g_y, g_w, g_h, fill="#d4e6f1", stroke=NEG, sw=2, rx=4))
    out.append(text(v1_x + v1_w / 2, g_y + 18, "Охоронна доріжка (Guard)", size=11, color=NEG, bold=True))

    for vx, vy in [
        (g_x + 15, g_y + 15), (g_x + g_w - 15, g_y + 15),
        (g_x + 15, g_y + g_h - 15), (g_x + g_w - 15, g_y + g_h - 15),
        (g_x + g_w / 2, g_y + 15), (g_x + g_w / 2, g_y + g_h - 15),
        (g_x + 15, g_y + g_h / 2), (g_x + g_w - 15, g_y + g_h / 2),
    ]:
        out.append(circle(vx, vy, 4, fill="#2980b9", stroke="#1a5276", sw=1))

    node_x, node_y, node_w, node_h = v1_x + 110, v1_y + 150, v1_w - 220, v1_h - 225
    out.append(rect(node_x, node_y, node_w, node_h, fill="#f9e79f", stroke="#d68910", sw=2, rx=3))
    out.append(text(v1_x + v1_w / 2, node_y + 20, "High-Z Пад", size=12, color="#7d6608", bold=True))
    out.append(text(v1_x + v1_w / 2, node_y + 36, "(Вхід ОП)", size=10, color="#7d6608"))

    out.append(text(v1_x + v1_w / 2, v1_y + v1_h - 12, "Повний 360° бар'єр без перетинів іншими сигналами", size=11, color=INK, italic=True))

    # ── Поперечний розріз (Cross-section) ──
    cs_x = v2_x + 30
    cs_w = v2_w - 60

    # Загальний блок діелектрика FR-4
    out.append(rect(cs_x, v2_y + 90, cs_w, 148, fill="#d5dbdb", stroke="#7f8c8d", sw=1.5, rx=2))
    tb_fr4, _, _ = textbox(v2_x + v2_w / 2, v2_y + 130, "FR-4 (Діелектрик)", size=11, fill="#d5dbdb", stroke="#7f8c8d", color=MUTED, pad=3)
    out.append(tb_fr4)

    # Внутрішній екранний шар (Layer 2: Guard Plane всередині FR-4)
    out.append(line(cs_x + 10, v2_y + 164, cs_x + cs_w - 10, v2_y + 164, color=NEG, sw=4))
    out.append(text(cs_x + cs_w - 10, v2_y + 155, "Шар 2: Внутрішній Guard Plane", size=11, color=NEG, anchor="end", bold=True))

    # Віаси зшивання через плату
    out.append(line(cs_x + 52, v2_y + 90, cs_x + 52, v2_y + 238, color="#2980b9", sw=6))
    out.append(line(cs_x + 267, v2_y + 90, cs_x + 267, v2_y + 238, color="#2980b9", sw=6))

    # Мідні провідники Top Layer
    out.append(rect(cs_x + 30, v2_y + 76, 45, 14, fill="#d4e6f1", stroke=NEG, sw=1.8, rx=2))
    out.append(text(cs_x + 52, v2_y + 87, "Guard", size=10, color=NEG, bold=True))

    out.append(rect(cs_x + 125, v2_y + 76, 70, 14, fill="#f9e79f", stroke="#d68910", sw=1.8, rx=2))
    out.append(text(cs_x + 160, v2_y + 87, "High-Z", size=10, color="#7d6608", bold=True))

    out.append(rect(cs_x + 245, v2_y + 76, 45, 14, fill="#d4e6f1", stroke=NEG, sw=1.8, rx=2))
    out.append(text(cs_x + 267, v2_y + 87, "Guard", size=10, color=NEG, bold=True))

    # Мідні провідники Bottom Layer
    out.append(rect(cs_x + 30, v2_y + 238, 45, 14, fill="#d4e6f1", stroke=NEG, sw=1.8, rx=2))
    out.append(rect(cs_x + 245, v2_y + 238, 45, 14, fill="#d4e6f1", stroke=NEG, sw=1.8, rx=2))

    # Паяльна маска з відкриттям (Clearance)
    out.append(rect(cs_x, v2_y + 72, 20, 8, fill="#a9dfbf", stroke="#27ae60", sw=1))
    out.append(rect(cs_x + cs_w - 20, v2_y + 72, 20, 8, fill="#a9dfbf", stroke="#27ae60", sw=1))
    out.append(text(cs_x + 10, v2_y + 65, "Маска", size=9, color="#27ae60"))
    out.append(line(cs_x + 25, v2_y + 70, cs_x + 295, v2_y + 70, color=POS, sw=1.2, dash="3,3"))
    out.append(text(cs_x + 160, v2_y + 65, "Маску видалено (Solder Mask Opening)", size=10, color=POS, bold=True))

    tb_cs, _, _ = textbox(v2_x + v2_w / 2, v2_y + 295, "Тривимірна клітка Guard: кільця на обох сторонах,\nзшивальні віаси та внутрішній екранний шар", size=11, fill="#eaf2f8", stroke=NEG, color=NEG, pad=6)
    out.append(tb_cs)

    out.append("</svg>")
    path = os.path.join(IMG_DIR, "pcb-guard-layout.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"Generated {path}")


def fig_connector_standoff():
    """Фігура 5: Триосьовий кабель (Triax) та монтаж на тефлоновій стійці (Teflon Standoff)."""
    w, h = 860, 360
    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    out.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')

    out.append(text(w / 2, 25, "Зовнішнє підключення: Триосьовий кабель (Triax) та тефлоновий монтаж", size=16, bold=True))

    p1_x, p1_y, p1_w, p1_h = 35, 55, 380, 285
    p2_x, p2_y, p2_w, p2_h = 445, 55, 380, 285

    out.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fafbfc", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(p1_x + p1_w / 2, p1_y + 22, "Триосьовий кабель (Triaxial Cable)", size=13, color=INK, bold=True))

    out.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fafbfc", stroke="#bdc3c7", sw=1.5, rx=6))
    out.append(text(p2_x + p2_w / 2, p2_y + 22, "Тефлонова стійка (PTFE Standoff)", size=13, color=INK, bold=True))

    # ── Триосьовий кабель ──
    cy = p1_y + 115
    out.append(rect(p1_x + 25, cy - 35, 75, 70, fill="#34495e", stroke="#1a252f", sw=1.5, rx=3))
    tb_sh1, _, _ = textbox(p1_x + 62, cy, "Зовнішня\nоболонка", size=10, fill="#34495e", stroke="#1a252f", color="#ffffff", bold=True, pad=3)
    out.append(tb_sh1)

    out.append(rect(p1_x + 100, cy - 28, 65, 56, fill="#bdc3c7", stroke="#7f8c8d", sw=1.5, rx=2))
    tb_sh2, _, _ = textbox(p1_x + 132, cy, "Зовнішній\nекран GND", size=10, fill="#bdc3c7", stroke="#7f8c8d", color=INK, bold=True, pad=3)
    out.append(tb_sh2)

    out.append(rect(p1_x + 165, cy - 22, 55, 44, fill="#eaeded", stroke="#95a5a6", sw=1.2, rx=2))
    tb_sh3, _, _ = textbox(p1_x + 192, cy, "Ізоляція", size=9, fill="#eaeded", stroke="#95a5a6", color=MUTED, pad=2)
    out.append(tb_sh3)

    out.append(rect(p1_x + 220, cy - 16, 65, 32, fill="#d4e6f1", stroke=NEG, sw=1.8, rx=2))
    out.append(text(p1_x + 252, cy + 4, "Guard", size=10, color=NEG, bold=True))

    out.append(rect(p1_x + 285, cy - 10, 40, 20, fill="#fdfefe", stroke="#bdc3c7", sw=1.2, rx=1))

    out.append(rect(p1_x + 325, cy - 5, 35, 10, fill="#f39c12", stroke="#b7950b", sw=1.5, rx=1))
    out.append(text(p1_x + 342, cy - 12, "Сигнал", size=10, color="#b7950b", bold=True))

    tb_triax, _, _ = textbox(p1_x + p1_w / 2, p1_y + 225, "Зовнішній екран відводить ЕМ-шум у землю (GND);\nВнутрішній екран Guard усуває витік та ємність кабелю", size=10.5, fill="#eaf2f8", stroke=NEG, color=NEG, pad=5)
    out.append(tb_triax)

    # ── Тефлонова стійка ──
    out.append(rect(p2_x + 30, p2_y + 160, p2_w - 60, 20, fill="#d5dbdb", stroke="#7f8c8d", sw=1.5, rx=2))
    out.append(text(p2_x + p2_w - 40, p2_y + 195, "Плата FR-4", size=10, color=MUTED, anchor="end"))

    st_x = p2_x + 125
    out.append(rect(st_x, p2_y + 90, 60, 65, fill="#ffffff", stroke="#2980b9", sw=2, rx=4))
    out.append(text(st_x + 30, p2_y + 126, "PTFE", size=11, color="#2980b9", bold=True))

    out.append(rect(st_x + 20, p2_y + 75, 20, 15, fill="#f39c12", stroke="#b7950b", sw=1.5, rx=2))

    ic_x = p2_x + 250
    out.append(rect(ic_x, p2_y + 115, 75, 45, fill="#34495e", stroke="#1a252f", sw=1.5, rx=3))
    out.append(text(ic_x + 37, p2_y + 140, "ОП (SOIC)", size=11, color="#ffffff", bold=True))

    out.append(f'<path d="M {ic_x} {p2_y+130} L {ic_x-20} {p2_y+130} L {ic_x-20} {p2_y+82} L {st_x+40} {p2_y+82}" fill="none" stroke="#f39c12" stroke-width="2.2" />')
    out.append(text(ic_x + 37, p2_y + 98, "Ніжка у повітрі", size=10, color="#b7950b", bold=True))

    out.append(line(p2_x + 50, p2_y + 82, st_x + 20, p2_y + 82, color="#f39c12", sw=2))
    out.append(text(p2_x + 75, p2_y + 72, "Вхідний датчик", size=10, color="#b7950b"))

    tb_ptfe, _, _ = textbox(p2_x + p2_w / 2, p2_y + 235, "Ніжка входу ОП піднята над платою й розпаяна\nна тефлоновій стійці (R_ізоляції > 10¹⁶ Ом)", size=10.5, fill="#fef9e7", stroke="#f39c12", color="#7d6608", pad=5)
    out.append(tb_ptfe)

    out.append("</svg>")
    path = os.path.join(IMG_DIR, "connector-standoff.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"Generated {path}")


if __name__ == "__main__":
    fig_leakage_mechanism()
    fig_guard_principle()
    fig_opamp_topologies()
    fig_pcb_guard_layout()
    fig_connector_standoff()
