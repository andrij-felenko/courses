#include <stdio.h>
#include <stdint.h>

typedef struct {
    int32_t num;
    int32_t den;
} Fraction;

/* Послідовна друкарня дробів Фарея порядку n.
   Використовує O(1) пам'яті (лише 6 змінних) та O(n²) часу. */
void farey_sequence_print(int32_t n) {
    if (n < 1) return;

    /* Початкові два члени послідовності Fₙ */
    Fraction f1 = {0, 1};
    Fraction f2 = {1, n};

    printf("%d/%d, %d/%d", f1.num, f1.den, f2.num, f2.den);

    int32_t a = f1.num, b = f1.den;
    int32_t c = f2.num, d = f2.den;

    while (c < d || c == 1) {
        /* Обчислюємо максимальний цілий коефіцієнт крок-вперед */
        int32_t k = (n + b) / d;
        int32_t e = k * c - a;
        int32_t f = k * d - b;

        printf(", %d/%d", e, f);

        /* Зсув вікна з двох попередніх дробів */
        a = c; b = d;
        c = e; d = f;

        if (e == 1 && f == 1) break;
    }
    printf("\n");
}
