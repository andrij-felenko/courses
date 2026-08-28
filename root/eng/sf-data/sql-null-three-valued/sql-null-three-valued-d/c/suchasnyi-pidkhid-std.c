#include <stdio.h>
#include <stdbool.h>

/* C-стиль представлення nullable поля через структуру з прапорцем */
typedef struct {
    int value;
    bool has_value;
} NullableInt;

NullableInt make_null(void) {
    NullableInt res = { 0, false };
    return res;
}

NullableInt make_int(int val) {
    NullableInt res = { val, true };
    return res;
}
