#include <iostream>
#include <memory>
#include <span>
#include <cstdlib>
#include "config.h"

#if __has_include(<unistd.h>)
#include <unistd.h>
#endif

struct AlignedDeleter {
    void operator()(void* ptr) const noexcept {
        std::free(ptr);
    }
};

template <typename T>
std::unique_ptr<T[], AlignedDeleter> make_aligned_buffer(std::size_t count) {
    std::size_t bytes = count * sizeof(T);
    void* raw_ptr = nullptr;
#if defined(HAVE_POSIX_MEMALIGN)
    if (posix_memalign(&raw_ptr, 4096, bytes) != 0) {
        return nullptr;
    }
#elif defined(HAVE_ALIGNED_ALLOC)
    raw_ptr = std::aligned_alloc(4096, bytes);
#else
    raw_ptr = std::malloc(bytes);
#endif
    return std::unique_ptr<T[], AlignedDeleter>(static_cast<T*>(raw_ptr));
}
