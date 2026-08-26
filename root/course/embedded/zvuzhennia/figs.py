# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. bisection-tree: Дерево половинного поділу простору пошуку ─────────────
def fig_bisection_tree():
    W, H = 880, 400
    p = []

    # Колонка ентропії ліворуч (x: 25..175)
    p.append(rect(25, 25, 155, 350, fill="#f9fafb", stroke="#d1d5db", sw=1.2, rx=8))
    p.append(text(102, 55, "ІНФОРМАЦІЯ", size=12, bold=True, color=INK))
    p.append(text(102, 78, "I = log₂(N / N_нов)", size=10.5, color=NEG, bold=True))
    p.append(line(35, 92, 170, 92, color="#e5e7eb", sw=1.0))
    p.append(text(102, 120, "1 тест 50/50:", size=10.5, bold=True, color=INK))
    p.append(text(102, 138, "+1.00 біт", size=11, color=FIELD, bold=True))
    p.append(line(35, 155, 170, 155, color="#e5e7eb", sw=1.0))
    p.append(text(102, 180, "10 тестів:", size=10.5, bold=True, color=INK))
    p.append(text(102, 198, "10.00 бітів", size=11, color=FIELD, bold=True))
    p.append(line(35, 215, 170, 215, color="#e5e7eb", sw=1.0))
    p.append(text(102, 245, "Лінійний перебір:", size=10, color=MUTED, bold=True))
    p.append(text(102, 265, "до 1000 спроб", size=10, color=POS, bold=True))
    p.append(line(35, 280, 170, 280, color="#e5e7eb", sw=1.0))
    p.append(text(102, 310, "Бісекція:", size=10, color=MUTED, bold=True))
    p.append(text(102, 330, "рівно 10 кроків", size=10.5, color=FIELD, bold=True))

    cx = 530
    bw = 360

    # Крок 0
    b0, w0, h0 = textbox(cx, 45, "ПРОСТІР ПОШУКУ: N = 1000\n1000 рядків коду або 40 компонентів",
                         size=12, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6, min_w=bw)
    p.append(b0)

    # Крок 1 (два блоки по 500)
    y1 = 125
    b1_l, _, _ = textbox(cx - 165, y1, "Блок A: 1..500 [OK]\n(Виключаємо 50%)",
                         size=11, bold=True, color=MUTED, fill="#f4f6f8", stroke="#cfd6dd", sw=1.2, min_w=190)
    b1_r, _, _ = textbox(cx + 165, y1, "Блок B: 501..1000 [ЗБІЙ]\n(Дефект тут: N = 500)",
                         size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.6, min_w=190)
    p.append(arrow(cx, 45 + h0/2, cx - 165, y1 - 22, color=MUTED, sw=1.4))
    p.append(arrow(cx, 45 + h0/2, cx + 165, y1 - 22, color=POS, sw=2.0))
    p.append(b1_l); p.append(b1_r)

    # Крок 2 (розсічення блоку B на 250)
    y2 = 205
    b2_l, _, _ = textbox(cx + 65, y2, "B1: 501..750 [ЗБІЙ]\n(N = 250)",
                         size=10.5, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.5, min_w=145)
    b2_r, _, _ = textbox(cx + 245, y2, "B2: 751..1000 [–]\n(Виключаємо)",
                         size=10.5, bold=True, color=MUTED, fill="#f4f6f8", stroke="#cfd6dd", sw=1.2, min_w=145)
    p.append(arrow(cx + 165, y1 + 22, cx + 65, y2 - 20, color=POS, sw=1.8))
    p.append(arrow(cx + 165, y1 + 22, cx + 245, y2 - 20, color=MUTED, sw=1.4))
    p.append(b2_l); p.append(b2_r)

    # Проміжні крапки до фіналу
    y3 = 275
    p.append(text(cx + 65, y3 - 5, "⋮   log₂(1000) ≈ 9.96 кроків   ⋮", size=11, color=INK, bold=True, italic=True))
    p.append(arrow(cx + 65, y3 + 8, cx + 65, y3 + 40, color=FIELD, sw=2.0))

    # Фінал: Крок 10
    y4 = 345
    bf, wf, hf = textbox(cx + 65, y4, "КРОК 10: N = 1\nТочний дефект (рядок або чип) знайдено за 10 тестів",
                         size=11.5, bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=2.0, min_w=340)
    p.append(bf)

    render(os.path.join(OUT, "bisection-tree.svg"), W, H, *p,
           title="Дерево дихотомічного пошуку несправності")


# ── 2. hw-isolation-bus: Схема апаратної ізоляції живлення та шин ───────────
def fig_hw_isolation_bus():
    W, H = 840, 360
    p = []

    # Мікроконтролер (MCU / Master)
    bmcu, wm, hm = textbox(110, 170, "ГОЛОВНИЙ MCU\n(Майстер I2C / SPI)\nЖивлення 3.3 В",
                           size=11.5, bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=150)
    p.append(bmcu)

    # Шини від MCU
    # Живлення VCC
    p.append(line(185, 120, 320, 120, color=POS, sw=2.5))
    p.append(text(250, 110, "VCC (3.3 В)", size=10.5, color=POS, bold=True))

    # Шина I2C (SDA/SCL)
    p.append(line(185, 170, 320, 170, color=INK, sw=2.0))
    p.append(text(250, 160, "I2C (SDA / SCL)", size=10.5, color=INK, bold=True))

    # Секція 1 (Ліва половина плати)
    p.append(rect(320, 45, 160, 250, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(400, 65, "Група A (Сенсори)", size=11, bold=True, color=INK))

    b_sens1, _, _ = textbox(400, 120, "Давач 1 (IMU)\n0x68", size=10, bold=True,
                            color=INK, fill=BG, stroke="#94a3b8", sw=1.2, min_w=120)
    b_sens2, _, _ = textbox(400, 220, "Давач 2 (Баро)\n0x76", size=10, bold=True,
                            color=INK, fill=BG, stroke="#94a3b8", sw=1.2, min_w=120)
    p.append(b_sens1); p.append(b_sens2)
    p.append(line(320, 120, 340, 120, color=POS, sw=2.0))
    p.append(line(320, 170, 340, 170, color=INK, sw=1.8))
    p.append(line(340, 170, 340, 220, color=INK, sw=1.8))
    p.append(line(340, 220, 340, 220, color=INK, sw=1.8))

    # ТОЧКА РОЗРИВУ (Центральний половинний поділ: нульовий резистор / перемичка)
    p.append(rect(500, 95, 65, 50, fill="#fdecea", stroke=POS, sw=2.0, rx=4))
    p.append(text(532, 115, "R_ZERO", size=9.5, color=POS, bold=True))
    p.append(text(532, 133, "[РОЗРИВ]", size=9, color=POS, bold=True))
    p.append(line(460, 120, 500, 120, color=POS, sw=2.0))
    p.append(line(565, 120, 600, 120, color=POS, sw=2.0, dash="3 3"))

    p.append(rect(500, 155, 65, 45, fill="#fff3e0", stroke="#e67e22", sw=1.8, rx=4))
    p.append(text(532, 175, "JP_I2C", size=9.5, color="#b9770e", bold=True))
    p.append(text(532, 190, "[МІСТОК]", size=9, color="#b9770e", bold=True))
    p.append(line(460, 170, 500, 170, color=INK, sw=1.8))
    p.append(line(565, 170, 600, 170, color=INK, sw=1.8, dash="3 3"))

    # Секція 2 (Права половина плати — тут приховане КЗ або завислий чип)
    p.append(rect(600, 45, 200, 250, fill="#fef2f2", stroke=POS, sw=1.6, rx=6))
    p.append(text(700, 65, "Група B (Зовнішній блок)", size=11, bold=True, color=POS))

    b_chip3, _, _ = textbox(700, 120, "EEPROM / Flash\n(Шина живлення)", size=10, bold=True,
                            color=INK, fill=BG, stroke="#94a3b8", sw=1.2, min_w=140)
    b_chip4, _, _ = textbox(700, 220, "Радіомодуль / Драйвер\n[ПРОБИТИЙ ЧИП: КЗ!]", size=10, bold=True,
                            color=POS, fill="#fdecea", stroke=POS, sw=1.5, min_w=160)
    p.append(b_chip3); p.append(b_chip4)

    # Висновок унизу
    p.append(text(W/2, 330, "Розмикання R_ZERO миттєво доводить: якщо MCU та Група A ожили — дефект праворуч у Групі B",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(OUT, "hw-isolation-bus.svg"), W, H, *p,
           title="Апаратний поділ шини живлення та інтерфейсів перемичками")


# ── 3. firmware-bisection-flow: Бісекція прошивки та RTOS-потоків ───────────
def fig_firmware_bisection_flow():
    W, H = 840, 370
    p = []

    # Рівні прошивки
    layers = [
        ("Рівень 4: Бізнес-логіка", 220, 60, "#eaf0fd", NEG),
        ("Рівень 3: RTOS-задачі та черги", 220, 130, "#fff3e0", "#b9770e"),
        ("Рівень 2: Драйвери периферії", 220, 200, "#eafaf0", FIELD),
        ("Рівень 1: HAL та регістри MCU", 220, 270, "#f3f4f6", INK),
    ]

    for name, cx, cy, fill, col in layers:
        b, w, h = textbox(cx, cy, name, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.5, min_w=250)
        p.append(b)
        if cy < 270:
            p.append(arrow(cx, cy + 20, cx, cy + 45, color=MUTED, sw=1.5))

    # Стовпець ізоляції праворуч
    p.append(rect(430, 30, 380, 290, fill="#f8fafc", stroke="#94a3b8", sw=1.4, rx=8))
    p.append(text(620, 55, "МЕТОД БІСЕКЦІЙНОЇ ІЗОЛЯЦІЇ", size=12, bold=True, color=INK))

    isolations = [
        (620, 95,  "1. Заглушка логіки (Fixed Data Stub)", "Перевіряє, чи не здурів обчислювальний алгоритм", "#eaf0fd", NEG),
        (620, 160, "2. Відключення 50% RTOS-потоків", "Ізолює взаємне блокування (Deadlock) і переповнення стеку", "#fff3e0", "#b9770e"),
        (620, 225, "3. Підміна драйвера на мок-сенсор", "Відділяє програмний протокол від апаратного чипа", "#eafaf0", FIELD),
        (620, 290, "4. Маскування половини NVIC IRQ", "Знаходить переривання, що завалює латентність системи", "#fdecea", POS),
    ]

    for cx, cy, title, desc, fill, col in isolations:
        p.append(rect(450, cy - 22, 340, 48, fill=fill, stroke=col, sw=1.2, rx=5))
        p.append(text(460, cy - 6, title, size=10.5, bold=True, color=col, anchor="start"))
        p.append(text(460, cy + 12, desc, size=9.5, color=MUTED, anchor="start"))

    # Стрілка поділу
    p.append(arrow(350, 165, 430, 165, color=POS, sw=2.5))
    p.append(text(390, 150, "Розсічення", size=10, bold=True, color=POS))

    p.append(text(W/2, 348, "Ізоляція шару або групи потоків усуває 50% коду з підозри за одну ітерацію тесту",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(OUT, "firmware-bisection-flow.svg"), W, H, *p,
           title="Покрокова бісекційна ізоляція шарів прошивки")


# ── 4. diagnostic-matrix: Матриця виключення гіпотез (HW vs SW) ─────────────
def fig_diagnostic_matrix():
    W, H = 840, 360
    p = []

    # Таблиця: Стовпці (Симптом, Апаратна перевірка, Програмна перевірка, Висновок)
    headers = ["Симптом збою", "Тест 1: Залізо (HW)", "Тест 2: Софт (SW)", "Діагноз / Локалізація"]
    col_w = [180, 200, 200, 200]
    x0 = 30
    y0 = 40
    row_h = 75

    # Шапка
    cur_x = x0
    for i, h in enumerate(headers):
        p.append(rect(cur_x, y0, col_w[i], 36, fill="#1e293b", stroke="#0f172a", sw=1.0, rx=4))
        p.append(text(cur_x + col_w[i]/2, y0 + 22, h, size=11, bold=True, color=BG))
        cur_x += col_w[i] + 8

    rows_data = [
        ("Шина I2C зависає наглухо",
         "Осцилограф: чи є 3.3 В на підтяжці? Розрив R0 ділить шину навпіл.",
         "GPIO Reset toggle (9 тактів SCL); перевірка таймауту в драйвері.",
         "Якщо лінія 0 В без чипів — коротке на платі; якщо після команди — завис чип.",
         "#fdecea", POS),
        ("HardFault раз на кілька годин",
         "Моніторинг VCC осцилографом: чи є просадка від передавача?",
         "MPU/Stack Canary: перевірка переповнення стеку та битого вказівника.",
         "Просадка живлення = апаратний BOR; битий вказівник = гонка в RTOS.",
         "#fff3e0", "#b9770e"),
        ("Биті дані в кадрах SPI/UART",
         "Перевірка форми фронтів (дзвін, затягнутий rise-time через ємність).",
         "Перевірка гонок буфера DMA та пріоритетів ISR у NVIC.",
         "Дзвін = відсутній резистор узгодження; зсув байтів = гонка в коді.",
         "#eafaf0", FIELD),
    ]

    for r_idx, (sym, hw_t, sw_t, diag, fill, col) in enumerate(rows_data):
        ry = y0 + 44 + r_idx * (row_h + 8)
        cx_cur = x0
        cells = [sym, hw_t, sw_t, diag]
        for c_idx, cell_text in enumerate(cells):
            w = col_w[c_idx]
            c_fill = fill if c_idx == 3 else BG
            c_stroke = col if c_idx == 3 else "#cbd5e1"
            p.append(rect(cx_cur, ry, w, row_h, fill=c_fill, stroke=c_stroke, sw=1.2, rx=4))
            words = cell_text.split()
            l1, l2, l3 = "", "", ""
            for w_item in words:
                if len(l1 + w_item) < 25 and not l2:
                    l1 += (" " if l1 else "") + w_item
                elif len(l2 + w_item) < 25 and not l3:
                    l2 += (" " if l2 else "") + w_item
                else:
                    l3 += (" " if l3 else "") + w_item

            ty = ry + (24 if not l3 else 18)
            p.append(text(cx_cur + w/2, ty, l1, size=9.5, bold=(c_idx==0 or c_idx==3), color=INK))
            if l2:
                p.append(text(cx_cur + w/2, ty + 16, l2, size=9.5, bold=(c_idx==0 or c_idx==3), color=INK))
            if l3:
                p.append(text(cx_cur + w/2, ty + 32, l3, size=9.5, bold=(c_idx==0 or c_idx==3), color=INK))
            cx_cur += w + 8

    p.append(text(W/2, 335, "Розчеплення гіпотез: один тест виключає або апаратну частину, або програмний стек",
                  size=11.5, color=INK, italic=True))

    render(os.path.join(OUT, "diagnostic-matrix.svg"), W, H, *p,
           title="Матриця діагностичного виключення гіпотез між залізом і кодом")


if __name__ == "__main__":
    fig_bisection_tree()
    fig_hw_isolation_bus()
    fig_firmware_bisection_flow()
    fig_diagnostic_matrix()
    print("All figures generated successfully in", OUT)
