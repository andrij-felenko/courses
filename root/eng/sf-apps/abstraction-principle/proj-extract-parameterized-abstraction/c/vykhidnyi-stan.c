#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define GNSS_MAX_PAYLOAD 128
#define OPTIC_MAX_PAYLOAD 64

// Стан парсера GNSS: очікує преамбулу 0xAA 0x55, довжину, байти тіла, контрольний байт XOR
typedef struct {
    uint8_t buf[GNSS_MAX_PAYLOAD];
    size_t len;
    size_t expected_len;
    uint8_t state;
    uint8_t crc;
} gnss_parser_t;

bool gnss_feed_byte(gnss_parser_t* p, uint8_t byte, void (*on_frame)(const uint8_t*, size_t)) {
    switch (p->state) {
        case 0: // Пошук першого байта заголовка 0xAA
            if (byte == 0xAA) { p->state = 1; }
            break;
        case 1: // Пошук другого байта заголовка 0x55
            if (byte == 0x55) { p->state = 2; p->len = 0; p->crc = 0; }
            else { p->state = (byte == 0xAA) ? 1 : 0; }
            break;
        case 2: // Зчитування довжини корисного навантаження
            p->expected_len = byte;
            p->crc ^= byte;
            p->state = (byte <= GNSS_MAX_PAYLOAD) ? 3 : 0;
            break;
        case 3: // Накопичення байтів корисного навантаження
            p->buf[p->len++] = byte;
            p->crc ^= byte;
            if (p->len == p->expected_len) { p->state = 4; }
            break;
        case 4: // Звірка контрольної суми
            p->state = 0;
            if (p->crc == byte) {
                on_frame(p->buf, p->len);
                return true;
            }
            break;
    }
    return false;
}

// Стан парсера оптичного давача: очікує преамбулу '$' (0x24), довжину, дані, байт суми за модулем 256
typedef struct {
    uint8_t buf[OPTIC_MAX_PAYLOAD];
    size_t len;
    size_t expected_len;
    uint8_t state;
    uint8_t crc;
} optic_parser_t;

bool optic_feed_byte(optic_parser_t* p, uint8_t byte, void (*on_frame)(const uint8_t*, size_t)) {
    switch (p->state) {
        case 0: // Пошук заголовка '$' (0x24)
            if (byte == 0x24) { p->state = 1; p->len = 0; p->crc = 0xFF; }
            break;
        case 1: // Зчитування довжини
            p->expected_len = byte;
            p->crc += byte;
            p->state = (byte <= OPTIC_MAX_PAYLOAD) ? 2 : 0;
            break;
        case 2: // Накопичення тіла кадру
            p->buf[p->len++] = byte;
            p->crc += byte;
            if (p->len == p->expected_len) { p->state = 3; }
            break;
        case 3: // Перевірка контрольної суми
            p->state = 0;
            if (p->crc == byte) {
                on_frame(p->buf, p->len);
                return true;
            }
            break;
    }
    return false;
}
