/**
 * @file syscall_stubs.hpp
 * @brief C++20 інтерфейс системних заглушок Newlib для вбудованих систем
 */
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <sys/stat.h>
#include <sys/types.h>

namespace embedded::sys {

inline constexpr std::size_t StackSafetyMarginBytes = 1024;
inline constexpr std::size_t UartTxBufferSize = 512;
inline constexpr std::size_t UartRxBufferSize = 128;

/**
 * @brief Метрики розподілу пам'яті SRAM
 */
struct HeapMemoryMetrics {
    std::uintptr_t heap_start_addr{0};
    std::uintptr_t heap_current_addr{0};
    std::uintptr_t heap_limit_addr{0};
    std::uintptr_t current_sp{0};
    std::size_t allocated_bytes{0};
    std::size_t free_margin_bytes{0};
    std::size_t allocation_failures{0};
};

class SyscallManager {
public:
    static void initialize() noexcept;
    static auto get_metrics() noexcept -> HeapMemoryMetrics;
    static void putc_immediate(char c) noexcept;
    static void flush_stdout() noexcept;

    SyscallManager() = delete;
};

} // namespace embedded::sys
