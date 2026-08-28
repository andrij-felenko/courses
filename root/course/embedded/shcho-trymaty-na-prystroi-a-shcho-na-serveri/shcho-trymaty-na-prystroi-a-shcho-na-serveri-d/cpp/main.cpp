#include <cstdint>
#include <cstddef>
#include <cstring>
#include <array>
#include <string_view>
#include <optional>
#include <expected>
#include <span>

namespace embedded::iot {

inline constexpr uint32_t ConfigMagic = 0x43464731U; // "CFG1"
inline constexpr size_t MaxAliasLength = 32;

inline constexpr float MinTargetTempC = -20.0f;
inline constexpr float MaxTargetTempC = 80.0f;
inline constexpr uint32_t MinIntervalSec = 5U;
inline constexpr uint32_t MaxIntervalSec = 86400U;

enum class SyncError : uint8_t {
    InvalidMagic,
    CrcMismatch,
    StaleVersion,
    OutOfRange,
    StorageFailure
};

#pragma pack(push, 1)
struct DeviceNvmPayload {
    uint32_t magic{ConfigMagic};
    uint32_t version{1};
    float targetTemperatureC{22.0f};
    uint32_t telemetryIntervalSec{60};
    bool autoValveEnabled{true};
    char deviceAlias[MaxAliasLength]{"Node-Default"};
};

struct DeviceNvmRecord {
    DeviceNvmPayload payload{};
    uint32_t crc32{0};
};
#pragma pack(pop)

struct ShadowDelta {
    uint32_t version{0};
    std::optional<float> targetTemperatureC{};
    std::optional<uint32_t> telemetryIntervalSec{};
    std::optional<bool> autoValveEnabled{};
    std::optional<std::string_view> deviceAlias{};
};

struct ShadowReportedState {
    uint32_t appliedVersion{};
    float currentSensorTempC{};
    float activeTargetTempC{};
    uint32_t activeIntervalSec{};
    bool activeValveState{};
    std::optional<SyncError> lastError{};
};

class Crc32Calculator {
public:
    static constexpr uint32_t Calculate(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (const uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 1U) {
                    crc = (crc >> 1) ^ 0xEDB88320U;
                } else {
                    crc >>= 1;
                }
            }
        }
        return ~crc;
    }
};

// Абстрактний інтерфейс сховища NVM (Flash / FRAM)
class INvmStorage {
public:
    virtual ~INvmStorage() = default;
    virtual bool Read(std::span<uint8_t> destination) = 0;
    virtual bool Write(std::span<const uint8_t> source) = 0;
};

// Симулятор NVM-драйвера в пам'яті
class SimulatedNvmStorage final : public INvmStorage {
public:
    bool Read(std::span<uint8_t> destination) override {
        if (destination.size() != m_storage.size()) return false;
        std::memcpy(destination.data(), m_storage.data(), destination.size());
        return true;
    }

    bool Write(std::span<const uint8_t> source) override {
        if (source.size() != m_storage.size()) return false;
        std::memcpy(m_storage.data(), source.data(), source.size());
        return true;
    }

private:
    std::array<uint8_t, sizeof(DeviceNvmRecord)> m_storage{};
};

class StateSynchronizer {
public:
    explicit StateSynchronizer(INvmStorage& storage) noexcept
        : m_storage(storage) {}

    [[nodiscard]] std::expected<void, SyncError> Initialize() noexcept {
        DeviceNvmRecord record{};
        auto recordSpan = std::span<uint8_t>(reinterpret_cast<uint8_t*>(&record), sizeof(record));

        if (!m_storage.Read(recordSpan)) {
            return std::unexpected(SyncError::StorageFailure);
        }

        if (record.payload.magic != ConfigMagic) {
            return InitializeFactoryDefaults();
        }

        auto payloadSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&record.payload), sizeof(DeviceNvmPayload));
        
        if (record.crc32 != Crc32Calculator::Calculate(payloadSpan)) {
            return std::unexpected(SyncError::CrcMismatch);
        }

        m_activeRecord = record;
        m_isInitialized = true;
        return {};
    }

    [[nodiscard]] std::expected<void, SyncError> ApplyDelta(const ShadowDelta& delta) noexcept {
        if (!m_isInitialized) {
            return std::unexpected(SyncError::StorageFailure);
        }

        if (delta.version <= m_activeRecord.payload.version) {
            return std::unexpected(SyncError::StaleVersion);
        }

        DeviceNvmRecord candidate = m_activeRecord;
        candidate.payload.version = delta.version;

        if (delta.targetTemperatureC) {
            if (*delta.targetTemperatureC < MinTargetTempC || *delta.targetTemperatureC > MaxTargetTempC) {
                return std::unexpected(SyncError::OutOfRange);
            }
            candidate.payload.targetTemperatureC = *delta.targetTemperatureC;
        }

        if (delta.telemetryIntervalSec) {
            if (*delta.telemetryIntervalSec < MinIntervalSec || *delta.telemetryIntervalSec > MaxIntervalSec) {
                return std::unexpected(SyncError::OutOfRange);
            }
            candidate.payload.telemetryIntervalSec = *delta.telemetryIntervalSec;
        }

        if (delta.autoValveEnabled) {
            candidate.payload.autoValveEnabled = *delta.autoValveEnabled;
        }

        if (delta.deviceAlias) {
            const size_t copyLen = std::min(delta.deviceAlias->size(), MaxAliasLength - 1);
            std::memset(candidate.payload.deviceAlias, 0, MaxAliasLength);
            std::memcpy(candidate.payload.deviceAlias, delta.deviceAlias->data(), copyLen);
        }

        auto payloadSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&candidate.payload), sizeof(DeviceNvmPayload));
        candidate.crc32 = Crc32Calculator::Calculate(payloadSpan);

        auto recordSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&candidate), sizeof(candidate));

        if (!m_storage.Write(recordSpan)) {
            return std::unexpected(SyncError::StorageFailure);
        }

        m_activeRecord = candidate;
        return {};
    }

    [[nodiscard]] ShadowReportedState GenerateReport(float currentSensorTemp, 
                                                    bool currentValveState,
                                                    std::optional<SyncError> error = std::nullopt) const noexcept {
        return ShadowReportedState{
            .appliedVersion = m_activeRecord.payload.version,
            .currentSensorTempC = currentSensorTemp,
            .activeTargetTempC = m_activeRecord.payload.targetTemperatureC,
            .activeIntervalSec = m_activeRecord.payload.telemetryIntervalSec,
            .activeValveState = currentValveState,
            .lastError = error
        };
    }

    [[nodiscard]] const DeviceNvmPayload& GetConfig() const noexcept {
        return m_activeRecord.payload;
    }

private:
    std::expected<void, SyncError> InitializeFactoryDefaults() noexcept {
        m_activeRecord = DeviceNvmRecord{};
        m_activeRecord.payload.magic = ConfigMagic;
        m_activeRecord.payload.version = 1;
        m_activeRecord.payload.targetTemperatureC = 22.0f;
        m_activeRecord.payload.telemetryIntervalSec = 60;
        m_activeRecord.payload.autoValveEnabled = true;

        constexpr std::string_view defaultAlias = "Node-Default";
        std::memcpy(m_activeRecord.payload.deviceAlias, defaultAlias.data(), defaultAlias.size());

        auto payloadSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&m_activeRecord.payload), sizeof(DeviceNvmPayload));
        m_activeRecord.crc32 = Crc32Calculator::Calculate(payloadSpan);

        auto recordSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&m_activeRecord), sizeof(m_activeRecord));

        if (!m_storage.Write(recordSpan)) {
            return std::unexpected(SyncError::StorageFailure);
        }

        m_isInitialized = true;
        return {};
    }

    INvmStorage& m_storage;
    DeviceNvmRecord m_activeRecord{};
    bool m_isInitialized{false};
};

} // namespace embedded::iot
