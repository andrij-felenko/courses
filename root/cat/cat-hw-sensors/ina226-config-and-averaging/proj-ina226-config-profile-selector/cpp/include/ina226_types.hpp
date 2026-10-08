#ifndef INA226_TYPES_HPP
#define INA226_TYPES_HPP

#include <cstdint>
#include <string>

namespace ina226 {

// Адреси регістрів давача INA226
enum class Register : uint8_t {
    Configuration = 0x00,
    ShuntVoltage  = 0x01,
    BusVoltage    = 0x02,
    Power         = 0x03,
    Current       = 0x04,
    Calibration   = 0x05,
    MaskEnable    = 0x06,
    AlertLimit    = 0x07,
    ManufacturerId= 0xFE,
    DieId         = 0xFF
};

// Режими усереднення (AVG: біти 11-9 регістру Configuration)
enum class AveragingMode : uint16_t {
    AVG_1    = 0b000, // 1 вибірка (без усереднення)
    AVG_4    = 0b001, // 4 вибірки
    AVG_16   = 0b010, // 16 вибірок
    AVG_64   = 0b011, // 64 вибірки
    AVG_128  = 0b100, // 128 вибірок
    AVG_256  = 0b101, // 256 вибірок
    AVG_512  = 0b110, // 512 вибірок
    AVG_1024 = 0b111  // 1024 вибірки
};

// Час перетворення (VSHCT/VBUSCT: біти 5-3 / 8-6 регістру Configuration)
enum class ConversionTime : uint16_t {
    TIME_140US  = 0b000, // 140 мкс
    TIME_204US  = 0b001, // 204 мкс
    TIME_332US  = 0b010, // 332 мкс
    TIME_588US  = 0b011, // 588 мкс
    TIME_1100US = 0b100, // 1.1 ms (за замовчуванням)
    TIME_2116US = 0b101, // 2.116 ms
    TIME_4156US = 0b110, // 4.156 ms
    TIME_8244US = 0b111  // 8.244 ms
};

// Режими роботи ADC (MODE: біти 2-0 регістру Configuration)
enum class OperatingMode : uint16_t {
    POWER_DOWN           = 0b000, // Вимкнено
    SHUNT_TRIGGERED      = 0b001, // Струм шунта (одноразове вимірювання)
    BUS_TRIGGERED        = 0b010, // Напруга шини (одноразове вимірювання)
    SHUNT_BUS_TRIGGERED  = 0b011, // Струм і напруга (одноразове вимірювання)
    ADC_OFF              = 0b100, // ADC вимкнено
    SHUNT_CONTINUOUS     = 0b101, // Струм шунта (неперервно)
    BUS_CONTINUOUS       = 0b110, // Напруга шини (неперервно)
    SHUNT_BUS_CONTINUOUS = 0b111  // Струм і напруга (неперервно, за замовчуванням)
};

// Бітові маски джерел переривання регістру Mask/Enable (адреса 0x06)
namespace AlertMask {
    constexpr uint16_t SHUNT_OVER_LIMIT  = 1 << 15; // SOL (Перевищення напруги шунта)
    constexpr uint16_t SHUNT_UNDER_LIMIT = 1 << 14; // SUL (Зниження напруги шунта)
    constexpr uint16_t BUS_OVER_LIMIT   = 1 << 13; // BOL (Перевищення напруги шини)
    constexpr uint16_t BUS_UNDER_LIMIT  = 1 << 12; // BUL (Зниження напруги шини)
    constexpr uint16_t POWER_OVER_LIMIT = 1 << 11; // POL (Перевищення потужності)
    constexpr uint16_t CONVERSION_READY = 1 << 10; // CNVR (Дані готові)
    constexpr uint16_t APOL_HIGH         = 1 << 1;  // APOL (1 = Active High, 0 = Active Low)
    constexpr uint16_t LATCH_ENABLE      = 1 << 0;  // LEN (1 = Latch mode, 0 = Transparent)
}

// Прапори статусу переривання в регістрі Mask/Enable
namespace AlertStatusFlag {
    constexpr uint16_t ALERT_FUNCTION = 1 << 4; // AFF (Спрацював Alert Limit)
    constexpr uint16_t CONVR_READY     = 1 << 3; // CVRF (Готові нові дані)
    constexpr uint16_t MATH_OVERFLOW   = 1 << 2; // OVF (Переповнення арифметики потужності/струму)
}

// Конструктор конфігураційного слова для регістру Configuration (0x00)
struct Ina226RegisterConfig {
    AveragingMode avg{AveragingMode::AVG_16};
    ConversionTime vbusct{ConversionTime::TIME_1100US};
    ConversionTime vshct{ConversionTime::TIME_1100US};
    OperatingMode mode{OperatingMode::SHUNT_BUS_CONTINUOUS};

    // Пакування параметрів у 16-бітне конфігураційне слово
    [[nodiscard]] constexpr uint16_t toRawValue() const noexcept {
        return (static_cast<uint16_t>(avg) << 9) |
               (static_cast<uint16_t>(vbusct) << 6) |
               (static_cast<uint16_t>(vshct) << 3) |
               static_cast<uint16_t>(mode);
    }

    // Розпакування 16-бітного слова у структуру
    static constexpr Ina226RegisterConfig fromRawValue(uint16_t raw) noexcept {
        Ina226RegisterConfig cfg;
        cfg.avg    = static_cast<AveragingMode>((raw >> 9) & 0x07);
        cfg.vbusct = static_cast<ConversionTime>((raw >> 6) & 0x07);
        cfg.vshct  = static_cast<ConversionTime>((raw >> 3) & 0x07);
        cfg.mode   = static_cast<OperatingMode>(raw & 0x07);
        return cfg;
    }
};

// Профіль вимірювань давача
struct SamplingProfile {
    const char* name;
    AveragingMode avg;
    ConversionTime vshct;
    ConversionTime vbusct;
    OperatingMode mode;

    [[nodiscard]] Ina226RegisterConfig toRegisterConfig() const noexcept {
        return Ina226RegisterConfig{avg, vbusct, vshct, mode};
    }
};

// Типи подій переривання
enum class AlertEventType {
    ConversionReady,
    OverCurrentLimit,
    BusOverVoltage,
    PowerLimitExceeded,
    MathOverflow,
    Unknown
};

// Структура даних події ALERT
struct AlertEvent {
    AlertEventType type;
    double currentAmperes;
    double busVoltageVolts;
    double shuntVoltageMv;
    double powerWatts;
    uint16_t rawMaskEnable;
};

} // namespace ina226

#endif // INA226_TYPES_HPP
