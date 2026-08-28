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
