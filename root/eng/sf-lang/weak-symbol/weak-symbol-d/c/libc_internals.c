// libc_internals.c — спрощена схема експорту функцій у libc.so
#include <stddef.h>

void* __libc_malloc(size_t size)
{
    // Внутрішня реалізація системного алокатора
    return (void*)0;
}

// Експорт публічного слабкого символу malloc
void* malloc(size_t size) __attribute__((weak, alias("__libc_malloc")));
