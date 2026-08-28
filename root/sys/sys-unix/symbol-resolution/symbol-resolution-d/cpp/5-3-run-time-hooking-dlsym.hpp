#define _GNU_SOURCE
#include <iostream>
#include <dlfcn.h>
#include <cstddef>

extern "C" void* malloc(std::size_t size) noexcept {
    using MallocFn = void* (*)(std::size_t);
    static MallocFn real_malloc = reinterpret_cast<MallocFn>(dlsym(RTLD_NEXT, "malloc"));
    
    /* Виклик оригінальної функції з libc */
    return real_malloc(size);
}
