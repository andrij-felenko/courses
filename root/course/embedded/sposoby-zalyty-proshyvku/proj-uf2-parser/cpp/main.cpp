#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace uf2 {

inline constexpr uint32_t MagicStart0   = 0x0A324655UL;  // "UF2\n"
inline constexpr uint32_t MagicStart1   = 0x9E5D5157UL;
inline constexpr uint32_t MagicEnd      = 0x0AB16414UL;
inline constexpr uint32_t FlagFamilyId  = 0x00002000UL;
inline constexpr size_t   BlockSize     = 512;
inline constexpr size_t   MaxPayload    = 476;

enum class ParseError : uint8_t {
    BadBufferLength,
    BadMagicStart,
    BadMagicEnd,
    FamilyMismatch,
    PayloadTooLarge,
    InvalidAddress,
    TotalBlocksZero
};

struct BlockInfo {
    uint32_t targetAddress;
    uint32_t blockIndex;
    uint32_t totalBlocks;
    std::span<const uint8_t> payload;
};

struct [[gnu::packed]] RawBlock {
    uint32_t magicStart0;
    uint32_t magicStart1;
    uint32_t flags;
    uint32_t targetAddr;
    uint32_t payloadSize;
    uint32_t blockNo;
    uint32_t numBlocks;
    uint32_t familyId;
    uint8_t  data[MaxPayload];
    uint32_t magicEnd;
};

[[nodiscard]] std::expected<BlockInfo, ParseError> parseAndValidateBlock(
    std::span<const uint8_t, BlockSize> sector,
    uint32_t expectedFamilyId,
    uint32_t flashStartAddr,
    uint32_t flashSizeBytes
) noexcept {
    const auto* blk = reinterpret_cast<const RawBlock*>(sector.data());

    if (blk->magicStart0 != MagicStart0 || blk->magicStart1 != MagicStart1) {
        return std::unexpected(ParseError::BadMagicStart);
    }

    if (blk->magicEnd != MagicEnd) {
        return std::unexpected(ParseError::BadMagicEnd);
    }

    if ((blk->flags & FlagFamilyId) != 0) {
        if (blk->familyId != expectedFamilyId) {
            return std::unexpected(ParseError::FamilyMismatch);
        }
    }

    if (blk->payloadSize == 0 || blk->payloadSize > MaxPayload) {
        return std::unexpected(ParseError::PayloadTooLarge);
    }

    if (blk->numBlocks == 0) {
        return std::unexpected(ParseError::TotalBlocksZero);
    }

    const uint32_t flashEndAddr = flashStartAddr + flashSizeBytes;
    if (blk->targetAddr < flashStartAddr ||
        (blk->targetAddr + blk->payloadSize) > flashEndAddr) {
        return std::unexpected(ParseError::InvalidAddress);
    }

    return BlockInfo{
        .targetAddress = blk->targetAddr,
        .blockIndex = blk->blockNo,
        .totalBlocks = blk->numBlocks,
        .payload = std::span<const uint8_t>(blk->data, blk->payloadSize)
    };
}

} // namespace uf2
