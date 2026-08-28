#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <string_view>
#include <algorithm>

namespace embedded::node {

constexpr size_t FlashPageSize = 256;
constexpr size_t FlashSectorSize = 4096;
constexpr size_t RxBufferSize = 64;
constexpr size_t TxBufferSize = 64;

#pragma pack(push, 1)
struct TelemetryRecord {
    uint32_t timestamp{0};     // Unix timestamp від DS3231
    int32_t  temperature{0};   // Температура x100 (°C)
    uint32_t pressure{0};      // Тиск x100 (Па)
    uint32_t humidity{0};      // Вологість x1024 (%RH)
    uint16_t sequenceId{0};    // Порядковий номер
    uint16_t statusFlags{0};   // Прапорці стану
    uint16_t crc16{0};         // Контрольна сума
};
#pragma pack(pop)

static_assert(sizeof(TelemetryRecord) == 24, "TelemetryRecord must be exactly 24 bytes");

enum class NodeEvent : uint8_t {
    None = 0,
    RtcTick,
    DataReady,
    Rs485Rx,
    FlashSync
};

// ── Обчислення контрольної суми CRC-16 ──────────────────────────────────────
[[nodiscard]] constexpr uint16_t calculateCrc16(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte);
        for (uint8_t j = 0; j < 8; ++j) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc = crc >> 1;
            }
        }
    }
    return crc;
}

// ── Інтерфейс апаратної платформи ──────────────────────────────────────────
class INodeHardware {
public:
    virtual ~INodeHardware() = default;
    virtual bool readBme280(int32_t& temp, uint32_t& press, uint32_t& hum) = 0;
    virtual bool getRtcTime(uint32_t& unixTime) = 0;
    virtual bool flashSectorErase(uint32_t addr) = 0;
    virtual bool flashPageProgram(uint32_t addr, std::span<const uint8_t> data) = 0;
    virtual void setRs485DriverEnable(bool enable) = 0;
    virtual void rs485Transmit(std::span<const uint8_t> data) = 0;
};

// ── RAII-обгортка для лінії Driver Enable трансивера RS-485 ─────────────────
class Rs485TxGuard {
public:
    explicit Rs485TxGuard(INodeHardware& hw) : hw_(hw) {
        hw_.setRs485DriverEnable(true);
    }
    ~Rs485TxGuard() {
        hw_.setRs485DriverEnable(false);
    }
    Rs485TxGuard(const Rs485TxGuard&) = delete;
    Rs485TxGuard& operator=(const Rs485TxGuard&) = delete;

private:
    INodeHardware& hw_;
};

// ── Логер енергонезалежної пам'яті NOR Flash ────────────────────────────────
class FlashLogger {
public:
    explicit FlashLogger(INodeHardware& hw) : hw_(hw) {
        pageBuffer_.fill(0xFF);
    }

    bool appendRecord(const TelemetryRecord& record) {
        if ((writeAddress_ % FlashSectorSize) == 0 && pageOffset_ == 0) {
            if (!hw_.flashSectorErase(writeAddress_)) {
                return false;
            }
        }

        const auto* bytePtr = reinterpret_cast<const uint8_t*>(&record);
        std::copy_n(bytePtr, sizeof(TelemetryRecord), &pageBuffer_[pageOffset_]);
        pageOffset_ += sizeof(TelemetryRecord);
        ++totalRecords_;

        if (pageOffset_ + sizeof(TelemetryRecord) > FlashPageSize) {
            auto span = std::span<const uint8_t>(pageBuffer_.data(), pageOffset_);
            if (!hw_.flashPageProgram(writeAddress_, span)) {
                return false;
            }
            writeAddress_ += FlashPageSize;
            pageOffset_ = 0;
            pageBuffer_.fill(0xFF);
        }
        return true;
    }

    [[nodiscard]] uint32_t totalRecords() const noexcept { return totalRecords_; }

private:
    INodeHardware& hw_;
    uint32_t writeAddress_{0x000000};
    uint32_t totalRecords_{0};
    size_t pageOffset_{0};
    std::array<uint8_t, FlashPageSize> pageBuffer_{};
};

// ── Головний клас координатора вузла ────────────────────────────────────────
class NodeCoordinator {
public:
    explicit NodeCoordinator(INodeHardware& hw)
        : hw_(hw), logger_(hw_) {}

    void onRtcTick() noexcept {
        pendingEvent_ = NodeEvent::RtcTick;
    }

    void onRs485PacketReceived(std::span<const uint8_t> frame) {
        if (frame.size() <= RxBufferSize) {
            std::copy(frame.begin(), frame.end(), rxBuffer_.begin());
            rxSize_ = frame.size();
            frameReady_ = true;
        }
    }

    void step() {
        if (pendingEvent_ == NodeEvent::RtcTick) {
            pendingEvent_ = NodeEvent::None;
            acquireSensorsAndLog();
        }

        if (frameReady_) {
            processRs485Command();
        }
    }

private:
    void acquireSensorsAndLog() {
        uint32_t time = 0;
        int32_t temp = 0;
        uint32_t press = 0;
        uint32_t hum = 0;

        if (hw_.getRtcTime(time) && hw_.readBme280(temp, press, hum)) {
            lastRecord_.timestamp = time;
            lastRecord_.temperature = temp;
            lastRecord_.pressure = press;
            lastRecord_.humidity = hum;
            lastRecord_.sequenceId = ++sequenceCounter_;
            lastRecord_.statusFlags = 0x0001;

            auto payloadSpan = std::span<const uint8_t>(
                reinterpret_cast<const uint8_t*>(&lastRecord_),
                sizeof(TelemetryRecord) - sizeof(uint16_t)
            );
            lastRecord_.crc16 = calculateCrc16(payloadSpan);

            logger_.appendRecord(lastRecord_);
        }
    }

    void processRs485Command() {
        frameReady_ = false;
        if (rxSize_ < 4 || rxBuffer_[0] != 0x01 || rxBuffer_[1] != 0x03) {
            return;
        }

        uint16_t expectedCrc = static_cast<uint16_t>(rxBuffer_[2]) |
                              (static_cast<uint16_t>(rxBuffer_[3]) << 8);

        if (calculateCrc16(std::span(rxBuffer_.data(), 2)) != expectedCrc) {
            return;
        }

        // Побудова кадру телеметричної відповіді
        txBuffer_[0] = 0x01;
        txBuffer_[1] = 0x03;
        txBuffer_[2] = sizeof(TelemetryRecord);

        const auto* recBytes = reinterpret_cast<const uint8_t*>(&lastRecord_);
        std::copy_n(recBytes, sizeof(TelemetryRecord), &txBuffer_[3]);

        size_t payloadLen = 3 + sizeof(TelemetryRecord);
        uint16_t txCrc = calculateCrc16(std::span(txBuffer_.data(), payloadLen));
        txBuffer_[payloadLen]     = static_cast<uint8_t>(txCrc & 0xFF);
        txBuffer_[payloadLen + 1] = static_cast<uint8_t>((txCrc >> 8) & 0xFF);
        size_t totalLen = payloadLen + 2;

        // Безпечна відправка з автоматичним поверненням DE в Low через RAII
        {
            Rs485TxGuard guard(hw_);
            hw_.rs485Transmit(std::span(txBuffer_.data(), totalLen));
        }
    }

    INodeHardware& hw_;
    FlashLogger logger_;
    TelemetryRecord lastRecord_{};
    uint16_t sequenceCounter_{0};
    volatile NodeEvent pendingEvent_{NodeEvent::None};

    std::array<uint8_t, RxBufferSize> rxBuffer_{};
    std::array<uint8_t, TxBufferSize> txBuffer_{};
    size_t rxSize_{0};
    bool frameReady_{false};
};

} // namespace embedded::node
