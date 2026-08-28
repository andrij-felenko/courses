#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди завершення та статуси виконання операцій */
typedef enum {
    CANTOR_SUCCESS           =  0, /* Операцію виконано успішно без помилок */
    CANTOR_ERR_NULL_POINTER  = -1, /* Передано нульовий покажчик для вихідних даних */
    CANTOR_ERR_OVERFLOW      = -2, /* Арифметичне переповнення цілочисельної розрядної сітки */
    CANTOR_ERR_INVALID_DIM   = -3  /* Некоректна розмірність кортежу (k == 0 або k > MAX_DIM) */
} cantor_status_t;

/* Двовимірна пара 32-бітних невід'ємних координат (ℕ₀ × ℕ₀) */
typedef struct {
    uint32_t x; /* Горизонтальна координата точки */
    uint32_t y; /* Вертикальна координата точки (зсув всередині діагоналі) */
} cantor_pair32_t;

/* Двовимірна пара 64-бітних невід'ємних координат */
typedef struct {
    uint64_t x;
    uint64_t y;
} cantor_pair64_t;

/* Двовимірна пара 32-бітних знакових цілих чисел для простору ℤ × ℤ */
typedef struct {
    int32_t x;  /* Знакова координата x */
    int32_t y;  /* Знакова координата y */
} cantor_signed_pair32_t;
