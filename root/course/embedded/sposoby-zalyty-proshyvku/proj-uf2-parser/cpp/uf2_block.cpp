#include "uf2_block.hpp"

#include <cstring>

namespace uf2 {
namespace {

// Зсуви полів у секторі. Читаємо через memcpy, а не через packed-структуру:
// буфер USB-стека не зобов'язаний бути вирівняний, а компілятор має право
// це припустити для reinterpret_cast.
enum Offset : std::size_t {
    OffMagicStart0 = 0,
    OffMagicStart1 = 4,
    OffFlags       = 8,
    OffTargetAddr  = 12,
    OffPayloadSize = 16,
    OffBlockNo     = 20,
    OffNumBlocks   = 24,
    OffFamilyId    = 28,
    OffData        = 32,
    OffMagicEnd    = 508,
};

[[nodiscard]] std::uint32_t readLe32(std::span<const std::uint8_t> sector, std::size_t at) noexcept
{
    std::uint32_t value{};
    std::memcpy(&value, sector.data() + at, sizeof(value)); // ядро little-endian, як і формат
    return value;
}

} // namespace

std::expected<BlockInfo, ParseError>
parseBlock(std::span<const std::uint8_t> sector,
           std::uint32_t                 expectedFamilyId,
           FlashRegion                   flash) noexcept
{
    // 1. Неповний сектор читати не можна: magicEnd лежить в останніх чотирьох байтах.
    if (sector.size() < BlockSize) {
        return std::unexpected(ParseError::BadSectorSize);
    }

    if (readLe32(sector, OffMagicStart0) != MagicStart0 ||
        readLe32(sector, OffMagicStart1) != MagicStart1) {
        return std::unexpected(ParseError::BadMagicStart);
    }
    if (readLe32(sector, OffMagicEnd) != MagicEnd) {
        return std::unexpected(ParseError::BadMagicEnd);
    }

    const std::uint32_t flags      = readLe32(sector, OffFlags);
    const std::uint32_t blockNo    = readLe32(sector, OffBlockNo);
    const std::uint32_t numBlocks  = readLe32(sector, OffNumBlocks);

    if (numBlocks == 0) {
        return std::unexpected(ParseError::TotalBlocksZero);
    }
    if (blockNo >= numBlocks) {
        return std::unexpected(ParseError::BlockIndexRange);
    }

    // Валідний блок, який до основної Flash не має стосунку: віддаємо порожній payload.
    if ((flags & (FlagNotMainFlash | FlagFileContainer)) != 0) {
        return BlockInfo{.targetAddress = 0,
                         .blockIndex    = blockNo,
                         .totalBlocks   = numBlocks,
                         .payload       = {}};
    }

    // 2. Сімейство кристала: бінарник від сусідньої плати сюди не поїде.
    if ((flags & FlagFamilyId) != 0 && readLe32(sector, OffFamilyId) != expectedFamilyId) {
        return std::unexpected(ParseError::FamilyMismatch);
    }

    // 3. Довжина навантаження: захист від виходу за межі data[476].
    const std::uint32_t payloadSize = readLe32(sector, OffPayloadSize);
    if (payloadSize == 0 || payloadSize > MaxPayload) {
        return std::unexpected(ParseError::PayloadTooLarge);
    }

    // 4. Діапазон адрес у 64 бітах: інакше targetAddr коло 0xFFFFFFFF переповнює
    // суму, вона стає маленькою — і перевірка пропускає запис у чужу область.
    const std::uint32_t targetAddr = readLe32(sector, OffTargetAddr);
    const std::uint64_t lo  = targetAddr;
    const std::uint64_t hi  = lo + payloadSize;
    const std::uint64_t end = std::uint64_t{flash.start} + flash.size;
    if (lo < flash.start || hi > end) {
        return std::unexpected(ParseError::InvalidAddress);
    }

    return BlockInfo{.targetAddress = targetAddr,
                     .blockIndex    = blockNo,
                     .totalBlocks   = numBlocks,
                     .payload       = sector.subspan(OffData, payloadSize)};
}

std::string_view describe(ParseError e) noexcept
{
    switch (e) {
    case ParseError::BadSectorSize:   return "неповний сектор";
    case ParseError::BadMagicStart:   return "немає початкових сигнатур";
    case ParseError::BadMagicEnd:     return "немає кінцевої сигнатури";
    case ParseError::FamilyMismatch:  return "чуже сімейство кристала";
    case ParseError::PayloadTooLarge: return "хибний payloadSize";
    case ParseError::InvalidAddress:  return "адреса поза межами Flash";
    case ParseError::TotalBlocksZero: return "numBlocks == 0";
    case ParseError::BlockIndexRange: return "blockNo поза numBlocks";
    }
    return "невідома відмова";
}

} // namespace uf2
