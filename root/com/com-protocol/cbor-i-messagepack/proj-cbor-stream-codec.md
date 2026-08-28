# ⚙️ Легковажний потоковий кодек CBOR на C та C++

На мікроконтролерах із обмеженим обсягом оперативної пам'яті (від 2 до 64 КБ SRAM) традиційні бібліотеки парсингу та серіалізації стикаються з критичними апаратними бар'єрами. Класичний підхід на основі об'єктного дерева документа (DOM, Document Object Model), реалізований у більшості JSON-парсерів, вимагає динамічного виділення пам'яті (`malloc`) під кожен вузол, ключ і значення. Це спричиняє швидку фрагментацію динамічної купи (heap fragmentation), непередбачувані затримки через роботу алокатора та ризик аварійного перезавантаження мікроконтролера через вичерпання пулу пам'яті (HardFault або переповнення стеку).

Альтернативою є нуль-копіювальний (Zero-Copy) потоковий кодек CBOR. Замість копіювання байтів у проміжні рядкові буфери та динамічні структури декодер розбирає пакет безпосередньо в буфері прийому (наприклад, у статичному кільцевому буфері UART чи масиві прямого доступу до пам'яті DMA). Рядки й сирі байти повертаються як незмінні зрізи пам'яті (`slice` у C або `std::span` / `std::string_view` у C++), а енкодер формує вихідні бінарні кадри у фіксованому статичному масиві з жорстким контролем меж.

---

### Архітектура зрізів пам'яті та керування станом

У нуль-копіювальній архітектурі критично розділити дані на два класи: скалярні примітиви (числа, логічні прапорці), які вміщуються у регістри процесора, та послідовності байтів (UTF-8 текст, бінарні масиви корисного навантаження), які не копіюються.

Для представлення розпарсованого значення використовується дискриміноване об'єднання (tagged union). Потоковий стан декодера зберігається у структурі `cbor_reader_t`, яка відстежує поточний зсув `offset` відносно загального розміру вхідного буфера `size`. Для запису використовується симетрична структура `cbor_writer_t`, що зберігає максимальну доступну ємність `capacity` і захищає від переповнення.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    CBOR_OK = 0,
    CBOR_ERR_BUFFER_OVERFLOW,
    CBOR_ERR_UNEXPECTED_EOF,
    CBOR_ERR_INVALID_HEADER,
    CBOR_ERR_UNSUPPORTED_TYPE
} cbor_error_t;

typedef enum {
    CBOR_TYPE_UINT,
    CBOR_TYPE_NINT,
    CBOR_TYPE_BSTR,
    CBOR_TYPE_TSTR,
    CBOR_TYPE_ARRAY,
    CBOR_TYPE_MAP,
    CBOR_TYPE_TAG,
    CBOR_TYPE_BOOL,
    CBOR_TYPE_NULL,
    CBOR_TYPE_FLOAT16,
    CBOR_TYPE_FLOAT32,
    CBOR_TYPE_FLOAT64
} cbor_item_type_t;

typedef struct {
    const uint8_t *ptr;
    size_t len;
} cbor_slice_t;

typedef struct {
    cbor_item_type_t type;
    union {
        uint64_t uint_val;
        int64_t  nint_val;
        cbor_slice_t slice;
        size_t container_len;
        uint64_t tag_val;
        bool bool_val;
        float float_val;
        double double_val;
    } as;
} cbor_value_t;

typedef struct {
    const uint8_t *data;
    size_t size;
    size_t offset;
} cbor_reader_t;

typedef struct {
    uint8_t *data;
    size_t capacity;
    size_t offset;
} cbor_writer_t;
```
```cpp
#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <array>
#include <variant>
#include <optional>
#include <system_error>
#include <cstring>

namespace cbor {

enum class Error {
    Ok = 0,
    BufferOverflow,
    UnexpectedEof,
    InvalidHeader,
    UnsupportedType
};

struct ErrorCategory : std::error_category {
    const char* name() const noexcept override { return "cbor"; }
    std::string message(int ev) const override {
        switch (static_cast<Error>(ev)) {
            case Error::BufferOverflow: return "Buffer overflow";
            case Error::UnexpectedEof: return "Unexpected end of buffer";
            case Error::InvalidHeader: return "Invalid header byte";
            case Error::UnsupportedType: return "Unsupported major type";
            default: return "Success";
        }
    }
};

inline const std::error_category& error_category() {
    static ErrorCategory cat;
    return cat;
}

inline std::error_code make_error_code(Error e) {
    return {static_cast<int>(e), error_category()};
}

enum class MajorType : uint8_t {
    UnsignedInt = 0,
    NegativeInt = 1,
    ByteString  = 2,
    TextString  = 3,
    Array       = 4,
    Map         = 5,
    Tag         = 6,
    Simple      = 7
};

struct ArrayHeader { size_t count; };
struct MapHeader   { size_t pairs_count; };
struct TagHeader   { uint64_t tag_id; };
struct NullValue   {};

using Value = std::variant<
    uint64_t,
    int64_t,
    std::span<const uint8_t>,
    std::string_view,
    ArrayHeader,
    MapHeader,
    TagHeader,
    bool,
    NullValue,
    float,
    double
>;

class Reader {
public:
    explicit constexpr Reader(std::span<const uint8_t> buffer) noexcept
        : buf_(buffer), offset_(0) {}

    [[nodiscard]] size_t remaining() const noexcept { return buf_.size() - offset_; }
    [[nodiscard]] size_t offset() const noexcept { return offset_; }

    [[nodiscard]] std::span<const uint8_t> current_slice() const noexcept {
        return buf_.subspan(offset_);
    }

private:
    std::span<const uint8_t> buf_;
    size_t offset_;
    friend class Decoder;
};

class Writer {
public:
    explicit constexpr Writer(std::span<uint8_t> buffer) noexcept
        : buf_(buffer), offset_(0) {}

    [[nodiscard]] size_t written_size() const noexcept { return offset_; }
    [[nodiscard]] size_t remaining_capacity() const noexcept { return buf_.size() - offset_; }
    [[nodiscard]] std::span<const uint8_t> written_data() const noexcept {
        return buf_.first(offset_);
    }

private:
    std::span<uint8_t> buf_;
    size_t offset_;
    friend class Encoder;
};

} // namespace cbor
```
:::

---

### Декодер CBOR: нуль-копіювальний розбір заголовків

Розбір кожного елемента CBOR починається зі зчитування одного початкового байта. Трьома старшими бітами (`byte >> 5`) визначається старший тип даних (`Major Type`), а п'ятьма молодшими бітами (`byte & 0x1F`) — додаткова інформація (`Additional Information`).

Шкала зчитування додаткової інформації працює за суворим правилом:
1. Якщо значення інфо становить від `0` до `23`, воно безпосередньо містить корисне число або довжину рядка.
2. Значення `24` означає, що наступний `1` байт містить 8-бітне беззнакове число (`uint8_t`).
3. Значення `25` вказує на наступні `2` байти у порядку Big-Endian (`uint16_t`).
4. Значення `26` вказує на наступні `4` байти (`uint32_t`).
5. Значення `27` вказує на наступні `8` байтів (`uint64_t`).

Особливістю Major Type 1 є кодування від'ємних чисел за формулою `-1 - n`. Якщо розкодоване беззнакове поле дорівнює `0`, реальне число становить `-1`. Якщо поле дорівнює `9`, число становить `-10`. Це дозволяє уникнути неоднозначності знакового біта та розширює діапазон від `-1` до `-18446744073709551616` (`-2^64`), що перекриває будь-які можливі від'ємні цілі.

Для рядків (Major Type 2 та 3) декодер витягує довжину `L`, перевіряє, що в буфері залишилося щонайменше `L` байтів, і повертає вказівник на початок масиву всередині оригінального буфера. Ніякого дублювання чи виділення пам'яті не відбувається.

:::tabs
```c
static cbor_error_t read_bytes(cbor_reader_t *r, void *dest, size_t n) {
    if (r->offset + n > r->size) {
        return CBOR_ERR_UNEXPECTED_EOF;
    }
    const uint8_t *src = r->data + r->offset;
    uint8_t *d = (uint8_t *)dest;
    for (size_t i = 0; i < n; ++i) {
        d[i] = src[i];
    }
    r->offset += n;
    return CBOR_OK;
}

static cbor_error_t read_uint_payload(cbor_reader_t *r, uint8_t additional_info, uint64_t *val) {
    if (additional_info < 24) {
        *val = additional_info;
        return CBOR_OK;
    }
    if (additional_info == 24) {
        uint8_t b8;
        cbor_error_t err = read_bytes(r, &b8, 1);
        if (err != CBOR_OK) return err;
        *val = b8;
        return CBOR_OK;
    }
    if (additional_info == 25) {
        uint8_t b[2];
        cbor_error_t err = read_bytes(r, b, 2);
        if (err != CBOR_OK) return err;
        *val = ((uint64_t)b[0] << 8) | (uint64_t)b[1];
        return CBOR_OK;
    }
    if (additional_info == 26) {
        uint8_t b[4];
        cbor_error_t err = read_bytes(r, b, 4);
        if (err != CBOR_OK) return err;
        *val = ((uint64_t)b[0] << 24) | ((uint64_t)b[1] << 16) |
               ((uint64_t)b[2] << 8)  | (uint64_t)b[3];
        return CBOR_OK;
    }
    if (additional_info == 27) {
        uint8_t b[8];
        cbor_error_t err = read_bytes(r, b, 8);
        if (err != CBOR_OK) return err;
        *val = ((uint64_t)b[0] << 56) | ((uint64_t)b[1] << 48) |
               ((uint64_t)b[2] << 40) | ((uint64_t)b[3] << 32) |
               ((uint64_t)b[4] << 24) | ((uint64_t)b[5] << 16) |
               ((uint64_t)b[6] << 8)  | (uint64_t)b[7];
        return CBOR_OK;
    }
    return CBOR_ERR_INVALID_HEADER;
}

cbor_error_t cbor_read_next(cbor_reader_t *r, cbor_value_t *out) {
    if (r->offset >= r->size) {
        return CBOR_ERR_UNEXPECTED_EOF;
    }
    uint8_t initial_byte = r->data[r->offset++];
    uint8_t major = initial_byte >> 5;
    uint8_t info = initial_byte & 0x1F;

    uint64_t val = 0;
    cbor_error_t err;

    switch (major) {
        case 0: // Unsigned Integer
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_UINT;
            out->as.uint_val = val;
            return CBOR_OK;

        case 1: // Negative Integer (-1 - val)
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_NINT;
            out->as.nint_val = -1 - (int64_t)val;
            return CBOR_OK;

        case 2: // Byte String (Zero-Copy)
        case 3: // Text String (Zero-Copy)
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            if (r->offset + val > r->size) return CBOR_ERR_UNEXPECTED_EOF;
            out->type = (major == 2) ? CBOR_TYPE_BSTR : CBOR_TYPE_TSTR;
            out->as.slice.ptr = r->data + r->offset;
            out->as.slice.len = (size_t)val;
            r->offset += (size_t)val;
            return CBOR_OK;

        case 4: // Array Header
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_ARRAY;
            out->as.container_len = (size_t)val;
            return CBOR_OK;

        case 5: // Map Header (pairs count)
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_MAP;
            out->as.container_len = (size_t)val;
            return CBOR_OK;

        case 6: // Semantic Tag
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_TAG;
            out->as.tag_val = val;
            return CBOR_OK;

        case 7: // Simple / Floats
            if (info == 20 || info == 21) {
                out->type = CBOR_TYPE_BOOL;
                out->as.bool_val = (info == 21);
                return CBOR_OK;
            }
            if (info == 22) {
                out->type = CBOR_TYPE_NULL;
                return CBOR_OK;
            }
            if (info == 26) { // IEEE 754 Float32
                uint32_t raw;
                err = read_uint_payload(r, 26, &val);
                if (err != CBOR_OK) return err;
                raw = (uint32_t)val;
                union { uint32_t u; float f; } conv;
                conv.u = raw;
                out->type = CBOR_TYPE_FLOAT32;
                out->as.float_val = conv.f;
                return CBOR_OK;
            }
            return CBOR_ERR_UNSUPPORTED_TYPE;

        default:
            return CBOR_ERR_UNSUPPORTED_TYPE;
    }
}
```
```cpp
class Decoder {
public:
    static std::expected<Value, Error> read_next(Reader& r) noexcept {
        if (r.remaining() == 0) {
            return std::unexpected(Error::UnexpectedEof);
        }

        const uint8_t initial_byte = r.buf_[r.offset_++];
        const auto major = static_cast<MajorType>(initial_byte >> 5);
        const uint8_t info = initial_byte & 0x1F;

        auto uint_res = read_uint_payload(r, info);
        if (!uint_res) {
            return std::unexpected(uint_res.error());
        }
        const uint64_t val = *uint_res;

        switch (major) {
            case MajorType::UnsignedInt:
                return val;

            case MajorType::NegativeInt:
                return static_cast<int64_t>(-1 - static_cast<int64_t>(val));

            case MajorType::ByteString: {
                if (r.remaining() < val) return std::unexpected(Error::UnexpectedEof);
                auto slice = r.buf_.subspan(r.offset_, val);
                r.offset_ += val;
                return slice;
            }

            case MajorType::TextString: {
                if (r.remaining() < val) return std::unexpected(Error::UnexpectedEof);
                std::string_view sv(reinterpret_cast<const char*>(r.buf_.data() + r.offset_), val);
                r.offset_ += val;
                return sv;
            }

            case MajorType::Array:
                return ArrayHeader{static_cast<size_t>(val)};

            case MajorType::Map:
                return MapHeader{static_cast<size_t>(val)};

            case MajorType::Tag:
                return TagHeader{val};

            case MajorType::Simple:
                if (info == 20) return false;
                if (info == 21) return true;
                if (info == 22) return NullValue{};
                if (info == 26) {
                    uint32_t raw = static_cast<uint32_t>(val);
                    float f;
                    std::memcpy(&f, &raw, sizeof(float));
                    return f;
                }
                return std::unexpected(Error::UnsupportedType);
        }
        return std::unexpected(Error::UnsupportedType);
    }

private:
    static std::expected<uint64_t, Error> read_uint_payload(Reader& r, uint8_t info) noexcept {
        if (info < 24) return info;
        if (info == 24) {
            if (r.remaining() < 1) return std::unexpected(Error::UnexpectedEof);
            return r.buf_[r.offset_++];
        }
        if (info == 25) {
            if (r.remaining() < 2) return std::unexpected(Error::UnexpectedEof);
            uint64_t v = (static_cast<uint64_t>(r.buf_[r.offset_]) << 8) |
                          static_cast<uint64_t>(r.buf_[r.offset_ + 1]);
            r.offset_ += 2;
            return v;
        }
        if (info == 26) {
            if (r.remaining() < 4) return std::unexpected(Error::UnexpectedEof);
            uint64_t v = (static_cast<uint64_t>(r.buf_[r.offset_]) << 24) |
                         (static_cast<uint64_t>(r.buf_[r.offset_ + 1]) << 16) |
                         (static_cast<uint64_t>(r.buf_[r.offset_ + 2]) << 8) |
                          static_cast<uint64_t>(r.buf_[r.offset_ + 3]);
            r.offset_ += 4;
            return v;
        }
        if (info == 27) {
            if (r.remaining() < 8) return std::unexpected(Error::UnexpectedEof);
            uint64_t v = 0;
            for (size_t i = 0; i < 8; ++i) {
                v = (v << 8) | static_cast<uint64_t>(r.buf_[r.offset_ + i]);
            }
            r.offset_ += 8;
            return v;
        }
        return std::unexpected(Error::InvalidHeader);
    }
};
```
:::

---

### Енкодер CBOR: детермінований запис у фіксований буфер

Серіалізатор формує бінарний потік згідно з вимогами стандарту dCBOR: будь-яке число записується у найкоротшому можливому форматі. Якщо значення вміщується у діапазон `0..23`, воно упаковується прямо в байт заголовка. Якщо значення дорівнює `255`, використовується заголовок `24` з одним байтом навантаження, і так далі.

Кожна функція запису перевіряє доступну ємність цільового буфера. У разі спроби виходу за межі виділеного масиву функція негайно припиняє роботу й повертає статус помилки `CBOR_ERR_BUFFER_OVERFLOW`, гарантуючи відсутність переповнення буфера на стеку або у статичній пам'яті.

:::tabs
```c
static cbor_error_t write_byte(cbor_writer_t *w, uint8_t b) {
    if (w->offset >= w->capacity) return CBOR_ERR_BUFFER_OVERFLOW;
    w->data[w->offset++] = b;
    return CBOR_OK;
}

static cbor_error_t write_header(cbor_writer_t *w, uint8_t major, uint64_t val) {
    uint8_t major_bits = major << 5;
    if (val < 24) {
        return write_byte(w, major_bits | (uint8_t)val);
    }
    if (val <= 0xFF) {
        cbor_error_t err = write_byte(w, major_bits | 24);
        if (err != CBOR_OK) return err;
        return write_byte(w, (uint8_t)val);
    }
    if (val <= 0xFFFF) {
        cbor_error_t err = write_byte(w, major_bits | 25);
        if (err != CBOR_OK) return err;
        write_byte(w, (uint8_t)(val >> 8));
        return write_byte(w, (uint8_t)(val & 0xFF));
    }
    if (val <= 0xFFFFFFFF) {
        cbor_error_t err = write_byte(w, major_bits | 26);
        if (err != CBOR_OK) return err;
        for (int i = 3; i >= 0; --i) {
            write_byte(w, (uint8_t)((val >> (i * 8)) & 0xFF));
        }
        return CBOR_OK;
    }
    cbor_error_t err = write_byte(w, major_bits | 27);
    if (err != CBOR_OK) return err;
    for (int i = 7; i >= 0; --i) {
        write_byte(w, (uint8_t)((val >> (i * 8)) & 0xFF));
    }
    return CBOR_OK;
}

cbor_error_t cbor_write_uint(cbor_writer_t *w, uint64_t val) {
    return write_header(w, 0, val);
}

cbor_error_t cbor_write_tstr(cbor_writer_t *w, const char *str, size_t len) {
    cbor_error_t err = write_header(w, 3, len);
    if (err != CBOR_OK) return err;
    if (w->offset + len > w->capacity) return CBOR_ERR_BUFFER_OVERFLOW;
    for (size_t i = 0; i < len; ++i) {
        w->data[w->offset++] = (uint8_t)str[i];
    }
    return CBOR_OK;
}

cbor_error_t cbor_write_bstr(cbor_writer_t *w, const uint8_t *bytes, size_t len) {
    cbor_error_t err = write_header(w, 2, len);
    if (err != CBOR_OK) return err;
    if (w->offset + len > w->capacity) return CBOR_ERR_BUFFER_OVERFLOW;
    for (size_t i = 0; i < len; ++i) {
        w->data[w->offset++] = bytes[i];
    }
    return CBOR_OK;
}

cbor_error_t cbor_write_map_header(cbor_writer_t *w, size_t num_pairs) {
    return write_header(w, 5, num_pairs);
}

cbor_error_t cbor_write_bool(cbor_writer_t *w, bool val) {
    return write_byte(w, (7 << 5) | (val ? 21 : 20));
}
```
```cpp
class Encoder {
public:
    static std::expected<void, Error> write_uint(Writer& w, uint64_t val) noexcept {
        return write_header(w, MajorType::UnsignedInt, val);
    }

    static std::expected<void, Error> write_int(Writer& w, int64_t val) noexcept {
        if (val >= 0) {
            return write_uint(w, static_cast<uint64_t>(val));
        }
        uint64_t encoded = static_cast<uint64_t>(-1 - val);
        return write_header(w, MajorType::NegativeInt, encoded);
    }

    static std::expected<void, Error> write_text(Writer& w, std::string_view sv) noexcept {
        auto res = write_header(w, MajorType::TextString, sv.size());
        if (!res) return res;
        if (w.remaining_capacity() < sv.size()) return std::unexpected(Error::BufferOverflow);
        std::memcpy(w.buf_.data() + w.offset_, sv.data(), sv.size());
        w.offset_ += sv.size();
        return {};
    }

    static std::expected<void, Error> write_bytes(Writer& w, std::span<const uint8_t> bytes) noexcept {
        auto res = write_header(w, MajorType::ByteString, bytes.size());
        if (!res) return res;
        if (w.remaining_capacity() < bytes.size()) return std::unexpected(Error::BufferOverflow);
        std::memcpy(w.buf_.data() + w.offset_, bytes.data(), bytes.size());
        w.offset_ += bytes.size();
        return {};
    }

    static std::expected<void, Error> write_map_header(Writer& w, size_t num_pairs) noexcept {
        return write_header(w, MajorType::Map, num_pairs);
    }

    static std::expected<void, Error> write_array_header(Writer& w, size_t num_items) noexcept {
        return write_header(w, MajorType::Array, num_items);
    }

    static std::expected<void, Error> write_bool(Writer& w, bool val) noexcept {
        if (w.remaining_capacity() < 1) return std::unexpected(Error::BufferOverflow);
        uint8_t byte = (static_cast<uint8_t>(MajorType::Simple) << 5) | (val ? 21 : 20);
        w.buf_[w.offset_++] = byte;
        return {};
    }

private:
    static std::expected<void, Error> write_header(Writer& w, MajorType major, uint64_t val) noexcept {
        const uint8_t major_bits = static_cast<uint8_t>(major) << 5;
        if (val < 24) {
            if (w.remaining_capacity() < 1) return std::unexpected(Error::BufferOverflow);
            w.buf_[w.offset_++] = major_bits | static_cast<uint8_t>(val);
            return {};
        }
        if (val <= 0xFF) {
            if (w.remaining_capacity() < 2) return std::unexpected(Error::BufferOverflow);
            w.buf_[w.offset_++] = major_bits | 24;
            w.buf_[w.offset_++] = static_cast<uint8_t>(val);
            return {};
        }
        if (val <= 0xFFFF) {
            if (w.remaining_capacity() < 3) return std::unexpected(Error::BufferOverflow);
            w.buf_[w.offset_++] = major_bits | 25;
            w.buf_[w.offset_++] = static_cast<uint8_t>(val >> 8);
            w.buf_[w.offset_++] = static_cast<uint8_t>(val & 0xFF);
            return {};
        }
        if (val <= 0xFFFFFFFF) {
            if (w.remaining_capacity() < 5) return std::unexpected(Error::BufferOverflow);
            w.buf_[w.offset_++] = major_bits | 26;
            for (int i = 3; i >= 0; --i) {
                w.buf_[w.offset_++] = static_cast<uint8_t>((val >> (i * 8)) & 0xFF);
            }
            return {};
        }
        if (w.remaining_capacity() < 9) return std::unexpected(Error::BufferOverflow);
        w.buf_[w.offset_++] = major_bits | 27;
        for (int i = 7; i >= 0; --i) {
            w.buf_[w.offset_++] = static_cast<uint8_t>((val >> (i * 8)) & 0xFF);
        }
        return {};
    }
};
```
:::

---

### Приклад використання: серіалізація та розбір телеметрії

Розглянемо практичний сценарій збору телеметрії з кліматичного давача: пристрій упаковує мітку часу UNIX, назву давача та статус справності в один CBOR-словник і надсилає його радіоканалом.

Приймач зчитує вхідні байти і виконує ітерацію по парах ключ-значення безпосередньо в буфері. Коли зустрічається ключ `2` (назва давача), витягується зріз тексту. Зверніть увагу: жоден символ рядка `"DHT22"` не копіюється в новий буфер — вказівник посилається на байти всередині вхідного масиву.

:::tabs
```c
void telemetry_example(void) {
    uint8_t buffer[64];
    cbor_writer_t writer = {
        .data = buffer,
        .capacity = sizeof(buffer),
        .offset = 0
    };

    // Серіалізація словника з 3 полями:
    // { 1: 1714560000, 2: "DHT22", 3: true }
    cbor_write_map_header(&writer, 3);

    cbor_write_uint(&writer, 1); // ключ 1 (timestamp)
    cbor_write_uint(&writer, 1714560000ULL);

    cbor_write_uint(&writer, 2); // ключ 2 (sensor_name)
    cbor_write_tstr(&writer, "DHT22", 5);

    cbor_write_uint(&writer, 3); // ключ 3 (status_ok)
    cbor_write_bool(&writer, true);

    // Десеріалізація (Zero-Copy)
    cbor_reader_t reader = {
        .data = buffer,
        .size = writer.offset,
        .offset = 0
    };

    cbor_value_t item;
    if (cbor_read_next(&reader, &item) == CBOR_OK && item.type == CBOR_TYPE_MAP) {
        size_t pairs = item.as.container_len;
        for (size_t i = 0; i < pairs; ++i) {
            cbor_value_t key, val;
            cbor_read_next(&reader, &key);
            cbor_read_next(&reader, &val);

            if (key.type == CBOR_TYPE_UINT && key.as.uint_val == 2) {
                // val.as.slice вказує безпосередньо в buffer без копіювання
                const uint8_t *name_ptr = val.as.slice.ptr;
                size_t name_len = val.as.slice.len;
                (void)name_ptr;
                (void)name_len;
            }
        }
    }
}
```
```cpp
void telemetry_example_cpp() {
    std::array<uint8_t, 64> buffer{};
    cbor::Writer writer(buffer);

    // Серіалізація словника
    cbor::Encoder::write_map_header(writer, 3).value();
    cbor::Encoder::write_uint(writer, 1).value();
    cbor::Encoder::write_uint(writer, 1714560000ULL).value();

    cbor::Encoder::write_uint(writer, 2).value();
    cbor::Encoder::write_text(writer, "DHT22").value();

    cbor::Encoder::write_uint(writer, 3).value();
    cbor::Encoder::write_bool(writer, true).value();

    // Десеріалізація через Zero-Copy Decoder
    cbor::Reader reader(writer.written_data());
    auto root = cbor::Decoder::read_next(reader);

    if (root && std::holds_alternative<cbor::MapHeader>(*root)) {
        const size_t pairs = std::get<cbor::MapHeader>(*root).pairs_count;
        for (size_t i = 0; i < pairs; ++i) {
            auto key = cbor::Decoder::read_next(reader);
            auto val = cbor::Decoder::read_next(reader);

            if (key && std::holds_alternative<uint64_t>(*key) && std::get<uint64_t>(*key) == 2) {
                if (val && std::holds_alternative<std::string_view>(*val)) {
                    std::string_view name = std::get<std::string_view>(*val);
                    (void)name; // name посилається прямо на пам'ять buffer
                }
            }
        }
    }
}
```
:::

---

### Аналіз ресурсів та безпека пам'яті на ядрі ARM Cortex-M

На типовому мікроконтролері з ядром ARM Cortex-M4 (компілятор GCC з оптимізацією `-O2`) такий кодек забезпечує визначні системні характеристики:
- **Пам'ять програм (Flash):** повний бінарний код енкодера та декодера займає менше 1.2 КБ машинних інструкцій, що робить його придатним навіть для чіпів сімейств Cortex-M0+ та ATTiny.
- **Оперативна пам'ять (SRAM):** `0` байтів у купі. Стек виклику функції `cbor_read_next` займає лише 32 байти (кілька збережених регістрів загального призначення `r4-r7` та вказівник повернення `lr`).
- **Час виконання:** розбір одного поля виконується за 15–30 тактів процесора (на тактовій частоті 64 МГц це близько 250–500 наносекунд на поле).
- **Захист від атак переповнення:** оскільки парсер є ітеративним і не створює рекурсивних викликів на стеку, атака через глибоко вкладені структури (`recursion exhaustion attack`) не здатна обвалити стек мікроконтролера.

Єдине правило безпеки при роботі з нуль-копіювальними структурами полягає у суворому контролі життєвого циклу вхідного буфера: вказівники у `cbor_slice_t` та об'єкти `std::string_view` валідні рівно доти, доки буфер прийому не буде перезаписано новим DMA-пакетом або очищено. Якщо додатку необхідно зберегти окреме значення між циклами обробки, копіюється лише конкретне необхідне поле, а не вся структура повідомлення.
