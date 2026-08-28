#include <stdio.h>
#include <stdint.h>

// Спрощена 16-бітна хеш-функція для демонстрації колізій Діріхле у криптографії
uint16_t simple_16bit_hash(const char* str) {
    uint16_t hash = 0x5555;
    while (*str) {
        hash ^= (uint16_t)(*str++);
        hash = (uint16_t)((hash << 5) | (hash >> 11)); // Циклічний зсув
    }
    return hash;
}

int main(void) {
    printf("=== Криптографічний аналіз: 16-бітний простір комірок ===\n");
    printf("Кількість унікальних 16-бітних хеш-кодів (комірок): %d\n", 1 << 16);
    printf("За принципом Діріхле, будь-яка множина з %d повідомлень\n", (1 << 16) + 1);
    printf("гарантовано містить принаймні одну криптографічну колізію!\n");

    const char* msg1 = "Message-A";
    const char* msg2 = "Message-B";
    printf("Хеш('%s') = 0x%04X\n", msg1, simple_16bit_hash(msg1));
    printf("Хеш('%s') = 0x%04X\n", msg2, simple_16bit_hash(msg2));
    return 0;
}
