# ⚙️ Розбір контейнера Apache Avro та узгодження схем

Контейнерний формат Apache Avro (*Object Container File*, OCF) — це еталонний приклад самоописового двійкового сховища послідовних записів. Він поєднує два інженерні компроміси: компактність чистого двійкового кодування без надлишкових текстових ключів у кожному рядку та абсолютну автономність файлу завдяки вбудованій схемі.

Головна відмінність Avro від неконтейнерних форматів полягає у тому, що файл не потребує зовнішнього файлу опису структури для прочитання. Заголовок файлу містить повну канонічну схему у форматі JSON, а тіло файлу розбите на незалежні блоки даних, розділені 16-байтними випадковими синхромаркерами. Завдяки синхромаркерам розподілені обчислювальні рушії (наприклад, Hadoop MapReduce або Apache Spark) можуть розщеплювати 100-гігабайтний файл на паралельні фрагменти: воркер переходить на довільне зміщення у файлі, сканує потік вперед у пошуках 16-байтної послідовності маркера і починає паралельне читання блоку без потреби аналізувати попередні гігабайти.

### Двійкова анатомія контейнера Avro

Файл складається з двох чітко розмежованих зон — одноразового заголовка метаданих і послідовності блоків даних.

```
+-----------------------------------------------------------------------+
| Magic Bytes: 'O', 'b', 'j', 0x01 (4 байти)                            |
+-----------------------------------------------------------------------+
| Metadata Map: count (varint), [key (string), value (bytes)]..., 0x00 |
|   - ключ "avro.schema" -> JSON-текст повної схеми                     |
|   - ключ "avro.codec"  -> "null", "snappy", "deflate", "zstandard"   |
+-----------------------------------------------------------------------+
| Sync Marker: 16 випадкових байтів (генеруються при створенні файлу)   |
+=======================================================================+
| Блок даних #1:                                                        |
|   - record_count (zigzag varint)                                      |
|   - block_byte_size (zigzag varint)                                   |
|   - raw_data_bytes [розміром block_byte_size]                         |
|   - 16 байтів Sync Marker (має збігатися з маркером заголовка)        |
+-----------------------------------------------------------------------+
| Блок даних #2 ... N                                                   |
+-----------------------------------------------------------------------+
```

### Кодування цілих чисел: Zigzag Varint

Усі лічильники, довжини рядків та цілочисельні поля записуються у форматі зі змінною довжиною (*Variable-length quantity*, Varint) з попереднім перетворенням Zigzag.

Звичайний прямий запис 64-бітного числа `int64` завжди забирає 8 байтів, навіть якщо число дорівнює `1`. Звичайний Varint записує число 7-бітними пачками, де старший біт (MSB, `0x80`) сигналізує про наявність наступного байта. Проте для від'ємних чисел (наприклад, `-1`, яке в комп'ютері записується як `0xFFFFFFFFFFFFFFFF`) стандартний Varint змушений виставляти всі біти й породжувати максимальні 10 байтів у вихідному потоці.

Кодування Zigzag розв'язує цю проблему, чергуючи додатні та від'ємні числа так, щоб малі за модулем значення перетворювалися на малі беззнакові цілі:
- Число `0` кодується як `0`.
- Число `-1` стає `1`.
- Число `1` стає `2`.
- Число `-2` стає `3`.

Математичне перетворення для 64-бітного цілого `n` виконується за один такт:
```
zigzag(n) = (n << 1) ^ (n >> 63)
```

Зворотне відновлення знакового числа з беззнакового значення `v`:
```
decode_zigzag(v) = (v >> 1) ^ -(v & 1)
```

### Простеження байтового потоку

Розглянемо, як конкретний фрагмент двійкових даних розгортається у пам'яті парсера:
- Байти `4F 62 6A 01` — це сигнатура ASCII `Obj` плюс байт версії `0x01`. Якщо перший байт не `0x4F`, парсер негайно відхиляє файл як несумісний.
- Байт `02` — лічильник Zigzag Varint, що декодується як число `1` (одна пара ключ-значення в поточному блоці метаданих).
- Далі слідує ключ: байт довжини `16` (значення `11` у Zigzag) та 11 ASCII-символів `"avro.schema"`.
- Значення містить довжину JSON-рядка у байтах та сам канонічний текст схеми.
- Завершує заголовок нульовий байт `0x00` (кінець карти метаданих) і 16 сирих псевдовипадкових байтів синхромаркера.

### Механізм динамічного узгодження схем

Коли програма читає дані, вона зіставляє схему записувача (*Writer Schema*, видобуту з заголовка файлу) із власною схемою зчитувача (*Reader Schema*, скомпільованою у коді).

Алгоритм узгодження діє за такими правилами:
1. **Збіг полів за іменами та аліасами.** Порядок полів у файлі та в пам'яті застосунку може відрізнятися. Зчитувач перебирає поля власної схеми й шукає відповідні поля у схемі записувача.
2. **Пропуск непотрібних полів.** Якщо схема записувача містить поле `legacy_tag`, якого немає у схемі зчитувача, парсер не створює помилки: він використовує тип поля зі схеми файлу, щоб визначити кількість байтів і пропустити (*skip*) їх без виділення динамічної пам'яті.
3. **Підстановка значень за замовчуванням.** Якщо зчитувач очікує поле `email`, якого не було в старій версії файлу, парсер підставляє значення `default`, визначене в схемі зчитувача. Якщо поле обов'язкове і не має `default`, виникає помилка несумісності схем.
4. **Просування числових типів.** Дозволяється автоматичне безпечне розширення типів: `int` (32 біти) автоматично підвищується до `long` (64 біти), `float` до `double`.

Нижче наведено робочу реалізацію низькорівневого парсера контейнера Avro мовами C та C++, яка розбирає заголовок, витягує схему, читає блоки та ілюструє повний цикл узгодження полів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define AVRO_SYNC_SIZE 16
#define AVRO_MAGIC_SIZE 4
static const uint8_t EXPECTED_MAGIC[AVRO_MAGIC_SIZE] = {'O', 'b', 'j', 0x01};

/* Зчитувач із буфера в пам'яті з контролем меж */
typedef struct {
    const uint8_t *data;
    size_t size;
    size_t offset;
} ByteReader;

static inline bool reader_has_bytes(const ByteReader *r, size_t n) {
    return r->offset + n <= r->size;
}

/* Декодування Zigzag Varint (64-бітне ціле зі знаком) */
static bool read_varint_long(ByteReader *r, int64_t *out_val) {
    uint64_t raw = 0;
    int shift = 0;

    while (reader_has_bytes(r, 1)) {
        uint8_t b = r->data[r->offset++];
        raw |= ((uint64_t)(b & 0x7F)) << shift;
        if ((b & 0x80) == 0) {
            /* Відновлення знаку з Zigzag-подання */
            *out_val = (int64_t)((raw >> 1) ^ (-(int64_t)(raw & 1)));
            return true;
        }
        shift += 7;
        if (shift >= 64) return false; /* Захист від некоректного varint */
    }
    return false;
}

/* Зчитування рядка (довжина у вигляді varint + байти) */
static bool read_avro_string(ByteReader *r, char **out_str, size_t *out_len) {
    int64_t len = 0;
    if (!read_varint_long(r, &len) || len < 0) return false;
    if (!reader_has_bytes(r, (size_t)len)) return false;

    char *buf = (char *)malloc((size_t)len + 1);
    if (!buf) return false;

    memcpy(buf, r->data + r->offset, (size_t)len);
    buf[len] = '\0';
    r->offset += (size_t)len;

    *out_str = buf;
    if (out_len) *out_len = (size_t)len;
    return true;
}

/* Зчитування двійкових байтів (довжина у вигляді varint + байти) */
static bool read_avro_bytes(ByteReader *r, uint8_t **out_bytes, size_t *out_len) {
    int64_t len = 0;
    if (!read_varint_long(r, &len) || len < 0) return false;
    if (!reader_has_bytes(r, (size_t)len)) return false;

    uint8_t *buf = (uint8_t *)malloc((size_t)len);
    if (!buf) return false;

    memcpy(buf, r->data + r->offset, (size_t)len);
    r->offset += (size_t)len;

    *out_bytes = buf;
    *out_len = (size_t)len;
    return true;
}

/* Метадані заголовка Avro OCF */
typedef struct {
    char *schema_json;
    char *codec;
    uint8_t sync_marker[AVRO_SYNC_SIZE];
} AvroHeader;

static void free_avro_header(AvroHeader *hdr) {
    if (hdr->schema_json) free(hdr->schema_json);
    if (hdr->codec) free(hdr->codec);
    hdr->schema_json = NULL;
    hdr->codec = NULL;
}

/* Розбір заголовка контейнера */
static bool parse_avro_header(ByteReader *r, AvroHeader *hdr) {
    memset(hdr, 0, sizeof(AvroHeader));

    /* 1. Перевірка 4 байтів Magic */
    if (!reader_has_bytes(r, AVRO_MAGIC_SIZE)) return false;
    if (memcmp(r->data + r->offset, EXPECTED_MAGIC, AVRO_MAGIC_SIZE) != 0) {
        return false;
    }
    r->offset += AVRO_MAGIC_SIZE;

    /* 2. Розбір карти метаданих (Metadata Map) */
    while (true) {
        int64_t count = 0;
        if (!read_varint_long(r, &count)) goto fail;
        if (count == 0) break; /* Кінець карти */

        if (count < 0) {
            /* Від'ємне число означає наявність сумарного розміру блоку карти в байтах */
            count = -count;
            int64_t byte_size = 0;
            if (!read_varint_long(r, &byte_size)) goto fail;
        }

        for (int64_t i = 0; i < count; i++) {
            char *key = NULL;
            uint8_t *val_bytes = NULL;
            size_t val_len = 0;

            if (!read_avro_string(r, &key, NULL)) goto fail;
            if (!read_avro_bytes(r, &val_bytes, &val_len)) {
                free(key);
                goto fail;
            }

            if (strcmp(key, "avro.schema") == 0) {
                hdr->schema_json = (char *)malloc(val_len + 1);
                if (hdr->schema_json) {
                    memcpy(hdr->schema_json, val_bytes, val_len);
                    hdr->schema_json[val_len] = '\0';
                }
            } else if (strcmp(key, "avro.codec") == 0) {
                hdr->codec = (char *)malloc(val_len + 1);
                if (hdr->codec) {
                    memcpy(hdr->codec, val_bytes, val_len);
                    hdr->codec[val_len] = '\0';
                }
            }

            free(key);
            free(val_bytes);
        }
    }

    /* 3. Зчитування 16-байтного синхромаркера */
    if (!reader_has_bytes(r, AVRO_SYNC_SIZE)) goto fail;
    memcpy(hdr->sync_marker, r->data + r->offset, AVRO_SYNC_SIZE);
    r->offset += AVRO_SYNC_SIZE;

    return true;

fail:
    free_avro_header(hdr);
    return false;
}

/* Імітація обробки записів із блоку з узгодженням схеми */
static void process_record_with_resolution(ByteReader *block_r) {
    /* Приклад схеми записувача (Writer): { id: int, name: string, legacy_tag: int }
       Приклад схеми зчитувача (Reader):   { id: long (розширено), name: string, email: string (default="") } */

    int64_t id_raw = 0;
    if (!read_varint_long(block_r, &id_raw)) return;

    char *name_str = NULL;
    if (!read_avro_string(block_r, &name_str, NULL)) return;

    /* Поле legacy_tag було у файлі, але не потрібне зчитувачу: пропускаємо байти */
    int64_t legacy_tag_discarded = 0;
    if (!read_varint_long(block_r, &legacy_tag_discarded)) {
        free(name_str);
        return;
    }

    /* Узгоджене представлення в пам'яті */
    int64_t resolved_id = id_raw;              /* Просування типу int -> long */
    const char *resolved_email = "default@none"; /* Підстановка значення за замовчуванням */

    printf("  [Запис] id: %lld, name: '%s', email: '%s' (legacy_tag %lld пропущено)\n",
           (long long)resolved_id, name_str, resolved_email, (long long)legacy_tag_discarded);

    free(name_str);
}

/* Ітерація по блоках даних контейнера */
static void parse_avro_data_blocks(ByteReader *r, const AvroHeader *hdr) {
    int block_index = 0;

    while (reader_has_bytes(r, 1)) {
        int64_t record_count = 0;
        int64_t byte_size = 0;

        if (!read_varint_long(r, &record_count)) break;
        if (!read_varint_long(r, &byte_size)) break;

        printf("Блок #%d: %lld записів, %lld байтів даних\n",
               ++block_index, (long long)record_count, (long long)byte_size);

        if (!reader_has_bytes(r, (size_t)byte_size)) {
            fprintf(stderr, "Помилка: неповний блок даних на зміщенні %zu\n", r->offset);
            return;
        }

        /* Створюємо підчитач для вмісту блоку */
        ByteReader block_r = {
            .data = r->data + r->offset,
            .size = (size_t)byte_size,
            .offset = 0
        };
        r->offset += (size_t)byte_size;

        /* Розбираємо записи всередині блоку */
        for (int64_t i = 0; i < record_count; i++) {
            process_record_with_resolution(&block_r);
        }

        /* Перевірка 16-байтного синхромаркера наприкінці блоку */
        if (!reader_has_bytes(r, AVRO_SYNC_SIZE)) {
            fprintf(stderr, "Помилка: відсутній маркер синхронізації блоку\n");
            return;
        }

        if (memcmp(r->data + r->offset, hdr->sync_marker, AVRO_SYNC_SIZE) != 0) {
            fprintf(stderr, "Критична помилка: маркер синхронізації блоку пошкоджено!\n");
            return;
        }
        r->offset += AVRO_SYNC_SIZE;
        printf("  -> Синхромаркер блоку верифіковано успішно.\n");
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <optional>
#include <expected>
#include <array>
#include <cstring>
#include <cstdint>

namespace avro {

constexpr size_t SYNC_SIZE = 16;
constexpr size_t MAGIC_SIZE = 4;
constexpr std::array<uint8_t, MAGIC_SIZE> EXPECTED_MAGIC = {'O', 'b', 'j', 0x01};

enum class ParseError {
    UnexpectedEof,
    InvalidMagic,
    CorruptedVarint,
    SyncMismatch,
    InvalidSchema
};

/* Зручний неволодіючий зчитувач двійкового зрізу */
class SpanReader {
public:
    explicit SpanReader(std::span<const uint8_t> buffer) : buffer_(buffer), offset_(0) {}

    [[nodiscard]] bool has_bytes(size_t n) const noexcept {
        return offset_ + n <= buffer_.size();
    }

    [[nodiscard]] size_t remaining() const noexcept {
        return buffer_.size() - offset_;
    }

    [[nodiscard]] size_t offset() const noexcept {
        return offset_;
    }

    std::expected<uint8_t, ParseError> read_u8() noexcept {
        if (!has_bytes(1)) return std::unexpected(ParseError::UnexpectedEof);
        return buffer_[offset_++];
    }

    /* Зчитування 64-бітного цілого Zigzag Varint */
    std::expected<int64_t, ParseError> read_zigzag_long() noexcept {
        uint64_t raw = 0;
        int shift = 0;

        while (has_bytes(1)) {
            uint8_t b = buffer_[offset_++];
            raw |= static_cast<uint64_t>(b & 0x7F) << shift;
            if ((b & 0x80) == 0) {
                int64_t decoded = static_cast<int64_t>((raw >> 1) ^ (-(raw & 1)));
                return decoded;
            }
            shift += 7;
            if (shift >= 64) return std::unexpected(ParseError::CorruptedVarint);
        }
        return std::unexpected(ParseError::UnexpectedEof);
    }

    /* Зчитування рядка UTF-8 */
    std::expected<std::string, ParseError> read_string() {
        auto len_res = read_zigzag_long();
        if (!len_res || *len_res < 0) return std::unexpected(ParseError::CorruptedVarint);

        size_t len = static_cast<size_t>(*len_res);
        if (!has_bytes(len)) return std::unexpected(ParseError::UnexpectedEof);

        std::string s(reinterpret_cast<const char*>(buffer_.data() + offset_), len);
        offset_ += len;
        return s;
    }

    /* Зчитування двійкового блоку байтів */
    std::expected<std::span<const uint8_t>, ParseError> read_bytes() noexcept {
        auto len_res = read_zigzag_long();
        if (!len_res || *len_res < 0) return std::unexpected(ParseError::CorruptedVarint);

        size_t len = static_cast<size_t>(*len_res);
        if (!has_bytes(len)) return std::unexpected(ParseError::UnexpectedEof);

        std::span<const uint8_t> slice(buffer_.data() + offset_, len);
        offset_ += len;
        return slice;
    }

    std::expected<void, ParseError> skip(size_t n) noexcept {
        if (!has_bytes(n)) return std::unexpected(ParseError::UnexpectedEof);
        offset_ += n;
        return {};
    }

private:
    std::span<const uint8_t> buffer_;
    size_t offset_{0};
};

/* Метадані та схема контейнера */
struct ContainerHeader {
    std::string schema_json;
    std::string codec{"null"};
    std::array<uint8_t, SYNC_SIZE> sync_marker{};
};

/* Розбір заголовка Avro OCF */
std::expected<ContainerHeader, ParseError> parse_header(SpanReader& reader) {
    ContainerHeader header;

    // 1. Перевірка магічних байтів
    if (!reader.has_bytes(MAGIC_SIZE)) return std::unexpected(ParseError::UnexpectedEof);
    for (size_t i = 0; i < MAGIC_SIZE; ++i) {
        if (reader.read_u8().value() != EXPECTED_MAGIC[i]) {
            return std::unexpected(ParseError::InvalidMagic);
        }
    }

    // 2. Розбір карти метаданих
    while (true) {
        auto count_res = reader.read_zigzag_long();
        if (!count_res) return std::unexpected(count_res.error());

        int64_t count = *count_res;
        if (count == 0) break; // Кінець метаданих

        if (count < 0) {
            count = -count;
            auto byte_size_res = reader.read_zigzag_long();
            if (!byte_size_res) return std::unexpected(byte_size_res.error());
        }

        for (int64_t i = 0; i < count; ++i) {
            auto key_res = reader.read_string();
            if (!key_res) return std::unexpected(key_res.error());

            auto val_res = reader.read_bytes();
            if (!val_res) return std::unexpected(val_res.error());

            if (*key_res == "avro.schema") {
                header.schema_json = std::string(
                    reinterpret_cast<const char*>(val_res->data()), val_res->size()
                );
            } else if (*key_res == "avro.codec") {
                header.codec = std::string(
                    reinterpret_cast<const char*>(val_res->data()), val_res->size()
                );
            }
        }
    }

    // 3. Зчитування синхромаркера
    if (!reader.has_bytes(SYNC_SIZE)) return std::unexpected(ParseError::UnexpectedEof);
    for (size_t i = 0; i < SYNC_SIZE; ++i) {
        header.sync_marker[i] = reader.read_u8().value();
    }

    return header;
}

/* Прикладний об'єкт після узгодження схем */
struct ResolvedUserRecord {
    int64_t id;
    std::string name;
    std::string email;
};

/* Зчитування запису із застосуванням правил еволюції схеми */
std::expected<ResolvedUserRecord, ParseError> decode_and_resolve_record(SpanReader& block_reader) {
    // Writer Schema містила: id (int), name (string), legacy_score (int)
    // Reader Schema очікує: id (long), name (string), email (string, default="none@domain")

    auto id_res = block_reader.read_zigzag_long();
    if (!id_res) return std::unexpected(id_res.error());

    auto name_res = block_reader.read_string();
    if (!name_res) return std::unexpected(name_res.error());

    // Пропуск застарілого поля записувача
    auto legacy_res = block_reader.read_zigzag_long();
    if (!legacy_res) return std::unexpected(legacy_res.error());

    return ResolvedUserRecord{
        .id = *id_res,                               // Безпечне розширення int -> long
        .name = std::move(*name_res),
        .email = "none@domain"                       // Значення за замовчуванням
    };
}

/* Ітератор по блоках контейнера */
void process_avro_container(std::span<const uint8_t> file_bytes) {
    SpanReader reader(file_bytes);
    auto header_res = parse_header(reader);
    if (!header_res) {
        std::cerr << "Помилка розбору заголовка Avro\n";
        return;
    }

    const auto& header = *header_res;
    std::cout << "Вбудована JSON-схема файлу:\n" << header.schema_json << "\n";
    std::cout << "Кодек стиснення: " << header.codec << "\n\n";

    size_t block_num = 0;
    while (reader.has_bytes(1)) {
        auto record_count = reader.read_zigzag_long();
        auto block_bytes_size = reader.read_zigzag_long();
        if (!record_count || !block_bytes_size) break;

        std::cout << "Блок #" << ++block_num << ": " << *record_count << " записів, "
                  << *block_bytes_size << " байтів\n";

        if (!reader.has_bytes(static_cast<size_t>(*block_bytes_size))) {
            std::cerr << "Помилка: неповний блок даних\n";
            return;
        }

        auto block_span = file_bytes.subspan(reader.offset(), static_cast<size_t>(*block_bytes_size));
        reader.skip(static_cast<size_t>(*block_bytes_size)).value();

        SpanReader block_reader(block_span);
        for (int64_t i = 0; i < *record_count; ++i) {
            auto rec = decode_and_resolve_record(block_reader);
            if (rec) {
                std::cout << "  [User] id=" << rec->id << ", name='" << rec->name
                          << "', email='" << rec->email << "'\n";
            }
        }

        // Перевірка маркера синхронізації
        if (!reader.has_bytes(SYNC_SIZE)) {
            std::cerr << "Помилка: відсутній маркер синхронізації\n";
            return;
        }

        for (size_t i = 0; i < SYNC_SIZE; ++i) {
            if (reader.read_u8().value() != header.sync_marker[i]) {
                std::cerr << "Критична помилка: маркер синхронізації пошкоджено!\n";
                return;
            }
        }
        std::cout << "  -> Синхромаркер перевірено успішно.\n";
    }
}

} // namespace avro
```
:::

### Практичні деталі та пастки реалізації

1. **Від'ємні лічильники блоків у карті метаданих.** Специфікація Avro дозволяє записувати від'ємний `count` у карті або масиві. Це сигналізує, що одразу після лічильника слідує `size` блоку в байтах, дозволяючи оптимізованому парсеру пропустити весь блок без розбору окремих пар ключ-значення. Пропуск обробки від'ємного знаку в коді ламає сумісність із файлами, створеними офіційними Java- та Go-бібліотеками.
2. **Захист від переповнення розрядної сітки у Varint.** 64-бітний varint займає від 1 до максимум 10 байтів у пам'яті (причому 10-й байт містить лише 1 біт даних). Нескінченний цикл або зациклення зсуву при пошкоджених вхідних байтах запобігається жорсткою перевіркою лічильника бітового зсуву (`shift >= 64`).
3. **Невирівняний доступ до пам'яті (*unaligned memory access*).** Avro записує байти підряд без вирівнювання на 4 чи 8 байтів. Спроба інтерпретувати покажчик `uint8_t*` як `int64_t*` через пряме розіменування призводить до апаратного виключення (*bus error*) на процесорах ARM/MIPS або до штрафу у десятки тактів процесора на архітектурах x86-64. Зчитування байтів через послідовні зсуви гарантує портативність на будь-якому залізі.
4. **Управління пам'яттю та володіння буферами.** У реалізації на C розробник зобов'язаний вручну відстежувати життєвий цикл кожного виділеного рядка та буфера (`schema_json`, `codec`, тимчасові рядкові поля записів), що у разі несподіваного обриву потоку даних загрожує витоками пам'яті. На противагу цьому, реалізація на C++ використовує семантику неволодіючих зрізів `std::span` та `std::string_view` для парсингу «на місці» без жодного зайвого динамічного виділення пам'яті на купі (*zero allocation during block scanning*), що кардинально прискорює пропуск непотрібних блоків.
