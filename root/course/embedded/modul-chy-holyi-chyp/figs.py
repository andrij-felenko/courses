# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. module-anatomy: Анатомія сертифікованого SMD-радіомодуля ──────────────
def fig_module_anatomy():
    W, H = 940, 520
    p = []

    # Заголовок та підкладка
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 40, "Анатомія сертифікованого радіомодуля: що приховано під екраном", size=16, color=INK, bold=True))

    # Корпус модуля (PCB модуля)
    mx, my, mw, mh = 60, 75, 460, 410
    p.append(rect(mx, my, mw, mh, fill="#1b4332", stroke="#081c15", sw=2, rx=6))
    p.append(text(mx + mw / 2, my + 25, "Друкована плата модуля (4 шари FR4, високочастотний ламінат)", size=12, color="#d8f3dc", bold=True))

    # Зубчасті контактні майданчики (Castellated pads) по периметру (всередині контуру плати)
    pad_h = 16
    pad_w = 12
    # ліві та праві контакти
    for i in range(12):
        py = my + 45 + i * 28
        p.append(rect(mx + 2, py, pad_w, pad_h, fill="#d4af37", stroke="#8c731e", sw=1, rx=2))
        p.append(rect(mx + mw - pad_w - 2, py, pad_w, pad_h, fill="#d4af37", stroke="#8c731e", sw=1, rx=2))
    # нижні контакти
    for j in range(10):
        px = mx + 60 + j * 36
        p.append(rect(px, my + mh - pad_w - 2, pad_h, pad_w, fill="#d4af37", stroke="#8c731e", sw=1, rx=2))

    # Зона антени (верхня частина плати)
    ax, ay, aw, ah = mx + 20, my + 40, mw - 40, 70
    p.append(rect(ax, ay, aw, ah, fill="#2d6a4f", stroke="#52b788", sw=1.5, rx=4))
    # Зигзагоподібна PCB антена (MIFA)
    antenna_pts = [
        (ax + 30, ay + 50), (ax + 30, ay + 20), (ax + 90, ay + 20),
        (ax + 90, ay + 45), (ax + 130, ay + 45), (ax + 130, ay + 20),
        (ax + 170, ay + 20), (ax + 170, ay + 45), (ax + 210, ay + 45),
        (ax + 210, ay + 20), (ax + 380, ay + 20)
    ]
    pts_str = " ".join(f"{x},{y}" for x, y in antenna_pts)
    p.append(f'<polyline points="{pts_str}" fill="none" stroke="#d4af37" stroke-width="3.5" stroke-linecap="round"/>')
    p.append(text(ax + aw / 2, ay + 62, "Погоджена друкована антена (MIFA 2.4 ГГц, 50 Ом)", size=11, color="#d8f3dc"))

    # Металевий екран (Shielding Can) - напівпрозорий контур
    sx, sy, sw_can, sh = mx + 20, my + 120, mw - 40, 255
    p.append(rect(sx, sy, sw_can, sh, fill="#edf2f7", stroke="#718096", sw=2, rx=4))
    p.append(text(sx + sw_can / 2, sy + 22, "Металевий екран (Shield Can — клітка Фарадея для FCC/CE)", size=11.5, color="#2d3748", bold=True))

    # Головний SoC (SoC QFN)
    cx, cy, cw, ch = sx + 30, sy + 45, 140, 140
    p.append(rect(cx, cy, cw, ch, fill="#1a202c", stroke="#4a5568", sw=1.5, rx=3))
    p.append(text(cx + cw / 2, cy + 50, "Головний SoC", size=13, color="#ffffff", bold=True))
    p.append(text(cx + cw / 2, cy + 72, "MCU + Wi-Fi/BLE", size=11, color="#a0aec0"))
    p.append(text(cx + cw / 2, cy + 92, "(Кремній без екрану)", size=9.5, color="#718096"))

    # QSPI Flash / PSRAM
    fx, fy, fw, fh = sx + 220, sy + 45, 120, 70
    p.append(rect(fx, fy, fw, fh, fill="#2d3748", stroke="#4a5568", sw=1.5, rx=3))
    p.append(text(fx + fw / 2, fy + 32, "Flash / PSRAM", size=12, color="#ffffff", bold=True))
    p.append(text(fx + fw / 2, fy + 52, "4-16 МБ QSPI/Octal", size=10, color="#cbd5e0"))

    # Кварцові резонатори
    # HFXO
    p.append(rect(sx + 30, sy + 200, 75, 40, fill="#e2e8f0", stroke="#a0aec0", sw=1.2, rx=2))
    p.append(text(sx + 67, sy + 224, "40 МГц Кварц", size=10, color=INK, bold=True))
    # LFXO
    p.append(rect(sx + 120, sy + 200, 75, 40, fill="#e2e8f0", stroke="#a0aec0", sw=1.2, rx=2))
    p.append(text(sx + 157, sy + 224, "32.768 кГц RTC", size=9.5, color=INK, bold=True))

    # RF-тракт (Балун, Pi-фільтр)
    rx_rf, ry_rf = sx + 220, sy + 135
    p.append(rect(rx_rf, ry_rf, 160, 50, fill="#fffaf0", stroke="#dd6b20", sw=1.5, rx=3))
    p.append(text(rx_rf + 80, ry_rf + 22, "RF-балун + Pi-фільтр", size=11, color="#9c4221", bold=True))
    p.append(text(rx_rf + 80, ry_rf + 40, "LC узгодження імпедансу", size=9.5, color="#c05621"))

    # Декаплінг конденсатори (0201 розсип)
    for k in range(5):
        dcx = sx + 220 + k * 30
        p.append(rect(dcx, sy + 200, 20, 26, fill="#b7791f", stroke="#744210", sw=1, rx=1))
        p.append(text(dcx + 10, sy + 242, "C_dec", size=9.5, color=MUTED))

    # Права панель пояснень: Що отримує розробник
    px0 = 550
    p.append(rect(px0, 75, 360, 410, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(px0 + 180, 105, "Переваги інтегрованого модуля", size=14, color=INK, bold=True))

    items = [
        ("Повністю протестований RF-тракт:", "узгодження 50 Ом, відсутність КСХ-хвиль, фільтрація 2-ї/3-ї гармонік.", POS),
        ("Сертифікати FCC / CE / RED / MIC:", "вбудований FCC ID усуває потребу дорогої сертифікації випромінювача ($15k–$50k).", FIELD),
        ("Прецизійні кварцові резонатори:", "підібрані ємності навантаження C_L, відсутність дрейфу частоти від температури.", NEG),
        ("Цілісність шин живлення та пам'яти:", "декаплінг прямо під кристалом, трасування Octal SPI без паразитних відбиттів.", INK),
        ("Готовий модуль як чорна скринька:", "живлення 3.3 В + лінії UART/GPIO — базова плата розробника лишається простою 2-шаровою.", MUTED)
    ]

    cur_y = 135
    for title, desc, col in items:
        p.append(circle(px0 + 20, cur_y + 6, 5, fill=col, stroke=col))
        p.append(text(px0 + 35, cur_y + 10, title, size=11.5, color=INK, bold=True, anchor="start"))
        words = desc.split(" ")
        l1, l2 = "", ""
        for w in words:
            if len(l1 + " " + w) < 44:
                l1 += (" " if l1 else "") + w
            else:
                l2 += (" " if l2 else "") + w
        lines = [l1, l2] if l2 else [l1]
        p.append(mtext(px0 + 35, cur_y + 28, lines, size=10, color="#475569", anchor="start", lh=1.25))
        cur_y += 54

    render(os.path.join(OUT, "module-anatomy.svg"), W, H, *p,
           title="Анатомія сертифікованого радіомодуля")


# ── 2. crossover-curve: Економічна точка перегину (Crossover Volume) ───────────
def fig_crossover_curve():
    W, H = 940, 480
    p = []

    # Підкладка
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 40, "Аналіз точки беззбитковості (Crossover Volume Analysis)", size=16, color=INK, bold=True))

    x0, y0 = 100, 390
    xw, yh = 780, 300

    # Осі координат
    p.append(line(x0, y0, x0 + xw, y0, color=INK, sw=2))
    p.append(line(x0, y0, x0, y0 - yh, color=INK, sw=2))

    p.append(text(x0 + xw - 10, y0 + 35, "Серійний тираж (N одиниць) →", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(x0 - 15, y0 - yh + 10, "Сукупні витрати TCO ($) →", size=12, color=INK, bold=True, anchor="end"))

    # Позначки на осі X (тиражі)
    ticks_x = [(0, "0"), (200, "5,000"), (390, "10,000"), (580, "15,000"), (760, "20,000")]
    for tx, lab in ticks_x:
        px = x0 + tx
        p.append(line(px, y0, px, y0 + 6, color=INK, sw=1.5))
        p.append(text(px, y0 + 20, lab, size=10.5, color=MUTED))
        if tx > 0:
            p.append(line(px, y0, px, y0 - yh, color="#f1f5f9", sw=1, dash="4,4"))

    # Позначки на осі Y
    ticks_y = [(0, "$0"), (80, "$50k"), (160, "$100k"), (240, "$150k"), (300, "$200k")]
    for ty, lab in ticks_y:
        py = y0 - ty
        p.append(line(x0 - 6, py, x0, py, color=INK, sw=1.5))
        p.append(text(x0 - 12, py + 4, lab, size=10.5, color=MUTED, anchor="end"))
        if ty > 0:
            p.append(line(x0, py, x0 + xw, py, color="#f1f5f9", sw=1, dash="4,4"))

    p_mod_start = (x0, y0 - 20)
    p_mod_cross = (x0 + 390, y0 - 130)
    p_mod_end   = (x0 + 760, y0 - 240)

    p_chip_start = (x0, y0 - 90)
    p_chip_cross = (x0 + 390, y0 - 130)
    p_chip_end   = (x0 + 760, y0 - 170)

    # Заливка зон вигідності
    p.append(f'<polygon points="{x0},{y0} {x0},{y0-20} {x0+390},{y0-130} {x0+390},{y0}" fill="#e8f5e9" opacity="0.6"/>')
    p.append(f'<polygon points="{x0+390},{y0} {x0+390},{y0-130} {x0+760},{y0-170} {x0+760},{y0}" fill="#e3f2fd" opacity="0.6"/>')

    # Лінії графіків
    p.append(f'<line x1="{p_mod_start[0]}" y1="{p_mod_start[1]}" x2="{p_mod_end[0]}" y2="{p_mod_end[1]}" stroke="{POS}" stroke-width="3"/>')
    p.append(f'<line x1="{p_chip_start[0]}" y1="{p_chip_start[1]}" x2="{p_chip_end[0]}" y2="{p_chip_end[1]}" stroke="{NEG}" stroke-width="3"/>')

    # Лінія точки перетину (Crossover)
    p.append(line(x0 + 390, y0, x0 + 390, y0 - 130, color="#475569", sw=2, dash="5,5"))
    p.append(circle(x0 + 390, y0 - 130, 6, fill="#ffffff", stroke="#0f172a", sw=2.5))

    # Підписи ліній та зон
    p.append(text(x0 + 170, y0 - 60, "Вигідніше ГОТОВИЙ МОДУЛЬ", size=11, color="#1b5e20", bold=True))
    p.append(text(x0 + 170, y0 - 45, "(низький стартовий NRE-поріг)", size=9.5, color="#2e7d32"))

    p.append(text(x0 + 580, y0 - 60, "Вигідніше ГОЛИЙ ЧИП (Chip-down)", size=11, color="#0d47a1", bold=True))
    p.append(text(x0 + 580, y0 - 45, "(нижча собівартість одиниці BOM)", size=9.5, color="#1565c0"))

    # Маркери NRE
    p.append(text(x0 + 8, y0 - 28, "NRE модуля ($10k)", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(x0 + 8, y0 - 98, "NRE чипа ($60k: PCB + FCC)", size=9.5, color=NEG, anchor="start", bold=True))

    # Виносний блок точки перегину
    callout_x, callout_y = x0 + 390, y0 - 200
    p.append(rect(callout_x - 110, callout_y - 25, 220, 50, fill="#ffffff", stroke="#0f172a", sw=1.5, rx=4))
    p.append(text(callout_x, callout_y - 5, "Точка перегину (Crossover)", size=11, color=INK, bold=True))
    p.append(text(callout_x, callout_y + 12, "N_cross = 10,000 одиниць", size=11, color=FIELD, bold=True))
    p.append(line(callout_x, callout_y + 25, callout_x, y0 - 138, color="#0f172a", sw=1.5))

    # Легенда
    p.append(line(x0 + 520, p_mod_end[1] - 40, x0 + 550, p_mod_end[1] - 40, color=POS, sw=3))
    p.append(text(x0 + 560, p_mod_end[1] - 36, "Стратегія Готового Модуля (швидкий TTM, дорогий BOM)", size=10.5, color=INK, anchor="start"))

    p.append(line(x0 + 520, p_mod_end[1] - 20, x0 + 550, p_mod_end[1] - 20, color=NEG, sw=3))
    p.append(text(x0 + 560, p_mod_end[1] - 16, "Стратегія Голого Чипа (довгий R&D, дешевий BOM)", size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "crossover-curve.svg"), W, H, *p,
           title="Економічна точка беззбитковості: модуль проти голого чипа")


# ── 3. lifecycle-migration: 4 фази життєвого циклу розробки ────────────────────
def fig_lifecycle_migration():
    W, H = 940, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 40, "Еволюція продукту: 4-етапна міграція від макетки до Chip-down", size=16, color=INK, bold=True))

    phases = [
        ("1. Прототип (PoC)", "1 – 10 шт.", "DIP / Breakout плати\n(Adafruit, SparkFun)", "Швидка перевірка ідеї на столі, з'єднання dupont-проводами.", "#fef3c7", "#d97706"),
        ("2. Пілот (MVP)", "100 – 1,000 шт.", "Сертифікований SMD модуль\n(ESP32-WROOM, Quectel)", "Швидкий TTM, модульний FCC ID, 2-шарова базова плата.", "#dcfce7", "#16a34a"),
        ("3. Серія (Scale-up)", "1k – 10k шт.", "SoM / Оптимізований модуль\n(виробничий стенд)", "Стабілізація прошивки, аналіз DFM/DFT, підготовка до chip-down.", "#e0e7ff", "#4f46e5"),
        ("4. Масове вир-во", "> 10,000+ шт.", "Повний Chip-down дизайн\n(голі QFN/BGA мікросхеми)", "Мінімальний BOM, власна FCC сертифікація, 4-6 шарові плати.", "#fce7f3", "#db2777")
    ]

    bw, bh = 205, 270
    start_x = 35
    start_y = 80

    for i, (title, vol, comp, desc, fill_bg, border_col) in enumerate(phases):
        bx = start_x + i * 225
        p.append(rect(bx, start_y, bw, bh, fill=fill_bg, stroke=border_col, sw=2, rx=6))

        # Заголовок фази
        p.append(rect(bx + 5, start_y + 8, bw - 10, 32, fill=border_col, stroke=border_col, sw=1, rx=4))
        p.append(text(bx + bw / 2, start_y + 30, title, size=12, color="#ffffff", bold=True))

        # Тираж
        p.append(text(bx + bw / 2, start_y + 62, "Тираж: " + vol, size=11, color=border_col, bold=True))
        p.append(line(bx + 15, start_y + 74, bx + bw - 15, start_y + 74, color=border_col, sw=1, dash="2,2"))

        # Конструктивне рішення
        p.append(mtext(bx + bw / 2, start_y + 96, comp, size=10.5, color=INK, bold=True, lh=1.2))

        # Опис та переваги
        desc_lines = desc.split("\n") if "\n" in desc else [desc[:32], desc[32:64], desc[64:]]
        desc_lines = [l.strip() for l in desc_lines if l.strip()]
        p.append(mtext(bx + bw / 2, start_y + 160, desc_lines, size=9.5, color="#334155", lh=1.3))

        # Стрілка переходу
        if i < 3:
            ax1 = bx + bw + 2
            ax2 = ax1 + 16
            ay_mid = start_y + bh / 2
            p.append(arrow(ax1, ay_mid, ax2, ay_mid, color="#64748b", sw=2))

    # Нижня інфо-панель: як змінюються метрики
    p.append(rect(35, start_y + bh + 15, W - 70, 40, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    p.append(text(60, start_y + bh + 38, "Час виходу на ринок (TTM): від 2 тижнів → до 9-12 місяців", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(W - 60, start_y + bh + 38, "Собівартість одиниці BOM: від $15+ → до < $3.50", size=10.5, color=FIELD, anchor="end", bold=True))

    render(os.path.join(OUT, "lifecycle-migration.svg"), W, H, *p,
           title="4-етапна стратегія міграції конструктиву виробу")


# ── 4. rf-matching-pcb: Трасування ВЧ-тракту (50 Ом хвилевід) ─────────────────
def fig_rf_matching_pcb():
    W, H = 940, 440
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=8))
    p.append(text(W / 2, 40, "Трасування ВЧ-тракту 50 Ом: правильний копланарний хвилевід проти помилок", size=15, color=INK, bold=True))

    # Ліва колонка: ПРАВИЛЬНО (CPW-G копланарний хвилевід)
    lx, ly, lw, lh = 35, 75, 420, 335
    p.append(rect(lx, ly, lw, lh, fill="#f0fdf4", stroke="#22c55e", sw=2, rx=6))
    p.append(text(lx + lw / 2, ly + 28, "✓ ПРАВИЛЬНО: Копланарний хвилевід (CPW-G)", size=12, color="#15803d", bold=True))

    # Візуалізація доріжки з землею та перехідними отворами (via fence)
    p.append(rect(lx + 30, ly + 50, lw - 60, 140, fill="#1e293b", stroke="#334155", sw=1.5, rx=4))
    # Верхній полігон землі
    p.append(rect(lx + 40, ly + 60, lw - 80, 35, fill="#15803d", stroke="#166534", sw=1, rx=2))
    p.append(text(lx + lw / 2, ly + 82, "Top Ground Pour (верхня земля)", size=10, color="#ffffff"))
    # Нижній полігон землі
    p.append(rect(lx + 40, ly + 145, lw - 80, 35, fill="#15803d", stroke="#166534", sw=1, rx=2))
    p.append(text(lx + lw / 2, ly + 167, "Top Ground Pour (верхня земля)", size=10, color="#ffffff"))
    # ВЧ доріжка 50 Ом
    p.append(rect(lx + 40, ly + 105, lw - 80, 30, fill="#d97706", stroke="#b45309", sw=1.5, rx=2))
    p.append(text(lx + lw / 2, ly + 124, "ВЧ-траса Z₀ = 50 Ом (контрольована ширина W та зазор S)", size=9.5, color="#ffffff", bold=True))

    # Via stitching (прошивка отворами)
    for v in range(7):
        vx = lx + 55 + v * 48
        p.append(circle(vx, ly + 72, 4, fill="#ffffff", stroke="#0f172a", sw=1.5))
        p.append(circle(vx, ly + 158, 4, fill="#ffffff", stroke="#0f172a", sw=1.5))

    p.append(text(lx + 20, ly + 215, "• Суцільний неперервний опорний шар GND під трасою (L2).", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 235, "• Зшивка полігонів отворами (Via fence) з кроком < λ/20.", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 255, "• Відсутність розривів імпедансу (постійна ширина W).", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 275, "• Повний зворотний струм тече строго під сигнальною трасою.", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 295, "• Нульове паразитне випромінювання на гармоніках.", size=10.5, color="#15803d", anchor="start", bold=True))

    # Права колонка: ПОМИЛКИ трасування
    rx_col, ry_col, rw_col, rh_col = 485, 75, 420, 335
    p.append(rect(rx_col, ry_col, rw_col, rh_col, fill="#fef2f2", stroke="#ef4444", sw=2, rx=6))
    p.append(text(rx_col + rw_col / 2, ry_col + 28, "✗ ПОМИЛКА: Розрив землі та гострі кути 90°", size=12, color="#b91c1c", bold=True))

    # Візуалізація з дефектами
    p.append(rect(rx_col + 30, ry_col + 50, rw_col - 60, 140, fill="#1e293b", stroke="#334155", sw=1.5, rx=4))
    # Розбитий опорний полігон з розрізом
    p.append(rect(rx_col + 40, ry_col + 60, 130, 120, fill="#fee2e2", stroke="#991b1b", sw=1, rx=2))
    p.append(rect(rx_col + 230, ry_col + 60, 130, 120, fill="#fee2e2", stroke="#991b1b", sw=1, rx=2))
    p.append(text(rx_col + 200, ry_col + 80, "Розріз GND", size=9.5, color="#991b1b"))

    # Крива траса з кутом 90 градусів через розріз
    bad_pts = [
        (rx_col + 40, ry_col + 140), (rx_col + 150, ry_col + 140),
        (rx_col + 150, ry_col + 95), (rx_col + 350, ry_col + 95)
    ]
    bad_pts_str = " ".join(f"{x},{y}" for x, y in bad_pts)
    p.append(f'<polyline points="{bad_pts_str}" fill="none" stroke="#d97706" stroke-width="4" stroke-linecap="square"/>')
    p.append(circle(rx_col + 150, ry_col + 140, 8, fill="none", stroke="#ef4444", sw=2))
    p.append(text(rx_col + 150, ry_col + 165, "Кут 90° (ємнісний стрибок)", size=9.5, color="#991b1b", bold=True))

    # Випромінювання хвиль через розріз
    p.append(f'<path d="M {rx_col+175},{ry_col+115} Q {rx_col+195},{ry_col+100} {rx_col+205},{ry_col+135}" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="3,3"/>')
    p.append(text(rx_col + 200, ry_col + 150, "EMC завада!", size=9.5, color="#ef4444", bold=True))

    p.append(text(rx_col + 20, ry_col + 215, "• Розрив опорного шару змушує струм робити петлю.", size=10.5, color=INK, anchor="start"))
    p.append(text(rx_col + 20, ry_col + 235, "• Стрибок імпедансу з 50 Ом до > 120 Ом (високий КСХ).", size=10.5, color=INK, anchor="start"))
    p.append(text(rx_col + 20, ry_col + 255, "• Гострий кут створює паразитну ємність і відбиття хвиль.", size=10.5, color=INK, anchor="start"))
    p.append(text(rx_col + 20, ry_col + 275, "• Падіння дальності зв'язку на 60–80%.", size=10.5, color=INK, anchor="start"))
    p.append(text(rx_col + 20, ry_col + 295, "• Гарантований провал сертифікації FCC/CE по випромінюванню.", size=10.5, color="#b91c1c", anchor="start", bold=True))

    render(os.path.join(OUT, "rf-matching-pcb.svg"), W, H, *p,
           title="Трасування ВЧ-тракту: копланарний хвилевід проти топологічних помилок")


if __name__ == "__main__":
    fig_module_anatomy()
    fig_crossover_curve()
    fig_lifecycle_migration()
    fig_rf_matching_pcb()
    print("All figures generated successfully.")
