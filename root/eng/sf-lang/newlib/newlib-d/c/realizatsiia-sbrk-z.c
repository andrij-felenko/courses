#include <stdint.h>
#include <stddef.h>
#include <errno.h>

/* Символи, визначені компонувальником у linker script */
extern uint8_t _end;          /* Початок купи відразу за .bss */
extern uint8_t _estack;       /* Фізична вершина SRAM */
extern uint8_t __StackLimit;  /* Нижній ліміт виділеного простору стека */

/* Мінімальний резервний зазор між купою та стеком (наприклад, 1024 байти) */
#define STACK_SAFETY_MARGIN  1024U

/* Функція отримання поточного вказівника стека (ARM Cortex-M) */
static inline uintptr_t get_stack_pointer(void) {
    uintptr_t sp;
    __asm__ volatile ("mov %0, sp" : "=r" (sp));
    return sp;
}

void *_sbrk(ptrdiff_t incr) {
    static uint8_t *heap_end = NULL;
    uint8_t *prev_heap_end;

    /* Перша ініціалізація: встановлення початкової межі на символ _end */
    if (heap_end == NULL) {
        heap_end = &_end;
    }

    prev_heap_end = heap_end;

    /* Розрахунок потенційної нової межі купи */
    uint8_t *next_heap_end = heap_end + incr;
    uintptr_t current_sp = get_stack_pointer();

    /* Перевірка 1: Нова купа не повинна перетинати поточний SP із запасом безпеки */
    if ((uintptr_t)next_heap_end + STACK_SAFETY_MARGIN > current_sp) {
        errno = ENOMEM;
        return (void *)-1;
    }

    /* Перевірка 2: Нова купа не повинна виходити за статичну межу стека з linker script */
    if (next_heap_end > &__StackLimit) {
        errno = ENOMEM;
        return (void *)-1;
    }

    /* Виділення дозволено: фіксуємо нову межу */
    heap_end = next_heap_end;
    return (void *)prev_heap_end;
}
