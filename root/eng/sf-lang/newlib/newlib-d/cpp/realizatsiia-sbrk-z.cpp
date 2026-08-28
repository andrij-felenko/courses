#include <cstdint>
#include <cstddef>
#include <cerrno>

extern "C" {
    extern std::uint8_t _end;
    extern std::uint8_t _estack;
    extern std::uint8_t __StackLimit;
}

namespace sys {

constexpr std::size_t StackSafetyMargin = 1024;

[[nodiscard]] inline auto get_stack_pointer() noexcept -> std::uintptr_t {
    std::uintptr_t sp{};
    asm volatile ("mov %0, sp" : "=r" (sp));
    return sp;
}

} // namespace sys

extern "C" auto _sbrk(std::ptrdiff_t incr) noexcept -> void * {
    static std::uint8_t *heap_end{nullptr};

    if (heap_end == nullptr) {
        heap_end = &_end;
    }

    auto *prev_heap_end = heap_end;
    auto *next_heap_end = heap_end + incr;
    const auto current_sp = sys::get_stack_pointer();

    // Перевірка колізії з динамічним стеком процесора
    if (reinterpret_cast<std::uintptr_t>(next_heap_end) + sys::StackSafetyMargin > current_sp) {
        errno = ENOMEM;
        return reinterpret_cast<void *>(-1);
    }

    // Перевірка перевищення ліміту скрипта компонування
    if (next_heap_end > &__StackLimit) {
        errno = ENOMEM;
        return reinterpret_cast<void *>(-1);
    }

    heap_end = next_heap_end;
    return reinterpret_cast<void *>(prev_heap_end);
}
