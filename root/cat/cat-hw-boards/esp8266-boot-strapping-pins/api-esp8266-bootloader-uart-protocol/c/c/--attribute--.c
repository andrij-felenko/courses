#include <stdint.h>
#include <stddef.h>

#define SLIP_END     0xC0
#define SLIP_ESC     0xDB
#define SLIP_ESC_END 0xDC
#define SLIP_ESC_ESC 0xDD

typedef struct __attribute__((packed)) {
    uint8_t  direction;  // 0x00 = Запит, 0x01 = Відповідь
    uint8_t  command;    // Код команди (Opcode)
    uint16_t size;       // Розмір даних у байтах
    uint32_t checksum;   // Контрольна сума або аргумент
} rom_command_header_t;

size_t slip_encode(const uint8_t *src, size_t src_len, uint8_t *dst) {
    size_t out_idx = 0;
    dst[out_idx++] = SLIP_END;
    for (size_t i = 0; i < src_len; i++) {
        if (src[i] == SLIP_END) {
            dst[out_idx++] = SLIP_ESC;
            dst[out_idx++] = SLIP_ESC_END;
        } else if (src[i] == SLIP_ESC) {
            dst[out_idx++] = SLIP_ESC;
            dst[out_idx++] = SLIP_ESC_ESC;
        } else {
            dst[out_idx++] = src[i];
        }
    }
    dst[out_idx++] = SLIP_END;
    return out_idx;
}
