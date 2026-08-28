#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

/* Включення заголовочного файла специфікації API */
/* #include "arithmetic_oracle_api.h" */

int main(void) {
    printf("=== Демонстрація використання C API Арифметичної Ієрархії ===\n\n");

    /* Побудова префікса для перевірки тотальності: ∀x ∃s T(e, x, s) */
    ah_quantifier_t total_prefix[] = {
        { AH_QUANT_FORALL, "x", false, 0 },
        { AH_QUANT_EXISTS, "s", false, 0 }
    };
    size_t count = sizeof(total_prefix) / sizeof(total_prefix[0]);

    ah_hierarchy_info_t info;
    int status = ah_classify_prefix(total_prefix, count, &info);

    if (status == AH_SUCCESS) {
        printf("Успішна класифікація формули:\n");
        printf(" - Початкових кванторів:  %zu\n", info.raw_quantifier_count);
        printf(" - Згорнутих кванторів:   %zu\n", info.contracted_count);
        printf(" - Рівень ієрархії (n):   %u\n", info.level_n);
        printf(" - Клас складності:       %s_%u^0\n", 
               (info.class_type == AH_CLASS_SIGMA_N) ? "Sigma" : "Pi", 
               info.level_n);
        printf(" - Потрібний оракул:      0^(%u)\n", info.oracle_jump_required);
        printf(" - Розв'язна (Delta_1):   %s\n", info.is_decidable ? "Так" : "Ні");
        printf(" - Перелічувана (Sigma_1): %s\n", info.is_recursively_enumerable ? "Так" : "Ні");
    } else {
        printf("Помилка класифікації: код %d\n", status);
    }

    /* Демонстрація безпечного кодування Кантора */
    uint64_t x = 42, y = 100, code = 0;
    if (ah_cantor_encode(x, y, &code) == AH_SUCCESS) {
        printf("\nПарування Кантора: <%lu, %lu> = %lu\n", (unsigned long)x, (unsigned long)y, (unsigned long)code);
        
        uint64_t rx = 0, ry = 0;
        if (ah_cantor_decode(code, &rx, &ry) == AH_SUCCESS) {
            printf("Декодування Кантора: %lu -> <%lu, %lu>\n", (unsigned long)code, (unsigned long)rx, (unsigned long)ry);
        }
    }

    return 0;
}
