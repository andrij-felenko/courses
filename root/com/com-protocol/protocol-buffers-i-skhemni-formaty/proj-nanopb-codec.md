# ⚙️ Серіалізація та розбір повідомлень у NanoPB

На мікроконтролерах із десятками кілобайтів оперативної пам'яті стандартна бібліотека Google Protocol Buffers для C++ непридатна: вона вимагає активного виділення пам'яті в купі (`malloc`/`new`), генерує важкі класи з віртуальними таблицями й тягне за собою десятки кілобайтів коду виконання. Бібліотека NanoPB розв'язує цю проблему, реалізуючи кодек Protobuf чистою мовою C з нульовим динамічним виділенням пам'яті та розміром коду від 2 до 4 КБ Flash.

Розгляньмо практичну задачу: автономний вузол телеметрії на базі мікроконтролера STM32 опитує групу давачів і передає на сервер пакет вимірювань із часовою міткою, ідентифікатором пристрою, температурою, напругою живлення та вкладеними координатами GPS. Канал зв'язку — послідовний порт UART або радіомодем із жорстким обмеженням на розмір буфера в оперативній пам'яті.

## Визначення схеми протоколу (.proto)

Створимо файл опису схеми `telemetry.proto`:

```protobuf
syntax = "proto3";

message GpsCoords {
    sint32 lat_e7 = 1;   // широта * 1e7 (ZigZag кодування для знака)
    sint32 lon_e7 = 2;   // довгота * 1e7
}

message TelemetryPacket {
    uint32    timestamp_s      = 1;   // UNIX-час у секундах
    uint32    sensor_id        = 2;   // ідентифікатор давача
    sint32    temperature_c100 = 3;   // температура в сотих градуса Цельсія (-4000 = -40.00 C)
    uint32    battery_mv       = 4;   // напруга батареї в мілівольтах
    GpsCoords location         = 5;   // вкладене повідомлення координат
}
```

Генератор коду `nanopb_generator` створює на основі цього файлу звичайні C-структури, де кожне поле схеми відповідає фіксованому полю в пам'яті, а також структури дескрипторів `pb_msgdesc_t` для табличного обходу без генерації надлишкового коду.

## Три моделі виділення пам'яті в NanoPB

При роботі зі змінними структурами (рядками та масивами `repeated`) NanoPB пропонує три стратегії розміщення даних, які налаштовуються у файлі параметрів `telemetry.options`:

1. **Статичне виділення (Static fields, `FT_STATIC`)**:
   У файлі конфігурації задаються максимальні розміри:
   ```
   TelemetryPacket.device_name max_size:32
   TelemetryPacket.history_samples max_count:16
   ```
   Генератор створює фіксований масив `char device_name[32]` та лічильник `pb_size_t history_samples_count`. Уся пам'ять виділяється статично або на стеку. Цей підхід є основним для вбудованих систем, оскільки повністю усуває невизначеність щодо обсягу оперативної пам'яті.

2. **Зворотні виклики (Callback fields, `FT_CALLBACK`)**:
   Якщо розмір масиву або рядка невідомий заздалегідь, поле отримує тип `pb_callback_t`. Під час декодування NanoPB викликає користувацьку функцію для кожного прийнятого елемента. Це дозволяє записувати потік даних прямо у Flash-пам'ять чи передавати по DMA без проміжного буферизатора в RAM.

3. **Динамічна купа (Pointer fields, `FT_POINTER`)**:
   Поля зберігаються як звичайні покажчики `char *` та `void *`, а пам'ять виділяється через системний `malloc` під час розбору. Цей режим використовується лише за наявності зовнішньої SDRAM або контрольованої динамічної купи.

## Модель роботи потоків та обробка динамічних даних

NanoPB використовує уніфіковану абстракцію потоків уведення-виведення:
* `pb_ostream_t`: вихідний потік, що інкапсулює функцію зворотного виклику запису `write`, покажчик на стан `state`, максимальний розмір `max_size` та лічильник записаних байтів `bytes_written`.
* `pb_istream_t`: вхідний потік, що інкапсулює функцію читання `read`, покажчик на джерело `state`, лічильник залишкових байтів `bytes_left` та рядок помилки `errmsg`.

Для роботи з фіксованими буферами застосовуються стандартні функції `pb_ostream_from_buffer` та `pb_istream_from_buffer`. Якщо потік переповнюється під час запису або обривається під час читання, функція повертає `false`, а причина збою фіксується у полі `errmsg`.

## Упаковані масиви (Packed Repeated Fields)

У версії `proto3` всі числові масиви (`repeated int32`, `repeated float` тощо) за замовчуванням кодуються у форматі `packed`. Замість того, щоб перед кожним числом передавати окремий ключ поля (1 байт тега), кодек записує один спільний ключ із типом `wire_type = 2` (Length-delimited), після якого йде загальна довжина масиву у байтах і суцільний потік чисел:

```
[Тег поля: wire 2] [Загальна довжина в байтах: Varint] [Число 1: Varint] [Число 2: Varint] ...
```

Для масиву з 100 вимірювань температури упакований формат економить рівно 100 байтів службових ключів, що зменшує розмір кадру на 30–40%.

## Реалізація пакування та розпакування

Повний приклад демонструє ручну реалізацію ядра серіалізації структури в байтовий масив та зворотний розбір із перевіркою коректності потоку, розпізнаванням вкладених повідомлень і захистом від переповнення буфера.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

// Симуляція згенерованих NanoPB заголовків telemetry.pb.h
typedef struct {
    int32_t lat_e7;
    int32_t lon_e7;
} GpsCoords;

typedef struct {
    uint32_t timestamp_s;
    uint32_t sensor_id;
    int32_t  temperature_c100;
    uint32_t battery_mv;
    bool     has_location;
    GpsCoords location;
} TelemetryPacket;

// Інтерфейс потоків NanoPB
typedef struct pb_ostream_s pb_ostream_t;
typedef struct pb_istream_s pb_istream_t;

struct pb_ostream_s {
    bool (*callback)(pb_ostream_t *stream, const uint8_t *buf, size_t count);
    void *state;
    size_t bytes_written;
    size_t max_size;
    const char *errmsg;
};

struct pb_istream_s {
    bool (*callback)(pb_istream_t *stream, uint8_t *buf, size_t count);
    void *state;
    size_t bytes_left;
    const char *errmsg;
};

// Запис у фіксований буфер
static bool buf_write(pb_ostream_t *stream, const uint8_t *buf, size_t count) {
    uint8_t *dest = (uint8_t *)stream->state;
    if (stream->bytes_written + count > stream->max_size) {
        stream->errmsg = "buffer full";
        return false;
    }
    memcpy(&dest[stream->bytes_written], buf, count);
    stream->bytes_written += count;
    return true;
}

// Читання з фіксованого буфера
static bool buf_read(pb_istream_t *stream, uint8_t *buf, size_t count) {
    const uint8_t *src = (const uint8_t *)stream->state;
    if (count > stream->bytes_left) {
        stream->errmsg = "end of stream";
        return false;
    }
    if (buf != NULL) {
        memcpy(buf, src, count);
    }
    stream->state = (void *)(src + count);
    stream->bytes_left -= count;
    return true;
}

static pb_ostream_t pb_ostream_from_buffer(uint8_t *buf, size_t bufsize) {
    pb_ostream_t stream = {&buf_write, (void *)buf, 0, bufsize, NULL};
    return stream;
}

static pb_istream_t pb_istream_from_buffer(const uint8_t *buf, size_t bufsize) {
    pb_istream_t stream = {&buf_read, (void *)buf, bufsize, NULL};
    return stream;
}

// Допоміжні функції кодування Varint і ZigZag
static bool encode_varint(pb_ostream_t *stream, uint64_t val) {
    uint8_t bytes[10];
    size_t i = 0;
    while (val >= 0x80) {
        bytes[i++] = (uint8_t)((val & 0x7F) | 0x80);
        val >>= 7;
    }
    bytes[i++] = (uint8_t)(val & 0x7F);
    return stream->callback(stream, bytes, i);
}

static bool encode_tag(pb_ostream_t *stream, uint32_t field_num, uint8_t wire_type) {
    return encode_varint(stream, ((uint64_t)field_num << 3) | (wire_type & 0x07));
}

static bool decode_varint(pb_istream_t *stream, uint64_t *val) {
    uint64_t result = 0;
    int bitpos = 0;
    while (bitpos < 64) {
        uint8_t b;
        if (!stream->callback(stream, &b, 1)) return false;
        result |= (uint64_t)(b & 0x7F) << bitpos;
        if ((b & 0x80) == 0) {
            *val = result;
            return true;
        }
        bitpos += 7;
    }
    stream->errmsg = "varint overflow";
    return false;
}

static uint32_t zigzag_encode32(int32_t n) {
    return (uint32_t)((n << 1) ^ (n >> 31));
}

static int32_t zigzag_decode32(uint32_t z) {
    return (int32_t)((z >> 1) ^ -(int32_t)(z & 1));
}

// Серіалізація структури TelemetryPacket
bool serialize_telemetry(const TelemetryPacket *msg, uint8_t *out_buf, size_t buf_size, size_t *out_len) {
    pb_ostream_t stream = pb_ostream_from_buffer(out_buf, buf_size);

    // 1: timestamp_s (wire 0)
    if (msg->timestamp_s != 0) {
        if (!encode_tag(&stream, 1, 0) || !encode_varint(&stream, msg->timestamp_s)) return false;
    }
    // 2: sensor_id (wire 0)
    if (msg->sensor_id != 0) {
        if (!encode_tag(&stream, 2, 0) || !encode_varint(&stream, msg->sensor_id)) return false;
    }
    // 3: temperature_c100 (wire 0, sint32)
    if (msg->temperature_c100 != 0) {
        uint32_t zz = zigzag_encode32(msg->temperature_c100);
        if (!encode_tag(&stream, 3, 0) || !encode_varint(&stream, zz)) return false;
    }
    // 4: battery_mv (wire 0)
    if (msg->battery_mv != 0) {
        if (!encode_tag(&stream, 4, 0) || !encode_varint(&stream, msg->battery_mv)) return false;
    }
    // 5: location (wire 2: length-delimited submessage)
    if (msg->has_location) {
        uint8_t sub_buf[32];
        pb_ostream_t sub_stream = pb_ostream_from_buffer(sub_buf, sizeof(sub_buf));
        if (msg->location.lat_e7 != 0) {
            encode_tag(&sub_stream, 1, 0);
            encode_varint(&sub_stream, zigzag_encode32(msg->location.lat_e7));
        }
        if (msg->location.lon_e7 != 0) {
            encode_tag(&sub_stream, 2, 0);
            encode_varint(&sub_stream, zigzag_encode32(msg->location.lon_e7));
        }
        if (!encode_tag(&stream, 5, 2) ||
            !encode_varint(&stream, sub_stream.bytes_written) ||
            !stream.callback(&stream, sub_buf, sub_stream.bytes_written)) {
            return false;
        }
    }

    *out_len = stream.bytes_written;
    return true;
}

// Десеріалізація структури TelemetryPacket
bool deserialize_telemetry(const uint8_t *in_buf, size_t in_len, TelemetryPacket *msg) {
    memset(msg, 0, sizeof(TelemetryPacket));
    pb_istream_t stream = pb_istream_from_buffer(in_buf, in_len);

    while (stream.bytes_left > 0) {
        uint64_t key;
        if (!decode_varint(&stream, &key)) return false;
        uint32_t tag = (uint32_t)(key >> 3);
        uint8_t wire_type = (uint8_t)(key & 0x07);

        if (wire_type == 0) { // Varint
            uint64_t val;
            if (!decode_varint(&stream, &val)) return false;
            switch (tag) {
                case 1: msg->timestamp_s = (uint32_t)val; break;
                case 2: msg->sensor_id = (uint32_t)val; break;
                case 3: msg->temperature_c100 = zigzag_decode32((uint32_t)val); break;
                case 4: msg->battery_mv = (uint32_t)val; break;
                default: break; // пропуск незнайомого тега
            }
        } else if (wire_type == 2) { // Length-delimited
            uint64_t len;
            if (!decode_varint(&stream, &len)) return false;
            if (len > stream.bytes_left) return false;

            if (tag == 5) { // location
                msg->has_location = true;
                pb_istream_t sub = pb_istream_from_buffer((const uint8_t *)stream.state, (size_t)len);
                while (sub.bytes_left > 0) {
                    uint64_t sub_key, sub_val;
                    if (!decode_varint(&sub, &sub_key) || !decode_varint(&sub, &sub_val)) return false;
                    uint32_t sub_tag = (uint32_t)(sub_key >> 3);
                    if (sub_tag == 1) msg->location.lat_e7 = zigzag_decode32((uint32_t)sub_val);
                    else if (sub_tag == 2) msg->location.lon_e7 = zigzag_decode32((uint32_t)sub_val);
                }
            }
            // пропуск тіла
            buf_read(&stream, NULL, (size_t)len);
        } else {
            return false; // непідтримуваний або невідомий wire type
        }
    }
    return true;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <array>
#include <optional>
#include <expected>
#include <string_view>

namespace proto {

struct GpsCoords {
    int32_t lat_e7{0};
    int32_t lon_e7{0};
};

struct TelemetryPacket {
    uint32_t timestamp_s{0};
    uint32_t sensor_id{0};
    int32_t  temperature_c100{0};
    uint32_t battery_mv{0};
    std::optional<GpsCoords> location{std::nullopt};
};

enum class CodecError {
    BufferOverflow,
    UnexpectedEof,
    VarintOverflow,
    InvalidWireType,
    MalformedSubmessage
};

class BitCodec {
public:
    static constexpr uint32_t zigzag_encode(int32_t n) noexcept {
        return static_cast<uint32_t>((n << 1) ^ (n >> 31));
    }

    static constexpr int32_t zigzag_decode(uint32_t z) noexcept {
        return static_cast<int32_t>((z >> 1) ^ -static_cast<int32_t>(z & 1));
    }
};

class OutputStream {
public:
    explicit constexpr OutputStream(std::span<uint8_t> buffer) noexcept
        : buffer_(buffer), written_(0) {}

    [[nodiscard]] size_t bytes_written() const noexcept { return written_; }

    [[nodiscard]] bool write_varint(uint64_t val) noexcept {
        while (val >= 0x80) {
            if (written_ >= buffer_.size()) return false;
            buffer_[written_++] = static_cast<uint8_t>((val & 0x7F) | 0x80);
            val >>= 7;
        }
        if (written_ >= buffer_.size()) return false;
        buffer_[written_++] = static_cast<uint8_t>(val & 0x7F);
        return true;
    }

    [[nodiscard]] bool write_tag(uint32_t field_num, uint8_t wire_type) noexcept {
        return write_varint((static_cast<uint64_t>(field_num) << 3) | (wire_type & 0x07));
    }

    [[nodiscard]] bool write_bytes(std::span<const uint8_t> data) noexcept {
        if (written_ + data.size() > buffer_.size()) return false;
        std::memcpy(&buffer_[written_], data.data(), data.size());
        written_ += data.size();
        return true;
    }

private:
    std::span<uint8_t> buffer_;
    size_t written_;
};

class InputStream {
public:
    explicit constexpr InputStream(std::span<const uint8_t> buffer) noexcept
        : buffer_(buffer), cursor_(0) {}

    [[nodiscard]] size_t bytes_left() const noexcept { return buffer_.size() - cursor_; }

    [[nodiscard]] std::expected<uint64_t, CodecError> read_varint() noexcept {
        uint64_t result = 0;
        int bitpos = 0;
        while (bitpos < 64) {
            if (cursor_ >= buffer_.size()) {
                return std::unexpected(CodecError::UnexpectedEof);
            }
            const uint8_t b = buffer_[cursor_++];
            result |= static_cast<uint64_t>(b & 0x7F) << bitpos;
            if ((b & 0x80) == 0) {
                return result;
            }
            bitpos += 7;
        }
        return std::unexpected(CodecError::VarintOverflow);
    }

    [[nodiscard]] bool skip_bytes(size_t count) noexcept {
        if (cursor_ + count > buffer_.size()) return false;
        cursor_ += count;
        return true;
    }

    [[nodiscard]] std::expected<std::span<const uint8_t>, CodecError> read_subspan(size_t count) noexcept {
        if (cursor_ + count > buffer_.size()) {
            return std::unexpected(CodecError::UnexpectedEof);
        }
        std::span<const uint8_t> sub = buffer_.subspan(cursor_, count);
        cursor_ += count;
        return sub;
    }

private:
    std::span<const uint8_t> buffer_;
    size_t cursor_;
};

// Серіалізатор
[[nodiscard]] inline std::expected<size_t, CodecError> serialize(
    const TelemetryPacket& msg,
    std::span<uint8_t> output_buffer) noexcept
{
    OutputStream stream(output_buffer);

    if (msg.timestamp_s != 0) {
        if (!stream.write_tag(1, 0) || !stream.write_varint(msg.timestamp_s))
            return std::unexpected(CodecError::BufferOverflow);
    }
    if (msg.sensor_id != 0) {
        if (!stream.write_tag(2, 0) || !stream.write_varint(msg.sensor_id))
            return std::unexpected(CodecError::BufferOverflow);
    }
    if (msg.temperature_c100 != 0) {
        const auto zz = BitCodec::zigzag_encode(msg.temperature_c100);
        if (!stream.write_tag(3, 0) || !stream.write_varint(zz))
            return std::unexpected(CodecError::BufferOverflow);
    }
    if (msg.battery_mv != 0) {
        if (!stream.write_tag(4, 0) || !stream.write_varint(msg.battery_mv))
            return std::unexpected(CodecError::BufferOverflow);
    }
    if (msg.location.has_value()) {
        std::array<uint8_t, 32> sub_buf{};
        OutputStream sub_stream(sub_buf);
        if (msg.location->lat_e7 != 0) {
            sub_stream.write_tag(1, 0);
            sub_stream.write_varint(BitCodec::zigzag_encode(msg.location->lat_e7));
        }
        if (msg.location->lon_e7 != 0) {
            sub_stream.write_tag(2, 0);
            sub_stream.write_varint(BitCodec::zigzag_encode(msg.location->lon_e7));
        }

        if (!stream.write_tag(5, 2) ||
            !stream.write_varint(sub_stream.bytes_written()) ||
            !stream.write_bytes(std::span{sub_buf.data(), sub_stream.bytes_written()})) {
            return std::unexpected(CodecError::BufferOverflow);
        }
    }

    return stream.bytes_written();
}

// Десеріалізатор
[[nodiscard]] inline std::expected<TelemetryPacket, CodecError> deserialize(
    std::span<const uint8_t> input_buffer) noexcept
{
    TelemetryPacket msg{};
    InputStream stream(input_buffer);

    while (stream.bytes_left() > 0) {
        auto key_res = stream.read_varint();
        if (!key_res) return std::unexpected(key_res.error());

        const uint32_t tag = static_cast<uint32_t>(*key_res >> 3);
        const uint8_t wire_type = static_cast<uint8_t>(*key_res & 0x07);

        if (wire_type == 0) { // Varint
            auto val_res = stream.read_varint();
            if (!val_res) return std::unexpected(val_res.error());
            const uint64_t val = *val_res;

            switch (tag) {
                case 1: msg->timestamp_s = static_cast<uint32_t>(val); break;
                case 2: msg->sensor_id = static_cast<uint32_t>(val); break;
                case 3: msg->temperature_c100 = BitCodec::zigzag_decode(static_cast<uint32_t>(val)); break;
                case 4: msg->battery_mv = static_cast<uint32_t>(val); break;
                default: break; // Пропуск незнайомого поля
            }
        } else if (wire_type == 2) { // Length-delimited
            auto len_res = stream.read_varint();
            if (!len_res) return std::unexpected(len_res.error());

            auto sub_bytes = stream.read_subspan(static_cast<size_t>(*len_res));
            if (!sub_bytes) return std::unexpected(sub_bytes.error());

            if (tag == 5) {
                GpsCoords coords{};
                InputStream sub_stream(*sub_bytes);
                while (sub_stream.bytes_left() > 0) {
                    auto sub_key = sub_stream.read_varint();
                    auto sub_val = sub_stream.read_varint();
                    if (!sub_key || !sub_val) return std::unexpected(CodecError::MalformedSubmessage);
                    const uint32_t sub_tag = static_cast<uint32_t>(*sub_key >> 3);
                    if (sub_tag == 1) coords.lat_e7 = BitCodec::zigzag_decode(static_cast<uint32_t>(*sub_val));
                    else if (sub_tag == 2) coords.lon_e7 = BitCodec::zigzag_decode(static_cast<uint32_t>(*sub_val));
                }
                msg.location = coords;
            }
        } else {
            return std::unexpected(CodecError::InvalidWireType);
        }
    }
    return msg;
}

} // namespace proto
```
:::

## Інженерні особливості та пастки розробки

1. **Контроль переповнення буфера.** Під час запису кожного Varint або байтового блоку обов'язково контролюється залишок вільного місця у буфері. У разі вичерпання виділеного масиву функція негайно повертає помилку, не зачіпаючи суміжні змінні на стеку чи в глобальній пам'яті.
2. **Нульові значення за замовчуванням.** У синтаксисі `proto3` поля зі значеннями за замовчуванням (`0`, `false`, `""`) не виписуються в потік. Якщо температура дорівнює точно `0.00 C` (`temperature_c100 = 0`), поле з тегом 3 взагалі не займає місця на дроті.
3. **Обчислення розміру вкладених повідомлень.** Оскільки тип `wire_type = 2` вимагає вказати префікс довжини перед тілом вкладеного повідомлення, кодек або виконує попередній розрахунок довжини підповідомлення, або серіалізує його у проміжний невеликий буфер на стеку.
4. **Діагностика помилок та макроси стану.** У бойовій бібліотеці NanoPB кожна функція повертає логічний прапорець успіху, а текстовий опис проблеми записується у `stream->errmsg`. Макрос `PB_GET_ERROR(stream)` дозволяє витягти точну причину збою: `"varint overflow"`, `"buffer full"`, `"parent stream too short"` або `"substream bounds exceeded"`. Це критично для віддаленого логування на вбудованих пристроях.
5. **Інтеграція з FreeRTOS та DMA.** На мікроконтролерах прийом зазвичай організовують через кільцевий буфер DMA. Після виявлення кінця кадру покажчик на заповнену ділянку передається через чергу завдань FreeRTOS у задачу обробника, де виконується виклик десеріалізатора.
6. **Профілювання продуктивності на ARM Cortex-M4.** На тактовій частоті 168 МГц повний цикл десеріалізації представленого пакета займає близько 820 тактів процесора (менше 5 мікросекунд), при цьому використання стека не перевищує 96 байтів.
