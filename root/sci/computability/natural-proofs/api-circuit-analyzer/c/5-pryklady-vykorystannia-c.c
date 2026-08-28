#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#include "natural_analyzer.h"

int main(void) {
    printf("=== Приклад використання C API libnatural_analyzer ===\n");

    natural_config_t config;
    natural_error_t err = natural_config_default(&config, 4); /* n = 4 змінних */
    if (err != NATURAL_SUCCESS) {
        fprintf(stderr, "Помилка конфігурації: %s\n", natural_error_string(err));
        return 1;
    }

    config.largeness_threshold = 0.05; /* 5% поріг великості */
    config.enable_walsh_transform = true;

    void* ctx = NULL;
    err = natural_context_create(&config, &ctx);
    if (err != NATURAL_SUCCESS) {
        fprintf(stderr, "Помилка створення контексту: %s\n", natural_error_string(err));
        return 1;
    }

    /* Таблиця істинності функції PARITY від 4 змінних (N = 16 біт, 2 байти) */
    uint8_t parity_table[2] = { 0x69, 0x96 };

    err = natural_set_truth_table(ctx, parity_table, sizeof(parity_table));
    if (err == NATURAL_SUCCESS) {
        natural_result_t result;
        err = natural_analyze(ctx, &result);
        if (err == NATURAL_SUCCESS) {
            printf("Аналіз завершено успішно:\n");
            printf(" - Час обчислення: %llu мкс\n", (unsigned long long)result.elapsed_time_us);
            printf(" - Частка великості: %.2f%%\n", result.estimated_largeness * 100.0);
            printf(" - Конструктивність: %s\n", result.is_constructive ? "ТАК" : "НІ");
            printf(" - Великість: %s\n", result.is_large ? "ТАК" : "НІ");
            printf(" - Вердикт Натуральності: %s\n", result.is_natural ? "НАТУРАЛЬНЕ ДОВЕДЕННЯ" : "НЕ-НАТУРАЛЬНЕ");
        }
    }

    natural_context_destroy(ctx);
    return 0;
}
