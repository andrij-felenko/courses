# -*- coding: utf-8 -*-
"""Фігури до теми «Тяги, качалки й люфт рульової поверхні».
Запуск: python figs.py  -> генерує SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# ── 1. Кінематика важільного механізму ───────────────────────────────────────
def fig_linkage_geometry():
    W, H = 760, 420
    f = [text(W / 2, 28, "Кінематика тяги: співвідношення плечей і передача моменту", size=16, bold=True)]

    # Координати осей
    xs, ys = 140, 230    # вісь сервоприводу O_s
    xh, yh = 590, 230    # вісь обертання руля (шарнір) O_h

    # Довжини плечей
    rs = 70              # r_servo
    rh = 110             # r_horn

    # Кути в нейтралі (вертикально вгору)
    p_s_x, p_s_y = xs, ys - rs
    p_h_x, p_h_y = xh, yh - rh

    # Вісь сервоприводу й рульової площини (базові опори)
    f.append(rect(xs - 45, ys - 35, 90, 90, fill="#edf2f7", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(xs, ys + 42, "Сервопривід", size=12, bold=True, color=INK))
    f.append(circle(xs, ys, 9, fill="#cbd5e1", stroke=INK, sw=2))
    f.append(circle(xs, ys, 3, fill=INK, stroke=INK, sw=1))

    # Рульова поверхня (стабілізатор + руль)
    # Нерухома основа крила/кіля
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#e2e8f0" stroke="%s" stroke-width="1.5"/>'
             % (xh - 90, yh - 25, xh, yh - 10, xh - 90, yh + 45, MUTED))
    f.append(text(xh - 55, yh + 35, "Крило / кіль", size=11, color=MUTED))

    # Рухомий руль
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="#fee2e2" stroke="%s" stroke-width="1.8"/>'
             % (xh, yh - 10, xh + 130, yh - 5, xh, yh + 20, POS))
    f.append(circle(xh, yh, 9, fill="#fca5a5", stroke=POS, sw=2))
    f.append(circle(xh, yh, 3, fill=POS, stroke=POS, sw=1))
    f.append(text(xh + 65, yh + 42, "Рульова поверхня", size=12, bold=True, color=POS))

    # Качалка сервоприводу (r_servo)
    f.append(line(xs, ys, p_s_x, p_s_y, color=NEG, sw=4.5))
    f.append(circle(p_s_x, p_s_y, 5.5, fill=BG, stroke=NEG, sw=2))

    # Кабанчик руля (r_horn)
    f.append(line(xh, yh, p_h_x, p_h_y, color=POS, sw=4.5))
    f.append(circle(p_h_x, p_h_y, 5.5, fill=BG, stroke=POS, sw=2))

    # Тяга (pushrod)
    f.append(line(p_s_x, p_s_y, p_h_x, p_h_y, color=INK, sw=3))
    f.append(text((p_s_x + p_h_x) / 2, p_s_y - 14, "Жорстка тяга (Pushrod) L", size=12.5, bold=True, color=INK))

    # Позначення плечей r_servo та r_horn
    f.append(line(xs - 25, ys, xs - 25, p_s_y, color=NEG, sw=1.3))
    f.append(line(xs - 30, ys, xs - 20, ys, color=NEG, sw=1.3))
    f.append(line(xs - 30, p_s_y, xs - 20, p_s_y, color=NEG, sw=1.3))
    f.append(text(xs - 40, (ys + p_s_y) / 2 + 4, "r_servo", size=12, bold=True, color=NEG, anchor="end"))

    f.append(line(xh + 25, yh, xh + 25, p_h_y, color=POS, sw=1.3))
    f.append(line(xh + 20, yh, xh + 30, yh, color=POS, sw=1.3))
    f.append(line(xh + 20, p_h_y, xh + 30, p_h_y, color=POS, sw=1.3))
    f.append(text(xh + 40, (yh + p_h_y) / 2 + 4, "r_horn", size=12, bold=True, color=POS, anchor="start"))

    # Пунктир відхилення сервоприводу і руля
    ang_s = math.radians(35)
    dx_s = rs * math.sin(ang_s)
    dy_s = rs * (1 - math.cos(ang_s))
    p_s_def_x, p_s_def_y = xs + dx_s, p_s_y + dy_s
    f.append(line(xs, ys, p_s_def_x, p_s_def_y, color=NEG, sw=2, dash="4,3"))
    f.append(circle(p_s_def_x, p_s_def_y, 4, fill=NEG, stroke=NEG, sw=1))

    # Кутове переміщення серво
    f.append('<path d="M %d,%d A %d %d 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="2,2"/>'
             % (xs, ys - 45, 45, 45, xs + 45 * math.sin(ang_s), ys - 45 * math.cos(ang_s), NEG))
    f.append(text(xs + 26, ys - 50, "θ_servo", size=11.5, color=NEG))

    # Кутове переміщення руля
    ang_h = math.asin(dx_s / rh)
    p_h_def_x, p_h_def_y = xh + dx_s, yh - rh * math.cos(ang_h)
    f.append(line(xh, yh, p_h_def_x, p_h_def_y, color=POS, sw=2, dash="4,3"))
    f.append(circle(p_h_def_x, p_h_def_y, 4, fill=POS, stroke=POS, sw=1))
    f.append('<path d="M %d,%d A %d %d 0 0 1 %d,%d" fill="none" stroke="%s" stroke-width="1.6" stroke-dasharray="2,2"/>'
             % (xh, yh - 65, 65, 65, xh + 65 * math.sin(ang_h), yh - 65 * math.cos(ang_h), POS))
    f.append(text(xh + 36, yh - 72, "δ_surf", size=11.5, color=POS))

    # Відхилена тяга
    f.append(line(p_s_def_x, p_s_def_y, p_h_def_x, p_h_def_y, color=MUTED, sw=1.8, dash="4,3"))

    # Блок формули внизу
    tb, _, _ = textbox(W / 2, 375,
                       "Передавальне відношення i = r_servo / r_horn = δ_surf / θ_servo | Момент M_surf = M_servo · (r_horn / r_servo) · η",
                       size=12.5, bold=True, fill="#f8fafc", stroke=INK)
    f.append(tb)

    render(os.path.join(IMG, "linkage-geometry.svg"), W, H, *f)

# ── 2. Диференційне відхилення елеронів ──────────────────────────────────────
def fig_differential_linkage():
    W, H = 760, 390
    f = [text(W / 2, 26, "Симетричний хід проти елеронного диференціалу", size=16, bold=True)]

    # Ліва панель: симетричний хід (качалка 90° в нейтралі)
    w_box = 340
    f.append(rect(25, 55, w_box, 305, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(25 + w_box / 2, 82, "Симетрична кінематика (90° до тяги)", size=13.5, bold=True, color=INK))

    cx1, cy1 = 195, 175
    r = 55
    # Качалка нейтраль (вертикально)
    f.append(circle(cx1, cy1, 7, fill="#cbd5e1", stroke=INK, sw=1.5))
    f.append(line(cx1, cy1, cx1, cy1 - r, color=INK, sw=3.5))
    f.append(circle(cx1, cy1 - r, 4.5, fill=BG, stroke=INK, sw=1.5))

    # Хід ліворуч і праворуч на однаковий кут 40°
    a40 = math.radians(40)
    xl, yl = cx1 - r * math.sin(a40), cy1 - r * math.cos(a40)
    xr, yr = cx1 + r * math.sin(a40), cy1 - r * math.cos(a40)
    f.append(line(cx1, cy1, xl, yl, color=NEG, sw=2, dash="3,3"))
    f.append(line(cx1, cy1, xr, yr, color=POS, sw=2, dash="3,3"))

    dx_l = cx1 - xl
    dx_r = xr - cx1
    f.append(text(cx1, 255, "Лінійний хід тяги: Δx_вгору = Δx_вниз", size=12, bold=True, color=FIELD))
    f.append(text(cx1, 276, "Кут елерона вгору (+15°) = Кут вниз (-15°)", size=11, color=MUTED))
    f.append(text(cx1, 300, "Створює несприятливе рискання (Adverse Yaw)", size=11, color=POS))
    f.append(text(cx1, 320, "через різницю індуктивного опору крил", size=10.5, color=MUTED))

    # Права панель: диференціал (качалка нахилена на кут гамма)
    x0_r = 395
    f.append(rect(x0_r, 55, w_box, 305, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(x0_r + w_box / 2, 82, "Механічний диференціал (зсув нуля γ)", size=13.5, bold=True, color=INK))

    cx2, cy2 = x0_r + w_box / 2, 175
    # Качалка нейтраль зміщена вперед на 30°
    g = math.radians(30)
    xn, yn = cx2 + r * math.sin(g), cy2 - r * math.cos(g)
    f.append(circle(cx2, cy2, 7, fill="#cbd5e1", stroke=INK, sw=1.5))
    f.append(line(cx2, cy2, xn, yn, color=INK, sw=3.5))
    f.append(circle(xn, yn, 4.5, fill=BG, stroke=INK, sw=1.5))

    # Хід у бік тяги (вгору) +40° -> сумарний кут 70° від вертикалі
    x_up, y_up = cx2 + r * math.sin(g + a40), cy2 - r * math.cos(g + a40)
    # Хід у бік штовхання (вниз) -40° -> кут -10° від вертикалі
    x_dn, y_dn = cx2 + r * math.sin(g - a40), cy2 - r * math.cos(g - a40)

    f.append(line(cx2, cy2, x_up, y_up, color=POS, sw=2.5, dash="3,3"))
    f.append(line(cx2, cy2, x_dn, y_dn, color=NEG, sw=2, dash="3,3"))

    f.append(text(cx2, 255, "Лінійний хід: Δx_вгору >> Δx_вниз", size=12, bold=True, color=POS))
    f.append(text(cx2, 276, "Кут елерона вгору (+20°) > Кут вниз (-10°)", size=11, color=MUTED))
    f.append(text(cx2, 300, "Компенсує рискання: опір опущеного", size=11, color=FIELD))
    f.append(text(cx2, 320, "елерона зменшено, літак входить у віраж чисто", size=10.5, color=MUTED))

    render(os.path.join(IMG, "differential-linkage.svg"), W, H, *f)

# ── 3. Жорсткість тяг та поздовжній вигин Ейлера ─────────────────────────────
def fig_euler_buckling():
    W, H = 760, 420
    f = [text(W / 2, 26, "Робота тяги на розтяг і стиск: критична сила вигину Ейлера", size=16, bold=True)]

    # Ліва частина: Розтяг (Tension)
    f.append(rect(25, 55, 340, 160, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(195, 80, "Розтяг тяги (Tension) — ідеальна стабільність", size=12.5, bold=True, color=FIELD))
    f.append(circle(65, 130, 6, fill=BG, stroke=INK, sw=2))
    f.append(circle(325, 130, 6, fill=BG, stroke=INK, sw=2))
    f.append(line(71, 130, 319, 130, color=FIELD, sw=4))
    f.append(arrow(65, 130, 40, 130, color=FIELD, sw=2.5))
    f.append(arrow(325, 130, 350, 130, color=FIELD, sw=2.5))
    f.append(text(195, 160, "Тяга самоцентрується під силою F", size=11.5, color=INK))
    f.append(text(195, 182, "Межа міцності визначається площею перерізу σ = F / S", size=10.5, color=MUTED))

    # Права частина: Стиск без підтримки (Buckling)
    f.append(rect(395, 55, 340, 160, fill="#fef2f2", stroke=POS, sw=1.4, rx=6))
    f.append(text(565, 80, "Стиск (Compression) — втрата стійкості", size=12.5, bold=True, color=POS))
    f.append(circle(435, 130, 6, fill=BG, stroke=INK, sw=2))
    f.append(circle(695, 130, 6, fill=BG, stroke=INK, sw=2))
    f.append(arrow(410, 130, 435, 130, color=POS, sw=2.5))
    f.append(arrow(720, 130, 695, 130, color=POS, sw=2.5))

    # Вигнута тяга (параболічна дуга)
    f.append('<path d="M 441,130 Q 565,92 689,130" fill="none" stroke="%s" stroke-width="4"/>' % POS)
    f.append(line(565, 130, 565, 111, color=POS, sw=1.3, dash="2,2"))
    f.append(text(575, 122, "f_прогин", size=10.5, color=POS, anchor="start"))
    f.append(text(565, 160, "Критична сила Ейлера: P_cr = π²·E·I / L²", size=11.5, bold=True, color=POS))
    f.append(text(565, 182, "Тонка довга тяга втрачає хід керма при штовханні", size=10.5, color=MUTED))

    # Нижня частина: порівняння трьох конструкцій
    f.append(rect(25, 230, 710, 170, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(W / 2, 254, "Конструктивні рішення для високої поздовжньої жорсткості", size=13, bold=True, color=INK))

    # Варіант 1: Сталевий дріт
    f.append(text(140, 280, "1. Суцільний сталевий дріт", size=11.5, bold=True, color=INK))
    f.append(text(140, 300, "d = 1.2–1.5 мм", size=11, color=MUTED))
    f.append(text(140, 320, "I = π·d⁴ / 64", size=11, color=NEG))
    f.append(text(140, 342, "Гнеться на довжині >150 мм", size=10.5, color=POS))
    f.append(text(140, 362, "Тільки для мікромоделей", size=10.5, color=MUTED))

    # Варіант 2: Карбонова трубка
    f.append(text(380, 280, "2. Карбонова трубка (CFRP)", size=11.5, bold=True, color=FIELD))
    f.append(text(380, 300, "D = 4 мм, d = 2.5 мм", size=11, color=MUTED))
    f.append(text(380, 320, "I = π·(D⁴ − d⁴) / 64", size=11, color=FIELD))
    f.append(text(380, 342, "Момент інерції I в 40+ разів вищий", size=10.5, color=FIELD))
    f.append(text(380, 362, "Мінімальна маса, нульовий прогин", size=10.5, color=MUTED))

    # Варіант 3: Боуден з проміжними опорами
    f.append(text(620, 280, "3. Боуден з напрямними", size=11.5, bold=True, color=INK))
    f.append(text(620, 300, "Сталь у фторопластовій трубці", size=11, color=MUTED))
    f.append(text(620, 320, "Опори кожні 100 мм -> L_eff = L/N", size=11, color=NEG))
    f.append(text(620, 342, "P_cr зростає пропорційно N²", size=10.5, color=FIELD))
    f.append(text(620, 362, "Дозволяє вигин траси в фюзеляжі", size=10.5, color=MUTED))

    f.append(line(260, 268, 260, 385, color="#e2e8f0", sw=1.2, dash="3,3"))
    f.append(line(500, 268, 500, 385, color="#e2e8f0", sw=1.2, dash="3,3"))

    render(os.path.join(IMG, "euler-buckling.svg"), W, H, *f)

# ── 4. Вузли з'єднання, люфт і виникнення флаттеру ───────────────────────────
def fig_clevis_ball_link_flutter():
    W, H = 760, 420
    f = [text(W / 2, 26, "Наконечники тяг, механічний люфт і петля аеродинамічного флаттеру", size=16, bold=True)]

    # Ліва частина: Порівняння трьох наконечників
    w_left = 340
    f.append(rect(25, 55, w_left, 345, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(25 + w_left / 2, 80, "Типи наконечників тяг і люфт", size=13.5, bold=True, color=INK))

    # 4а. Z-згин
    f.append(text(45, 110, "Z-згин дроту (Z-bend):", size=12, bold=True, color=POS))
    f.append(line(45, 135, 100, 135, color=INK, sw=3))
    f.append(line(100, 135, 100, 155, color=INK, sw=3))
    f.append(line(100, 155, 135, 155, color=INK, sw=3))
    f.append(circle(100, 145, 7, fill="#fee2e2", stroke=POS, sw=1.5))
    f.append(text(150, 135, "Зазор отвору розбивається", size=11, color=POS))
    f.append(text(150, 152, "Люфт: ±0.3–0.8 мм", size=10.5, color=MUTED))

    # 4б. Клевіс (вилка)
    f.append(text(45, 190, "Вилка / Клевіс (Clevis):", size=12, bold=True, color=NEG))
    f.append(rect(45, 210, 60, 22, fill="#e0f2fe", stroke=NEG, sw=1.5, rx=3))
    f.append(circle(90, 221, 4, fill=BG, stroke=NEG, sw=1.5))
    f.append(line(105, 221, 140, 221, color=INK, sw=3))
    f.append(text(150, 215, "Штифт у кабанчику", size=11, color=INK))
    f.append(text(150, 232, "Люфт: ±0.1–0.25 мм", size=10.5, color=MUTED))

    # 4в. Кульовий наконечник (Ball Link)
    f.append(text(45, 270, "Кульовий наконечник (Ball Link):", size=12, bold=True, color=FIELD))
    f.append(circle(75, 305, 10, fill="#dcfce7", stroke=FIELD, sw=2))
    f.append(circle(75, 305, 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(rect(83, 298, 45, 14, fill="#edf2f7", stroke=INK, sw=1.5, rx=2))
    f.append(line(128, 305, 155, 305, color=INK, sw=3))
    f.append(text(165, 300, "Сферичне охоплення без зазору", size=11, color=FIELD))
    f.append(text(165, 318, "Люфт: <0.03 мм (нульовий)", size=10.5, bold=True, color=FIELD))

    f.append(text(25 + w_left / 2, 375, "Для швидкостей >100 км/год — виключно Ball Link", size=11, bold=True, color=INK))

    # Права частина: Механізм автоколивань флаттеру
    w_right = 350
    x_r = 385
    f.append(rect(x_r, 55, w_right, 345, fill="#fef2f2", stroke=POS, sw=1.4, rx=6))
    f.append(text(x_r + w_right / 2, 80, "Петля самозбудження флаттеру", size=13.5, bold=True, color=POS))

    # Кроки циклу флаттеру
    b1, _, _ = textbox(x_r + w_right / 2, 120, "1. Люфт у тязі / редукторі\nРуль вільно плаває в межах мертвої зони ±Δδ",
                       size=11, fill=BG, stroke=POS)
    b2, _, _ = textbox(x_r + w_right / 2, 185, "2. Аеродинамічний момент\nПотік повітря відхиляє руль до упору зазору",
                       size=11, fill=BG, stroke=POS)
    b3, _, _ = textbox(x_r + w_right / 2, 250, "3. Пружний удар і відскок\nТяга натягується, пружність крила кидає руль назад",
                       size=11, fill=BG, stroke=POS)
    b4, _, _ = textbox(x_r + w_right / 2, 315, "4. Зсув фази між силою і рухом\nЕнергія потоку накачує амплітуду (Резонанс)",
                       size=11, fill=BG, stroke=POS)

    f.append(b1)
    f.append(b2)
    f.append(b3)
    f.append(b4)

    f.append(arrow(x_r + w_right / 2, 142, x_r + w_right / 2, 162, color=POS, sw=2))
    f.append(arrow(x_r + w_right / 2, 207, x_r + w_right / 2, 227, color=POS, sw=2))
    f.append(arrow(x_r + w_right / 2, 272, x_r + w_right / 2, 292, color=POS, sw=2))
    f.append('<path d="M %d,%d C %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (x_r + w_right - 20, 325, x_r + w_right + 15, 220, x_r + w_right + 15, 140, x_r + w_right - 20, 120, POS))

    f.append(text(x_r + w_right / 2, 375, "Результат: руйнування керма за 0.2–0.5 с", size=11.5, bold=True, color=POS))

    render(os.path.join(IMG, "clevis-ball-link-flutter.svg"), W, H, *f)

if __name__ == "__main__":
    fig_linkage_geometry()
    fig_differential_linkage()
    fig_euler_buckling()
    fig_clevis_ball_link_flutter()
    print("OK: 4 figures generated in", IMG)
