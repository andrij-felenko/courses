/**
 * @file zero_alloc_log.c
 * @brief Безпечне форматування рядків без динамічної пам'яті (C99)
 */
#include "syscall_stubs.h"
#include <stdio.h>
#include <stdarg.h>

void log_telemetry_c(const char *tag, float voltage, float current) {
    char stack_buf[128];
    int len = snprintf(stack_buf, sizeof(stack_buf), 
                       "[%s] V=%.2f V, I=%.3f A\r\n", 
                       tag, (double)voltage, (double)current);

    if (len > 0) {
        /* Пряма передача в системний дескриптор stdout без проміжних викликів malloc */
        _write(1, stack_buf, (len < (int)sizeof(stack_buf)) ? len : (int)(sizeof(stack_buf) - 1));
    }
}
