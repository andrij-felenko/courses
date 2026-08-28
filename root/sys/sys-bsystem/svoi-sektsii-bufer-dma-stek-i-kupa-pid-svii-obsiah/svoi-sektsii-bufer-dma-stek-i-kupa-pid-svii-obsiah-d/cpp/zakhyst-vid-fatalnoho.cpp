// НАЇВНА І НЕБЕЗПЕЧНА РЕАЛІЗАЦІЯ — НЕ ВИКОРИСТОВУВАТИ
extern "C" {
    extern char end;

    void* _sbrk_unsafe_cpp(std::ptrdiff_t incr) noexcept {
        static char* heap_end = &end;
        char* prev_heap_end = heap_end;
        heap_end += incr;
        return prev_heap_end;
    }
}
