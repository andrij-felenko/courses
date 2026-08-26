# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Figure 1: errata-anatomy ──────────────────────────────────────────────────
# Структура офіційного документа Errata Sheet: від ревізій до обходу
def fig_errata_anatomy():
    W, H = 760, 400
    p = []
    p.append(text(W / 2, 28, "Анатомія статті в офіційному документі Errata Sheet", size=16, bold=True))

    # Зовнішня рамка документа
    p.append(rect(40, 50, 680, 325, fill="#ffffff", stroke="#2c3e50", sw=2, rx=8))
    p.append(rect(40, 50, 680, 34, fill="#2c3e50", stroke="#2c3e50", sw=1, rx=6))
    p.append(text(380, 72, "STM32F103xC/D/E Errata Sheet — Розділ 2.14: Периферійний модуль I2C", size=13, color="#ffffff", bold=True))

    # Секція 1: Ідентифікатор та Назва дефекту
    p.append(rect(60, 100, 640, 48, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=4))
    p.append(text(75, 122, "2.14.7", size=13, color=POS, bold=True, anchor="start"))
    p.append(text(130, 122, "Хибне спрацьовування аналогового фільтра блокує генерацію тактування", size=13, color=INK, bold=True, anchor="start"))
    p.append(text(130, 138, "Клас: Silicon Bug (апаратна логіка) | Модуль: I2C1 / I2C2", size=11, color=MUTED, anchor="start"))

    # Секція 2: Таблиця уражених ревізій кремнію
    p.append(rect(60, 158, 640, 52, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))
    p.append(text(75, 180, "Уражені ревізії кремнію (Silicon Revisions):", size=12, bold=True, anchor="start"))

    revs = [
        ("Rev 'Z' (0x1001)", "УРАЖЕНО", POS, "#fdecea"),
        ("Rev 'Y' (0x1003)", "УРАЖЕНО", POS, "#fdecea"),
        ("Rev '1' (0x2000)", "УРАЖЕНО", POS, "#fdecea"),
        ("Rev '2' (0x2001)", "ВИПРАВЛЕНО", FIELD, "#eafaf1")
    ]
    rx_pos = 75
    for r_name, r_status, r_col, r_bg in revs:
        p.append(rect(rx_pos, 188, 145, 18, fill=r_bg, stroke=r_col, sw=1, rx=3))
        p.append(text(rx_pos + 6, 201, r_name, size=10, color=INK, bold=True, anchor="start"))
        p.append(text(rx_pos + 140, 201, r_status, size=9.5, color=r_col, bold=True, anchor="end"))
        rx_pos += 152

    # Секція 3: Фізичний механізм та наслідок
    p.append(rect(60, 220, 640, 66, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=4))
    p.append(text(75, 238, "Опис дефекту (Description & Impact):", size=12, color=POS, bold=True, anchor="start"))
    p.append(text(75, 255, "Короткий сплеск завади під час очікування шини переводить аналоговий фільтр у стан десинхронізації.", size=11, color=INK, anchor="start"))
    p.append(text(75, 271, "Скінченний автомат виставляє біт BUSY=1. Генерація тактів SCL зупиняється навічно, модуль не реагує на START.", size=11, color=INK, anchor="start"))

    # Секція 4: Рекомендований обхід (Workaround)
    p.append(rect(60, 296, 640, 66, fill="#eef6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(75, 314, "Рекомендований обхід (Workaround):", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(75, 331, "1. Програмне скидання периферії через біт I2C1RST у регістрі RCC->APB1RSTR.", size=11, color=INK, anchor="start"))
    p.append(text(75, 347, "2. Переведення пінів у GPIO: вибити 9 тактів на SCL для звільнення лінії SDA зовнішнім слейвом.", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "errata-anatomy.svg"), W, H, *p)


# ── Figure 2: i2c-lockup-mechanism ────────────────────────────────────────────
# Механізм апаратного зависання I2C в кремнії
def fig_i2c_lockup():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 28, "Механізм апаратного зависання I2C (STM32F103 Silicon Errata)", size=16, bold=True))

    # Блок 1: Фізична шина
    p.append(rect(40, 55, 200, 110, fill=FILL, stroke=LINE, sw=1.5))
    p.append(text(140, 78, "Фізична лінія I2C", size=13, bold=True))
    p.append(line(55, 105, 225, 105, color=NEG, sw=2))
    p.append(text(60, 98, "SDA (3.3V)", size=10, color=NEG, anchor="start"))
    p.append(line(55, 135, 225, 135, color=POS, sw=2))
    p.append(text(60, 128, "SCL (3.3V)", size=10, color=POS, anchor="start"))
    p.append(text(140, 155, "Шина вільна, є підтяжка", size=10.5, color=MUTED))

    p.append(arrow(240, 110, 285, 110, color=LINE, sw=1.8))

    # Блок 2: Аналоговий фільтр шумів та десинхронізація
    p.append(rect(285, 55, 210, 110, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(390, 78, "Аналоговий Noise Filter", size=13, bold=True, color=POS))
    p.append(text(390, 98, "Сплеск завади (< 50 нс)", size=11, color=INK))
    p.append(text(390, 116, "Хибний детекшн START", size=11, color=POS, bold=True))
    p.append(text(390, 136, "FSM у невалідному стані", size=11, color=INK))
    p.append(text(390, 153, "Clock stretching триває", size=10.5, color=MUTED))

    p.append(arrow(495, 110, 540, 110, color=POS, sw=1.8))

    # Блок 3: Регістри периферії I2C
    p.append(rect(540, 55, 180, 110, fill="#f8fafc", stroke=POS, sw=1.8))
    p.append(text(630, 78, "Регістри I2C_SR1 / SR2", size=13, bold=True))
    p.append(rect(555, 92, 150, 24, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    p.append(text(630, 108, "SR2: BUSY = 1 (LATCH)", size=11, color=POS, bold=True))
    p.append(rect(555, 122, 150, 24, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
    p.append(text(630, 138, "SR1: BTF / ADDR = 0", size=11, color=MUTED))

    # Стрілка вниз до поведінки прошивки
    p.append(arrow(630, 165, 630, 205, color=POS, sw=1.8))

    # Блок 4: Пастка в прошивці
    p.append(rect(380, 205, 340, 120, fill="#fdecea", stroke=POS, sw=2, rx=6))
    p.append(text(550, 228, "Глухий кут у стандартному драйвері", size=13, bold=True, color=POS))
    p.append(rect(400, 240, 300, 32, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=3))
    p.append(text(550, 260, "while (I2C1->SR2 & I2C_SR2_BUSY);", size=11.5, color=POS, bold=True))
    p.append(text(550, 288, "Прапорець BUSY ніколи не скинеться апаратно!", size=11, color=POS, bold=True))
    p.append(text(550, 308, "Потрібен примусовий RCC reset периферії", size=10.5, color=INK))

    # Блок 5: Ліки (Workaround)
    p.append(rect(40, 205, 300, 120, fill="#eafaf1", stroke=FIELD, sw=2, rx=6))
    p.append(text(190, 228, "Апаратне лікування (Workaround)", size=13, bold=True, color=FIELD))
    p.append(text(60, 252, "1. RCC->APB1RSTR |= I2C1RST (скидання блоку)", size=10.5, color=INK, anchor="start"))
    p.append(text(60, 272, "2. GPIO Bit-Bang: 9 тактів SCL (скидання Slave)", size=10.5, color=INK, anchor="start"))
    p.append(text(60, 292, "3. Генерація STOP на шині через GPIO", size=10.5, color=INK, anchor="start"))
    p.append(text(60, 312, "4. Повна переініціалізація I2C регістрами", size=10.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "i2c-lockup-mechanism.svg"), W, H, *p)


# ── Figure 3: isolation-protocol ──────────────────────────────────────────────
# 5-кроковий протокол локалізації кремнієвого дефекту
def fig_isolation_protocol():
    W, H = 760, 390
    p = []
    p.append(text(W / 2, 28, "Інженерний протокол доведення кремнієвого дефекту (MRE Flow)", size=16, bold=True))

    steps = [
        ("1. Перевірка живлення", "Осцилограф: шуми VDD, VREF, падіння напруги під навантаженням", "#2c3e50"),
        ("2. Звірення з Reference Manual", "Порядок запису конфігураційних бітів, тактування шин APB/AHB", "#2457d6"),
        ("3. Побудова MRE (Bare-Metal)", "Вимкнення RTOS, HAL, зайвих IRQ; прямий доступ CMSIS; мінімум коду", "#c0392b"),
        ("4. Зчитування Silicon REV_ID", "Читання регістра DBGMCU_IDCODE, визначення літерної ревізії чіпа", "#27ae60"),
        ("5. Звірення з Errata Sheet", "Пошук номера дефекту, застосування Workaround або заміна чіпа", "#2c3e50"),
    ]

    y0, rh = 55, 58
    for i, (st_title, st_desc, st_col) in enumerate(steps):
        y = y0 + i * rh
        # Рамка кроку
        p.append(rect(60, y, 640, 48, fill=FILL, stroke=st_col, sw=1.6, rx=6))
        # Номер кроку
        p.append(circle(92, y + 24, 15, fill="#ffffff", stroke=st_col, sw=2))
        p.append(text(92, y + 29, str(i + 1), size=13, bold=True, color=st_col))
        # Текст
        p.append(text(125, y + 20, st_title, size=13, bold=True, color=INK, anchor="start"))
        p.append(text(125, y + 37, st_desc, size=11, color=MUTED, anchor="start"))

        # Стрілка між кроками
        if i < len(steps) - 1:
            p.append(arrow(380, y + 48, 380, y + rh, color=MUTED, sw=1.5))

    render(os.path.join(OUT, "isolation-protocol.svg"), W, H, *p)


# ── Figure 4: busmatrix-arbitration-race ───────────────────────────────────────
# Конфлікт арбітражу на багатошаровій матриці шин Multi-layer AHB
def fig_busmatrix_race():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 28, "Колізія на Multi-layer BusMatrix: одночасний доступ CPU та DMA", size=16, bold=True))

    # Ліва колонка: Майстри шини (Bus Masters)
    p.append(rect(40, 65, 170, 75, fill="#f8fafc", stroke=NEG, sw=1.8, rx=6))
    p.append(text(125, 92, "Cortex-M CPU", size=13, bold=True, color=NEG))
    p.append(text(125, 110, "D-Code / System Bus", size=10.5, color=MUTED))
    p.append(text(125, 126, "Читання буфера в циклі", size=10, color=INK))

    p.append(rect(40, 195, 170, 75, fill="#f8fafc", stroke=POS, sw=1.8, rx=6))
    p.append(text(125, 222, "DMA1 Controller", size=13, bold=True, color=POS))
    p.append(text(125, 240, "AHB Master Port", size=10.5, color=MUTED))
    p.append(text(125, 256, "Запис даних з АЦП/SPI", size=10, color=INK))

    # Центральний блок: Матриця шин (BusMatrix Arbiter)
    p.append(rect(270, 55, 220, 230, fill="#f4f6f8", stroke="#2c3e50", sw=2, rx=8))
    p.append(text(380, 80, "Multi-layer AHB Matrix", size=13, bold=True, color="#2c3e50"))
    p.append(rect(285, 95, 190, 175, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=4))

    p.append(text(380, 120, "Арбітр пріоритетів", size=12, bold=True))
    p.append(text(380, 138, "Round-Robin / Fixed", size=10.5, color=MUTED))

    p.append(rect(295, 155, 170, 50, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(380, 173, "Апаратна гонка (Race)", size=11, color=POS, bold=True))
    p.append(text(380, 191, "Конфлікт на фронті такту", size=10, color=POS))

    p.append(text(380, 230, "Затримка підтвердження", size=10.5, color=MUTED))
    p.append(text(380, 246, "(HREADY stall glitch)", size=10, color=MUTED))

    # Стрілки від майстрів до матриці
    p.append(arrow(210, 102, 270, 102, color=NEG, sw=2))
    p.append(arrow(210, 232, 270, 232, color=POS, sw=2))

    # Права колонка: Цільова пам'ять (Slaves)
    p.append(rect(550, 65, 170, 100, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    p.append(text(635, 90, "SRAM Bank 1", size=13, bold=True))
    p.append(text(635, 108, "Спільна область пам'яті", size=10.5, color=MUTED))
    p.append(text(635, 128, "Спільний порт доступу", size=10, color=MUTED))
    p.append(text(635, 148, "Конфлікт шини!", size=11, color=POS, bold=True))

    p.append(rect(550, 185, 170, 100, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(635, 210, "SRAM Bank 2 / CCM", size=13, bold=True, color=FIELD))
    p.append(text(635, 228, "Ізольований банк", size=10.5, color=MUTED))
    p.append(text(635, 248, "Окремий порт шини", size=10, color=FIELD))
    p.append(text(635, 268, "Безпечно (Workaround)", size=11, color=FIELD, bold=True))

    # Стрілки від матриці до пам'яті
    p.append(arrow(490, 115, 550, 115, color=POS, sw=2))
    p.append(arrow(490, 235, 550, 235, color=FIELD, sw=2))

    # Підсумок знизу
    p.append(text(W / 2, 325, "Наслідок дефекту: DMA пропускає запис байта без BusFault помилки (Silent Data Corruption)", size=11.5, color=POS, bold=True))
    p.append(text(W / 2, 345, "Виправлення: рознесення буферів DMA та коду CPU по різних фізичних банках SRAM", size=11, color=FIELD, italic=True))

    render(os.path.join(OUT, "busmatrix-arbitration-race.svg"), W, H, *p)


if __name__ == "__main__":
    fig_errata_anatomy()
    fig_i2c_lockup()
    fig_isolation_protocol()
    fig_busmatrix_race()
    print("Figures generated successfully.")
