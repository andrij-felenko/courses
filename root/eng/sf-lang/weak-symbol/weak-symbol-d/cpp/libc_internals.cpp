// libc_internals.cpp — спрощена схема експорту функцій на C++20
#include <cstddef>

extern "C" {

void* __libc_malloc(std::size_t size) noexcept
{
    return nullptr;
}

void* malloc(std::size_t size) noexcept [[gnu::weak, gnu::alias("__libc_malloc")]];

} // extern "C"
