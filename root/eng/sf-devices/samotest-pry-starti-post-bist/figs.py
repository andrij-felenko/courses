# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольорова палітра для функційної безпеки
SAFE_GREEN = "#1e8449"
SAFE_BG    = "#d5f5e3"
WARN_AMBER = "#b9770e"
WARN_BG    = "#fdf3d6"
CRIT_RED   = "#c0392b"
CRIT_BG    = "#fcdcd7"
BLUE_DARK  = "#1a5276"
BLUE_BG    = "#d6eaf8"
PURPLE_DK  = "#6c3483"
PURPLE_BG  = "#ebdef0"


# ── 1. safety-standards-classes: класи безпеки та часовий бюджет ──────────────
def fig_safety_standards():
    W, H = 840, 520
    p = []

    # Заголовок блоків класифікації
    p.append(text(W / 2, 28, "Класифікація функційної безпеки та часовий бюджет реакції на відмову", size=15, bold=True))

    # Три колонки стандартів
    cw = 240
    gap = 25
    left_x = 45

    # Class A
    x1 = left_x
    p.append(rect(x1, 55, cw, 160, fill="#f8f9f9", stroke=MUTED, sw=1.5, rx=6))
    p.append(rect(x1, 55, cw, 34, fill="#ebedef", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(x1 + cw / 2, 77, "Class A (IEC 60730)", size=13, bold=True, color=INK))
    p.append(mtext(x1 + cw / 2, 110, "Некритичні функції\nВідмова не створює небезпеки\nПриклади: дисплей, підсвітка,\nклавіатура інтерфейсу", size=11, color=INK))

    # Class B
    x2 = x1 + cw + gap
    p.append(rect(x2, 55, cw, 160, fill=WARN_BG, stroke=WARN_AMBER, sw=1.8, rx=6))
    p.append(rect(x2, 55, cw, 34, fill="#fdebd0", stroke=WARN_AMBER, sw=1.8, rx=6))
    p.append(text(x2 + cw / 2, 77, "Class B (SIL 2 / ASIL B)", size=13, bold=True, color=WARN_AMBER))
    p.append(mtext(x2 + cw / 2, 110, "Запобігання небезпечній роботі\nОдинична відмова в MCU/ПЗ\nПриклади: контроль дверцят,\nтермостат бойлера, пралки", size=11, color=INK))

    # Class C
    x3 = x2 + cw + gap
    p.append(rect(x3, 55, cw, 160, fill=CRIT_BG, stroke=CRIT_RED, sw=1.8, rx=6))
    p.append(rect(x3, 55, cw, 34, fill="#fadbd8", stroke=CRIT_RED, sw=1.8, rx=6))
    p.append(text(x3 + cw / 2, 77, "Class C (SIL 3 / ASIL D)", size=13, bold=True, color=CRIT_RED))
    p.append(mtext(x3 + cw / 2, 110, "Запобігання вибуху та пожежі\nОдиничні та подвійні відмови\nПриклади: газові котли, клапани\nпалива, медичні апарати", size=11, color=INK))

    # Нижня частина: часова діаграма FDTI + FRT <= PST
    by = 240
    p.append(rect(left_x, by, W - 2 * left_x, 245, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(W / 2, by + 28, "Часовий бюджет безпеки: Process Safety Time (PST)", size=13, bold=True, color=BLUE_DARK))

    # Часова вісь
    t_start = left_x + 40
    t_len = W - 2 * left_x - 80
    ty = by + 90

    p.append(arrow(t_start, ty, t_start + t_len, ty, color=LINE, sw=2.0))
    p.append(text(t_start + t_len - 15, ty + 22, "Час (t)", size=11, bold=True, color=MUTED))

    # Точки на осі
    pt_fault = t_start + 40
    pt_detect = pt_fault + 260
    pt_safe = pt_detect + 200
    pt_danger = t_start + t_len - 50

    p.append(circle(pt_fault, ty, 5, fill=CRIT_RED, stroke=INK, sw=1.5))
    p.append(text(pt_fault, ty - 15, "Виникнення відмови", size=11, bold=True, color=CRIT_RED))
    p.append(line(pt_fault, ty, pt_fault, ty + 70, color=CRIT_RED, sw=1.2, dash="4,4"))

    p.append(circle(pt_detect, ty, 5, fill=WARN_AMBER, stroke=INK, sw=1.5))
    p.append(text(pt_detect, ty - 15, "Виявлення (BIST)", size=11, bold=True, color=WARN_AMBER))
    p.append(line(pt_detect, ty, pt_detect, ty + 70, color=WARN_AMBER, sw=1.2, dash="4,4"))

    p.append(circle(pt_safe, ty, 5, fill=SAFE_GREEN, stroke=INK, sw=1.5))
    p.append(text(pt_safe, ty - 15, "Безпечний стан", size=11, bold=True, color=SAFE_GREEN))
    p.append(line(pt_safe, ty, pt_safe, ty + 70, color=SAFE_GREEN, sw=1.2, dash="4,4"))

    p.append(circle(pt_danger, ty, 5, fill=CRIT_RED, stroke=INK, sw=1.5))
    p.append(text(pt_danger, ty - 15, "Межа шкоди (аварія)", size=11, bold=True, color=CRIT_RED))
    p.append(line(pt_danger, ty, pt_danger, ty + 120, color=CRIT_RED, sw=1.5, dash="2,2"))

    # Інтервали
    # FDTI
    iy1 = ty + 35
    p.append(line(pt_fault, iy1, pt_detect, iy1, color=BLUE_DARK, sw=2.0))
    p.append(line(pt_fault, iy1 - 5, pt_fault, iy1 + 5, color=BLUE_DARK, sw=2.0))
    p.append(line(pt_detect, iy1 - 5, pt_detect, iy1 + 5, color=BLUE_DARK, sw=2.0))
    p.append(text((pt_fault + pt_detect) / 2, iy1 - 8, "FDTI (період діагностики BIST)", size=10.5, bold=True, color=BLUE_DARK))

    # FRT
    p.append(line(pt_detect, iy1, pt_safe, iy1, color=PURPLE_DK, sw=2.0))
    p.append(line(pt_safe, iy1 - 5, pt_safe, iy1 + 5, color=PURPLE_DK, sw=2.0))
    p.append(text((pt_detect + pt_safe) / 2, iy1 - 8, "FRT (час переходу)", size=10.5, bold=True, color=PURPLE_DK))

    # PST загальний
    iy2 = ty + 95
    p.append(line(pt_fault, iy2, pt_danger, iy2, color=CRIT_RED, sw=2.0))
    p.append(line(pt_fault, iy2 - 6, pt_fault, iy2 + 6, color=CRIT_RED, sw=2.0))
    p.append(line(pt_danger, iy2 - 6, pt_danger, iy2 + 6, color=CRIT_RED, sw=2.0))
    p.append(text((pt_fault + pt_danger) / 2, iy2 - 10, "PST (Process Safety Time: граничний час розвитку небезпеки)", size=11, bold=True, color=CRIT_RED))

    p.append(rect((pt_fault + pt_safe) / 2 - 190, by + 205, 380, 26, fill="#e8f8f5", stroke=SAFE_GREEN, sw=1.5, rx=4))
    p.append(text((pt_fault + pt_safe) / 2, by + 222, "Критична вимога: FDTI + FRT ≤ PST", size=11.5, bold=True, color=SAFE_GREEN))

    render(os.path.join(OUT, "safety-standards-classes.svg"), W, H, *p,
           title="Класи функційної безпеки та часовий бюджет")


# ── 2. post-vs-runtime-timeline: життєвий цикл POST та фонового BIST ─────────
def fig_post_timeline():
    W, H = 840, 480
    p = []

    p.append(text(W / 2, 28, "Життєвий цикл самотестування: стартовий POST та фоновий BIST", size=15, bold=True))

    bx = 40
    bw = W - 2 * bx

    # Фаза 1: Power On Reset & Pre-Init POST
    y1 = 65
    h1 = 100
    p.append(rect(bx, y1, bw, h1, fill="#f4f6f7", stroke=LINE, sw=1.5, rx=6))
    p.append(rect(bx, y1, 150, h1, fill=BLUE_BG, stroke=BLUE_DARK, sw=1.5, rx=6))
    p.append(text(bx + 75, y1 + 35, "1. Скид (POR)", size=12, bold=True, color=BLUE_DARK))
    p.append(text(bx + 75, y1 + 65, "Reset_Handler", size=11, color=MUTED))

    p.append(arrow(bx + 150, y1 + 50, bx + 185, y1 + 50, color=LINE, sw=2.0))

    # POST блок
    post_w = 420
    p.append(rect(bx + 185, y1 + 10, post_w, h1 - 20, fill=PURPLE_BG, stroke=PURPLE_DK, sw=1.8, rx=6))
    p.append(text(bx + 185 + post_w / 2, y1 + 35, "POST (до ініціалізації середовища C / .bss / .data)", size=12, bold=True, color=PURPLE_DK))
    p.append(mtext(bx + 185 + post_w / 2, y1 + 58, "• Тест регістрів CPU (R0-R12, SP, LR, xPSR)  • Повний тест RAM (March C-)\n• Перевірка Flash CRC-32  • Тест тактування та сторожового таймера", size=10.5, color=INK))

    p.append(arrow(bx + 185 + post_w, y1 + 50, bx + 645, y1 + 50, color=LINE, sw=2.0))

    # С-ініціалізація
    p.append(rect(bx + 645, y1 + 15, 115, h1 - 30, fill=SAFE_BG, stroke=SAFE_GREEN, sw=1.5, rx=6))
    p.append(mtext(bx + 645 + 57, y1 + 45, "C-Init:\n.bss / .data", size=11, bold=True, color=SAFE_GREEN))

    # Перехід до робочого циклу
    p.append(arrow(bx + 702, y1 + h1, bx + 702, y1 + h1 + 40, color=LINE, sw=2.0))

    # Фаза 2: Робочий цикл (Super-loop / RTOS) та фонові слайси BIST
    y2 = y1 + h1 + 45
    h2 = 180
    p.append(rect(bx, y2, bw, h2, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(bx + 20, y2 + 25, "2. Робочий цикл (Runtime): періодичний неруйнівний нагляд", size=12.5, bold=True, color=BLUE_DARK, anchor="start"))

    # Блоки циклу
    steps = [
        ("Читання\nдавачів", "#eaf2f8", BLUE_DARK),
        ("Логіка\nкерування", "#eaf2f8", BLUE_DARK),
        ("Квант BIST\n(RAM-зріз)", WARN_BG, WARN_AMBER),
        ("Квант BIST\n(Flash CRC)", WARN_BG, WARN_AMBER),
        ("Тест\nтакту", WARN_BG, WARN_AMBER),
        ("Годування\nWDT", SAFE_BG, SAFE_GREEN),
        ("Керування\nприводами", "#eaf2f8", BLUE_DARK)
    ]

    sx = bx + 25
    step_w = 95
    step_gap = 12
    for i, (label, fill, col) in enumerate(steps):
        cur_x = sx + i * (step_w + step_gap)
        p.append(rect(cur_x, y2 + 45, step_w, 75, fill=fill, stroke=col, sw=1.5, rx=4))
        p.append(mtext(cur_x + step_w / 2, y2 + 80, label, size=10.5, bold=True, color=col))
        if i < len(steps) - 1:
            p.append(arrow(cur_x + step_w, y2 + 82, cur_x + step_w + step_gap, y2 + 82, color=LINE, sw=1.5))

    # Зворотна стрілка циклу
    last_x = sx + (len(steps) - 1) * (step_w + step_gap) + step_w / 2
    p.append(line(last_x, y2 + 120, last_x, y2 + 145, color=LINE, sw=1.5))
    p.append(line(last_x, y2 + 145, sx + step_w / 2, y2 + 145, color=LINE, sw=1.5))
    p.append(arrow(sx + step_w / 2, y2 + 145, sx + step_w / 2, y2 + 120, color=LINE, sw=1.5))
    p.append(text(W / 2, y2 + 162, "Повторення кожного циклу (зрізи RAM та Flash послідовно просуваються)", size=10, italic=True, color=MUTED))

    # Гілка аварії в Safe State
    p.append(line(bx + 420, y2 + 45, bx + 420, y2 - 10, color=CRIT_RED, sw=1.8, dash="4,4"))
    p.append(arrow(bx + 420, y2 - 10, bx + 420, y2 - 25, color=CRIT_RED, sw=1.8))
    p.append(rect(bx + 300, y2 - 40, 240, 26, fill=CRIT_BG, stroke=CRIT_RED, sw=1.5, rx=4))
    p.append(text(bx + 420, y2 - 23, "Помилка тесту → Safe State (вимикання)", size=10.5, bold=True, color=CRIT_RED))

    # Підсумок знизу
    p.append(text(W / 2, H - 20, "POST перевіряє залізо на 100% при включенні; BIST контролює його малими порціями під час роботи", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "post-vs-runtime-timeline.svg"), W, H, *p,
           title="Життєвий цикл самотестування: POST та BIST")


# ── 3. march-c-phases: фази алгоритму March C- ──────────────────────────────
def fig_march_c():
    W, H = 840, 460
    p = []

    p.append(text(W / 2, 26, "Алгоритм March C- для тестування ОЗП (6 фаз, складність 10N)", size=15, bold=True))

    phases = [
        ("M0: ⇕ (w0)", "Ініціалізація", "Запис 0 в усі комірки ОЗП у довільному порядку", "#f2f4f4", MUTED, "w0"),
        ("M1: ⇑ (r0, w1)", "Висхідний 0→1", "Зчитуємо 0 (перевірка), записуємо 1 (інверсія)", BLUE_BG, BLUE_DARK, "r0 → w1"),
        ("M2: ⇑ (r1, w0)", "Висхідний 1→0", "Зчитуємо 1 (перевірка), записуємо 0 (інверсія)", BLUE_BG, BLUE_DARK, "r1 → w0"),
        ("M3: ⇓ (r0, w1)", "Низхідний 0→1", "Зчитуємо 0 (перевірка), записуємо 1 (інверсія)", PURPLE_BG, PURPLE_DK, "r0 → w1"),
        ("M4: ⇓ (r1, w0)", "Низхідний 1→0", "Зчитуємо 1 (перевірка), записуємо 0 (інверсія)", PURPLE_BG, PURPLE_DK, "r1 → w0"),
        ("M5: ⇕ (r0)", "Фінальне читання", "Перевірка збереження 0 у всіх комірках", SAFE_BG, SAFE_GREEN, "r0")
    ]

    bx = 40
    bw = W - 2 * bx
    top_y = 55
    card_h = 52
    gap = 12

    for i, (title_str, sub_str, desc_str, bg_col, stroke_col, op_str) in enumerate(phases):
        y = top_y + i * (card_h + gap)
        p.append(rect(bx, y, bw, card_h, fill=bg_col, stroke=stroke_col, sw=1.5, rx=5))

        # Іконка/номер
        p.append(rect(bx + 10, y + 8, 140, card_h - 16, fill="#ffffff", stroke=stroke_col, sw=1.2, rx=3))
        p.append(text(bx + 80, y + 26, title_str, size=11.5, bold=True, color=stroke_col))

        # Опис напрямку та операцій
        p.append(text(bx + 175, y + 20, sub_str, size=11, bold=True, color=INK, anchor="start"))
        p.append(text(bx + 175, y + 38, desc_str, size=10, color=MUTED, anchor="start"))

        # Операційний бейдж праворуч
        p.append(rect(bx + bw - 110, y + 10, 95, card_h - 20, fill="#ffffff", stroke=stroke_col, sw=1.2, rx=4))
        p.append(text(bx + bw - 62, y + 26, op_str, size=11, bold=True, color=stroke_col))

    # Легенда покриття дефектів знизу
    by = top_y + 6 * (card_h + gap) + 5
    p.append(rect(bx, by, bw, 52, fill="#fdfefe", stroke=LINE, sw=1.2, rx=5))
    p.append(text(W / 2, by + 18, "Модель виявлення дефектів пам'яті алгоритмом March C-:", size=11, bold=True, color=INK))
    p.append(text(W / 2, by + 36, "• Залипання (SAF)  • Дефекти переходів (TF)  • Дефекти адресації (AF)  • Взаємний вплив комірок (CFin / CFid)", size=10.5, color=SAFE_GREEN, bold=True))

    render(os.path.join(OUT, "march-c-phases.svg"), W, H, *p,
           title="Фази алгоритму March C-")


# ── 4. clock-cross-check: перехресна перевірка тактових генераторів ──────────
def fig_clock_check():
    W, H = 840, 460
    p = []

    p.append(text(W / 2, 26, "Перехресна перевірка тактування (Clock Plausibility via Cross-Checking)", size=15, bold=True))

    # Джерело 1: Головний генератор (HSE / PLL)
    x1, y1, gw, gh = 50, 65, 220, 110
    p.append(rect(x1, y1, gw, gh, fill=BLUE_BG, stroke=BLUE_DARK, sw=1.8, rx=6))
    p.append(text(x1 + gw / 2, y1 + 30, "Основний тактовий домен", size=12, bold=True, color=BLUE_DARK))
    p.append(mtext(x1 + gw / 2, y1 + 60, "HSE (кварцовий резонатор)\n+ PLL (наприклад, 168 МГц)\nТактує ядро та таймер TIM_A", size=10.5, color=INK))

    # Джерело 2: Незалежний генератор (LSI / LSE)
    x2, y2 = 50, 215
    p.append(rect(x2, y2, gw, gh, fill=PURPLE_BG, stroke=PURPLE_DK, sw=1.8, rx=6))
    p.append(text(x2 + gw / 2, y2 + 30, "Допоміжне джерело (LSI / RTC)", size=12, bold=True, color=PURPLE_DK))
    p.append(mtext(x2 + gw / 2, y2 + 60, "Внутрішній RC (LSI ~32 кГц)\nабо годинниковий кварц LSE\nФізично незалежне живлення", size=10.5, color=INK))

    # Центральний вузол: Вхідне захоплення таймера (Timer Input Capture)
    cx, cy, cw, ch = 330, 110, 230, 170
    p.append(rect(cx, cy, cw, ch, fill="#fcfcfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(cx + cw / 2, cy + 30, "Вузол вимірювання (TIM_IC)", size=12.5, bold=True, color=INK))
    p.append(mtext(cx + cw / 2, cy + 65, "Таймер TIM_A рахує на частоті PLL.\nСигнал від LSI подається на канал\nвхідного захоплення (Input Capture).\nВимірюється кількість тактів PLL\nміж двома фронтами LSI.", size=10.5, color=MUTED))

    # Стрілки від джерел до вимірювача
    p.append(arrow(x1 + gw, y1 + gh / 2, cx, cy + 40, color=BLUE_DARK, sw=2.0))
    p.append(text(x1 + gw + 25, y1 + gh / 2 - 10, "f_main", size=11, bold=True, color=BLUE_DARK))

    p.append(arrow(x2 + gw, y2 + gh / 2, cx, cy + 120, color=PURPLE_DK, sw=2.0))
    p.append(text(x2 + gw + 25, y2 + gh / 2 + 18, "f_ref", size=11, bold=True, color=PURPLE_DK))

    # Блок прийняття рішення праворуч
    rx, ry, rw, rh = 610, 110, 185, 170
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=WARN_AMBER, sw=1.8, rx=8))
    p.append(text(rx + rw / 2, ry + 30, "Верифікація вікна", size=12, bold=True, color=WARN_AMBER))
    p.append(mtext(rx + rw / 2, ry + 65, "N_actual = T_ref / T_main\nОчікувано: N_nom ± ΔN\n(допуск, наприклад, ±5%)\n\nN_min ≤ N_actual ≤ N_max", size=10.5, color=INK))

    p.append(arrow(cx + cw, cy + ch / 2, rx, ry + rh / 2, color=LINE, sw=2.0))

    # Виходи результату
    oy1 = 330
    p.append(rect(200, oy1, 200, 50, fill=SAFE_BG, stroke=SAFE_GREEN, sw=1.5, rx=5))
    p.append(mtext(300, oy1 + 22, "В межах норми\n→ Дозвіл роботи / WDT", size=11, bold=True, color=SAFE_GREEN))

    p.append(rect(480, oy1, 220, 50, fill=CRIT_BG, stroke=CRIT_RED, sw=1.5, rx=5))
    p.append(mtext(590, oy1 + 22, "Вихід за межі вікна\n→ Відмова такту → Safe State", size=11, bold=True, color=CRIT_RED))

    p.append(arrow(rx + rw / 2 - 20, ry + rh, 300, oy1, color=SAFE_GREEN, sw=1.8))
    p.append(arrow(rx + rw / 2 + 20, ry + rh, 590, oy1, color=CRIT_RED, sw=1.8))

    # Нижній підпис
    p.append(text(W / 2, H - 20, "Якщо головний кварц розколовся або PLL зірвався, таймер зафіксує аномалію ще до виходу з ладу логіки", size=11, italic=True, color=MUTED))

    render(os.path.join(OUT, "clock-cross-check.svg"), W, H, *p,
           title="Перехресна перевірка частоти тактування")


if __name__ == "__main__":
    fig_safety_standards()
    fig_post_timeline()
    fig_march_c()
    fig_clock_check()
    print("All figures generated successfully.")
