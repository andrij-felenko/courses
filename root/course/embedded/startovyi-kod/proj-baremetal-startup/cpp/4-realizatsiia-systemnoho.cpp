#include <cstdint>
#include <cstddef>
#include <cerrno>

/* Реалізація системного виклику _sbrk мовою C++ */
extern "C" {
    extern std::uint32_t _end;
    extern std::uint32_t _estack;

    void* _sbrk(std::ptrdiff_t incr) noexcept {
        static auto* heap_end = reinterpret_cast<std::uint8_t*>(&_end);
        auto* const prev_heap_end = heap_end;

        const auto current_sp = reinterpret_cast<std::uintptr_t>(heap_end + incr);
        const auto stack_limit = reinterpret_cast<std::uintptr_t>(&_estack) - 1024UL;

        if (current_sp > stack_limit) {
            errno = ENOMEM;
            return reinterpret_cast<void*>(-1);
        }

        heap_end += incr;
        return reinterpret_cast<void*>(prev_heap_end);
    }
}
