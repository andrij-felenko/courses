#include <stdio.h>
#include <stdint.h>
#include <math.h>

/* Обчислення складності Поліга — Геллмана за найбільшим простим множником */
double estimate_pohlig_hellman_ops(uint64_t max_prime_factor) {
    return sqrt((double)max_prime_factor);
}

int main(void) {
    printf("=== Симуляція аналізу стійкості до атаки Поліга — Геллмана (C) ===\n\n");

    /* Параметри гладкого модуля */
    uint64_t smooth_q = 180181;
    uint64_t smooth_max_factor = 13; /* q - 1 = 180180 = 2^2 * 3^2 * 5 * 7 * 11 * 13 */

    /* Параметри безпечного модуля */
    uint64_t safe_p = 500000003;
    uint64_t safe_q = 2 * safe_p + 1;

    double ops_smooth = estimate_pohlig_hellman_ops(smooth_max_factor);
    double ops_safe = estimate_pohlig_hellman_ops(safe_p);

    printf("1. Гладкий модуль q = %llu (найбільший множник q-1 дорівнює %llu):\n", 
           (unsigned long long)smooth_q, (unsigned long long)smooth_max_factor);
    printf("   Обчислювальна складність атаки: %.2f операцій.\n", ops_smooth);
    printf("   СТАТУС: ЗЛАМАНО МИТТЄВО!\n\n");

    printf("2. Безпечний модуль q = 2p + 1 = %llu (найбільший множник p = %llu):\n", 
           (unsigned long long)safe_q, (unsigned long long)safe_p);
    printf("   Обчислювальна складність атаки: %.2f операцій.\n", ops_safe);
    printf("   СТАТУС: АБОЛЮТНИЙ КРИПТОГРАФІЧНИЙ ЗАХИСТ!\n\n");

    printf("Перевага безпечного модуля у стійкості: у %.0f разів вища!\n", ops_safe / ops_smooth);

    return 0;
}
