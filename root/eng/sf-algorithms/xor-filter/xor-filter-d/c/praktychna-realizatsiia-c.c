#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

/* Використання бібліотечного Xor-фільтра */
#include "xor_filter.h"

int main(void) {
    const size_t num_keys = 5;
    uint64_t dataset[5] = {
        0x1000ULL, 0x2000ULL, 0x3000ULL, 0x4000ULL, 0x5000ULL
    };

    xor_filter_8_t filter;
    if (!xor_filter_8_build(&filter, dataset, num_keys)) {
        fprintf(stderr, "Помилка конструювання Xor-фільтра\n");
        return 1;
    }

    /* Перевірка наявних ключів */
    for (size_t i = 0; i < num_keys; ++i) {
        bool exists = xor_filter_8_contains(&filter, dataset[i]);
        printf("Ключ 0x%llX: %s (очікується ТАК)\n",
               (unsigned long long)dataset[i], exists ? "ТАК" : "НІ");
    }

    /* Перевірка відсутнього ключа */
    uint64_t missing_key = 0x9999ULL;
    bool false_positive = xor_filter_8_contains(&filter, missing_key);
    printf("Відсутній ключ 0x%llX: %s\n",
           (unsigned long long)missing_key, false_positive ? "ХИБНИЙ СПАЛАХ" : "НІ (відсутній)");

    xor_filter_8_destroy(&filter);
    return 0;
}
