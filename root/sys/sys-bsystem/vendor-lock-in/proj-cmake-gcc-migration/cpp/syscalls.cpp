// core/src/syscalls.cpp
#include <sys/stat.h>
#include <cerrno>
#include <cstdint>
#include <cstddef>
#include <span>

extern "C" {
    extern std::uint32_t _end;
    extern std::uint32_t _estack;

    void uart_send_char(char c) noexcept;

    void* _sbrk(std::ptrdiff_t incr) noexcept {
        static auto* heap_end = reinterpret_cast<std::uint8_t*>(&_end);
        auto* prev_heap_end = heap_end;

        const auto* stack_limit = reinterpret_cast<std::uint8_t*>(&_estack) - 0x400;
        if (heap_end + incr > stack_limit) {
            errno = ENOMEM;
            return reinterpret_cast<void*>(-1);
        }

        heap_end += incr;
        return reinterpret_cast<void*>(prev_heap_end);
    }

    int _write(int file, const char *ptr, int len) noexcept {
        (void)file;
        std::span<const char> buffer(ptr, static_cast<std::size_t>(len));
        for (char ch : buffer) {
            uart_send_char(ch);
        }
        return len;
    }

    int _read(int, char*, int) noexcept { return 0; }
    int _close(int) noexcept { return -1; }
    int _fstat(int, struct stat *st) noexcept { st->st_mode = S_IFCHR; return 0; }
    int _isatty(int) noexcept { return 1; }
    int _lseek(int, int, int) noexcept { return 0; }
}
