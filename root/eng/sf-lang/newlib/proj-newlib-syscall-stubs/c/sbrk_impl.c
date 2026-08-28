/**
 * @file sbrk_impl.c
 * @brief Реалізація захищеного виділення пам'яті для Newlib (C99)
 */
#include "syscall_stubs.h"
#include <errno.h>
#include <sys/reent.h>

/* Символи, визначені компонувальником у linker script */
extern uint8_t _end;          /**< Початок купи після секції .bss */
extern uint8_t __StackLimit;  /**< Нижня границя виділеного стека */
extern uint8_t _estack;       /**< Фізична вершина пам'яті SRAM */

static uint8_t *g_heap_current = NULL;
static uint32_t g_alloc_failures_count = 0;

/**
 * @brief Зчитування поточного значення апаратного вказівника стека SP
 */
static inline uintptr_t read_current_stack_pointer(void) {
    uintptr_t sp_val;
    __asm__ volatile ("mov %0, sp" : "=r" (sp_val));
    return sp_val;
}

void *_sbrk_r(struct _reent *r, ptrdiff_t incr) {
    uint8_t *prev_heap_end;
    uint8_t *next_heap_end;
    uintptr_t current_sp;

    /* Перший виклик: ініціалізація початкового покажчика купи */
    if (g_heap_current == NULL) {
        g_heap_current = &_end;
    }

    prev_heap_end = g_heap_current;

    /* Запит на отримання поточної межі без виділення (incr == 0) */
    if (incr == 0) {
        return (void *)prev_heap_end;
    }

    next_heap_end = g_heap_current + incr;
    current_sp = read_current_stack_pointer();

    /* 1. Перевірка на від'ємний покажчик (стиснення нижче початкової точки _end) */
    if (next_heap_end < &_end) {
        r->_errno = EINVAL;
        g_alloc_failures_count++;
        return (void *)-1;
    }

    /* 2. Перевірка динамічного перекриття з активним стеком ядра */
    if (((uintptr_t)next_heap_end + SYS_STACK_SAFETY_MARGIN_BYTES) > current_sp) {
        r->_errno = ENOMEM;
        g_alloc_failures_count++;
        return (void *)-1;
    }

    /* 3. Перевірка статичного ліміту із скрипта компонувальника */
    if (next_heap_end > &__StackLimit) {
        r->_errno = ENOMEM;
        g_alloc_failures_count++;
        return (void *)-1;
    }

    /* Усі перевірки пройдено успішно: фіксуємо нову межу купи */
    g_heap_current = next_heap_end;
    return (void *)prev_heap_end;
}

/* Стандартна нереентрабельна заглушка транслюється у _sbrk_r */
void *_sbrk(ptrdiff_t incr) {
    return _sbrk_r(_impure_ptr, incr);
}

void syscalls_get_heap_stats(sys_heap_stats_t *stats) {
    if (stats == NULL) return;

    uintptr_t current_sp = read_current_stack_pointer();
    uint8_t *cur = (g_heap_current != NULL) ? g_heap_current : &_end;

    stats->heap_start_addr = (uint32_t)(uintptr_t)&_end;
    stats->heap_current_addr = (uint32_t)(uintptr_t)cur;
    stats->heap_limit_addr = (uint32_t)(uintptr_t)&__StackLimit;
    stats->stack_current_sp = (uint32_t)current_sp;
    stats->allocated_bytes = (uint32_t)(cur - &_end);
    stats->allocation_failures = g_alloc_failures_count;

    if (current_sp > (uintptr_t)cur) {
        stats->free_margin_bytes = (uint32_t)(current_sp - (uintptr_t)cur);
    } else {
        stats->free_margin_bytes = 0;
    }
}
