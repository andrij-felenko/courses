void* operator new(std::size_t size) {
    if (size == 0) size = 1;
    void* p = malloc(size);
    if (!p) {
        #if __cpp_exceptions
        throw std::bad_alloc();
        #else
        std::abort(); // На вбудованих системах без винятків
        #endif
    }
    return p;
}

void operator delete(void* p) noexcept {
    if (p) free(p);
}
