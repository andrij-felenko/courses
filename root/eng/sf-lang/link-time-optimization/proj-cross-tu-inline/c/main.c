// main.c — точка входу та використання інтерфейсу (C)
#include <stdio.h>
#include "engine.h"

int main(void) {
    GainFilter filter;
    gain_filter_init(&filter, 5);

    // Віртуальний / непрямий виклик через покажчик на функцію
    int32_t step1 = filter.base.process(&filter, 10);

    // Виклик окремої функції з іншого модуля
    int32_t step2 = fast_scale(step1, 3);

    printf("Result: %d\n", step2);
    return 0;
}
