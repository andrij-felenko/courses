#include <cstdint>
#include <cstddef>
#include <span>
#include <memory>
#include <expected>

enum class LfsResult : int {
    Ok      = 0,
    IoError = -5,
    Corrupt = -84
};

struct FlashGeometry {
    uint32_t base_address{0x00000000};
    uint32_t sector_size{4096};
    uint32_t page_size{256};
    uint32_t total_blocks{512};
};

class ISpiFlashDriver {
public:
    virtual ~ISpiFlashDriver() = default;
    [[nodiscard]] virtual bool readRaw(uint32_t address, std::span<uint8_t> destination) = 0;
    [[nodiscard]] virtual bool programRaw(uint32_t address, std::span<const uint8_t> source) = 0;
    [[nodiscard]] virtual bool eraseSectorRaw(uint32_t address) = 0;
    [[nodiscard]] virtual bool waitForReady(uint32_t timeoutMs) = 0;
};

class LittleFsDriverBridge final {
public:
    LittleFsDriverBridge(std::shared_ptr<ISpiFlashDriver> hardware, FlashGeometry geometry)
        : hw_(std::move(hardware)), geom_(geometry) {}

    [[nodiscard]] int read(uint32_t block, uint32_t offset, std::span<uint8_t> dest) const noexcept {
        if (block >= geom_.total_blocks || offset + dest.size() > geom_.sector_size) {
            return static_cast<int>(LfsResult::IoError);
        }
        uint32_t phys = geom_.base_address + (block * geom_.sector_size) + offset;
        if (!hw_->readRaw(phys, dest)) {
            return static_cast<int>(LfsResult::IoError);
        }
        return static_cast<int>(LfsResult::Ok);
    }

    [[nodiscard]] int prog(uint32_t block, uint32_t offset, std::span<const uint8_t> src) noexcept {
        if (block >= geom_.total_blocks || offset + src.size() > geom_.sector_size) {
            return static_cast<int>(LfsResult::IoError);
        }
        uint32_t phys = geom_.base_address + (block * geom_.sector_size) + offset;
        if (!hw_->programRaw(phys, src)) {
            return static_cast<int>(LfsResult::IoError);
        }
        return static_cast<int>(LfsResult::Ok);
    }

    [[nodiscard]] int erase(uint32_t block) noexcept {
        if (block >= geom_.total_blocks) {
            return static_cast<int>(LfsResult::IoError);
        }
        uint32_t phys = geom_.base_address + (block * geom_.sector_size);
        if (!hw_->eraseSectorRaw(phys)) {
            return static_cast<int>(LfsResult::IoError);
        }
        return static_cast<int>(LfsResult::Ok);
    }

    [[nodiscard]] int sync() noexcept {
        if (!hw_->waitForReady(500)) {
            return static_cast<int>(LfsResult::IoError);
        }
        return static_cast<int>(LfsResult::Ok);
    }

private:
    std::shared_ptr<ISpiFlashDriver> hw_;
    FlashGeometry geom_;
};
