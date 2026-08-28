#pragma once

#if defined(__has_cpp_attribute)
    #if __has_cpp_attribute(no_unique_address) >= 201803L
        #define COMPAT_NO_UNIQUE_ADDRESS [[no_unique_address]]
    #else
        #define COMPAT_NO_UNIQUE_ADDRESS
    #endif
#else
    #define COMPAT_NO_UNIQUE_ADDRESS
#endif

template <typename Allocator, typename T>
struct CompressedBucket {
    COMPAT_NO_UNIQUE_ADDRESS Allocator alloc;
    T* data;
    std::size_t size;
};
