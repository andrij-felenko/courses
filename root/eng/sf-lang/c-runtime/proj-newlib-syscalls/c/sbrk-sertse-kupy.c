#include <errno.h>
#include <sys/types.h>

extern char _end;            // символ із лінкер-скрипта: кінець .bss = початок купи
extern char _estack;         // вершина RAM (низ стека) — теж із лінкер-скрипта

static char *heap_end = 0;

void *_sbrk(ptrdiff_t increment) {
    if (heap_end == 0)
        heap_end = &_end;                 // перший виклик: купа стартує за .bss

    char *prev = heap_end;
    char *next = heap_end + increment;

    // межа: не дати купі врости у стек (лишаємо запас під поточний кадр)
    char *limit = &_estack - 512;         // 512 Б оберегу під стек
    if (next > limit) {
        errno = ENOMEM;                   // пам'ять скінчилась
        return (void *) -1;               // malloc побачить -1 → поверне NULL
    }

    heap_end = next;
    return prev;                          // стара межа = адреса нового блоку
}
