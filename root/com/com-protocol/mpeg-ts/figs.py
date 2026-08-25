# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. ts-packet-structure: Анатомія 188-байтного пакета MPEG-TS ──────────────
def fig_ts_packet_structure():
    W, H = 840, 440
    p = []

    # Заголовок
    p.append(text(40, 26, "Структура 188-байтного пакета MPEG-2 Transport Stream (MPEG-TS)", size=13, bold=True, color=INK, anchor="start"))

    # Загальна шкала пакета (188 байтів)
    y0 = 48
    p.append(rect(40, y0, 160, 44, fill="#dbeafe", stroke=NEG, sw=1.8, rx=4))
    p.append(text(120, y0 + 18, "Заголовок TS (4 байти)", size=11, bold=True, color=NEG))
    p.append(text(120, y0 + 33, "Фіксована службова частина", size=9, color=MUTED))

    p.append(rect(208, y0, 210, 44, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=4))
    p.append(text(313, y0 + 18, "Адаптаційне поле (0..184 B)", size=11, bold=True, color="#b45309"))
    p.append(text(313, y0 + 33, "Опційне: PCR, стаффінг 0xFF", size=9, color=MUTED))

    p.append(rect(426, y0, 374, 44, fill="#dcfce7", stroke=POS, sw=1.8, rx=4))
    p.append(text(613, y0 + 18, "Корисне навантаження Payload (до 184 байтів)", size=11, bold=True, color=POS))
    p.append(text(613, y0 + 33, "Фрагмент кадру PES (відео/аудіо) або секція таблиці PSI", size=9, color=MUTED))

    # Розгортка 4-байтового заголовка (32 біти)
    p.append(text(40, 120, "1. Побайтова та побітова розкладка заголовка TS (4 байти / 32 біти):", size=11, bold=True, color=INK, anchor="start"))

    y1 = 135
    # Байт 1: Sync Byte (0x47)
    p.append(rect(40, y1, 100, 56, fill="#eff6ff", stroke=NEG, sw=1.4, rx=3))
    p.append(text(90, y1 + 17, "Sync Byte", size=10, bold=True, color=NEG))
    p.append(text(90, y1 + 32, "8 бітів = 0x47", size=9, color=INK))
    p.append(text(90, y1 + 46, "Синхромаркер", size=9, color=MUTED))

    # Байт 2-3 (старші біти): TEI, PUSI, Priority
    p.append(rect(144, y1, 56, 56, fill="#fee2e2", stroke="#ef4444", sw=1.4, rx=3))
    p.append(text(172, y1 + 17, "TEI", size=10, bold=True, color="#b91c1c"))
    p.append(text(172, y1 + 32, "1 біт", size=9, color=INK))
    p.append(text(172, y1 + 46, "Помилка", size=9, color=MUTED))

    p.append(rect(204, y1, 56, 56, fill="#fef9c3", stroke="#ca8a04", sw=1.4, rx=3))
    p.append(text(232, y1 + 17, "PUSI", size=10, bold=True, color="#854d0e"))
    p.append(text(232, y1 + 32, "1 біт", size=9, color=INK))
    p.append(text(232, y1 + 46, "Старт", size=9, color=MUTED))

    p.append(rect(264, y1, 56, 56, fill="#f1f5f9", stroke="#64748b", sw=1.4, rx=3))
    p.append(text(292, y1 + 17, "Priority", size=9, bold=True, color="#334155"))
    p.append(text(292, y1 + 32, "1 біт", size=9, color=INK))
    p.append(text(292, y1 + 46, "Пріоритет", size=9, color=MUTED))

    # PID (13 бітів)
    p.append(rect(324, y1, 160, 56, fill="#e0e7ff", stroke="#4f46e5", sw=1.4, rx=3))
    p.append(text(404, y1 + 17, "PID (Packet Identifier)", size=10, bold=True, color="#4338ca"))
    p.append(text(404, y1 + 32, "13 бітів (0x0000..0x1FFF)", size=9, color=INK))
    p.append(text(404, y1 + 46, "Ідентифікатор потоку", size=9, color=MUTED))

    # TSC (2 біти)
    p.append(rect(488, y1, 80, 56, fill="#f1f5f9", stroke="#64748b", sw=1.4, rx=3))
    p.append(text(528, y1 + 17, "TSC", size=10, bold=True, color="#334155"))
    p.append(text(528, y1 + 32, "2 біти", size=9, color=INK))
    p.append(text(528, y1 + 46, "Шифрування", size=9, color=MUTED))

    # AFC (2 біти)
    p.append(rect(572, y1, 120, 56, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=3))
    p.append(text(632, y1 + 17, "Adaptation Ctrl", size=10, bold=True, color="#b45309"))
    p.append(text(632, y1 + 32, "2 біти (01, 10, 11)", size=9, color=INK))
    p.append(text(632, y1 + 46, "Наявність AF/Payload", size=9, color=MUTED))

    # CC (4 біти)
    p.append(rect(696, y1, 104, 56, fill="#dcfce7", stroke=POS, sw=1.4, rx=3))
    p.append(text(748, y1 + 17, "Continuity", size=10, bold=True, color=POS))
    p.append(text(748, y1 + 32, "4 біти (0..15)", size=9, color=INK))
    p.append(text(748, y1 + 46, "Лічильник втрат", size=9, color=MUTED))

    # Розгортка Адаптаційного поля
    p.append(text(40, 220, "2. Внутрішня будова адаптаційного поля (Adaptation Field):", size=11, bold=True, color=INK, anchor="start"))

    y2 = 236
    p.append(rect(40, y2, 84, 54, fill="#fffbeb", stroke="#d97706", sw=1.3, rx=3))
    p.append(text(82, y2 + 18, "AF Length", size=9, bold=True, color="#b45309"))
    p.append(text(82, y2 + 33, "1 байт", size=9, color=INK))
    p.append(text(82, y2 + 46, "Довжина поля", size=9, color=MUTED))

    p.append(rect(128, y2, 136, 54, fill="#fffbeb", stroke="#d97706", sw=1.3, rx=3))
    p.append(text(196, y2 + 18, "8 прапорців (Flags)", size=9, bold=True, color="#b45309"))
    p.append(text(196, y2 + 33, "PCR, OPCR, Splicing...", size=9, color=INK))
    p.append(text(196, y2 + 46, "1 байт конфігурації", size=9, color=MUTED))

    p.append(rect(268, y2, 230, 54, fill="#fef3c7", stroke="#d97706", sw=1.3, rx=3))
    p.append(text(383, y2 + 18, "PCR (Program Clock Reference)", size=9, bold=True, color="#b45309"))
    p.append(text(383, y2 + 33, "Base (33 b, 90 kHz) + Ext (9 b, 27 MHz)", size=9, color=INK))
    p.append(text(383, y2 + 46, "Синхронізація опорного генератора", size=9, color=MUTED))

    p.append(rect(502, y2, 298, 54, fill="#f8fafc", stroke="#94a3b8", sw=1.3, rx=3))
    p.append(text(651, y2 + 18, "Байтове набивання (Stuffing Bytes)", size=9, bold=True, color="#475569"))
    p.append(text(651, y2 + 33, "Послідовність байтів 0xFF до кінця пакета", size=9, color=INK))
    p.append(text(651, y2 + 46, "Вирівнювання довжини пакетів CBR", size=9, color=MUTED))

    # Підсумкові виноски правил
    y3 = 312
    p.append(rect(40, y3, 760, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(55, y3 + 20, "Ключові інваріанти формату:", size=10, bold=True, color=INK, anchor="start"))
    p.append(text(55, y3 + 40, "• Завжди рівно 188 байтів: апаратні DVB/ATSC приймачі синхронізуються за першим байтом 0x47 кожні 188 октетів.", size=9, color=INK, anchor="start"))
    p.append(text(55, y3 + 58, "• PUSI = 1: вказує на початок нового кадру PES (відео/аудіо) або наявність Pointer Field для таблиць PSI.", size=9, color=INK, anchor="start"))
    p.append(text(55, y3 + 76, "• Continuity Counter (4 біти): інкрементується від 0 до 15 для кожного наступного пакета з тим самим PID.", size=9, color=INK, anchor="start"))
    p.append(text(55, y3 + 94, "• Null Packet (PID 0x1FFF): заповнювальний порожній пакет для вирівнювання постійного бітрейту (CBR) каналу.", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "ts-packet-structure.svg"), W, H, *p,
           title="Анатомія 188-байтного пакета MPEG-TS")


# ── 2. ts-multiplexing-pipeline: Мультиплексування елементарних потоків ───────
def fig_ts_multiplexing_pipeline():
    W, H = 840, 410
    p = []

    p.append(text(40, 24, "Конвеєр мультиплексування: від медіапотоків (ES) до транспортного потоку (TS)", size=13, bold=True, color=INK, anchor="start"))

    # Рівень 1: Elementary Streams (ES)
    y_es = 52
    p.append(text(40, y_es + 22, "1. Елементарні потоки (ES):", size=10, bold=True, color=INK, anchor="start"))

    p.append(rect(230, y_es, 160, 38, fill="#eff6ff", stroke=NEG, sw=1.4, rx=4))
    p.append(text(310, y_es + 16, "Відео (H.264 / HEVC)", size=10, bold=True, color=NEG))
    p.append(text(310, y_es + 30, "Кадри I, P, B", size=9, color=MUTED))

    p.append(rect(420, y_es, 160, 38, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=4))
    p.append(text(500, y_es + 16, "Аудіо (AAC / AC-3)", size=10, bold=True, color="#b45309"))
    p.append(text(500, y_es + 30, "Аудіоссемпли 48 кГц", size=9, color=MUTED))

    p.append(rect(610, y_es, 180, 38, fill="#f3e8ff", stroke="#9333ea", sw=1.4, rx=4))
    p.append(text(700, y_es + 16, "Телеметрія (KLV / Data)", size=10, bold=True, color="#7e22ce"))
    p.append(text(700, y_es + 30, "Координати дрона, кути", size=9, color=MUTED))

    # Стрілки вниз до PES
    p.append(arrow(310, y_es + 40, 310, y_es + 64, color=NEG, sw=1.5))
    p.append(arrow(500, y_es + 40, 500, y_es + 64, color="#d97706", sw=1.5))
    p.append(arrow(700, y_es + 40, 700, y_es + 64, color="#9333ea", sw=1.5))

    # Рівень 2: PES (Packetized Elementary Stream)
    y_pes = 122
    p.append(text(40, y_pes + 22, "2. Пакетизація PES:", size=10, bold=True, color=INK, anchor="start"))

    p.append(rect(200, y_pes, 220, 44, fill="#dbeafe", stroke=NEG, sw=1.4, rx=4))
    p.append(text(310, y_pes + 17, "Відео PES (PTS / DTS)", size=10, bold=True, color=NEG))
    p.append(text(310, y_pes + 33, "Префікс 0x000001 + мітки часу", size=9, color=MUTED))

    p.append(rect(450, y_pes, 160, 44, fill="#fef3c7", stroke="#d97706", sw=1.4, rx=4))
    p.append(text(530, y_pes + 17, "Аудіо PES (PTS)", size=10, bold=True, color="#b45309"))
    p.append(text(530, y_pes + 33, "Синхронізація звуку", size=9, color=MUTED))

    p.append(rect(630, y_pes, 160, 44, fill="#f3e8ff", stroke="#9333ea", sw=1.4, rx=4))
    p.append(text(710, y_pes + 17, "Data PES (PTS)", size=10, bold=True, color="#7e22ce"))
    p.append(text(710, y_pes + 33, "Прив'язка метаданих", size=9, color=MUTED))

    # Стрілки вниз до TS Мультиплексора
    p.append(arrow(310, y_pes + 46, 380, y_pes + 80, color=NEG, sw=1.5))
    p.append(arrow(530, y_pes + 46, 450, y_pes + 80, color="#d97706", sw=1.5))
    p.append(arrow(710, y_pes + 46, 520, y_pes + 80, color="#9333ea", sw=1.5))

    # Генератор таблиць PSI
    p.append(rect(40, y_pes + 72, 140, 50, fill="#fee2e2", stroke="#ef4444", sw=1.4, rx=4))
    p.append(text(110, y_pes + 90, "Таблиці PSI/SI", size=10, bold=True, color="#b91c1c"))
    p.append(text(110, y_pes + 107, "PAT (PID 0), PMT (PID X)", size=9, color=MUTED))
    p.append(arrow(182, y_pes + 97, 320, y_pes + 105, color="#ef4444", sw=1.5))

    # Рівень 3: Мультиплексор TS
    y_mux = 208
    p.append(rect(320, y_mux, 260, 42, fill="#f1f5f9", stroke="#334155", sw=1.6, rx=6))
    p.append(text(450, y_mux + 18, "MPEG-TS Мультиплексор", size=11, bold=True, color="#1e293b"))
    p.append(text(450, y_mux + 33, "Фрагментація на 188 B, вставка PCR, чергування", size=9, color=MUTED))

    p.append(arrow(450, y_mux + 44, 450, y_mux + 70, color=INK, sw=1.8))

    # Рівень 4: Єдиний потік 188-байтних пакетів
    y_ts = 288
    p.append(text(40, y_ts + 24, "3. Результуючий потік TS:", size=10, bold=True, color=INK, anchor="start"))

    packets = [
        ("PAT", "PID 0x0000", "#fee2e2", "#b91c1c"),
        ("PMT", "PID 0x0100", "#fecdd3", "#be123c"),
        ("Video 1", "PID 0x0101", "#dbeafe", NEG),
        ("Video 2", "PID 0x0101", "#eff6ff", NEG),
        ("Audio", "PID 0x0102", "#fef3c7", "#b45309"),
        ("Video 3", "PID 0x0101", "#dbeafe", NEG),
        ("KLV Meta", "PID 0x0103", "#f3e8ff", "#7e22ce"),
        ("Null Pkt", "PID 0x1FFF", "#f1f5f9", "#64748b"),
    ]

    px = 200
    pw = 72
    for name, desc, bg, border in packets:
        p.append(rect(px, y_ts, pw, 54, fill=bg, stroke=border, sw=1.4, rx=3))
        p.append(text(px + pw/2, y_ts + 18, name, size=9, bold=True, color=border))
        p.append(text(px + pw/2, y_ts + 33, desc, size=9, color=INK))
        p.append(text(px + pw/2, y_ts + 46, "188 B", size=9, color=MUTED))
        px += pw + 4

    p.append(text(W / 2, H - 14, "Мультиплексор нарізає великі кадри PES на 188-байтні пакети та чергує їх у часі зі службовими таблицями PSI",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "ts-multiplexing-pipeline.svg"), W, H, *p,
           title="Конвеєр мультиплексування потоків MPEG-TS")


# ── 3. psi-table-hierarchy: Деревоподібний розбір таблиць PSI ─────────────────
def fig_psi_table_hierarchy():
    W, H = 840, 400
    p = []

    p.append(text(40, 24, "Ієрархія та демультиплексування службових таблиць PSI (Program Specific Information)", size=13, bold=True, color=INK, anchor="start"))

    # Рівень 0: Корінь — Фіксований PID 0x0000 (PAT)
    x_pat, y_pat = 140, 80
    p.append(rect(x_pat - 100, y_pat, 200, 75, fill="#fee2e2", stroke="#ef4444", sw=1.8, rx=6))
    p.append(text(x_pat, y_pat + 22, "PAT (PID 0x0000)", size=12, bold=True, color="#b91c1c"))
    p.append(text(x_pat, y_pat + 42, "Program Association Table", size=10, color=INK))
    p.append(text(x_pat, y_pat + 60, "Стартовий якір для всього потоку", size=9, color=MUTED))

    # Стрілки від PAT до PMT
    p.append(arrow(x_pat + 102, y_pat + 25, 340, 70, color="#ef4444", sw=1.6))
    p.append(arrow(x_pat + 102, y_pat + 50, 340, 180, color="#ef4444", sw=1.6))

    # Рівень 1: PMT (Program Map Tables)
    # Програма 1 (Телеканал / Головна камера)
    p.append(rect(345, 45, 190, 70, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=5))
    p.append(text(440, 66, "PMT (Програма 1)", size=11, bold=True, color="#b45309"))
    p.append(text(440, 84, "PID = 0x0100", size=10, bold=True, color=INK))
    p.append(text(440, 101, "PCR PID = 0x0101", size=9, color=MUTED))

    # Програма 2 (Тепловізор / Інший канал)
    p.append(rect(345, 150, 190, 70, fill="#fef3c7", stroke="#d97706", sw=1.6, rx=5))
    p.append(text(440, 171, "PMT (Програма 2)", size=11, bold=True, color="#b45309"))
    p.append(text(440, 189, "PID = 0x0200", size=10, bold=True, color=INK))
    p.append(text(440, 206, "PCR PID = 0x0201", size=9, color=MUTED))

    # Стрілки від PMT 1 до потоків Програми 1
    p.append(arrow(537, 55, 620, 40, color="#d97706", sw=1.4))
    p.append(arrow(537, 75, 620, 85, color="#d97706", sw=1.4))
    p.append(arrow(537, 95, 620, 130, color="#d97706", sw=1.4))

    # Потоки Програми 1
    p.append(rect(625, 20, 180, 38, fill="#dbeafe", stroke=NEG, sw=1.3, rx=4))
    p.append(text(715, 36, "Відео (H.264) — PID 0x0101", size=9, bold=True, color=NEG))
    p.append(text(715, 50, "Stream Type 0x1B", size=9, color=MUTED))

    p.append(rect(625, 65, 180, 38, fill="#fef9c3", stroke="#ca8a04", sw=1.3, rx=4))
    p.append(text(715, 81, "Аудіо (AAC) — PID 0x0102", size=9, bold=True, color="#854d0e"))
    p.append(text(715, 95, "Stream Type 0x0F", size=9, color=MUTED))

    p.append(rect(625, 110, 180, 38, fill="#f3e8ff", stroke="#9333ea", sw=1.3, rx=4))
    p.append(text(715, 126, "KLV Телеметрія — PID 0x0103", size=9, bold=True, color="#7e22ce"))
    p.append(text(715, 140, "Stream Type 0x06 (Data)", size=9, color=MUTED))

    # Стрілки від PMT 2 до потоків Програми 2
    p.append(arrow(537, 175, 620, 180, color="#d97706", sw=1.4))
    p.append(arrow(537, 195, 620, 225, color="#d97706", sw=1.4))

    # Потоки Програми 2
    p.append(rect(625, 165, 180, 38, fill="#dbeafe", stroke=NEG, sw=1.3, rx=4))
    p.append(text(715, 181, "Відео Thermal — PID 0x0201", size=9, bold=True, color=NEG))
    p.append(text(715, 195, "Stream Type 0x24 (HEVC)", size=9, color=MUTED))

    p.append(rect(625, 210, 180, 38, fill="#f3e8ff", stroke="#9333ea", sw=1.3, rx=4))
    p.append(text(715, 226, "Метадані цілей — PID 0x0202", size=9, bold=True, color="#7e22ce"))
    p.append(text(715, 240, "Stream Type 0x06 (Data)", size=9, color=MUTED))

    # Інформаційна плашка знизу
    y_bot = 270
    p.append(rect(40, y_bot, 765, 105, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(55, y_bot + 20, "Алгоритм пошуку медіапотоків у невідомому TS-потоці:", size=10, bold=True, color=INK, anchor="start"))
    p.append(text(55, y_bot + 40, "1. Приймач слухає пакети з фіксованим PID 0x0000 і читає таблицю PAT.", size=9, color=INK, anchor="start"))
    p.append(text(55, y_bot + 58, "2. З PAT вибирається номер потрібної програми та дізнається PID відповідної таблиці PMT (наприклад, 0x0100).", size=9, color=INK, anchor="start"))
    p.append(text(55, y_bot + 76, "3. З PMT зчитуються типи дескрипторів та PID елементарних потоків (відео, аудіо, телеметрія) і опорний PCR PID.", size=9, color=INK, anchor="start"))
    p.append(text(55, y_bot + 94, "4. Демодулятор/демультиплексор налаштовує апаратні PID-фільтри на виділені потоки.", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "psi-table-hierarchy.svg"), W, H, *p,
           title="Ієрархія таблиць PSI в MPEG-TS")


# ── 4. pcr-pts-dts-timeline: Синхронізація часу PCR, PTS та DTS ───────────────
def fig_pcr_pts_dts_timeline():
    W, H = 840, 400
    p = []

    p.append(text(40, 24, "Часова синхронізація в MPEG-TS: опорний годинник PCR проти міток PTS/DTS", size=13, bold=True, color=INK, anchor="start"))

    # Верхня шкала: Опорний годинник 27 МГц (PCR)
    y_pcr = 56
    p.append(rect(40, y_pcr, 760, 72, fill="#eff6ff", stroke=NEG, sw=1.4, rx=6))
    p.append(text(55, y_pcr + 20, "Опорна часова база передавача: System Time Clock (STC 27 МГц)", size=10, bold=True, color=NEG, anchor="start"))
    p.append(text(55, y_pcr + 36, "Передається через регулярні мітки PCR в адаптаційних полях кожні 20..40 мс", size=9, color=MUTED, anchor="start"))

    # Точки PCR на часовій осі
    p.append(line(55, y_pcr + 54, 770, y_pcr + 54, color=NEG, sw=1.5))
    for t_x, lbl in [(120, "PCR₁ = 0.00 s"), (320, "PCR₂ = 0.04 s"), (520, "PCR₃ = 0.08 s"), (720, "PCR₄ = 0.12 s")]:
        p.append(circle(t_x, y_pcr + 54, 4, fill=NEG))
        p.append(text(t_x, y_pcr + 67, lbl, size=9, color=NEG))

    # Стрілка синхронізації генератора PLL приймача
    p.append(arrow(440, y_pcr + 74, 440, y_pcr + 100, color="#4f46e5", sw=1.8))
    p.append(text(450, y_pcr + 90, "Синхронізація частоти генератора (PLL/VCXO)", size=9, color="#4f46e5", bold=True, anchor="start"))

    # Нижня шкала: Декодування (DTS) та Відображення (PTS) для кадрів I, P, B
    y_pes = 180
    p.append(rect(40, y_pes, 760, 195, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(55, y_pes + 20, "Часова шкала представлення медіа (90 кГц): DTS (декодування) vs PTS (показ на екрані)", size=10, bold=True, color=INK, anchor="start"))

    frames = [
        ("I₁ (Keyframe)", "DTS = 100 ms", "PTS = 180 ms", 70, "#fee2e2", "#b91c1c"),
        ("P₄ (Ref Frame)", "DTS = 140 ms", "PTS = 300 ms", 215, "#dbeafe", NEG),
        ("B₂ (Bi-dir)", "DTS = 180 ms", "PTS = 220 ms", 360, "#fef9c3", "#854d0e"),
        ("B₃ (Bi-dir)", "DTS = 220 ms", "PTS = 260 ms", 505, "#fef9c3", "#854d0e"),
        ("P₇ (Ref Frame)", "DTS = 260 ms", "PTS = 420 ms", 650, "#dbeafe", NEG),
    ]

    for title, dts_lbl, pts_lbl, fx, bg, border in frames:
        p.append(rect(fx, y_pes + 36, 135, 84, fill=bg, stroke=border, sw=1.4, rx=4))
        p.append(text(fx + 67, y_pes + 53, title, size=10, bold=True, color=border))
        p.append(text(fx + 67, y_pes + 73, dts_lbl, size=9, bold=True, color="#334155"))
        p.append(text(fx + 67, y_pes + 92, pts_lbl, size=9, bold=True, color=POS))
        p.append(text(fx + 67, y_pes + 108, "(DTS ≠ PTS)" if "B" not in title else "(Двосторонній)", size=9, color=MUTED))

    # Пояснення знизу
    p.append(text(55, y_pes + 140, "• PCR (27 МГц): усуває дрейф фізичного кварцового генератора приймача, гарантуючи рівномірність споживання буфера.", size=9, color=INK, anchor="start"))
    p.append(text(55, y_pes + 158, "• DTS (90 кГц): вказує точний момент вилучення стисненого кадру з буфера та подачі на відеодекодер.", size=9, color=INK, anchor="start"))
    p.append(text(55, y_pes + 176, "• PTS (90 кГц): вказує момент рендерингу оцифрованого зображення на дисплеї, узгоджуючи відео зі звуком (Lip Sync).", size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "pcr-pts-dts-timeline.svg"), W, H, *p,
           title="Синхронізація часу PCR, PTS і DTS")


# ── 5. loss-and-resync-state: Стійкість до втрат і скінченний автомат ─────────
def fig_loss_and_resync_state():
    W, H = 840, 380
    p = []

    p.append(text(40, 24, "Скінченний автомат синхронізації та обробка втрат у завадозахищеному радіоканалі", size=13, bold=True, color=INK, anchor="start"))

    # Стан 1: Пошук байта синхронізації (Sync Search)
    s1_x, s1_y = 150, 115
    p.append(rect(s1_x - 95, s1_y - 48, 190, 96, fill="#fee2e2", stroke="#ef4444", sw=1.8, rx=6))
    p.append(text(s1_x, s1_y - 22, "1. Пошук синхронізації", size=11, bold=True, color="#b91c1c"))
    p.append(text(s1_x, s1_y, "Побайтний зсув буфера", size=9, color=INK))
    p.append(text(s1_x, s1_y + 19, "Очікування 0x47", size=9, bold=True, color="#b91c1c"))
    p.append(text(s1_x, s1_y + 36, "Скидання демультиплексора", size=9, color=MUTED))

    # Стан 2: Підтвердження кадрування (Pre-Sync)
    s2_x, s2_y = 420, 115
    p.append(rect(s2_x - 105, s2_y - 48, 210, 96, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    p.append(text(s2_x, s2_y - 22, "2. Підтвердження періоду", size=11, bold=True, color="#b45309"))
    p.append(text(s2_x, s2_y, "Перевірка N наступних", size=9, color=INK))
    p.append(text(s2_x, s2_y + 19, "байтів 0x47 з кроком 188 B", size=9, bold=True, color="#b45309"))
    p.append(text(s2_x, s2_y + 36, "Захист від 0x47 у даних", size=9, color=MUTED))

    # Стан 3: Синхронізація зафіксована (In-Sync / Lock)
    s3_x, s3_y = 690, 115
    p.append(rect(s3_x - 95, s3_y - 48, 190, 96, fill="#dcfce7", stroke=POS, sw=1.8, rx=6))
    p.append(text(s3_x, s3_y - 22, "3. Захоплення (Locked)", size=11, bold=True, color=POS))
    p.append(text(s3_x, s3_y, "Нормальний демультиплекс", size=9, color=INK))
    p.append(text(s3_x, s3_y + 19, "Перевірка CC та TEI", size=9, bold=True, color=POS))
    p.append(text(s3_x, s3_y + 36, "Потік іде в декодер", size=9, color=MUTED))

    # Переходи між станами
    p.append(arrow(s1_x + 98, s1_y - 15, s2_x - 108, s1_y - 15, color="#d97706", sw=1.6))
    p.append(text((s1_x + s2_x)/2, s1_y - 27, "Знайдено перший 0x47", size=9, color="#d97706", bold=True))

    p.append(arrow(s2_x + 108, s1_y - 15, s3_x - 98, s1_y - 15, color=POS, sw=1.6))
    p.append(text((s2_x + s3_x)/2, s1_y - 27, "3..5 валідних пакетів підряд", size=9, color=POS, bold=True))

    # Зворотний перехід при збої
    p.append(arrow(s2_x - 40, s2_y + 50, s1_x + 40, s1_y + 50, color="#ef4444", sw=1.4))
    p.append(text((s1_x + s2_x)/2, s1_y + 64, "Крок ≠ 188 B (фальшивий старт)", size=9, color="#ef4444"))

    p.append(arrow(s3_x, s3_y + 50, s1_x, s1_y + 74, color="#ef4444", sw=1.5))
    p.append(text(420, s1_y + 86, "Втрата 3+ маркерів 0x47 поспіль → зрив синхронізації", size=9, color="#ef4444", bold=True))

    # Нижня панель: Обробка Continuity Counter та TEI
    y_bot = 240
    p.append(rect(40, y_bot, 760, 120, fill="#f8fafc", stroke="#cbd5e1", sw=1.3, rx=6))
    p.append(text(55, y_bot + 20, "Реакція на пошкодження окремих пакетів у радіоефірі (DVB-T / Відео з дрона):", size=10, bold=True, color=INK, anchor="start"))
    p.append(text(55, y_bot + 42, "• TEI (Transport Error Indicator) = 1: демодулятор не зміг виправити біти кодом Reed-Solomon/LDPC. Пакет відкидається.", size=9, color=INK, anchor="start"))
    p.append(text(55, y_bot + 62, "• Розрив Continuity Counter (наприклад, 4 → 7): демультиплексор фіксує втрату 2 пакетів і скидає поточний PES-кадр.", size=9, color=INK, anchor="start"))
    p.append(text(55, y_bot + 82, "• Автоматичне відновлення: наступний пакет з PUSI = 1 починає новий чистий кадр I/P без зависання всього потоку.", size=9, color=POS, anchor="start"))
    p.append(text(55, y_bot + 102, "• Ізоляція програм: пошкодження пакетів однієї програми (PID X) не впливає на декодування інших (PID Y).", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "loss-and-resync-state.svg"), W, H, *p,
           title="Автомат синхронізації та обробка втрат у радіоефірі")


def main():
    fig_ts_packet_structure()
    fig_ts_multiplexing_pipeline()
    fig_psi_table_hierarchy()
    fig_pcr_pts_dts_timeline()
    fig_loss_and_resync_state()
    print("MPEG-TS figures generated successfully in ./img/")

if __name__ == "__main__":
    main()
