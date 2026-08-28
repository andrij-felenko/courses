#include <new>
#include <cstdlib>

// Базові форми
void* operator new(std::size_t size) {
    if (size == 0) size = 1;
    while (void* p = std::malloc(size)) {
        return p;
    }
    if (auto h = std::get_new_handler()) { h(); return operator new(size); }
    throw std::bad_alloc();
}

void* operator new[](std::size_t size) { return ::operator new(size); }

void operator delete(void* ptr) noexcept { std::free(ptr); }
void operator delete[](void* ptr) noexcept { ::operator delete(ptr); }

// Sized forms (C++14)
void operator delete(void* ptr, std::size_t) noexcept { ::operator delete(ptr); }
void operator delete[](void* ptr, std::size_t) noexcept { ::operator delete[](ptr); }

// Aligned forms (C++17)
void* operator new(std::size_t size, std::align_val_t al) {
    if (size == 0) size = 1;
    std::size_t align = static_cast<std::size_t>(al);
    void* ptr = nullptr;
#if defined(_MSC_VER)
    ptr = _aligned_malloc(size, align);
#else
    if (posix_memalign(&ptr, align, size) != 0) ptr = nullptr;
#endif
    if (ptr) return ptr;
    if (auto h = std::get_new_handler()) { h(); return operator new(size, al); }
    throw std::bad_alloc();
}

void* operator new[](std::size_t size, std::align_val_t al) { return ::operator new(size, al); }

void operator delete(void* ptr, std::align_val_t) noexcept {
#if defined(_MSC_VER)
    _aligned_free(ptr);
#else
    std::free(ptr);
#endif
}

void operator delete[](void* ptr, std::align_val_t al) noexcept { ::operator delete(ptr, al); }
void operator delete(void* ptr, std::size_t, std::align_val_t al) noexcept { ::operator delete(ptr, al); }
void operator delete[](void* ptr, std::size_t, std::align_val_t al) noexcept { ::operator delete[](ptr, al); }
