#include <cstdint>
#include <expected>
#include <span>
#include <concepts>
#include "stm32f4xx_hal.h"

namespace vbat {

enum class BatteryState : uint8_t {
    Good,       // Напруга > 2.8 В, ресурс достатній
    Degraded,   // Напруга 2.4..2.8 В, планова заміна
    Critical,   // Напруга < 2.4 В, загроза втрати даних RTC
    Invalid     // Помилка апаратного вимірювання
};

enum class DriverError : uint8_t {
    AdcConfigFailed,
    ConversionTimeout,
    CalibrationFailed
};

struct DiagnosticReport {
    uint32_t voltage_mv;
    BatteryState state;

    [[nodiscard]] constexpr bool is_safe() const noexcept {
        return state == BatteryState::Good;
    }
};

/**
 * @brief RAII-обгортка для гарантованого відключення вимірювального моста VBAT.
 * Запобігає неперервному витоку струму через мікроконтролерний дільник АЦП.
 */
class VbatBridgeGuard {
public:
    explicit VbatBridgeGuard(ADC_Common_TypeDef* common_regs) noexcept 
        : common_(common_regs) 
    {
        __HAL_RCC_PWR_CLK_ENABLE();
        common_->CCR |= ADC_CCR_VBATE; // Замикаємо міст дільника
    }

    ~VbatBridgeGuard() noexcept {
        common_->CCR &= ~ADC_CCR_VBATE; // Гарантовано розмикаємо міст при виході з області видимості
    }

    VbatBridgeGuard(const VbatBridgeGuard&) = delete;
    VbatBridgeGuard& operator=(const VbatBridgeGuard&) = delete;
    VbatBridgeGuard(VbatBridgeGuard&&) = delete;
    VbatBridgeGuard& operator=(VbatBridgeGuard&&) = delete;

private:
    ADC_Common_TypeDef* common_;
};

class BatteryMonitor {
public:
    static constexpr uint32_t ThresholdGoodMv     = 2800;
    static constexpr uint32_t ThresholdWarningMv  = 2400;
    static constexpr uint32_t DividerRatio        = 4;     // Дільник 1/4
    static constexpr uint32_t AdcMaxCounts        = 4095;  // 12-бітний АЦП

    explicit BatteryMonitor(ADC_HandleTypeDef& adc_handle) noexcept 
        : adc_handle_(adc_handle) {}

    [[nodiscard]] std::expected<DiagnosticReport, DriverError> sample(uint32_t vdda_mv = 3300) noexcept {
        // Застосовуємо RAII guard: міст буде відключено автоматично при будь-якому поверненні
        VbatBridgeGuard bridge_guard(ADC);

        ADC_ChannelConfTypeDef config{};
        config.Channel      = ADC_CHANNEL_VBAT;
        config.Rank         = 1;
        config.SamplingTime = ADC_SAMPLETIME_480CYCLES;

        if (HAL_ADC_ConfigChannel(&adc_handle_, &config) != HAL_OK) {
            return std::unexpected(DriverError::AdcConfigFailed);
        }

        if (HAL_ADC_Start(&adc_handle_) != HAL_OK) {
            return std::unexpected(DriverError::AdcConfigFailed);
        }

        if (HAL_ADC_PollForConversion(&adc_handle_, 10) != HAL_OK) {
            HAL_ADC_Stop(&adc_handle_);
            return std::unexpected(DriverError::ConversionTimeout);
        }

        const uint32_t raw = HAL_ADC_GetValue(&adc_handle_);
        HAL_ADC_Stop(&adc_handle_);

        const uint32_t measured_mv = (raw * vdda_mv * DividerRatio) / AdcMaxCounts;
        const BatteryState state   = evaluate_state(measured_mv);

        return DiagnosticReport{ .voltage_mv = measured_mv, .state = state };
    }

private:
    ADC_HandleTypeDef& adc_handle_;

    [[nodiscard]] static constexpr BatteryState evaluate_state(uint32_t mv) noexcept {
        if (mv >= ThresholdGoodMv) {
            return BatteryState::Good;
        }
        if (mv >= ThresholdWarningMv) {
            return BatteryState::Degraded;
        }
        return BatteryState::Critical;
    }
};

} // namespace vbat
