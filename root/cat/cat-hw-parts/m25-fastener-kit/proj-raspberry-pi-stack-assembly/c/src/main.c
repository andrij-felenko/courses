/**
 * @file main.c
 * @brief Точка входу консольної утиліти для стрес-тестування шилда HAT (M2.5 fastener kit)
 *        та перевірки якості монтажу через шину I2C.
 */

#include <stdio.h>
#include <stdlib.h>
#include "hat_contact_tester.h"

int main(int argc, char *argv[]) {
    printf("=== Консольна утиліта перевірки контактів HAT (M2.5 Fastener Kit) ===\n");

    hat_test_config_t config;
    hat_tester_init_config(&config);

    // Якщо передано аргумент з кількістю циклів, перевизначаємо
    if (argc > 1) {
        int custom_cycles = atoi(argv[1]);
        if (custom_cycles > 0) {
            config.total_cycles = custom_cycles;
        }
    }

    // Якщо передано шлях до шини I2C
    if (argc > 2) {
        config.i2c_device_path = argv[2];
    }

    hat_test_stats_t stats;

    // Запуск стрес-тесту
    if (!hat_tester_run_stress_test(&config, &stats)) {
        fprintf(stderr, "[КРИТИЧНА ПОМИЛКА] Не вдалося виконати стрес-тест шини I2C.\n");
        fprintf(stderr, "Переконайтеся, що ви запускаєте утиліту на Linux з правами доступу до /dev/i2c-1\n");
        fprintf(stderr, "та що шилд HAT підключено коректно.\n");
        return 1;
    }

    // Виведення діагностичного звіту
    hat_tester_print_report(&stats);

    return (stats.failure_rate_percent > 5.0) ? 1 : 0;
}
