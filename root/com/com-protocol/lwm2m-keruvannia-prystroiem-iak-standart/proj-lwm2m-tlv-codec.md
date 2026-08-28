# ⚙️ Двійковий кодек LwM2M TLV для мікроконтролерів без динамічної пам'яті

Двійковий формат серіалізації OMA LwM2M TLV (Type-Length-Value) розроблено спеціально для передачі складних ієрархічних структур даних через мережеві датаграми з мінімальними обчислювальними витратами на мікроконтролерах із суворими обмеженнями пам'яті RAM.

На відміну від важких текстових форматів JSON або XML, LwM2M TLV не потребує побудови динамічних синтаксичних дерев, виділення пам'яті в купі (`malloc`) чи складного лексичного аналізу. Весь процес декодування та кодування виконується в один прохід через лінійні буфери фіксованого розміру з гарантованим захистом від переповнення та нульовим копіюванням даних (Zero-Copy).

---

### Архітектурні вимоги до кодека на мікроконтролері

Розробка вбудованого кодека для обробки мережевих пакетів LwM2M на базі процесорів архітектури ARM Cortex-M, RISC-V або Xtensa стикається з трьома критичними обмеженнями:

1. **Повна відмова від динамічного виділення пам'яті (`malloc` / `free`):**
   У пристроях класу C0/C1 із загальним обсягом RAM від 8 до 64 КБ використання купи неминуче призводить до фрагментації пам'яті після тривалої роботи. Раптовий збій алокатора під час розбору великого пакета конфігурації викликає падіння системи. Вбудований кодек зобов'язаний працювати виключно з буферами фіксованого розміру, розміщеними на стеку або у статичній секції BSS.
2. **Захист від нерозподіленого доступу до пам'яті (Unaligned Memory Access):**
   Процесорні ядра молодших лінійок (зокрема ARM Cortex-M0 та Cortex-M0+) не підтримують апаратне зчитування 16-бітних або 32-бітних чисел за непарними адресами пам'яті. Пряме розіменування вказівника на зразок `*(uint32_t*)&buf[offset]` у разі зміщення `offset = 1` генерує апаратне переривання `HardFault`. Кодек повинен зчитувати багатобайтові поля побайтово через зсуви або через безпечні функції `memcpy`.
3. **Мережевий порядок байтів (Big-Endian):**
   Стандарт LwM2M вимагає передачі всіх багатобайтових чисел (ідентифікаторів, довжин, цілих та дійсних значень Float) у порядку від старшого байта до молодшого (Big-Endian). Оскільки переважна більшість мікроконтролерів використовує порядок Little-Endian, кодек має здійснювати явну конвертацію байтів під час пакування та розпакування.

---

### Структура байта типу (Type Header)

Кожен елемент TLV починається з фіксованого 8-бітного заголовка типу (Type Byte), що містить чотири бітові поля:

```
 7   6   5   4   3   2   1   0
+---+---+---+---+---+---+---+---+
| Type  |ID | Length|   Value   |
| (2b)  |(1)| (2b)  | Length(3b)|
+---+---+---+---+---+---+---+---+
```

1. **Bits 7–6 (Тип вузла ієрархії):**
   - `00` (`0`): **Object Instance** — екземпляр об'єкта, значення містить послідовність вкладених TLV-записів окремих ресурсів;
   - `01` (`1`): **Resource Instance** — екземпляр значення всередині множинного ресурсу;
   - `10` (`2`): **Multiple Resource** — множинний ресурс, що містить список вкладених `Resource Instance`;
   - `11` (`3`): **Resource with Value** — звичайний одиничний ресурс із прямим значенням (ціле число, float, рядок або бінарний масив).
2. **Bit 5 (Довжина ідентифікатора ID):**
   - `0`: Ідентифікатор займає 8 бітів (1 байт, числовий діапазон `0..255`);
   - `1`: Ідентифікатор займає 16 бітів (2 байти Big-Endian, діапазон `0..65535`).
3. **Bits 4–3 (Тип поля довжини Length):**
   - `00`: Поле Length відсутнє; довжина значення Value зберігається безпосередньо в бітах 2–0 байта Type (діапазон `0..7` байтів);
   - `01`: Поле Length займає 8 бітів (1 байт, значення довжини `0..255`);
   - `10`: Поле Length займає 16 бітів (2 байти Big-Endian, значення довжини `0..65535`);
   - `11`: Поле Length займає 24 біти (3 байти Big-Endian, значення довжини `0..16777215`).
4. **Bits 2–0 (Довжина значення Value Length):**
   - Якщо Bits 4–3 == `00`, ці 3 біти задають точну довжину корисного навантаження (від 0 до 7 байтів);
   - Якщо Bits 4–3 != `00`, ці 3 біти ігноруються або використовуються як резервні.

---

### Правила двійкового кодування значень (Value Encoding)

- **Цілі числа (Integer / Time):** Кодуються у форматі зі знаком або без знака у мережевому порядку байтів (Big-Endian). Число упаковується в мінімально необхідну кількість байтів: `1` (uint8/int8), `2` (int16), `4` (int32) або `8` (int64). Наприклад, число `100` займає 1 байт (`0x64`), а `1000` — 2 байти (`0x03 0xE8`).
- **Дійсні числа (Float):** Кодуються за стандартом IEEE 754 у мережевому порядку байтів. Довжина становить або 4 байти (Single Precision float32), або 8 байтів (Double Precision float64).
- **Булеві значення (Boolean):** Кодуються 1 байтом: `0` (`false`) або `1` (`true`).
- **Рядки (String) та масиви байтів (Opaque):** Кодуються послідовністю UTF-8 або сирих байтів без кінцевого нуль-термінатора `\0` (довжина явно задана полем Length).

---

### Реалізація кодека TLV на C та C++

Нижче наведено повнофункціональні модулі кодека TLV: реалізацію на чистому ANSI C з перевіркою меж і нульовим динамічним виділенням пам'яті та ідіоматичний еквівалент на сучасному C++ із використанням `std::span`, безпечних типів `enum class` та опціональних значень `std::optional`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* Типи вузлів LwM2M TLV (біти 7-6) */
typedef enum {
    LWM2M_TLV_OBJECT_INSTANCE   = 0x00,
    LWM2M_TLV_RESOURCE_INSTANCE = 0x01,
    LWM2M_TLV_MULTIPLE_RESOURCE = 0x02,
    LWM2M_TLV_RESOURCE          = 0x03
} lwm2m_tlv_type_t;

/* Структура розпарсеного елемента TLV */
typedef struct {
    lwm2m_tlv_type_t type;
    uint16_t id;
    uint32_t length;
    const uint8_t *value;
} lwm2m_tlv_record_t;

/*
 * Декодування одного елемента TLV з буфера.
 * Повертає кількість спожитих байтів з буфера (0 у разі помилки або браку даних).
 */
size_t lwm2m_tlv_decode(const uint8_t *buf, size_t buf_len, lwm2m_tlv_record_t *out_rec) {
    if (buf == NULL || out_rec == NULL || buf_len < 2) {
        return 0;
    }

    size_t offset = 0;
    uint8_t type_byte = buf[offset++];

    /* 1. Витягуємо тип вузла */
    out_rec->type = (lwm2m_tlv_type_t)((type_byte >> 6) & 0x03);
    uint8_t id_len_flag = (type_byte >> 5) & 0x01;
    uint8_t len_type = (type_byte >> 3) & 0x03;
    uint8_t val_len_bits = type_byte & 0x07;

    /* 2. Декодуємо ідентифікатор ID */
    if (id_len_flag == 0) {
        /* 8-бітний ID */
        out_rec->id = buf[offset++];
    } else {
        /* 16-бітний ID (Big-Endian) */
        if (offset + 2 > buf_len) return 0;
        out_rec->id = ((uint16_t)buf[offset] << 8) | (uint16_t)buf[offset + 1];
        offset += 2;
    }

    /* 3. Декодуємо довжину Length */
    uint32_t length = 0;
    if (len_type == 0x00) {
        length = val_len_bits;
    } else if (len_type == 0x01) {
        if (offset + 1 > buf_len) return 0;
        length = buf[offset++];
    } else if (len_type == 0x02) {
        if (offset + 2 > buf_len) return 0;
        length = ((uint32_t)buf[offset] << 8) | (uint32_t)buf[offset + 1];
        offset += 2;
    } else if (len_type == 0x03) {
        if (offset + 3 > buf_len) return 0;
        length = ((uint32_t)buf[offset] << 16) | ((uint32_t)buf[offset + 1] << 8) | (uint32_t)buf[offset + 2];
        offset += 3;
    }

    /* 4. Перевірка наявності даних у буфері */
    if (offset + length > buf_len) {
        return 0; /* Неповний пакет */
    }

    out_rec->length = length;
    out_rec->value = (length > 0) ? &buf[offset] : NULL;
    offset += length;

    return offset;
}

/* Допоміжні функції читання значень */
bool lwm2m_tlv_get_int64(const lwm2m_tlv_record_t *rec, int64_t *val) {
    if (rec == NULL || val == NULL || rec->length == 0 || rec->length > 8) return false;
    int64_t res = 0;
    /* Знакове розширення для першого байта */
    if (rec->value[0] & 0x80) {
        res = -1;
    }
    for (size_t i = 0; i < rec->length; i++) {
        res = (res << 8) | rec->value[i];
    }
    *val = res;
    return true;
}

bool lwm2m_tlv_get_float(const lwm2m_tlv_record_t *rec, float *val) {
    if (rec == NULL || val == NULL || rec->length != 4) return false;
    union {
        uint32_t u;
        float f;
    } conv;
    conv.u = ((uint32_t)rec->value[0] << 24) |
             ((uint32_t)rec->value[1] << 16) |
             ((uint32_t)rec->value[2] << 8)  |
             (uint32_t)rec->value[3];
    *val = conv.f;
    return true;
}

/* Кодування одного числового ресурсу (int32) у TLV буфер */
size_t lwm2m_tlv_encode_int32(uint8_t *buf, size_t buf_len, uint16_t res_id, int32_t value) {
    /* Визначаємо мінімальну кількість байтів для збереження числа */
    uint8_t val_buf[4];
    size_t val_len = 0;

    if (value >= -128 && value <= 127) {
        val_buf[0] = (uint8_t)(value & 0xFF);
        val_len = 1;
    } else if (value >= -32768 && value <= 32767) {
        val_buf[0] = (uint8_t)((value >> 8) & 0xFF);
        val_buf[1] = (uint8_t)(value & 0xFF);
        val_len = 2;
    } else {
        val_buf[0] = (uint8_t)((value >> 24) & 0xFF);
        val_buf[1] = (uint8_t)((value >> 16) & 0xFF);
        val_buf[2] = (uint8_t)((value >> 8) & 0xFF);
        val_buf[3] = (uint8_t)(value & 0xFF);
        val_len = 4;
    }

    size_t header_len = 1 + (res_id > 255 ? 2 : 1);
    if (header_len + val_len > buf_len) return 0;

    size_t offset = 0;
    uint8_t type_byte = (LWM2M_TLV_RESOURCE << 6);
    if (res_id > 255) {
        type_byte |= (1 << 5); /* 16-бітний ID */
    }
    type_byte |= (uint8_t)(val_len & 0x07); /* Довжина 0..7 у бітах 2-0 */

    buf[offset++] = type_byte;
    if (res_id > 255) {
        buf[offset++] = (uint8_t)((res_id >> 8) & 0xFF);
        buf[offset++] = (uint8_t)(res_id & 0xFF);
    } else {
        buf[offset++] = (uint8_t)(res_id & 0xFF);
    }

    memcpy(&buf[offset], val_buf, val_len);
    offset += val_len;

    return offset;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>
#include <array>
#include <string_view>

namespace lwm2m {

enum class TlvType : uint8_t {
    ObjectInstance   = 0x00,
    ResourceInstance = 0x01,
    MultipleResource = 0x02,
    Resource         = 0x03
};

struct TlvRecord {
    TlvType type{TlvType::Resource};
    uint16_t id{0};
    std::span<const uint8_t> value{};

    [[nodiscard]] std::optional<int64_t> as_int64() const noexcept {
        if (value.empty() || value.size() > 8) return std::nullopt;
        int64_t res = (value[0] & 0x80) ? -1 : 0;
        for (uint8_t b : value) {
            res = (res << 8) | b;
        }
        return res;
    }

    [[nodiscard]] std::optional<float> as_float() const noexcept {
        if (value.size() != 4) return std::nullopt;
        uint32_t raw = (static_cast<uint32_t>(value[0]) << 24) |
                       (static_cast<uint32_t>(value[1]) << 16) |
                       (static_cast<uint32_t>(value[2]) << 8)  |
                       static_cast<uint32_t>(value[3]);
        float f;
        std::memcpy(&f, &raw, sizeof(f));
        return f;
    }

    [[nodiscard]] std::optional<std::string_view> as_string() const noexcept {
        if (value.empty()) return std::string_view{};
        return std::string_view{reinterpret_cast<const char*>(value.data()), value.size()};
    }
};

class TlvDecoder {
public:
    explicit constexpr TlvDecoder(std::span<const uint8_t> buffer) noexcept : buffer_(buffer) {}

    [[nodiscard]] bool has_next() const noexcept {
        return cursor_ < buffer_.size();
    }

    [[nodiscard]] std::optional<TlvRecord> next() noexcept {
        if (cursor_ + 2 > buffer_.size()) {
            return std::nullopt;
        }

        const uint8_t type_byte = buffer_[cursor_++];
        const auto type = static_cast<TlvType>((type_byte >> 6) & 0x03);
        const bool id_is_16bit = (type_byte & (1 << 5)) != 0;
        const uint8_t len_type = (type_byte >> 3) & 0x03;
        const uint8_t val_len_bits = type_byte & 0x07;

        uint16_t id = 0;
        if (!id_is_16bit) {
            id = buffer_[cursor_++];
        } else {
            if (cursor_ + 2 > buffer_.size()) return std::nullopt;
            id = (static_cast<uint16_t>(buffer_[cursor_]) << 8) | buffer_[cursor_ + 1];
            cursor_ += 2;
        }

        uint32_t length = 0;
        if (len_type == 0x00) {
            length = val_len_bits;
        } else if (len_type == 0x01) {
            if (cursor_ + 1 > buffer_.size()) return std::nullopt;
            length = buffer_[cursor_++];
        } else if (len_type == 0x02) {
            if (cursor_ + 2 > buffer_.size()) return std::nullopt;
            length = (static_cast<uint32_t>(buffer_[cursor_]) << 8) | buffer_[cursor_ + 1];
            cursor_ += 2;
        } else if (len_type == 0x03) {
            if (cursor_ + 3 > buffer_.size()) return std::nullopt;
            length = (static_cast<uint32_t>(buffer_[cursor_]) << 16) |
                     (static_cast<uint32_t>(buffer_[cursor_ + 1]) << 8) |
                     buffer_[cursor_ + 2];
            cursor_ += 3;
        }

        if (cursor_ + length > buffer_.size()) {
            return std::nullopt;
        }

        TlvRecord record{
            .type = type,
            .id = id,
            .value = buffer_.subspan(cursor_, length)
        };
        cursor_ += length;

        return record;
    }

private:
    std::span<const uint8_t> buffer_;
    size_t cursor_{0};
};

class TlvEncoder {
public:
    explicit constexpr TlvEncoder(std::span<uint8_t> out_buffer) noexcept : out_(out_buffer) {}

    [[nodiscard]] bool write_int32(uint16_t res_id, int32_t value) noexcept {
        std::array<uint8_t, 4> val_bytes{};
        size_t val_len = 0;

        if (value >= -128 && value <= 127) {
            val_bytes[0] = static_cast<uint8_t>(value & 0xFF);
            val_len = 1;
        } else if (value >= -32768 && value <= 32767) {
            val_bytes[0] = static_cast<uint8_t>((value >> 8) & 0xFF);
            val_bytes[1] = static_cast<uint8_t>(value & 0xFF);
            val_len = 2;
        } else {
            val_bytes[0] = static_cast<uint8_t>((value >> 24) & 0xFF);
            val_bytes[1] = static_cast<uint8_t>((value >> 16) & 0xFF);
            val_bytes[2] = static_cast<uint8_t>((value >> 8) & 0xFF);
            val_bytes[3] = static_cast<uint8_t>(value & 0xFF);
            val_len = 4;
        }

        const size_t header_len = 1 + (res_id > 255 ? 2 : 1);
        if (offset_ + header_len + val_len > out_.size()) {
            return false;
        }

        uint8_t type_byte = (static_cast<uint8_t>(TlvType::Resource) << 6);
        if (res_id > 255) {
            type_byte |= (1 << 5);
        }
        type_byte |= static_cast<uint8_t>(val_len & 0x07);

        out_[offset_++] = type_byte;
        if (res_id > 255) {
            out_[offset_++] = static_cast<uint8_t>((res_id >> 8) & 0xFF);
            out_[offset_++] = static_cast<uint8_t>(res_id & 0xFF);
        } else {
            out_[offset_++] = static_cast<uint8_t>(res_id & 0xFF);
        }

        std::memcpy(&out_[offset_], val_bytes.data(), val_len);
        offset_ += val_len;
        return true;
    }

    [[nodiscard]] size_t bytes_written() const noexcept { return offset_; }

private:
    std::span<uint8_t> out_;
    size_t offset_{0};
};

} // namespace lwm2m
```
:::

---

### Пастки реалізації та крайові випадки

1. **Знакове розширення (Sign Extension) для від'ємних цілих чисел:**
   Якщо ресурс типу Integer містить від'ємне значення, упаковане лише в 1 або 2 байти (наприклад, `-10` зберігається як один байт `0xF6`), функція декодування зобов'язана виконати знакове розширення до 64 бітів (`0xFFFFFFFFFFFFFFF6`). Якщо перевірити лише перший біт `0x80` без розширення, звичайне присвоєння перетворить від'ємне число на додатне `246`.
2. **Розбір вкладених структур (Nested TLV Traversal):**
   При читанні екземпляра об'єкта (Type `00` Object Instance) поле `Value` містить не сирі байти даних, а суцільний блок послідовних TLV-записів окремих ресурсів. Декодер має створити вкладений ітератор, обмежений діапазоном `offset` та батьківським розміром `length`. Якщо довжина вкладеного ресурсу перевищує задекларовану довжину батьківського екземпляра, пакет вважається дефектним і негайно відкидається.
3. **Захист від навмисного переповнення буфера:**
   Зловмисник або пошкоджена датаграма може передати заголовок із полем довжини Length у 3 байти зі значенням `0xFFFFFF` (16 мегабайтів) при фізичному розмірі пакета UDP лише у 40 байтів. Перед будь-яким розіменуванням вказівника на корисне навантаження декодер обов'язково перевіряє умову `offset + length <= total_buffer_len`.
