#pragma once

#include <array>
#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>
#include <string_view>
#include <vector>

#include "spi_link.hpp"

namespace flash {

inline constexpr std::uint8_t kCmdReadSfdp = 0x5A;
inline constexpr std::size_t  kSfdpMaxDwords = 20;  /* JESD216D має 20; більше не читаємо */

enum class SfdpError {
    BadSignature,   /* заголовок не починається з 'S' 'F' 'D' 'P' */
    NoBasicTable,   /* серед заголовків параметрів немає базової таблиці */
    Truncated       /* таблиця коротша за обов'язкові поля */
};

[[nodiscard]] std::string_view describe(SfdpError error) noexcept;

/* Як саме на цьому кристалі вмикається біт Quad Enable — поле QER із DWORD15. */
enum class QuadEnable : std::uint8_t {
    None            = 0,
    Sr2Bit1Write01  = 1,
    Sr1Bit6Write01  = 2,
    Sr2Bit7Cmd3E    = 3,
    Sr2Bit1Read35   = 4,
    Sr2Bit1Write31  = 5,
    Unknown         = 0xFF
};

[[nodiscard]] std::string_view describe(QuadEnable scheme) noexcept;

struct EraseType {
    std::uint8_t              opcode{};
    std::uint32_t             size_bytes{};
    std::chrono::milliseconds typical{};
};

struct FastRead {
    std::uint8_t opcode{};
    std::uint8_t dummy_clocks{};
    std::uint8_t mode_clocks{};
};

struct Parameters {
    std::uint8_t  major{};
    std::uint8_t  minor{};
    std::size_t   dwords{};             /* фактично прочитана довжина таблиці */
    std::uint8_t  address_bytes{3};
    bool          four_byte_capable{false};
    std::uint64_t density_bits{};
    std::uint64_t density_bytes{};
    std::uint32_t page_size{256};
    std::optional<FastRead> read_1_4_4;
    std::optional<FastRead> read_1_1_4;
    QuadEnable    quad_enable{QuadEnable::Unknown};
    std::vector<EraseType> erase_types;
};

[[nodiscard]] std::expected<Parameters, SfdpError> read_parameters(SpiLink &link);

}  // namespace flash
