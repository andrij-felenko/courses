/* src/main.c — реалізація утиліти на чистій мові C11 */
#include <stdio.h>
#include <stdint.h>
#include "diag/config.h"

int main(void) {
    printf("========================================\n");
    printf("Діагностична утиліта ядра (C11 клієнт)\n");
    printf("========================================\n");
    printf("Розмір виділеного буфера: %d байтів\n", (int)DIAG_BUFFER_SIZE);

#if DIAG_ENABLE_ZSTD
    printf("Підсистема стиснення: модуль Zstandard [УВІМКНЕНО]\n");
#else
    printf("Підсистема стиснення: raw stream [ВИМКНЕНО]\n");
#endif

#if DIAG_ENABLE_TRACING
    printf("Мережеве трасування: розширений журнал [АКТИВНИЙ]\n");
#else
    printf("Мережеве трасування: вимкнено для економії CPU\n");
#endif

#if DIAG_ENABLE_AVX512
    printf("Векторні операції: векторні регістри ZMM 512-біт\n");
#else
    printf("Векторні операції: базовий набір SSE/AVX2\n");
#endif

    return 0;
}
