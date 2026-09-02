// Бінарний контракт UF2: константи формату, причини відмови й розбір сектора.
#pragma once

#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace uf2 {

inline constexpr std::uint32_t MagicStart0 = 0x0A324655U; // "UF2\n"
inline constexpr std::uint32_t MagicStart1 = 0x9E5D5157U;
inline constexpr std::uint32_t MagicEnd    = 0x0AB16414U;

inline constexpr std::uint32_t FlagNotMainFlash = 0x00000001U;
inline constexpr std::uint32_t FlagFileContainer = 0x00001000U;
inline constexpr std::uint32_t FlagFamilyId      = 0x00002000U;

inline constexpr std::size_t BlockSize  = 512; // логічний сектор емульованого диска
inline constexpr std::size_t MaxPayload = 476;

enum class ParseError : std::uint8_t {
    BadSectorSize,
    BadMagicStart,
    BadMagicEnd,
    FamilyMismatch,
    PayloadTooLarge,
    InvalidAddress,
    TotalBlocksZero,
    BlockIndexRange,
};

// Межі області, куди взагалі дозволено писати.
struct FlashRegion {
    std::uint32_t start;
    std::uint32_t size;
};

// Розібраний блок. payload дивиться всередину переданого сектора — копії немає,
// тож span живе рівно доти, доки живий буфер USB-стека.
struct BlockInfo {
    std::uint32_t            targetAddress;
    std::uint32_t            blockIndex;
    std::uint32_t            totalBlocks;
    std::span<const std::uint8_t> payload; // порожній ⇒ блок валідний, але не для Flash
};

// Порожній payload означає «пропустити»: блок позначено як не-для-основної-Flash.
[[nodiscard]] std::expected<BlockInfo, ParseError>
parseBlock(std::span<const std::uint8_t> sector,
           std::uint32_t                 expectedFamilyId,
           FlashRegion                   flash) noexcept;

// true, якщо сектор просто не є блоком UF2 (службовий запис файлової системи).
[[nodiscard]] constexpr bool isForeignSector(ParseError e) noexcept
{
    return e == ParseError::BadMagicStart || e == ParseError::BadMagicEnd;
}

[[nodiscard]] std::string_view describe(ParseError e) noexcept;

} // namespace uf2
