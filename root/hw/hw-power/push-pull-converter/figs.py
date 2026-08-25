# -*- coding: utf-8 -*-
"""Фігури до теми «Двотактний (push-pull) перетворювач».
Запуск: python figs.py  → пише .svg у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def path_d(pts):
    return "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])


# ── Фігура 1: Принципова схема ізольованого двотактного перетворювача ───────
def fig_topology():
    W, H = 860, 480
    els = []
    els.append(text(W / 2, 28, "Принципова схема ізольованого двотактного (Push-Pull) перетворювача", size=16, bold=True))

    # ── Первинна сторона (гаряча земля) ──
    # Вхідне живлення Vin
    els.append(line(60, 90, 60, 410, color=POS, sw=2.5))  # шина +Vin
    els.append(line(60, 410, 310, 410, color=INK, sw=2))  # шина GND первинна
    els.append(text(50, 80, "+Vin", size=14, color=POS, bold=True, anchor="start"))
    els.append(text(50, 430, "GND (перв.)", size=12, color=MUTED, anchor="start"))

    # Центральний відвід первинної обмотки
    els.append(line(60, 240, 260, 240, color=POS, sw=2.5))
    els.append(circle(260, 240, 4.5, fill=POS, stroke=POS))
    els.append(text(210, 230, "Центральний відвід (+Vin)", size=11, color=POS, bold=True))

    # Первинні напівобмотки Np1 та Np2
    # З'єднання відводу з обмотками
    els.append(line(260, 240, 260, 160, color=POS, sw=2))
    els.append(line(260, 240, 260, 320, color=POS, sw=2))
    els.append(line(260, 160, 280, 160, color=POS, sw=2))
    els.append(line(260, 320, 280, 320, color=POS, sw=2))

    # Обмотка Np1 (верхня)
    els.append(rect(280, 130, 30, 60, fill="#eef4ff", stroke=NEG, sw=2, rx=4))
    els.append(text(295, 164, "Np1", size=12, color=NEG, bold=True))
    els.append(circle(288, 140, 3, fill=INK, stroke=INK))  # крапка полярності

    # Обмотка Np2 (нижня)
    els.append(rect(280, 290, 30, 60, fill="#eef4ff", stroke=NEG, sw=2, rx=4))
    els.append(text(295, 324, "Np2", size=12, color=NEG, bold=True))
    els.append(circle(288, 300, 3, fill=INK, stroke=INK))  # крапка полярності

    # Магнітопровід (феритове осердя)
    els.append(line(320, 105, 320, 375, color=INK, sw=2.5))
    els.append(line(326, 105, 326, 375, color=INK, sw=2.5))
    els.append(text(323, 95, "T1 (ферит)", size=11, color=MUTED))

    # Ключі Q1 та Q2
    # Ключ Q1 (верхній)
    els.append(line(280, 130, 210, 130, color=INK, sw=2))
    els.append(line(210, 130, 210, 145, color=INK, sw=2))
    frag1, _, _ = textbox(210, 170, "Q1 (MOSFET)\nVds1 = 2·Vin", size=11, bold=True, stroke=POS, fill="#fff", min_w=95)
    els.append(frag1)
    # Витік Q1 обходить Q2 зліва на x=150
    els.append(line(210, 195, 145, 195, color=INK, sw=2))
    els.append(line(145, 195, 145, 410, color=INK, sw=2))

    # Ключ Q2 (нижній)
    els.append(line(280, 350, 210, 350, color=INK, sw=2))
    els.append(line(210, 350, 210, 362, color=INK, sw=2))
    frag2, _, _ = textbox(210, 385, "Q2 (MOSFET)\nVds2 = 2·Vin", size=11, bold=True, stroke=NEG, fill="#fff", min_w=95)
    els.append(frag2)
    els.append(line(210, 408, 210, 410, color=INK, sw=2))

    # Сигнали керування затворами
    els.append(arrow(60, 170, 120, 170, color=POS, sw=1.8))
    els.append(text(90, 155, "PWM 1", size=11, color=POS, bold=True))
    els.append(arrow(60, 385, 120, 385, color=NEG, sw=1.8))
    els.append(text(90, 370, "PWM 2 (180°)", size=10, color=NEG, bold=True))

    # ── Вторинна сторона (ізольована) ──
    # Вторинні обмотки Ns1 та Ns2
    els.append(rect(336, 130, 30, 60, fill="#fdeeee", stroke=POS, sw=2, rx=4))
    els.append(text(351, 164, "Ns1", size=12, color=POS, bold=True))
    els.append(circle(358, 140, 3, fill=INK, stroke=INK))  # крапка

    els.append(rect(336, 290, 30, 60, fill="#fdeeee", stroke=POS, sw=2, rx=4))
    els.append(text(351, 324, "Ns2", size=12, color=POS, bold=True))
    els.append(circle(358, 300, 3, fill=INK, stroke=INK))  # крапка

    # Центральний відвід вторинної обмотки -> вторинна земля GND_sec
    els.append(line(366, 190, 400, 190, color=INK, sw=2))
    els.append(line(366, 290, 400, 290, color=INK, sw=2))
    els.append(line(400, 190, 400, 290, color=INK, sw=2))
    els.append(circle(400, 240, 4.5, fill=INK, stroke=INK))
    els.append(line(400, 240, 400, 410, color=INK, sw=2))
    els.append(line(400, 410, 800, 410, color=INK, sw=2))
    els.append(text(400, 430, "GND (вторинна)", size=12, color=MUTED))

    # Випрямні діоди D1, D2
    els.append(line(366, 130, 440, 130, color=POS, sw=2))
    els.append('<path d="M440 118 L440 142 L464 130 Z" fill="#fdeeee" stroke="%s" stroke-width="2"/>' % POS)
    els.append(line(464, 118, 464, 142, color=POS, sw=2.5))
    els.append(text(452, 108, "D1", size=12, color=POS, bold=True))

    els.append(line(366, 350, 440, 350, color=POS, sw=2))
    els.append('<path d="M440 338 L440 362 L464 350 Z" fill="#fdeeee" stroke="%s" stroke-width="2"/>' % POS)
    els.append(line(464, 338, 464, 362, color=POS, sw=2.5))
    els.append(text(452, 378, "D2", size=12, color=POS, bold=True))

    # З'єднання катодів діодів до дроселя Lout
    els.append(line(464, 130, 510, 130, color=POS, sw=2))
    els.append(line(464, 350, 510, 350, color=POS, sw=2))
    els.append(line(510, 130, 510, 350, color=POS, sw=2))
    els.append(circle(510, 240, 4.5, fill=POS, stroke=POS))
    els.append(line(510, 240, 540, 240, color=POS, sw=2.5))

    # Вихідний дросель Lout
    frag_l, _, _ = textbox(575, 240, "Lout\n(дросель)", size=11, bold=True, stroke=POS, fill="#fff", min_w=65)
    els.append(frag_l)
    els.append(line(610, 240, 680, 240, color=POS, sw=2.5))

    # Вихідний конденсатор Cout
    cx = 680
    els.append(line(cx, 240, cx, 300, color=POS, sw=2))
    els.append(line(cx - 18, 300, cx + 18, 300, color=INK, sw=2.5))
    els.append(line(cx - 18, 312, cx + 18, 312, color=INK, sw=2.5))
    els.append(text(cx + 28, 306, "Cout", size=12, color=NEG, bold=True, anchor="start"))
    els.append(line(cx, 312, cx, 410, color=INK, sw=2))

    # Навантаження Rload
    rx = 760
    els.append(line(680, 240, rx, 240, color=POS, sw=2.5))
    els.append(line(rx, 240, rx, 280, color=POS, sw=2))
    frag_r, _, _ = textbox(rx, 310, "Rн\n(навант.)", size=11, bold=True, stroke=INK, fill="#fff", min_w=60)
    els.append(frag_r)
    els.append(line(rx, 340, rx, 410, color=INK, sw=2))

    # Вихідна напруга Vout
    els.append(text(720, 225, "+Vout", size=13, color=POS, bold=True))
    els.append(arrow(740, 250, 740, 390, color=FIELD, sw=1.8))
    els.append(text(748, 320, "Vout", size=12, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(IMG, "topology.svg"), W, H, *els)


# ── Фігура 2: Часові діаграми комутації push-pull перетворювача ─────────────
def fig_phases():
    W, H = 840, 560
    els = []
    els.append(text(W / 2, 26, "Часові діаграми напруг, струмів та індукції двотактного перетворювача", size=15, bold=True))

    # Межі періодів
    x0, x_end = 170, 780
    T_len = (x_end - x0) / 2
    x_half = x0 + T_len
    ton = T_len * 0.4

    # Вертикальні розділові сітки фаз
    t_points = [
        (x0, "0"),
        (x0 + ton, "ton"),
        (x_half, "T/2"),
        (x_half + ton, "T/2+ton"),
        (x_end, "T")
    ]
    for px, label in t_points:
        els.append(line(px, 50, px, 515, color="#e0e0e0", sw=1.2, dash="3,3"))
        els.append(text(px, 530, label, size=11, color=MUTED))

    # 6 сигналів: V_gate1, V_gate2, V_ds1, V_ds2, B(t), I_L(t)
    sigs = [
        ("V_gate(Q1)", 85, [
            (x0, 100), (x0, 65), (x0 + ton, 65), (x0 + ton, 100),
            (x_end, 100)
        ], POS),
        ("V_gate(Q2)", 155, [
            (x0, 170), (x_half, 170), (x_half, 135), (x_half + ton, 135), (x_half + ton, 170),
            (x_end, 170)
        ], NEG),
        ("V_ds(Q1)", 235, [
            (x0, 250), (x0 + ton, 250), (x0 + ton, 230), (x_half, 230),
            (x_half, 205), (x_half + ton, 205), (x_half + ton, 230), (x_end, 230)
        ], POS),
        ("V_ds(Q2)", 315, [
            (x0, 285), (x0 + ton, 285), (x0 + ton, 310), (x_half, 310),
            (x_half, 330), (x_half + ton, 330), (x_half + ton, 310), (x_end, 310)
        ], NEG),
        ("B(t) осердя", 400, [
            (x0, 420), (x0 + ton, 380), (x_half, 380),
            (x_half + ton, 420), (x_end, 420)
        ], FIELD),
        ("i_L(t) вихідний", 480, [
            (x0, 495), (x0 + ton, 465), (x_half, 495),
            (x_half + ton, 465), (x_end, 495)
        ], INK)
    ]

    for name, base_y, pts, col in sigs:
        # Назва осі зліва
        els.append(text(x0 - 15, base_y, name, size=11.5, bold=True, color=col, anchor="end"))
        # Нульова вісь
        els.append(line(x0, base_y + 15, x_end + 10, base_y + 15, color="#bbb", sw=1))

        # Малювання полілінії сигналу
        for i in range(len(pts) - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            els.append(line(x1, y1, x2, y2, color=col, sw=2.2))

    # Позначки рівнів напруги для Vds
    els.append(text(x_half + 45, 198, "2·Vin", size=10.5, color=POS, bold=True))
    els.append(text(x0 + 45, 278, "2·Vin", size=10.5, color=NEG, bold=True))
    els.append(text(x0 - 25, 230, "Vin", size=10, color=MUTED, anchor="end"))

    # Позначки індукції
    els.append(text(x0 + ton + 10, 375, "+B_max", size=10.5, color=FIELD, bold=True))
    els.append(text(x0 - 25, 420, "−B_max", size=10.5, color=FIELD, bold=True, anchor="end"))
    els.append(text(x_end + 15, 400, "ΔB = 2·B_max", size=11, color=FIELD, bold=True, anchor="start"))

    # Позначка частоти на дроселі
    els.append(text(x_end + 15, 480, "f_out = 2·f_sw", size=11, color=INK, bold=True, anchor="start"))

    render(os.path.join(IMG, "phases.svg"), W, H, *els)


# ── Фігура 3: Порівняння використання петлі гістерезису ─────────────────────
def fig_bh_comparison():
    W, H = 840, 440
    els = []
    els.append(text(W / 2, 26, "Використання петлі гістерезису: однотактний Forward проти Push-Pull", size=15, bold=True))

    # Панель 1 (ліва): Однотактний Forward
    cx1 = 220
    els.append(rect(40, 55, 360, 360, fill="#fafbfc", stroke="#d0d5dd", sw=1.5, rx=8))
    els.append(text(cx1, 80, "Однотактний Forward (1 квадрант)", size=13, bold=True, color=POS))

    # Осі B і H
    els.append(arrow(cx1, 380, cx1, 105, color=INK, sw=1.5))  # Вісь B
    els.append(arrow(60, 245, 380, 245, color=INK, sw=1.5))  # Вісь H
    els.append(text(cx1 + 12, 115, "B (Тл)", size=11, bold=True, anchor="start"))
    els.append(text(375, 235, "H (А/м)", size=11, bold=True, anchor="end"))

    # Траєкторія Forward (лише I квадрант)
    els.append('<path d="M %d 215 Q %d 180 %d 150 Q %d 180 %d 215" fill="none" stroke="%s" stroke-width="2.8"/>'
               % (cx1, cx1 + 90, cx1 + 90, cx1 + 30, cx1, POS))
    # Заштрихована/виділена робоча зона
    els.append(rect(cx1 + 8, 140, 115, 65, fill="#fdeeee", stroke=POS, sw=1, rx=4))
    els.append(text(cx1 + 65, 162, "Робоча зона ΔB", size=11, color=POS, bold=True))
    els.append(text(cx1 + 65, 180, "ΔB = B_max − B_r", size=10.5, color=POS))
    els.append(text(cx1 + 65, 196, "≈ 0.15–0.18 Тл", size=10.5, color=MUTED))

    els.append(circle(cx1, 215, 3.5, fill=POS, stroke=POS))
    els.append(text(cx1 - 10, 215, "B_r", size=11, color=POS, bold=True, anchor="end"))
    els.append(circle(cx1 + 90, 150, 3.5, fill=POS, stroke=POS))
    els.append(text(cx1 + 95, 145, "B_max", size=11, color=POS, bold=True, anchor="start"))

    els.append(text(cx1, 395, "Перемагнічування лише в один бік", size=11, color=MUTED))

    # Панель 2 (права): Двотактний Push-Pull
    cx2 = 620
    els.append(rect(440, 55, 360, 360, fill="#fafbfc", stroke="#d0d5dd", sw=1.5, rx=8))
    els.append(text(cx2, 80, "Двотактний Push-Pull (I та III квадранти)", size=13, bold=True, color=FIELD))

    # Осі B і H
    els.append(arrow(cx2, 380, cx2, 105, color=INK, sw=1.5))
    els.append(arrow(460, 245, 780, 245, color=INK, sw=1.5))
    els.append(text(cx2 + 12, 115, "B (Тл)", size=11, bold=True, anchor="start"))
    els.append(text(775, 235, "H (А/м)", size=11, bold=True, anchor="end"))

    # Симетрична повна петля
    els.append('<path d="M %d 340 Q %d 320 %d 245 Q %d 170 %d 150 Q %d 170 %d 245 Q %d 320 %d 340" '
               'fill="none" stroke="%s" stroke-width="2.8"/>'
               % (cx2 - 80, cx2 - 20, cx2 + 20, cx2 + 80, cx2 + 80, cx2 + 20, cx2 - 20, cx2 - 80, cx2 - 80, FIELD))

    # Виділена подвійна робоча зона (написи зміщені вгору над H-віссю)
    els.append(rect(cx2 - 85, 145, 170, 80, fill="#eef7ee", stroke=FIELD, sw=1, rx=4))
    els.append(text(cx2, 170, "Повна симетрична петля", size=11, color=FIELD, bold=True))
    els.append(text(cx2, 190, "ΔB = 2 · B_max", size=11.5, color=FIELD, bold=True))
    els.append(text(cx2, 210, "≈ 0.40–0.60 Тл (удвічі більше!)", size=10, color=FIELD))

    # Позначки точок +Bmax та -Bmax
    els.append(circle(cx2 + 80, 150, 3.5, fill=FIELD, stroke=FIELD))
    els.append(text(cx2 + 88, 145, "+B_max", size=11, color=FIELD, bold=True, anchor="start"))
    els.append(circle(cx2 - 80, 340, 3.5, fill=FIELD, stroke=FIELD))
    els.append(text(cx2 - 88, 345, "−B_max", size=11, color=FIELD, bold=True, anchor="end"))

    els.append(text(cx2, 395, "Габарити осердя зменшені в 1.8–2 рази", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "bh-comparison.svg"), W, H, *els)


# ── Фігура 4: Механізм одностороннього підмагнічування та захист PCMC ───────
def fig_flux_walking():
    W, H = 840, 480
    els = []
    els.append(text(W / 2, 26, "Явище зміщення магнітного потоку (Flux Walking) та стабілізація за струмом", size=15, bold=True))

    # Панель 1 (ліва): Асиметрія та звалювання в насичення (Voltage Mode)
    cx1 = 220
    els.append(rect(40, 55, 360, 400, fill="#fdfbfb", stroke=POS, sw=1.5, rx=8))
    els.append(text(cx1, 80, "Асиметрія імпульсів (Voltage Mode)", size=13, bold=True, color=POS))
    els.append(text(cx1, 98, "Незбалансовані вольт-секунди: V1·t1 ≠ V2·t2", size=10.5, color=MUTED))

    # Сходинкове наростання індукції B(t)
    bx0, by0 = 70, 240
    els.append(line(bx0, by0, 370, by0, color="#bbb", sw=1))
    els.append(text(bx0 + 10, by0 - 85, "+B_sat (насичення)", size=10.5, color=POS, bold=True))
    els.append(line(bx0, by0 - 75, 370, by0 - 75, color=POS, sw=1.5, dash="3,3"))

    # Сходинки
    pts_b = [
        (bx0, by0), (bx0 + 35, by0 - 25), (bx0 + 60, by0 - 25),
        (bx0 + 95, by0 - 5), (bx0 + 120, by0 - 5),
        (bx0 + 155, by0 - 45), (bx0 + 180, by0 - 45),
        (bx0 + 215, by0 - 20), (bx0 + 240, by0 - 20),
        (bx0 + 275, by0 - 75), (bx0 + 300, by0 - 75)
    ]
    for i in range(len(pts_b) - 1):
        els.append(line(pts_b[i][0], pts_b[i][1], pts_b[i + 1][0], pts_b[i + 1][1], color=POS, sw=2.2))

    els.append(text(bx0 + 160, by0 + 20, "Сходинкове зміщення потоку", size=10.5, color=POS))

    # Сплеск струму внизу
    iy0 = 390
    els.append(line(bx0, iy0, 370, iy0, color="#bbb", sw=1))
    els.append(text(bx0 + 10, iy0 - 70, "Струм ключа I_pk", size=10.5, color=POS, bold=True))
    pts_i_vm = [
        (bx0 + 10, iy0), (bx0 + 35, iy0 - 15), (bx0 + 35, iy0),
        (bx0 + 130, iy0), (bx0 + 155, iy0 - 25), (bx0 + 155, iy0),
        (bx0 + 250, iy0), (bx0 + 275, iy0 - 65), (bx0 + 275, iy0)
    ]
    els.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_d(pts_i_vm), POS))
    els.append(text(bx0 + 280, iy0 - 50, "Вибухове зростання!", size=10.5, color=POS, bold=True, anchor="start"))
    els.append(text(cx1, 435, "Результат: тепловий пробій MOSFET", size=11, color=POS, bold=True))

    # Панель 2 (права): Автоматичне центрування (Current Mode Control)
    cx2 = 620
    els.append(rect(440, 55, 360, 400, fill="#fbfdfb", stroke=FIELD, sw=1.5, rx=8))
    els.append(text(cx2, 80, "Поцикловий захист (Current Mode)", size=13, bold=True, color=FIELD))
    els.append(text(cx2, 98, "Обмеження за піковим струмом: I_pk1 = I_pk2", size=10.5, color=MUTED))

    # Струмовий поріг I_ref
    px0, py0 = 470, 240
    els.append(line(px0, py0 - 45, 770, py0 - 45, color=FIELD, sw=1.5, dash="3,3"))
    els.append(text(px0 + 10, py0 - 55, "Поріг компаратора I_ref", size=10.5, color=FIELD, bold=True))

    # Форма струму з динамічним обтинанням ширини
    pts_i_cm = [
        (px0 + 15, py0), (px0 + 55, py0 - 45), (px0 + 55, py0),
        (px0 + 115, py0), (px0 + 145, py0 - 45), (px0 + 145, py0),
        (px0 + 205, py0), (px0 + 240, py0 - 45), (px0 + 240, py0)
    ]
    els.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_d(pts_i_cm), FIELD))

    els.append(text(px0 + 35, py0 + 18, "ton1 (авто-зменшення)", size=10, color=FIELD))
    els.append(text(px0 + 130, py0 + 18, "ton2 (баланс)", size=10, color=FIELD))

    # Стабільна індукція B(t) внизу
    by2 = 380
    els.append(line(px0, by2, 770, by2, color="#bbb", sw=1))
    els.append(text(px0 + 10, by2 - 40, "Індукція B(t) строго центрована", size=10.5, color=FIELD, bold=True))
    pts_b_cm = [
        (px0 + 15, by2 + 25), (px0 + 55, by2 - 25), (px0 + 115, by2 - 25),
        (px0 + 145, by2 + 25), (px0 + 205, by2 + 25), (px0 + 240, by2 - 25)
    ]
    els.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path_d(pts_b_cm), FIELD))

    els.append(text(cx2, 435, "Результат: абсолютна стійкість осердя", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "flux-walking.svg"), W, H, *els)


# ── Фігура 5: Індуктивність розсіювання та демпфувальні кола (снубери) ───────
def fig_snubber_leakage():
    W, H = 840, 460
    els = []
    els.append(text(W / 2, 26, "Паразитна індуктивність розсіювання L_lk та захисні снубери", size=15, bold=True))

    # Схема первинного кола з L_lk та снуберами
    # Центральний відвід
    els.append(line(60, 230, 200, 230, color=POS, sw=2.5))
    els.append(text(60, 220, "+Vin", size=13, color=POS, bold=True, anchor="start"))
    els.append(circle(200, 230, 4, fill=POS, stroke=POS))

    # Верхня гілка: L_lk1 + Np1
    els.append(line(200, 230, 200, 140, color=POS, sw=2))
    els.append(line(200, 140, 240, 140, color=POS, sw=2))
    # Індуктивність розсіювання L_lk1
    frag_lk1, _, _ = textbox(270, 140, "L_lk1\n(розсіювання)", size=10.5, bold=True, stroke=POS, fill="#fff", min_w=85)
    els.append(frag_lk1)
    els.append(line(315, 140, 360, 140, color=POS, sw=2))
    # Обмотка Np1
    els.append(rect(360, 115, 30, 50, fill="#eef4ff", stroke=NEG, sw=2, rx=4))
    els.append(text(375, 144, "Np1", size=11, color=NEG, bold=True))

    # Нижня гілка: L_lk2 + Np2
    els.append(line(200, 230, 200, 320, color=POS, sw=2))
    els.append(line(200, 320, 240, 320, color=POS, sw=2))
    frag_lk2, _, _ = textbox(270, 320, "L_lk2\n(розсіювання)", size=10.5, bold=True, stroke=NEG, fill="#fff", min_w=85)
    els.append(frag_lk2)
    els.append(line(315, 320, 360, 320, color=POS, sw=2))
    # Обмотка Np2
    els.append(rect(360, 295, 30, 50, fill="#eef4ff", stroke=NEG, sw=2, rx=4))
    els.append(text(375, 324, "Np2", size=11, color=NEG, bold=True))

    # Осердя
    els.append(line(405, 100, 405, 360, color=INK, sw=2.5))
    els.append(line(411, 100, 411, 360, color=INK, sw=2.5))

    # Ключі
    # Q1
    els.append(line(360, 115, 360, 90, color=INK, sw=2))
    els.append(line(360, 90, 470, 90, color=INK, sw=2))
    els.append(line(470, 90, 470, 120, color=INK, sw=2))
    frag_q1, _, _ = textbox(470, 145, "Q1", size=12, bold=True, stroke=POS, fill="#fff", min_w=50)
    els.append(frag_q1)
    els.append(line(470, 170, 470, 400, color=INK, sw=2))

    # Q2
    els.append(line(360, 345, 360, 370, color=INK, sw=2))
    els.append(line(360, 370, 470, 370, color=INK, sw=2))
    els.append(line(470, 370, 470, 340, color=INK, sw=2))
    frag_q2, _, _ = textbox(470, 315, "Q2", size=12, bold=True, stroke=NEG, fill="#fff", min_w=50)
    els.append(frag_q2)
    els.append(line(470, 290, 470, 260, color=INK, sw=2))
    els.append(line(470, 340, 470, 400, color=INK, sw=2))

    els.append(line(470, 400, 800, 400, color=INK, sw=2))
    els.append(text(470, 420, "GND", size=11, color=MUTED))

    # RC-снубери паралельно кожному транзистору
    # RC1 для Q1: між стоком (470, 90) та витоком/GND (470, 195)
    els.append(line(470, 90, 560, 90, color=POS, sw=1.8))
    els.append(line(560, 90, 560, 125, color=POS, sw=1.8))
    frag_rc1, _, _ = textbox(560, 150, "R_sn1 + C_sn1\n(RC-демпфер)", size=10, bold=True, stroke=POS, fill="#fdfbfb", min_w=85)
    els.append(frag_rc1)
    els.append(line(560, 175, 560, 210, color=INK, sw=1.8))
    els.append(line(560, 210, 470, 210, color=INK, sw=1.8))

    # RC2 для Q2: між стоком (470, 370) та витоком/GND (470, 400)
    els.append(line(470, 370, 560, 370, color=NEG, sw=1.8))
    els.append(line(560, 370, 560, 345, color=NEG, sw=1.8))
    frag_rc2, _, _ = textbox(560, 320, "R_sn2 + C_sn2\n(RC-демпфер)", size=10, bold=True, stroke=NEG, fill="#fdfbfb", min_w=85)
    els.append(frag_rc2)
    els.append(line(560, 295, 560, 260, color=INK, sw=1.8))
    els.append(line(560, 260, 470, 260, color=INK, sw=1.8))

    # Права інформаційна панель: формули напруги та рекомендації
    els.append(rect(640, 90, 180, 280, fill="#fafbfc", stroke="#d0d5dd", sw=1.5, rx=6))
    els.append(text(730, 115, "Рівень перенапруги", size=12, bold=True, color=POS))
    els.append(text(730, 140, "Vds_max = 2·Vin + V_spike", size=11, bold=True, color=INK))
    els.append(text(730, 165, "V_spike = L_lk · (di/dt)", size=10.5, color=POS))

    els.append(line(655, 185, 805, 185, color="#e0e0e0", sw=1))

    els.append(text(730, 205, "Методи придушення:", size=11, bold=True, color=FIELD))
    els.append(text(730, 230, "1. Біфілярна намотка", size=10.5, color=INK))
    els.append(text(730, 248, "(мінімізує L_lk)", size=9.5, color=MUTED))
    els.append(text(730, 275, "2. RC-снубери", size=10.5, color=INK))
    els.append(text(730, 293, "(гасять дзвін f_ring)", size=9.5, color=MUTED))
    els.append(text(730, 320, "3. Ключі на 2.5–3·Vin", size=10.5, color=INK))
    els.append(text(730, 338, "(запас за напругою)", size=9.5, color=MUTED))

    render(os.path.join(IMG, "snubber-leakage.svg"), W, H, *els)


if __name__ == "__main__":
    fig_topology()
    fig_phases()
    fig_bh_comparison()
    fig_flux_walking()
    fig_snubber_leakage()
    print("Всі 5 фігур згенеровано успішно.")
