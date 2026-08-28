#include <stdint.h>
#include <stdbool.h>

#define DSHOT600_ARR          280
#define DSHOT600_CCR_BIT0     93
#define DSHOT600_CCR_BIT1     187
#define DSHOT_BUFFER_LENGTH   17

/* Розрахунок 16-бітного пакета DShot з 4-бітним CRC */
uint16_t dshot_prepare_packet(uint16_t throttle_value, bool telemetry_req, bool bidirectional) {
    if (throttle_value > 2047) {
        throttle_value = 2047;
    }

    uint16_t packet = (throttle_value << 1) | (telemetry_req ? 1 : 0);
    uint16_t csum = 0;
    uint16_t temp = packet;

    /* XOR трьох ніблів 12-бітного слова */
    for (int i = 0; i < 3; i++) {
        csum ^= (temp & 0x0F);
        temp >>= 4;
    }

    if (bidirectional) {
        csum = (~csum) & 0x0F; /* Інвертований CRC для Bi-dir DShot */
    } else {
        csum &= 0x0F;
    }

    return (packet << 4) | csum;
}

/* Заповнення масиву DMA значеннями порогів таймера CCR */
void dshot_build_dma_frame(uint16_t packet, uint32_t *dma_buffer) {
    for (int i = 0; i < 16; i++) {
        /* Старший біт іде першим (MSB first) */
        if (packet & (1 << (15 - i))) {
            dma_buffer[i] = DSHOT600_CCR_BIT1;
        } else {
            dma_buffer[i] = DSHOT600_CCR_BIT0;
        }
    }
    /* Завершальний нульовий рівень для міжкадрової паузи */
    dma_buffer[16] = 0;
}
