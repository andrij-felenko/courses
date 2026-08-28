#include <stdint.h>
#include <stddef.h>

/**
 * Гарантоване затирання пам'яті без ризику видалення оптимізатором.
 * Використовує volatile вказівник та асемблерний бар'єр пам'яті.
 */
void secure_zero_memory(void *v, size_t n) {
    if (v == NULL || n == 0) {
        return;
    }
    
    // Крок 1: побайтовий запис через volatile вказівник
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) {
        *p++ = 0x00;
    }

    // Крок 2: бар'єр пам'яті для гарантії завершення всіх операцій запису
    #if defined(__GNUC__) || defined(__clang__)
    __asm__ __volatile__("" : : "r"(v) : "memory");
    #endif
}

/**
 * Порівняння двох буферів секретів за константний час (Constant-Time).
 * Запобігає витоку секретів через аналіз часу виконання (Timing Attacks).
 * 
 * Повертає:
 *   1 — якщо буфери повністю ідентичні;
 *   0 — якщо є бодай один незбіжний байт або некоректні параметри.
 */
int constant_time_memcmp(const void *a, const void *b, size_t n) {
    if (a == NULL || b == NULL) {
        return 0;
    }

    const volatile uint8_t *pa = (const volatile uint8_t *)a;
    const volatile uint8_t *pb = (const volatile uint8_t *)b;
    volatile uint8_t diff = 0;

    // Цикл проходить ВСІ n байтів завжди, без дострокового виходу
    for (size_t i = 0; i < n; i++) {
        diff |= (pa[i] ^ pb[i]);
    }

    // Повертаємо 1 лише тоді, коли diff == 0
    return (diff == 0);
}
