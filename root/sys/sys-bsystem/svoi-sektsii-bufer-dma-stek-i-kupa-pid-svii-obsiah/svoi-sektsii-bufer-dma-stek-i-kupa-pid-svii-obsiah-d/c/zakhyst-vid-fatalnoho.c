/* НАЇВНА І НЕБЕЗПЕЧНА РЕАЛІЗАЦІЯ — НЕ ВИКОРИСТОВУВАТИ */
void* _sbrk_unsafe(ptrdiff_t incr) {
    extern char end; /* Символ кінця .bss зі скрипта компонувальника */
    static char *heap_end = NULL;
    char *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = &end;
    }
    prev_heap_end = heap_end;
    heap_end += incr;
    return (void*)prev_heap_end;
}
