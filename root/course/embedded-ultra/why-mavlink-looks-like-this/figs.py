# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. mavlink-v1-vs-v2-frame: Порівняння структури кадру v1 та v2 ────────────
def fig_v1_vs_v2():
    W, H = 980, 560
    p = []

    p.append(text(W / 2, 30, "Анатомія кадру MAVLink: еволюція від версії v1 (8 байтів оверхеду) до v2 (14+13 байтів)", size=15, color=INK, bold=True))

    # --- Блок v1 ---
    y1 = 65
    p.append(rect(40, y1, 900, 195, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(60, y1 + 24, "MAVLink v1 — Базовий двійковий кадр (Службовий оверхед: 8 байтів, MSG ID до 255)", size=13, color=NEG, bold=True, anchor="start"))

    v1_fields = [
        ("STX", "0xFE", "1 Б", "#fef3c7", "#d97706", 55),
        ("LEN", "0..255", "1 Б", "#e0f2fe", "#0284c7", 55),
        ("SEQ", "0..255", "1 Б", "#e0f2fe", "#0284c7", 55),
        ("SYS ID", "1..255", "1 Б", "#e0f2fe", "#0284c7", 65),
        ("COMP ID", "1..255", "1 Б", "#e0f2fe", "#0284c7", 70),
        ("MSG ID", "0..255", "1 Б", "#ede9fe", "#7c3aed", 70),
        ("PAYLOAD (Корисні дані)", "Впорядковані за розміром поля (0 .. 255 байтів)", "N Б", "#eaf2ec", FIELD, 345),
        ("CRC-16", "MCRF4XX + Extra", "2 Б", "#fef2f2", POS, 120),
    ]

    cur_x = 55
    for name, val, sz, bg_c, brd_c, fw in v1_fields:
        p.append(rect(cur_x, y1 + 42, fw, 75, fill=bg_c, stroke=brd_c, sw=1.5, rx=5))
        p.append(text(cur_x + fw / 2, y1 + 64, name, size=11, color=brd_c, bold=True))
        p.append(text(cur_x + fw / 2, y1 + 84, val, size=9.5, color=INK))
        p.append(text(cur_x + fw / 2, y1 + 104, sz, size=9.5, color=MUTED))
        cur_x += fw + 5

    # Пояснення v1 обмежень
    p.append(text(60, y1 + 145, "• Заголовок (6 Б) + CRC (2 Б) = 8 байтів службових даних на будь-який пакет.", size=11, color=INK, anchor="start"))
    p.append(text(60, y1 + 165, "• Вузьке місце v1: 1-байтовий MSG ID обмежує простір повідомлень лише 256 типами (вичерпано у 2015 році).", size=11, color=POS, anchor="start"))
    p.append(text(60, y1 + 185, "• Відсутні прапорці розширення, сумісності версій та вбудована автентифікація каналу.", size=11, color=MUTED, anchor="start"))

    # --- Блок v2 ---
    y2 = 285
    p.append(rect(40, y2, 900, 255, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(60, y2 + 24, "MAVLink v2 — Розширений кадр (Оверхед: 14 байтів + опційний підпис 13 байтів, MSG ID 24-біт)", size=13, color=FIELD, bold=True, anchor="start"))

    v2_fields = [
        ("STX", "0xFD", "1 Б", "#fef3c7", "#d97706", 45),
        ("LEN", "0..255", "1 Б", "#e0f2fe", "#0284c7", 45),
        ("INC", "Incompat", "1 Б", "#fee2e2", POS, 45),
        ("CMP", "Compat", "1 Б", "#e0e7ff", "#4338ca", 45),
        ("SEQ", "0..255", "1 Б", "#e0f2fe", "#0284c7", 45),
        ("SYS", "1..255", "1 Б", "#e0f2fe", "#0284c7", 45),
        ("COMP", "1..255", "1 Б", "#e0f2fe", "#0284c7", 45),
        ("MSG ID", "24-біт (3 байти)", "3 Б", "#ede9fe", "#7c3aed", 85),
        ("PAYLOAD", "Zero-Truncation (0..255 Б)", "N Б", "#eaf2ec", FIELD, 215),
        ("CRC", "16-біт", "2 Б", "#fef2f2", POS, 65),
        ("SIGNATURE (Опція)", "LinkID (1B) + Time (6B) + HMAC (6B)", "13 Б", "#fef3c7", "#b45309", 155),
    ]

    cur_x = 55
    for name, val, sz, bg_c, brd_c, fw in v2_fields:
        p.append(rect(cur_x, y2 + 42, fw, 75, fill=bg_c, stroke=brd_c, sw=1.5, rx=5))
        p.append(text(cur_x + fw / 2, y2 + 64, name, size=10.5, color=brd_c, bold=True))
        p.append(text(cur_x + fw / 2, y2 + 84, val, size=9.5, color=INK))
        p.append(text(cur_x + fw / 2, y2 + 104, sz, size=9.5, color=MUTED))
        cur_x += fw + 4

    p.append(text(60, y2 + 145, "• STX = 0xFD: парсер миттєво відрізняє v2 від v1 у спільному потоці байтів.", size=11, color=INK, anchor="start"))
    p.append(text(60, y2 + 165, "• 24-бітний MSG ID (3 байти, Little-Endian): розширює каталог до 16,777,216 унікальних повідомлень.", size=11, color=INK, anchor="start"))
    p.append(text(60, y2 + 185, "• INC FLAGS (0x01 = наявний блок підпису) та CMP FLAGS: гарантують безпечну еволюцію стандарту.", size=11, color=INK, anchor="start"))
    p.append(text(60, y2 + 205, "• Zero-Truncation: кінцеві байти зі значенням 0x00 відтинаються при відправці, зменшуючи трафік на лінку.", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(60, y2 + 225, "• Signature (13 Б): захист від replay-атак і підробки команд керування за допомогою HMAC-SHA256.", size=11, color="#b45309", anchor="start"))

    render(os.path.join(OUT, "mavlink-v1-vs-v2-frame.svg"), W, H, *p,
           title="Анатомія кадру MAVLink v1 та v2")


# ── 2. field-alignment-ordering: Природне вирівнювання полів у пам'яті ───────
def fig_field_alignment():
    W, H = 980, 520
    p = []

    p.append(text(W / 2, 30, "Сортування полів у MAVLink: нуль байтів паддингу та нульове копіювання на ARM", size=15, color=INK, bold=True))

    # Лівий блок: Довільний порядок
    lx, ly, lw, lh = 40, 65, 435, 430
    p.append(rect(lx, ly, lw, lh, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 26, "ДО СОРТУВАННЯ: Наївний порядок полів", size=13, color=POS, bold=True))
    p.append(text(lx + lw / 2, ly + 46, "Компілятор C вставляє паддинг для вирівнювання адрес", size=10.5, color=MUTED))

    unsorted_blocks = [
        ("uint8_t system_status", "1 байт за адресою 0x00", "#e0f2fe", "#0284c7", 38),
        ("PAD (3 байти дірки!)", "Паддинг для вирівнювання наступного int64", "#fee2e2", POS, 38),
        ("uint64_t time_usec", "8 байтів за адресою 0x04 (зсув 4) -> Помилка!", "#fef3c7", "#d97706", 50),
        ("uint16_t voltage_battery", "2 байти за адресою 0x0C", "#e0f2fe", "#0284c7", 38),
        ("PAD (2 байти дірки!)", "Паддинг для вирівнювання float на межу 4 Б", "#fee2e2", POS, 38),
        ("float roll_rate", "4 байти за адресою 0x10", "#ede9fe", "#7c3aed", 42),
    ]

    cy = ly + 65
    for name, desc, bg_c, brd_c, bh in unsorted_blocks:
        p.append(rect(lx + 20, cy, lw - 40, bh, fill=bg_c, stroke=brd_c, sw=1.2, rx=4))
        p.append(text(lx + 32, cy + bh / 2 - 6, name, size=11.5, color=brd_c, bold=True, anchor="start"))
        p.append(text(lx + 32, cy + bh / 2 + 10, desc, size=9.5, color=INK, anchor="start"))
        cy += bh + 6

    p.append(text(lx + 20, ly + 375, "❌ 5 байтів з 20 (25%) витрачено на пусті дірки пам'яті.", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(lx + 20, ly + 395, "❌ Прямий cast буфера DMA на структуру викликає UsageFault", size=10.5, color=POS, anchor="start"))
    p.append(text(lx + 20, ly + 413, "   або вимагає повільного побайтового копіювання memcpy.", size=10, color=MUTED, anchor="start"))

    # Правий блок: MAVLink впорядкування
    rx_pos, ry, rw, rh = 505, 65, 435, 430
    p.append(rect(rx_pos, ry, rw, rh, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(rx_pos + rw / 2, ry + 26, "MAVLINK ПОРЯДОК: Сортування за розміром", size=13, color=FIELD, bold=True))
    p.append(text(rx_pos + rw / 2, ry + 46, "8 Б (uint64) -> 4 Б (float) -> 2 Б (uint16) -> 1 Б (uint8)", size=10.5, color=MUTED))

    sorted_blocks = [
        ("uint64_t time_usec", "8 байтів (зміщення 0x00 .. 0x07, вирівняно на 8)", "#fef3c7", "#d97706", 52),
        ("float roll_rate", "4 байти (зміщення 0x08 .. 0x0B, вирівняно на 4)", "#ede9fe", "#7c3aed", 45),
        ("uint16_t voltage_battery", "2 байти (зміщення 0x0C .. 0x0D, вирівняно на 2)", "#e0f2fe", "#0284c7", 40),
        ("uint8_t system_status", "1 байт (зміщення 0x0E, природне вирівнювання)", "#eaf2ec", FIELD, 38),
    ]

    cy = ry + 65
    for name, desc, bg_c, brd_c, bh in sorted_blocks:
        p.append(rect(rx_pos + 20, cy, rw - 40, bh, fill=bg_c, stroke=brd_c, sw=1.2, rx=4))
        p.append(text(rx_pos + 32, cy + bh / 2 - 6, name, size=11.5, color=brd_c, bold=True, anchor="start"))
        p.append(text(rx_pos + 32, cy + bh / 2 + 10, desc, size=9.5, color=INK, anchor="start"))
        cy += bh + 8

    p.append(rect(rx_pos + 20, ry + 265, rw - 40, 85, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(rx_pos + 32, ry + 285, "Чому це працює на будь-якому CPU:", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx_pos + 32, ry + 305, "Будь-яка адреса, кратна 8, автоматично кратна 4, 2 та 1.", size=10, color=INK, anchor="start"))
    p.append(text(rx_pos + 32, ry + 323, "Кожне поле ідеально лягає на межу свого розміру.", size=10, color=INK, anchor="start"))
    p.append(text(rx_pos + 32, ry + 341, "Нуль байтів паддингу. 100% корисна щільність у кадрі.", size=10, color=FIELD, bold=True, anchor="start"))

    p.append(text(rx_pos + 20, ry + 375, "✓ Нульовий оверхед каналу: в ефір ідуть лише дані.", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx_pos + 20, ry + 395, "✓ Zero-Copy десеріалізація на STM32 Cortex-M4/M7.", size=10.5, color=FIELD, anchor="start"))
    p.append(text(rx_pos + 20, ry + 413, "✓ Відсутність UsageFault при прямому читанні з буфера.", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "field-alignment-ordering.svg"), W, H, *p,
           title="Сортування полів у MAVLink для вирівнювання пам'яті")


# ── 3. crc-extra-generation: Захист схеми через CRC_EXTRA ────────────────────
def fig_crc_extra():
    W, H = 980, 480
    p = []

    p.append(text(W / 2, 30, "Механізм CRC_EXTRA: перевірка цілісності каналу та несумісності схем в одній контрольній сумі", size=14.5, color=INK, bold=True))

    # Крок 1: XML схема повідомлення
    p.append(rect(40, 65, 260, 150, fill="#f8fafc", stroke=NEG, sw=1.5, rx=6))
    p.append(text(170, 90, "1. XML визначення (ATTITUDE)", size=12, color=NEG, bold=True))
    p.append(text(55, 115, '<message id="30" name="ATTITUDE">', size=9.5, color=INK, anchor="start"))
    p.append(text(55, 133, '  <field type="uint32_t" name="time_boot_ms"/>', size=9, color=MUTED, anchor="start"))
    p.append(text(55, 151, '  <field type="float" name="roll"/>', size=9, color=MUTED, anchor="start"))
    p.append(text(55, 169, '  <field type="float" name="pitch"/>', size=9, color=MUTED, anchor="start"))
    p.append(text(55, 187, '  <field type="float" name="yaw"/>', size=9, color=MUTED, anchor="start"))
    p.append(text(55, 203, '</message>', size=9.5, color=INK, anchor="start"))

    # Стрілка генерації CRC_EXTRA
    p.append(arrow(300, 140, 350, 140, color=NEG, sw=2))
    p.append(text(325, 130, "mavgen", size=10, color=NEG, bold=True))

    # Крок 2: Хеш схеми (CRC_EXTRA)
    p.append(rect(355, 90, 200, 100, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(455, 115, "2. CRC_EXTRA (1 байт)", size=12, color="#d97706", bold=True))
    p.append(text(455, 140, "CRC_EXTRA = 39 (0x27)", size=12, color=INK, bold=True))
    p.append(text(455, 165, "Обчислено зі списку типів та імен", size=9.5, color=MUTED))

    # Крок 3: Розрахунок CRC на відправнику
    p.append(rect(600, 65, 340, 150, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(770, 90, "3. Обчислення фінального CRC-16", size=12, color=FIELD, bold=True))
    p.append(text(620, 118, "crc = crc_calculate(Header + Payload)", size=10.5, color=INK, anchor="start"))
    p.append(text(620, 142, "crc_accumulate(CRC_EXTRA, &crc);", size=10.5, color="#d97706", bold=True, anchor="start"))
    p.append(text(620, 168, "-> Фінальний CRC (2 байти) записується в кінець кадру", size=9.5, color=MUTED, anchor="start"))
    p.append(text(620, 192, "⚠️ CRC_EXTRA НЕ передається в радіоканал!", size=10, color=POS, bold=True, anchor="start"))

    p.append(arrow(555, 140, 600, 140, color=FIELD, sw=2))

    # Нижня частина: Перевірка на стороні приймача
    y_sc = 245
    p.append(rect(40, y_sc, 900, 215, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(W / 2, y_sc + 24, "Що відбувається під час прийому повідомлення на наземній станції (GCS)", size=13, color=INK, bold=True))

    # Сценарій А: Схеми збігаються
    p.append(rect(60, y_sc + 45, 405, 150, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(262, y_sc + 70, "Сценарій А: Однаковий діалект (CRC_EXTRA = 39)", size=11.5, color=FIELD, bold=True))
    p.append(text(80, y_sc + 98, "1. Отримано байти кадру з ефіру.", size=10, color=INK, anchor="start"))
    p.append(text(80, y_sc + 120, "2. Приймач обчислює CRC над даними та додає свій CRC_EXTRA (39).", size=10, color=INK, anchor="start"))
    p.append(text(80, y_sc + 142, "3. Обчислена CRC == Отримана CRC у пакеті.", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(80, y_sc + 168, "✓ Пакет валідний. Кути орієнтації відображаються коректно.", size=10, color=FIELD, anchor="start"))

    # Сценарій Б: Схеми розійшлися
    p.append(rect(515, y_sc + 45, 405, 150, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(717, y_sc + 70, "Сценарій Б: Несумісна схема (CRC_EXTRA = 184)", size=11.5, color=POS, bold=True))
    p.append(text(535, y_sc + 98, "1. На дроні нова прошивка (додано поле sensor_id).", size=10, color=INK, anchor="start"))
    p.append(text(535, y_sc + 120, "2. GCS має старий XML: її CRC_EXTRA = 39 != 184.", size=10, color=INK, anchor="start"))
    p.append(text(535, y_sc + 142, "3. Обчислена CRC != Отримана CRC у пакеті!", size=10, color=POS, bold=True, anchor="start"))
    p.append(text(535, y_sc + 168, "❌ Пакет мовчки відкинуто. Захист від зсуву полів і аварії.", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "crc-extra-generation.svg"), W, H, *p,
           title="Генерація та верифікація CRC_EXTRA в MAVLink")


# ── 4. zero-truncation-efficiency: Відтинання нулів у MAVLink v2 ──────────────
def fig_zero_truncation():
    W, H = 980, 470
    p = []

    p.append(text(W / 2, 30, "Оптимізація каналу в MAVLink v2: механізм Zero-Truncation (відтинання кінцевих нулів)", size=14.5, color=INK, bold=True))

    y = 65
    # Повне повідомлення в пам'яті відправника
    p.append(rect(40, y, 900, 110, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(60, y + 24, "1. Структура повідомлення в оперативній пам'яті дрона (Повна довжина: 32 байти)", size=12, color=NEG, bold=True, anchor="start"))

    # Блоки даних
    p.append(rect(60, y + 42, 280, 50, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=4))
    p.append(text(200, y + 64, "Активні поля (10 байтів)", size=11, color="#0284c7", bold=True))
    p.append(text(200, y + 82, "time_usec (8B), state_flags (2B)", size=9.5, color=INK))

    p.append(rect(345, y + 42, 575, 50, fill="#fef2f2", stroke=POS, sw=1.5, rx=4))
    p.append(text(632, y + 64, "Кінцеві нулі / Невикористані розширення (22 байти: 0x00, 0x00 ... 0x00)", size=11, color=POS, bold=True))
    p.append(text(632, y + 82, "Опційні розширені сенсори, додаткові канали сервоприводів тощо", size=9.5, color=MUTED))

    # Стрілка обрізання
    p.append(arrow(490, y + 115, 490, y + 155, color=FIELD, sw=2))
    p.append(text(505, y + 138, "mavlink_finalize_message: відтинає всі 0x00 з кінця", size=10.5, color=FIELD, bold=True, anchor="start"))

    # Кадр у радіоефірі
    y2 = 225
    p.append(rect(40, y2, 900, 95, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(60, y2 + 24, "2. Реальний пакет у радіоефірі (LEN = 10 замість 32! Заощаджено 22 байти на кожному пакеті)", size=12, color=FIELD, bold=True, anchor="start"))

    p.append(rect(60, y2 + 42, 180, 42, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(150, y2 + 67, "Header v2 (LEN=10)", size=10.5, color="#d97706", bold=True))

    p.append(rect(245, y2 + 42, 280, 42, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(385, y2 + 67, "Payload (лише 10 Б)", size=10.5, color="#0284c7", bold=True))

    p.append(rect(530, y2 + 42, 90, 42, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    p.append(text(575, y2 + 67, "CRC (2 Б)", size=10.5, color=POS, bold=True))

    p.append(rect(630, y2 + 42, 290, 42, fill="#ffffff", stroke="#94a3b8", sw=1, rx=4))
    p.append(text(775, y2 + 67, "В ефір НЕ передається (Економія 68%!)", size=10, color=MUTED, bold=True))

    # Стрілка прийому
    p.append(arrow(490, y2 + 100, 490, y2 + 138, color=NEG, sw=2))
    p.append(text(505, y2 + 120, "Приймач: memset(&msg, 0) + memcpy(msg, payload, LEN)", size=10.5, color=NEG, bold=True, anchor="start"))

    # Відновлена структура на GCS
    y3 = 368
    p.append(rect(40, y3, 900, 85, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(60, y3 + 22, "3. Відновлена структура в пам'яті GCS: непоставлені байти автоматично лишаються нулями", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(60, y3 + 45, "• Повна зворотна та пряма сумісність: нові поля в кінці структури не ламають старі приймачі.", size=10.5, color=INK, anchor="start"))
    p.append(text(60, y3 + 65, "• При частоті телеметрії 50 Гц відтинання 20 нульових байтів економить 1000 байтів/с (10 кбіт/с смуги!).", size=10.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "zero-truncation-bandwidth.svg"), W, H, *p,
           title="Відтинання нульових байтів (Zero-Truncation) у MAVLink v2")


if __name__ == "__main__":
    fig_v1_vs_v2()
    fig_field_alignment()
    fig_crc_extra()
    fig_zero_truncation()
    print("All figures generated successfully.")
