#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <algorithm>
#include <array>
#include <string_view>

enum class LogLevel : uint8_t {
    Trace = 0,
    Debug = 1,
    Info  = 2,
    Warn  = 3,
    Error = 4,
    Fatal = 5
};

enum class SectorState : uint32_t {
    Erased = 0xFFFFFFFF,
    Active = 0xFFFFFFFE,
    Full   = 0xFFFFFFFC,
    Dirty  = 0x00000000
};

enum class LoggerError {
    HalError,
    BufferOverflow,
    InvalidRecord,
    CrcMismatch,
    SectorCorrupt
};

class FlashHal {
public:
    virtual ~FlashHal() = default;
    virtual bool read(uint32_t addr, std::span<uint8_t> dst) = 0;
    virtual bool write(uint32_t addr, std::span<const uint8_t> src) = 0;
    virtual bool eraseSector(uint32_t sector_addr) = 0;
};

class PersistentRingLogger {
public:
    static constexpr size_t SectorSize = 4096;
    static constexpr size_t SectorCount = 8;
    static constexpr uint16_t SectorMagic = 0xA55A;
    static constexpr uint16_t RecordMagic = 0x55AA;

#pragma pack(push, 1)
    struct SectorHeader {
        uint16_t    magic{SectorMagic};
        uint16_t    version{1};
        uint32_t    seqNum{0};
        uint32_t    eraseCount{0};
        SectorState state{SectorState::Erased};
    };

    struct RecordHeader {
        uint16_t magic{RecordMagic};
        uint8_t  length{0};
        LogLevel level{LogLevel::Info};
        uint8_t  moduleId{0};
        uint8_t  reserved{0};
        uint32_t timestampMs{0};
        uint32_t tokenId{0};
    };
#pragma pack(pop)

    explicit PersistentRingLogger(FlashHal& hal, uint32_t baseAddr = 0)
        : hal_(hal), baseAddr_(baseAddr) {}

    std::expected<void, LoggerError> init() {
        uint32_t maxSeq = 0;
        int activeIdx = -1;
        int oldestIdx = -1;
        uint32_t minSeq = 0xFFFFFFFF;

        for (uint32_t i = 0; i < SectorCount; ++i) {
            SectorHeader hdr{};
            if (!hal_.read(sectorAddress(i), std::as_writable_bytes(std::span{&hdr, 1}))) {
                return std::unexpected(LoggerError::HalError);
            }

            if (hdr.magic == SectorMagic) {
                if (hdr.state == SectorState::Active) {
                    activeIdx = static_cast<int>(i);
                }
                if (hdr.seqNum > maxSeq) {
                    maxSeq = hdr.seqNum;
                }
                if (hdr.seqNum < minSeq && hdr.state != SectorState::Erased) {
                    minSeq = hdr.seqNum;
                    oldestIdx = static_cast<int>(i);
                }
            }
        }

        if (activeIdx != -1) {
            activeSectorIdx_ = static_cast<uint32_t>(activeIdx);
            globalSeqNum_ = maxSeq;
            recoverActiveSectorOffset();
        } else {
            activeSectorIdx_ = 0;
            globalSeqNum_ = 1;
            if (!hal_.eraseSector(sectorAddress(0))) {
                return std::unexpected(LoggerError::HalError);
            }
            SectorHeader newHdr{
                .magic = SectorMagic,
                .version = 1,
                .seqNum = globalSeqNum_,
                .eraseCount = 1,
                .state = SectorState::Active
            };
            if (!hal_.write(sectorAddress(0), std::as_bytes(std::span{&newHdr, 1}))) {
                return std::unexpected(LoggerError::HalError);
            }
            writeOffset_ = sizeof(SectorHeader);
        }

        tailSectorIdx_ = (oldestIdx != -1) ? static_cast<uint32_t>(oldestIdx) : activeSectorIdx_;
        return {};
    }

    std::expected<void, LoggerError> log(LogLevel level, uint8_t moduleId,
                                         uint32_t timestampMs, uint32_t tokenId,
                                         std::span<const uint8_t> payload = {}) {
        const size_t totalLen = sizeof(RecordHeader) + payload.size() + sizeof(uint16_t);
        if (totalLen > 255) {
            return std::unexpected(LoggerError::BufferOverflow);
        }

        if (writeOffset_ + totalLen > SectorSize) {
            if (auto res = rotateSector(); !res) {
                return res;
            }
        }

        std::array<uint8_t, 256> buffer{};
        auto* hdr = reinterpret_cast<RecordHeader*>(buffer.data());
        hdr->magic = RecordMagic;
        hdr->length = static_cast<uint8_t>(totalLen);
        hdr->level = level;
        hdr->moduleId = moduleId;
        hdr->reserved = 0;
        hdr->timestampMs = timestampMs;
        hdr->tokenId = tokenId;

        if (!payload.empty()) {
            std::copy(payload.begin(), payload.end(), buffer.begin() + sizeof(RecordHeader));
        }

        uint16_t crc = calculateCrc(std::span{buffer.data() + 2, totalLen - 4});
        buffer[totalLen - 2] = static_cast<uint8_t>(crc & 0xFF);
        buffer[totalLen - 1] = static_cast<uint8_t>((crc >> 8) & 0xFF);

        uint32_t writeAddr = sectorAddress(activeSectorIdx_) + writeOffset_;
        if (!hal_.write(writeAddr, std::span{buffer.data(), totalLen})) {
            return std::unexpected(LoggerError::HalError);
        }

        writeOffset_ += totalLen;
        return {};
    }

    std::expected<void, LoggerError> commitTailAck(uint32_t sectorIdx) {
        if (sectorIdx >= SectorCount) {
            return std::unexpected(LoggerError::SectorCorrupt);
        }
        if (sectorIdx == activeSectorIdx_) {
            return {};
        }

        uint32_t addr = sectorAddress(sectorIdx) + offsetof(SectorHeader, state);
        SectorState dirtyState = SectorState::Dirty;
        if (!hal_.write(addr, std::as_bytes(std::span{&dirtyState, 1}))) {
            return std::unexpected(LoggerError::HalError);
        }

        if (sectorIdx == tailSectorIdx_) {
            tailSectorIdx_ = (tailSectorIdx_ + 1) % SectorCount;
        }
        return {};
    }

    [[nodiscard]] uint32_t activeSector() const noexcept { return activeSectorIdx_; }
    [[nodiscard]] uint32_t tailSector() const noexcept { return tailSectorIdx_; }

private:
    FlashHal& hal_;
    uint32_t  baseAddr_{0};
    uint32_t  activeSectorIdx_{0};
    uint32_t  writeOffset_{sizeof(SectorHeader)};
    uint32_t  tailSectorIdx_{0};
    uint32_t  globalSeqNum_{0};

    [[nodiscard]] uint32_t sectorAddress(uint32_t idx) const noexcept {
        return baseAddr_ + (idx * SectorSize);
    }

    static uint16_t calculateCrc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc <<= 1;
                }
            }
        }
        return crc;
    }

    void recoverActiveSectorOffset() {
        uint32_t offset = sizeof(SectorHeader);
        uint32_t sAddr = sectorAddress(activeSectorIdx_);
        std::array<uint8_t, 256> recBuf{};

        while (offset + sizeof(RecordHeader) + sizeof(uint16_t) <= SectorSize) {
            RecordHeader rh{};
            if (!hal_.read(sAddr + offset, std::as_writable_bytes(std::span{&rh, 1}))) {
                break;
            }
            if (rh.magic != RecordMagic || rh.length < sizeof(RecordHeader) + 2) {
                break;
            }
            if (rh.length > recBuf.size()) break;

            hal_.read(sAddr + offset, std::span{recBuf.data(), rh.length});
            uint16_t expectedCrc = static_cast<uint16_t>(recBuf[rh.length - 2] | (recBuf[rh.length - 1] << 8));
            uint16_t actualCrc = calculateCrc(std::span{recBuf.data() + 2, static_cast<size_t>(rh.length - 4)});

            if (expectedCrc != actualCrc) {
                break; // Відсікання незавершеного запису
            }
            offset += rh.length;
        }
        writeOffset_ = offset;
    }

    std::expected<void, LoggerError> rotateSector() {
        uint32_t curAddr = sectorAddress(activeSectorIdx_) + offsetof(SectorHeader, state);
        SectorState fullState = SectorState::Full;
        if (!hal_.write(curAddr, std::as_bytes(std::span{&fullState, 1}))) {
            return std::unexpected(LoggerError::HalError);
        }

        uint32_t nextIdx = (activeSectorIdx_ + 1) % SectorCount;
        SectorHeader oldHdr{};
        hal_.read(sectorAddress(nextIdx), std::as_writable_bytes(std::span{&oldHdr, 1}));
        uint32_t eraseCount = (oldHdr.magic == SectorMagic) ? (oldHdr.eraseCount + 1) : 1;

        if (!hal_.eraseSector(sectorAddress(nextIdx))) {
            return std::unexpected(LoggerError::HalError);
        }

        ++globalSeqNum_;
        SectorHeader newHdr{
            .magic = SectorMagic,
            .version = 1,
            .seqNum = globalSeqNum_,
            .eraseCount = eraseCount,
            .state = SectorState::Active
        };

        if (!hal_.write(sectorAddress(nextIdx), std::as_bytes(std::span{&newHdr, 1}))) {
            return std::unexpected(LoggerError::HalError);
        }

        activeSectorIdx_ = nextIdx;
        writeOffset_ = sizeof(SectorHeader);

        if (activeSectorIdx_ == tailSectorIdx_) {
            tailSectorIdx_ = (tailSectorIdx_ + 1) % SectorCount;
        }
        return {};
    }
};
