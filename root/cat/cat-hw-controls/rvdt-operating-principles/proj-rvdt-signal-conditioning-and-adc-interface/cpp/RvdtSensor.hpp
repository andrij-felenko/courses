#ifndef RVDT_SENSOR_HPP
#define RVDT_SENSOR_HPP

#include <cstdint>
#include <string_view>
#include <span>
#include <optional>

// Сильно типізований статус діагностики обмоток RVDT
enum class RvdtStatus : uint8_t {
    Ok = 0,                 // Нормальний робочий стан
    WindingOpenCircuit,     // Обрив обмотки або відсутність напруги збудження (V1 + V2 занадто мала)
    WindingShortCircuit,    // Коротке замикання обмотки (V1 + V2 перевищує допустиму межу)
    SumOutOfRange,          // Вихід кута за припустимі робочі межі
    InvalidParameters       // Некоректні параметри або порожній буфер відліків
};

// Параметри калібрування та конфігурації RVDT
struct RvdtConfig {
    float sensitivity{50.0f};       // Крутизна перетворення (градуси на одиницю ratiometric-відношення)
    float zeroOffsetDeg{0.0f};      // Зсув нульової позиції у градусах
    float minAngleDeg{-50.0f};      // Мінімальний припустимий кут повороту (-50°)
    float maxAngleDeg{+50.0f};      // Максимальний припустимий кут повороту (+50°)
    float vSumMinVolts{0.5f};       // Мінімальний поріг суми напруг для виявлення обриву (0.5 В)
    float vSumMaxVolts{7.0f};       // Максимальний поріг суми напруг для виявлення КЗ (7.0 В)
    float filterAlpha{0.4f};        // Коефіцієнт згладжування EMA-фільтра (0 < alpha <= 1)
};

// Результат вимірювання та діагностики
struct RvdtReading {
    float v1Volts{0.0f};            // Амплітуда першої вторинної обмотки V_S1
    float v2Volts{0.0f};            // Амплітуда другої вторинної обмотки V_S2
    float ratiometricRatio{0.0f};   // Коефіцієнт R = (V1 - V2) / (V1 + V2)
    float angleDegrees{0.0f};       // Обчислений кут повороту у градусах
    RvdtStatus status{RvdtStatus::Ok}; // Стан діагностики
};

class RvdtSensor {
public:
    explicit RvdtSensor(const RvdtConfig& config = RvdtConfig{});

    // Оновлення вимірювань за безпосередніми амплітудами V1 та V2
    RvdtStatus processAmplitudes(float rawV1Volts, float rawV2Volts) noexcept;

    // Цифрова фазочутлива демодуляція (PSD) за буферами відліків АЦП
    RvdtStatus processAdcSamples(std::span<const int16_t> s1Samples,
                                 std::span<const int16_t> s2Samples,
                                 std::span<const int16_t> refSamples,
                                 float vRefVolts = 3.3f,
                                 uint8_t adcBits = 12) noexcept;

    // Калібрування нульової позиції (установлення поточного кута як 0.0°)
    bool calibrateZero() noexcept;

    // Калібрування крутизни за еталонним кутом
    bool calibrateSpan(float referenceAngleDeg) noexcept;

    // Отримання поточних результатів вимірювання
    [[nodiscard]] const RvdtReading& getReading() const noexcept { return m_reading; }
    [[nodiscard]] float getAngle() const noexcept { return m_reading.angleDegrees; }
    [[nodiscard]] RvdtStatus getStatus() const noexcept { return m_reading.status; }
    [[nodiscard]] const RvdtConfig& getConfig() const noexcept { return m_config; }

    // Конвертація статусу в string_view
    [[nodiscard]] static std::string_view statusToString(RvdtStatus status) noexcept;

private:
    RvdtConfig m_config;
    RvdtReading m_reading;
};

#endif // RVDT_SENSOR_HPP
