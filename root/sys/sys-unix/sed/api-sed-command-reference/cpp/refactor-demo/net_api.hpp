// net_api.hpp — сучасний інтерфейс того самого мережевого стека.
//
// Це «стало» для рецепта масової міграції: пара «покажчик, довжина» згорнута
// в span і більше не може розійтися, два безіменні числа в хвості стали
// іменованим агрегатом, а помилка — не -1 з errno, а std::expected.
#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <system_error>

namespace net {

inline constexpr std::uint32_t flag_urgent  = 0x01u;
inline constexpr std::uint32_t flag_nodelay = 0x02u;

class net_conn;

// Іменовані поля замість позиційних чисел: переставити flags і timeout_ms
// місцями тепер неможливо навіть друкарською помилкою.
struct net_send_opts {
    std::uint32_t flags{0};
    std::uint32_t timeout_ms{0};
};

auto net_send_packet(net_conn& conn, std::span<const std::uint8_t> payload,
                     net_send_opts opts) -> std::expected<std::size_t, std::error_code>;

}  // namespace net
