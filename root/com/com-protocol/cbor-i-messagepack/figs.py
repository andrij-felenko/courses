# -*- coding: utf-8 -*-
"""Фігури до теми «CBOR і MessagePack: JSON, що влазить у пакет»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Анатомія початкового байта CBOR та шкала довжин
# ─────────────────────────────────────────────────────────────────────────────
def fig_cbor_type_byte_layout():
    W, H = 1000, 560
    f = []

    # Головна підкладка
    f.append(rect(20, 20, 960, 520, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))

    f.append(text(40, 52, "Анатомія початкового байта CBOR (RFC 8949)", size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 76, "8 бітів заголовка: 3 біти старшого типу (Major Type) + 5 бітів додаткової інформації (Additional Info)", size=12, color=MUTED, anchor="start"))

    # Байт заголовка
    bx, by = 40, 100
    # 3 біти Major Type
    f.append(rect(bx, by, 320, 70, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    f.append(text(bx + 160, by + 30, "Major Type (3 біти)", size=13, color="#1e40af", bold=True))
    f.append(text(bx + 160, by + 52, "Біти 7 .. 5: значення 0 .. 7", size=11, color="#1e40af"))

    # 5 бітів Additional Info
    f.append(rect(bx + 330, by, 590, 70, fill="#fdf4ff", stroke="#a855f7", sw=1.5, rx=6))
    f.append(text(bx + 625, by + 30, "Additional Information (5 бітів)", size=13, color="#6b21a8", bold=True))
    f.append(text(bx + 625, by + 52, "Біти 4 .. 0: пряме значення (0..23), формат розширення (24..27) або маркер (31)", size=11, color="#6b21a8"))

    # Таблиця 8 Major Types (ліворуч)
    tx, ty = 40, 190
    f.append(rect(tx, ty, 420, 330, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    f.append(text(tx + 20, ty + 28, "8 головних типів даних (Major Types 0..7)", size=13, color=INK, anchor="start", bold=True))

    mtypes = [
        ("0: Unsigned Integer", "uint: 0 .. 2^64 - 1", "#2563eb"),
        ("1: Negative Integer", "int: -1 - n (-1 .. -2^64)", "#0284c7"),
        ("2: Byte String", "bstr: сирий масив байтів (довжина L)", "#059669"),
        ("3: Text String", "tstr: валідний UTF-8 рядок (довжина L)", "#16a34a"),
        ("4: Array of items", "list: масив довільних елементів", "#d97706"),
        ("5: Map of pairs", "dict: пари ключ-значення (2L елементів)", "#ea580c"),
        ("6: Semantic Tag", "tag: розширення (дати, UUID, bignum)", "#7c3aed"),
        ("7: Simple / Floats", "bool, null, float16/32/64, Break", "#db2777"),
    ]

    for i, (m_name, m_desc, col) in enumerate(mtypes):
        yy = ty + 46 + i * 34
        f.append(rect(tx + 15, yy, 160, 26, fill="#ffffff", stroke=col, sw=1.2, rx=4))
        f.append(text(tx + 95, yy + 17, m_name, size=11, color=col, bold=True))
        f.append(text(tx + 185, yy + 17, m_desc, size=10.5, color=INK, anchor="start"))

    # Таблиця Additional Info Ladder (праворуч)
    lx, ly = 480, 190
    f.append(rect(lx, ly, 480, 330, fill="#faf5ff", stroke="#e9d5ff", sw=1.2, rx=8))
    f.append(text(lx + 20, ly + 28, "Шкала розширення довжини (Additional Info)", size=13, color="#6b21a8", anchor="start", bold=True))

    ladders = [
        ("0 .. 23", "Пряме значення", "Значення 0..23 зберігається в самому заголовку (1 байт разом)", "#16a34a"),
        ("24 (0x18)", "+1 байт uint8", "Наступний 1 байт несе значення 24 .. 255", "#0284c7"),
        ("25 (0x19)", "+2 байти uint16", "Наступні 2 байти несе значення 256 .. 65 535 (Big-Endian)", "#2563eb"),
        ("26 (0x1A)", "+4 байти uint32", "Наступні 4 байти несе значення до 4 294 967 295 (Big-Endian)", "#7c3aed"),
        ("27 (0x1B)", "+8 байтів uint64", "Наступні 8 байтів несе значення до 2^64 - 1 (Big-Endian)", "#9333ea"),
        ("28 .. 30", "Зарезервовано", "Не використовується у стандарті RFC 8949", "#94a3b8"),
        ("31 (0x1F)", "Indefinite length", "Потоковий режим без фіксованої довжини; кінець — маркер 0xFF", "#dc2626"),
    ]

    for i, (l_code, l_type, l_desc, col) in enumerate(ladders):
        yy = ly + 46 + i * 38
        f.append(rect(lx + 15, yy, 95, 28, fill="#ffffff", stroke=col, sw=1.2, rx=4))
        f.append(text(lx + 62, yy + 18, l_code, size=11, color=col, bold=True))
        f.append(text(lx + 120, yy + 13, l_type, size=11, color=INK, anchor="start", bold=True))
        f.append(text(lx + 120, yy + 26, l_desc, size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "cbor-type-byte-layout.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Порівняння розкладки байтів: JSON vs MessagePack vs CBOR vs Raw binary
# ─────────────────────────────────────────────────────────────────────────────
def fig_cbor_vs_msgpack_wire():
    W, H = 1000, 600
    f = []

    f.append(rect(20, 20, 960, 560, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))
    f.append(text(40, 52, "Порівняння упаковки повідомлення у форматах даних", size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 76, "Телеметрія: sensor_id=1, temp=23.5°C, ok=true — розмір, накладні метадані та самоописовість", size=12, color=MUTED, anchor="start"))

    formats = [
        ("1. JSON (текстовий формат, RFC 8259)", 42, "#fee2e2", "#ef4444", [
            ("{\"temp\":23.5,\"id\":1,\"ok\":true}", 42, "Символи ASCII: лапки, двокрапки, коми, числа текстом; 42 байти")
        ]),
        ("2. MessagePack (бінарний з рядковими ключами)", 22, "#fef3c7", "#f59e0b", [
            ("83", 1, "fixmap(3)"),
            ("A4 74 65 6D 70", 5, "fixstr(4): \"temp\""),
            ("CA 41 BC 00 00", 5, "float32: 23.5"),
            ("A2 69 64", 3, "fixstr(2): \"id\""),
            ("01", 1, "pos fixint: 1"),
            ("A2 6F 6B", 3, "fixstr(2): \"ok\""),
            ("C3", 1, "true (0xC3)"),
        ]),
        ("3. CBOR (бінарний з цілочисельними ключами)", 9, "#dcfce7", "#10b981", [
            ("A3", 1, "map(3)"),
            ("01", 1, "key 1 (temp)"),
            ("F9 51 E0", 3, "float16: 23.5 (0x51E0)"),
            ("02", 1, "key 2 (id)"),
            ("01", 1, "val 1"),
            ("03", 1, "key 3 (ok)"),
            ("F5", 1, "true (0xF5)"),
        ]),
        ("4. Raw C-Struct (пам'ять без метаданих)", 8, "#eff6ff", "#3b82f6", [
            ("00 00 BC 41", 4, "float temp (LE)"),
            ("01", 1, "uint8 id"),
            ("01", 1, "uint8 ok"),
            ("00 00", 2, "2 байти вирівнювання (padding)"),
        ])
    ]

    y_pos = 100
    for title, total_bytes, bg_col, br_col, chunks in formats:
        f.append(rect(40, y_pos, 920, 105, fill=bg_col, stroke=br_col, sw=1.2, rx=8))
        f.append(text(55, y_pos + 24, title, size=12.5, color=INK, anchor="start", bold=True))
        f.append(rect(840, y_pos + 10, 105, 24, fill=br_col, stroke=br_col, rx=4))
        f.append(text(892, y_pos + 26, "%d байтів" % total_bytes, size=11, color="#ffffff", bold=True))

        # Відмальовка чанків
        cx = 55
        cy = y_pos + 42
        for hex_str, byte_cnt, desc in chunks:
            box_w = max(len(hex_str) * 8 + 16, 60)
            if box_w + cx > 940:
                box_w = 940 - cx
            f.append(rect(cx, cy, box_w, 24, fill="#ffffff", stroke=br_col, sw=1, rx=4))
            f.append(text(cx + box_w / 2, cy + 16, hex_str, size=10, color=INK, bold=True))
            cx += box_w + 6

        # Опис під чанками
        desc_summary = "   |   ".join("%s: %s" % (c[0], c[2]) for c in chunks[:4])
        if len(chunks) > 4:
            desc_summary += "   |   ..."
        f.append(text(55, y_pos + 90, desc_summary, size=9.5, color=MUTED, anchor="start"))

        y_pos += 115

    render(os.path.join(OUT, "cbor-vs-msgpack-wire.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Модель пам'яті Zero-Copy: потоковий парсер на MCU без динамічної купи
# ─────────────────────────────────────────────────────────────────────────────
def fig_zero_copy_token_stream():
    W, H = 1000, 540
    f = []

    f.append(rect(20, 20, 960, 500, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))
    f.append(text(40, 52, "Модель пам'яті Zero-Copy декодера CBOR на мікроконтролері", size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 76, "Зрізи даних (Slices / spans) посилаються безпосередньо на буфер прийому без malloc() і дублювання в RAM", size=12, color=MUTED, anchor="start"))

    # Вхідний кільцевий / статичний буфер UART/DMA
    bx, by = 40, 105
    f.append(rect(bx, by, 920, 90, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(bx + 20, by + 26, "Статичний буфер прийому (DMA / RX Buffer у SRAM): uint8_t rx_buf[256]", size=12, color=INK, anchor="start", bold=True))

    bytes_seq = [
        ("0x83", "arr(3)", "#64748b"),
        ("0x64", "tstr(4)", "#0284c7"),
        ("0x73", "'s'", "#0369a1"),
        ("0x79", "'y'", "#0369a1"),
        ("0x6E", "'n'", "#0369a1"),
        ("0x63", "'c'", "#0369a1"),
        ("0x44", "bstr(4)", "#059669"),
        ("0xDE", "0xDE", "#047857"),
        ("0xAD", "0xAD", "#047857"),
        ("0xBE", "0xBE", "#047857"),
        ("0xEF", "0xEF", "#047857"),
        ("0x18", "u8: 42", "#d97706"),
        ("0x2A", "42", "#d97706"),
    ]

    cx = bx + 20
    for i, (bval, blbl, bcol) in enumerate(bytes_seq):
        f.append(rect(cx, by + 38, 62, 40, fill="#ffffff", stroke=bcol, sw=1.2, rx=4))
        f.append(text(cx + 31, by + 54, bval, size=11, color=bcol, bold=True))
        f.append(text(cx + 31, by + 70, blbl, size=9.5, color=MUTED))
        cx += 68

    f.append(rect(cx, by + 38, 120, 40, fill="#f1f5f9", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(cx + 60, by + 62, "вільні байти...", size=10, color=MUTED))

    # Стрілки посилань
    # Текстовий зріз: байти 2..5
    f.append(line(bx + 20 + 2 * 68 + 31, by + 80, bx + 150, 240, color="#0284c7", sw=1.5))
    # Бінарний зріз: байти 7..10
    f.append(line(bx + 20 + 7 * 68 + 31, by + 80, bx + 490, 240, color="#059669", sw=1.5))

    # Токен-структури в стеку процесора
    # Блок 1: Text String Slice
    f.append(rect(40, 245, 290, 160, fill="#f0f9ff", stroke="#0284c7", sw=1.2, rx=8))
    f.append(text(55, 272, "cbor_slice_t (Text String)", size=12, color="#0369a1", anchor="start", bold=True))
    f.append(text(55, 296, "const uint8_t *ptr = &rx_buf[2]", size=11, color=INK, anchor="start"))
    f.append(text(55, 318, "size_t len = 4", size=11, color=INK, anchor="start"))
    f.append(text(55, 340, "cbor_type_t type = CBOR_TSTR", size=11, color=MUTED, anchor="start"))
    f.append(rect(55, 355, 260, 34, fill="#ffffff", stroke="#0284c7", rx=4))
    f.append(text(185, 376, "std::string_view(\"sync\")", size=10.5, color="#0284c7", bold=True))

    # Блок 2: Binary Payload Slice
    f.append(rect(350, 245, 290, 160, fill="#ecfdf5", stroke="#059669", sw=1.2, rx=8))
    f.append(text(365, 272, "cbor_slice_t (Byte String)", size=12, color="#047857", anchor="start", bold=True))
    f.append(text(365, 296, "const uint8_t *ptr = &rx_buf[7]", size=11, color=INK, anchor="start"))
    f.append(text(365, 318, "size_t len = 4", size=11, color=INK, anchor="start"))
    f.append(text(365, 340, "cbor_type_t type = CBOR_BSTR", size=11, color=MUTED, anchor="start"))
    f.append(rect(365, 355, 260, 34, fill="#ffffff", stroke="#059669", rx=4))
    f.append(text(495, 376, "std::span<const uint8_t, 4>", size=10.5, color="#059669", bold=True))

    # Блок 3: Переваги Zero-Copy
    f.append(rect(660, 245, 300, 160, fill="#fefce8", stroke="#eab308", sw=1.2, rx=8))
    f.append(text(675, 272, "Властивості Zero-Copy на MCU", size=12, color="#854d0e", anchor="start", bold=True))
    f.append(text(675, 298, "• 0 викликів malloc() і free()", size=11, color=INK, anchor="start"))
    f.append(text(675, 320, "• Немає фрагментації купи", size=11, color=INK, anchor="start"))
    f.append(text(675, 342, "• O(1) додаткова пам'ять", size=11, color=INK, anchor="start"))
    f.append(text(675, 364, "• Час розбору лінійний від розміру", size=11, color=INK, anchor="start"))
    f.append(text(675, 386, "• Валідація довжини на межах буфера", size=11, color=MUTED, anchor="start"))

    # Пояснення внизу
    f.append(rect(40, 425, 920, 75, fill="#f8fafc", stroke="#e2e8f0", sw=1, rx=6))
    f.append(text(55, 450, "Інваріант безпеки:", size=11.5, color=INK, anchor="start", bold=True))
    f.append(text(55, 472, "Вказівники ptr валідні рівно стільки, скільки живе вхідний rx_buf. Якщо буфер перезаписується новим пакетом DMA,", size=10.5, color=MUTED, anchor="start"))
    f.append(text(55, 488, "програма зобов'язана або обробити зріз синхронно у перериванні/задачі, або скопіювати лише потрібне поле.", size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "zero-copy-token-stream.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Канонічний CBOR (dCBOR / Deterministic CBOR) та сортування ключів COSE
# ─────────────────────────────────────────────────────────────────────────────
def fig_dcbor_canonical_sorting():
    W, H = 1000, 560
    f = []

    f.append(rect(20, 20, 960, 520, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=10))
    f.append(text(40, 52, "Детерміноване кодування (dCBOR) для криптографії COSE (RFC 9052)", size=16, color=INK, anchor="start", bold=True))
    f.append(text(40, 76, "Канонізація усуває неоднозначність серіалізації: однаковий зміст завжди дає ідентичний байтовий геш", size=12, color=MUTED, anchor="start"))

    # Ліва колонка: Неканонічний CBOR (помилка верифікації підпису)
    f.append(rect(40, 100, 420, 420, fill="#fff1f2", stroke="#f43f5e", sw=1.2, rx=8))
    f.append(text(55, 128, "Неканонічний CBOR (Підпис ламається)", size=13, color="#9f1239", anchor="start", bold=True))

    bad_rules = [
        ("Неоптимальні цілі", "Число 10 закодовано як 0x19 00 0A (uint16) замість 0x0A (1 байт)"),
        ("Довільний порядок ключів", "Мапа: {\"b\": 1, \"a\": 2} серіалізована у порядку вставки"),
        ("Невизначена довжина", "Масив [1, 2] закодовано через 0x9F ... 0xFF (indefinite-length)"),
        ("Різна точність Float", "23.0 закодовано як 8-байтний float64 або float32"),
        ("Нестандартні NaN", "Різні бітові патерни сигнальних та тихих значень NaN"),
    ]

    for i, (rtitle, rdesc) in enumerate(bad_rules):
        yy = 150 + i * 50
        f.append(rect(55, yy, 390, 42, fill="#ffffff", stroke="#fecdd3", sw=1, rx=4))
        f.append(text(70, yy + 17, "✗  " + rtitle, size=11, color="#be123c", anchor="start", bold=True))
        f.append(text(70, yy + 33, rdesc, size=9.5, color=MUTED, anchor="start"))

    f.append(rect(55, 415, 390, 85, fill="#ffe4e6", stroke="#fb7185", rx=6))
    f.append(text(70, 438, "Наслідок для COSE / WebAuthn:", size=11, color="#881337", anchor="start", bold=True))
    f.append(text(70, 458, "Сервер отримав байтовий потік, обчислив SHA-256,", size=10, color=INK, anchor="start"))
    f.append(text(70, 474, "але через інший порядок ключів хеш не збігся з підписаним.", size=10, color=INK, anchor="start"))
    f.append(text(70, 490, "Результат: Crypto Signature Verification Failed!", size=10, color="#be123c", anchor="start", bold=True))

    # Права колонка: Вимоги dCBOR (RFC 8949 Section 4.2.1 / RFC 9052)
    f.append(rect(500, 100, 460, 420, fill="#f0fdf4", stroke="#22c55e", sw=1.2, rx=8))
    f.append(text(515, 128, "Вимоги dCBOR (Детермінований канон)", size=13, color="#14532d", anchor="start", bold=True))

    good_rules = [
        ("Найкоротше представлення", "Цілі числа упаковуються у мінімальну кількість байтів (0..23 -> 1B)"),
        ("Лексикографічне сортування", "Ключі мап сортуються: спершу за байтовою довжиною, тоді побайтово"),
        ("Заборона невизначеної довжини", "Використовуються виключно definite-length масиви та мапи"),
        ("Канонізація чисел з комою", "Єдиний формат float (або найменший без втрати); NaN = 0x7E00 (half)"),
        ("Унікальність ключів", "Дублікати ключів у словниках суворо заборонені й відхиляються"),
    ]

    for i, (rtitle, rdesc) in enumerate(good_rules):
        yy = 150 + i * 50
        f.append(rect(515, yy, 430, 42, fill="#ffffff", stroke="#bbf7d0", sw=1, rx=4))
        f.append(text(530, yy + 17, "✓  " + rtitle, size=11, color="#15803d", anchor="start", bold=True))
        f.append(text(530, yy + 33, rdesc, size=9.5, color=MUTED, anchor="start"))

    f.append(rect(515, 415, 430, 85, fill="#dcfce7", stroke="#86efac", rx=6))
    f.append(text(530, 438, "Гарантія криптографічної стійкості:", size=11, color="#14532d", anchor="start", bold=True))
    f.append(text(530, 458, "Будь-який вузол мережі на будь-якій архітектурі формує", size=10, color=INK, anchor="start"))
    f.append(text(530, 474, "100% бінарно ідентичний потік байтів для однакових даних.", size=10, color=INK, anchor="start"))
    f.append(text(530, 490, "Хеш SHA-256 і підпис Ed25519 валідні на всіх пристроях.", size=10, color="#15803d", anchor="start", bold=True))

    render(os.path.join(OUT, "dcbor-canonical-sorting.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cbor_type_byte_layout()
    fig_cbor_vs_msgpack_wire()
    fig_zero_copy_token_stream()
    fig_dcbor_canonical_sorting()
    print("All figures generated successfully.")
