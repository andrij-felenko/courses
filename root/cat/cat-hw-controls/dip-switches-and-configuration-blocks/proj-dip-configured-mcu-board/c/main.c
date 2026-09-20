#include <stdio.h>
#include "dip_switch.h"

// Зовнішня функція емуляції перемикання станів пінів для тестування
extern void dip_switch_set_simulated_pins(uint8_t pins_state);

int main(void) {
    printf("=== Драйвер зчитування та декодування DIP-перемикачів (C) ===\n\n");
    
    // Конфігурація 8-позиційного DIP-блока:
    // Біти 0..3: Адреса пристрою на шині (маска 0x0F, без зсуву)
    // Біти 4..7: Прапорці режимів роботи (маска 0xF0, зсув на 4 біти)
    dip_switch_config_t dip_cfg = {
        .pin_numbers = {0, 1, 2, 3, 4, 5, 6, 7},
        .pin_count = 8,
        .address_mask = 0x0F,
        .address_shift = 0,
        .mode_mask = 0xF0,
        .mode_shift = 4,
        .debounce_samples = 3
    };
    
    // Ініціалізація вхідних ліній GPIO
    dip_switch_init(&dip_cfg);
    
    // Тест 1: Важелі 0, 2 увімкнені (Адреса = 5), важіль 4 увімкнений (Режим = 1)
    // При підтяжці Pull-Up увімкнений важіль дає 0, вимкнений 1 -> Байт пінів: 0xEA
    dip_switch_set_simulated_pins(0xEA);
    
    dip_switch_data_t data;
    if (dip_switch_read_stable(&dip_cfg, &data)) {
        printf("[УСПІХ] Стабільний стан конфігурації зчитано:\n");
        printf("  Сирий стан ліній GPIO (Active Low): 0x%02X\n", data.raw_pins_state);
        printf("  Декодований конфігураційний байт: 0x%02X\n", data.config_byte);
        printf("  Виділена адреса пристрою (біти 0..3): %d (0x%X)\n", data.device_address, data.device_address);
        printf("  Прапорці режимів роботи (біти 4..7): %d (0x%X)\n", data.mode_flags, data.mode_flags);
    } else {
        printf("[ПОМИЛКА] Виявлено брязкіт або нестабільний стан DIP-перемикача!\n");
    }
    
    printf("\n--- Симуляція зміни стану важелів перемикача ---\n");
    // Тест 2: Важелі 0, 1, 2, 3 увімкнені (Адреса = 15), важелі 6, 7 увімкнені (Режим = 12)
    // Байт пінів: 0x30 (біти 0..3 = 0, біти 4..5 = 1, біти 6..7 = 0)
    dip_switch_set_simulated_pins(0x30);
    
    if (dip_switch_read_stable(&dip_cfg, &data)) {
        printf("[УСПІХ] Нова конфігурація зчитана:\n");
        printf("  Декодований конфігураційний байт: 0x%02X\n", data.config_byte);
        printf("  Нова адреса пристрою: %d\n", data.device_address);
        printf("  Нові прапорці режимів: %d\n", data.mode_flags);
    }
    
    return 0;
}
