// system_core.c — ядро системи зі слабким посиланням на діагностику
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// Оголошуємо зовнішню функцію слабким посиланням
extern __attribute__((weak)) void memory_audit_hook(const void* ptr, size_t size);

void* allocate_buffer(size_t size)
{
    void* ptr = malloc(size);
    if (!ptr) {
        return NULL;
    }

    // Перевірка наявності модуля в збірці
    if (memory_audit_hook != NULL) {
        memory_audit_hook(ptr, size);
    }

    return ptr;
}
