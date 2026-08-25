# 📋 Специфікація бінарного формату Apache Parquet та ClickHouse MergeTree

Ця довідкова специфікація визначає бінарні структури, формати заголовків, контракти метаданих та алгоритми кодування сторінок для двох стандартів сучасного стовпцевого зберігання: відкритого файлового формату **Apache Parquet** та рушія таблиць **ClickHouse MergeTree**.

---

## 1. Загальна бінарна модель Apache Parquet

Файл формату Apache Parquet є самодостатнім двійковим контейнером, розробленим для збереження великих обсягів структурованих та напівструктурованих даних на блокових та об'єктних сховищах (HDFS, Amazon S3, Ceph, локальні файлові системи).

Файл базується на гібридному розкладі PAX (Partition Attributes Across): дані горизонтально сегментуються на великі групи рядків (**Row Groups**), а всередині кожної групи фізично відокремлюються у стовпцеві чанки (**Column Chunks**).

```
Загальна бінарна схема файлу Apache Parquet:

┌────────────────────────────────────────────────────────────────────────┐
│ 4 байти: Магічний заголовок 'P' 'A' 'R' '1' (0x50 0x41 0x52 0x31)      │
├────────────────────────────────────────────────────────────────────────┤
│ Row Group 0 (наприклад, 512 МБ або 1 000 000 рядків)                  │
│   ├── Column Chunk 0 (Стовпець «user_id»)                              │
│   │     ├── Page 0: Dictionary Page (словник значень)                  │
│   │     ├── Page 1: Data Page V1/V2 (рівні + стиснені значення)        │
│   │     └── Page 2: Data Page V1/V2 ...                                │
│   ├── Column Chunk 1 (Стовпець «amount»)                               │
│   │     ├── Page 0: Data Page V1/V2 (Plain / Delta-кодований потік)    │
│   │     └── Page 1: Data Page V1/V2 ...                                │
│   └── Column Chunk N ...                                               │
├────────────────────────────────────────────────────────────────────────┤
│ Row Group 1 ...                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ Row Group M ...                                                        │
├────────────────────────────────────────────────────────────────────────┤
│ FileMetaData (Серіалізована бінарна структура Apache Thrift)          │
│   ├── Версія формату (version: i32)                                    │
│   ├── Дерево схеми (schema: list<SchemaElement>)                       │
│   ├── Кількість рядків (num_rows: i64)                                 │
│   ├── Метадані груп (row_groups: list<RowGroup>)                       │
│   │     └── Статистика стовпців: min/max, null_count, офсети           │
│   └── Користувацькі метадані (key_value_metadata)                      │
├────────────────────────────────────────────────────────────────────────┤
│ 4 байти: Довжина FileMetaData у байтах (uint32_t Little-Endian)        │
├────────────────────────────────────────────────────────────────────────┤
│ 4 байти: Магічний кінцевик 'P' 'A' 'R' '1' (0x50 0x41 0x52 0x31)       │
└────────────────────────────────────────────────────────────────────────┘
```

Особливістю Parquet є розміщення метаданих у кінці файлу (**File Footer**). Це дозволяє записувати файл за один послідовний прохід (Single-pass Streaming Write), обчислюючи зміщення та статистики чанків під час генерації, і лише наприкінці формувати та записувати `FileMetaData`.

---

## 2. Структури метаданих Thrift

Метадані файлу, груп рядків, стовпців та сторінок закодовані за допомогою компактного протоколу **Apache Thrift** (Compact Protocol / Binary Protocol).

### 1. `FileMetaData` (Головний опис файлу)

```thrift
struct FileMetaData {
  1: required i32 version
  2: required list<SchemaElement> schema
  3: required i64 num_rows
  4: required list<RowGroup> row_groups
  5: optional list<KeyValue> key_value_metadata
  6: optional string created_by
  7: optional ColumnOrder column_orders
  8: optional EncryptionAlgorithm encryption_algorithm
  9: optional binary footer_signing_key_metadata
}
```

- `version`: версія стандарту Parquet (значення `1` для сумісності або `2` для розширених кодувань).
- `schema`: плаский список елементів схеми, які утворюють деревоподібну структуру завдяки полю `num_children`. Перший елемент списку завжди є кореневим вузлом (кореневою структурою кортежу).
- `num_rows`: точна загальна кількість логічних рядків у файлі в усіх Row Groups.
- `row_groups`: масив структур `RowGroup`, що описують фізичне розташування та розміри кожного чанка.
- `created_by`: текстовий підпис бібліотеки-генератора (наприклад, `parquet-cpp version 1.14.0`, `duckdb 1.0.0`).

### 2. `SchemaElement` (Елемент схеми даних)

```thrift
struct SchemaElement {
  1: optional Type type
  2: optional i32 type_length
  3: optional FieldRepetitionType repetition_type
  4: required string name
  5: optional i32 num_children
  6: optional ConvertedType converted_type
  7: optional Scale scale
  8: optional Precision precision
  9: optional i32 field_id
  10: optional LogicalType logicalType
}
```

- `type`: фізичний примітивний тип даних (`BOOLEAN`, `INT32`, `INT64`, `INT96` (застарілий час), `FLOAT`, `DOUBLE`, `BYTE_ARRAY`, `FIXED_LEN_BYTE_ARRAY`).
- `repetition_type`: правило повторюваності поля за моделлю Dremel:
  - `REQUIRED (0)`: поле завжди присутнє і не може бути `NULL` (рівень визначеності не потребує бітів);
  - `OPTIONAL (1)`: поле може бути відсутнім або дорівнювати `NULL`;
  - `REPEATED (2)`: поле є списком або масивом із нулем або більше значень.
- `num_children`: кількість дочірніх полів (для складених типів `STRUCT`, `MAP`, `LIST`). Якщо значення більше нуля, вузол є складеним контейнером, а наступні `num_children` елементів списку є його підполями.

### 3. `ColumnChunk` та `ColumnMetaData`

```thrift
struct ColumnMetaData {
  1: required Type type
  2: required list<Encoding> encodings
  3: required list<string> path_in_schema
  4: required CompressionCodec codec
  5: required i64 num_values
  6: required i64 total_uncompressed_size
  7: required i64 total_compressed_size
  8: optional list<KeyValue> key_value_metadata
  9: required i64 data_page_offset
  10: optional i64 index_page_offset
  11: optional i64 dictionary_page_offset
  12: optional Statistics statistics
  13: optional list<PageEncodingStats> encoding_stats
  14: optional i64 bloom_filter_offset
}
```

- `codec`: алгоритм блочної компресії (`UNCOMPRESSED = 0`, `SNAPPY = 1`, `GZIP = 2`, `LZO = 3`, `BROTLI = 4`, `LZ4 = 5`, `ZSTD = 6`, `LZ4_RAW = 7`).
- `data_page_offset`: абсолютний байтовий зсув першої сторінки даних від початку файлу.
- `dictionary_page_offset`: абсолютний зсув сторінки словника (якщо використовується словникове кодування).
- `statistics`: зонні карти стовпця (`min_value`, `max_value`, `null_count`, `distinct_count`), закодовані в двійковому представленні примітивного типу стовпця.

---

## 3. Анатомія сторінки стовпця (Page Layout)

Кожен Column Chunk складається з неперервної послідовності сторінок (**Pages**). Сторінка є неподільною одиницею кодування та блочного стиснення (розміром зазвичай від 64 КБ до 1 МБ).

```
Двійкова структура сторінки Parquet:

┌────────────────────────────────────────────────────────────────────────┐
│ 1. Заголовок PageHeader (серіалізований Thrift)                        │
│    ├── PageType: DATA_PAGE, DICTIONARY_PAGE, DATA_PAGE_V2             │
│    ├── uncompressed_page_size: uint32                                  │
│    ├── compressed_page_size: uint32                                    │
│    ├── crc: uint32 (опціональна контрольна сума)                       │
│    └── data_page_header / dictionary_page_header                       │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Потік Definition Levels (рівні визначеності для NULL-значень)       │
│    Закодований за допомогою RLE / Bit-Packed гібридного кодування      │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Потік Repetition Levels (рівні повторення для масивів)              │
│    Закодований за допомогою RLE / Bit-Packed гібридного кодування      │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Закодовані значення стовпця (Encoded Values)                        │
│    Масив числових або словникових індексів                             │
└────────────────────────────────────────────────────────────────────────┘
```

### Відмінності між `DATA_PAGE` (V1) та `DATA_PAGE_V2`
- У форматі **V1** заголовок `PageHeader` передує суцільному стисненому блоку, всередині якого лежать і рівні визначеності/повторення, і корисні дані. Щоб перевірити наявність `NULL`, рушій змушений декомпресувати всю сторінку повністю.
- У форматі **V2** рівні визначеності та повторення виносяться **перед** стисненим блоком у нестисненому вигляді. Це дозволяє обчислювати кількість `NULL` та довжини масивів без витрат на блочну декомпресію корисного навантаження.

---

## 4. Алгоритми кодування значень (Parquet Encodings)

Перелік підтримуваних алгоритмів кодування визначається переліком `Encoding`:

1. **`PLAIN (0)`:** Пряме бінарне збереження значень фіксованої довжини в порядку Little-Endian (цілі числа, плаваючі числа) або послідовність `[4 байти довжини] + [байти рядка]` для `BYTE_ARRAY`.
2. **`RLE_DICTIONARY (8)` / `PLAIN_DICTIONARY (2)`:** Словникове кодування. Сторінка словника містить масив унікальних значень, закодованих у форматі `PLAIN`. Сторінка даних містить 1 байт бітової ширини індексів `bit_width`, за яким слідує гібридний RLE/Bit-Packed потік цілочисельних індексів словника.
3. **`RLE (3)`:** Гібридне кодування RLE/Bit-Packing. Потік розбивається на групи. Якщо значення повторюються, записується заголовок серії RLE. Якщо значення неповторювані, пакується група з 8 чисел фіксованої бітової ширини.
4. **`DELTA_BINARY_PACKED (5)`:** Дельта-кодування цілих чисел (аналог FastPFOR). Блок ділиться на міні-блоки, обчислюється мінімальна дельта та мінімальна кількість бітів для міні-блоку.
5. **`DELTA_LENGTH_BYTE_ARRAY (6)`:** Збереження довжин рядків через `DELTA_BINARY_PACKED` із суцільним конкатенованим байтовим масивом символів.
6. **`DELTA_BYTE_ARRAY (7)`:** Інкрементне префіксне кодування рядків (збереження довжини спільного префікса з попереднім рядком + суфікс).
7. **`BYTE_STREAM_SPLIT (9)`:** Розщеплення плаваючих чисел (`float`, `double`): усі нульові байти мантиси виділяються в окремий суцільний потік, усі перші байти — у другий потік, і так далі. Це різко підвищує ступінь наступного блочного стиснення LZ4/ZSTD.

---

## 5. Фізичний формат рушія ClickHouse MergeTree

На відміну від єдиного багатостовпцевого контейнера Parquet, рушій **ClickHouse MergeTree** використовує роздільні файли на рівні операційної системи. Кожна колонка таблиці представлена в каталозі партіції парою файлів:
- `column.bin` — стиснені блоки даних;
- `column.mrk2` (або `.mrk` / `.mrk3`) — індексні засічки гранул.

```
Структура зв'язку між гранулами, засічками та стисненими блоками в ClickHouse:

Primary Index (primary.idx у пам'яті):
  ├── Гранула 0: "2026-08-01"
  ├── Гранула 1: "2026-08-05"
  └── Гранула 2: "2026-08-10"
          │
          ▼
Файл засічок column.mrk2 (на диску):
  ├── Засічка 0: [offset_in_bin = 0,     offset_in_decomp = 0,     rows = 8192]
  ├── Засічка 1: [offset_in_bin = 0,     offset_in_decomp = 32768, rows = 8192]
  └── Засічка 2: [offset_in_bin = 74120, offset_in_decomp = 0,     rows = 8192]
          │
          ▼
Файл стиснених даних column.bin (на диску):
  ├── Блок 0 (зсув 0):     [Header: 16B Checksum | 1B Method | 4B Comp | 4B Uncomp] + [LZ4 Payload]
  └── Блок 1 (зсув 74120): [Header: 16B Checksum | 1B Method | 4B Comp | 4B Uncomp] + [LZ4 Payload]
```

### 1. Формат стисненого блоку ClickHouse (`column.bin`)

Дані зберігаються послідовністю незалежних стиснених блоків. Розмір нестисненого блоку за замовчуванням становить від 64 КБ до 1 МБ.

:::tabs
```c
#include <stdint.h>

#pragma pack(push, 1)
struct ClickHouseCompressedBlockHeader {
    uint8_t  cityhash128_checksum[16]; /* 128-бітний хеш CityHash128 від заголовка та payload */
    uint8_t  compression_method;       /* 0x82 = LZ4, 0x90 = ZSTD, 0x02 = NONE */
    uint32_t compressed_size_with_header; /* Розмір стиснених даних + 9 байтів заголовка */
    uint32_t uncompressed_size;        /* Точний розмір розпакованих даних у байтах */
};
#pragma pack(pop)
```
```cpp
#include <cstdint>
#include <array>

#pragma pack(push, 1)
struct ClickHouseCompressedBlockHeader {
    std::array<std::uint8_t, 16> cityhash128_checksum{}; /* 128-бітний CityHash128 */
    std::uint8_t                 compression_method{0};  /* 0x82 = LZ4, 0x90 = ZSTD */
    std::uint32_t                compressed_size_with_header{0};
    std::uint32_t                uncompressed_size{0};
};
#pragma pack(pop)
```
:::

- `cityhash128_checksum`: захищає дані від пошкоджень на дисковому контролері;
- `compression_method`: визначає декомпресор ядра;
- `uncompressed_size`: дозволяє заздалегідь виділити буфер точного розміру в RAM перед викликом декомпресора `LZ4_decompress_safe()`.

### 2. Структура засічки (`column.mrk2`)

Таблиця ClickHouse логічно нарізається на **гранули** (за замовчуванням по 8192 рядки). Кожна засічка в бінарному файлі `.mrk2` описує точну фізичну адресу початку гранули:

:::tabs
```c
#include <stdint.h>

struct MergeTreeMark2 {
    uint64_t offset_in_compressed_file;   /* Байт-зсув початку CompressedBlock у файлі .bin */
    uint64_t offset_in_decompressed_block;/* Байт-зсув першого байта гранули в розпакованому буфері */
    uint64_t rows_in_granule;             /* Кількість рядків у гранулі (для адаптивної грануляції) */
};
```
```cpp
#include <cstdint>

struct MergeTreeMark2 {
    std::uint64_t offset_in_compressed_file{0};   /* Зсув CompressedBlock у файлі .bin */
    std::uint64_t offset_in_decompressed_block{0};/* Зсув гранули в розпакованому буфері */
    std::uint64_t rows_in_granule{0};             /* Кількість рядків у гранулі */
};
```
:::

Під час виконання запиту з фільтром за первинним ключем ClickHouse здійснює двійковий пошук за `primary.idx`, знаходить номери гранул, які необхідно прочитати, зчитує лише відповідні засічки з `.mrk2` і завантажує з диска виключно ті блоки `.bin`, які містять зазначені гранули, повністю ігноруючи решту гігабайтів файлу.
