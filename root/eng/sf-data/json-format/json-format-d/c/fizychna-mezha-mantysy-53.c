#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

int main(void) {
    uint64_t original_id = 9007199254740993ULL; /* 2^53 + 1 */
    
    /* Парсинг числа в тип double (як це робить штатний JSON парсер) */
    double parsed_as_double = (double)original_id;
    uint64_t recovered_id = (uint64_t)parsed_as_double;

    printf("Початковий ID:    %" PRIu64 "\n", original_id);
    printf("Після double:     %" PRIu64 "\n", recovered_id);
    printf("Втрата точності:  %s\n", (original_id != recovered_id) ? "ТАК (значення змінено!)" : "НІ");

    return 0;
}
