#pragma once
#include <cstdlib>

template <typename T>
T* allocate_guarded(std::size_t count) {
    T* ptr = static_cast<T*>(std::malloc(count * sizeof(T)));
    if (!ptr) {
#if defined(__cpp_exceptions)
        throw std::bad_alloc();
#else
        std::abort();
#endif
    }
    return ptr;
}
