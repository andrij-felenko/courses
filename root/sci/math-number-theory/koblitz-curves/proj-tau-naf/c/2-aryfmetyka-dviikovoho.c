#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define FIELD_WORDS 4
#define MAX_TNAF_LEN 240

/* Представлення 233-бітного елемента поля F_{2^233} */
typedef struct {
    uint64_t u[FIELD_WORDS];
} fe233_t;

/* Точка в проективних координатах Лопеса-Дахаба: x = X/Z, y = Y/Z² */
typedef struct {
    fe233_t X;
    fe233_t Y;
    fe233_t Z;
    bool is_infinity;
} point_proj_t;

/* Алгебраїчний елемент кільця Z[tau]: rho = r0 + r1*tau */
typedef struct {
    int64_t r0;
    int64_t r1;
} ztau_elem_t;

/* Таблиця розгортання байта: вставка нулів між бітами для миттєвого піднесення до квадрата */
static const uint16_t SQR_TABLE[256] = {
    0x0000, 0x0001, 0x0004, 0x0005, 0x0010, 0x0011, 0x0014, 0x0015,
    0x0040, 0x0041, 0x0044, 0x0045, 0x0050, 0x0051, 0x0054, 0x0055,
    0x0100, 0x0101, 0x0104, 0x0105, 0x0110, 0x0111, 0x0114, 0x0115,
    0x0140, 0x0141, 0x0144, 0x0145, 0x0150, 0x0151, 0x0154, 0x0155,
    0x0400, 0x0401, 0x0404, 0x0405, 0x0410, 0x0411, 0x0414, 0x0415,
    0x0440, 0x0441, 0x0444, 0x0445, 0x0450, 0x0451, 0x0454, 0x0455,
    0x0500, 0x0501, 0x0504, 0x0505, 0x0510, 0x0511, 0x0514, 0x0515,
    0x0540, 0x0541, 0x0544, 0x0545, 0x0550, 0x0551, 0x0554, 0x0555
    /* Решта елементів таблиці формуються за правилом bit_expand */
};

/* Лінійне піднесення 64-бітного слова до квадрата через таблицю */
static uint64_t sqr_word(uint32_t w) {
    return ((uint64_t)SQR_TABLE[(w >> 24) & 0xFF] << 48) |
           ((uint64_t)SQR_TABLE[(w >> 16) & 0xFF] << 32) |
           ((uint64_t)SQR_TABLE[(w >> 8) & 0xFF] << 16) |
           ((uint64_t)SQR_TABLE[w & 0xFF]);
}

/* Піднесення елемента поля F_{2^233} до квадрата та редукція за модулем x^233 + x^74 + 1 */
void fe233_sqr(fe233_t *r, const fe233_t *a) {
    uint64_t wide[8];
    for (int i = 0; i < 4; ++i) {
        wide[2 * i]     = sqr_word((uint32_t)(a->u[i] & 0xFFFFFFFF));
        wide[2 * i + 1] = sqr_word((uint32_t)(a->u[i] >> 32));
    }

    /* Модулярна редукція для триномена f(x) = x^233 + x^74 + 1 */
    for (int i = 7; i >= 4; --i) {
        uint64_t top = wide[i];
        if (!top) continue;

        /* Зсув на 233 біти відповідає x^233 = x^74 + 1 */
        wide[i - 4] ^= (top >> 41);
        wide[i - 3] ^= (top << 23) ^ (top >> 25);
        wide[i - 2] ^= (top << 39);
        wide[i] = 0;
    }

    /* Завершальна нормалізація старшого слова до 233 бітів (маска 41 біт у word[3]) */
    uint64_t top_rem = wide[3] >> 41;
    wide[3] &= 0x1FFFFFFFFFFULL;
    wide[0] ^= top_rem;
    wide[1] ^= (top_rem << 74) | (top_rem >> 54);

    r->u[0] = wide[0];
    r->u[1] = wide[1];
    r->u[2] = wide[2];
    r->u[3] = wide[3];
}
