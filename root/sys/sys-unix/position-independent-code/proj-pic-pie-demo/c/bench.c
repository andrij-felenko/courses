/* bench.c — Вимірювання часу викликів на C */
#include <stdio.h>
#include <time.h>

static inline void local_func(long* val) {
    (*val)++;
}

void external_dummy(long* val); // Зовнішня функція з бібліотеки

int main(void) {
    long count = 0;
    clock_t start, end;

    start = clock();
    for (long i = 0; i < 100000000L; i++) {
        local_func(&count);
    }
    end = clock();
    printf("Локальний виклик (inlined/direct): %.4f сек\n", 
           (double)(end - start) / CLOCKS_PER_SEC);

    return 0;
}
