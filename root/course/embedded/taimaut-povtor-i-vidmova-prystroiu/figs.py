# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. spinning-trap-vs-timeout: Пастка вічного циклу проти таймауту ───────────
def fig_spinning_trap():
    W, H = 940, 480
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))

    # Заголовок
    p.append(text(W / 2, 28, "Порівняння реакцій системи на апаратний збій периферії", size=16, color=INK, bold=True))

    # Ліва колонка: Наївне опитування (Deadlock)
    p.append(rect(30, 55, 420, 400, fill="#fdf2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(240, 85, "Наївний цикл: while (!flag)", size=14, color=POS, bold=True))
    p.append(text(240, 105, "Небезпека мертвого зависання процесора", size=11, color=MUTED))

    # Схема ліворуч
    p.append(fitbox(50, 125, 380, 50, [
        "1. Процесор ініціює зчитування I2C/SPI",
        "Очікує прапорець готовності RXNE / BUSY=0"
    ], size=11, fill="#ffffff", stroke="#e0b4b4", color=INK))

    p.append(fitbox(50, 190, 380, 50, [
        "2. Збій: обрив дроту, зависання давача",
        "Лінія SCL затиснута в 0 (Clock Stretching)"
    ], size=11, fill="#fee2e2", stroke=POS, color=POS, bold=True))

    p.append(fitbox(50, 255, 380, 55, [
        "3. Прапорець ніколи не виставиться в 1",
        "while (!(I2C1->SR1 & RXNE)) крутиться вічно,",
        "стек не розкручується, інші задачі заблоковані"
    ], size=11, fill="#ffffff", stroke="#e0b4b4", color=INK))

    p.append(fitbox(50, 325, 380, 55, [
        "4. Катастрофічний наслідок:",
        "Сторожовий таймер (WDT) скидає мікроконтролер",
        "або система мертво зависає без оновлень"
    ], size=11, fill="#fbe8e8", stroke=POS, color=POS, bold=True))

    p.append(fitbox(50, 395, 380, 42, [
        "Підсумок: Відмова одного давача кладе весь пристрій"
    ], size=11, fill="#fee2e2", stroke=POS, color=POS, bold=True))

    # Права колонка: Детермінований таймаут (Safe Fail)
    p.append(rect(490, 55, 420, 400, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(700, 85, "Захищений таймаут: DWT / SysTick", size=14, color=FIELD, bold=True))
    p.append(text(700, 105, "Гарантоване повернення керування за дедлайном", size=11, color=MUTED))

    # Схема праворуч
    p.append(fitbox(510, 125, 380, 50, [
        "1. Фіксація стартового часу операції",
        "t_start = get_time();  t_deadline = t_start + timeout;"
    ], size=11, fill="#ffffff", stroke="#bbf7d0", color=INK))

    p.append(fitbox(510, 190, 380, 50, [
        "2. Збій: шина зависла / чип мовчить",
        "Прапорець апаратно не перемикається"
    ], size=11, fill="#fee2e2", stroke=POS, color=POS))

    p.append(fitbox(510, 255, 380, 55, [
        "3. Спрацьовує умова (get_time() > t_deadline)",
        "Цикл примусово переривається,",
        "драйвер повертає статусний код ERR_TIMEOUT"
    ], size=11, fill="#ffffff", stroke="#bbf7d0", color=INK))

    p.append(fitbox(510, 325, 380, 55, [
        "4. Контрольоване відновлення:",
        "Виклик bus_recover(), повтор через Backoff,",
        "або перехід у режим деградації (Failsafe)"
    ], size=11, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True))

    p.append(fitbox(510, 395, 380, 42, [
        "Підсумок: Система жива, процесор керує ситуацією"
    ], size=11, fill="#bbf7d0", stroke=FIELD, color=FIELD, bold=True))

    render(os.path.join(OUT, "spinning-trap-vs-timeout.svg"), W, H, *p)


# ── 2. timeout-mechanisms-comparison: Порівняння механізмів таймаутів ─────────
def fig_timeout_mechanisms():
    W, H = 940, 450
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    p.append(text(W / 2, 28, "Джерела вимірювання часу для таймаутів на мікроконтролері", size=16, color=INK, bold=True))

    cols = [
        ("Програмний лічильник", "uint32_t to = 100000; while(!f && --to);", [
            "• Залежить від оптимізації (-O0 vs -O3)",
            "• Змінюється від тактової частоти ядра",
            "• Непередбачуваний через Flash Wait States",
            "• Переривання спотворюють реальний час",
            "Вердикт: Небезпечно у промисловому коді"
        ], POS, "#fdf2f2", "#fee2e2"),

        ("SysTick / RTOS Tick", "uint32_t start = xTaskGetTickCount();", [
            "• Дискретність зазвичай 1 мс (1000 Гц)",
            "• Не залежить від швидкості виконання коду",
            "• Ідеально для затримок > 5–10 мс",
            "• Не підходить для мікросекундних шин (SPI)",
            "Вердикт: Відмінно для високорівневих дій"
        ], NEG, "#eff6ff", "#dbeafe"),

        ("DWT->CYCCNT (Апаратний)", "uint32_t t0 = DWT->CYCCNT;", [
            "• 32-бітний лічильник тактів процесора",
            "• Роздільна здатність у наносекундах",
            "• Модульна арифметика обробляє overflow",
            "• Нульовий оверхед, детермінований результат",
            "Вердикт: Еталон для низькорівневих драйверів"
        ], FIELD, "#f0fdf4", "#dcfce7")
    ]

    cw = 275
    gap = 25
    x_start = 35

    for i, (title, sub, items, border_col, bg_col, box_col) in enumerate(cols):
        cx = x_start + i * (cw + gap)
        p.append(rect(cx, 55, cw, 370, fill=bg_col, stroke=border_col, sw=1.8, rx=6))
        p.append(text(cx + cw / 2, 85, title, size=13, color=border_col, bold=True))
        p.append(fitbox(cx + 10, 105, cw - 20, 42, [sub], size=10, fill="#ffffff", stroke="#cbd5e1", color=INK))

        # Пункти
        y_cur = 160
        for it in items[:-1]:
            p.append(fitbox(cx + 10, y_cur, cw - 20, 44, [it], size=10.5, fill="#ffffff", stroke="#e2e8f0", color=INK))
            y_cur += 50

        # Вердикт
        p.append(fitbox(cx + 10, 365, cw - 20, 45, [items[-1]], size=11, fill=box_col, stroke=border_col, color=border_col, bold=True))

    render(os.path.join(OUT, "timeout-mechanisms-comparison.svg"), W, H, *p)


# ── 3. error-classification-taxonomy: Класифікація помилок ─────────────────────
def fig_error_taxonomy():
    W, H = 940, 480
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    p.append(text(W / 2, 28, "Класифікація помилок комунікації та маршрути відновлення", size=16, color=INK, bold=True))

    # Корінь: Помилка транзакції
    p.append(fitbox(340, 50, 260, 45, ["Збій транзакції драйвера", "NACK / Timeout / CRC Error / Bad ID"], size=11.5, fill="#fee2e2", stroke=POS, color=POS, bold=True))

    # Стрілки вліво і вправо
    p.append(line(470, 95, 230, 135, color=LINE, sw=1.5))
    p.append(line(470, 95, 710, 135, color=LINE, sw=1.5))

    # Гілка 1: Транзиєнтні помилки (Soft / Transient)
    p.append(rect(35, 135, 390, 320, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(230, 160, "Транзиєнтні збої (Transient)", size=14, color=NEG, bold=True))
    p.append(text(230, 180, "Короткочасні електричні або програмні завади", size=11, color=MUTED))

    p.append(fitbox(55, 195, 350, 55, [
        "Причини:",
        "• Електромагнітна завада (EMI) на шині",
        "• Одиничний збій контрольної суми CRC",
        "• Давач зайнятий перетворенням АЦП (NACK)"
    ], size=10.5, fill="#ffffff", stroke="#bfdbfe", color=INK))

    p.append(fitbox(55, 260, 350, 55, [
        "Стратегія реакції:",
        "• Повторна спроба (Retry) після паузи",
        "• Експоненційний відкат (Backoff) з джитером",
        "• Ліміт спроб: N = 2..4 рази"
    ], size=10.5, fill="#ffffff", stroke="#bfdbfe", color=INK))

    p.append(fitbox(55, 325, 350, 60, [
        "Результат повтору:",
        "• Успіх → продовжуємо штатну роботу",
        "• Вичерпано N спроб → ескалація до фатальної"
    ], size=11, fill="#dbeafe", stroke=NEG, color=NEG, bold=True))

    p.append(fitbox(55, 395, 350, 45, [
        "Ціль: Не збурювати систему через одиничний шум"
    ], size=11, fill="#bfdbfe", stroke=NEG, color=INK, bold=True))

    # Гілка 2: Фатальні / Перманентні помилки (Hard / Permanent)
    p.append(rect(515, 135, 390, 320, fill="#fdf2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(710, 160, "Фатальні відмови (Permanent)", size=14, color=POS, bold=True))
    p.append(text(710, 180, "Фізичне пошкодження або втрата зв'язку", size=11, color=MUTED))

    p.append(fitbox(535, 195, 350, 55, [
        "Причини:",
        "• Фізичний обрив дроту SDA / SCL / MISO",
        "• Знеструмлення або пробій мікросхеми",
        "• Невідповідність WHO_AM_I (0x00 / 0xFF)",
        "• Залипання шини веденим чипом"
    ], size=10.5, fill="#ffffff", stroke="#fecaca", color=INK))

    p.append(fitbox(535, 260, 350, 55, [
        "Стратегія реакції:",
        "• Відмова від негайних ретраїв (no busy-spin)",
        "• Апаратне скидання шини (I2C Bus Clear / Reset)",
        "• Спрацьовування Circuit Breaker (розрив)"
    ], size=10.5, fill="#ffffff", stroke="#fecaca", color=INK))

    p.append(fitbox(535, 325, 350, 60, [
        "Результат ескалації:",
        "• Перехід у захисний режим (Failsafe mode)",
        "• Перемикання на дублюючий давач / зупинка"
    ], size=11, fill="#fee2e2", stroke=POS, color=POS, bold=True))

    p.append(fitbox(535, 395, 350, 45, [
        "Ціль: Захистити шину і процесор від спаму відмов"
    ], size=11, fill="#fecaca", stroke=POS, color=INK, bold=True))

    render(os.path.join(OUT, "error-classification-taxonomy.svg"), W, H, *p)


# ── 4. circuit-breaker-fsm: Автомат Circuit Breaker ────────────────────────────
def fig_circuit_breaker():
    W, H = 940, 500
    p = []

    p.append(rect(0, 0, W, H, fill="#ffffff", stroke="#d0d7de", sw=1, rx=8))
    p.append(text(W / 2, 28, "Автомат стану здоров'я пристрою (Circuit Breaker)", size=16, color=INK, bold=True))

    # Стан 1: CLOSED (Здоровий)
    p.append(rect(40, 80, 250, 240, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(165, 110, "1. CLOSED (Замкнений)", size=14, color=FIELD, bold=True))
    p.append(text(165, 130, "Штатний робочий стан", size=11, color=MUTED))
    p.append(fitbox(55, 150, 220, 95, [
        "• Усі транзакції дозволені",
        "• Лічильник помилок = 0",
        "• При успіху: скидання помилок",
        "• При збої: failures++"
    ], size=11, fill="#ffffff", stroke="#bbf7d0", color=INK))
    p.append(fitbox(55, 255, 220, 50, [
        "Умова переходу:",
        "failures >= FAIL_THRESHOLD"
    ], size=10.5, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True))

    # Стан 2: OPEN (Розірваний / Відмова)
    p.append(rect(650, 80, 250, 240, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    p.append(text(775, 110, "2. OPEN (Розірваний)", size=14, color=POS, bold=True))
    p.append(text(775, 130, "Ізоляція несправного чипа", size=11, color=MUTED))
    p.append(fitbox(665, 150, 220, 95, [
        "• Звернення блокуються O(1)",
        "• Шина не навантажується",
        "• Повернення ERR_OFFLINE",
        "• Запуск таймера кулдауну"
    ], size=11, fill="#ffffff", stroke="#fecaca", color=INK))
    p.append(fitbox(665, 255, 220, 50, [
        "Умова переходу:",
        "Час охолодження T_cool минув"
    ], size=10.5, fill="#fee2e2", stroke=POS, color=POS, bold=True))

    # Стан 3: HALF-OPEN (Пробний)
    p.append(rect(345, 280, 250, 190, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(text(470, 305, "3. HALF-OPEN (Пробний)", size=14, color=NEG, bold=True))
    p.append(text(470, 325, "Перевірка готовності чипа", size=11, color=MUTED))
    p.append(fitbox(360, 345, 220, 65, [
        "• Дозволено 1 тестовий запит",
        "• Успіх → повернення в CLOSED",
        "• Збій → повернення в OPEN"
    ], size=11, fill="#ffffff", stroke="#bfdbfe", color=INK))
    p.append(fitbox(360, 415, 220, 45, [
        "Відновлення або повторна ізоляція"
    ], size=10.5, fill="#dbeafe", stroke=NEG, color=NEG, bold=True))

    # Стрілка CLOSED -> OPEN
    p.append(line(290, 160, 650, 160, color=POS, sw=2))
    p.append(text(470, 145, "Серія помилок (failures >= N) → РОЗРИВ", size=11, color=POS, bold=True))

    # Стрілка OPEN -> HALF-OPEN
    p.append(line(720, 320, 595, 370, color=NEG, sw=2))
    p.append(text(710, 360, "Кулдаун минув →", size=11, color=NEG, bold=True))

    # Стрілка HALF-OPEN -> CLOSED (Success)
    p.append(line(345, 370, 220, 320, color=FIELD, sw=2))
    p.append(text(230, 360, "← Тест успішний", size=11, color=FIELD, bold=True))

    # Стрілка HALF-OPEN -> OPEN (Fail)
    p.append(line(595, 410, 670, 320, color=POS, sw=2))
    p.append(text(665, 410, "Тест провалено →", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "circuit-breaker-fsm.svg"), W, H, *p)


if __name__ == "__main__":
    fig_spinning_trap()
    fig_timeout_mechanisms()
    fig_error_taxonomy()
    fig_circuit_breaker()
    print("Figures generated successfully.")
