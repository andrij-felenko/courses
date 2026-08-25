# -*- coding: utf-8 -*-
"""Фігури теми «Журнал подій (Kafka-модель)». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"

# ── 1. destructive-queue-vs-event-log ────────────────────────────────────────
def fig_destructive_vs_event_log():
    W, H = 1000, 420
    f = []

    # Ліва половина: Руйнівна черга повідомлень (Destructive Message Queue)
    f.append(rect(15, 15, 470, 390, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(250, 42, "Традиційна черга: руйнівне вичитування", size=13, bold=True, color=POS))

    # Виробник
    b_prod1, _, _ = textbox(90, 110, "Продюсер\n(Producer)", size=11, bold=True, min_w=95, pad=6, fill=FILL, stroke=LINE)
    f.append(b_prod1)

    # Черга посередині лівої панелі
    f.append(rect(170, 80, 160, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(250, 98, "Черга (Queue)", size=11, bold=True))
    f.append(rect(180, 108, 30, 24, fill=BLUE_F, stroke=LINE, sw=1))
    f.append(text(195, 124, "M3", size=9.5, bold=True))
    f.append(rect(215, 108, 30, 24, fill=BLUE_F, stroke=LINE, sw=1))
    f.append(text(230, 124, "M2", size=9.5, bold=True))
    f.append(rect(250, 108, 30, 24, fill=RED_F, stroke=POS, sw=1))
    f.append(text(265, 124, "M1", size=9.5, color=POS))
    f.append(text(250, 155, "Вичитане M1 видаляється (ACK)", size=10, color=POS, italic=True))

    f.append(arrow(140, 110, 165, 110, color=LINE, sw=1.5))
    f.append(arrow(335, 110, 365, 110, color=POS, sw=1.5))

    # Консюмер 1
    b_c1, _, _ = textbox(415, 110, "Консюмер A\n(Billing)", size=11, bold=True, min_w=90, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(b_c1)

    # Проблема другого консюмера: треба ще одну чергу та фан-аут
    f.append(rect(170, 200, 160, 60, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    f.append(text(250, 218, "Дубльована черга", size=11, bold=True))
    f.append(rect(180, 228, 30, 24, fill=BLUE_F, stroke=LINE, sw=1))
    f.append(text(195, 244, "M3", size=9.5, bold=True))
    f.append(rect(215, 228, 30, 24, fill=BLUE_F, stroke=LINE, sw=1))
    f.append(text(230, 244, "M2", size=9.5, bold=True))
    f.append(rect(250, 228, 30, 24, fill=BLUE_F, stroke=LINE, sw=1))
    f.append(text(265, 244, "M1", size=9.5, bold=True))

    f.append(arrow(90, 140, 165, 230, color=MUTED, sw=1.2))
    f.append(arrow(335, 230, 365, 230, color=FIELD, sw=1.5))

    b_c2, _, _ = textbox(415, 230, "Консюмер B\n(Analytics)", size=11, bold=True, min_w=90, pad=6, fill=GREEN_F, stroke=FIELD)
    f.append(b_c2)

    # Підсумок лівої сторони
    f.append(line(30, 290, 470, 290, color=MUTED, sw=0.8))
    f.append(text(250, 312, "✗ Дані зникають після обробки (немає replay)", size=10.5, color=POS, bold=True))
    f.append(text(250, 335, "✗ Новий сервіс потребує дублювання черг (Fan-out)", size=10.5, color=POS))
    f.append(text(250, 358, "✗ Накопичення мільйонів повідомлень сповільнює брокер", size=10.5, color=POS))
    f.append(text(250, 381, "✗ Конкурентні споживачі ламають порядок повідомлень", size=10.5, color=POS))

    # Права половина: Журнал подій (Partitioned Append-Only Event Log)
    f.append(rect(515, 15, 470, 390, fill="#fafbfc", stroke=MUTED, sw=1, rx=8))
    f.append(text(750, 42, "Журнал подій: незмінний персистентний лог", size=13, bold=True, color=FIELD))

    # Виробник справа
    b_prod2, _, _ = textbox(570, 110, "Продюсер\n(Producer)", size=11, bold=True, min_w=85, pad=6, fill=FILL, stroke=LINE)
    f.append(b_prod2)

    # Журнал з комірками (offset 0..5)
    f.append(rect(630, 80, 260, 60, fill="#ffffff", stroke=LINE, sw=1.8, rx=4))
    f.append(text(760, 96, "Append-Only Log (Послідовний запис)", size=10.5, bold=True))

    offsets = [("0", 638), ("1", 680), ("2", 722), ("3", 764), ("4", 806), ("5", 848)]
    for off, ox in offsets:
        f.append(rect(ox, 106, 38, 26, fill=GREEN_F, stroke=FIELD, sw=1))
        f.append(text(ox + 19, 123, f"off:{off}", size=9.5, bold=True))

    f.append(arrow(615, 110, 635, 110, color=LINE, sw=1.5))

    # Вказівники споживачів (Offset Cursors)
    # Споживач A на offset 4
    f.append(rect(785, 160, 140, 45, fill=BLUE_F, stroke=NEG, sw=1.2, rx=4))
    f.append(text(855, 178, "Консюмер A (Billing)", size=9.5, bold=True, color=NEG))
    f.append(text(855, 194, "Поточний offset: 4", size=9.5, color=INK))
    f.append(arrow(855, 160, 825, 135, color=NEG, sw=1.4))

    # Споживач B на offset 1 (повільний або наздоганяє історію)
    f.append(rect(640, 220, 150, 45, fill=WARN_F, stroke=POS, sw=1.2, rx=4))
    f.append(text(715, 238, "Консюмер B (Analytics / ML)", size=9.5, bold=True, color=POS))
    f.append(text(715, 254, "Читає історію: offset 1", size=9.5, color=INK))
    f.append(arrow(715, 220, 700, 135, color=POS, sw=1.4))

    # Підсумок правої сторони
    f.append(line(530, 290, 970, 290, color=MUTED, sw=0.8))
    f.append(text(750, 312, "✓ Дані не видаляються при читанні (Non-destructive)", size=10.5, color=FIELD, bold=True))
    f.append(text(750, 335, "✓ Незалежні вказівники зсуву (Offset) для кожного сервісу", size=10.5, color=FIELD))
    f.append(text(750, 358, "✓ Можливість перемотування часу назад (Time travel / Replay)", size=10.5, color=FIELD))
    f.append(text(750, 381, "✓ Послідовний I/O на диску: швидкість 100+ MB/s на HDD / GB/s на SSD", size=10.5, color=FIELD))

    render(out("destructive-queue-vs-event-log.svg"), W, H, *f,
           title="Порівняння черги повідомлень та незмінного журналу подій")


# ── 2. log-segments-and-sparse-index ─────────────────────────────────────────
def fig_log_segments_and_sparse_index():
    W, H = 1000, 380
    f = []

    f.append(rect(15, 15, 970, 350, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 42, "Внутрішня будова секції: сегментні файли даних (.log) та розріджений індекс (.index)", size=13, bold=True))

    # Сегмент 1: Закритий (read-only)
    f.append(rect(40, 70, 270, 275, fill="#f8f9fa", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(175, 92, "Сегмент 00000000000000000000", size=10.5, bold=True))
    f.append(text(175, 108, "Статус: Закритий (Read-Only)", size=9.5, color=MUTED))

    f.append(rect(55, 125, 240, 80, fill=FILL, stroke=LINE, sw=1, rx=4))
    f.append(text(175, 142, "00000000000000000000.log", size=10, bold=True))
    f.append(text(175, 160, "Записи: offset 0 ... 9999", size=9.5))
    f.append(text(175, 178, "Розмір: 1 ГБ (заповнено)", size=9.5, color=MUTED))
    f.append(text(175, 196, "Фізичний послідовний файл", size=9, italic=True))

    f.append(rect(55, 220, 240, 105, fill=BLUE_F, stroke=NEG, sw=1, rx=4))
    f.append(text(175, 238, "00000000000000000000.index", size=10, bold=True, color=NEG))
    f.append(text(175, 256, "Розріджений індекс (Sparse Index)", size=9.5))
    f.append(text(175, 274, "off: 0 → byte: 0", size=9))
    f.append(text(175, 290, "off: 240 → byte: 4096", size=9))
    f.append(text(175, 306, "off: 512 → byte: 8192 ...", size=9))

    # Сегмент 2: Активний (Active Segment для запису)
    f.append(rect(340, 70, 620, 275, fill="#ffffff", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(650, 92, "Активний сегмент 00000000000000010000 (Приймає нові записи)", size=11, bold=True, color=FIELD))

    # Показ .index всередині активного сегмента
    f.append(rect(360, 120, 260, 205, fill=BLUE_F, stroke=NEG, sw=1.2, rx=4))
    f.append(text(490, 140, "Розріджений індекс: .index", size=10.5, bold=True, color=NEG))
    f.append(text(490, 158, "Запис кожні 4 КБ (index.interval.bytes)", size=9.5, color=MUTED))

    idx_rows = [
        ("Зсув (Offset)", "Фізична позиція (Pos)"),
        ("10000", "0 B"),
        ("10045", "4096 B  (4 KB)"),
        ("10092", "8192 B  (8 KB)"),
        ("10140", "12288 B (12 KB)")
    ]
    iy = 180
    for r1, r2 in idx_rows:
        bold_row = (iy == 180)
        f.append(text(430, iy, r1, size=9.5, bold=bold_row))
        f.append(text(545, iy, r2, size=9.5, bold=bold_row))
        if not bold_row:
            f.append(line(375, iy + 4, 605, iy + 4, color="#cbd5e1", sw=0.5))
        iy += 20

    f.append(text(490, 305, "Двійковий пошук у пам'яті (mmap) O(log N)", size=9.5, color=NEG, bold=True))

    # Показ .log файлу даних активного сегмента
    f.append(rect(650, 120, 290, 205, fill=GREEN_F, stroke=FIELD, sw=1.2, rx=4))
    f.append(text(795, 140, "Файл даних: .log", size=10.5, bold=True, color=FIELD))
    f.append(text(795, 158, "Послідовні бінарні фрейми повідомлень", size=9.5, color=MUTED))

    log_blocks = [
        ("0 B", "Offset 10000..10044 [4096 байт]"),
        ("4096 B", "Offset 10045..10091 [4096 байт]"),
        ("8192 B", "Offset 10092..10139 [4096 байт]"),
        ("12288 B", "Offset 10140..10185 [Новий запис →]")
    ]
    ly = 185
    for pos_lbl, data_lbl in log_blocks:
        f.append(rect(665, ly - 12, 60, 22, fill="#ffffff", stroke=LINE, sw=0.8))
        f.append(text(695, ly + 3, pos_lbl, size=9, bold=True))
        f.append(rect(730, ly - 12, 195, 22, fill="#ffffff", stroke=FIELD, sw=0.8))
        f.append(text(827, ly + 3, data_lbl, size=9))
        ly += 28

    # Стрілка пошуку від index до log
    f.append(arrow(605, 220, 660, 213, color=NEG, sw=1.5))
    f.append(text(632, 202, "Прямий стрибок", size=9, color=NEG, bold=True))

    render(out("log-segments-and-sparse-index.svg"), W, H, *f,
           title="Будова сегментів та розрідженого індексу журналу")


# ── 3. partitioning-and-consumer-groups ───────────────────────────────────────
def fig_partitioning_and_consumer_groups():
    W, H = 1000, 440
    f = []

    f.append(rect(15, 15, 970, 410, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 40, "Секціонування топіка (Partitioning) та паралелізм груп споживачів (Consumer Groups)", size=13, bold=True))

    # Ліва колонка: Продюсер і хешування ключів
    f.append(rect(30, 70, 180, 335, fill="#fafbfc", stroke=MUTED, sw=1, rx=6))
    f.append(text(120, 95, "Продюсери", size=12, bold=True))

    f.append(rect(45, 120, 150, 60, fill=FILL, stroke=LINE, sw=1, rx=4))
    f.append(text(120, 140, "Ключ: user_42", size=10, bold=True))
    f.append(text(120, 160, "hash(key) % 4 = 0", size=9.5, color=FIELD))

    f.append(rect(45, 200, 150, 60, fill=FILL, stroke=LINE, sw=1, rx=4))
    f.append(text(120, 220, "Ключ: user_99", size=10, bold=True))
    f.append(text(120, 240, "hash(key) % 4 = 2", size=9.5, color=NEG))

    f.append(rect(45, 280, 150, 60, fill=FILL, stroke=LINE, sw=1, rx=4))
    f.append(text(120, 300, "Без ключа (null)", size=10, bold=True))
    f.append(text(120, 320, "Round-Robin / Sticky", size=9.5, color=MUTED))

    # Центральна колонка: Топік з 4 секціями (Partitions)
    f.append(rect(240, 70, 340, 335, fill="#fafbfc", stroke=LINE, sw=1.5, rx=6))
    f.append(text(410, 95, "Топік: orders (4 секції / партиції)", size=12, bold=True))

    parts = [
        ("Секція 0 (Partition 0)", 130, GREEN_F, FIELD),
        ("Секція 1 (Partition 1)", 195, FILL, LINE),
        ("Секція 2 (Partition 2)", 260, BLUE_F, NEG),
        ("Секція 3 (Partition 3)", 325, FILL, LINE),
    ]

    for p_name, py, fill_c, stroke_c in parts:
        f.append(rect(255, py, 310, 50, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        f.append(text(315, py + 20, p_name, size=9.5, bold=True))
        # Маленькі комірки офсетів
        for i in range(5):
            f.append(rect(390 + i * 32, py + 12, 28, 26, fill="#ffffff", stroke=stroke_c, sw=0.8))
            f.append(text(404 + i * 32, py + 29, str(i), size=9))

    # Стрілки від продюсера до секцій
    f.append(arrow(195, 150, 255, 155, color=FIELD, sw=1.5))
    f.append(arrow(195, 230, 255, 285, color=NEG, sw=1.5))
    f.append(arrow(195, 310, 255, 220, color=MUTED, sw=1.2))

    # Права колонка: Групи споживачів
    # Група 1: Обробка замовлень (2 екземпляри ділять 4 секції)
    f.append(rect(610, 70, 360, 160, fill="#f0f9ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(790, 92, "Група споживачів: order-processing-group", size=11, bold=True, color=NEG))
    f.append(text(790, 108, "2 воркери ділять по 2 секції між собою", size=9.5, color=MUTED))

    f.append(rect(625, 125, 160, 90, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    f.append(text(705, 145, "Воркер 1 (Інстанс A)", size=10, bold=True))
    f.append(text(705, 165, "Обслуговує: Секція 0, 1", size=9.5, color=FIELD))
    f.append(text(705, 185, "Гарантія порядку в межах ключа", size=9, italic=True))

    f.append(rect(795, 125, 160, 90, fill="#ffffff", stroke=NEG, sw=1, rx=4))
    f.append(text(875, 145, "Воркер 2 (Інстанс B)", size=10, bold=True))
    f.append(text(875, 165, "Обслуговує: Секція 2, 3", size=9.5, color=NEG))
    f.append(text(875, 185, "Гарантія порядку в межах ключа", size=9, italic=True))

    f.append(arrow(565, 155, 625, 170, color=FIELD, sw=1.3))
    f.append(arrow(565, 285, 795, 170, color=NEG, sw=1.3))

    # Група 2: Аудит / Аналітика (1 екземпляр читає всі 4 секції)
    f.append(rect(610, 245, 360, 160, fill="#fdf4ff", stroke="#9333ea", sw=1.5, rx=6))
    f.append(text(790, 267, "Група споживачів: audit-and-archive-group", size=11, bold=True, color="#9333ea"))
    f.append(text(790, 283, "1 воркер вичитує всі 4 секції незалежно", size=9.5, color=MUTED))

    f.append(rect(680, 300, 220, 90, fill="#ffffff", stroke="#9333ea", sw=1, rx=4))
    f.append(text(790, 320, "Воркер аудиту (DWH / Data Lake)", size=10, bold=True))
    f.append(text(790, 340, "Читає Секції 0, 1, 2, 3 одночасно", size=9.5, color="#9333ea"))
    f.append(text(790, 360, "Власні незалежні зсуви (offsets)", size=9, italic=True))

    f.append(arrow(565, 350, 680, 350, color="#9333ea", sw=1.3))

    render(out("partitioning-and-consumer-groups.svg"), W, H, *f,
           title="Секціонування топіка та паралелізм груп споживачів")


# ── 4. isr-high-watermark-replication ────────────────────────────────────────
def fig_isr_high_watermark_replication():
    W, H = 1000, 440
    f = []

    f.append(rect(15, 15, 970, 410, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 40, "Реплікація секції: лідер, синхронні фоловери (ISR), High Watermark та Log End Offset", size=13, bold=True))

    # Брокер 1: Лідер секції
    f.append(rect(35, 75, 430, 225, fill=GREEN_F, stroke=FIELD, sw=1.8, rx=6))
    f.append(text(250, 98, "Брокер 1: Лідер секції (Leader Replica)", size=11.5, bold=True, color=FIELD))
    f.append(text(250, 116, "Приймає всі записи продюсерів та запити читання", size=9.5, color=MUTED))

    # Секція на Лідері (офсети 0..9)
    for i in range(10):
        ox = 55 + i * 39
        is_hw = (i <= 6)
        c_fill = "#ffffff" if is_hw else WARN_F
        c_stroke = FIELD if is_hw else POS
        f.append(rect(ox, 135, 35, 45, fill=c_fill, stroke=c_stroke, sw=1.2, rx=3))
        f.append(text(ox + 17, 152, "off", size=9, color=MUTED))
        f.append(text(ox + 17, 169, str(i), size=10, bold=True))

    # Лінії меж: HW та LEO
    # High Watermark на 6 (між 6 та 7: x = 55 + 7 * 39 - 2 = 326)
    f.append(line(326, 130, 326, 210, color=NEG, sw=2, dash="4,2"))
    f.append(text(275, 230, "High Watermark (HW = 7)", size=10, bold=True, color=NEG))
    f.append(text(275, 246, "Межа безпечного читання клієнтами", size=9, color=NEG))

    # Log End Offset на 9 (після 9: x = 55 + 10 * 39 - 2 = 443)
    f.append(line(443, 130, 443, 210, color=POS, sw=2, dash="4,2"))
    f.append(text(390, 268, "Log End Offset (LEO = 10)", size=10, bold=True, color=POS))
    f.append(text(390, 284, "Останній записаний байт на лідері", size=9, color=POS))

    # Фоловери праворуч
    # Фоловери 1 (Входить в ISR)
    f.append(rect(510, 75, 450, 135, fill="#fafbfc", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(735, 96, "Брокер 2: Фоловер 1 (У складі ISR — In-Sync Replica)", size=11, bold=True, color=FIELD))
    f.append(text(735, 112, "Синхронізований: лаг < replica.lag.time.max.ms", size=9.5, color=FIELD))

    for i in range(10):
        ox = 530 + i * 39
        has_msg = (i <= 7)
        c_fill = "#ffffff" if has_msg else "#f1f5f9"
        c_stroke = FIELD if has_msg else MUTED
        f.append(rect(ox, 128, 35, 38, fill=c_fill, stroke=c_stroke, sw=1, rx=3))
        f.append(text(ox + 17, 144, "off", size=9, color=MUTED))
        f.append(text(ox + 17, 158, str(i) if has_msg else "—", size=9.5, bold=has_msg))

    f.append(arrow(450, 155, 525, 147, color=FIELD, sw=1.4))
    f.append(text(488, 135, "Fetch", size=9.5, color=FIELD, bold=True))

    # Фоловери 2 (Відстав / Вибув з ISR)
    f.append(rect(510, 225, 450, 135, fill="#fafbfc", stroke=POS, sw=1.4, rx=6))
    f.append(text(735, 246, "Брокер 3: Фоловер 2 (Вибув з ISR — Lagging Replica)", size=11, bold=True, color=POS))
    f.append(text(735, 262, "Відстав від лідера через GC паузу або мережеву затримку", size=9.5, color=POS))

    for i in range(10):
        ox = 530 + i * 39
        has_msg = (i <= 4)
        c_fill = "#ffffff" if has_msg else "#fee2e2"
        c_stroke = POS if has_msg else MUTED
        f.append(rect(ox, 278, 35, 38, fill=c_fill, stroke=c_stroke, sw=1, rx=3))
        f.append(text(ox + 17, 294, "off", size=9, color=MUTED))
        f.append(text(ox + 17, 308, str(i) if has_msg else "—", size=9.5, bold=has_msg))

    # Зона вичитування консюмерами
    f.append(rect(35, 315, 430, 85, fill=BLUE_F, stroke=NEG, sw=1.2, rx=6))
    f.append(text(250, 336, "Споживачі читають ТІЛЬКИ до High Watermark (offset ≤ 6)", size=10.5, bold=True, color=NEG))
    f.append(text(250, 356, "Записи з offset 7..9 ще не зафіксовані (Uncommitted)", size=9.5, color=INK))
    f.append(text(250, 376, "Гарантія: відсутність «брудного читання» при зміні лідера", size=9, italic=True))

    f.append(text(735, 385, "acks=all вимагає запису на всі ISR репліки перед підняттям HW", size=9.5, bold=True, color=INK))

    render(out("isr-high-watermark-replication.svg"), W, H, *f,
           title="Реплікація секцій та межа фіксації High Watermark")


if __name__ == "__main__":
    fig_destructive_vs_event_log()
    fig_log_segments_and_sparse_index()
    fig_partitioning_and_consumer_groups()
    fig_isr_high_watermark_replication()
    print("All figures generated successfully.")
