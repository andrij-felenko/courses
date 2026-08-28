// newlib_stubs.c — слабкі заглушки системних викликів у newlib
#include <errno.h>
#include <stddef.h>

__attribute__((weak)) int _write(int file, const char* ptr, int len)
{
    // За замовчуванням вивід відсутній
    errno = ENOSYS;
    return -1;
}

__attribute__((weak)) void* _sbrk(ptrdiff_t incr)
{
    extern char _end; // Символ кінця секції BSS з лінкер-скрипта
    static char* heap_end = 0;
    char* prev_heap_end;

    if (heap_end == 0) {
        heap_end = &_end;
    }

    prev_heap_end = heap_end;
    heap_end += incr;
    return (void*)prev_heap_end;
}
