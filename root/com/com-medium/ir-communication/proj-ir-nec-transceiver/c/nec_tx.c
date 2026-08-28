/* nec_tx.c - Генерація пачок передавача */
#include <stdint.h>
#include <stdbool.h>

// Апаратні функції керування ШІМ таймера
extern void timer_pwm_carrier_enable(void);
extern void timer_pwm_carrier_disable(void);
extern void delay_us(uint32_t us);

void nec_tx_send_burst(uint32_t burst_us, uint32_t space_us) {
    timer_pwm_carrier_enable();
    delay_us(burst_us);
    timer_pwm_carrier_disable();
    if (space_us > 0) {
        delay_us(space_us);
    }
}

void nec_tx_send_frame(uint8_t address, uint8_t command) {
    uint32_t raw = (uint32_t)address |
                   ((uint32_t)(~address & 0xFF) << 8) |
                   ((uint32_t)command << 16) |
                   ((uint32_t)(~command & 0xFF) << 24);

    // 1. Преамбула (Leader)
    nec_tx_send_burst(9000, 4500);

    // 2. Передача 32 бітів даних (LSB first)
    for (uint8_t i = 0; i < 32; i++) {
        if (raw & ((uint32_t)1 << i)) {
            // Біт '1': 560 мкс пачка + 1690 мкс пауза
            nec_tx_send_burst(560, 1690);
        } else {
            // Біт '0': 560 мкс пачка + 560 мкс пауза
            nec_tx_send_burst(560, 560);
        }
    }

    // 3. Завершальний стоп-імпульс
    nec_tx_send_burst(560, 0);
}
