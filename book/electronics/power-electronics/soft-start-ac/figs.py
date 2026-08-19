# -*- coding: utf-8 -*-
import sys, os
import math

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/electronics/power-electronics/soft-start-ac)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COL_MOTOR = "#2457d6"    # синій — двигун
COL_XFMR  = "#c0392b"    # червоний — трансформатор / магнітне насичення
COL_HEAT  = "#d35400"    # помаранчевий — нагрівачі / лампи
COL_SCR   = "#8e44ad"    # фіолетовий — тиристори
COL_CONT  = "#27ae60"    # зелений — байпасний контактор
COL_WARN  = "#b8901f"    # золотисто-жовтий — попередження / кидки


# ── 1. three-ac-inrush-causes.svg ──────────────────────────────────────────────
# Три фізичні механізми кидка струму в колах змінного струму:
# А: Асинхронний двигун (s=1, нуль проти-ЕРС, 5-8x Iном)
# Б: Трансформатор (увімкнення в нуль напруги, 2*Фмакс + Фзал, насичення, 10-40x Iном)
# В: Нагрівач / лампа (холодний опір Rхол = Rгар/15, 10-15x Iном)

def fig_three_ac_inrush_causes():
    W, H = 840, 480
    p = []

    cols = [
        ("А. Асинхронний двигун", 150, COL_MOTOR),
        ("Б. Силовий трансформатор", 420, COL_XFMR),
        ("В. Лампа / нагрівач", 690, COL_HEAT),
    ]
    cw, ch = 250, 410

    for title, cx, col in cols:
        x = cx - cw / 2
        y = 20
        p.append(rect(x, y, cw, ch, fill="none", stroke=col, sw=1.6, rx=8))
        p.append(text(cx, y + 26, title, size=15, color=col, bold=True))
        p.append(line(x + 15, y + 38, x + cw - 15, y + 38, color=col, sw=1.2))

    # Колонка А: Двигун
    cA = 150
    p.append(circle(cA, 95, 26, fill="#eef4fd", stroke=COL_MOTOR, sw=2))
    p.append(text(cA, 91, "M", size=18, color=COL_MOTOR, bold=True))
    p.append(text(cA, 107, "3~", size=11, color=COL_MOTOR, bold=True))

    b1, _, _ = textbox(cA, 155, ["Стан спокою: швидкість ω = 0", "Ковзання s = 1.0", "Проти-ЕРС = 0 В"],
                       size=11, fill="#ffffff", stroke=COL_MOTOR, sw=1.1, pad=6, min_w=220)
    p.append(b1)

    b2, _, _ = textbox(cA, 235, ["Опір короткозамкненого ротора", "вкрай малий (Zпуск ≈ Rобм + jX)", "Обмежений лише міддю обмоток"],
                       size=11, fill="#ffffff", stroke=MUTED, sw=1, pad=6, min_w=220)
    p.append(b2)

    b3, _, _ = textbox(cA, 320, ["Кидок струму:", "5 ... 8 × Іном", "Ударний момент: 2 ... 3 × Тном"],
                       size=12, fill="#e1ecfc", stroke=COL_MOTOR, sw=1.5, color=COL_MOTOR, bold=True, pad=8, min_w=220)
    p.append(b3)

    b4, _, _ = textbox(cA, 395, ["Наслідок: просадка напруги в мережі,", "механічний удар по редукторах і валах"],
                       size=10, fill="#ffffff", stroke=MUTED, sw=1, color=INK, pad=5, min_w=220)
    p.append(b4)

    # Колонка Б: Трансформатор
    cB = 420
    p.append(circle(cB - 12, 95, 18, fill="#fdf0ed", stroke=COL_XFMR, sw=2))
    p.append(circle(cB + 12, 95, 18, fill="#fdf0ed", stroke=COL_XFMR, sw=2))

    b5, _, _ = textbox(cB, 155, ["Вмикання в нуль напруги (v=0)", "Інтеграл Φ(t) = ∫ v dt", "Подвоєння: Φмакс → 2·Φмакс + Φзал"],
                       size=11, fill="#ffffff", stroke=COL_XFMR, sw=1.1, pad=6, min_w=220)
    p.append(b5)

    b6, _, _ = textbox(cB, 235, ["Осердя входить у глибоке насичення", "Проникність падає: μr → μ0 (повітря)", "Індуктивність котушки обвалюється"],
                       size=11, fill="#ffffff", stroke=MUTED, sw=1, pad=6, min_w=220)
    p.append(b6)

    b7, _, _ = textbox(cB, 320, ["Кидок намагнічування:", "10 ... 40 × Іном", "Аперіодична складова триває секунди"],
                       size=12, fill="#fcdcd7", stroke=COL_XFMR, sw=1.5, color=COL_XFMR, bold=True, pad=8, min_w=220)
    p.append(b7)

    b8, _, _ = textbox(cB, 395, ["Наслідок: помилкові спрацьовування", "автоматів захисту та струмовий стрес"],
                       size=10, fill="#ffffff", stroke=MUTED, sw=1, color=INK, pad=5, min_w=220)
    p.append(b8)

    # Колонка В: Нагрівач / лампа
    cC = 690
    p.append(circle(cC, 95, 20, fill="#fdf3eb", stroke=COL_HEAT, sw=2))
    p.append(line(cC - 12, 95 - 12, cC + 12, 95 + 12, color=COL_HEAT, sw=1.8))
    p.append(line(cC - 12, 95 + 12, cC + 12, 95 - 12, color=COL_HEAT, sw=1.8))

    b9, _, _ = textbox(cC, 155, ["Холодний стан метал. провідника (20 °C)", "Позитивний темп. коефіцієнт (PTC)", "Rхол = Rгар / (10 ... 15)"],
                       size=11, fill="#ffffff", stroke=COL_HEAT, sw=1.1, pad=6, min_w=220)
    p.append(b9)

    b10, _, _ = textbox(cC, 235, ["Опір росте лише в міру розігріву", "ТКС вольфраму / ніхрому:", "доки метал холодний — опір мізерний"],
                        size=11, fill="#ffffff", stroke=MUTED, sw=1, pad=6, min_w=220)
    p.append(b10)

    b11, _, _ = textbox(cC, 320, ["Холодний кидок струму:", "10 ... 15 × Іном", "Спадає за 50 ... 200 мс під час нагріву"],
                        size=12, fill="#fde6d5", stroke=COL_HEAT, sw=1.5, color=COL_HEAT, bold=True, pad=8, min_w=220)
    p.append(b11)

    b12, _, _ = textbox(cC, 395, ["Наслідок: тепловий удар по нитці,", "перегорання ламп у мить вмикання"],
                        size=10, fill="#ffffff", stroke=MUTED, sw=1, color=INK, pad=5, min_w=220)
    p.append(b12)

    render(os.path.join(OUT, "three-ac-inrush-causes.svg"), W, H, *p,
           title="Три фізичні причини пускових струмів змінного навантаження")


# ── 2. thyristor-phase-control.svg ─────────────────────────────────────────────
# Фазове керування змінною напругою

def fig_thyristor_phase_control():
    W, H = 820, 440
    p = []

    b_top, _, _ = textbox(W / 2, 28,
                          "Фазове керування: плавне зменшення кута затримки α від 150° до 0° збільшує діючу напругу",
                          size=12, fill="#f4f6f8", stroke=COL_SCR, sw=1.3, pad=7)
    p.append(b_top)

    panels = [
        ("Вхідна мережева напруга (50 Гц)", 80, "full_sin"),
        ("Старт розгону: кут α = 135° (Uдіюче ≈ 30% Uном)", 165, "alpha_135"),
        ("Середина розгону: кут α = 75° (Uдіюче ≈ 75% Uном)", 250, "alpha_75"),
        ("Фініш розгону: кут α = 0° → увімкнення байпасу", 335, "alpha_0"),
    ]

    gx_start = 280
    gx_end   = 760
    gw       = gx_end - gx_start
    n_pts    = 200

    for title, gy, mode in panels:
        p.append(text(gx_start - 15, gy + 4, title, size=11, color=INK, anchor="end", bold=True))
        p.append(line(gx_start, gy, gx_end, gy, color="#d0d7de", sw=1))

        sin_pts = []
        for i in range(n_pts + 1):
            t = (i / n_pts) * (4 * math.pi)
            x = gx_start + (i / n_pts) * gw
            y = gy - 26 * math.sin(t)
            sin_pts.append((x, y))

        for i in range(len(sin_pts) - 1):
            p.append(line(sin_pts[i][0], sin_pts[i][1], sin_pts[i+1][0], sin_pts[i+1][1], color="#cbd5e1", sw=1, dash="2,2"))

        col_curve = COL_SCR if mode != "full_sin" else "#64748b"
        if mode == "alpha_0":
            col_curve = COL_CONT

        fill_poly = [(gx_start, gy)]
        for i in range(n_pts + 1):
            t = (i / n_pts) * (4 * math.pi)
            half_cycle_t = t % math.pi
            x = gx_start + (i / n_pts) * gw

            val = 0.0
            if mode == "full_sin":
                val = math.sin(t)
            elif mode == "alpha_135":
                alpha = 135.0 * math.pi / 180.0
                if half_cycle_t >= alpha:
                    val = math.sin(t)
            elif mode == "alpha_75":
                alpha = 75.0 * math.pi / 180.0
                if half_cycle_t >= alpha:
                    val = math.sin(t)
            elif mode == "alpha_0":
                val = math.sin(t)

            y = gy - 26 * val
            fill_poly.append((x, y))

        fill_poly.append((gx_end, gy))

        for i in range(1, len(fill_poly) - 2):
            x1, y1 = fill_poly[i]
            x2, y2 = fill_poly[i+1]
            p.append(line(x1, y1, x2, y2, color=col_curve, sw=2))

        if mode == "alpha_135":
            x_zero = gx_start
            x_fire = gx_start + (135.0 / 360.0) * (gw / 2)
            p.append(line(x_fire, gy - 28, x_fire, gy + 28, color=POS, sw=1.2, dash="2,2"))
            p.append(arrow(x_zero + 5, gy - 12, x_fire - 2, gy - 12, color=POS, sw=1.2))
            p.append(text((x_zero + x_fire) / 2, gy - 18, "α = 135°", size=10, color=POS, bold=True))
        elif mode == "alpha_75":
            x_zero = gx_start
            x_fire = gx_start + (75.0 / 360.0) * (gw / 2)
            p.append(line(x_fire, gy - 28, x_fire, gy + 28, color=POS, sw=1.2, dash="2,2"))
            p.append(arrow(x_zero + 5, gy - 12, x_fire - 2, gy - 12, color=POS, sw=1.2))
            p.append(text((x_zero + x_fire) / 2, gy - 18, "α = 75°", size=10, color=POS, bold=True))
        elif mode == "alpha_0":
            p.append(text(gx_end + 15, gy + 4, "KM1 закрито!", size=10, color=COL_CONT, anchor="start", bold=True))

    b_bot, _, _ = textbox(W / 2, 410,
                          "Зрізані синусоїди формують нижчу діючу напругу U_rms(α) = U_line · √((π−α + ½·sin 2α)/π), зменшуючи пусковий струм",
                          size=11, fill="#ffffff", stroke=MUTED, sw=1, pad=6)
    p.append(b_bot)

    render(os.path.join(OUT, "thyristor-phase-control.svg"), W, H, *p,
           title="Фазове зрізання синусоїди зустрічно-паралельними тиристорами")


# ── 3. softstart-power-schematic.svg ───────────────────────────────────────────
# Силова принципова схема трифазного софтстартера

def fig_softstart_power_schematic():
    W, H = 820, 480
    p = []

    b_head, _, _ = textbox(W / 2, 25,
                           "Силова схема трифазного софтстартера: тиристорний міст, байпасний контактор та контур вимірювання струму",
                           size=12, fill="#f4f6f8", stroke=LINE, sw=1.3, pad=6)
    p.append(b_head)

    y_lines = [95, 175, 255]
    phase_names = ["L1 (A)", "L2 (B)", "L3 (C)"]

    x_in   = 50
    x_scr  = 230
    x_bp_s = 140
    x_bp_e = 440
    x_bp_y = 350
    x_ct   = 530
    x_out  = 680

    p.append(rect(110, 55, 490, 365, fill="#fafbfc", stroke="#94a3b8", sw=1.4, rx=8))
    p.append(text(355, 75, "Блок плавного пуску (Soft Starter)", size=13, color=MUTED, bold=True))

    for i, y in enumerate(y_lines):
        p.append(text(x_in - 5, y + 4, phase_names[i], size=12, color=INK, anchor="end", bold=True))
        p.append(line(x_in, y, x_scr - 45, y, color=LINE, sw=2))

        p.append(circle(x_bp_s + i * 25, y, 3.5, fill=LINE, stroke=LINE))
        p.append(line(x_bp_s + i * 25, y, x_bp_s + i * 25, x_bp_y + i * 18 - 25, color=COL_CONT, sw=1.6))

        scr_box_w, scr_box_h = 75, 42
        p.append(rect(x_scr - scr_box_w/2, y - scr_box_h/2, scr_box_w, scr_box_h, fill="#f5eeff", stroke=COL_SCR, sw=1.6, rx=5))
        p.append(text(x_scr, y - 6, f"SCR {2*i+1}", size=10, color=COL_SCR, bold=True))
        p.append(text(x_scr, y + 10, f"SCR {2*i+2}", size=10, color=COL_SCR, bold=True))
        p.append(line(x_scr - 30, y, x_scr + 30, y, color=COL_SCR, sw=1, dash="2,2"))

        p.append(line(x_scr + 45, y, x_ct - 25, y, color=LINE, sw=2))

        p.append(circle(x_bp_e - i * 20, y, 3.5, fill=LINE, stroke=LINE))
        p.append(line(x_bp_e - i * 20, x_bp_y + i * 18 + 15, x_bp_e - i * 20, y, color=COL_CONT, sw=1.6))

        p.append(rect(x_ct - 16, y - 18, 32, 36, fill="#fdf0ed", stroke=COL_XFMR, sw=1.4, rx=4))
        p.append(text(x_ct, y + 4, f"CT{i+1}", size=10, color=COL_XFMR, bold=True))

        p.append(line(x_ct + 16, y, x_out, y, color=LINE, sw=2))

    p.append(rect(230, 315, 170, 85, fill="#edfcf2", stroke=COL_CONT, sw=1.6, rx=6))
    p.append(text(315, 335, "Байпасний контактор KM1", size=11, color=COL_CONT, bold=True))
    p.append(text(315, 353, "(замикається після розгону,", size=10, color=COL_CONT))
    p.append(text(315, 368, "ліквідує втрати нагріву SCR)", size=10, color=COL_CONT))
    p.append(text(315, 388, "Втрати SCR: 1.2 В × 100 А → 0 Вт", size=9, color=MUTED, bold=True))

    for i, y in enumerate(y_lines):
        p.append(line(x_bp_s + i * 25, x_bp_y + i * 18 - 25, 230, x_bp_y + i * 18 - 25, color=COL_CONT, sw=1.6))
        p.append(line(400, x_bp_y + i * 18 + 15, x_bp_e - i * 20, x_bp_y + i * 18 + 15, color=COL_CONT, sw=1.6))

    p.append(circle(735, 175, 45, fill="#eef4fd", stroke=COL_MOTOR, sw=2.2))
    p.append(text(735, 168, "M", size=24, color=COL_MOTOR, bold=True))
    p.append(text(735, 192, "3 ~", size=14, color=COL_MOTOR, bold=True))

    p.append(line(x_out, 95, 698, 145, color=LINE, sw=2))
    p.append(line(x_out, 175, 690, 175, color=LINE, sw=2))
    p.append(line(x_out, 255, 698, 205, color=LINE, sw=2))

    p.append(rect(485, 315, 100, 85, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=5))
    p.append(text(535, 335, "MCU контролер", size=10, color=INK, bold=True))
    p.append(text(535, 353, "• ZC детектор", size=9, color=MUTED))
    p.append(text(535, 368, "• ПІД струму", size=9, color=MUTED))
    p.append(text(535, 385, "• Керування KM1", size=9, color=MUTED))

    b_foot, _, _ = textbox(W / 2, 452,
                           "У розгоні струм ведуть тиристори SCR; після виходу на швидкість контактор KM1 шунтує ключі, прибираючи падіння 1.2 В",
                           size=11, fill="#ffffff", stroke=LINE, sw=1, pad=6)
    p.append(b_foot)

    render(os.path.join(OUT, "softstart-power-schematic.svg"), W, H, *p,
           title="Принципова схема силового трифазного софтстартера з байпасом")


# ── 4. softstart-control-curves.svg ────────────────────────────────────────────
# Порівняння характеристик пуску

def fig_softstart_control_curves():
    W, H = 820, 440
    p = []

    b_head, _, _ = textbox(W / 2, 24,
                           "Порівняння методів пуску асинхронного двигуна: прямий пуск, зірка-трикутник та електронний софтстартер",
                           size=12, fill="#f4f6f8", stroke=LINE, sw=1.3, pad=6)
    p.append(b_head)

    gx1, gy1, gw1, gh1 = 90, 80, 270, 240
    gx2, gy2, gw2, gh2 = 470, 80, 270, 240

    # Графік 1: Струм
    p.append(rect(gx1, gy1, gw1, gh1, fill="#ffffff", stroke="#cbd5e1", sw=1))
    p.append(line(gx1, gy1 + gh1, gx1 + gw1, gy1 + gh1, color=INK, sw=1.5))
    p.append(line(gx1, gy1, gx1, gy1 + gh1, color=INK, sw=1.5))
    p.append(text(gx1 + gw1 / 2, gy1 - 10, "Струм двигуна (I / Іном)", size=13, color=INK, bold=True))
    p.append(text(gx1 + gw1, gy1 + gh1 + 18, "Час t", size=11, color=MUTED))
    p.append(text(gx1 - 8, gy1 + 10, "8×", size=10, color=MUTED, anchor="end"))
    p.append(text(gx1 - 8, gy1 + gh1 * 0.5, "4×", size=10, color=MUTED, anchor="end"))
    p.append(text(gx1 - 8, gy1 + gh1 * 0.875, "1×", size=10, color=MUTED, anchor="end"))
    p.append(line(gx1, gy1 + gh1 * 0.875, gx1 + gw1, gy1 + gh1 * 0.875, color="#e2e8f0", sw=1, dash="2,2"))

    # Крива 1 (DOL):
    p.append(line(gx1, gy1 + gh1 * 0.12, gx1 + 50, gy1 + gh1 * 0.12, color=POS, sw=2))
    p.append(line(gx1 + 50, gy1 + gh1 * 0.12, gx1 + 75, gy1 + gh1 * 0.875, color=POS, sw=2))
    p.append(text(gx1 + 10, gy1 + gh1 * 0.12 - 8, "DOL (7×)", size=10, color=POS, anchor="start", bold=True))

    # Крива 2 (Зірка-трикутник):
    p.append(line(gx1, gy1 + gh1 * 0.65, gx1 + 90, gy1 + gh1 * 0.78, color=COL_WARN, sw=2))
    p.append(line(gx1 + 90, gy1 + gh1 * 0.78, gx1 + 92, gy1 + gh1 * 0.35, color=COL_WARN, sw=2))
    p.append(line(gx1 + 92, gy1 + gh1 * 0.35, gx1 + 130, gy1 + gh1 * 0.875, color=COL_WARN, sw=2))
    p.append(text(gx1 + 96, gy1 + gh1 * 0.35 - 8, "Сплеск Y-Δ", size=10, color=COL_WARN, anchor="start", bold=True))

    # Крива 3 (Soft Start):
    p.append(line(gx1, gy1 + gh1 * 0.52, gx1 + 180, gy1 + gh1 * 0.52, color=COL_CONT, sw=2.5))
    p.append(line(gx1 + 180, gy1 + gh1 * 0.52, gx1 + 220, gy1 + gh1 * 0.875, color=COL_CONT, sw=2.5))
    p.append(line(gx1 + 220, gy1 + gh1 * 0.875, gx1 + gw1, gy1 + gh1 * 0.875, color=COL_CONT, sw=2.5))
    p.append(text(gx1 + 165, gy1 + gh1 * 0.52 - 8, "Софтстартер (3.5×)", size=10, color=COL_CONT, anchor="start", bold=True))

    # Графік 2: Момент
    p.append(rect(gx2, gy2, gw2, gh2, fill="#ffffff", stroke="#cbd5e1", sw=1))
    p.append(line(gx2, gy2 + gh2, gx2 + gw2, gy2 + gh2, color=INK, sw=1.5))
    p.append(line(gx2, gy2, gx2, gy2 + gh2, color=INK, sw=1.5))
    p.append(text(gx2 + gw2 / 2, gy2 - 10, "Обертовий момент (T / Тном)", size=13, color=INK, bold=True))
    p.append(text(gx2 + gw2, gy2 + gh2 + 18, "Час t", size=11, color=MUTED))
    p.append(text(gx2 - 8, gy2 + 15, "3×", size=10, color=MUTED, anchor="end"))
    p.append(text(gx2 - 8, gy2 + gh2 * 0.45, "2×", size=10, color=MUTED, anchor="end"))
    p.append(text(gx2 - 8, gy2 + gh2 * 0.72, "1×", size=10, color=MUTED, anchor="end"))
    p.append(line(gx2, gy2 + gh2 * 0.72, gx2 + gw2, gy2 + gh2 * 0.72, color="#e2e8f0", sw=1, dash="2,2"))

    # Крива 1 (DOL):
    p.append(line(gx2, gy2 + gh2 * 0.3, gx2 + 50, gy2 + gh2 * 0.2, color=POS, sw=2))
    p.append(line(gx2 + 50, gy2 + gh2 * 0.2, gx2 + 75, gy2 + gh2 * 0.72, color=POS, sw=2))
    p.append(text(gx2 + 10, gy2 + gh2 * 0.2 - 8, "Ударний момент DOL", size=10, color=POS, anchor="start", bold=True))

    # Крива 2 (Зірка-трикутник):
    p.append(line(gx2, gy2 + gh2 * 0.88, gx2 + 90, gy2 + gh2 * 0.82, color=COL_WARN, sw=2))
    p.append(line(gx2 + 90, gy2 + gh2 * 0.82, gx2 + 92, gy2 + gh2 * 0.38, color=COL_WARN, sw=2))
    p.append(line(gx2 + 92, gy2 + gh2 * 0.38, gx2 + 130, gy2 + gh2 * 0.72, color=COL_WARN, sw=2))
    p.append(text(gx2 + 96, gy2 + gh2 * 0.38 - 8, "Удар при Y→Δ", size=10, color=COL_WARN, anchor="start", bold=True))

    # Крива 3 (Soft Start):
    p.append(line(gx2, gy2 + gh2 * 0.92, gx2 + 180, gy2 + gh2 * 0.65, color=COL_CONT, sw=2.5))
    p.append(line(gx2 + 180, gy2 + gh2 * 0.65, gx2 + 220, gy2 + gh2 * 0.72, color=COL_CONT, sw=2.5))
    p.append(line(gx2 + 220, gy2 + gh2 * 0.72, gx2 + gw2, gy2 + gh2 * 0.72, color=COL_CONT, sw=2.5))
    p.append(text(gx2 + 160, gy2 + gh2 * 0.65 - 8, "Плавний момент", size=10, color=COL_CONT, anchor="start", bold=True))

    # Легенда знизу
    b_leg, _, _ = textbox(W / 2, 405,
                          "Червоний — прямий пуск (ударний струм і момент); Жовтий — Y-Δ (провал і вторинний удар); Зелений — плавний пуск",
                          size=11, fill="#ffffff", stroke=MUTED, sw=1, pad=7)
    p.append(b_leg)

    render(os.path.join(OUT, "softstart-control-curves.svg"), W, H, *p,
           title="Порівняльні криві струму та моменту під час пуску різними методами")


# ── 5. softstart-vs-softstop.svg ───────────────────────────────────────────────
# Профілі керування: Плавний пуск із поштовхом (Kickstart) та Плавна зупинка (Soft Stop)

def fig_softstart_vs_softstop():
    W, H = 820, 440
    p = []

    b_head, _, _ = textbox(W / 2, 24,
                           "Режими роботи софтстартера: початковий поштовх (Kickstart), рампа напруги та плавна зупинка (Soft Stop)",
                           size=12, fill="#f4f6f8", stroke=LINE, sw=1.3, pad=6)
    p.append(b_head)

    gx1, gy1, gw1, gh1 = 80, 75, 300, 245
    gx2, gy2, gw2, gh2 = 440, 75, 300, 245

    # Ліва панель
    p.append(rect(gx1, gy1, gw1, gh1, fill="#ffffff", stroke="#cbd5e1", sw=1))
    p.append(line(gx1, gy1 + gh1, gx1 + gw1, gy1 + gh1, color=INK, sw=1.5))
    p.append(line(gx1, gy1, gx1, gy1 + gh1, color=INK, sw=1.5))
    p.append(text(gx1 + gw1 / 2, gy1 - 10, "Плавний пуск (Soft Start)", size=13, color=COL_MOTOR, bold=True))
    p.append(text(gx1 + gw1, gy1 + gh1 + 18, "Час t", size=10, color=MUTED))
    p.append(text(gx1 - 8, gy1 + 15, "100%", size=10, color=MUTED, anchor="end"))
    p.append(text(gx1 - 8, gy1 + gh1 * 0.65, "Uстарт", size=10, color=MUTED, anchor="end"))
    p.append(text(gx1 - 8, gy1 + gh1, "0%", size=10, color=MUTED, anchor="end"))

    # Kickstart
    p.append(rect(gx1, gy1 + gh1 * 0.25, 25, gh1 * 0.75, fill="#fde6d5", stroke=COL_HEAT, sw=1.2))
    p.append(text(gx1 + 12, gy1 + gh1 * 0.25 - 8, "Kick", size=9, color=COL_HEAT, bold=True))

    # Рампа напруги
    p.append(line(gx1 + 25, gy1 + gh1 * 0.65, gx1 + 200, gy1 + gh1 * 0.08, color=COL_MOTOR, sw=2.5))
    p.append(line(gx1 + 200, gy1 + gh1 * 0.08, gx1 + gw1, gy1 + gh1 * 0.08, color=COL_CONT, sw=2.5))
    p.append(text(gx1 + 110, gy1 + gh1 * 0.42, "Рампа напруги U(t)", size=10, color=COL_MOTOR, bold=True))
    p.append(text(gx1 + 240, gy1 + gh1 * 0.08 - 8, "Байпас (100%)", size=9, color=COL_CONT, bold=True))

    p.append(arrow(gx1 + 25, gy1 + gh1 - 15, gx1 + 200, gy1 + gh1 - 15, color=MUTED, sw=1.2))
    p.append(text(gx1 + 112, gy1 + gh1 - 22, "Час пуску tпуск (1...30 с)", size=10, color=MUTED))

    # Права панель
    p.append(rect(gx2, gy2, gw2, gh2, fill="#ffffff", stroke="#cbd5e1", sw=1))
    p.append(line(gx2, gy2 + gh2, gx2 + gw2, gy2 + gh2, color=INK, sw=1.5))
    p.append(line(gx2, gy2, gx2, gy2 + gh2, color=INK, sw=1.5))
    p.append(text(gx2 + gw2 / 2, gy2 - 10, "Плавна зупинка (Soft Stop)", size=13, color=COL_XFMR, bold=True))
    p.append(text(gx2 + gw2, gy2 + gh2 + 18, "Час t", size=10, color=MUTED))
    p.append(text(gx2 - 8, gy2 + 15, "100%", size=10, color=MUTED, anchor="end"))
    p.append(text(gx2 - 8, gy2 + gh2 * 0.65, "Uстоп", size=10, color=MUTED, anchor="end"))
    p.append(text(gx2 - 8, gy2 + gh2, "0%", size=10, color=MUTED, anchor="end"))

    p.append(line(gx2, gy2 + gh2 * 0.08, gx2 + 35, gy2 + gh2 * 0.08, color=COL_CONT, sw=2.5))
    p.append(line(gx2 + 35, gy2 + gh2 * 0.08, gx2 + 220, gy2 + gh2 * 0.65, color=COL_XFMR, sw=2.5))
    p.append(line(gx2 + 220, gy2 + gh2 * 0.65, gx2 + 225, gy2 + gh2, color=COL_XFMR, sw=2))
    p.append(line(gx2 + 225, gy2 + gh2, gx2 + gw2, gy2 + gh2, color=MUTED, sw=1.5))

    p.append(text(gx2 + 130, gy2 + gh2 * 0.32, "Спад напруги U(t)", size=10, color=COL_XFMR, bold=True))
    p.append(text(gx2 + 240, gy2 + gh2 * 0.65 - 6, "Відсічка", size=9, color=COL_XFMR))

    p.append(arrow(gx2 + 35, gy2 + gh2 - 15, gx2 + 220, gy2 + gh2 - 15, color=MUTED, sw=1.2))
    p.append(text(gx2 + 125, gy2 + gh2 - 22, "Час зупинки tстоп (2...60 с)", size=10, color=MUTED))

    b_bot, _, _ = textbox(W / 2, 385,
                          "У насосних системах раптове вимкнення спричиняє закриття зворотного клапана й руйнівний гідроудар у трубах.",
                          size=11, fill="#fdf0ed", stroke=COL_XFMR, sw=1.2, pad=6)
    p.append(b_bot)

    b_bot2, _, _ = textbox(W / 2, 415,
                           "Режим Soft Stop поступово знижує напругу, сповільнюючи водяний стовп без гідравлічних сплесків тиску.",
                           size=11, fill="#ffffff", stroke=MUTED, sw=1, pad=5)
    p.append(b_bot2)

    render(os.path.join(OUT, "softstart-vs-softstop.svg"), W, H, *p,
           title="Профілі напруги: розгін із початковим поштовхом та плавна зупинка")


def main():
    fig_three_ac_inrush_causes()
    fig_thyristor_phase_control()
    fig_softstart_power_schematic()
    fig_softstart_control_curves()
    fig_softstart_vs_softstop()
    print("Усі фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
