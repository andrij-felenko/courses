#include <cstdint>
#include <vector>
#include <span>
#include <array>
#include <optional>
#include <expected>
#include <algorithm>

namespace storage {

constexpr size_t PageSize        = 4096;
constexpr size_t OobSize         = 224;
constexpr size_t PagesPerBlock   = 64;
constexpr size_t TotalBlocks     = 1024;
constexpr size_t ReservedBlocks  = 64;
constexpr size_t UserBlocks      = TotalBlocks - ReservedBlocks;

constexpr size_t OobMarkerOffset = 0;
constexpr uint8_t GoodMarker     = 0xFF;

enum class BlockState : uint8_t {
    FactoryBad = 0x00,
    Reserved   = 0x01,
    GrownBad   = 0x02,
    Good       = 0x03
};

enum class BbmError {
    DeviceIoFailure,
    ReservePoolExhausted,
    OutOfBounds
};

struct RemapRule {
    uint16_t badPhysBlock;
    uint16_t sparePhysBlock;
    bool active{true};
};

class FlashHardwareInterface {
public:
    virtual ~FlashHardwareInterface() = default;
    virtual bool readOob(uint32_t block, uint32_t page, std::span<uint8_t, OobSize> oob) = 0;
    virtual bool readPage(uint32_t block, uint32_t page, std::span<uint8_t, PageSize> data, std::span<uint8_t, OobSize> oob) = 0;
    virtual bool writePage(uint32_t block, uint32_t page, std::span<const uint8_t, PageSize> data, std::span<const uint8_t, OobSize> oob) = 0;
    virtual bool eraseBlock(uint32_t block) = 0;
};

class BadBlockTableManager {
public:
    BadBlockTableManager() {
        bitmap_.fill(0xFF);
    }

    [[nodiscard]] BlockState getBlockState(uint16_t block) const {
        if (block >= TotalBlocks) return BlockState::FactoryBad;
        const size_t byteIdx = block / 4;
        const size_t bitShift = (block % 4) * 2;
        return static_cast<BlockState>((bitmap_[byteIdx] >> bitShift) & 0x03);
    }

    void setBlockState(uint16_t block, BlockState state) {
        if (block >= TotalBlocks) return;
        const size_t byteIdx = block / 4;
        const size_t bitShift = (block % 4) * 2;
        bitmap_[byteIdx] &= ~(0x03 << bitShift);
        bitmap_[byteIdx] |= (static_cast<uint8_t>(state) & 0x03) << bitShift;
    }

    std::expected<void, BbmError> scanDevice(FlashHardwareInterface& hw) {
        bitmap_.fill(0xFF);
        remapRules_.clear();
        nextFreeReserved_ = UserBlocks;

        std::array<uint8_t, OobSize> oobBuf{};

        for (uint16_t b = 0; b < TotalBlocks; ++b) {
            bool isBad = false;
            for (uint32_t p : {0u, 1u}) {
                if (!hw.readOob(b, p, oobBuf) || oobBuf[OobMarkerOffset] != GoodMarker) {
                    isBad = true;
                    break;
                }
            }

            if (isBad) {
                setBlockState(b, BlockState::FactoryBad);
            } else if (b >= UserBlocks) {
                setBlockState(b, BlockState::Reserved);
            } else {
                setBlockState(b, BlockState::Good);
            }
        }

        for (uint16_t b = 0; b < UserBlocks; ++b) {
            if (getBlockState(b) == BlockState::FactoryBad) {
                auto spare = allocateSpareBlock();
                if (!spare) return std::unexpected(BbmError::ReservePoolExhausted);
                remapRules_.push_back(RemapRule{.badPhysBlock = b, .sparePhysBlock = *spare, .active = true});
            }
        }
        return {};
    }

    [[nodiscard]] std::expected<uint16_t, BbmError> resolveAddress(uint16_t userBlock) const {
        if (userBlock >= UserBlocks) return std::unexpected(BbmError::OutOfBounds);

        if (getBlockState(userBlock) == BlockState::Good) {
            return userBlock;
        }

        auto it = std::find_if(remapRules_.begin(), remapRules_.end(), [userBlock](const RemapRule& r) {
            return r.active && r.badPhysBlock == userBlock;
        });

        if (it != remapRules_.end()) {
            return it->sparePhysBlock;
        }
        return std::unexpected(BbmError::OutOfBounds);
    }

private:
    std::optional<uint16_t> allocateSpareBlock() {
        while (nextFreeReserved_ < TotalBlocks) {
            uint16_t candidate = nextFreeReserved_++;
            if (getBlockState(candidate) == BlockState::Reserved) {
                return candidate;
            }
        }
        return std::nullopt;
    }

    std::array<uint8_t, TotalBlocks / 4> bitmap_{};
    std::vector<RemapRule> remapRules_{};
    uint16_t nextFreeReserved_{UserBlocks};
};

} // namespace storage
