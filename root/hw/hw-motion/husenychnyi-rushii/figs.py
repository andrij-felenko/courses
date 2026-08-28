# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для статті «Гусеничний рушій: поворот ковзанням»."""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_tracked_undercarriage_anatomy():
    """Фігура 1: Анатомія та будова гусеничного рушія."""
    w, h = 860, 440
    frags = []

    # Заголовок / підкладка
    frags.append(rect(10, 10, w - 20, h - 20, fill="#fdfefe", stroke="#d0d7de", sw=1, rx=8))

    # Спрощена схема гусеничного обводу
    # Задня зірочка (Sprocket) - ведуча
    sprocket_cx, sprocket_cy, sprocket_r = 710, 240, 68
    # Передній лінивець (Idler) - натяжний
    idler_cx, idler_cy, idler_r = 150, 240, 60
    # Опорні котки (Road wheels) - 4 штуки знизу
    road_y = 265
    road_r = 45
    road_xs = [260, 375, 490, 605]
    # Підтримуючі котки (Return rollers) - 2 штуки зверху
    support_y = 175
    support_r = 22
    support_xs = [330, 520]

    # Гусенична стрічка (зовнішній та внутрішній контур)
    track_path = (
        f"M {idler_cx} {idler_cy - idler_r} "
        f"L {sprocket_cx} {sprocket_cy - sprocket_r} "
        f"A {sprocket_r} {sprocket_r} 0 0 1 {sprocket_cx + sprocket_r} {sprocket_cy} "
        f"A {sprocket_r} {sprocket_r} 0 0 1 {sprocket_cx} {sprocket_cy + sprocket_r} "
        f"L {idler_cx} {road_y + road_r} "
        f"A {idler_r} {idler_r} 0 0 1 {idler_cx - idler_r} {idler_cy} "
        f"A {idler_r} {idler_r} 0 0 1 {idler_cx} {idler_cy - idler_r} Z"
    )
    # Зовнішня чорна стрічка з товщиною
    frags.append(f'<path d="{track_path}" fill="none" stroke="{LINE}" stroke-width="14" stroke-linejoin="round"/>')
    frags.append(f'<path d="{track_path}" fill="none" stroke="#606770" stroke-width="6" stroke-linejoin="round"/>')

    # Зубчасте колесо - Зірочка (Sprocket)
    frags.append(circle(sprocket_cx, sprocket_cy, sprocket_r, fill="#e8eaed", stroke=LINE, sw=2))
    frags.append(circle(sprocket_cx, sprocket_cy, 22, fill="#cfd4dc", stroke=LINE, sw=1.5))
    for i in range(12):
        ang = i * (2 * math.pi / 12)
        tx1 = sprocket_cx + (sprocket_r - 4) * math.cos(ang)
        ty1 = sprocket_cy + (sprocket_r - 4) * math.sin(ang)
        tx2 = sprocket_cx + (sprocket_r + 9) * math.cos(ang)
        ty2 = sprocket_cy + (sprocket_r + 9) * math.sin(ang)
        frags.append(line(tx1, ty1, tx2, ty2, color=POS, sw=3.5))

    # Лінивець (Idler)
    frags.append(circle(idler_cx, idler_cy, idler_r, fill="#f1f3f4", stroke=LINE, sw=2))
    frags.append(circle(idler_cx, idler_cy, 20, fill="#cfd4dc", stroke=LINE, sw=1.5))

    # Опорні котки (Road wheels)
    for rx in road_xs:
        frags.append(circle(rx, road_y, road_r, fill="#ffffff", stroke=LINE, sw=2.5))
        frags.append(circle(rx, road_y, road_r - 8, fill="#eef1f6", stroke="#707a8a", sw=1.5))
        frags.append(circle(rx, road_y, 14, fill="#2457d6", stroke=LINE, sw=1.5))

    # Підтримуючі котки (Return rollers)
    for sx in support_xs:
        frags.append(circle(sx, support_y, support_r, fill="#e9ecef", stroke=LINE, sw=1.8))
        frags.append(circle(sx, support_y, 7, fill=LINE, stroke=LINE, sw=1))

    # Механізм натягу та демпферна пружина на лінивці
    frags.append(rect(idler_cx + 20, idler_cy - 12, 60, 24, fill="#fff2cc", stroke="#d6b656", sw=1.5, rx=3))
    # Зигзаг пружини
    spring_pts = [
        f"{idler_cx + 24},{idler_cy}",
        f"{idler_cx + 32},{idler_cy - 8}",
        f"{idler_cx + 40},{idler_cy + 8}",
        f"{idler_cx + 48},{idler_cy - 8}",
        f"{idler_cx + 56},{idler_cy + 8}",
        f"{idler_cx + 64},{idler_cy - 8}",
        f"{idler_cx + 72},{idler_cy + 8}",
        f"{idler_cx + 76},{idler_cy}"
    ]
    frags.append(f'<polyline points="{" ".join(spring_pts)}" fill="none" stroke="{POS}" stroke-width="2"/>')
    frags.append(arrow(idler_cx + 10, idler_cy, idler_cx - 24, idler_cy, color=POS, sw=2))

    # Лінія ґрунту під гусеницею
    frags.append(line(50, road_y + road_r + 7, 810, road_y + road_r + 7, color="#8b5a2b", sw=3))
    # Штриховка ґрунту
    for gx in range(60, 810, 25):
        frags.append(line(gx, road_y + road_r + 8, gx - 12, road_y + road_r + 20, color="#bcaaa4", sw=1.5))

    # Виносні лінії та текстові підписи
    # 1. Ведуча зірочка (Sprocket)
    t1, _, _ = textbox(710, 85, "Провідне колесо (зірочка)\nЗубчасте зачеплення з траками\nПередає тяговий момент", size=11, pad=6, fill="#fdecea", stroke=POS, bold=False)
    frags.append(t1)
    frags.append(arrow(710, 125, sprocket_cx, sprocket_cy - sprocket_r - 2, color=POS, sw=1.5))

    # 2. Лінивець і натягувач
    t2, _, _ = textbox(150, 85, "Лінивець (напрямне колесо)\n+ Натяжний циліндр і пружина\nЗахист від спадання стрічки", size=11, pad=6, fill="#fef9e7", stroke="#d4ac0d", bold=False)
    frags.append(t2)
    frags.append(arrow(150, 125, idler_cx, idler_cy - idler_r - 2, color="#d4ac0d", sw=1.5))

    # 3. Підтримуючі котки
    t3, _, _ = textbox(425, 75, "Підтримуючі котки\nУсувають провисання верхньої гілки", size=11, pad=6, fill="#eaf2f8", stroke="#2980b9", bold=False)
    frags.append(t3)
    frags.append(arrow(390, 100, support_xs[0] + 10, support_y - support_r - 2, color="#2980b9", sw=1.3))
    frags.append(arrow(460, 100, support_xs[1] - 10, support_y - support_r - 2, color="#2980b9", sw=1.3))

    # 4. Опорні котки
    t4, _, _ = textbox(435, 385, "Опорні котки (розподіл ваги mg по довжині контакту L)", size=11, pad=6, fill="#eafaf1", stroke=FIELD, bold=True)
    frags.append(t4)
    frags.append(arrow(340, 370, road_xs[1], road_y + road_r + 2, color=FIELD, sw=1.5))
    frags.append(arrow(530, 370, road_xs[2], road_y + road_r + 2, color=FIELD, sw=1.5))

    # 5. Довжина контакту L
    frags.append(line(idler_cx, 335, sprocket_cx, 335, color=MUTED, sw=1.2, dash="4,3"))
    frags.append(line(idler_cx, 325, idler_cx, 345, color=MUTED, sw=1.2))
    frags.append(line(sprocket_cx, 325, sprocket_cx, 345, color=MUTED, sw=1.2))
    frags.append(text(435, 331, "Довжина опорної бази L", size=11, color=MUTED, anchor="middle", bold=True))

    render(os.path.join(OUT_DIR, "tracked-undercarriage-anatomy.svg"), w, h, *frags)


def fig_skid_steering_kinematics_icr():
    """Фігура 2: Кінематика повороту ковзанням та миттєвий центр швидкостей (ICR)."""
    w, h = 860, 480
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Центр корпусу машини
    chassis_cx, chassis_cy = 500, 240
    track_len = 220
    track_w = 40
    gauge_b = 180  # відстань між осями гусениць

    left_y = chassis_cy - gauge_b / 2
    right_y = chassis_cy + gauge_b / 2

    # Корпус робота (рама)
    frags.append(rect(chassis_cx - track_len / 2 + 20, chassis_cy - gauge_b / 2 + track_w / 2 + 5,
                      track_len - 40, gauge_b - track_w - 10, fill="#f4f6f8", stroke="#95a5a6", sw=1.5, rx=8))

    # Ліва гусениця (вгорі)
    frags.append(rect(chassis_cx - track_len / 2, left_y - track_w / 2, track_len, track_w, fill="#34495e", stroke=LINE, sw=2, rx=6))
    # Права гусениця (внизу)
    frags.append(rect(chassis_cx - track_len / 2, right_y - track_w / 2, track_len, track_w, fill="#34495e", stroke=LINE, sw=2, rx=6))

    # Малювання ґрунтозачепів
    for gx in range(int(chassis_cx - track_len / 2 + 10), int(chassis_cx + track_len / 2), 18):
        frags.append(line(gx, left_y - track_w / 2 + 2, gx, left_y + track_w / 2 - 2, color="#7f8c8d", sw=2))
        frags.append(line(gx, right_y - track_w / 2 + 2, gx, right_y + track_w / 2 - 2, color="#7f8c8d", sw=2))

    # Поздовжня вісь та поперечна вісь
    frags.append(line(chassis_cx - 150, chassis_cy, chassis_cx + 170, chassis_cy, color="#95a5a6", sw=1.2, dash="5,4"))
    frags.append(line(chassis_cx, chassis_cy - 160, chassis_cx, chassis_cy + 160, color="#95a5a6", sw=1.2, dash="5,4"))
    frags.append(circle(chassis_cx, chassis_cy, 4, fill=POS, stroke=LINE, sw=1))
    frags.append(text(chassis_cx + 12, chassis_cy - 8, "C (центр мас)", size=11, color=INK, anchor="start", bold=True))

    # Вектори лінійних швидкостей гусениць: поворот ліворуч (v_r > v_l)
    # Ліва гусениця: повільна вперед
    frags.append(arrow(chassis_cx + track_len / 2, left_y, chassis_cx + track_len / 2 + 55, left_y, color=NEG, sw=2.5))
    frags.append(text(chassis_cx + track_len / 2 + 62, left_y + 4, "v_l", size=13, color=NEG, anchor="start", bold=True))

    # Права гусениця: швидка вперед
    frags.append(arrow(chassis_cx + track_len / 2, right_y, chassis_cx + track_len / 2 + 130, right_y, color=POS, sw=3))
    frags.append(text(chassis_cx + track_len / 2 + 138, right_y + 4, "v_r (v_r > v_l)", size=13, color=POS, anchor="start", bold=True))

    # Вектор швидкості центру мас v_x
    frags.append(arrow(chassis_cx, chassis_cy, chassis_cx + 90, chassis_cy, color=FIELD, sw=2.5))
    frags.append(text(chassis_cx + 95, chassis_cy - 8, "v_x = (v_r + v_l) / 2", size=12, color=FIELD, anchor="start", bold=True))

    # Кутова швидкість ω_z
    arc_d = f"M {chassis_cx + 35} {chassis_cy - 40} A 50 50 0 0 0 {chassis_cx - 35} {chassis_cy - 40}"
    frags.append(f'<path d="{arc_d}" fill="none" stroke="{POS}" stroke-width="2.2" marker-end="url(#arrow)"/>')
    frags.append(text(chassis_cx, chassis_cy - 52, "ω_z = (v_r − v_l) / B", size=12, color=POS, anchor="middle", bold=True))

    # Миттєвий центр швидкостей (ICR)
    icr_x, icr_y = chassis_cx, chassis_cy - 300
    frags.append(circle(icr_x, 35, 7, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(icr_x + 14, 38, "ICR (миттєвий центр обертання)", size=13, color=POS, anchor="start", bold=True))

    # Радіуси обертання від ICR
    frags.append(line(icr_x, 35, chassis_cx, chassis_cy, color=POS, sw=1.5, dash="4,3"))
    frags.append(line(icr_x, 35, chassis_cx, left_y, color=NEG, sw=1.2, dash="3,3"))
    frags.append(line(icr_x, 35, chassis_cx, right_y, color=POS, sw=1.2, dash="3,3"))

    # Підпис радіуса R
    frags.append(text(chassis_cx - 15, 140, "Радіус повороту R", size=12, color=POS, anchor="end", bold=True))
    frags.append(text(chassis_cx - 15, 156, "R = (B / 2) · (v_r + v_l) / (v_r − v_l)", size=11, color=INK, anchor="end"))

    # Розмірні лінії: колія B і база L
    # Колія B
    frags.append(line(chassis_cx - track_len / 2 - 25, left_y, chassis_cx - track_len / 2 - 25, right_y, color=LINE, sw=1.3))
    frags.append(line(chassis_cx - track_len / 2 - 32, left_y, chassis_cx - track_len / 2 - 18, left_y, color=LINE, sw=1.3))
    frags.append(line(chassis_cx - track_len / 2 - 32, right_y, chassis_cx - track_len / 2 - 18, right_y, color=LINE, sw=1.3))
    frags.append(text(chassis_cx - track_len / 2 - 35, chassis_cy + 4, "Колія B", size=12, color=LINE, anchor="end", bold=True))

    # База контакту L
    frags.append(line(chassis_cx - track_len / 2, right_y + 35, chassis_cx + track_len / 2, right_y + 35, color=LINE, sw=1.3))
    frags.append(line(chassis_cx - track_len / 2, right_y + 28, chassis_cx - track_len / 2, right_y + 42, color=LINE, sw=1.3))
    frags.append(line(chassis_cx + track_len / 2, right_y + 28, chassis_cx + track_len / 2, right_y + 42, color=LINE, sw=1.3))
    frags.append(text(chassis_cx, right_y + 52, "Довжина опорної поверхні L", size=12, color=LINE, anchor="middle", bold=True))

    # Інформаційний блок зліва
    info_box, _, _ = textbox(130, 240, "Крайові режими:\n1. Прямо: v_r = v_l → R = ∞\n2. На одній гусениці: v_l = 0 → R = B / 2\n3. На місці (Neutral turn):\n   v_r = −v_l → R = 0", size=11, pad=8, fill="#f4f6f8", stroke="#bdc3c7", bold=False)
    frags.append(info_box)

    render(os.path.join(OUT_DIR, "skid-steering-kinematics-icr.svg"), w, h, *frags)


def fig_soil_shear_forces():
    """Фігура 3: Зсув ґрунту, бічний опір та розподіл моментів при розвороті на місці."""
    w, h = 860, 480
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Центр схеми
    cx, cy = 430, 235
    track_len = 320
    track_w = 46
    gauge_b = 200

    left_y = cy - gauge_b / 2
    right_y = cy + gauge_b / 2

    # Гусениці
    frags.append(rect(cx - track_len / 2, left_y - track_w / 2, track_len, track_w, fill="#34495e", stroke=LINE, sw=2, rx=4))
    frags.append(rect(cx - track_len / 2, right_y - track_w / 2, track_len, track_w, fill="#34495e", stroke=LINE, sw=2, rx=4))

    # Поздовжня та поперечна осі
    frags.append(line(cx - 200, cy, cx + 200, cy, color="#bdc3c7", sw=1.2, dash="5,4"))
    frags.append(line(cx, cy - 170, cx, cy + 170, color="#bdc3c7", sw=1.2, dash="5,4"))
    frags.append(text(cx + 8, cy + 16, "O (центр контакту)", size=11, color=MUTED, anchor="start"))

    # Розворот на місці проти годинникової стрілки (ліва назад v_l < 0, права вперед v_r > 0)
    # Тягові поздовжні сили F_outer та F_inner
    frags.append(arrow(cx + track_len / 2 + 10, right_y, cx + track_len / 2 + 80, right_y, color=POS, sw=3))
    frags.append(text(cx + track_len / 2 + 85, right_y + 5, "+F_тяг (права гусениця)", size=12, color=POS, anchor="start", bold=True))

    frags.append(arrow(cx - track_len / 2 - 10, left_y, cx - track_len / 2 - 80, left_y, color=NEG, sw=3))
    frags.append(text(cx - track_len / 2 - 85, left_y + 5, "−F_тяг (ліва гусениця)", size=12, color=NEG, anchor="end", bold=True))

    # Поперечні сили опору зсуву ґрунту dF_t(x)
    # Ліва гусениця: передня частина зсувається праворуч -> ґрунт чинить опір вліво (вниз на кресленні)
    # задня частина зсувається ліворуч -> ґрунт чинить опір вправо (вгору на кресленні)
    # Для лівої гусениці:
    for dx in range(25, int(track_len / 2), 35):
        # Передня половина (dx > 0)
        frags.append(arrow(cx + dx, left_y - track_w / 2 - 2, cx + dx, left_y - track_w / 2 - 24, color="#d35400", sw=1.8))
        # Задня половина (dx < 0)
        frags.append(arrow(cx - dx, left_y + track_w / 2 + 2, cx - dx, left_y + track_w / 2 + 24, color="#d35400", sw=1.8))

    # Для правої гусениці:
    for dx in range(25, int(track_len / 2), 35):
        # Передня половина (dx > 0)
        frags.append(arrow(cx + dx, right_y + track_w / 2 + 2, cx + dx, right_y + track_w / 2 + 24, color="#d35400", sw=1.8))
        # Задня половина (dx < 0)
        frags.append(arrow(cx - dx, right_y - track_w / 2 - 2, cx - dx, right_y - track_w / 2 - 24, color="#d35400", sw=1.8))

    frags.append(text(cx + 80, left_y - 36, "dF_t(x) = μ_t · q · dx (бічний зсув ґрунту)", size=11, color="#d35400", anchor="middle", bold=True))
    frags.append(text(cx - 80, right_y - 36, "dF_t(x)", size=11, color="#d35400", anchor="middle", bold=True))

    # Момент опору M_c (дуга навколо центру)
    arc_m = f"M {cx + 40} {cy + 40} A 55 55 0 0 1 {cx - 40} {cy + 40}"
    frags.append(f'<path d="{arc_m}" fill="none" stroke="{POS}" stroke-width="2.5" marker-end="url(#arrow)"/>')
    frags.append(text(cx, cy + 70, "Момент опору повороту M_c = (μ_t · m · g · L) / 4", size=12, color=POS, anchor="middle", bold=True))

    # Формульний блок внизу
    tb, _, _ = textbox(cx, 420, "Умова повороту без зриву в юз: F_тяг · B ≥ M_c  ⇒  F_тяг ≥ μ_t · m · g · (L / (4 · B))\nЧим більше відношення L / B, тим більший крутний момент потрібен двигунам!", size=11, pad=7, fill="#fef9e7", stroke="#d4ac0d", bold=False)
    frags.append(tb)

    render(os.path.join(OUT_DIR, "soil-shear-forces.svg"), w, h, *frags)


def fig_power_circulation_and_thermal():
    """Фігура 4: Енергетика повороту, циркуляція потужності та нагрів двигунів."""
    w, h = 860, 440
    frags = []

    frags.append(rect(10, 10, w - 20, h - 20, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Схема потоків енергії зліва
    frags.append(text(220, 40, "Розподіл електричної потужності", size=14, color=INK, anchor="middle", bold=True))

    # Акумулятор
    frags.append(rect(140, 65, 160, 45, fill="#eaf2f8", stroke="#2980b9", sw=1.8, rx=5))
    frags.append(text(220, 88, "Батарея (48V Li-Ion)", size=12, color="#2980b9", anchor="middle", bold=True))
    frags.append(text(220, 102, "Загальний струм I_bat", size=10, color=MUTED, anchor="middle"))

    # Драйвери та двигуни: Лівий (внутрішній) та Правий (зовнішній)
    # Лівий мотор (гальмування або мала тяга)
    frags.append(rect(50, 165, 150, 80, fill="#fdfefe", stroke=NEG, sw=1.5, rx=5))
    frags.append(text(125, 185, "Лівий привід (внутр.)", size=11, color=NEG, anchor="middle", bold=True))
    frags.append(text(125, 205, "I_left: 5 А (або рекуперація)", size=10, color=INK, anchor="middle"))
    frags.append(text(125, 225, "P_loss = I² · R ≈ 15 Вт", size=10, color=FIELD, anchor="middle", bold=True))

    # Правий мотор (максимальне перевантаження)
    frags.append(rect(240, 165, 150, 80, fill="#fdedec", stroke=POS, sw=2, rx=5))
    frags.append(text(315, 185, "Правий привід (зовн.)", size=11, color=POS, anchor="middle", bold=True))
    frags.append(text(315, 205, "I_right: 42 А (перевантаж.)", size=10, color=POS, anchor="middle", bold=True))
    frags.append(text(315, 225, "P_loss = I² · R ≈ 1050 Вт!", size=10, color=POS, anchor="middle", bold=True))

    # Стрілки струму від батареї
    frags.append(arrow(180, 110, 125, 165, color=NEG, sw=1.8))
    frags.append(arrow(260, 110, 315, 165, color=POS, sw=3))

    # Порівняльна гістограма струмів та нагріву справа
    chart_x = 480
    frags.append(text(650, 40, "Стрибок струму та нагріву обмоток", size=14, color=INK, anchor="middle", bold=True))

    # Осі графіка
    frags.append(line(chart_x, 340, chart_x + 330, 340, color=LINE, sw=1.5))
    frags.append(line(chart_x, 80, chart_x, 340, color=LINE, sw=1.5))
    frags.append(text(chart_x - 10, 85, "Струм I (А)", size=11, color=MUTED, anchor="end"))

    # Стовпчики
    # 1. Прямолінійний рух (8 А)
    b1_h = 45
    frags.append(rect(chart_x + 40, 340 - b1_h, 55, b1_h, fill="#27ae60", stroke=LINE, sw=1.2, rx=3))
    frags.append(text(chart_x + 67, 340 - b1_h - 8, "8 А", size=12, color=FIELD, anchor="middle", bold=True))
    frags.append(text(chart_x + 67, 360, "Прямий\nрух", size=10, color=INK, anchor="middle"))
    frags.append(text(chart_x + 67, 395, "T = 42°C\nНорма", size=10, color=FIELD, anchor="middle"))

    # 2. Поворот з великим радіусом (18 А)
    b2_h = 100
    frags.append(rect(chart_x + 135, 340 - b2_h, 55, b2_h, fill="#f39c12", stroke=LINE, sw=1.2, rx=3))
    frags.append(text(chart_x + 162, 340 - b2_h - 8, "18 А", size=12, color="#d35400", anchor="middle", bold=True))
    frags.append(text(chart_x + 162, 360, "Плавний\nповорот", size=10, color=INK, anchor="middle"))
    frags.append(text(chart_x + 162, 395, "T = 65°C\nПомірний", size=10, color="#d35400", anchor="middle"))

    # 3. Розворот на місці в піску/болоті (42 А)
    b3_h = 230
    frags.append(rect(chart_x + 230, 340 - b3_h, 55, b3_h, fill="#e74c3c", stroke=POS, sw=2, rx=3))
    frags.append(text(chart_x + 257, 340 - b3_h - 8, "42 А!", size=12, color=POS, anchor="middle", bold=True))
    frags.append(text(chart_x + 257, 360, "Розворот\nна місці", size=10, color=POS, anchor="middle", bold=True))
    frags.append(text(chart_x + 257, 395, "T > 130°C!\nПерегрів", size=10, color=POS, anchor="middle", bold=True))

    # Лінія граничного струму драйвера
    frags.append(line(chart_x, 340 - 180, chart_x + 330, 340 - 180, color=POS, sw=1.2, dash="4,3"))
    frags.append(text(chart_x + 325, 340 - 186, "Thermal Limit", size=10, color=POS, anchor="end", italic=True))

    # Висновок знизу
    frags.append(text(220, 300, "Джоулеве тепло росте як I²:\nПри 5-кратному струмі втрати зростають у 25 разів!", size=11, color=POS, anchor="middle", bold=True))

    render(os.path.join(OUT_DIR, "power-circulation-and-thermal.svg"), w, h, *frags)


if __name__ == '__main__':
    fig_tracked_undercarriage_anatomy()
    fig_skid_steering_kinematics_icr()
    fig_soil_shear_forces()
    fig_power_circulation_and_thermal()
    print("All figures generated successfully.")
