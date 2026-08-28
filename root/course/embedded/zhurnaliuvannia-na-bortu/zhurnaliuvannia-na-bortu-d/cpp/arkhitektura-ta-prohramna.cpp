#include <cstdint>
#include <span>
#include <expected>

enum class LoggerStatus : uint8_t {
    Ok,
    HalError,
    BufferFull,
    InvalidParam
};

class FlashHalInterface {
public:
    virtual ~FlashHalInterface() = default;
    virtual bool read(uint32_t addr, std::span<uint8_t> dst) = 0;
    virtual bool write(uint32_t addr, std::span<const uint8_t> src) = 0;
    virtual bool eraseSector(uint32_t sectorAddr) = 0;
};

class FlashRingLogger {
public:
    static constexpr size_t SectorSize = 4096;
    static constexpr size_t SectorCount = 8;

    explicit FlashRingLogger(FlashHalInterface& hal, uint32_t baseAddr = 0) noexcept
        : hal_(hal), baseAddr_(baseAddr) {}

    std::expected<void, LoggerStatus> init();
    
    std::expected<void, LoggerStatus> write(uint8_t level, uint8_t moduleId,
                                           uint32_t timestampMs, uint32_t tokenId,
                                           std::span<const uint8_t> payload = {});

    std::expected<void, LoggerStatus> commitTail(uint32_t sectorIdx);

private:
    FlashHalInterface& hal_;
    uint32_t baseAddr_{0};
    uint32_t activeSectorIdx_{0};
    uint32_t writeOffset_{0};
    uint32_t tailSectorIdx_{0};
    uint32_t seqNum_{0};
};
