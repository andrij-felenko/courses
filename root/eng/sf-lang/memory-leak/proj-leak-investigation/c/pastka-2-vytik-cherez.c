#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

int process_data(const int *buf, size_t size) {
    if (size == 0) return -1; /* Помилка вхідних даних */
    int sum = 0;
    for (size_t i = 0; i < size; ++i) sum += buf[i];
    return sum;
}

int calculate(size_t n) {
    int *buffer = (int *)malloc(n * sizeof(int));
    if (!buffer) return -1;

    /* Імітація обробки даних */
    for (size_t i = 0; i < n; ++i) buffer[i] = (int)(i * 2);

    int result = process_data(buffer, 0); // Повертає -1 (помилка)
    if (result < 0) {
        /* ПОМИЛКА: Раннє повернення без виклику free(buffer) */
        return -1; 
    }

    free(buffer);
    return result;
}

int main(void) {
    int res = calculate(1024);
    printf("Результат: %d (пам'ять 4 KB витекла через ранній return)\n", res);
    return 0;
}
