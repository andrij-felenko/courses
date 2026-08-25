# -*- coding: utf-8 -*-
"""Фігури до теми «Напівмістовий перетворювач».
Запуск: python figs.py  → пише .svg у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Принципова схема ізольованого напівмостового перетворювача ────
def fig_schematic():
    W, H = 840, 480
    els = []
    els.append(text(W / 2, 28, "Принципова схема ізольованого напівмостового DC-DC перетворювача", size=16, bold=True))

    # ── Первинна сторона (гаряча земля) ──
    # Вхідне живлення Vin
    els.append(line(60, 90, 60, 410, color=POS, sw=2.5))  # шина +Vin
    els.append(line(60, 410, 240, 410, color=INK, sw=2))  # шина GND
    els.append(text(50, 80, "+Vin", size=14, color=POS, bold=True, anchor="start"))
    els.append(text(50, 430, "GND (перв.)", size=12, color=MUTED, anchor="start"))

    # Ємнісний дільник C1, C2
    cx = 120
    els.append(line(60, 110, cx, 110, color=POS, sw=2))
    els.append(line(cx, 110, cx, 170, color=POS, sw=2))
    # Конденсатор C1
    els.append(line(cx - 20, 170, cx + 20, 170, color=INK, sw=2.5))
    els.append(line(cx - 20, 182, cx + 20, 182, color=INK, sw=2.5))
    els.append(text(cx - 30, 178, "C1", size=13, color=NEG, bold=True, anchor="end"))
    els.append(text(cx - 30, 195, "Vin / 2", size=11, color=MUTED, anchor="end"))
    # Середня точка дільника
    els.append(line(cx, 182, cx, 260, color=INK, sw=2))
    els.append(circle(cx, 260, 4.5, fill=INK, stroke=INK))
    els.append(text(cx - 15, 255, "MID", size=13, color=FIELD, bold=True, anchor="end"))
    els.append(text(cx - 15, 272, "Vin / 2", size=11, color=FIELD, anchor="end"))
    # Конденсатор C2
    els.append(line(cx, 260, cx, 330, color=INK, sw=2))
    els.append(line(cx - 20, 330, cx + 20, 330, color=INK, sw=2.5))
    els.append(line(cx - 20, 342, cx + 20, 342, color=INK, sw=2.5))
    els.append(text(cx - 30, 338, "C2", size=13, color=NEG, bold=True, anchor="end"))
    els.append(text(cx - 30, 355, "Vin / 2", size=11, color=MUTED, anchor="end"))
    els.append(line(cx, 342, cx, 410, color=INK, sw=2))

    # Стійка ключів Q1, Q2 (напівміст)
    qx = 240
    els.append(line(60, 90, qx, 90, color=POS, sw=2))
    els.append(line(qx, 90, qx, 130, color=POS, sw=2))
    # Ключ Q1 (верхній)
    frag1, _, _ = textbox(qx, 155, "Q1\n(верхній)", size=12, bold=True, stroke=POS, fill="#fff", min_w=68)
    els.append(frag1)
    els.append(line(qx, 180, qx, 260, color=INK, sw=2))
    # Вузол SW
    els.append(circle(qx, 260, 4.5, fill=INK, stroke=INK))
    els.append(text(qx + 16, 255, "SW", size=13, color=POS, bold=True, anchor="start"))
    els.append(text(qx + 16, 272, "0...Vin", size=11, color=MUTED, anchor="start"))
    # Ключ Q2 (нижній)
    els.append(line(qx, 260, qx, 340, color=INK, sw=2))
    frag2, _, _ = textbox(qx, 365, "Q2\n(нижній)", size=12, bold=True, stroke=NEG, fill="#fff", min_w=68)
    els.append(frag2)
    els.append(line(qx, 390, qx, 410, color=INK, sw=2))

    # Первинна обмотка трансформатора T1 між SW та MID
    els.append(line(cx, 260, 310, 260, color=FIELD, sw=2))
    els.append(line(qx, 280, 310, 280, color=POS, sw=2))
    # Трансформатор Т1
    # Первинна котушка
    els.append(rect(310, 240, 30, 60, fill="#eef4ff", stroke=NEG, sw=2, rx=4))
    els.append(text(325, 274, "Np", size=12, color=NEG, bold=True))
    # Магнітопровід (сердечник)
    els.append(line(347, 215, 347, 325, color=INK, sw=2.5))
    els.append(line(353, 215, 353, 325, color=INK, sw=2.5))
    els.append(text(350, 205, "T1 (ферит)", size=11, color=MUTED))
    # Вторинні котушки Ns1, Ns2
    els.append(rect(360, 215, 30, 50, fill="#fdeeee", stroke=POS, sw=2, rx=4))
    els.append(text(375, 244, "Ns1", size=12, color=POS, bold=True))
    els.append(rect(360, 275, 30, 50, fill="#fdeeee", stroke=POS, sw=2, rx=4))
    els.append(text(375, 304, "Ns2", size=12, color=POS, bold=True))

    # ── Вторинна сторона (ізольована) ──
    # Випрямні діоди D1, D2
    els.append(line(390, 240, 450, 240, color=POS, sw=2))
    # Діод D1
    els.append('<path d="M450 228 L450 252 L474 240 Z" fill="#fdeeee" stroke="%s" stroke-width="2"/>' % POS)
    els.append(line(474, 228, 474, 252, color=POS, sw=2.5))
    els.append(text(462, 218, "D1", size=12, color=POS, bold=True))

    els.append(line(390, 300, 450, 300, color=POS, sw=2))
    # Діод D2
    els.append('<path d="M450 288 L450 312 L474 300 Z" fill="#fdeeee" stroke="%s" stroke-width="2"/>' % POS)
    els.append(line(474, 288, 474, 312, color=POS, sw=2.5))
    els.append(text(462, 328, "D2", size=12, color=POS, bold=True))

    # З'єднання діодів до дроселя L_out
    els.append(line(474, 240, 520, 240, color=POS, sw=2))
    els.append(line(474, 300, 520, 300, color=POS, sw=2))
    els.append(line(520, 240, 520, 300, color=POS, sw=2))
    els.append(circle(520, 270, 4, fill=POS, stroke=POS))
    els.append(line(520, 270, 560, 270, color=POS, sw=2))

    # Середня точка вторинної обмотки -> вторинна земля
    els.append(line(390, 270, 420, 270, color=INK, sw=2))
    els.append(line(420, 270, 420, 410, color=INK, sw=2))
    els.append(line(420, 410, 780, 410, color=INK, sw=2))
    els.append(text(425, 430, "GND (вторинна)", size=12, color=MUTED, anchor="start"))

    # Вихідний LC-фільтр
    # Дросель L_out
    els.append(rect(560, 255, 60, 30, fill="#eef7ee", stroke=FIELD, sw=2, rx=4))
    els.append(text(590, 274, "Lout", size=13, color=FIELD, bold=True))
    els.append(line(620, 270, 690, 270, color=POS, sw=2))

    # Конденсатор C_out
    els.append(line(690, 270, 690, 320, color=POS, sw=2))
    els.append(line(675, 320, 705, 320, color=INK, sw=2.5))
    els.append(line(675, 332, 705, 332, color=INK, sw=2.5))
    els.append(text(716, 328, "Cout", size=13, color=NEG, bold=True, anchor="start"))
    els.append(line(690, 332, 690, 410, color=INK, sw=2))

    # Навантаження R_load
    els.append(line(690, 270, 770, 270, color=POS, sw=2))
    els.append(line(770, 270, 770, 310, color=POS, sw=2))
    els.append(rect(755, 310, 30, 60, fill="#fbfbfb", stroke=INK, sw=2, rx=3))
    els.append(text(770, 344, "Rн", size=13, color=INK, bold=True))
    els.append(line(770, 370, 770, 410, color=INK, sw=2))

    # Вихідна напруга Vout
    els.append(circle(770, 270, 4, fill=POS, stroke=POS))
    els.append(text(785, 274, "+Vout", size=14, color=POS, bold=True, anchor="start"))

    # Межа гальванічної ізоляції (штрихова лінія)
    els.append(line(350, 70, 350, 450, color="#9ca3af", sw=1.5, dash="6,6"))
    els.append(text(350, 465, "Межа гальванічної ізоляції", size=12, color="#9ca3af", italic=True))

    render(os.path.join(IMG, "schematic.svg"), W, H, *els)


# ── Фігура 2: Чотири фази комутації та часові діаграми ───────────────────────
def fig_phases():
    W, H = 840, 520
    els = []
    els.append(text(W / 2, 26, "Чотири фази циклу комутації напівмостового перетворювача", size=16, bold=True))

    ox = 110
    T_w = 680
    f_w = T_w / 4

    # Фази заголовки
    phases_info = [
        ("Фаза 1: Q1 ON, Q2 OFF", "Vpri = +Vin/2", POS),
        ("Фаза 2: Dead-time", "Діоди D1, D2 вільний хід", MUTED),
        ("Фаза 3: Q1 OFF, Q2 ON", "Vpri = -Vin/2", NEG),
        ("Фаза 4: Dead-time", "Діоди D1, D2 вільний хід", MUTED),
    ]
    for i, (title, sub, col) in enumerate(phases_info):
        fx = ox + i * f_w
        els.append(fitbox(fx + 6, 48, f_w - 12, 36, title + "\n" + sub, size=11, bold=True, fill="#fff", stroke=col))
        els.append(line(fx, 48, fx, 490, color="#e5e7eb", sw=1.2, dash="4,4"))
    els.append(line(ox + T_w, 48, ox + T_w, 490, color="#e5e7eb", sw=1.2, dash="4,4"))

    # Графік 1: Керування затворами Vgs1, Vgs2
    y1 = 125
    els.append(text(ox - 12, y1 + 10, "Vgs1, Vgs2", size=12, color=INK, anchor="end", bold=True))
    els.append(line(ox, y1 + 25, ox + T_w, y1 + 25, color=MUTED, sw=1))
    # Vgs1 (червоний)
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        f"{ox},{y1+25} {ox},{y1-15} {ox+f_w-20},{y1-15} {ox+f_w-20},{y1+25} {ox+T_w},{y1+25}", POS
    ))
    els.append(text(ox + 35, y1 - 20, "Q1 ON", size=11, color=POS, bold=True))
    # Vgs2 (синій)
    p3_start = ox + 2 * f_w
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (
        f"{ox},{y1+25} {p3_start},{y1+25} {p3_start},{y1-15} {p3_start+f_w-20},{y1-15} {p3_start+f_w-20},{y1+25} {ox+T_w},{y1+25}", NEG
    ))
    els.append(text(p3_start + 35, y1 - 20, "Q2 ON", size=11, color=NEG, bold=True))
    # Мертвий час позначка
    els.append(text(ox + f_w - 10, y1 + 38, "t_dead", size=10, color=MUTED, italic=True))
    els.append(text(p3_start + f_w - 10, y1 + 38, "t_dead", size=10, color=MUTED, italic=True))

    # Графік 2: Напруга на первинній обмотці V_primary
    y2 = 215
    els.append(text(ox - 12, y2, "V_primary", size=12, color=INK, anchor="end", bold=True))
    els.append(line(ox, y2, ox + T_w, y2, color=MUTED, sw=1))  # 0 V лінія
    els.append(text(ox - 8, y2 - 25, "+Vin/2", size=10, color=POS, anchor="end"))
    els.append(text(ox - 8, y2 + 30, "−Vin/2", size=10, color=NEG, anchor="end"))
    pts_vp = [
        f"{ox},{y2} {ox},{y2-25} {ox+f_w-20},{y2-25} {ox+f_w-20},{y2}",
        f"{ox+2*f_w},{y2} {ox+2*f_w},{y2+25} {ox+3*f_w-20},{y2+25} {ox+3*f_w-20},{y2} {ox+T_w},{y2}"
    ]
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_vp), FIELD))

    # Графік 3: Струм первинної обмотки I_primary
    y3 = 310
    els.append(text(ox - 12, y3, "I_primary", size=12, color=INK, anchor="end", bold=True))
    els.append(line(ox, y3, ox + T_w, y3, color=MUTED, sw=1))
    pts_ip = [
        f"{ox},{y3-10} {ox+f_w-20},{y3-30} {ox+f_w},{y3}",
        f"{ox+f_w},{y3} {ox+2*f_w},{y3+10} {ox+3*f_w-20},{y3+30} {ox+3*f_w},{y3} {ox+T_w},{y3-10}"
    ]
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_ip), INK))

    # Графік 4: Струм вихідного дроселя I_Lout (подвійна частота пульсацій)
    y4 = 425
    els.append(text(ox - 12, y4, "I_Lout", size=12, color=INK, anchor="end", bold=True))
    els.append(line(ox, y4 + 20, ox + T_w, y4 + 20, color=MUTED, sw=1))
    pts_il = [
        f"{ox},{y4+10} {ox+f_w-20},{y4-20} {ox+f_w},{y4+5}",
        f"{ox+2*f_w},{y4+10} {ox+3*f_w-20},{y4-20} {ox+3*f_w},{y4+5} {ox+T_w},{y4+10}"
    ]
    els.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(pts_il), POS))
    els.append(text(ox + T_w / 2, y4 + 42, "Частота пульсацій дроселя f_ripple = 2 · f_sw", size=12, color=POS, bold=True))

    render(os.path.join(IMG, "phases.svg"), W, H, *els)


# ── Фігура 3: Порівняння B-H кривих (однотактні vs напівміст/повний міст) ────
def fig_bh_loop():
    W, H = 820, 460
    els = []
    els.append(text(W / 2, 28, "Використання петлі гістерезису: однотактні топології проти напівмоста", size=16, bold=True))

    # ── Ліва панель: Однотактні (Forward / Flyback) ──
    lx = 210
    ly = 240
    els.append(fitbox(lx - 160, 60, 320, 36, "ОДНОТАКТНІ ТОПОЛОГІЇ (Forward, Flyback)\nУніполярне збудження (лише I квадрант)",
                      size=12, bold=True, fill="#fdeeee", stroke=POS))
    # Осі B - H
    els.append(arrow(lx - 150, ly, lx + 150, ly, color=INK, sw=1.5))
    els.append(text(lx + 155, ly + 4, "H (струм)", size=11, color=INK, anchor="start"))
    els.append(arrow(lx, ly + 140, lx, ly - 140, color=INK, sw=1.5))
    els.append(text(lx - 8, ly - 145, "B (індукція)", size=11, color=INK, anchor="end"))

    # Межа насичення B_sat
    els.append(line(lx - 140, ly - 110, lx + 140, ly - 110, color=POS, sw=1.2, dash="4,4"))
    els.append(text(lx + 145, ly - 106, "+B_sat", size=11, color=POS, anchor="start", bold=True))

    # Траєкторія однотактного режиму (робота лише вгорі праворуч)
    els.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.8"/>' % (
        lx, ly - 20, lx + 70, ly - 40, lx + 100, ly - 95,
        lx + 60, ly - 10, lx, ly - 20, POS
    ))
    els.append(circle(lx, ly - 20, 4, fill=POS, stroke=POS))
    els.append(text(lx - 12, ly - 20, "B_r (залишок)", size=10, color=MUTED, anchor="end"))
    els.append(text(lx + 70, ly - 120, "Робочий розмах ΔB ≤ B_sat − B_r", size=11, color=POS, bold=True))
    els.append(text(lx, ly + 160, "Потрібне розмагнічування або зазор\nОсердя використовується лише на ~30–40%", size=11, color=MUTED))

    # ── Права панель: Напівмостова топологія ──
    rx = 610
    ry = 240
    els.append(fitbox(rx - 160, 60, 320, 36, "НАПІВМІСТ І ПОВНИЙ МІСТ\nСиметричне біполярне збудження (I та III квадранти)",
                      size=12, bold=True, fill="#eef7ee", stroke=FIELD))
    # Осі B - H
    els.append(arrow(rx - 150, ry, rx + 150, ry, color=INK, sw=1.5))
    els.append(text(rx + 155, ry + 4, "H (струм)", size=11, color=INK, anchor="start"))
    els.append(arrow(rx, ry + 140, rx, ry - 140, color=INK, sw=1.5))
    els.append(text(rx - 8, ry - 145, "B (індукція)", size=11, color=INK, anchor="end"))

    # Межі насичення +B_sat, -B_sat
    els.append(line(rx - 140, ry - 110, rx + 140, ry - 110, color=POS, sw=1.2, dash="4,4"))
    els.append(text(rx + 145, ry - 106, "+B_sat", size=11, color=POS, anchor="start"))
    els.append(line(rx - 140, ry + 110, rx + 140, ry + 110, color=NEG, sw=1.2, dash="4,4"))
    els.append(text(rx + 145, ry + 114, "−B_sat", size=11, color=NEG, anchor="start"))

    # Траєкторія симетричного циклу (повна петля навколо 0,0)
    els.append('<path d="M %d %d Q %d %d %d %d Q %d %d %d %d Q %d %d %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.8"/>' % (
        rx - 90, ry + 85, rx - 30, ry + 10, rx + 90, ry - 85,
        rx + 70, ry - 30, rx, ry + 20,
        rx + 30, ry - 10, rx - 90, ry + 85,
        rx - 70, ry + 30, rx - 90, ry + 85, FIELD
    ))
    els.append(circle(rx, ry, 4, fill=FIELD, stroke=FIELD))
    els.append(text(rx - 75, ry - 95, "Розмах ΔB = 2 · B_peak", size=12, color=FIELD, bold=True))
    els.append(text(rx, ry + 160, "Подвійний розмах індукції\nГабарити сердечника зменшуються майже вдвічі", size=11, color=MUTED))

    render(os.path.join(IMG, "bh-loop.svg"), W, H, *els)


# ── Фігура 4: Автоматичне самобалансування постійної складової (Flux Walking) ─
def fig_flux_balance():
    W, H = 900, 450
    els = []
    els.append(text(W / 2, 28, "Механізм автобалансування середньої точки дільника проти насичення", size=16, bold=True))

    # 4 кроки у вигляді окремих панелей без накладання
    steps = [
        ("1. Асиметрія ШІМ", "t_on1 > t_on2 чи розкид Rds(on)\nВиникає вольт-секундний зсув", POS, 120),
        ("2. Постійний струм Idc", "Крізь обмотку потік заряд\nΔQ = Idc · T", INK, 340),
        ("3. Зсув середньої точки", "Потенціал MID зміщується:\nΔVmid = ΔQ / (C1 + C2)", FIELD, 560),
        ("4. Автокомпенсація", "(Vin − Vmid)·t1 = Vmid·t2\nІнтеграл напруги рівний 0!", NEG, 780),
    ]

    for title, desc, col, cx in steps:
        els.append(fitbox(cx - 95, 60, 190, 85, title + "\n\n" + desc, size=11, bold=True, fill="#fff", stroke=col))

    # Стрілки між етапами (строго між рамками)
    els.append(arrow(218, 102, 242, 102, color=INK, sw=2))
    els.append(arrow(438, 102, 462, 102, color=INK, sw=2))
    els.append(arrow(658, 102, 682, 102, color=INK, sw=2))

    # Нижня частина: ілюстрація відновлення симетрії B-H
    els.append(rect(60, 200, 780, 210, fill="#f9fafb", stroke=MUTED, sw=1.5, rx=8))
    els.append(text(450, 235, "Чому напівміст не боїться однобічного підмагнічування (flux walking)", size=14, bold=True, color=INK))

    els.append(text(450, 275, "У звичайному Push-pull чи повному мості без конденсатора постійний струм наростає лавиною,", size=12, color=POS))
    els.append(text(450, 300, "оскільки опір первинного кола суто омічний (міліоми). Сердечник злітає в насичення.", size=12, color=POS))
    els.append(text(450, 340, "У напівмості ємнісний дільник діє як природний негативний зворотний зв'язок за напругою:", size=12, color=FIELD))
    els.append(text(450, 365, "найменший постійний струм зміщує напругу MID і миттєво ліквідує власну першопричину.", size=12, color=FIELD, bold=True))

    render(os.path.join(IMG, "flux-balance.svg"), W, H, *els)


# ── Фігура 5: Порівняння трьох ключових двотактних топологій ─────────────────
def fig_topologies():
    W, H = 840, 480
    els = []
    els.append(text(W / 2, 28, "Порівняння Push-Pull, Напівмостової та Повномостової топологій", size=16, bold=True))

    cols_x = [170, 420, 670]
    topos = [
        ("Push-Pull (двотактна)", "2 ключі (обидва на GND)", "Напруга на ключах: 2 · Vin", "Чутлива до підмагнічування", "10–500 Вт (низький Vin: 12/24 В)", POS),
        ("Напівміст (Half-Bridge)", "2 ключі (верхній + нижній)", "Напруга на ключах: Vin", "Стійка (автобаланс C1/C2)", "100–1000 Вт (мережа 230 В / 400 В)", FIELD),
        ("Повний міст (Full-Bridge)", "4 ключі (2 верхніх, 2 нижніх)", "Напруга на ключах: Vin", "Потребує симетрії або DC-блока", "> 1000 Вт (кіловати та десятки кВт)", NEG),
    ]

    for i, (name, switches, volt_stress, core_safety, power_band, col) in enumerate(topos):
        cx = cols_x[i]
        # Заголовок колонки
        els.append(fitbox(cx - 110, 60, 220, 40, name, size=13, bold=True, fill="#fff", stroke=col))

        # Картки параметрів
        y = 125
        rows = [
            ("Ключі", switches),
            ("Стрес напруги", volt_stress),
            ("Захист осердя", core_safety),
            ("Діапазон потужності", power_band),
        ]
        for label, val in rows:
            frag, _, _ = textbox(cx, y + 25, label + "\n" + val, size=11, bold=True, stroke=MUTED, fill=FILL, min_w=210)
            els.append(frag)
            y += 65

    # Підсумок у нижній панелі
    els.append(rect(60, 395, 720, 65, fill="#eef7ee", stroke=FIELD, sw=1.5, rx=6))
    els.append(text(420, 420, "Золота середина: напівміст дає повне використання сердечника і стрес ключів лише Vin,",
                    size=12.5, bold=True, color=FIELD))
    els.append(text(420, 442, "заощаджуючи два дорогих ключі порівняно з повним мостом.",
                    size=12, color=INK))

    render(os.path.join(IMG, "topologies.svg"), W, H, *els)


# ── Фігура 6: Мертвий час — компроміс між наскрізним струмом і втратами діодів
def fig_deadtime_danger():
    W, H = 800, 430
    els = []
    els.append(text(W / 2, 28, "Мертвий час (dead-time): небезпека наскрізного струму проти втрат діода", size=16, bold=True))

    # Три зони: Замалий -> Оптимальний -> Завеликий
    zones = [
        ("ЗАМАЛИЙ МЕРТВИЙ ЧАС", "Наскрізний струм (shoot-through)", "Одночасне відкриття Q1 та Q2:\nкоротке замикання шини Vin.\nМиттєвий тепловий вибух кристала.", POS, 160, "#fdeeee"),
        ("ОПТИМАЛЬНИЙ ЧАС", "М'яка комутація (ZVS)", "Індуктивність перезаряджає Coss.\nНапруга спадає до нуля до вмикання.\nМінімальні динамічні втрати.", FIELD, 400, "#eef7ee"),
        ("ЗАВЕЛИКИЙ МЕРТВИЙ ЧАС", "Провідність body-діода", "Струм іде крізь паразитний діод MOSFET.\nПадіння 1.2 В + втрати відновлення Qrr.\nПерегрів ключів і дзвони на фронтах.", NEG, 640, "#eaf0fd"),
    ]

    for title, subtitle, desc, col, cx, bg_col in zones:
        els.append(fitbox(cx - 110, 65, 220, 50, title + "\n" + subtitle, size=11.5, bold=True, fill=bg_col, stroke=col))
        frag, _, _ = textbox(cx, 210, desc, size=11, bold=False, stroke=col, fill="#fff", min_w=215)
        els.append(frag)

    # Нижня шкала вибору мертвого часу
    els.append(line(80, 340, 720, 340, color=INK, sw=2))
    els.append(arrow(80, 340, 725, 340, color=INK, sw=2))
    els.append(text(725, 360, "t_dead", size=12, color=INK, bold=True, anchor="end"))

    # Позначки на шкалі
    els.append(line(270, 330, 270, 350, color=POS, sw=2))
    els.append(text(270, 365, "t_off(max)", size=11, color=POS, bold=True))
    els.append(line(530, 330, 530, 350, color=NEG, sw=2))
    els.append(text(530, 365, "t_dead(max)", size=11, color=NEG, bold=True))

    # Зона оптимуму
    els.append(rect(270, 325, 260, 30, fill="#27ae60", stroke="none", rx=3))
    els.append(text(400, 345, "Діапазон безпечної роботи (~50–200 нс)", size=11, color="#ffffff", bold=True))

    render(os.path.join(IMG, "deadtime-danger.svg"), W, H, *els)


if __name__ == "__main__":
    fig_schematic()
    fig_phases()
    fig_bh_loop()
    fig_flux_balance()
    fig_topologies()
    fig_deadtime_danger()
    print("Всі 6 фігур згенеровано успішно.")
