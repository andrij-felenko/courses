# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми fuse-operation (Принцип роботи запобіжника)."""
import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_thermal_balance():
    """Фігура 1: Тепловий баланс плавкої ланки при різних режимах струму."""
    w, h = 880, 420
    frags = []

    # Заголовок блоків
    frags.append(text(w / 2, 28, "Тепловий баланс плавкої ланки: генерація I²R проти тепловідводу", size=16, bold=True))

    # Три колонки: 1) Штатний режим (I <= Inom), 2) Перевантаження (Inom < I < 3Inom), 3) Коротке замикання (I >> Inom)
    col_w = 260
    col_gap = 30
    x0 = 35

    # ── Колонка 1: Штатний режим ──
    x1 = x0
    frags.append(rect(x1, 55, col_w, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(rect(x1 + 10, 65, col_w - 20, 32, fill="#e2e8f0", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(x1 + col_w / 2, 86, "Штатний режим (I ≤ I_nom)", size=13, bold=True, color="#0f172a"))

    # Схема балансу 1
    frags.append(textbox(x1 + col_w / 2, 130, "Теплогенерація:\nQ_in = I² · R(T) · t", size=12, pad=6, fill="#fef2f2", stroke=POS, sw=1.2)[0])
    frags.append(textbox(x1 + col_w / 2, 195, "Тепловідвід:\nQ_out = k_th · (T - T_amb) · t", size=12, pad=6, fill="#eff6ff", stroke=NEG, sw=1.2)[0])
    
    # Рівновага
    frags.append(textbox(x1 + col_w / 2, 265, "Q_in = Q_out\n(Стаціонарна рівновага)", size=12, bold=True, pad=6, fill="#ecfdf5", stroke=FIELD, sw=1.5)[0])
    frags.append(textbox(x1 + col_w / 2, 345, "Температура стабілізується:\nT_стала << T_плавлення\n(Провідник не пошкоджується)", size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])

    # ── Колонка 2: Помірне перевантаження ──
    x2 = x1 + col_w + col_gap
    frags.append(rect(x2, 55, col_w, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(rect(x2 + 10, 65, col_w - 20, 32, fill="#fef3c7", stroke="#fde68a", sw=1, rx=4))
    frags.append(text(x2 + col_w / 2, 86, "Перевантаження (I_nom < I ≤ 3·I_nom)", size=13, bold=True, color="#92400e"))

    frags.append(textbox(x2 + col_w / 2, 130, "Q_in > Q_out\n(Повільне накопичення тепла)", size=12, pad=6, fill="#fef2f2", stroke=POS, sw=1.2)[0])
    frags.append(textbox(x2 + col_w / 2, 195, "Частина тепла розсіюється\nу виводи та корпус", size=12, pad=6, fill="#eff6ff", stroke=NEG, sw=1.2)[0])
    frags.append(textbox(x2 + col_w / 2, 265, "T(t) повільно зростає\nЧас розриву: секунди...хвилини", size=12, bold=True, pad=6, fill="#fffbeb", stroke="#f59e0b", sw=1.5)[0])
    frags.append(textbox(x2 + col_w / 2, 345, "Діє M-ефект (дифузія олова)\nабо прогрів термобаласту", size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])

    # ── Колонка 3: Коротке замикання ──
    x3 = x2 + col_w + col_gap
    frags.append(rect(x3, 55, col_w, 340, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(rect(x3 + 10, 65, col_w - 20, 32, fill="#fee2e2", stroke="#fca5a5", sw=1, rx=4))
    frags.append(text(x3 + col_w / 2, 86, "Коротке замикання (I >> I_nom)", size=13, bold=True, color="#991b1b"))

    frags.append(textbox(x3 + col_w / 2, 130, "Q_in >>> Q_out\nАдіабатичний процес (Q_out ≈ 0)", size=12, pad=6, fill="#fef2f2", stroke=POS, sw=1.2)[0])
    frags.append(textbox(x3 + col_w / 2, 195, "Тепло не встигає вийти\nв довкілля за мілісекунди", size=12, pad=6, fill="#ffffff", stroke="#94a3b8", sw=1.2)[0])
    frags.append(textbox(x3 + col_w / 2, 265, "Уся енергія йде на плавлення:\nI²t_melt = const(матеріал, S)", size=12, bold=True, pad=6, fill="#fee2e2", stroke=POS, sw=1.5)[0])
    frags.append(textbox(x3 + col_w / 2, 345, "Вибухове випаровування перешийка\nі запалювання електричної дуги", size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])

    out_path = os.path.join(IMG_DIR, "fuse-thermal-balance.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


def fig_arc_phases():
    """Фігура 2: Стадії відключення струму к.з. та гасіння електричної дуги."""
    w, h = 900, 380
    frags = []

    frags.append(text(w / 2, 26, "Стадії спрацьовування термоплавкого запобіжника при короткому замиканні", size=16, bold=True))

    box_w = 200
    box_h = 280
    gap = 20
    x_start = 20

    # 4 стадії
    steps = [
        ("1. Нагрів ланки", "#e2e8f0", "#475569", [
            "Струм к.з. стрімко зростає",
            "Адіабатичний нагрів I²R",
            "Метал твердий",
            "T < T_плавлення",
            "Струм визначається колом"
        ]),
        ("2. Плавлення ланки", "#fef3c7", "#d97706", [
            "Фазовий перехід розплавлення",
            "Розрив рідкого перешийка",
            "Час плавлення: t_melt",
            "Виділена енергія: I²t_melt",
            "Металева пара заповнює зазор"
        ]),
        ("3. Горіння дуги", "#fee2e2", "#dc2626", [
            "Іонізація пари металу",
            "Плазма дуги (5000-15000 K)",
            "Струм далі тече через дугу!",
            "Кварцовий пісок плавиться",
            "Енергія дуги: I²t_arc"
        ]),
        ("4. Гасіння та розрив", "#dcfce7", "#16a34a", [
            "Інтенсивний тепловідвід піску",
            "Утворення фульгуриту (скло)",
            "Деіонізація плазми",
            "Струм падає до нуля",
            "Повний інтеграл: I²t_total"
        ]),
    ]

    for i, (title, fill_c, stroke_c, points) in enumerate(steps):
        bx = x_start + i * (box_w + gap)
        frags.append(rect(bx, 50, box_w, box_h, fill="#ffffff", stroke=stroke_c, sw=2, rx=8))
        frags.append(rect(bx, 50, box_w, 36, fill=fill_c, stroke=stroke_c, sw=1.5, rx=6))
        frags.append(text(bx + box_w / 2, 74, title, size=13, bold=True, color="#0f172a"))

        for j, pt in enumerate(points):
            py = 112 + j * 32
            frags.append(circle(bx + 14, py - 4, 3, fill=stroke_c, stroke=stroke_c))
            frags.append(text(bx + 24, py, pt, size=11, anchor="start", color="#1e293b"))

        # Стрілка переходу між блоками
        if i < 3:
            ax1 = bx + box_w + 3
            ax2 = bx + box_w + gap - 3
            frags.append(arrow(ax1, 180, ax2, 180, color="#64748b", sw=2))

    # Підсумковий пояснювальний банер унизу
    frags.append(rect(x_start, 342, w - 2 * x_start, 28, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    frags.append(text(w / 2, 361, "Повний час відключення: t_total = t_melt + t_arc  │  Повний тепловий інтеграл: I²t_total = I²t_melt + I²t_arc", size=12, bold=True, color="#0f172a"))

    out_path = os.path.join(IMG_DIR, "arc-extinction-phases.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


def fig_time_current_curves():
    """Фігура 3: Часо-струмові характеристики (TCC) різних типів запобіжників."""
    w, h = 880, 480
    frags = []

    frags.append(text(w / 2, 26, "Часо-струмові характеристики (TCC) та координація з напівпровідником", size=16, bold=True))

    # Область графіка: логарифмічні осі
    gx0, gy0 = 90, 60
    gw, gh = 460, 360

    # Тло та сітка
    frags.append(rect(gx0, gy0, gw, gh, fill="#fafafa", stroke="#94a3b8", sw=1.5, rx=4))

    # Горизонтальні лінії сітки (логарифмічний час: 1000s, 100s, 10s, 1s, 0.1s, 0.01s, 0.001s)
    y_labels = [
        (gy0 + 10, "1000 с"),
        (gy0 + 65, "100 с"),
        (gy0 + 120, "10 с"),
        (gy0 + 175, "1 с"),
        (gy0 + 230, "0.1 с"),
        (gy0 + 285, "10 мс"),
        (gy0 + 340, "1 мс"),
    ]
    for y_pos, lbl in y_labels:
        frags.append(line(gx0, y_pos, gx0 + gw, y_pos, color="#e2e8f0", sw=1, dash="4,4"))
        frags.append(text(gx0 - 10, y_pos + 4, lbl, size=10, anchor="end", color="#64748b"))

    # Вертикальні лінії сітки (кратність струму: 1.5x, 2x, 4x, 10x, 20x, 50x)
    x_labels = [
        (gx0 + 40, "1.5·I_nom"),
        (gx0 + 100, "2·I_nom"),
        (gx0 + 190, "4·I_nom"),
        (gx0 + 290, "10·I_nom"),
        (gx0 + 370, "20·I_nom"),
        (gx0 + 435, "50·I_nom"),
    ]
    for x_pos, lbl in x_labels:
        frags.append(line(x_pos, gy0, x_pos, gy0 + gh, color="#e2e8f0", sw=1, dash="4,4"))
        frags.append(text(x_pos, gy0 + gh + 18, lbl, size=10, anchor="middle", color="#64748b"))

    # Підписи осей
    frags.append(text(gx0 - 55, gy0 + gh / 2, "Час відключення (t)", size=12, bold=True, anchor="middle", color="#1e293b"))
    frags.append(text(gx0 + gw / 2, gy0 + gh + 38, "Кратність перевантаження за струмом (I / I_nom)", size=12, bold=True, anchor="middle", color="#1e293b"))

    # Криві:
    # 1. Повільний запобіжник (Slow-Blow / Time-Lag / T) — синя лінія
    t_curve = f"M {gx0+30} {gy0+20} Q {gx0+60} {gy0+120} {gx0+140} {gy0+200} T {gx0+300} {gy0+290} T {gx0+450} {gy0+345}"
    frags.append(f'<path d="{t_curve}" fill="none" stroke="#2563eb" stroke-width="3"/>')

    # 2. Швидкий запобіжник (Fast / F) — зелена лінія
    f_curve = f"M {gx0+25} {gy0+20} Q {gx0+45} {gy0+140} {gx0+100} {gy0+220} T {gx0+220} {gy0+310} T {gx0+400} {gy0+350}"
    frags.append(f'<path d="{f_curve}" fill="none" stroke="#16a34a" stroke-width="3"/>')

    # 3. Надшвидкий запобіжник (Super-Rapid / FF) — помаранчева лінія
    ff_curve = f"M {gx0+20} {gy0+30} Q {gx0+35} {gy0+160} {gx0+75} {gy0+250} T {gx0+160} {gy0+330} T {gx0+320} {gy0+355}"
    frags.append(f'<path d="{ff_curve}" fill="none" stroke="#d97706" stroke-width="3"/>')

    # 4. Гранична крива стійкості напівпровідника (SCR / Diode damage curve) — червоний пунктир
    semi_curve = f"M {gx0+50} {gy0+50} Q {gx0+80} {gy0+190} {gx0+130} {gy0+280} T {gx0+240} {gy0+340} T {gx0+360} {gy0+357}"
    frags.append(f'<path d="{semi_curve}" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-dasharray="6,4"/>')

    # Права панель: Легенда та пояснення
    lx = gx0 + gw + 25
    lw = 275

    frags.append(rect(lx, gy0, lw, gh, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=6))
    frags.append(text(lx + lw / 2, gy0 + 25, "Класифікація та призначення", size=13, bold=True, color="#0f172a"))

    # Елементи легенди
    items = [
        ("#2563eb", "Повільний (T / Time-Lag)", "Витримує пускові імпульси,\nтрансформатори, мотори"),
        ("#16a34a", "Швидкий (F / Fast-Acting)", "Загальний захист ліній, кабелів,\nрезистивних навантажень"),
        ("#d97706", "Надшвидкий (FF / Ultra-Rapid)", "Мінімальний I²t, захист чутливих\nнапівпровідникових ключів"),
        ("#dc2626", "Межа стійкості напівпровідника", "Крива FF лежить лівіше межі:\nзапобіжник встигає врятувати чип"),
    ]

    for idx, (col, title_txt, desc_txt) in enumerate(items):
        iy = gy0 + 55 + idx * 72
        frags.append(line(lx + 15, iy + 6, lx + 45, iy + 6, color=col, sw=3, dash="5,3" if idx == 3 else None))
        frags.append(circle(lx + 30, iy + 6, 4, fill=col, stroke=col))
        frags.append(text(lx + 55, iy + 8, title_txt, size=11, bold=True, anchor="start", color="#0f172a"))
        
        lines_desc = desc_txt.split("\n")
        for di, dln in enumerate(lines_desc):
            frags.append(text(lx + 55, iy + 24 + di * 15, dln, size=10, anchor="start", color="#475569"))

    out_path = os.path.join(IMG_DIR, "time-current-curves.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


def fig_pptc_mechanism():
    """Фігура 4: Будова та фізичний механізм роботи самовідновного запобіжника PPTC."""
    w, h = 880, 440
    frags = []

    frags.append(text(w / 2, 26, "Фізика самовідновного запобіжника (PPTC PolySwitch)", size=16, bold=True))

    col_w = 400
    x_l = 30
    x_r = 450
    box_h = 370
    y0 = 50

    # ── Лівий блок: Холодний провідний стан ──
    frags.append(rect(x_l, y0, col_w, box_h, fill="#f8fafc", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(rect(x_l, y0, col_w, 36, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=6))
    frags.append(text(x_l + col_w / 2, y0 + 24, "Холодний стан (T < T_trip, I ≤ I_hold)", size=13, bold=True, color="#0369a1"))

    # Схематичне зображення кристалічної матриці з ланцюжками вуглецю
    my0 = y0 + 50
    frags.append(rect(x_l + 20, my0, col_w - 40, 140, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=4))

    # Кристалічні зони полімеру
    frags.append(rect(x_l + 35, my0 + 15, 80, 45, fill="#cbd5e1", stroke="#94a3b8", rx=4))
    frags.append(rect(x_l + 160, my0 + 20, 90, 40, fill="#cbd5e1", stroke="#94a3b8", rx=4))
    frags.append(rect(x_l + 285, my0 + 15, 80, 45, fill="#cbd5e1", stroke="#94a3b8", rx=4))
    frags.append(rect(x_l + 90, my0 + 75, 100, 45, fill="#cbd5e1", stroke="#94a3b8", rx=4))
    frags.append(rect(x_l + 225, my0 + 75, 100, 45, fill="#cbd5e1", stroke="#94a3b8", rx=4))

    # Вуглецеві ланцюжки (чорні кульки в неперервних доріжках)
    coords_cold = [
        (45, 68), (65, 68), (90, 68), (115, 68), (140, 68), (165, 68), (195, 68), (225, 68), (255, 68), (285, 68), (315, 68), (345, 68),
        (45, 128), (75, 128), (105, 128), (135, 128), (165, 128), (195, 128), (225, 128), (255, 128), (285, 128), (315, 128), (345, 128),
    ]
    # Лінії провідності
    frags.append(line(x_l + 45, my0 + 68, x_l + 345, my0 + 68, color="#1e293b", sw=3))
    frags.append(line(x_l + 45, my0 + 128, x_l + 345, my0 + 128, color="#1e293b", sw=3))
    for cx_rel, cy_rel in coords_cold:
        frags.append(circle(x_l + cx_rel, my0 + cy_rel, 5, fill="#0f172a", stroke="#0f172a"))

    frags.append(text(x_l + col_w / 2, my0 + 170, "Неперервні провідні ланцюжки вуглецю", size=11, bold=True, color="#0f172a"))

    # Опис холодного стану
    frags.append(textbox(x_l + col_w / 2, y0 + 260, "Кристалічна структура полімеру\nщільна, об'єм мінімальний", size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])
    frags.append(textbox(x_l + col_w / 2, y0 + 325, "Опір дуже малий: R_initial ≈ 0.01...0.5 Ом\nСтрум вільно протікає в навантаження", size=11, bold=True, pad=6, fill="#ecfdf5", stroke=FIELD, sw=1.2)[0])

    # ── Правий блок: Гарячий стан спрацьовування ──
    frags.append(rect(x_r, y0, col_w, box_h, fill="#f8fafc", stroke="#dc2626", sw=1.5, rx=8))
    frags.append(rect(x_r, y0, col_w, 36, fill="#fee2e2", stroke="#dc2626", sw=1.5, rx=6))
    frags.append(text(x_r + col_w / 2, y0 + 24, "Гарячий спрацьований стан (T > T_trip)", size=13, bold=True, color="#991b1b"))

    # Схематичне зображення аморфної матриці зі спаленими ланцюжками
    frags.append(rect(x_r + 20, my0, col_w - 40, 140, fill="#fef2f2", stroke="#fca5a5", sw=1, rx=4))

    # Аморфна фаза (розширений полімер без порядку)
    coords_hot = [
        (45, 55), (75, 45), (110, 60), (145, 40), (180, 58), (215, 42), (250, 62), (285, 45), (320, 58), (345, 48),
        (45, 140), (80, 125), (115, 145), (150, 120), (185, 142), (220, 118), (255, 140), (290, 122), (325, 142), (345, 130),
    ]
    for cx_rel, cy_rel in coords_hot:
        frags.append(circle(x_r + cx_rel, my0 + cy_rel, 5, fill="#0f172a", stroke="#0f172a"))

    frags.append(text(x_r + col_w / 2, my0 + 170, "Ланцюжки розірвані через теплове розширення", size=11, bold=True, color="#991b1b"))

    # Опис гарячого стану
    frags.append(textbox(x_r + col_w / 2, y0 + 260, "Аморфний фазовий стан полімеру,\nоб'єм матриці розширюється", size=11, pad=6, fill="#ffffff", stroke="#cbd5e1", sw=1)[0])
    frags.append(textbox(x_r + col_w / 2, y0 + 325, "Опір зростає на 4-6 порядків:\nR_trip ≈ 10...100 кОм (струм заблоковано)", size=11, bold=True, pad=6, fill="#fef2f2", stroke=POS, sw=1.2)[0])

    out_path = os.path.join(IMG_DIR, "pptc-mechanism.svg")
    render(out_path, w, h, *frags)
    print(f"Згенеровано {out_path}")


if __name__ == "__main__":
    fig_thermal_balance()
    fig_arc_phases()
    fig_time_current_curves()
    fig_pptc_mechanism()
