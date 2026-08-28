#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define AES_POLY 0x11B  /* Поліном AES: x^8 + x^4 + x^3 + x + 1 */
#define FIELD_SIZE 256

/* Таблиці логарифмів та експонент для GF(2^8) */
static uint8_t gf_exp[FIELD_SIZE * 2];
static uint8_t gf_log[FIELD_SIZE];
static bool tables_initialized = false;

/* Додавання та віднімання у GF(2^8) еквівалентні побітовому XOR */
uint8_t gf_add(uint8_t a, uint8_t b) {
    return a ^ b;
}

uint8_t gf_sub(uint8_t a, uint8_t b) {
    return a ^ b;
}

/* Множення одного елемента на x (зсув вліво з маскою редукції 0x1B) */
uint8_t gf_mul_x(uint8_t a) {
    if (a & 0x80) {
        return (uint8_t)((a << 1) ^ 0x1B);
    } else {
        return (uint8_t)(a << 1);
    }
}

/* Поліноміальне множення "зсув-і-складання" без таблиць O(m) */
uint8_t gf_mul_slow(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    uint8_t temp_a = a;
    uint8_t temp_b = b;

    while (temp_b > 0) {
        if (temp_b & 1) {
            result ^= temp_a;
        }
        temp_a = gf_mul_x(temp_a);
        temp_b >>= 1;
    }
    return result;
}

/* Генерація таблиць експонент та логарифмів за примітивним елементом alpha = 0x03 */
void gf_init_tables(void) {
    uint8_t x = 1;
    /* У полі AES з поліномом 0x11B елемент 0x03 є примітивним породжувачем */
    uint8_t primitive = 0x03;

    for (int i = 0; i < 255; i++) {
        gf_exp[i] = x;
        gf_exp[i + 255] = x;
        gf_log[x] = (uint8_t)i;
        x = gf_mul_slow(x, primitive);
    }
    gf_log[0] = 0; /* Дискретний логарифм нуля не визначений */
    tables_initialized = true;
}

/* Швидке множення O(1) за допомогою таблиць Зеха */
uint8_t gf_mul_fast(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    if (!tables_initialized) gf_init_tables();
    int log_sum = gf_log[a] + gf_log[b];
    return gf_exp[log_sum];
}

/* Швидке ділення O(1) за допомогою віднімання логарифмів */
uint8_t gf_div_fast(uint8_t a, uint8_t b) {
    if (b == 0) return 0; /* Ділення на нуль повертає 0 як індикатор помилки */
    if (a == 0) return 0;
    if (!tables_initialized) gf_init_tables();
    int log_diff = gf_log[a] - gf_log[b] + 255;
    return gf_exp[log_diff % 255];
}
