/**
 * @file zero_alloc_log.hpp
 * @brief Безпечне логування на базі std::span та std::format_to_n (C++20)
 */
#pragma once

#include "syscall_stubs.hpp"
#include <span>
#include <array>
#include <format>
#include <string_view>

namespace embedded::log {

template <std::size_t BufferSize = 128>
class ZeroAllocLogger {
public:
    template <typename... Args>
    static void print(std::format_string<Args...> fmt, Args&&... args) noexcept {
        std::array<char, BufferSize> local_buffer{};
        
        // Форматування безпосередньо у статичний стековий масив
        const auto result = std::format_to_n(
            local_buffer.data(),
            local_buffer.size() - 1,
            fmt,
            std::forward<Args>(args)...
        );

        const auto written_count = std::min(
            static_cast<std::size_t>(result.size), 
            local_buffer.size() - 1
        );

        // Передача у Newlib syscall шар
        _write(1, local_buffer.data(), static_cast<int>(written_count));
    }
};

} // namespace embedded::log
