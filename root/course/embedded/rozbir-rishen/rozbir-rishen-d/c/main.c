#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Типобезпечний двійковий кодувальник CBOR у статичний буфер (C99)
typedef struct {
    uint8_t *buf;
    size_t cap;
    size_t pos;
    bool overflow;
} cbor_stream_t;

static void cbor_init(cbor_stream_t *s, uint8_t *buf, size_t cap) {
    s->buf = buf;
    s->cap = cap;
    s->pos = 0;
    s->overflow = false;
}

static void cbor_write_byte(cbor_stream_t *s, uint8_t val) {
    if (s->pos < s->cap) {
        s->buf[s->pos++] = val;
    } else {
        s->overflow = true;
    }
}

// Запис цілого беззнакового числа за стандартом RFC 8949 (major type 0)
static void cbor_write_uint(cbor_stream_t *s, uint8_t major, uint32_t val) {
    uint8_t type_hdr = (uint8_t)(major << 5);
    if (val < 24) {
        cbor_write_byte(s, (uint8_t)(type_hdr | val));
    } else if (val <= 0xFF) {
        cbor_write_byte(s, (uint8_t)(type_hdr | 24));
        cbor_write_byte(s, (uint8_t)val);
    } else if (val <= 0xFFFF) {
        cbor_write_byte(s, (uint8_t)(type_hdr | 25));
        cbor_write_byte(s, (uint8_t)(val >> 8));
        cbor_write_byte(s, (uint8_t)(val & 0xFF));
    } else {
        cbor_write_byte(s, (uint8_t)(type_hdr | 26));
        cbor_write_byte(s, (uint8_t)(val >> 24));
        cbor_write_byte(s, (uint8_t)((val >> 16) & 0xFF));
        cbor_write_byte(s, (uint8_t)((val >> 8) & 0xFF));
        cbor_write_byte(s, (uint8_t)(val & 0xFF));
    }
}

// Пакування кадру телеметрії згідно з ADR-0001 (фіксована мапа з 6 пар)
bool encode_telemetry_cbor(uint32_t node_id, uint32_t ts, bool fault, 
                           float temp, float hum, uint16_t vbat_mv,
                           uint8_t *out_buf, size_t out_cap, size_t *out_len) {
    cbor_stream_t s;
    cbor_init(&s, out_buf, out_cap);

    // Мапа з 6 пар ключ/значення (major type 5, довжина 6)
    cbor_write_byte(&s, 0xA6);

    // Ключ 1: node_id
    cbor_write_uint(&s, 0, 1);
    cbor_write_uint(&s, 0, node_id);

    // Ключ 2: timestamp
    cbor_write_uint(&s, 0, 2);
    cbor_write_uint(&s, 0, ts);

    // Ключ 3: fault_flag (major type 7: 0xF4 = false, 0xF5 = true)
    cbor_write_uint(&s, 0, 3);
    cbor_write_byte(&s, fault ? 0xF5 : 0xF4);

    // Ключ 4: temperature (для детермінізму множимо на 10 і пишемо як sint16)
    cbor_write_uint(&s, 0, 4);
    int16_t temp_scaled = (int16_t)(temp * 10.0f);
    if (temp_scaled >= 0) {
        cbor_write_uint(&s, 0, (uint32_t)temp_scaled);
    } else {
        cbor_write_uint(&s, 1, (uint32_t)(-1 - temp_scaled)); // major type 1: negative
    }

    // Ключ 5: humidity (uint16 помножений на 10)
    cbor_write_uint(&s, 0, 5);
    cbor_write_uint(&s, 0, (uint32_t)(hum * 10.0f));

    // Ключ 6: vbat_mv
    cbor_write_uint(&s, 0, 6);
    cbor_write_uint(&s, 0, vbat_mv);

    if (s.overflow) {
        return false;
    }
    *out_len = s.pos;
    return true;
}
