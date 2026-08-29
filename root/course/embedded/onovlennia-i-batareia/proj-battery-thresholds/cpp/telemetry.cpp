#include "telemetry.hpp"

namespace ota {
namespace {

using namespace std::chrono_literals;

// Формат пакета (big-endian, як усе на цьому каналі):
//   'O' 'T' 'A' версія | код | прапорці | retry_after (4 байти)
//   далі TLV: тег(1) довжина(1) значення
// Сервер, що не знає тега, перестрибує його за довжиною.
constexpr std::uint8_t kVersion     = 0x01;
constexpr std::uint8_t kFlagService = 0x01;

constexpr std::uint8_t kTagTemp     = 0x01;
constexpr std::uint8_t kTagSoc      = 0x02;
constexpr std::uint8_t kTagEsr      = 0x03;
constexpr std::uint8_t kTagIdle     = 0x04;
constexpr std::uint8_t kTagLoad     = 0x05;
constexpr std::uint8_t kTagForecast = 0x06;
constexpr std::uint8_t kTagFaults   = 0x07;

class Writer {
public:
    explicit Writer(std::span<std::byte> out) noexcept : out_(out) {}

    void u8(std::uint8_t v) noexcept {
        if (n_ >= out_.size()) {
            overflow_ = true;
            return;
        }
        out_[n_++] = std::byte{v};
    }
    void u16(std::uint16_t v) noexcept {
        u8(static_cast<std::uint8_t>(v >> 8));
        u8(static_cast<std::uint8_t>(v & 0xFFu));
    }
    void u32(std::uint32_t v) noexcept {
        u16(static_cast<std::uint16_t>(v >> 16));
        u16(static_cast<std::uint16_t>(v & 0xFFFFu));
    }
    void tlv(std::uint8_t tag, std::uint8_t v) noexcept { u8(tag); u8(1); u8(v); }
    void tlv(std::uint8_t tag, std::uint16_t v) noexcept { u8(tag); u8(2); u16(v); }

    [[nodiscard]] bool overflow() const noexcept { return overflow_; }
    [[nodiscard]] std::span<const std::byte> written() const noexcept { return out_.first(n_); }

private:
    std::span<std::byte> out_;
    std::size_t          n_ = 0;
    bool                 overflow_ = false;
};

}  // namespace

std::string_view name(TelemetryCode code) noexcept
{
    switch (code) {
    case TelemetryCode::RetryCold:       return "OTA_RETRY_COLD";
    case TelemetryCode::RetryHot:        return "OTA_RETRY_HOT";
    case TelemetryCode::RetryLowSoc:     return "OTA_RETRY_LOW_SOC";
    case TelemetryCode::AlertHighEsr:    return "OTA_ALERT_HIGH_ESR";
    case TelemetryCode::AlertSensorFail: return "OTA_ALERT_SENSOR_FAIL";
    case TelemetryCode::AlertPowerFault: return "OTA_ALERT_POWER_FAULT";
    }
    return "OTA_UNKNOWN";
}

std::string_view name(DenyReason reason) noexcept
{
    switch (reason) {
    case DenyReason::Cold:              return "холодна комірка";
    case DenyReason::Hot:               return "перегріта комірка";
    case DenyReason::LowSoc:            return "замало заряду";
    case DenyReason::HighEsr:           return "високий опір комірки";
    case DenyReason::PowerFaultLockout: return "блокування після зривів живлення";
    case DenyReason::SensorFault:       return "збій вимірювальних кіл";
    }
    return "невідома причина";
}

DenialReport summarize(const Denial& denial, const SafetyLimits& limits) noexcept
{
    switch (denial.reason) {
    case DenyReason::Cold: {
        // Чекаємо денного прогріву. Глибокий мінус — довше вікно: сонце
        // має встигнути витягти комірку в робочий коридор.
        const bool deep = denial.diag.tempC
                       && *denial.diag.tempC < static_cast<std::int16_t>(limits.tempMinC - 5);
        return {TelemetryCode::RetryCold, deep ? 8h : 6h, false};
    }
    case DenyReason::Hot:
        return {TelemetryCode::RetryHot, 4h, false};  // до вечірнього спаду
    case DenyReason::LowSoc:
        return {TelemetryCode::RetryLowSoc, 2h, false};  // час на підзарядку
    case DenyReason::HighEsr:
        // Опір комірки сам не впаде: далі не пробуємо, сервер заводить
        // сервісну задачу на заміну батареї.
        return {TelemetryCode::AlertHighEsr, 0s, true};
    case DenyReason::PowerFaultLockout:
        return {TelemetryCode::AlertPowerFault, 0s, true};
    case DenyReason::SensorFault:
        return {TelemetryCode::AlertSensorFail, 1h, true};
    }
    return {TelemetryCode::AlertSensorFail, 1h, true};
}

std::expected<std::span<const std::byte>, EncodeError>
encode(const Denial& denial, const SafetyLimits& limits, std::span<std::byte> out) noexcept
{
    const DenialReport report = summarize(denial, limits);

    Writer w{out};
    w.u8('O');
    w.u8('T');
    w.u8('A');
    w.u8(kVersion);
    w.u8(static_cast<std::uint8_t>(report.code));
    w.u8(report.serviceRequired ? kFlagService : std::uint8_t{0});
    w.u32(static_cast<std::uint32_t>(report.retryAfter.count()));

    const auto& diag = denial.diag;
    if (diag.tempC) {
        w.tlv(kTagTemp, static_cast<std::uint16_t>(*diag.tempC));  // доповняльний код
    }
    if (diag.socPercent) {
        w.tlv(kTagSoc, *diag.socPercent);
    }
    if (diag.idleMv) {
        w.tlv(kTagIdle, *diag.idleMv);
    }
    if (diag.pulse) {
        w.tlv(kTagLoad, diag.pulse->loadMv);
        w.tlv(kTagEsr, diag.pulse->esrMilliOhm);
        w.tlv(kTagForecast, diag.pulse->forecastMv);
    }
    w.tlv(kTagFaults, diag.powerFaults);

    if (w.overflow()) {
        return std::unexpected(EncodeError::BufferTooSmall);
    }
    return w.written();
}

}  // namespace ota
