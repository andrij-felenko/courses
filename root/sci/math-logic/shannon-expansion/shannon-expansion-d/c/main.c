#include <stdint.h>
#include <stdio.h>

/* Уся функція трьох змінних — 8 бітів: біт i несе значення f на наборі
   A = (i>>2)&1, B = (i>>1)&1, C = i&1. Мажоритарна функція A·B+A·C+B·C
   має одиниці в рядках 011, 101, 110, 111 — це 0xE8. */

static const uint8_t WHERE_1[3] = { 0xAA, 0xCC, 0xF0 };   /* де C=1, де B=1, де A=1 */

/* Кофактор за змінною j: лишаємо потрібну половину рядків і копіюємо її
   на місце викинутої — після цього змінна j ні на що не впливає. */
static uint8_t cofactor(uint8_t f, int j, int value)
{
    int shift = 1 << j;                  /* відстань між рядками, що різняться бітом j */
    uint8_t half = f & (value ? WHERE_1[j] : (uint8_t)~WHERE_1[j]);
    return value ? (uint8_t)(half | (half >> shift))
                 : (uint8_t)(half | (half << shift));
}

int main(void)
{
    uint8_t maj = 0xE8;
    printf("f           = %02X\n", maj);
    printf("f при C = 1 = %02X   (A + B)\n", cofactor(maj, 0, 1));
    printf("f при C = 0 = %02X   (A · B)\n", cofactor(maj, 0, 0));

    /* Тотожність — це просто збирання половин назад. Перевіримо її на ВСІХ
       256 функціях трьох змінних і за кожною з трьох змінних. */
    for (int f = 0; f < 256; f++)
        for (int j = 0; j < 3; j++) {
            uint8_t m = WHERE_1[j];
            uint8_t f1 = cofactor((uint8_t)f, j, 1);
            uint8_t f0 = cofactor((uint8_t)f, j, 0);
            if ((uint8_t)((m & f1) | (~m & f0)) != (uint8_t)f) {
                printf("спростовано: f=%02X, змінна %d\n", f, j);
                return 1;
            }
        }
    puts("тотожність справджується для всіх 256 функцій трьох змінних");
    return 0;
}
