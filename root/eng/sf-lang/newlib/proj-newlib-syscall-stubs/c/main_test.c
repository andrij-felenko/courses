/**
 * @file main_test.c
 * @brief Тестовий стенд діагностики Newlib (C99)
 */
#include "syscall_stubs.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

void run_newlib_diagnostics(void) {
    syscalls_init();

    printf("========================================\r\n");
    printf("     Newlib Embedded Diagnostics (C99)   \r\n");
    printf("========================================\r\n");

    /* Тест 1: Перевірка форматування чисел із рухомою комою */
    float voltage = 3.305f;
    double current = 0.0425;
    printf("[TEST 1] Float formatting: V=%.3f V, I=%.4f A\r\n", (double)voltage, current);

    /* Тест 2: Діагностика початкового стану пам'яті */
    sys_heap_stats_t stats;
    syscalls_get_heap_stats(&stats);
    printf("[TEST 2] Initial Heap State:\r\n");
    printf("  - Heap Start:   0x%08lX\r\n", (unsigned long)stats.heap_start_addr);
    printf("  - Heap Current: 0x%08lX\r\n", (unsigned long)stats.heap_current_addr);
    printf("  - Stack SP:     0x%08lX\r\n", (unsigned long)stats.stack_current_sp);
    printf("  - Free Margin:  %lu bytes\r\n", (unsigned long)stats.free_margin_bytes);

    /* Тест 3: Виділення та звільнення блоку */
    size_t test_size = 256;
    uint8_t *buf = (uint8_t *)malloc(test_size);
    if (buf != NULL) {
        memset(buf, 0xAA, test_size);
        printf("[TEST 3] malloc(%zu) SUCCESS at 0x%p\r\n", test_size, (void *)buf);
        free(buf);
        printf("[TEST 3] free() SUCCESS\r\n");
    } else {
        printf("[TEST 3] malloc(%zu) FAILED, errno=%d\r\n", test_size, errno);
    }

    /* Тест 4: Штучне вичерпання пам'яті (Out of Memory Stress Test) */
    printf("[TEST 4] Simulating Heap Exhaustion (Stress Test)...\r\n");
    size_t chunk_size = 4096;
    size_t total_allocated = 0;
    void *ptrs[64];
    int count = 0;

    while (count < 64) {
        void *p = malloc(chunk_size);
        if (p == NULL) {
            printf("  -> Heap exhausted as expected! errno=%d (ENOMEM=%d)\r\n", errno, ENOMEM);
            break;
        }
        ptrs[count++] = p;
        total_allocated += chunk_size;
    }

    printf("  -> Allocated %zu bytes in %d chunks before protection triggered\r\n", total_allocated, count);

    /* Звільнення виділених блоків */
    for (int i = 0; i < count; ++i) {
        free(ptrs[i]);
    }
    printf("  -> All test memory freed successfully.\r\n");

    /* Тест 5: Фінальні метрики */
    syscalls_get_heap_stats(&stats);
    printf("[TEST 5] Final Diagnostics:\r\n");
    printf("  - Total Failures Caught: %lu\r\n", (unsigned long)stats.allocation_failures);
    printf("  - Final Free Margin:     %lu bytes\r\n", (unsigned long)stats.free_margin_bytes);
    printf("========================================\r\n");
}
