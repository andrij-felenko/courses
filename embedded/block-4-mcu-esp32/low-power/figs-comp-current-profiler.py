# -*- coding: utf-8 -*-
"""
Фігури для вставки 🔌 «Профілювальники струму (клас Power Profiler)»
Розділ r13-low-power, тема 4.13.7, вставка c.

fig-r13-s7c-1-profiler-chain.svg — тракт сигналу + range-switching
fig-r13-s7c-2-wiring.svg        — два режими ввімкнення
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.7c.1  — тракт сигналу всередині профілювальника
# ═══════════════════════════════════════════════════════════════════════════════

def fig1():
    W, H = 860, 440
    frags = []

    # ── Заголовок ──────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 30, "Тракт сигналу профілювальника струму", size=16, bold=True))

    # ── Головні блоки тракту (зліва направо) ──────────────────────────────────
    # x-координати центрів блоків (без вузла range-switch, він буде вгорі)
    blocks_y = 200  # y-центр основного рядка

    # DUT
    b, bw, bh = textbox(60, blocks_y, "DUT\n(пристрій\nпід тестом)", size=13, fill=FILL,
                         stroke=INK, pad=10)
    frags.append(b)
    dut_right = 60 + bw / 2

    # Range-switch вузол — виділений FIELD-кольором, розміщений по центру між DUT і CSA
    rs_cx = 250
    rs_cy = 190

    # Стрілка DUT → range-switch вузол (через шунти)
    frags.append(arrow(dut_right, blocks_y, rs_cx - 68, rs_cy, color=INK))

    # Вузол range-switching (виділений FIELD)
    frags.append(rect(rs_cx - 78, rs_cy - 80, 156, 160, fill="#e8f8f0", stroke=FIELD, sw=2.5, rx=10))
    frags.append(text(rs_cx, rs_cy - 68, "Range-switching", size=11, color=FIELD, bold=True))

    # Три шунти всередині вузла
    shunt_labels = ["нА-шунт\n(великий Ω)", "мкА/мА-шунт", "А-шунт\n(малий Ω)"]
    shunt_fills  = ["#dff5e8", "#f4f6f8", "#fdf0e8"]
    for i, (lbl, sfill) in enumerate(zip(shunt_labels, shunt_fills)):
        sy = rs_cy - 42 + i * 40
        sb, sbw, _ = textbox(rs_cx, sy, lbl, size=10, fill=sfill, stroke=MUTED, pad=6, min_w=110)
        frags.append(sb)

    # Підпис-пояснення під вузлом
    frags.append(text(rs_cx, rs_cy + 88, "автоперемикання за нс–мкс", size=10, color=MUTED))

    # Стрілка range-switch → підсилювач
    csa_cx = 440
    frags.append(arrow(rs_cx + 78, rs_cy, csa_cx - 70, blocks_y, color=INK))

    # CSA (current-sense amplifier)
    b2, bw2, _ = textbox(csa_cx, blocks_y, "Підсилювач\nрізниці\n(CSA)", size=13, fill=FILL,
                          stroke=INK, pad=10)
    frags.append(b2)

    # Стрілка CSA → АЦП
    adc_cx = 590
    frags.append(arrow(csa_cx + bw2 / 2, blocks_y, adc_cx - 55, blocks_y, color=INK))

    # АЦП
    b3, bw3, _ = textbox(adc_cx, blocks_y, "Швидкий\nАЦП\n(≥10 кSPS)", size=13, fill=FILL,
                           stroke=INK, pad=10)
    frags.append(b3)

    # Стрілка АЦП → USB буфер
    usb_cx = 720
    frags.append(arrow(adc_cx + bw3 / 2, blocks_y, usb_cx - 52, blocks_y, color=INK))

    # USB/буфер
    b4, bw4, _ = textbox(usb_cx, blocks_y, "USB /\nбуфер", size=13, fill=FILL,
                           stroke=INK, pad=10)
    frags.append(b4)

    # Стрілка USB → ПК
    pc_cx = 820
    frags.append(arrow(usb_cx + bw4 / 2, blocks_y, pc_cx - 20, blocks_y, color=INK))

    # ПК — графік I(t)
    b5, _, _ = textbox(pc_cx, blocks_y, "ПК\nI(t)", size=13, fill="#e8eaf6",
                        stroke=NEG, pad=10)
    frags.append(b5)

    # ── Підпис burden voltage ──────────────────────────────────────────────────
    frags.append(line(rs_cx, rs_cy + 80, rs_cx, H - 60, color=POS, sw=1.2, dash="4,3"))
    frags.append(text(rs_cx, H - 46, "burden voltage — спад на шунті,", size=11, color=POS))
    frags.append(text(rs_cx, H - 32, "критичний для сплячого МК", size=11, color=POS))

    # ── Нижній підпис-висновок ─────────────────────────────────────────────────
    frags.append(text(W / 2, H - 10,
        "Range-switching склеює нА сну та сотні мА передачі в єдиний суцільний графік",
        size=12, color=MUTED))

    render(os.path.join(OUT, 'fig-r13-s7c-1-profiler-chain.svg'), W, H, *frags)
    print("fig-r13-s7c-1-profiler-chain.svg — OK")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.7c.2  — два режими ввімкнення
# ═══════════════════════════════════════════════════════════════════════════════

def fig2():
    W, H = 820, 400
    frags = []

    frags.append(text(W / 2, 28, "Два режими ввімкнення профілювальника", size=16, bold=True))

    # ── Ліва панель: Ampere-meter mode ─────────────────────────────────────────
    panel_y = 55
    frags.append(rect(10, panel_y, 380, H - 70, fill="#f9fafb", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(200, panel_y + 20, "Ampere-meter mode", size=13, bold=True, color=INK))
    frags.append(text(200, panel_y + 36, "(розрив плюсового проводу)", size=11, color=MUTED))

    # Джерело живлення
    sb, _, _ = textbox(75, 175, "Джерело\nживлення", size=12, fill=FILL, stroke=INK, pad=8)
    frags.append(sb)

    # Профілювальник
    pb, _, _ = textbox(210, 175, "Профіль-\nщик\nIN+→OUT+", size=12, fill="#e8f8f0", stroke=FIELD,
                        sw=2, pad=8)
    frags.append(pb)

    # DUT
    db, _, _ = textbox(340, 175, "DUT\nVDD", size=12, fill=FILL, stroke=INK, pad=8)
    frags.append(db)

    # Стрілки
    frags.append(arrow(118, 163, 155, 163, color=INK))
    frags.append(arrow(265, 163, 305, 163, color=INK))

    # GND лінія знизу
    frags.append(line(30, 220, 375, 220, color=NEG, sw=1.8))
    frags.append(text(200, 238, "спільна GND", size=11, color=NEG))

    # «+» і «−» мітки
    frags.append(plus(135, 155, r=8))
    frags.append(minus(135, 225, r=8))

    # Пояснення
    frags.append(text(200, 275, "Прилад — послідовно у розрив плюса.", size=11, color=INK))
    frags.append(text(200, 292, "Своє живлення — окремий USB до ПК.", size=11, color=INK))

    # ── Права панель: Source-meter mode ────────────────────────────────────────
    rx0 = 420
    frags.append(rect(rx0, panel_y, 390, H - 70, fill="#f9fafb", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(rx0 + 195, panel_y + 20, "Source-meter mode", size=13, bold=True, color=INK))
    frags.append(text(rx0 + 195, panel_y + 36, "(прилад сам живить DUT)", size=11, color=MUTED))

    # Профілювальник (source)
    sp, _, _ = textbox(rx0 + 150, 175, "Профілювальник\n3.3 В / source\n+ вимір I", size=12,
                        fill="#e8f8f0", stroke=FIELD, sw=2, pad=8)
    frags.append(sp)

    # DUT
    sd, _, _ = textbox(rx0 + 330, 175, "DUT\nVDD", size=12, fill=FILL, stroke=INK, pad=8)
    frags.append(sd)

    frags.append(arrow(rx0 + 220, 163, rx0 + 285, 163, color=INK))
    frags.append(line(rx0 + 20, 220, rx0 + 375, 220, color=NEG, sw=1.8))
    frags.append(text(rx0 + 195, 238, "спільна GND", size=11, color=NEG))

    # USB-живлення приладу (окремий кабель)
    frags.append(line(rx0 + 150, 132, rx0 + 150, 105, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(text(rx0 + 150, 96, "USB ПК (лише управління + живлення приладу)", size=10, color=MUTED))

    frags.append(text(rx0 + 195, 275, "Один кабель до ПК — і джерело, і вимір.", size=11, color=INK))

    # ── Антипатерн: НЕправильна точка врізання ────────────────────────────────
    frags.append(rect(10, H - 56, W - 20, 46, fill="#fff5f5", stroke=POS, sw=1.5, rx=7))
    frags.append(text(W / 2, H - 38,
        "⚠ НЕ вмикати в розрив після USB-роз'єму DevKit — USB-UART міст і LDO домішують своє споживання",
        size=11, color=POS))
    frags.append(text(W / 2, H - 22,
        "→ вмикати в розрив батарейного живлення або в спеціальний jumper розриву струму",
        size=11, color=INK))

    render(os.path.join(OUT, 'fig-r13-s7c-2-wiring.svg'), W, H, *frags)
    print("fig-r13-s7c-2-wiring.svg — OK")


if __name__ == '__main__':
    fig1()
    fig2()
