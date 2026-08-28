#include <stdint.h>
#include <stdbool.h>

/* Функція обробки буфера з явним бар'єром компілятора */
void process_with_barrier(int *shared_buffer, int count) {
    for (int i = 0; i < count; ++i) {
        shared_buffer[i] = i * 2;
        
        /* Програмний бар'єр забороняє переносити або об'єднувати записи */
        __asm__ __volatile__ ("" ::: "memory");
    }
}

/* Функція обробки буфера без бар'єра (піддається агресивній оптимізації) */
void process_without_barrier(int *shared_buffer, int count) {
    for (int i = 0; i < count; ++i) {
        shared_buffer[i] = i * 2;
    }
}
