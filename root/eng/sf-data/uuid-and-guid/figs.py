# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. uuid-bit-layout: 128 бітів і 16 байтів канонічного UUID ───────────────
def fig_uuid_bit_layout():
    W, H = 840, 360
    p = []
    cx = W / 2
    p.append(text(cx, 32, "128-бітний UUID (RFC 4122 / RFC 9562): 16 байтів у записі 8-4-4-4-12", size=15, bold=True))

    # Канонічний рядок з дефісами
    p.append(fitbox(40, 52, 760, 48,
                    "f81d4fae - 7dec - 11d0 - a765 - 00a0c91e6bf6\n"
                    "8 hex-знаків    4 hex     4 hex     4 hex         12 hex-знаків",
                    size=12, fill="#f8fafc", stroke=LINE, sw=1.5, color=INK))

    # Поля структури у 16 байтах
    fields = [
        ("time_low", "4 байти (32 біти)\nбайти 0..3", "#eef4ff", NEG, 170),
        ("time_mid", "2 байти (16 бітів)\nбайти 4..5", "#f0fdf4", FIELD, 120),
        ("time_hi_and_ver", "2 байти (16 бітів)\n4-біт версія + 12 бітів", "#fef3c7", "#d97706", 160),
        ("clk_seq", "2 байти (16 бітів)\n2-3 біти варіант + посл.", "#fdeeea", POS, 150),
        ("node / entropy", "6 байтів (48 бітів)\nMAC-адреса або 48 випадкових бітів", "#f3e8ff", "#9333ea", 160),
    ]

    x = 40
    y = 120
    h_box = 75
    for name, desc, bg_col, border_col, bw in fields:
        p.append(fitbox(x, y, bw, h_box, f"{name}\n\n{desc}", size=11, fill=bg_col, stroke=border_col, sw=1.6, color=INK))
        x += bw

    # Пояснення версії та варіанта
    p.append(fitbox(40, 215, 370, 95,
                    "Поле версії (Version): старші 4 біти байта 6\n"
                    "• 0001 (1) = time + MAC   • 0100 (4) = CSPRNG\n"
                    "• 0101 (5) = SHA-1 назва  • 0111 (7) = Unix ms + rand",
                    size=11, fill="#fffbeb", stroke="#d97706", sw=1.5, color=INK))

    p.append(fitbox(430, 215, 370, 95,
                    "Поле варіанта (Variant): старші 2-3 біти байта 8\n"
                    "• 10x (RFC 4122 / RFC 9562 / Leach-Salz)\n"
                    "• 0xx (Apollo NCS)  • 110 (Microsoft COM GUID)\n"
                    "• 111 (Зарезервовано для майбутніх стандартів)",
                    size=11, fill="#fef2f2", stroke=POS, sw=1.5, color=INK))

    p.append(text(cx, 335, "128 бітів = 16 байтів = 32 шістнадцяткові цифри + 4 дефіси",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "uuid-bit-layout.svg"), W, H, *p,
           title="Анатомія 128-бітного UUID: поля, версія і варіант")


# ── 2. v1-vs-v4-vs-v7: порівняння розподілу 128 бітів між версіями ──────────
def fig_v1_vs_v4_vs_v7():
    W, H = 820, 390
    p = []
    cx = W / 2
    p.append(text(cx, 30, "Розподіл 128 бітів у версіях UUIDv1, UUIDv4 та UUIDv7", size=15, bold=True))

    rows = [
        ("UUIDv1\n(Час + MAC)", [
            (240, "60-бітний час (100 нс від 1582 року)", "#eef4ff", NEG),
            (30, "v1", "#fef3c7", "#d97706"),
            (110, "14-біт clk_seq", "#fdeeea", POS),
            (260, "48-бітний MAC-адрес (IEEE 802)", "#f3e8ff", "#9333ea"),
        ]),
        ("UUIDv4\n(Випадковий)", [
            (320, "48 бітів криптографічної ентропії (CSPRNG)", "#f0fdf4", FIELD),
            (30, "v4", "#fef3c7", "#d97706"),
            (12, "var", "#fdeeea", POS),
            (278, "74 біти випадкової ентропії (разом: 122 біти)", "#f0fdf4", FIELD),
        ]),
        ("UUIDv7\n(Unix ms + Rand)", [
            (240, "48-бітний Unix Epoch Timestamp (мілісекунди)", "#eef4ff", NEG),
            (30, "v7", "#fef3c7", "#d97706"),
            (70, "12 біт sub-ms", "#ecfdf5", FIELD),
            (12, "var", "#fdeeea", POS),
            (288, "62 біти випадкової ентропії (k-сортувальний)", "#f3e8ff", "#9333ea"),
        ]),
    ]

    y = 60
    for title, segments in rows:
        p.append(fitbox(30, y, 110, 56, title, size=11, fill="#f8fafc", stroke=LINE, sw=1.4, bold=True))
        bx = 150
        for w_seg, lbl, bg, stroke_c in segments:
            p.append(fitbox(bx, y, w_seg, 56, lbl, size=10, fill=bg, stroke=stroke_c, sw=1.4, color=INK))
            bx += w_seg
        y += 75

    # Порівняльна плашка
    p.append(fitbox(30, 290, 760, 75,
                    "• UUIDv1: прив'язаний до заліза (MAC), видає фізичну адресу вузла й точний час;\n"
                    "• UUIDv4: 122 випадкові біти, не розкриває залізо, але хаотичний для B-дерев;\n"
                    "• UUIDv7: 48 бітів Unix ms + 74 біти ентропії — монотонний у часі та дружній до БД.",
                    size=11, fill="#fafafa", stroke=MUTED, sw=1.3, color=INK))

    render(os.path.join(OUT, "v1-vs-v4-vs-v7.svg"), W, H, *p,
           title="Порівняння бітового складу UUIDv1, UUIDv4 та UUIDv7")


# ── 3. guid-endianness-mismatch: конфлікт порядку байтів RFC vs GUID ──────────
def fig_guid_endianness_mismatch():
    W, H = 840, 360
    p = []
    cx = W / 2
    p.append(text(cx, 30, "Конфлікт порядку байтів: мережевий RFC 4122 vs Microsoft GUID", size=15, bold=True))

    p.append(fitbox(40, 52, 760, 46,
                    "Канонічний текстовий рядок:  00112233-4455-6677-8899-aabbccddeeff\n"
                    "Усі 16 байтів за стандартом IETF/RFC записуються в Big-Endian (Network Byte Order)",
                    size=12, fill="#f8fafc", stroke=LINE, sw=1.4, color=INK))

    # Ліва колонка: RFC 4122
    p.append(fitbox(40, 115, 365, 175,
                    "RFC 4122 / RFC 9562 (Big-Endian)\n\n"
                    "Байтовий масив у пам'яті (16 байтів):\n"
                    "[00 11 22 33] [44 55] [66 77] [88 99 aa bb cc dd ee ff]\n\n"
                    "• Усі поля зберігаються старшим байтом уперед.\n"
                    "• Порядок байтів у пам'яті повністю збігається\n"
                    "  із порядком символів у hex-рядку.",
                    size=11, fill="#eef4ff", stroke=NEG, sw=1.8, color=INK))

    # Права колонка: Microsoft GUID
    p.append(fitbox(435, 115, 365, 175,
                    "Microsoft GUID struct (Little-Endian на x86/ARM)\n\n"
                    "struct { u32 Data1; u16 Data2; u16 Data3; u8 Data4[8]; }\n"
                    "[33 22 11 00] [55 44] [77 66] [88 99 aa bb cc dd ee ff]\n\n"
                    "• Data1, Data2, Data3 перевертаються в пам'яті!\n"
                    "• Прямий memcpy() дає фальшивий інший UUID:\n"
                    "  33221100-5544-7766-8899-aabbccddeeff",
                    size=11, fill="#fdeeea", stroke=POS, sw=1.8, color=INK))

    p.append(text(cx, 325, "Збереження struct GUID через memcpy() у мережу чи SQLite BLOB спотворює перші 8 байтів",
                  size=12, color=POS, bold=True))

    render(os.path.join(OUT, "guid-endianness-mismatch.svg"), W, H, *p,
           title="Порядок байтів у пам'яті: RFC 4122 Big-Endian vs Windows GUID struct Little-Endian")


# ── 4. btree-fragmentation: випадковий v4 проти монотонного v7 у B-Tree ──────
def fig_btree_fragmentation():
    W, H = 840, 360
    p = []
    cx = W / 2
    p.append(text(cx, 30, "Вплив ідентифікатора на B-дерево індексу: UUIDv4 проти UUIDv7", size=15, bold=True))

    # ЛІВО: UUIDv4
    p.append(fitbox(40, 55, 365, 235,
                    "UUIDv4 (Випадковий ключ)\n\n"
                    "1. Ключі потрапляють у випадкові листки дерева.\n"
                    "2. Заповнений листок розщеплюється навпіл (Page Split).\n"
                    "3. Коефіцієнт заповнення сторінок падає до ~50%.\n"
                    "4. Кеш Buffer Pool вимивається хаотичними сторінками.\n"
                    "5. Високий Write Amplification (запис 8-16 КБ на ключ).\n"
                    "6. Продуктивність вставки падає в рази при зростанні БД.",
                    size=11, fill="#fdeeea", stroke=POS, sw=1.8, color=INK))

    # ПРАВО: UUIDv7
    p.append(fitbox(435, 55, 365, 235,
                    "UUIDv7 (Часово впорядкований ключ)\n\n"
                    "1. Нові ключі монотонно додаються в крайній правий листок.\n"
                    "2. Сторінки заповнюються послідовно без розщеплень.\n"
                    "3. Коефіцієнт заповнення індексу досягає 90-98%.\n"
                    "4. Гаряча сторінка лишається в L1/L2/RAM кеші.\n"
                    "5. Мінімальний Write Amplification та послідовний I/O.\n"
                    "6. Швидкість вставки стабільна навіть на мільярдах рядків.",
                    size=11, fill="#f0fdf4", stroke=FIELD, sw=1.8, color=INK))

    p.append(text(cx, 325, "UUIDv7 зберігає унікальність без реєстру і водночас захищає індекси баз даних від фрагментації",
                  size=12, color=INK, italic=True))

    render(os.path.join(OUT, "btree-fragmentation.svg"), W, H, *p,
           title="B-Tree індекси: деградація через випадковий UUIDv4 проти монотонного UUIDv7")


if __name__ == "__main__":
    fig_uuid_bit_layout()
    fig_v1_vs_v4_vs_v7()
    fig_guid_endianness_mismatch()
    fig_btree_fragmentation()
    print("OK: all figures generated in", OUT)
