#include <cstdint>
#include <concepts>
#include <span>
#include <optional>

namespace embedded::power {

/* Результати оцінки стану живлення для OTA */
enum class BatteryVerdict : uint8_t {
    AllowAcPowered,  // Дозволено: живлення від зовнішнього джерела
    AllowBatteryOk,  // Дозволено: параметри акумулятора в нормі
    DenyCold,        // Заборонено: температура надто низька
    DenyHot,         // Заборонено: температура надто висока
    DenyLowSoc,      // Заборонено: недостатній рівень заряду
    DenyHighEsr,     // Заборонено: небезпечне динамічне просідання
    DenySensorFail   // Заборонено: збій апаратних давачів
};

/* Налаштування безпекових меж */
struct SafetyLimits {
    int16_t  tempMinC           = 5;     // +5 °C
    int16_t  tempMaxC           = 45;    // +45 °C
    uint8_t  minSocPercent      = 45;    // 45 %
    uint16_t vBorSafeMv         = 2900;  // 2.90 В
    uint16_t testLoadCurrentMa  = 200;   // 200 мА
    uint16_t otaPeakCurrentMa   = 320;   // 320 мА
};

/* Результат детальної перевірки */
struct CheckResult {
    BatteryVerdict verdict;
    uint16_t       forecastVoltageMv;
    uint16_t       measuredEsrMilliOhm;
};

/* Концепт для апаратного рівня абстракції */
template <typename T>
concept PowerPlatformHal = requires(T hal, bool enable, uint32_t ms) {
    { hal.isVbusPresent() } -> std::same_as<bool>;
    { hal.readTemperatureC() } -> std::same_as<std::optional<int16_t>>;
    { hal.readSocPercent() } -> std::same_as<std::optional<uint8_t>>;
    { hal.readVoltageMv() } -> std::same_as<uint16_t>;
    { hal.setTestLoad(enable) } -> std::same_as<void>;
    { hal.delayMs(ms) } -> std::same_as<void>;
};

/* Автомат безпечного допуску до OTA */
template <PowerPlatformHal THal>
class BatteryPreflightSupervisor {
public:
    constexpr explicit BatteryPreflightSupervisor(const SafetyLimits& limits = {})
        : m_limits(limits) {}

    [[nodiscard]] CheckResult evaluate(THal& hal) const noexcept {
        // 1. Якщо підключено мережевий адаптер або USB — повний допуск
        if (hal.isVbusPresent()) {
            return {
                .verdict = BatteryVerdict::AllowAcPowered,
                .forecastVoltageMv = hal.readVoltageMv(),
                .measuredEsrMilliOhm = 0
            };
        }

        // 2. Перевірка температури комірки
        const auto tempC = hal.readTemperatureC();
        if (!tempC.has_value()) {
            return {.verdict = BatteryVerdict::DenySensorFail, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }
        if (*tempC < m_limits.tempMinC) {
            return {.verdict = BatteryVerdict::DenyCold, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }
        if (*tempC > m_limits.tempMaxC) {
            return {.verdict = BatteryVerdict::DenyHot, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }

        // 3. Перевірка рівня заряду (SoC)
        const auto soc = hal.readSocPercent();
        if (!soc.has_value()) {
            return {.verdict = BatteryVerdict::DenySensorFail, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }
        if (*soc < m_limits.minSocPercent) {
            return {.verdict = BatteryVerdict::DenyLowSoc, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }

        // 4. Активний стрес-тест імпедансу комірки
        const uint16_t vIdle = hal.readVoltageMv();
        if (vIdle < m_limits.vBorSafeMv) {
            return {.verdict = BatteryVerdict::DenyLowSoc, .forecastVoltageMv = vIdle, .measuredEsrMilliOhm = 0};
        }

        // Вмикаємо навантаження на 15 мілісекунд
        hal.setTestLoad(true);
        hal.delayMs(15);
        const uint16_t vLoad = hal.readVoltageMv();
        hal.setTestLoad(false);

        // Пауза релаксації для відновлення хімічного стану поверхні електродів
        hal.delayMs(50);

        if (vLoad > vIdle) {
            return {.verdict = BatteryVerdict::DenySensorFail, .forecastVoltageMv = 0, .measuredEsrMilliOhm = 0};
        }

        const uint16_t deltaVTest = vIdle - vLoad;
        const auto esrMilliOhm = static_cast<uint16_t>(
            (static_cast<uint32_t>(deltaVTest) * 1000) / m_limits.testLoadCurrentMa
        );

        const auto deltaVOta = static_cast<uint32_t>(
            (static_cast<uint32_t>(deltaVTest) * m_limits.otaPeakCurrentMa) / m_limits.testLoadCurrentMa
        );

        if (deltaVOta >= vIdle) {
            return {.verdict = BatteryVerdict::DenyHighEsr, .forecastVoltageMv = 0, .measuredEsrMilliOhm = esrMilliOhm};
        }

        const auto vForecast = static_cast<uint16_t>(vIdle - deltaVOta);

        if (vForecast < m_limits.vBorSafeMv) {
            return {
                .verdict = BatteryVerdict::DenyHighEsr,
                .forecastVoltageMv = vForecast,
                .measuredEsrMilliOhm = esrMilliOhm
            };
        }

        return {
            .verdict = BatteryVerdict::AllowBatteryOk,
            .forecastVoltageMv = vForecast,
            .measuredEsrMilliOhm = esrMilliOhm
        };
    }

private:
    SafetyLimits m_limits;
};

} // namespace embedded::power
