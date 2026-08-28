# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. HSI vs HSE: Чому перший запуск роблять від внутрішнього RC-генератора ──
def fig_hsi_vs_hse():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 32, "Тактування при першому запуску: внутрішній RC (HSI) проти зовнішнього кварцу (HSE)", size=16, color=INK, bold=True))

    # Лівий блок: HSI (Надійний мінімальний старт)
    lx, ly, lw, lh = 40, 65, 410, 390
    p.append(rect(lx, ly, lw, lh, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(lx + lw / 2, ly + 28, "Внутрішній генератор HSI / FIRC (16 МГц)", size=14, color=FIELD, bold=True))
    p.append(text(lx + lw / 2, ly + 46, "Працює одразу після скидання (Reset за замовчуванням)", size=11, color=MUTED))

    # Схема HSI всередині кремнію
    p.append(rect(lx + 25, ly + 65, lw - 50, 135, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(lx + lw / 2, ly + 88, "КРЕМНІЄВИЙ КРИСТАЛ МІКРОКОНТРОЛЕРА", size=10, color=MUTED, bold=True))

    # Внутрішній RC блок
    p.append(rect(lx + 45, ly + 105, 140, 75, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(lx + 115, ly + 133, "Інтегрований", size=11, color=FIELD, bold=True))
    p.append(text(lx + 115, ly + 150, "RC-генератор", size=11, color=FIELD, bold=True))
    p.append(text(lx + 115, ly + 167, "16 МГц ±1%", size=10, color=MUTED))

    p.append(arrow(lx + 185, ly + 142, lx + 235, ly + 142, color=FIELD, sw=2))

    # Системний мультиплексор
    p.append(rect(lx + 235, ly + 115, 125, 55, fill="#f8fafc", stroke=LINE, sw=1.2, rx=4))
    p.append(text(lx + 297, ly + 138, "SYSCLK Mux", size=11, color=INK, bold=True))
    p.append(text(lx + 297, ly + 155, "Ядро процесора", size=10, color=MUTED))

    # Переваги HSI
    hsi_points = [
        ("Нуль зовнішніх деталей:", "Не залежить від пайки обв'язки на платі."),
        ("Миттєвий запуск:", "Готовий до тактування за лічені мікросекунди."),
        ("Неможливо зависнути:", "Не блокує шину в очікуванні біта готовності."),
        ("Діагностична опора:", "Якщо прошивка не блимає — це код або живлення."),
    ]
    cur_y = ly + 215
    for title, desc in hsi_points:
        p.append(text(lx + 30, cur_y, title, size=11, color=FIELD, bold=True, anchor="start"))
        p.append(text(lx + 30, cur_y + 16, desc, size=10.5, color=INK, anchor="start"))
        cur_y += 40

    # Правий блок: HSE + PLL (Ризикований старт)
    rx_b, ry_b, rw, rh = 490, 65, 410, 390
    p.append(rect(rx_b, ry_b, rw, rh, fill="#fef2f2", stroke=POS, sw=2, rx=8))
    p.append(text(rx_b + rw / 2, ry_b + 28, "Зовнішній кварц HSE + PLL (8–168 МГц)", size=14, color=POS, bold=True))
    p.append(text(rx_b + rw / 2, ry_b + 46, "Потребує робочої аналогової обв'язки та налаштування", size=11, color=MUTED))

    # Схема HSE з платою
    p.append(rect(rx_b + 25, ry_b + 65, rw - 50, 135, fill="#ffffff", stroke=POS, sw=1.2, rx=6))

    # Кварц і конденсатори на платі
    p.append(rect(rx_b + 40, ry_b + 95, 95, 45, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(rx_b + 87, ry_b + 115, "Кварц XTAL", size=10.5, color=POS, bold=True))
    p.append(text(rx_b + 87, ry_b + 130, "CL1, CL2, флюс", size=9.5, color=MUTED))

    p.append(line(rx_b + 135, ry_b + 110, rx_b + 175, ry_b + 110, color=POS, sw=1.5))
    p.append(line(rx_b + 135, ry_b + 125, rx_b + 175, ry_b + 125, color=POS, sw=1.5))
    p.append(text(rx_b + 155, ry_b + 102, "OSC", size=9, color=MUTED))

    # Інвертор Пірса в МК
    p.append(rect(rx_b + 175, ry_b + 95, 80, 45, fill="#fff", stroke=LINE, sw=1.2, rx=4))
    p.append(text(rx_b + 215, ry_b + 115, "Генератор", size=10, color=INK, bold=True))
    p.append(text(rx_b + 215, ry_b + 130, "Пірса", size=9.5, color=MUTED))

    p.append(arrow(rx_b + 255, ry_b + 117, rx_b + 285, ry_b + 117, color=POS, sw=1.5))

    # Блок PLL
    p.append(rect(rx_b + 285, ry_b + 95, 85, 45, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(rx_b + 327, ry_b + 115, "Блок PLL", size=10, color=POS, bold=True))
    p.append(text(rx_b + 327, ry_b + 130, "Flash Latency", size=9, color=MUTED))

    p.append(text(rx_b + rw / 2, ry_b + 182, "Зависання в циклі: while(!(RCC->CR & RCC_CR_HSERDY));", size=10, color=POS, bold=True))

    # Ризики HSE на новій платі
    hse_risks = [
        ("Непропай або мікротріщина:", "Кварц не генерує коливання — чип зависає наглухо."),
        ("Помилка номіналу ємностей:", "Неправильні CL1/CL2 зривають генерацію або зміщують частоту."),
        ("Паразитний опір флюсу:", "Залишки флюсу шунтують високоомний вхід генератора."),
        ("Помилка дільників PLL:", "Перевищення частоти шини призводить до HardFault ядра."),
    ]
    cur_y = ry_b + 215
    for title, desc in hse_risks:
        p.append(text(rx_b + 30, cur_y, title, size=11, color=POS, bold=True, anchor="start"))
        p.append(text(rx_b + 30, cur_y + 16, desc, size=10.5, color=INK, anchor="start"))
        cur_y += 40

    render(os.path.join(OUT, "hsi-vs-hse-startup.svg"), W, H, *p)


# ── 2. Active High проти Active Low: Фізика та струми ────────────────────────
def fig_led_topologies():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 32, "Схеми підключення світлодіода: Active High (Source) проти Active Low (Sink)", size=16, color=INK, bold=True))

    # Ліва схема: Active High
    ax, ay, aw, ah = 40, 65, 415, 395
    p.append(rect(ax, ay, aw, ah, fill="#f8fafc", stroke=FIELD, sw=2, rx=8))
    p.append(text(ax + aw / 2, ay + 28, "Active High: Витікаючий струм (Source)", size=14, color=FIELD, bold=True))
    p.append(text(ax + aw / 2, ay + 46, "Логічна «1» (3.3 В) запалює світлодіод", size=11, color=MUTED))

    # Блок виходу МК
    p.append(rect(ax + 25, ay + 65, 140, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(ax + 95, ay + 88, "GPIO Push-Pull", size=11, color=INK, bold=True))

    # Верхній ключ PMOS
    p.append(rect(ax + 45, ay + 105, 100, 35, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(ax + 95, ay + 122, "PMOS (ВКЛ)", size=10.5, color=FIELD, bold=True))
    p.append(text(ax + 95, ay + 134, "до VDD (+3.3V)", size=9, color=MUTED))

    # Нижній ключ NMOS
    p.append(rect(ax + 45, ay + 165, 100, 35, fill="#f1f5f9", stroke=MUTED, sw=1, rx=4))
    p.append(text(ax + 95, ay + 182, "NMOS (ВИМК)", size=10.5, color=MUTED))
    p.append(text(ax + 95, ay + 194, "до GND (0V)", size=9, color=MUTED))

    # Лінія з піна назовні
    p.append(line(ax + 145, ay + 122, ax + 200, ay + 122, color=POS, sw=2.5))
    p.append(text(ax + 175, ay + 112, "PIN", size=10, color=POS, bold=True))

    # Світлодіод та резистор
    p.append(rect(ax + 200, ay + 102, 70, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(ax + 235, ay + 121, "LED (D1)", size=10.5, color=POS, bold=True))
    p.append(text(ax + 235, ay + 135, "VF ≈ 2.0V", size=9, color=MUTED))

    p.append(line(ax + 270, ay + 122, ax + 295, ay + 122, color=POS, sw=2))

    p.append(rect(ax + 295, ay + 107, 65, 30, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(ax + 327, ay + 126, "R = 330 Ω", size=10, color=INK, bold=True))

    p.append(line(ax + 360, ay + 122, ax + 385, ay + 122, color=LINE, sw=2))
    p.append(line(ax + 385, ay + 112, ax + 385, ay + 132, color=LINE, sw=2.5))
    p.append(text(ax + 385, ay + 146, "GND", size=10, color=MUTED, bold=True))

    # Стрілка струму
    p.append(arrow(ax + 170, ay + 155, ax + 340, ay + 155, color=POS, sw=2))
    p.append(text(ax + 255, ay + 172, "Струм I_source = (3.3V - 2.0V) / 330Ω ≈ 4.0 мА", size=10.5, color=POS, bold=True))

    # Опис поведінки Active High
    ah_notes = [
        ("Пряма логіка в коді:", "1 = LED ON, 0 = LED OFF — інтуїтивно зрозуміло."),
        ("Стан при скиданні (Reset):", "Пін у Hi-Z (вхід). Світлодіод надійно згаслий."),
        ("Струмове навантаження:", "Струм береться з шини живлення VDD мікроконтролера."),
    ]
    cur_y = ay + 245
    for title, desc in ah_notes:
        p.append(text(ax + 25, cur_y, title, size=11, color=FIELD, bold=True, anchor="start"))
        p.append(text(ax + 25, cur_y + 16, desc, size=10.5, color=INK, anchor="start"))
        cur_y += 44

    # Права схема: Active Low
    bx, by, bw, bh = 485, 65, 415, 395
    p.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=NEG, sw=2, rx=8))
    p.append(text(bx + bw / 2, by + 28, "Active Low: Втікаючий струм (Sink)", size=14, color=NEG, bold=True))
    p.append(text(bx + bw / 2, by + 46, "Логічний «0» (0 В) запалює світлодіод", size=11, color=MUTED))

    # Лінія живлення VCC
    p.append(line(bx + 35, by + 122, bx + 60, by + 122, color=POS, sw=2))
    p.append(text(bx + 35, by + 112, "+3.3V / +5V", size=9.5, color=POS, bold=True))

    # Резистор та світлодіод
    p.append(rect(bx + 60, by + 107, 65, 30, fill="#ffffff", stroke=LINE, sw=1.5, rx=2))
    p.append(text(bx + 92, by + 126, "R = 330 Ω", size=10, color=INK, bold=True))

    p.append(line(bx + 125, by + 122, bx + 150, by + 122, color=POS, sw=2))

    p.append(rect(bx + 150, by + 102, 70, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(bx + 185, by + 121, "LED (D1)", size=10.5, color=POS, bold=True))
    p.append(text(bx + 185, by + 135, "Анод -> Катод", size=9, color=MUTED))

    p.append(line(bx + 220, by + 122, bx + 265, by + 122, color=NEG, sw=2.5))
    p.append(text(bx + 242, by + 112, "PIN", size=10, color=NEG, bold=True))

    # Блок виходу МК для Sink
    p.append(rect(bx + 265, by + 65, 125, 160, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(bx + 327, by + 88, "GPIO Драйвер", size=11, color=INK, bold=True))

    # Верхній ключ PMOS (Вимкнено)
    p.append(rect(bx + 275, by + 105, 105, 35, fill="#f1f5f9", stroke=MUTED, sw=1, rx=4))
    p.append(text(bx + 327, by + 122, "PMOS (ВИМК)", size=10.5, color=MUTED))
    p.append(text(bx + 327, by + 134, "до VDD", size=9, color=MUTED))

    # Нижній ключ NMOS (Ввімкнено)
    p.append(rect(bx + 275, by + 165, 105, 35, fill="#dbeafe", stroke=NEG, sw=1.2, rx=4))
    p.append(text(bx + 327, by + 182, "NMOS (ВКЛ -> 0V)", size=10.5, color=NEG, bold=True))
    p.append(text(bx + 327, by + 194, "притягує до GND", size=9, color=MUTED))

    # Стрілка струму (втікає)
    p.append(arrow(bx + 60, by + 155, bx + 265, by + 155, color=NEG, sw=2))
    p.append(text(bx + 165, by + 172, "Струм I_sink втікає в пін МК до шини GND", size=10.5, color=NEG, bold=True))

    # Опис поведінки Active Low
    al_notes = [
        ("Інверсна логіка в коді:", "0 = LED ON, 1 = LED OFF — треба пам'ятати при написанні."),
        ("Більша навантажувальна здатність:", "NMOS-транзистори зазвичай мають менший опір RDS(on)."),
        ("Сумісність із Open-Drain:", "Дозволяє живити світлодіод від +5 В через 5V-tolerant пін."),
    ]
    cur_y = by + 245
    for title, desc in al_notes:
        p.append(text(bx + 25, cur_y, title, size=11, color=NEG, bold=True, anchor="start"))
        p.append(text(bx + 25, cur_y + 16, desc, size=10.5, color=INK, anchor="start"))
        cur_y += 44

    render(os.path.join(OUT, "led-driving-topologies.svg"), W, H, *p)


# ── 3. Конвеєр регістрів GPIO: RCC -> MODER -> BSRR -> Фізичний пін ───────────
def fig_gpio_registers():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 32, "Конвеєр прямого доступу до регістрів GPIO (на прикладі ARM Cortex-M)", size=16, color=INK, bold=True))

    # Блок 1: Тактування RCC
    b1_x, b1_y, b1_w, b1_h = 40, 75, 200, 360
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(b1_x + b1_w / 2, b1_y + 26, "1. Тактування порту", size=13, color=FIELD, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 44, "Регістр RCC_AHBxENR", size=11, color=MUTED))

    p.append(rect(b1_x + 15, b1_y + 65, b1_w - 30, 95, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(b1_x + b1_w / 2, b1_y + 88, "Біт GPIOCEN = 1", size=12, color=FIELD, bold=True))
    p.append(text(b1_x + b1_w / 2, b1_y + 110, "Подає такт від шини", size=10, color=INK))
    p.append(text(b1_x + b1_w / 2, b1_y + 128, "AHB на блок логіки", size=10, color=INK))
    p.append(text(b1_x + b1_w / 2, b1_y + 146, "порту GPIO", size=10, color=MUTED))

    p.append(rect(b1_x + 15, b1_y + 175, b1_w - 30, 155, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    p.append(text(b1_x + 25, b1_y + 195, "Чому це критично:", size=11, color=POS, bold=True, anchor="start"))
    p.append(mtext(b1_x + 25, b1_y + 215, [
        "За замовчуванням тактування",
        "всіх портів ВИМКНЕНО для",
        "економії енергії.",
        "Спроба запису в регістри",
        "без такту викликає BusFault",
        "або операція ігнорується."
    ], size=10, color=INK, anchor="start", lh=1.35))

    p.append(arrow(b1_x + b1_w, b1_y + 112, b1_x + b1_w + 35, b1_y + 112, color=FIELD, sw=2.5))

    # Блок 2: Налаштування режиму (MODER, OSPEEDR, OTYPER)
    b2_x, b2_y, b2_w, b2_h = 275, 75, 200, 360
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(text(b2_x + b2_w / 2, b2_y + 26, "2. Конфігурація піна", size=13, color=NEG, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 44, "Регістри MODER / OTYPER", size=11, color=MUTED))

    p.append(rect(b2_x + 15, b2_y + 65, b2_w - 30, 115, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(b2_x + b2_w / 2, b2_y + 88, "GPIOx_MODER", size=12, color=NEG, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 108, "00: Вхід (Input/Hi-Z)", size=10, color=MUTED))
    p.append(text(b2_x + b2_w / 2, b2_y + 126, "01: Вихід (Output GP)", size=10.5, color=FIELD, bold=True))
    p.append(text(b2_x + b2_w / 2, b2_y + 144, "10: Альтернативна AF", size=10, color=MUTED))
    p.append(text(b2_x + b2_w / 2, b2_y + 162, "11: Аналоговий режим", size=10, color=MUTED))

    p.append(rect(b2_x + 15, b2_y + 195, b2_w - 30, 135, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    p.append(text(b2_x + 25, b2_y + 215, "Додаткові регістри:", size=11, color=INK, bold=True, anchor="start"))
    p.append(mtext(b2_x + 25, b2_y + 235, [
        "OTYPER: Push-Pull (0)",
        "або Open-Drain (1).",
        "OSPEEDR: Low Speed (00)",
        "— зменшує завади на шині",
        "живлення при перемиканні."
    ], size=10, color=INK, anchor="start", lh=1.35))

    p.append(arrow(b2_x + b2_w, b2_y + 122, b2_x + b2_w + 35, b2_y + 122, color=NEG, sw=2.5))

    # Блок 3: Атомарне керування BSRR / ODR
    b3_x, b3_y, b3_w, b3_h = 510, 75, 200, 360
    p.append(rect(b3_x, b3_y, b3_w, b3_h, fill="#faf5ff", stroke="#7c3aed", sw=2, rx=8))
    p.append(text(b3_x + b3_w / 2, b3_y + 26, "3. Атомарне перемикання", size=13, color="#7c3aed", bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 44, "Регістр BSRR (Set / Reset)", size=11, color=MUTED))

    p.append(rect(b3_x + 15, b3_y + 65, b3_w - 30, 115, fill="#ffffff", stroke="#7c3aed", sw=1.2, rx=6))
    p.append(text(b3_x + b3_w / 2, b3_y + 88, "BSRR[31:16] - Скидання (0)", size=10.5, color=POS, bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 106, "Запис '1' -> Вихід = 0", size=10, color=MUTED))
    p.append(text(b3_x + b3_w / 2, b3_y + 132, "BSRR[15:0] - Встановлення (1)", size=10.5, color=FIELD, bold=True))
    p.append(text(b3_x + b3_w / 2, b3_y + 150, "Запис '1' -> Вихід = 1", size=10, color=MUTED))
    p.append(text(b3_x + b3_w / 2, b3_y + 168, "Запис '0' -> Немає дії", size=9.5, color=MUTED))

    p.append(rect(b3_x + 15, b3_y + 195, b3_w - 30, 135, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    p.append(text(b3_x + 25, b3_y + 215, "Чому BSRR, а не ODR:", size=11, color="#7c3aed", bold=True, anchor="start"))
    p.append(mtext(b3_x + 25, b3_y + 235, [
        "ODR |= (1<<pin) робить",
        "Read-Modify-Write (3 такти).",
        "Переривання може змінити",
        "інший пін під час RMW.",
        "BSRR змінює пін за 1 такт",
        "без конфліктів шини."
    ], size=10, color=INK, anchor="start", lh=1.35))

    p.append(arrow(b3_x + b3_w, b3_y + 130, b3_x + b3_w + 35, b3_y + 130, color="#7c3aed", sw=2.5))

    # Блок 4: Фізичний каскад виходу
    b4_x, b4_y, b4_w, b4_h = 745, 75, 160, 360
    p.append(rect(b4_x, b4_y, b4_w, b4_h, fill="#fffbeb", stroke="#d97706", sw=2, rx=8))
    p.append(text(b4_x + b4_w / 2, b4_y + 26, "4. Фізичний пін", size=13, color="#d97706", bold=True))
    p.append(text(b4_x + b4_w / 2, b4_y + 44, "Драйвер виводу", size=11, color=MUTED))

    p.append(rect(b4_x + 15, b4_y + 75, b4_w - 30, 75, fill="#ffffff", stroke="#d97706", sw=1.2, rx=6))
    p.append(text(b4_x + b4_w / 2, b4_y + 102, "Push-Pull", size=11, color=INK, bold=True))
    p.append(text(b4_x + b4_w / 2, b4_y + 122, "Каскад FETs", size=10.5, color=MUTED))

    p.append(line(b4_x + b4_w / 2, b4_y + 150, b4_x + b4_w / 2, b4_y + 185, color=LINE, sw=2))

    # Металевий пін мікроконтролера
    p.append(rect(b4_x + 25, b4_y + 185, b4_w - 50, 45, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    p.append(text(b4_x + b4_w / 2, b4_y + 212, "PAD / PIN (QFP/BGA)", size=10, color=INK, bold=True))

    p.append(arrow(b4_x + b4_w / 2, b4_y + 230, b4_x + b4_w / 2, b4_y + 265, color=POS, sw=2.5))

    p.append(rect(b4_x + 20, b4_y + 265, b4_w - 40, 55, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    p.append(text(b4_x + b4_w / 2, b4_y + 288, "Світлодіод D1", size=11, color=POS, bold=True))
    p.append(text(b4_x + b4_w / 2, b4_y + 306, "Блимання 1 Гц", size=10, color=MUTED))

    render(os.path.join(OUT, "gpio-register-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_hsi_vs_hse()
    fig_led_topologies()
    fig_gpio_registers()
    print("OK: generated 3 figures in ->", OUT)
