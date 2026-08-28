#include <stdio.h>
#include <math.h>

void verify_compression_pigeonhole(unsigned int n_bits) {
    if (n_bits >= 30) {
        printf("Розмір N = %u занадто великий для обчислення 64-бітними числами.\n", n_bits);
        return;
    }

    // 2^N вхідних комбінацій
    unsigned long long input_space_size = 1ULL << n_bits;           
    // Сума 2^k для k від 0 до N-1 дорівнює 2^N - 1
    unsigned long long output_space_size = input_space_size - 1;    

    printf("=== Аналіз універсального стиснення для файлів N = %u бітів ===\n", n_bits);
    printf("Кількість унікальних вхідних файлів (2^N):   %llu\n", input_space_size);
    printf("Кількість вихідних кодів довжиною < N (2^N-1): %llu\n", output_space_size);

    if (input_space_size > output_space_size) {
        printf("ОЦІНКА: Вхідних файлів (%llu) > Вихідних комірок (%llu).\n",
               input_space_size, output_space_size);
        printf("ВИСНОВОК: За принципом Діріхле універсальне стиснення БЕЗ втрат ламається!\n");
        printf("Принаймні %llu файли отримають однаковий стиснений код (колізія).\n",
               input_space_size - output_space_size + 1);
    }
}

int main(void) {
    verify_compression_pigeonhole(3);
    printf("\n");
    verify_compression_pigeonhole(8);
    return 0;
}
