#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <algorithm>

namespace hardware::telemetry {

inline constexpr uint32_t FlashSectorSize = 4096;
inline constexpr uint16_t RecordMagic = 0xA55A;

enum class TrackerError : uint8_t {
    FlashReadFailed,
    FlashWriteFailed,
    FlashEraseFailed,
    CorruptedData
};

struct [[gnu::packed]] LifeRecord {
    uint16_t magic{RecordMagic};
    uint16_t sequenceId{0};
    uint32_t flightTimeSec{0};
    uint32_t totalMilliampSec{0};
    uint16_t powerCycles{0};
    uint16_t connectorCycles{0};
    uint16_t maxTempDecicelsius{0};
    uint16_t escVibrationIndex{0};
    uint8_t  reserved[12]{};
    uint16_t crc16{0};

    [[nodiscard]] uint16_t computeCrc() const noexcept {
        auto rawSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(this),
            sizeof(LifeRecord) - sizeof(uint16_t)
        );
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : rawSpan) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x8000) ? (static_cast<uint16_t>(crc << 1) ^ 0x1021)
                                     : static_cast<uint16_t>(crc << 1);
            }
        }
        return crc;
    }

    [[nodiscard]] bool isValid() const noexcept {
        return magic == RecordMagic && crc16 == computeCrc();
    }
};

class FlashWearTracker {
public:
    explicit constexpr FlashWearTracker(uint32_t sectorAddress) noexcept
        : m_sectorAddress(sectorAddress) {}

    std::expected<void, TrackerError> init() noexcept {
        uint16_t maxSeq = 0;
        bool foundValid = false;
        constexpr uint32_t totalSlots = FlashSectorSize / sizeof(LifeRecord);

        for (uint32_t i = 0; i < totalSlots; ++i) {
            LifeRecord rec{};
            const uint32_t slotAddr = m_sectorAddress + i * sizeof(LifeRecord);
            if (!halRead(slotAddr, std::span<uint8_t>(reinterpret_cast<uint8_t*>(&rec), sizeof(LifeRecord)))) {
                return std::unexpected(TrackerError::FlashReadFailed);
            }

            if (rec.isValid()) {
                if (!foundValid || rec.sequenceId >= maxSeq) {
                    maxSeq = rec.sequenceId;
                    m_state = rec;
                    m_currentSlot = i;
                    foundValid = true;
                }
            }
        }

        if (foundValid) {
            m_currentSlot = (m_currentSlot + 1) % totalSlots;
        } else {
            if (!halErase(m_sectorAddress)) {
                return std::unexpected(TrackerError::FlashEraseFailed);
            }
            m_state = LifeRecord{.magic = RecordMagic, .sequenceId = 1};
            m_currentSlot = 0;
        }
        return {};
    }

    std::expected<void, TrackerError> commit() noexcept {
        constexpr uint32_t totalSlots = FlashSectorSize / sizeof(LifeRecord);

        if (m_currentSlot == 0 && m_state.sequenceId > 1) {
            if (!halErase(m_sectorAddress)) {
                return std::unexpected(TrackerError::FlashEraseFailed);
            }
        }

        m_state.magic = RecordMagic;
        m_state.sequenceId++;
        m_state.crc16 = m_state.computeCrc();

        const uint32_t targetAddr = m_sectorAddress + m_currentSlot * sizeof(LifeRecord);
        auto dataSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&m_state),
            sizeof(LifeRecord)
        );

        if (!halWrite(targetAddr, dataSpan)) {
            return std::unexpected(TrackerError::FlashWriteFailed);
        }

        m_currentSlot = (m_currentSlot + 1) % totalSlots;
        return {};
    }

    void recordFlight(uint32_t durationSeconds, uint32_t currentMilliamps) noexcept {
        m_state.flightTimeSec += durationSeconds;
        m_state.totalMilliampSec += durationSeconds * currentMilliamps;
    }

    [[nodiscard]] const LifeRecord& state() const noexcept { return m_state; }

private:
    uint32_t m_sectorAddress{0};
    uint32_t m_currentSlot{0};
    LifeRecord m_state{};

    // Зовнішні апаратні виклики (mock/HAL)
    static bool halRead(uint32_t addr, std::span<uint8_t> dst) noexcept;
    static bool halWrite(uint32_t addr, std::span<const uint8_t> src) noexcept;
    static bool halErase(uint32_t sectorAddr) noexcept;
};

} // namespace hardware::telemetry
