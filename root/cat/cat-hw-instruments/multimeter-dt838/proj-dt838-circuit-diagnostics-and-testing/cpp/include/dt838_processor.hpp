#ifndef DT838_PROCESSOR_HPP
#define DT838_PROCESSOR_HPP

#include <string>
#include <string_view>
#include <optional>
#include <cstdint>

namespace dt838 {

// Режими вимірювань мультиметра DT-838
enum class MeasurementMode {
    VoltageDC_200mV,
    VoltageDC_2000mV,
    VoltageDC_20V,
    VoltageDC_200V,
    VoltageDC_1000V,
    VoltageAC_200V,
    VoltageAC_750V,
    Resistance_200Ohm,
    Resistance_2000Ohm,
    Resistance_20kOhm,
    Resistance_200kOhm,
    Resistance_2000kOhm,
    DiodeTest,
    Temperature
};

// Стан напівпровідникового p-n переходу при тестуванні
enum class SemiconductorState {
    NormalSilicon,    // Нормальний кремнієвий p-n перехід (0.5 – 0.8 В)
    NormalGermanium,  // Нормальний германієвий p-n перехід (0.2 – 0.4 В)
    ShortCircuit,     // Пробій / Коротке замикання (< 0.1 В)
    OpenCircuit,      // Обрив або зворотне включення (> 1.5 В / Overflow)
    Unknown           // Невизначений стан
};

// Результат вимірювання фізичної величини
struct MeasurementResult {
    double value{0.0};
    std::string unit;
    bool overflow{false};
    bool valid{true};
    std::string description;
};

// Статус перевірки температурного допуску
struct TemperatureStatus {
    double temperatureCelsius{0.0};
    bool withinLimits{true};
    bool highAlarm{false};
    bool lowAlarm{false};
    std::string message;
};

// Клас конвертації відліків АЦП ICL7106 (3.5 розряди: 0 - 1999)
class AdcConvertor {
public:
    AdcConvertor() = default;

    // Конвертація сирого відліку АЦП (0..1999) відповідно до обраного режиму
    [[nodiscard]] MeasurementResult processRawAdc(int16_t rawAdcCount, MeasurementMode mode) const;
};

// Клас тестування та діагностики напівпровідникових діодів/транзисторів
class DiodeTester {
public:
    DiodeTester() = default;

    // Аналіз падіння напруги в мілівольтах (мВ) на p-n переході
    [[nodiscard]] SemiconductorState evaluateJunction(double voltageDropmV) const;

    // Отримання текстового опису стану переходу українською мовою
    [[nodiscard]] static std::string_view getStateDescription(SemiconductorState state);
};

// Клас обчислення температури з термокомпенсацією холодного спаю та контролю допусків
class TemperatureEvaluator {
public:
    explicit TemperatureEvaluator(double minAllowedCelsius = 0.0, double maxAllowedCelsius = 100.0);

    // Обчислення температури за сигналом термопари K-типу та температурою довкілля
    [[nodiscard]] TemperatureStatus evaluate(double rawThermocoupleVoltagemV, double ambientTempCelsius) const;

    void setLimits(double minAllowed, double maxAllowed);

private:
    double minTemp_{0.0};
    double maxTemp_{100.0};

    // Середній коефіцієнт термо-РС термопари K-типу: ~41 мкВ/°C (0.041 мВ/°C)
    static constexpr double SeebeckCoefficientmVPerC = 0.041;
};

} // namespace dt838

#endif // DT838_PROCESSOR_HPP
