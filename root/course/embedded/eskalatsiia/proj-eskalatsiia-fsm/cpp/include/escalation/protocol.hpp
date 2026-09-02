#pragma once

// Бінарний протокол запиту до оператора та відповіді станції.
// Кадр не довший за MTU радіомодема — пакувальник рахує байти сам.

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace esc {

using namespace std::chrono_literals;

inline constexpr std::size_t kMtuBytes   = 255;
inline constexpr std::size_t kMaxOptions = 4;
inline constexpr std::size_t kDescMax    = 31;
inline constexpr std::size_t kRoiMax     = 160;

inline constexpr std::byte    kMagicQuery{0xE5};
inline constexpr std::byte    kMagicReply{0xE6};
inline constexpr std::byte    kWireVersion{0x01};
inline constexpr std::uint8_t kFlagRoiDropped = 0x01;

enum class Trigger : std::uint8_t {
    None = 0,
    SceneAmbiguity,      // висока ентропія softmax, класи близькі
    PathExhausted,       // усі гілки costmap заблоковані
    BorderlineCritical,  // критичний об'єкт у діапазоні [0.4 .. 0.7]
    OddExcursion         // вихід за робочий домен (сонце, вітер, EKF)
};

struct Option {
    std::uint8_t     id{};
    std::string_view description{};  // підпис кнопки в інтерфейсі оператора
    float            estimated_cost_detour_m{};
    float            risk_score{};
};

// Запит у бортовій формі: нічим не володіє, лише дивиться на чужі буфери
struct Query {
    std::uint16_t             query_id{};
    std::chrono::milliseconds timestamp{0ms};
    std::chrono::milliseconds deadline{0ms};
    Trigger                   trigger{Trigger::None};
    std::uint8_t              flags{};
    std::array<float, 3>      position{};
    std::array<float, 3>      velocity{};
    std::span<const Option>   options{};
    std::span<const std::byte> roi{};
};

// Розібраний кадр на боці станції.
// УВАГА: description і roi дивляться всередину кадру — не переживають його буфер.
struct DecodedQuery {
    std::uint16_t                    query_id{};
    std::chrono::milliseconds        timestamp{0ms};
    std::chrono::milliseconds        deadline{0ms};
    Trigger                          trigger{Trigger::None};
    std::uint8_t                     flags{};
    std::array<float, 3>             position{};
    std::array<float, 3>             velocity{};
    std::array<Option, kMaxOptions>  options{};
    std::uint8_t                     options_count{};
    std::span<const std::byte>       roi{};

    [[nodiscard]] std::span<const Option> offered() const noexcept {
        return std::span<const Option>{options.data(), options_count};
    }
};

struct Reply {
    std::uint16_t             query_id{};
    std::uint8_t              option_id{};
    std::chrono::milliseconds gcs_time{0ms};
};

enum class WireError : std::uint8_t { Short, Magic, Version, Crc, Field, NoRoom };

[[nodiscard]] std::string_view to_string(WireError e) noexcept;

[[nodiscard]] std::uint16_t crc16(std::span<const std::byte> data) noexcept;

// Повертають підобласть out із записаним кадром
[[nodiscard]] std::expected<std::span<const std::byte>, WireError>
pack_query(const Query& q, std::span<std::byte> out) noexcept;

[[nodiscard]] std::expected<DecodedQuery, WireError>
unpack_query(std::span<const std::byte> frame) noexcept;

[[nodiscard]] std::expected<std::span<const std::byte>, WireError>
pack_reply(const Reply& r, std::span<std::byte> out) noexcept;

[[nodiscard]] std::expected<Reply, WireError>
unpack_reply(std::span<const std::byte> frame) noexcept;

}  // namespace esc
