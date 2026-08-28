#include <stdint.h>
#include <stddef.h>
#include <errno.h>

#undef errno
extern int errno;

/* Символи зі скрипта компонувальника */
extern uint8_t end;
extern uint8_t _estack;
extern uint32_t _Min_Stack_Size;

/* Читання поточного значення апаратного покажчика стека (MSP) */
static inline uint32_t read_current_msp(void) {
    uint32_t result;
    __asm volatile("mrs %0, msp" : "=r"(result));
    return result;
}

void* _sbrk(ptrdiff_t incr) {
    static uint8_t *heap_end = NULL;
    uint8_t *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = &end;
    }

    prev_heap_end = heap_end;
    uint8_t *next_heap_end = heap_end + incr;

    /* Зчитування поточного динамічного стека */
    uint32_t current_sp = read_current_msp();

    /* Розрахунок статичної межі безпеки під стек */
    uint8_t *stack_boundary = (uint8_t*)(&_estack) - (uint32_t)(&_Min_Stack_Size);

    /* 
     * Перевірка двох умов:
     * 1. Чи не наздогнала купа поточний активний стек SP
     * 2. Чи не зайшла купа в гарантований резерв стека переривань
     */
    if ((next_heap_end > (uint8_t*)current_sp) || (next_heap_end > stack_boundary)) {
        errno = ENOMEM;
        return (void*)-1;
    }

    heap_end = next_heap_end;
    return (void*)prev_heap_end;
}
