#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

long parse_config_value(const char *str, int *out_ok) {
    char *endptr = NULL;
    errno = 0; /* ОБОВ'ЯЗКОВО: скидаємо стан перед викликом */

    long val = strtol(str, &endptr, 10);

    /* 1. Перевірка на переповнення / вихід за межі */
    if (errno == ERANGE && (val == LONG_MAX || val == LONG_MIN)) {
        if (out_ok) *out_ok = 0;
        return 0;
    }
    /* 2. Перевірка на інші системні помилки */
    if (errno != 0 && val == 0) {
        if (out_ok) *out_ok = 0;
        return 0;
    }
    /* 3. Перевірка: чи було прочитано хоча б одну цифру */
    if (endptr == str) {
        if (out_ok) *out_ok = 0;
        return 0;
    }

    if (out_ok) *out_ok = 1;
    return val;
}
