#ifndef ADC_CONFIG_HPP
#define ADC_CONFIG_HPP

#include <cstdint>

/**
 * @brief Перелічення джерел опорної напруги аналого-цифрового перетворювача (АЦП).
 */
enum class AdcReference : uint8_t {
    DefaultVcc,     ///< Зовнішнє живлення шини (VCC, зазвичай 5,0 В або 3,3 В)
    Internal1V1,    ///< Внутрішнє стабільне джерело опорної напруги 1,1 В
    ExternalRef     ///< Зовнішня опорна напруга на виводі AREF
};

/**
 * @brief Перелічення роздільної здатності АЦП у бітах.
 */
enum class AdcResolution : uint8_t {
    Bits10 = 10,    ///< 10-бітний АЦП (1024 рівні дискретизації)
    Bits12 = 12     ///< 12-бітний АЦП (4096 рівнів дискретизації)
};

/**
 * @brief Допоміжна структура конфігурації АЦП мікроконтролера.
 */
struct AdcConfig {
    AdcReference reference{AdcReference::Internal1V1}; ///< Джерело опорної напруги (1,1 В за замовчуванням)
    float ref_voltage_v{1.1f};                         ///< Значення опорної напруги у вольтах (1,1 В)
    AdcResolution resolution{AdcResolution::Bits10};   ///< Роздільна здатність АЦП у бітах
    uint8_t analog_pin{0};                             ///< Номер аналогового каналу (входу)

    /**
     * @brief Обчислення максимального дискретного значення АЦП (2^N - 1).
     */
    constexpr uint32_t maxAdcValue() const noexcept {
        return (1U << static_cast<uint8_t>(resolution)) - 1U;
    }
};

/**
 * @brief Структура збереження параметрів калібрування аналогового тракту.
 */
struct CalibrationParams {
    float offset_celsius{0.0f};  ///< Адитивна калібрувальна поправка (температурний зсув у °C)
    float scale_factor{1.0f};    ///< Мультиплікативна калібрувальна поправка (масштабування)
};

#endif // ADC_CONFIG_HPP
