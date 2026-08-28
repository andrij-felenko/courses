#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// ── 1. Контракт політики кадрування ──────────────────────────────────
typedef struct {
    const uint8_t* header;
    size_t header_len;
    size_t max_payload;
    uint8_t initial_crc;
    uint8_t (*update_crc)(uint8_t current_crc, uint8_t byte);
} frame_policy_t;

// ── 2. Єдиний механізм кінцевого автомата ───────────────────────────
typedef struct {
    const frame_policy_t* policy;
    uint8_t* buffer;
    size_t buffer_capacity;
    size_t payload_len;
    size_t expected_len;
    size_t header_matched;
    uint8_t crc;
    uint8_t state;
} stream_framer_t;

void stream_framer_init(stream_framer_t* f, const frame_policy_t* policy, uint8_t* buf, size_t cap) {
    f->policy = policy;
    f->buffer = buf;
    f->buffer_capacity = cap;
    f->state = 0;
    f->header_matched = 0;
    f->payload_len = 0;
    f->crc = policy->initial_crc;
}

bool stream_framer_feed(stream_framer_t* f, uint8_t byte, void (*on_frame)(const uint8_t*, size_t)) {
    switch (f->state) {
        case 0: // Зіставлення байтів преамбули довільної довжини
            if (byte == f->policy->header[f->header_matched]) {
                f->header_matched++;
                if (f->header_matched == f->policy->header_len) {
                    f->state = 1;
                    f->header_matched = 0;
                    f->payload_len = 0;
                    f->crc = f->policy->initial_crc;
                }
            } else {
                // Безпечний відкат FSM при частковому збігу преамбули
                f->header_matched = (byte == f->policy->header[0]) ? 1 : 0;
            }
            break;

        case 1: // Читання довжини та перевірка інваріанта переповнення
            f->expected_len = byte;
            f->crc = f->policy->update_crc(f->crc, byte);
            if (byte <= f->buffer_capacity && byte <= f->policy->max_payload) {
                f->state = 2;
            } else {
                f->state = 0; // Відхилення аномально довгого кадру
            }
            break;

        case 2: // Накопичення корисного вантажу в буфер
            f->buffer[f->payload_len++] = byte;
            f->crc = f->policy->update_crc(f->crc, byte);
            if (f->payload_len == f->expected_len) {
                f->state = 3;
            }
            break;

        case 3: // Перевірка контрольної суми
            f->state = 0;
            if (f->crc == byte) {
                on_frame(f->buffer, f->payload_len);
                return true;
            }
            break;
    }
    return false;
}

// ── 3. Декларативні конфігурації конкретних протоколів ───────────────

static uint8_t crc_xor(uint8_t c, uint8_t b) { return c ^ b; }
static uint8_t crc_add(uint8_t c, uint8_t b) { return c + b; }

static const uint8_t GNSS_HDR[] = { 0xAA, 0x55 };
static const frame_policy_t GNSS_POLICY = {
    .header = GNSS_HDR, .header_len = 2,
    .max_payload = 128, .initial_crc = 0x00, .update_crc = crc_xor
};

static const uint8_t OPTIC_HDR[] = { 0x24 };
static const frame_policy_t OPTIC_POLICY = {
    .header = OPTIC_HDR, .header_len = 1,
    .max_payload = 64, .initial_crc = 0xFF, .update_crc = crc_add
};
