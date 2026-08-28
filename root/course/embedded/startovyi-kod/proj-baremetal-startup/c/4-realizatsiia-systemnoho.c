/* Реалізація системного виклику _sbrk мовою C */
#include <errno.h>
#include <stdint.h>

extern uint32_t _end;
extern uint32_t _estack;

void *_sbrk(ptrdiff_t incr) {
    static uint8_t *heap_end = NULL;
    uint8_t *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = (uint8_t *)&_end;
    }

    prev_heap_end = heap_end;

    /* Перевірка на зіткнення купи зі стеком */
    if ((uint32_t)(heap_end + incr) > ((uint32_t)&_estack - 1024)) {
        errno = ENOMEM;
        return (void *)-1;
    }

    heap_end += incr;
    return (void *)prev_heap_end;
}
