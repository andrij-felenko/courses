# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми 'Самоописовий формат: схема всередині файлу'."""

import sys, os

# Додаємо шлях до scripts/ у корені репозиторію (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_metadata_architectures():
    """Порівняння трьох підходів до опису структури даних."""
    w, h = 980, 480
    frags = []

    frags.append(text(w / 2, 28, "Три підходи до опису двійкових даних", size=18, bold=True))

    col_w = 285
    col_gap = 35
    x_start = 30
    y_top = 60
    col_h = 390

    # 1. Безсхемні / теговані
    x1 = x_start
    frags.append(rect(x1, y_top, col_w, col_h, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(x1, y_top, col_w, 40, fill="#eaf2f8", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x1 + col_w / 2, y_top + 25, "1. Безсхемні / Теговані", size=15, bold=True, color="#1b4f72"))
    frags.append(text(x1 + col_w / 2, y_top + 60, "JSON, BSON, CBOR, MessagePack", size=12, color=MUTED, italic=True))

    box1 = fitbox(x1 + 15, y_top + 80, col_w - 30, 95,
                  'Кожен запис повторює ключі й теги типів:\n'
                  '{"id": 1, "temp": 21.5}\n'
                  '{"id": 2, "temp": 22.1}\n'
                  '{"id": 3, "temp": 20.8}',
                  size=11, fill="#f4f6f7", stroke="#bdc3c7")
    frags.append(box1)

    p1 = fitbox(x1 + 15, y_top + 190, col_w - 30, 80,
                '+ Повна гнучкість запису\n'
                '+ Довільна динамічна структура\n'
                '+ Не потрібна попередня схема',
                size=12, fill="#e8f8f5", stroke=FIELD)
    frags.append(p1)

    m1 = fitbox(x1 + 15, y_top + 285, col_w - 30, 90,
                '− 50–80% розміру — повтори імен\n'
                '− Повільний розбір типів рядків\n'
                '− Немає суворого контракту',
                size=12, fill="#fdedec", stroke=POS)
    frags.append(m1)

    # 2. Зовнішня схема
    x2 = x1 + col_w + col_gap
    frags.append(rect(x2, y_top, col_w, col_h, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(x2, y_top, col_w, 40, fill="#fef9e7", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x2 + col_w / 2, y_top + 25, "2. Зовнішня схема", size=15, bold=True, color="#7d6608"))
    frags.append(text(x2 + col_w / 2, y_top + 60, "Protocol Buffers, FlatBuffers", size=12, color=MUTED, italic=True))

    box2 = fitbox(x2 + 15, y_top + 80, col_w - 30, 95,
                  'Схема окремо у файлі schema.proto;\n'
                  'у двійковому файлі лише номери полів:\n'
                  '[0x08, 0x01, 0x15, 0x00, ...]\n'
                  'Без .proto байти непрочитні',
                  size=11, fill="#fcf3cf", stroke="#f1c40f")
    frags.append(box2)

    p2 = fitbox(x2 + 15, y_top + 190, col_w - 30, 80,
                '+ Мінімальний оверхед у мережі\n'
                '+ Швидка серіалізація\n'
                '+ Сувора статична типізація',
                size=12, fill="#e8f8f5", stroke=FIELD)
    frags.append(p2)

    m2 = fitbox(x2 + 15, y_top + 285, col_w - 30, 90,
                '− Файл мертвий без точної версії .proto\n'
                '− Крихке довгострокове архівування\n'
                '− Важко читати стороннім інструментам',
                size=12, fill="#fdedec", stroke=POS)
    frags.append(m2)

    # 3. Самоописові формати
    x3 = x2 + col_w + col_gap
    frags.append(rect(x3, y_top, col_w, col_h, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(rect(x3, y_top, col_w, 40, fill="#eafaf1", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x3 + col_w / 2, y_top + 25, "3. Самоописові (вбудована)", size=15, bold=True, color="#1e8449"))
    frags.append(text(x3 + col_w / 2, y_top + 60, "Apache Avro, Apache Parquet, HDF5", size=12, color=MUTED, italic=True))

    box3 = fitbox(x3 + 15, y_top + 80, col_w - 30, 95,
                  'Схема записана 1 раз у файлі;\n'
                  'дані лежать компактно без імен полів:\n'
                  '[Header/Footer: Schema JSON/Thrift]\n'
                  '[Data: щільні двійкові масиви/колонки]',
                  size=11, fill="#d5f5e3", stroke="#58d68d")
    frags.append(box3)

    p3 = fitbox(x3 + 15, y_top + 190, col_w - 30, 80,
                '+ Файл повністю автономний\n'
                '+ Дані компактні (без оверхеду ключів)\n'
                '+ Автоматична еволюція схеми',
                size=12, fill="#e8f8f5", stroke=FIELD)
    frags.append(p3)

    m3 = fitbox(x3 + 15, y_top + 285, col_w - 30, 90,
                '− Невеликий фіксований оверхед схеми\n'
                '− Складніший формат контейнера\n'
                '− Потрібен рушій зіставлення схем',
                size=12, fill="#fdedec", stroke=POS)
    frags.append(m3)

    render(os.path.join(OUT_DIR, "metadata-architectures.svg"), w, h, *frags)


def fig_avro_ocf_layout():
    """Анатомія контейнерного файлу Apache Avro (Object Container File)."""
    w, h = 940, 430
    frags = []

    frags.append(text(w / 2, 28, "Структура контейнера Apache Avro (Object Container File)", size=18, bold=True))

    y_hdr = 65
    frags.append(text(60, y_hdr - 10, "Заголовок файлу (Header):", size=13, bold=True, anchor="start"))

    b1 = fitbox(30, y_hdr, 110, 60, "Magic Bytes\n4 байти:\n'Obj' + 0x01", size=12, fill="#d4e6f1", stroke="#2980b9", bold=True)
    b2 = fitbox(150, y_hdr, 520, 60,
                "Карта метаданих (Metadata Map: avro.schema + avro.codec)\n"
                "JSON-схема типу: {\"type\":\"record\",\"name\":\"User\",\"fields\":[...]}",
                size=11, fill="#d5f5e3", stroke="#27ae60")
    b3 = fitbox(680, y_hdr, 230, 60, "Синхромаркер (Sync Marker)\n16 випадкових байтів\n(унікальний для файлу)", size=11, fill="#fdebd0", stroke="#d35400", bold=True)
    frags.extend([b1, b2, b3])

    frags.append(line(795, y_hdr + 60, 795, y_hdr + 105, color="#d35400", sw=1.5, dash="4,4"))

    y_blk = 195
    frags.append(text(60, y_blk - 15, "Блоки даних (Data Blocks):", size=13, bold=True, anchor="start"))

    blk1_w = 420
    frags.append(rect(30, y_blk, blk1_w, 140, fill="#f8f9fa", stroke="#7f8c8d", sw=1.5, rx=6))
    frags.append(text(30 + blk1_w / 2, y_blk + 20, "Блок даних #1", size=13, bold=True))

    f1 = fitbox(45, y_blk + 35, 100, 45, "Кількість рядків\n(varint)", size=11, fill="#eaeded")
    f2 = fitbox(155, y_blk + 35, 110, 45, "Розмір байтів\n(varint)", size=11, fill="#eaeded")
    f3 = fitbox(275, y_blk + 35, 160, 45, "16-байтний маркер\n(той самий Sync)", size=11, fill="#fdebd0", stroke="#d35400")
    f4 = fitbox(45, y_blk + 85, 390, 40, "Стиснені двійкові записи (Snappy / Deflate / Zstd)\nПослідовність чистих двійкових значень згідно зі схемою", size=10, fill="#e8f8f5", stroke="#2ecc71")
    frags.extend([f1, f2, f3, f4])

    blk2_w = 420
    frags.append(rect(490, y_blk, blk2_w, 140, fill="#f8f9fa", stroke="#7f8c8d", sw=1.5, rx=6))
    frags.append(text(490 + blk2_w / 2, y_blk + 20, "Блок даних #2 ... N", size=13, bold=True))

    g1 = fitbox(505, y_blk + 35, 100, 45, "Кількість рядків\n(varint)", size=11, fill="#eaeded")
    g2 = fitbox(615, y_blk + 35, 110, 45, "Розмір байтів\n(varint)", size=11, fill="#eaeded")
    g3 = fitbox(735, y_blk + 35, 160, 45, "16-байтний маркер\n(той самий Sync)", size=11, fill="#fdebd0", stroke="#d35400")
    g4 = fitbox(505, y_blk + 85, 390, 40, "Стиснені двійкові записи наступної пачки\nДозапис у хвіст без перезапису заголовка", size=10, fill="#e8f8f5", stroke="#2ecc71")
    frags.extend([g1, g2, g3, g4])

    expl = fitbox(30, 355, 880, 55,
                  "Потоковий запис: схема пишеться на початку один раз; блоки дописуються в кінець без оновлення зміщень.\n"
                  "Синхромаркер дозволяє паралельним процесам MapReduce знаходити межі блоків у довільному місці файлу.",
                  size=11, fill="#f4f6f7", stroke="#bdc3c7")
    frags.append(expl)

    render(os.path.join(OUT_DIR, "avro-ocf-layout.svg"), w, h, *frags)


def fig_parquet_footer_layout():
    """Анатомія колонкового файлу Apache Parquet з футером та оптимізаціями."""
    w, h = 980, 520
    frags = []

    frags.append(text(w / 2, 28, "Колонкове збереження Parquet: метадані у футері та оптимізації", size=18, bold=True))

    x_sec = 40
    w_sec = 440

    frags.append(fitbox(x_sec, 60, w_sec, 30, "Початок файлу: 4 байти Magic 'PAR1'", size=12, fill="#d4e6f1", stroke="#2980b9", bold=True))

    # Row Group 1
    frags.append(rect(x_sec, 100, w_sec, 135, fill="#fdfefe", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(x_sec + w_sec / 2, 118, "Row Group #1 (наприклад, 1 000 000 рядків)", size=12, bold=True))
    c1 = fitbox(x_sec + 10, 130, 130, 95, "ColumnChunk 1\n(user_id)\nDict Page\nData Pages", size=10, fill="#e8f8f5", stroke="#27ae60")
    c2 = fitbox(x_sec + 150, 130, 130, 95, "ColumnChunk 2\n(timestamp)\nData Pages\nSnappy/Zstd", size=10, fill="#e8f8f5", stroke="#27ae60")
    c3 = fitbox(x_sec + 290, 130, 140, 95, "ColumnChunk 3\n(payload_json)\nData Pages\nSnappy/Zstd", size=10, fill="#fdedec", stroke="#e74c3c")
    frags.extend([c1, c2, c3])

    # Пропуск рядків (Row Group 2...N)
    frags.append(rect(x_sec, 245, w_sec, 30, fill="#f8f9fa", stroke="#bdc3c7", sw=1))
    frags.append(text(x_sec + w_sec / 2, 264, "Row Group #2 ... #N", size=11, color=MUTED))

    # Футер файлу
    frags.append(rect(x_sec, 285, w_sec, 160, fill="#fef9e7", stroke="#d4ac0d", sw=2, rx=6))
    frags.append(text(x_sec + w_sec / 2, 305, "ФУТЕР ФАЙЛУ: FileMetaData (Thrift)", size=13, bold=True, color="#7d6608"))

    f_sch = fitbox(x_sec + 10, 318, 420, 38, "Дерево схеми: SchemaElement (типи, вкладення, repetition)", size=10, fill="#ffffff", stroke="#f1c40f")
    f_rg = fitbox(x_sec + 10, 360, 420, 45,
                  "Метадані груп: зміщення чанків, розміри, кодеки, словники;\n"
                  "Статистика чанків: min / max значення, null_count",
                  size=10, fill="#ffffff", stroke="#f1c40f", bold=True)
    f_len = fitbox(x_sec + 10, 410, 205, 28, "Footer Length (4 байти uint32)", size=10, fill="#d5f5e3", stroke="#27ae60")
    f_end = fitbox(x_sec + 225, 410, 205, 28, "Magic 'PAR1' (4 байти)", size=10, fill="#d4e6f1", stroke="#2980b9", bold=True)
    frags.extend([f_sch, f_rg, f_len, f_end])

    # Права панель
    x_rt = 530
    w_rt = 410

    frags.append(rect(x_rt, 60, w_rt, 385, fill="#f4f6f7", stroke="#7f8c8d", sw=1.5, rx=8))
    frags.append(text(x_rt + w_rt / 2, 85, "Оптимізації завдяки футеру метаданих", size=14, bold=True))

    q1 = fitbox(x_rt + 15, 105, w_rt - 30, 45,
                "Крок 1. Зчитування кінця файлу\n"
                "Читаємо останні 4–512 КБ: беремо довжину футера й розбираємо FileMetaData.",
                size=11, fill="#ffffff", stroke="#3498db")
    frags.append(q1)

    q2 = fitbox(x_rt + 15, 160, w_rt - 30, 80,
                "Проекція колонок (Column Projection):\n"
                "Запит: SELECT user_id FROM t\n"
                "Читаються байти ТІЛЬКИ ColumnChunk 1.\n"
                "ColumnChunk 3 (великий JSON) не торкається на диску!",
                size=11, fill="#eafaf1", stroke="#2ecc71")
    frags.append(q2)

    q3 = fitbox(x_rt + 15, 250, w_rt - 30, 85,
                "Проштовхування предикатів (Predicate Pushdown):\n"
                "Запит: WHERE timestamp >= 2026-08-01\n"
                "Якщо в статистиці чанка max < 2026-08-01, уся\n"
                "група рядків (мільйон рядків) пропускається без дискового I/O!",
                size=11, fill="#fef5e7", stroke="#e67e22")
    frags.append(q3)

    q4 = fitbox(x_rt + 15, 345, w_rt - 30, 85,
                "Чому футер, а не заголовок?\n"
                "Під час запису точні зміщення, розміри після стиснення та min/max статистика стають відомі лише ПІСЛЯ завершення запису всіх рядків.",
                size=10, fill="#ffffff", stroke="#95a5a6", italic=True)
    frags.append(q4)

    frags.append(arrow(x_sec + w_sec, 360, x_rt, 125, color="#2980b9", sw=2))

    render(os.path.join(OUT_DIR, "parquet-footer-layout.svg"), w, h, *frags)


def fig_schema_resolution_flow():
    """Процес зіставлення схем (Schema Resolution: Reader vs Writer Schema)."""
    w, h = 960, 460
    frags = []

    frags.append(text(w / 2, 28, "Еволюція даних: узгодження схеми записувача і зчитувача", size=18, bold=True))

    w_box = fitbox(30, 65, 270, 160,
                   "Схема записувача (Writer Schema)\n"
                   "[вбудована всередині старого файлу]\n"
                   "{\n"
                   "  \"id\": int,\n"
                   "  \"username\": string,\n"
                   "  \"legacy_status\": int\n"
                   "}",
                   size=11, fill="#d4e6f1", stroke="#2980b9")
    frags.append(w_box)

    r_box = fitbox(660, 65, 270, 160,
                   "Схема зчитувача (Reader Schema)\n"
                   "[скомпільована в поточному коді]\n"
                   "{\n"
                   "  \"id\": long,           // тип розширено\n"
                   "  \"username\": string,\n"
                   "  \"email\": string = \"\" // нове поле з дефолтом\n"
                   "}",
                   size=11, fill="#d5f5e3", stroke="#27ae60")
    frags.append(r_box)

    eng_w = 280
    eng_x = 340
    frags.append(rect(eng_x, 65, eng_w, 240, fill="#fdfefe", stroke=LINE, sw=2, rx=8))
    frags.append(text(eng_x + eng_w / 2, 90, "Рушій зіставлення (Resolver)", size=14, bold=True))

    r1 = fitbox(eng_x + 10, 105, eng_w - 20, 36, "1. Збіг полів за іменами / аліасами", size=10, fill="#f4f6f7")
    r2 = fitbox(eng_x + 10, 145, eng_w - 20, 36, "2. Просування типів (int → long)", size=10, fill="#f4f6f7")
    r3 = fitbox(eng_x + 10, 185, eng_w - 20, 50, "3. Нове поле в Reader:\nпідставляється default (\"\")", size=10, fill="#e8f8f5", stroke=FIELD)
    r4 = fitbox(eng_x + 10, 240, eng_w - 20, 50, "4. Видалене поле з Writer:\nlegacy_status пропускається парсером", size=10, fill="#fdedec", stroke=POS)
    frags.extend([r1, r2, r3, r4])

    frags.append(arrow(300, 145, eng_x, 145, color="#2980b9", sw=2))
    frags.append(arrow(660, 145, eng_x + eng_w, 145, color="#27ae60", sw=2))

    out_box = fitbox(230, 335, 500, 95,
                     "Результуючий об'єкт у пам'яті застосунку:\n"
                     "User { id: 42L, username: \"alice\", email: \"\" }\n"
                     "✓ Старий файл успішно прочитано новим кодом без міграції бази даних!\n"
                     "Якщо поле відсутнє і не має default → SchemaResolutionException.",
                     size=11, fill="#fef9e7", stroke="#f39c12", bold=False)
    frags.append(out_box)

    frags.append(arrow(eng_x + eng_w / 2, 305, eng_x + eng_w / 2, 335, color=LINE, sw=2))

    render(os.path.join(OUT_DIR, "schema-resolution-flow.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_metadata_architectures()
    fig_avro_ocf_layout()
    fig_parquet_footer_layout()
    fig_schema_resolution_flow()
    print("Всі фігури згенеровано успішно.")
