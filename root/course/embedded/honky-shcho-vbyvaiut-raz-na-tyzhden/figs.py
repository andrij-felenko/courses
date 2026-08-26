# -*- coding: utf-8 -*-
"""Фігури для теми honky-shcho-vbyvaiut-raz-na-tyzhden.
Згенеровано через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_timing_window_race():
    """Статистичне вікно вразливості: чому гонки виникають раз на мільйони операцій."""
    W, H = 820, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок панелі
    p.append(rect(20, 15, 780, 45, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(410, 42, "Часова анатомія стану гонки: мікроскопічне вікно вразливості", size=15, color=INK, bold=True))

    # Секція 1: Головний потік і RMW-цикл
    p.append(rect(20, 70, 780, 145, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(35, 95, "Головний потік (Thread Mode, RMW цикл: count++)", size=13, color=INK, bold=True, anchor="start"))

    # Тактова вісь
    p.append(arrow(50, 140, 755, 140, color=LINE, sw=1.5))
    p.append(text(750, 160, "Час (t)", size=11, color=MUTED, anchor="end"))

    # Блоки інструкцій
    # 1. LDR
    p.append(rect(60, 115, 120, 50, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
    p.append(text(120, 138, "1. LDR r0, [r1]", size=12, color=INK, bold=True))
    p.append(text(120, 155, "Зчитування: 15 нс", size=10, color=MUTED))

    # 2. ADDS
    p.append(rect(200, 115, 120, 50, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
    p.append(text(260, 138, "2. ADDS r0, #1", size=12, color=INK, bold=True))
    p.append(text(260, 155, "Модифікація: 15 нс", size=10, color=MUTED))

    # Вікно вразливості (червона зона)
    p.append(rect(180, 105, 160, 70, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text(260, 125, "ВІКНО ГОНКИ (31.25 нс)", size=10, color=POS, bold=True))
    p.append(text(260, 145, "Стан ОЗП застарілий!", size=11, color=POS, bold=True))
    p.append(text(260, 162, "ОЗП != регістр r0", size=10, color=POS))

    # 3. STR
    p.append(rect(360, 115, 120, 50, fill="#e2e8f0", stroke=LINE, sw=1.2, rx=4))
    p.append(text(420, 138, "3. STR r0, [r1]", size=12, color=INK, bold=True))
    p.append(text(420, 155, "Запис у ОЗП: 15 нс", size=10, color=MUTED))

    # Поза вікном: безпечна зона
    p.append(rect(500, 115, 230, 50, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(615, 138, "Безпечний фоновий код", size=12, color=FIELD, bold=True))
    p.append(text(615, 155, "Тривалість: 10 000 000 нс (10 мс)", size=10, color=MUTED))

    # Секція 2: Події переривань (ISR)
    p.append(rect(20, 225, 780, 180, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(35, 248, "Асинхронні переривання (Handler Mode: ISR опитування сенсора / таймера)", size=13, color=INK, bold=True, anchor="start"))

    # Сценарій А: Переривання в безпечній зоні
    p.append(rect(500, 265, 250, 125, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(625, 288, "Сценарій А: Безпечне влучання", size=12, color=FIELD, bold=True))
    p.append(text(625, 310, "Ймовірність: 99.9997%", size=11, color=INK, bold=True))
    p.append(text(625, 330, "ISR зчитує валідне значення.", size=10, color=MUTED))
    p.append(text(625, 348, "RMW-цикл ще не почався або", size=10, color=MUTED))
    p.append(text(625, 365, "вже повністю завершився.", size=10, color=MUTED))

    # Стрілка безпечного ISR
    p.append(arrow(625, 265, 625, 175, color=FIELD, sw=1.5))

    # Сценарій Б: Фатальна колізія у вікні гонки
    p.append(rect(40, 265, 430, 125, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(255, 288, "Сценарій Б: Фатальне влучання у вікно (Race Hazard)", size=12, color=POS, bold=True))
    p.append(text(255, 310, "Ймовірність: 0.0003% (~1 на 330 000 викликів RMW)", size=11, color=POS, bold=True))
    p.append(text(255, 330, "1. ISR витісняє потік між LDR та STR, модифікує count у ОЗП.", size=10, color=INK))
    p.append(text(255, 348, "2. Потік прокидається і записує застаріле r0 -> запис ISR ВТРАЧЕНО!", size=10, color=POS, bold=True))
    p.append(text(255, 368, "Результат: крах раз на 7 діб безперервної роботи в полі.", size=10, color=MUTED))

    # Стрілка колізії ISR
    p.append(arrow(260, 265, 260, 185, color=POS, sw=2.0))

    render(os.path.join(OUT, "timing-window-race.svg"), W, H, *p)


def fig_multibyte_tearing():
    """Анатомія байтового дроблення (Data Tearing) на 8-бітних та 32-бітних ядрах."""
    W, H = 820, 390
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок панелі
    p.append(rect(20, 15, 780, 42, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(410, 41, "Байтове дроблення (Word/Data Tearing) при неатомарному доступі", size=15, color=INK, bold=True))

    # Ліва колонка: 8-бітне ядро (AVR) записує uint32_t
    p.append(rect(20, 68, 375, 305, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(207, 95, "8-бітне ядро (AVR ATmega / PIC)", size=13, color=INK, bold=True))
    p.append(text(207, 115, "Запис uint32_t: 0x0000FFFF -> 0x00010000", size=11, color=MUTED))

    # 4 байти
    bytes_avr = [
        ("Байт 0 (0x00)", "STS 0x60, r16", "#dcfce7", FIELD, "Записано 0x00"),
        ("Байт 1 (0x00)", "STS 0x61, r17", "#dcfce7", FIELD, "Записано 0x00"),
        ("--- ВИКЛИК ISR ---", "Переривання читає ОЗП!", "#fee2e2", POS, "ОЗП = 0x00000000 (ФАНТОМ!)"),
        ("Байт 2 (0x01)", "STS 0x62, r18", "#f1f5f9", INK, "Записано 0x01"),
        ("Байт 3 (0x00)", "STS 0x63, r19", "#f1f5f9", INK, "Записано 0x00"),
    ]
    y = 135
    for b_title, b_code, b_bg, b_col, b_desc in bytes_avr:
        is_isr = "ISR" in b_title
        p.append(rect(35, y, 345, 38, fill=b_bg, stroke=b_col, sw=1.2, rx=4))
        p.append(text(45, y + 23, b_title, size=11, color=b_col, bold=True, anchor="start"))
        p.append(text(185, y + 23, b_code, size=10, color=INK, anchor="start"))
        p.append(text(370, y + 23, b_desc, size=9, color=b_col, bold=is_isr, anchor="end"))
        y += 44

    p.append(text(207, 360, "Наслідок: Лічильник стрибнув з 65535 у 0 замість 65536!", size=10, color=POS, bold=True))

    # Права колонка: 32-бітне ядро (ARM) зчитує uint64_t
    p.append(rect(425, 68, 375, 305, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(612, 95, "32-бітне ядро (ARM Cortex-M)", size=13, color=INK, bold=True))
    p.append(text(612, 115, "Читання uint64_t таймера g_uptime_us", size=11, color=MUTED))

    bytes_arm = [
        ("1. LDR r0, [time]", "Читання молодших 32 біт", "#dcfce7", FIELD, "r0 = 0xFFFFFFFF"),
        ("--- ВИКЛИК ISR ---", "ISR оновлює час на +1 мкс!", "#fee2e2", POS, "Час став 0x0002_00000000"),
        ("2. LDR r1, [time+4]", "Читання старших 32 біт", "#dcfce7", FIELD, "r1 = 0x00000002"),
        ("Результат у потоці", "time64 = (r1<<32) | r0", "#fef2f2", POS, "0x00000002_FFFFFFFF"),
        ("Стрибок у часі", "Фантомний стрибок у майбутнє", "#fee2e2", POS, "+4294.97 с (~71.6 хв)!"),
    ]
    y = 135
    for b_title, b_code, b_bg, b_col, b_desc in bytes_arm:
        is_isr = "ISR" in b_title or "Стрибок" in b_title or "Результат" in b_title
        p.append(rect(440, y, 345, 38, fill=b_bg, stroke=b_col, sw=1.2, rx=4))
        p.append(text(450, y + 23, b_title, size=11, color=b_col, bold=True, anchor="start"))
        p.append(text(590, y + 23, b_code, size=10, color=INK, anchor="start"))
        p.append(text(775, y + 23, b_desc, size=9, color=b_col, bold=is_isr, anchor="end"))
        y += 44

    p.append(text(612, 360, "Наслідок: Таймаут таймера миттєво спрацьовує або зависає!", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "multibyte-tearing.svg"), W, H, *p)


def fig_exclusive_monitor_ldrex_strex():
    """Апаратний автомат станів Exclusive Monitor для інструкцій LDREX/STREX."""
    W, H = 820, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок панелі
    p.append(rect(20, 15, 780, 42, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(410, 41, "Апаратний монітор ексклюзивного доступу (ARM Cortex-M3/M4/M7/M33)", size=15, color=INK, bold=True))

    # Ліва половина: Скінченний автомат Local Exclusive Monitor
    p.append(rect(20, 68, 380, 335, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(210, 95, "Автомат станів Exclusive Monitor", size=13, color=INK, bold=True))

    # Стан Open Access
    p.append(rect(50, 130, 320, 65, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=8))
    p.append(text(210, 155, "СТАН: OPEN ACCESS (Вільний)", size=12, color=INK, bold=True))
    p.append(text(210, 175, "Ексклюзивну мітку скинуто. Запис STREX заборонено.", size=10, color=MUTED))

    # Стан Exclusive Access
    p.append(rect(50, 270, 320, 65, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(210, 295, "СТАН: EXCLUSIVE ACCESS (Захоплений)", size=12, color=FIELD, bold=True))
    p.append(text(210, 315, "Адресу позначено. STREX дозволено виконати запис.", size=10, color=FIELD))

    # Перехід 1: LDREX (вниз ліворуч)
    p.append(arrow(75, 195, 75, 265, color=FIELD, sw=2.0))
    p.append(text(70, 235, "LDREX r0, [r1]", size=11, color=FIELD, bold=True, anchor="end"))

    # Перехід 2: STREX успіх (вгору праворуч)
    p.append(arrow(335, 270, 335, 200, color=LINE, sw=1.5))
    p.append(text(340, 235, "STREX -> OK (r2=0)", size=10, color=LINE, bold=True, anchor="start"))

    # Перехід 3: Переривання ISR / CLREX скидає монітор (по центру)
    p.append(arrow(185, 270, 185, 200, color=POS, sw=2.0))
    p.append(text(192, 235, "ISR/CLREX скидає", size=10, color=POS, bold=True, anchor="start"))

    p.append(text(210, 360, "Якщо монітор у стані OPEN: STREX повертає 1 (помилка),", size=10, color=POS))
    p.append(text(210, 378, "а запис у комірку пам'яті фізично БЛОКУЄТЬСЯ апаратно.", size=10, color=POS, bold=True))

    # Права половина: Петля атомарної модифікації (Atomic Retry Loop)
    p.append(rect(420, 68, 380, 335, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(610, 95, "Апаратна петля повтору (Lock-Free Retry Loop)", size=13, color=INK, bold=True))

    steps_loop = [
        ("1. LDREX r0, [r1]", "Завантажити значення та встановити Exclusive tag", "#f1f5f9", INK),
        ("2. ADDS r0, r0, #1", "Модифікувати значення локально в регістрі r0", "#f1f5f9", INK),
        ("3. STREX r2, r0, [r1]", "Спроба атомарного збереження (r2 = результат)", "#fef3c7", "#92400e"),
        ("4. CMP r2, #0", "Перевірка: чи був запис успішним? (r2 == 0)", "#f1f5f9", INK),
        ("5. BNE retry_loop", "Якщо r2 != 0: повторити спробу спочатку!", "#fee2e2", POS),
    ]
    y = 120
    for s_code, s_desc, s_bg, s_col in steps_loop:
        p.append(rect(435, y, 350, 42, fill=s_bg, stroke=s_col if s_col != INK else MUTED, sw=1.2, rx=4))
        p.append(text(445, y + 20, s_code, size=11, color=s_col, bold=True, anchor="start"))
        p.append(text(445, y + 35, s_desc, size=9, color=MUTED, anchor="start"))
        y += 48

    p.append(text(610, 375, "Без вимкнення переривань! Жодного збільшення latency!", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "exclusive-monitor-ldrex-strex.svg"), W, H, *p)


def fig_lock_free_spsc_fifo():
    """Архітектура Lock-Free SPSC кільцевого буфера з розділеними індексами."""
    W, H = 820, 430
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок панелі
    p.append(rect(20, 15, 780, 42, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(410, 41, "Архітектура безблокувального SPSC FIFO буфера (Single-Producer Single-Consumer)", size=15, color=INK, bold=True))

    # Кільцевий масив (8 комірок)
    p.append(rect(20, 68, 780, 160, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(410, 92, "Кільцевий буфер розміру N = 8 (Маска: index & 0x07)", size=13, color=INK, bold=True))

    # 8 комірок масиву
    cells = [
        (0, "Slot 0", "data[0]", "#dcfce7", FIELD),
        (1, "Slot 1", "data[1]", "#dcfce7", FIELD),
        (2, "Slot 2", "data[2]", "#dcfce7", FIELD),
        (3, "Slot 3", "data[3]", "#f1f5f9", MUTED),
        (4, "Slot 4", "data[4]", "#f1f5f9", MUTED),
        (5, "Slot 5", "data[5]", "#f1f5f9", MUTED),
        (6, "Slot 6", "data[6]", "#f1f5f9", MUTED),
        (7, "Slot 7", "data[7]", "#f1f5f9", MUTED),
    ]
    cx_start = 65
    for idx, label, val, c_bg, c_stroke in cells:
        x = cx_start + idx * 88
        p.append(rect(x, 110, 78, 60, fill=c_bg, stroke=c_stroke, sw=1.5, rx=6))
        p.append(text(x + 39, 133, label, size=11, color=INK, bold=True))
        p.append(text(x + 39, 153, val, size=10, color=c_stroke, bold=True))

    # Покажчики tail та head
    # Tail вказує на Slot 0
    p.append(arrow(104, 210, 104, 175, color=NEG, sw=2.0))
    p.append(text(104, 225, "tail = 0 (Consumer)", size=11, color=NEG, bold=True))

    # Head вказує на Slot 3
    p.append(arrow(368, 210, 368, 175, color=POS, sw=2.0))
    p.append(text(368, 225, "head = 3 (Producer)", size=11, color=POS, bold=True))

    # Дані між tail та head
    p.append(text(236, 195, "3 елементи готові до вичитування", size=10, color=FIELD, bold=True))

    # Нижня частина: Розподіл відповідальності
    # Лівий блок: Producer (Виробник / ISR)
    p.append(rect(20, 240, 375, 175, fill="#fff7ed", stroke="#ea580c", sw=1.2, rx=6))
    p.append(text(207, 265, "Виробник / Producer (тільки ISR або потік TX)", size=12, color="#c2410c", bold=True))
    p.append(text(35, 290, "1. Зчитує tail (relaxed): перевірка на заповнення.", size=10, color=INK, anchor="start"))
    p.append(text(35, 310, "2. Записує дані в buffer[head & MASK].", size=10, color=INK, anchor="start"))
    p.append(text(35, 330, "3. Бар'єр пам'яті (DMB / memory_order_release).", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(35, 350, "4. Оновлює head = head + 1 (ТІЛЬКИ Producer пише head!).", size=10, color=INK, anchor="start"))
    p.append(text(35, 375, "✓ Без критичних секцій: Consumer ніколи не пише head!", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(35, 395, "✓ Дані гарантовано у пам'яті ДО оновлення індексу head.", size=9, color=MUTED, anchor="start"))

    # Правий блок: Consumer (Споживач / Головний потік)
    p.append(rect(425, 240, 375, 175, fill="#eff6ff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(612, 265, "Споживач / Consumer (тільки головний цикл / RTOS)", size=12, color=NEG, bold=True))
    p.append(text(440, 290, "1. Зчитує head з memory_order_acquire.", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(440, 310, "2. Якщо head == tail: буфер порожній (вихід).", size=10, color=INK, anchor="start"))
    p.append(text(440, 330, "3. Зчитує дані з buffer[tail & MASK].", size=10, color=INK, anchor="start"))
    p.append(text(440, 350, "4. Бар'єр пам'яті (DMB / memory_order_release).", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(440, 370, "5. Оновлює tail = tail + 1 (ТІЛЬКИ Consumer пише tail!).", size=10, color=INK, anchor="start"))
    p.append(text(440, 395, "✓ Безпека: читач ніколи не пережене записувача.", size=10, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "lock-free-spsc-fifo.svg"), W, H, *p)


if __name__ == "__main__":
    fig_timing_window_race()
    fig_multibyte_tearing()
    fig_exclusive_monitor_ldrex_strex()
    fig_lock_free_spsc_fifo()
    print("Всі 4 фігури успішно згенеровано у img/")
