#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Типізована структура даних
typedef struct {
    uint32_t timestamp_s;
    uint32_t sensor_id;
    int32_t  temperature_c100;
    uint32_t battery_mv;
} TelemetryReading;

// Запис Varint у буфер
static size_t write_varint(uint8_t *buf, size_t max_len, uint64_t val) {
    size_t written = 0;
    while (val >= 0x80) {
        if (written >= max_len) return 0;
        buf[written++] = (uint8_t)((val & 0x7F) | 0x80);
        val >>= 7;
    }
    if (written >= max_len) return 0;
    buf[written++] = (uint8_t)(val & 0x7F);
    return written;
}

// Запис ключа (номер поля + wire type)
static size_t write_tag(uint8_t *buf, size_t max_len, uint32_t field_num, uint8_t wire_type) {
    return write_varint(buf, max_len, ((uint64_t)field_num << 3) | (wire_type & 0x07));
}

// ZigZag кодування для sint32
static inline uint32_t encode_zigzag32(int32_t n) {
    return (uint32_t)((n << 1) ^ (n >> 31));
}

static inline int32_t decode_zigzag32(uint32_t z) {
    return (int32_t)((z >> 1) ^ -(int32_t)(z & 1));
}

// Серіалізація повідомлення
size_t encode_telemetry(const TelemetryReading *msg, uint8_t *out_buf, size_t max_len) {
    size_t offset = 0;
    size_t step = 0;

    if (msg->timestamp_s != 0) {
        step = write_tag(out_buf + offset, max_len - offset, 1, 0);
        if (!step) return 0; offset += step;
        step = write_varint(out_buf + offset, max_len - offset, msg->timestamp_s);
        if (!step) return 0; offset += step;
    }
    if (msg->sensor_id != 0) {
        step = write_tag(out_buf + offset, max_len - offset, 2, 0);
        if (!step) return 0; offset += step;
        step = write_varint(out_buf + offset, max_len - offset, msg->sensor_id);
        if (!step) return 0; offset += step;
    }
    if (msg->temperature_c100 != 0) {
        step = write_tag(out_buf + offset, max_len - offset, 3, 0);
        if (!step) return 0; offset += step;
        step = write_varint(out_buf + offset, max_len - offset, encode_zigzag32(msg->temperature_c100));
        if (!step) return 0; offset += step;
    }
    if (msg->battery_mv != 0) {
        step = write_tag(out_buf + offset, max_len - offset, 4, 0);
        if (!step) return 0; offset += step;
        step = write_varint(out_buf + offset, max_len - offset, msg->battery_mv);
        if (!step) return 0; offset += step;
    }
    return offset;
}

// Десеріалізація з перевіркою коректності
bool decode_telemetry(const uint8_t *in_buf, size_t len, TelemetryReading *msg) {
    memset(msg, 0, sizeof(TelemetryReading));
    size_t cursor = 0;

    while (cursor < len) {
        // Читання ключа
        uint64_t key = 0;
        int bitpos = 0;
        while (bitpos < 64) {
            if (cursor >= len) return false;
            uint8_t b = in_buf[cursor++];
            key |= (uint64_t)(b & 0x7F) << bitpos;
            if ((b & 0x80) == 0) break;
            bitpos += 7;
        }

        uint32_t tag = (uint32_t)(key >> 3);
        uint8_t wire_type = (uint8_t)(key & 0x07);

        if (wire_type == 0) { // Varint
            uint64_t val = 0;
            bitpos = 0;
            while (bitpos < 64) {
                if (cursor >= len) return false;
                uint8_t b = in_buf[cursor++];
                val |= (uint64_t)(b & 0x7F) << bitpos;
                if ((b & 0x80) == 0) break;
                bitpos += 7;
            }
            switch (tag) {
                case 1: msg->timestamp_s = (uint32_t)val; break;
                case 2: msg->sensor_id = (uint32_t)val; break;
                case 3: msg->temperature_c100 = decode_zigzag32((uint32_t)val); break;
                case 4: msg->battery_mv = (uint32_t)val; break;
                default: break; // Безпечний пропуск невідомого поля
            }
        } else if (wire_type == 1) { // 64-bit
            if (cursor + 8 > len) return false;
            cursor += 8;
        } else if (wire_type == 2) { // Length-delimited
            uint64_t l = 0;
            bitpos = 0;
            while (bitpos < 64) {
                if (cursor >= len) return false;
                uint8_t b = in_buf[cursor++];
                l |= (uint64_t)(b & 0x7F) << bitpos;
                if ((b & 0x80) == 0) break;
                bitpos += 7;
            }
            if (cursor + l > len) return false;
            cursor += (size_t)l;
        } else if (wire_type == 5) { // 32-bit
            if (cursor + 4 > len) return false;
            cursor += 4;
        } else {
            return false; // Неприпустимий wire type
        }
    }
    return true;
}
