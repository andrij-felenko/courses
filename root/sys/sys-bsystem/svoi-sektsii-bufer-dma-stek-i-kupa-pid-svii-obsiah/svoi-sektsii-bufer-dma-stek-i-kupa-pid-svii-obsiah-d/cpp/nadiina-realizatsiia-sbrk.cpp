#include <cstdint>
#include <cstddef>
#include <cerrno>

extern "C" {
    extern std::uint8_t end;
    extern std::uint8_t _estack;
    extern std::uint32_t _Min_Stack_Size;

    void* _sbrk(std::ptrdiff_t incr) noexcept;
}

namespace sys {

[[nodiscard]] inline std::uintptr_t read_current_msp() noexcept {
    std::uintptr_t sp_value;
    asm volatile("mrs %0, msp" : "=r"(sp_value));
    return sp_value;
}

class CollisionSafeHeap {
public:
    static void* allocate(std::ptrdiff_t incr) noexcept {
        static std::uint8_t* heap_end = &end;

        auto* prev_heap_end = heap_end;
        auto* next_heap_end = heap_end + incr;

        const auto active_sp = read_current_msp();
        const auto* stack_boundary = &_estack - reinterpret_cast<std::uintptr_t>(&_Min_Stack_Size);

        // Перевірка обох бар'єрів
        if ((next_heap_end > reinterpret_cast<const std::uint8_t*>(active_sp)) || 
            (next_heap_end > stack_boundary)) {
            errno = ENOMEM;
            return reinterpret_cast<void*>(-1);
        }

        heap_end = next_heap_end;
        return prev_heap_end;
    }
};

} // namespace sys

extern "C" void* _sbrk(std::ptrdiff_t incr) noexcept {
    return sys::CollisionSafeHeap::allocate(incr);
}
