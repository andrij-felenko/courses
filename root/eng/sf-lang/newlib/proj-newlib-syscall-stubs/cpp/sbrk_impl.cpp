/**
 * @file sbrk_impl.cpp
 * @brief Реалізація захищеного виділення пам'яті для Newlib (C++20)
 */
#include "syscall_stubs.hpp"
#include <cerrno>
#include <sys/reent.h>

extern "C" {
    extern std::uint8_t _end;
    extern std::uint8_t __StackLimit;
    extern std::uint8_t _estack;
}

namespace embedded::sys {

namespace {

std::uint8_t* g_heap_current{nullptr};
std::size_t g_alloc_failures{0};

[[nodiscard]] inline auto read_sp() noexcept -> std::uintptr_t {
    std::uintptr_t sp_val{};
    asm volatile ("mov %0, sp" : "=r" (sp_val));
    return sp_val;
}

} // namespace

auto SyscallManager::get_metrics() noexcept -> HeapMemoryMetrics {
    const auto current_sp = read_sp();
    auto* cur = (g_heap_current != nullptr) ? g_heap_current : &_end;

    HeapMemoryMetrics metrics{};
    metrics.heap_start_addr = reinterpret_cast<std::uintptr_t>(&_end);
    metrics.heap_current_addr = reinterpret_cast<std::uintptr_t>(cur);
    metrics.heap_limit_addr = reinterpret_cast<std::uintptr_t>(&__StackLimit);
    metrics.current_sp = current_sp;
    metrics.allocated_bytes = static_cast<std::size_t>(cur - &_end);
    metrics.allocation_failures = g_alloc_failures;

    if (current_sp > reinterpret_cast<std::uintptr_t>(cur)) {
        metrics.free_margin_bytes = current_sp - reinterpret_cast<std::uintptr_t>(cur);
    } else {
        metrics.free_margin_bytes = 0;
    }

    return metrics;
}

} // namespace embedded::sys

extern "C" {

auto _sbrk_r(struct _reent *r, std::ptrdiff_t incr) noexcept -> void * {
    using namespace embedded::sys;

    if (g_heap_current == nullptr) {
        g_heap_current = &_end;
    }

    auto *prev_end = g_heap_current;
    if (incr == 0) {
        return reinterpret_cast<void *>(prev_end);
    }

    auto *next_end = g_heap_current + incr;
    const auto current_sp = read_sp();

    // 1. Захист від стиснення купи нижче базової секції .bss
    if (next_end < &_end) {
        r->_errno = EINVAL;
        g_alloc_failures++;
        return reinterpret_cast<void *>(-1);
    }

    // 2. Захист від накладання на активний стек ядра з зазором безпеки
    if ((reinterpret_cast<std::uintptr_t>(next_end) + StackSafetyMarginBytes) > current_sp) {
        r->_errno = ENOMEM;
        g_alloc_failures++;
        return reinterpret_cast<void *>(-1);
    }

    // 3. Захист від перевищення ліміту linker script
    if (next_end > &__StackLimit) {
        r->_errno = ENOMEM;
        g_alloc_failures++;
        return reinterpret_cast<void *>(-1);
    }

    g_heap_current = next_end;
    return reinterpret_cast<void *>(prev_end);
}

auto _sbrk(std::ptrdiff_t incr) noexcept -> void * {
    return _sbrk_r(_impure_ptr, incr);
}

} // extern "C"
