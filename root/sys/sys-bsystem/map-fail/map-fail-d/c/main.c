// C99: Компактне форматування числа з фіксованою комою
#include <stdint.h>
#include <stddef.h>

// Форматує число виду 12345 (значення 123.45) у рядок без використання float і printf
// Займає всього ~120 байтів Flash замість 20+ КБ
size_t format_fixed_point(char *out, size_t max_len, int32_t val, uint8_t decimals) {
    char temp[16];
    size_t idx = 0;
    int is_neg = 0;

    if (val < 0) {
        is_neg = 1;
        val = -val;
    }

    // Запис дробової та цілої частин у зворотному порядку
    uint8_t dec_count = 0;
    do {
        if (decimals > 0 && dec_count == decimals) {
            temp[idx++] = '.';
        }
        temp[idx++] = (char)('0' + (val % 10));
        val /= 10;
        dec_count++;
    } while (val > 0 || dec_count <= decimals);

    if (is_neg) {
        temp[idx++] = '-';
    }

    if (idx >= max_len) {
        return 0; // Переповнення буфера
    }

    // Реверс рядка у вихідний буфер
    for (size_t i = 0; i < idx; ++i) {
        out[i] = temp[idx - 1 - i];
    }
    out[idx] = '\0';
    return idx;
}
