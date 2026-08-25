# -*- coding: utf-8 -*-
import sys, os, math

# Import svgkit from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_helmert_geometry():
    """Фігура 1: Геометрія 7-параметричного перетворення Гельмерта."""
    W, H = 840, 520
    f = []

    # Тло та заголовок
    f.append(text(W / 2, 28, "Семипараметричне перетворення Гельмерта у тривимірному просторі", size=16, bold=True))

    # Вихідна система A (Синя)
    oax, oay = 160.0, 380.0
    f.append(circle(oax, oay, 5, fill=NEG, stroke=NEG))
    tb_oa, _, _ = textbox(oax - 35, oay + 22, "O_A (вихідний центр)", size=12, color=NEG, bold=True, fill="#eef3fd", stroke=NEG)
    f.append(tb_oa)

    # Осі системи A
    f.append(arrow(oax, oay, oax + 130, oay + 40, color=NEG, sw=2.0))
    f.append(text(oax + 145, oay + 45, "X_A", size=13, color=NEG, bold=True))

    f.append(arrow(oax, oay, oax + 150, oay - 20, color=NEG, sw=2.0))
    f.append(text(oax + 165, oay - 20, "Y_A", size=13, color=NEG, bold=True))

    f.append(arrow(oax, oay, oax, oay - 140, color=NEG, sw=2.0))
    f.append(text(oax, oay - 150, "Z_A", size=13, color=NEG, bold=True))

    # Цільова система B (Червона)
    obx, oby = 410.0, 320.0
    f.append(circle(obx, oby, 5, fill=POS, stroke=POS))
    tb_ob, _, _ = textbox(obx + 20, oby + 35, "O_B (цільовий центр)", size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    f.append(tb_ob)

    # Вектор зсуву початку координат T = (Tx, Ty, Tz)
    f.append(arrow(oax, oay, obx, oby, color=INK, sw=2.2))
    tb_t, _, _ = textbox((oax + obx) / 2 - 10, (oay + oby) / 2 + 30, "Зсув: T = (Tx, Ty, Tz)", size=12, color=INK, bold=True, fill="#fff9db", stroke="#d4b106")
    f.append(tb_t)

    # Осі системи B (повернуті відносно A)
    ang_x = 0.22
    ang_y = -0.15
    ang_z = -0.30

    # Вісь X_B
    f.append(arrow(obx, oby, obx + 120 * math.cos(ang_x), oby + 120 * math.sin(ang_x) + 40, color=POS, sw=2.0))
    f.append(text(obx + 130 * math.cos(ang_x) + 15, oby + 120 * math.sin(ang_x) + 45, "X_B", size=13, color=POS, bold=True))

    # Вісь Y_B
    f.append(arrow(obx, oby, obx + 140 * math.cos(ang_y), oby + 140 * math.sin(ang_y) - 20, color=POS, sw=2.0))
    f.append(text(obx + 150 * math.cos(ang_y) + 15, oby + 140 * math.sin(ang_y) - 20, "Y_B", size=13, color=POS, bold=True))

    # Вісь Z_B
    f.append(arrow(obx, oby, obx - 140 * math.sin(ang_z), oby - 140 * math.cos(ang_z), color=POS, sw=2.0))
    f.append(text(obx - 150 * math.sin(ang_z), oby - 150 * math.cos(ang_z), "Z_B", size=13, color=POS, bold=True))

    # Точка P у просторі
    px, py = 640.0, 110.0
    f.append(circle(px, py, 6, fill="#27ae60", stroke="#1e8449", sw=2))
    tb_p, _, _ = textbox(px + 45, py - 18, "Точка P", size=13, color="#1e8449", bold=True, fill="#eafaf1", stroke="#27ae60")
    f.append(tb_p)

    # Вектор P_A (від O_A до P)
    f.append(line(oax, oay, px, py, color=NEG, sw=1.8, dash="6,4"))
    f.append(text((oax + px) / 2 - 35, (oay + py) / 2 - 10, "Вектор P_A", size=12, color=NEG, bold=True))

    # Вектор P_B (від O_B до P)
    f.append(line(obx, oby, px, py, color=POS, sw=1.8, dash="6,4"))
    f.append(text((obx + px) / 2 + 40, (oby + py) / 2 + 10, "Вектор P_B", size=12, color=POS, bold=True))

    # Інформаційні блоки праворуч / внизу
    card_text = (
        "Сім параметрів зв'язку:\n"
        "• 3 лінійні зсуви початку відліку: Tx, Ty, Tz\n"
        "• 3 просторові кути обертання осей: Rx, Ry, Rz\n"
        "• 1 масштабний коефіцієнт: s (або m = s · 10⁶ ppm)\n\n"
        "Формула просторової подібності:\n"
        "P_B = T + (1 + s) · R · P_A"
    )
    fb = fitbox(480, 365, 340, 135, card_text, size=12, pad=10, fill=FILL, stroke=LINE)
    f.append(fb)

    render(os.path.join(IMG, "helmert-geometry.svg"), W, H, *f)


def fig_conventions_pv_vs_cf():
    """Фігура 2: Порівняння конвенцій Position Vector (EPSG:9606) та Coordinate Frame (EPSG:9607)."""
    W, H = 840, 500
    f = []

    f.append(text(W / 2, 28, "Дві геодезичні конвенції: поворот вектора проти повороту осей", size=16, bold=True))

    # Ліва панель: Position Vector (EPSG:9606)
    f.append(rect(20, 55, 385, 360, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    f.append(text(212, 85, "Position Vector / Вектор положення", size=14, color=NEG, bold=True))
    f.append(text(212, 105, "EPSG: 9606 (IERS, ISO 19111, активний поворот)", size=11, color=MUTED))

    # Схема активного повороту вектора
    cx1, cy1 = 150.0, 240.0
    # Нерухомі осі X, Y
    f.append(arrow(cx1, cy1, cx1 + 160, cy1, color=LINE, sw=1.5))
    f.append(text(cx1 + 175, cy1 + 4, "X", size=12, color=INK, bold=True))
    f.append(arrow(cx1, cy1, cx1, cy1 - 110, color=LINE, sw=1.5))
    f.append(text(cx1, cy1 - 120, "Y", size=12, color=INK, bold=True))

    # Початковий вектор V
    v_len = 110.0
    ang0 = math.radians(25)
    f.append(line(cx1, cy1, cx1 + v_len * math.cos(ang0), cy1 - v_len * math.sin(ang0), color=NEG, sw=2.0))
    f.append(circle(cx1 + v_len * math.cos(ang0), cy1 - v_len * math.sin(ang0), 4, fill=NEG, stroke=NEG))
    f.append(text(cx1 + v_len * math.cos(ang0) + 15, cy1 - v_len * math.sin(ang0) + 10, "P (початкова)", size=11, color=NEG))

    # Повернутий вектор V'
    ang1 = math.radians(65)
    f.append(line(cx1, cy1, cx1 + v_len * math.cos(ang1), cy1 - v_len * math.sin(ang1), color=POS, sw=2.0))
    f.append(circle(cx1 + v_len * math.cos(ang1), cy1 - v_len * math.sin(ang1), 4, fill=POS, stroke=POS))
    f.append(text(cx1 + v_len * math.cos(ang1) - 10, cy1 - v_len * math.sin(ang1) - 12, "P' (повернута)", size=11, color=POS, bold=True))

    # Дуга повороту
    f.append(text(cx1 + 65, cy1 - 45, "+θ (проти стрілки)", size=11, color="#b7791f", bold=True))

    # Текст під панеллю 1
    pv_desc = (
        "Осі координат нерухомі.\n"
        "Точка P повертається в системі координат.\n"
        "Матриця для малих кутів:\n"
        "R_pv = I + Ω  [позитивні знаки поворотів]"
    )
    f.append(fitbox(35, 310, 355, 90, pv_desc, size=11, pad=8, fill="#ffffff", stroke=NEG))

    # Права панель: Coordinate Frame (EPSG:9607)
    f.append(rect(435, 55, 385, 360, fill="#f8fafc", stroke=POS, sw=1.5, rx=8))
    f.append(text(627, 85, "Coordinate Frame / Осі координат", size=14, color=POS, bold=True))
    f.append(text(627, 105, "EPSG: 9607 (Bursa-Wolf, пасивний поворот)", size=11, color=MUTED))

    # Схема пасивного повороту осей
    cx2, cy2 = 565.0, 240.0
    # Початкові осі X, Y
    f.append(arrow(cx2, cy2, cx2 + 150, cy2, color=MUTED, sw=1.4))
    f.append(text(cx2 + 160, cy2 + 4, "X", size=11, color=MUTED))
    f.append(arrow(cx2, cy2, cx2, cy2 - 110, color=MUTED, sw=1.4))
    f.append(text(cx2, cy2 - 120, "Y", size=11, color=MUTED))

    # Повернуті осі X', Y'
    ang_rot = math.radians(25)
    f.append(arrow(cx2, cy2, cx2 + 150 * math.cos(ang_rot), cy2 + 150 * math.sin(ang_rot), color=POS, sw=2.0))
    f.append(text(cx2 + 160 * math.cos(ang_rot), cy2 + 150 * math.sin(ang_rot) + 5, "X'", size=12, color=POS, bold=True))
    f.append(arrow(cx2, cy2, cx2 - 110 * math.sin(ang_rot), cy2 - 110 * math.cos(ang_rot), color=POS, sw=2.0))
    f.append(text(cx2 - 110 * math.sin(ang_rot) - 15, cy2 - 110 * math.cos(ang_rot), "Y'", size=12, color=POS, bold=True))

    # Нерухома точка P
    px_static, py_static = cx2 + 85, cy2 - 75
    f.append(circle(px_static, py_static, 5, fill="#27ae60", stroke="#1e8449"))
    f.append(text(px_static + 50, py_static, "Точка P нерухома", size=11, color="#1e8449", bold=True))

    # Текст під панеллю 2
    cf_desc = (
        "Точка в просторі нерухома.\n"
        "Повертається сама рамка (осі координат).\n"
        "Матриця для малих кутів:\n"
        "R_cf = R_pv^T = I - Ω  [знаки кутів ПРОТИЛЕЖНІ]"
    )
    f.append(fitbox(450, 310, 355, 90, cf_desc, size=11, pad=8, fill="#ffffff", stroke=POS))

    # Попереджувальний блок унизу
    warn_text = "Знак кутів (Rx, Ry, Rz) у конвенції Coordinate Frame строго протилежний до Position Vector! Помилка дає зсув ~31 м на 1″ при R ≈ 6371 км."
    f.append(fitbox(20, 425, 800, 55, warn_text, size=12, pad=8, fill="#fff3cd", stroke="#e0a800", color="#856404", bold=True))

    render(os.path.join(IMG, "conventions-pv-vs-cf.svg"), W, H, *f)


def fig_molodensky_badekas_lever():
    """Фігура 3: Проблема важеля геоцентра та розчеплення параметрів у моделі Молоденського-Бадекаса."""
    W, H = 840, 500
    f = []

    f.append(text(W / 2, 28, "Усунення важеля обертання: класичний Гельмерт проти Молоденського — Бадекаса", size=15, bold=True))

    # Лівий блок: Класичний Гельмерт (обертання навколо 0,0,0)
    f.append(rect(20, 55, 385, 425, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(212, 85, "Класичний Гельмерт: центр у геоцентрі", size=13, color=POS, bold=True))

    # Геоцентр (ліворуч вгорі/посередині)
    gc_x, gc_y = 80.0, 240.0
    f.append(circle(gc_x, gc_y, 6, fill=INK, stroke=INK))
    f.append(text(gc_x + 5, gc_y + 22, "Геоцентр (0, 0, 0)", size=11, color=INK, bold=True))

    # Лінія важеля
    net_x, net_y = 310.0, 140.0
    f.append(line(gc_x, gc_y, net_x - 30, net_y, color=MUTED, sw=1.8, dash="5,4"))
    f.append(text((gc_x + net_x) / 2 - 25, (gc_y + net_y) / 2 - 12, "Важіль R ≈ 6371 км", size=11, color=POS, bold=True))

    # Регіональна мережа точок на поверхні
    f.append(circle(net_x - 20, net_y - 10, 4, fill=NEG, stroke=NEG))
    f.append(circle(net_x + 15, net_y + 15, 4, fill=NEG, stroke=NEG))
    f.append(circle(net_x + 25, net_y - 25, 4, fill=NEG, stroke=NEG))
    f.append(rect(net_x - 35, net_y - 35, 70, 60, fill="none", stroke="#27ae60", sw=1.5))
    f.append(text(net_x, net_y - 42, "Мережа точок", size=11, color="#27ae60", bold=True))

    # Зсув мережі від малого повороту
    f.append(arrow(net_x + 25, net_y, net_x + 60, net_y - 20, color=POS, sw=2.0))
    f.append(text(net_x + 5, net_y + 40, "ΔX = R · θ ≈ 30.9 м/1″", size=11, color=POS, bold=True))

    desc_left = (
        "Поворот навколо геоцентра (0,0,0)\n"
        "створює плече довжиною 6371 км.\n\n"
        "Наслідок: екстремальна кореляція\n"
        "між зсувами T та кутами R в МНК."
    )
    f.append(fitbox(35, 305, 355, 155, desc_left, size=12, pad=10, fill="#fdecea", stroke=POS))

    # Правий блок: Молоденський-Бадекас (обертання навколо центроїда)
    f.append(rect(435, 55, 385, 425, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(627, 85, "Молоденський — Бадекас: центр у X₀", size=13, color="#27ae60", bold=True))

    # Центроїд мережі X0
    mb_x, mb_y = 627.0, 160.0
    f.append(circle(mb_x, mb_y, 7, fill="#27ae60", stroke="#1e8449", sw=2))
    f.append(text(mb_x, mb_y - 18, "Центроїд мережі X₀", size=12, color="#1e8449", bold=True))

    # Точки навколо центроїда
    f.append(circle(mb_x - 60, mb_y - 25, 4, fill=NEG, stroke=NEG))
    f.append(circle(mb_x + 55, mb_y - 35, 4, fill=NEG, stroke=NEG))
    f.append(circle(mb_x - 45, mb_y + 40, 4, fill=NEG, stroke=NEG))
    f.append(circle(mb_x + 50, mb_y + 30, 4, fill=NEG, stroke=NEG))

    # Вектори від X0 до точок
    f.append(line(mb_x, mb_y, mb_x - 60, mb_y - 25, color=MUTED, sw=1.2))
    f.append(line(mb_x, mb_y, mb_x + 55, mb_y - 35, color=MUTED, sw=1.2))
    f.append(line(mb_x, mb_y, mb_x - 45, mb_y + 40, color=MUTED, sw=1.2))
    f.append(line(mb_x, mb_y, mb_x + 50, mb_y + 30, color=MUTED, sw=1.2))

    # Плече — лише радіус мережі
    f.append(text(mb_x, mb_y + 70, "Плече r ≤ 100...500 км (лише розмір мережі)", size=11, color="#27ae60", bold=True))

    desc_right = (
        "Центр обертання перенесено в барицентр:\n"
        "X₀ = (1/n) · ∑ X_i\n\n"
        "Формула (10 параметрів: 7 + X₀):\n"
        "P_B = X₀ + T + (1 + s) · R · (P_A - X₀)\n\n"
        "Повне розчеплення T та R у матриці МНК!"
    )
    f.append(fitbox(450, 305, 355, 155, desc_right, size=12, pad=10, fill="#eafaf1", stroke="#27ae60"))

    render(os.path.join(IMG, "molodensky-badekas-lever.svg"), W, H, *f)


def fig_epoch_drift_14param():
    """Фігура 4: 14-параметричне перетворення з урахуванням швидкостей тектонічного руху."""
    W, H = 840, 460
    f = []

    f.append(text(W / 2, 28, "14-параметрична кінематична трансформація з урахуванням швидкостей дрейфу", size=15, bold=True))

    # Схема руху плит
    # Епоха t0
    f.append(rect(40, 65, 230, 260, fill="#f8fafc", stroke=NEG, sw=1.5, rx=6))
    f.append(text(155, 95, "Базова епоха t₀", size=14, color=NEG, bold=True))
    f.append(text(155, 115, "(наприклад, 2010.0)", size=11, color=MUTED))

    f.append(circle(155, 190, 8, fill=NEG, stroke=NEG))
    f.append(text(155, 220, "P(t₀)", size=13, color=NEG, bold=True))
    f.append(text(155, 245, "7 параметрів на епоху t₀:\nTx, Ty, Tz, Rx, Ry, Rz, s", size=11, color=INK))

    # Стрілка еволюції в часі
    f.append(arrow(285, 190, 520, 190, color=POS, sw=3.0))
    tb_time, _, _ = textbox(405, 150, "Часовий зсув: Δt = (t − t₀) років\n+ 7 швидкостей зміни (Ṫ, Ṙ, ṡ)", size=12, color=POS, bold=True, fill="#fff3cd", stroke="#d4b106")
    f.append(tb_time)
    f.append(text(405, 225, "Тектонічний дрейф: ~2–5 см/рік", size=11, color=MUTED))

    # Епоха t
    f.append(rect(535, 65, 265, 260, fill="#f8fafc", stroke=POS, sw=1.5, rx=6))
    f.append(text(667, 95, "Поточна епоха t", size=14, color=POS, bold=True))
    f.append(text(667, 115, "(наприклад, 2026.5)", size=11, color=MUTED))

    f.append(circle(667, 190, 8, fill=POS, stroke=POS))
    f.append(text(667, 220, "P(t) = P(t₀) + V · (t − t₀)", size=13, color=POS, bold=True))
    f.append(text(667, 245, "Миттєві параметри на епоху t:\nTx(t) = Tx(t₀) + Ṫx · (t − t₀)\nRx(t) = Rx(t₀) + Ṙx · (t − t₀)\ns(t)  = s(t₀)  + ṡ  · (t − t₀)", size=10, color=INK))

    # Підсумковий блок
    summary = (
        "Кінематична модель Гельмерта (14 параметрів = 7 базових + 7 похідних за часом):\n"
        "Зв'язує динамічні супутникові системи відліку (ITRF2014, ITRF2020) з фіксованими на тектонічних плитах (ETRF2000, NAD83)."
    )
    f.append(fitbox(40, 345, 760, 85, summary, size=12, pad=10, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, "epoch-drift-14param.svg"), W, H, *f)


if __name__ == "__main__":
    fig_helmert_geometry()
    fig_conventions_pv_vs_cf()
    fig_molodensky_badekas_lever()
    fig_epoch_drift_14param()
    print("Figures successfully generated in img/")
