// newlib_stubs.cpp — слабкі заглушки системних викликів на C++20
#include <cerrno>
#include <cstddef>

extern "C" {

[[gnu::weak]] int _write(int file, const char* ptr, int len) noexcept
{
    errno = ENOSYS;
    return -1;
}

[[gnu::weak]] void* _sbrk(std::ptrdiff_t incr) noexcept
{
    extern char _end;
    static char* heap_end = nullptr;

    if (heap_end == nullptr) {
        heap_end = &_end;
    }

    char* prev_heap_end = heap_end;
    heap_end += incr;
    return static_cast<void*>(prev_heap_end);
}

} // extern "C"
