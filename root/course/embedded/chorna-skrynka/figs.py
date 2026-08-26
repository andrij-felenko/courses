# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. ring-buffer-snapshot: Циклічний буфер у RAM та знімок аварії ──
def fig_ring_buffer_snapshot():
    W, H = 940, 520
    p = []

    p.append(rect(15, 15, 910, 490, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(470, 42, "Архітектура циклічного буфера в RAM (Ring Buffer Snapshot)", size=15, color=INK, bold=True))

    # Лівий блок: Циклічний буфер у пам'яті .noinit
    p.append(rect(35, 68, 410, 390, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(240, 95, "Кільцевий буфер у секції .noinit RAM", size=13, color=INK, bold=True))
    p.append(text(240, 115, "Неперервний запис подій O(1) без зносу пам'яті", size=10, color=MUTED))

    # Кільце кадрів (сегменти буфера)
    slots = [
        ("Кадр 102 (T - 4.5 с)", "#dbeafe", "#2563eb", "Норма (FSM=RUN)"),
        ("Кадр 103 (T - 3.2 с)", "#dbeafe", "#2563eb", "Шина I2C OK"),
        ("Кадр 104 (T - 1.8 с)", "#fef3c7", "#d97706", "I2C NACK / Retry"),
        ("Кадр 105 (T - 0.5 с)", "#fee2e2", "#c0392b", "FSM=ERROR_CRIT"),
        ("Кадр 106 (T = 0.0 с)", "#fee2e2", "#b91c1c", "⚡ HardFault / Crash"),
        ("Кадр 107 (T + 0.1 с)", "#f1f5f9", "#64748b", "Пост-тригер 1"),
        ("Кадр 108 (T + 0.2 с)", "#f1f5f9", "#64748b", "Пост-тригер 2"),
        ("Кадр 101 (Перезапис)", "#f1f5f9", "#94a3b8", "Старий кадр"),
    ]

    y_off = 138
    for i, (title, fcol, scol, note) in enumerate(slots):
        y = y_off + i * 36
        p.append(rect(50, y, 220, 30, fill=fcol, stroke=scol, sw=1.2, rx=4))
        p.append(text(160, y + 20, title, size=10, color=INK, bold=True))
        p.append(rect(280, y, 145, 30, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
        p.append(text(352, y + 20, note, size=9.5, color=scol, bold=True))

    # Покажчик Head
    p.append(arrow(25, 300, 48, 300, color=POS, sw=2))
    p.append(text(22, 304, "Head", size=10, color=POS, bold=True, anchor="end"))

    # Правий блок: Хронологія фіксації знімка аварії (Pre-Trigger / Post-Trigger)
    p.append(rect(465, 68, 460, 390, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(695, 95, "Хронологія фіксації аварійного знімка", size=13, color=INK, bold=True))

    # Візуалізація часової шкали
    p.append(rect(485, 125, 420, 75, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    p.append(line(500, 162, 885, 162, color=INK, sw=1.5))
    
    # Секція Pre-Trigger
    p.append(rect(510, 142, 230, 38, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=4))
    p.append(text(625, 165, "Pre-Trigger (Історія до аварії: 5 с)", size=10, color="#1e40af", bold=True))

    # Точка тригера
    p.append(line(740, 132, 740, 192, color=POS, sw=2.5))
    p.append(text(740, 140, "⚡ Тригер відмови (T=0)", size=10, color=POS, bold=True))

    # Секція Post-Trigger
    p.append(rect(745, 142, 130, 38, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(810, 165, "Post-Trigger (+200 мс)", size=9.5, color=POS, bold=True))

    # Блок дій при фіксації аварії
    p.append(rect(485, 215, 420, 160, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    p.append(text(695, 238, "Алгоритм фіксації знімка (Snapshot Freeze):", size=11, color=INK, bold=True))
    
    steps = [
        "1. Перехоплення в HardFault / PVD / WDT Early Warning IRQ",
        "2. Блокування покажчика Head: заборона нових записів у RAM",
        "3. Збір контексту ядра: регістри CFSR, HFSR, PC, LR, SP, FSM",
        "4. Обчислення CRC-16 для всього масиву кадрів буфера",
        "5. Швидкий експорт (Commit) у FRAM або слот аварій Flash"
    ]
    for idx, st in enumerate(steps):
        p.append(text(500, 262 + idx * 21, st, size=9.5, color=INK, anchor="start"))

    # Блок сховища Flash / FRAM
    p.append(rect(485, 388, 420, 55, fill="#dcfce7", stroke="#15803d", sw=1.2, rx=6))
    p.append(text(695, 410, "Збережений аварійний дамп у Non-Volatile Memory", size=11, color="#15803d", bold=True))
    p.append(text(695, 430, "Слот 0x01 | Magic: 0x424F5831 | Розмір: 2048 байтів | CRC OK", size=9.5, color="#166534"))

    # Нижній висновок
    b, _, _ = textbox(470, 485, "Кільцевий буфер у RAM утримує передісторію аварії; при фатальному збої буфер миттєво заморожується і скидається в енергонезалежну пам'ять для посмертного аналізу.",
                      size=10.5, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "ring-buffer-snapshot.svg"), W, H, *p)

# ── 2. binary-frame-layout: Структура компактного бінарного кадру ──
def fig_binary_frame_layout():
    W, H = 940, 500
    p = []

    p.append(rect(15, 15, 910, 470, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(470, 42, "Структура та оптимізація бінарного кадру чорної скриньки", size=15, color=INK, bold=True))

    # Верхній блок: Неефективне текстове логування
    p.append(rect(35, 68, 870, 105, fill="#fee2e2", stroke=POS, sw=1.2, rx=8))
    p.append(text(470, 90, "Неефективне текстове логування (ASCII / Printf / String Logs)", size=12, color=POS, bold=True))
    
    txt_example = '"2026-08-26 14:32:01.452 [WARN] Subsys:NAV Event:LOST_LOCK Sat:4 HDOP:3.8 V_bat:3.72V\\n"'
    p.append(rect(55, 103, 830, 28, fill="#ffffff", stroke=POS, sw=1, rx=4))
    p.append(text(470, 122, txt_example, size=10, color=POS, bold=True))

    p.append(text(150, 153, "• Розмір рядка: 84 байти", size=10, color=INK, bold=True))
    p.append(text(470, 153, "• Затримка передачі на UART 115200: 7.3 мс (блокування ядра)", size=10, color=POS, bold=True))
    p.append(text(780, 153, "• Оверхед парсингу в ISR: критичний", size=10, color=INK, bold=True))

    # Нижній блок: Компактний 16-байтний бінарний кадр
    p.append(rect(35, 188, 870, 240, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(470, 212, "Компактний 16-байтний бінарний кадр події (Binary Event Frame)", size=13, color=INK, bold=True))

    # Візуалізація байтової розкладки кадру (16 байтів)
    fields = [
        ("timestamp_ms\n(uint32_t, 4B)", 4, "#dbeafe", "#2563eb", "Мітка часу від старту\n(точність 1 мс, діапазон 49.7 діб)"),
        ("subsys_id\n(uint8_t, 1B)", 1, "#fef3c7", "#d97706", "ID підсистеми\n(NAV, POWER, COM)"),
        ("event_id\n(uint8_t, 1B)", 1, "#fef3c7", "#d97706", "Код події\n(ERR, STATE_CHG)"),
        ("fsm_state\n(uint16_t, 2B)", 2, "#e2e8f0", "#475569", "Стан автоматів FSM\nі бітові прапорці"),
        ("payload[6]\n(6 байтів)", 6, "#dcfce7", "#15803d", "Корисні дані (напруга мВ,\nструм, температура, лічильник)"),
        ("crc16\n(uint16_t, 2B)", 2, "#fce7f3", "#db2777", "CRC-16/CCITT\nконтрольна сума 0..13B")
    ]

    total_w = 820
    x_start = 60
    y_box = 235

    # Малюємо блоки байтів
    for name, b_len, fcol, scol, desc in fields:
        w = int(total_w * (b_len / 16.0))
        p.append(rect(x_start, y_box, w, 52, fill=fcol, stroke=scol, sw=1.5, rx=4))
        
        lines = name.split("\n")
        p.append(text(x_start + w/2, y_box + 20, lines[0], size=10, color=INK, bold=True))
        p.append(text(x_start + w/2, y_box + 38, lines[1], size=9, color=scol, bold=True))
        
        # Опис під блоком
        dlines = desc.split("\n")
        p.append(text(x_start + w/2, y_box + 70, dlines[0], size=9.5, color=MUTED))
        if len(dlines) > 1:
            p.append(text(x_start + w/2, y_box + 84, dlines[1], size=9.5, color=MUTED))

        x_start += w

    # Порівняльна таблиця характеристик
    p.append(rect(55, 335, 830, 80, fill="#ffffff", stroke=MUTED, sw=1, rx=6))
    p.append(text(470, 355, "Переваги оптимізованого бінарного формату:", size=11, color=INK, bold=True))
    
    p.append(text(180, 378, "✓ Стиснення обсягу: у 5.25 раза менше", size=10, color="#15803d", bold=True))
    p.append(text(470, 378, "✓ Час упаковки: < 35 тактів ядра (0.2 мкс при 168 МГц)", size=10, color="#15803d", bold=True))
    p.append(text(760, 378, "✓ Безпека: нульове виділення купи (No Malloc)", size=10, color="#15803d", bold=True))
    
    p.append(text(180, 398, "✓ Апаратна сумісність: вирівнювання за 4 байти", size=9.5, color=INK))
    p.append(text(470, 398, "✓ Гарантія цілісності: апаратний/програмний розрахунок CRC-16", size=9.5, color=INK))
    p.append(text(760, 398, "✓ ISR-безпека: атомарне копіювання в буфер", size=9.5, color=INK))

    # Нижній висновок
    b, _, _ = textbox(470, 465, "Бінарний 16-байтний кадр вміщує повний контекст події, гарантує константний час збереження O(1) і запобігає блокуванню ядра під час аварійного виклику.",
                      size=10.5, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "binary-frame-layout.svg"), W, H, *p)

# ── 3. nv-storage-architecture: Дворівнева архітектура пам'яті (RAM + FRAM/Flash) ──
def fig_nv_storage_architecture():
    W, H = 940, 540
    p = []

    p.append(rect(15, 15, 910, 510, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(470, 42, "Дворівнева архітектура сховища бортового реєстратора (L1 RAM → L2 Non-Volatile)", size=15, color=INK, bold=True))

    # Ліва колонка: Рівень 1 (L1 RAM Buffer)
    p.append(rect(35, 70, 410, 400, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(240, 98, "Рівень 1 (L1): Швидкий буфер у SRAM (.noinit)", size=12.5, color=INK, bold=True))
    p.append(text(240, 118, "Розмір: 4–8 КБ | Затримка: 0 мкс | Ресурс: ∞", size=10, color=MUTED))

    # Структура SRAM
    p.append(rect(55, 135, 370, 60, fill="#dbeafe", stroke="#2563eb", sw=1.2, rx=6))
    p.append(text(240, 158, "Заголовок буфера (Ring Header)", size=11, color="#1e40af", bold=True))
    p.append(text(240, 178, "Magic: 0x52494E47 | Head: 142 | Tail: 0 | Frozen: 0", size=9.5, color=INK))

    p.append(rect(55, 205, 370, 130, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(240, 228, "Масив 256–512 бінарних кадрів (Event Array)", size=11, color=INK, bold=True))
    p.append(text(240, 250, "• Кадри пишуться циклічно під час кожного виклику", size=9.5, color=INK))
    p.append(text(240, 270, "• Прямий доступ з переривань ISR без м'ютексів", size=9.5, color=INK))
    p.append(text(240, 290, "• Секція .noinit зберігає дані при скиданні NVIC_SystemReset()", size=9.5, color=POS, bold=True))
    p.append(text(240, 310, "• При HardFault буфер заморожується (Frozen = 1)", size=9.5, color=POS, bold=True))

    p.append(rect(55, 345, 370, 110, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    p.append(text(240, 368, "Регістри стану ядра (Crash Context)", size=11, color=POS, bold=True))
    p.append(text(240, 390, "CFSR, HFSR, MMFAR, BFAR (причина винятку)", size=9.5, color=INK))
    p.append(text(240, 410, "R0..R3, R12, LR, PC, xPSR (стековий кадр винятку)", size=9.5, color=INK))
    p.append(text(240, 430, "Стан FSM усіх підсистем + покажчик вершини стека SP", size=9.5, color=INK))

    # Стрілка переносу даних (Flush / Commit)
    p.append(arrow(450, 270, 485, 270, color="#15803d", sw=3))
    p.append(text(467, 255, "Flush /", size=9.5, color="#15803d", bold=True))
    p.append(text(467, 295, "Commit", size=9.5, color="#15803d", bold=True))

    # Права колонка: Рівень 2 (L2 FRAM / SPI Flash)
    p.append(rect(490, 70, 420, 400, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(700, 98, "Рівень 2 (L2): Енергонезалежна пам'ять (FRAM / Flash)", size=12.5, color=INK, bold=True))
    p.append(text(700, 118, "Розмір: 32–64 КБ | Захист від повного знеструмлення", size=10, color=MUTED))

    # Розподіл пам'яті у FRAM / Flash
    p.append(rect(510, 135, 380, 55, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=6))
    p.append(text(700, 155, "0x0000: Метадані тому (Partition Header)", size=10.5, color="#92400e", bold=True))
    p.append(text(700, 173, "Magic: 0x424F5831 | Boot Count: 84 | Crash Count: 2 | CRC-16", size=9, color=INK))

    p.append(rect(510, 200, 380, 120, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    p.append(text(700, 220, "0x1000..0x3FFF: Слоти аварійних знімків (Crash Dumps)", size=10.5, color=POS, bold=True))
    p.append(text(700, 240, "• Слот 0 (2 КБ): Попередній аварійний дамп", size=9, color=INK))
    p.append(text(700, 260, "• Слот 1 (2 КБ): Останній аварійний дамп (Активний)", size=9, color=POS, bold=True))
    p.append(text(700, 280, "• Слот 2 (2 КБ): Резервний слот", size=9, color=INK))
    p.append(text(700, 300, "• Слот 3 (2 КБ): Резервний слот", size=9, color=INK))

    p.append(rect(510, 330, 380, 125, fill="#dcfce7", stroke="#15803d", sw=1.2, rx=6))
    p.append(text(700, 350, "0x4000..0xFFFF: Кільцевий журнал подій (Flight Log)", size=10.5, color="#15803d", bold=True))
    p.append(text(700, 370, "• 48 КБ неперервного запису ключових телеметричних подій", size=9, color=INK))
    p.append(text(700, 390, "• Монотонний sequence_id для відновлення послідовності", size=9, color=INK))
    p.append(text(700, 410, "• FRAM: миттєвий побайтовий запис без зносу (10^14 циклів)", size=9, color="#15803d", bold=True))
    p.append(text(700, 430, "• Flash: ротація секторів (Sector Erase + Ping-Pong)", size=9, color=MUTED))

    # Нижній висновок
    b, _, _ = textbox(470, 500, "Дворівнева буферизація розділяє нульову затримку запису в RAM під час роботи та гарантоване енергонезалежне збереження інциденту в постійну пам'ять.",
                      size=10.5, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "nv-storage-architecture.svg"), W, H, *p)

# ── 4. power-loss-dump-timing: Часова шкала аварійного скидання при знеструмленні ──
def fig_power_loss_dump_timing():
    W, H = 940, 520
    p = []

    p.append(rect(15, 15, 910, 490, fill="#ffffff", stroke=LINE, sw=1.5, rx=10))
    p.append(text(470, 42, "Часовий та енергетичний бюджет аварійного скидання при знеструмленні", size=15, color=INK, bold=True))

    # Графік напруги V_DD та часові пороги
    p.append(rect(35, 70, 870, 210, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(470, 95, "Динаміка розряду конденсатора живлення (Holdup Capacitor C = 470 µF)", size=12.5, color=INK, bold=True))

    # Осі
    p.append(line(70, 245, 870, 245, color=INK, sw=1.5))
    p.append(line(70, 245, 70, 115, color=INK, sw=1.5))
    p.append(text(870, 260, "Час t (мс)", size=10, color=INK, bold=True))
    p.append(text(65, 110, "V_DD (В)", size=10, color=INK, bold=True, anchor="end"))

    # Рівні напруги
    # 3.3V Номінал
    p.append(line(70, 130, 200, 130, color="#2563eb", sw=2))
    p.append(text(65, 134, "3.3 В", size=9.5, color="#2563eb", bold=True, anchor="end"))

    # Крива спаду напруги
    p.append('<path d="M 200 130 Q 320 135 420 165 T 650 215 T 820 245" fill="none" stroke="#c0392b" stroke-width="2.5"/>')

    # Поріг 1: PVD / Brownout Warning (2.9 В)
    p.append(line(70, 165, 870, 165, color="#d97706", sw=1.2, dash="3 3"))
    p.append(text(65, 169, "2.9 В (PVD)", size=9, color="#d97706", bold=True, anchor="end"))
    p.append(line(420, 115, 420, 245, color="#d97706", sw=1.5, dash="2 2"))
    p.append(text(420, 125, "T0: Спрацьовує переривання PVD IRQ", size=9.5, color="#d97706", bold=True))

    # Поріг 2: BOR Reset (2.0 В)
    p.append(line(70, 215, 870, 215, color=POS, sw=1.2, dash="3 3"))
    p.append(text(65, 219, "2.0 В (BOR)", size=9, color=POS, bold=True, anchor="end"))
    p.append(line(650, 115, 650, 245, color=POS, sw=1.5, dash="2 2"))
    p.append(text(650, 125, "T_end: Апаратне скидання BOR", size=9.5, color=POS, bold=True))

    # Вікно порятунку Delta T
    p.append(rect(420, 185, 230, 55, fill="#dcfce7", stroke="#15803d", sw=1.2, rx=4))
    p.append(text(535, 205, "Аварійне часове вікно Δt = 2.5 мс", size=10, color="#15803d", bold=True))
    p.append(text(535, 223, "Доступний запас енергії: E = 0.5·C·(V1² - V2²)", size=9, color="#166534"))

    # Фази виконання реєстратора всередині часового вікна
    p.append(rect(35, 295, 870, 160, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(470, 318, "Послідовність операцій у критичному інтервалі 2.5 мс:", size=12.5, color=INK, bold=True))

    phase_boxes = [
        ("Фаза 1: Відсікання навантаження", "0.00 – 0.05 мс", "#fee2e2", POS, "Вимкнення ШІМ моторів, радіотрансивера, LED для зупинки падіння напруги"),
        ("Фаза 2: Фіксація RAM та CRC-16", "0.05 – 0.20 мс", "#fef3c7", "#d97706", "Заморожування Head, розрахунок CRC-16 для 2 КБ дампу (3000 тактів)"),
        ("Фаза 3: Прямий запис у SPI FRAM/Flash", "0.20 – 1.80 мс", "#dbeafe", "#2563eb", "Потоковий запис 2 КБ дампу по SPI на 20 МГц (час передачі: 0.82 мс)"),
        ("Фаза 4: Атомарний коміт заголовка", "1.80 – 2.00 мс", "#dcfce7", "#15803d", "Запис байта MAGIC_VALID = 0xA5. Дамп зафіксовано! Ядро чекає BOR")
    ]

    for idx, (title, dur, fcol, scol, desc) in enumerate(phase_boxes):
        y = 338 + idx * 27
        p.append(rect(55, y, 220, 23, fill=fcol, stroke=scol, sw=1, rx=3))
        p.append(text(165, y + 15, title, size=9.5, color=scol, bold=True))
        
        p.append(rect(280, y, 100, 23, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
        p.append(text(330, y + 15, dur, size=9.5, color=INK, bold=True))
        
        p.append(rect(385, y, 500, 23, fill="#ffffff", stroke=MUTED, sw=1, rx=3))
        p.append(text(395, y + 15, desc, size=9.5, color=INK, anchor="start"))

    # Нижній висновок
    b, _, _ = textbox(470, 485, "Аварійне переривання PVD дозволяє пристрою зберегти повний контекст збою за 2 мілісекунди до того, як апаратний Brownout вимкне живлення мікроконтролера.",
                      size=10.5, fill="#f8fafc", stroke=MUTED)
    p.append(b)

    render(os.path.join(OUT, "power-loss-dump-timing.svg"), W, H, *p)

if __name__ == "__main__":
    fig_ring_buffer_snapshot()
    fig_binary_frame_layout()
    fig_nv_storage_architecture()
    fig_power_loss_dump_timing()
    print("All figures generated successfully.")
