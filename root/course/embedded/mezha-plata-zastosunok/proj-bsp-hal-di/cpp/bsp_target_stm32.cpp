// --- bsp_target_stm32.cpp: Реалізація IBoardSupport для STM32 ---
#include "supervisor.hpp"
#include "stm32f4xx_hal.h"

extern ADC_HandleTypeDef hadc1;
extern I2C_HandleTypeDef hi2c1;

namespace bsp {

class Stm32TargetBoard final : public IBoardSupport {
public:
    Status init() noexcept override { return Status::Ok; }
    Status deinit() noexcept override { return Status::Ok; }

    Status led_set(LedId led, LedState state) noexcept override {
        const auto pin_state = (state == LedState::On) ? GPIO_PIN_SET : GPIO_PIN_RESET;
        if (led == LedId::SystemStatus) {
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, pin_state);
            return Status::Ok;
        } else if (led == LedId::Warning) {
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, pin_state);
            return Status::Ok;
        }
        return Status::InvalidParam;
    }

    Status led_toggle(LedId led) noexcept override {
        if (led == LedId::SystemStatus) {
            HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_12);
            return Status::Ok;
        }
        return Status::InvalidParam;
    }

    Status power_domain_set(PowerDomain domain, bool enable) noexcept override {
        if (domain == PowerDomain::Sensors) {
            HAL_GPIO_WritePin(GPIOE, GPIO_PIN_3, enable ? GPIO_PIN_RESET : GPIO_PIN_SET);
            if (enable) {
                HAL_Delay(15);
            }
            return Status::Ok;
        }
        return Status::Unsupported;
    }

    std::expected<BatteryMetrics, Status> get_battery_metrics() noexcept override {
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
            const uint32_t raw = HAL_ADC_GetValue(&hadc1);
            const uint32_t v_pin = (raw * 3300) / 4095;
            BatteryMetrics m;
            m.voltage_mv = static_cast<uint16_t>((v_pin * 3) / 2);
            m.is_critical_low = (m.voltage_mv < 3000);
            return m;
        }
        return std::unexpected(Status::Timeout);
    }

    std::expected<EnvironmentMetrics, Status> read_environment() noexcept override {
        uint8_t raw[6] = {0};
        if (HAL_I2C_Mem_Read(&hi2c1, 0x76 << 1, 0xF7, 1, raw, 6, 50) == HAL_OK) {
            const int32_t temp_raw = (raw[3] << 12) | (raw[4] << 4) | (raw[5] >> 4);
            EnvironmentMetrics env;
            env.temperature_centi_c = static_cast<int16_t>((temp_raw * 100) / 5120);
            return env;
        }
        return std::unexpected(Status::BusFault);
    }

    Status enter_low_power(SleepMode mode, std::chrono::milliseconds) noexcept override {
        if (mode == SleepMode::Deep) {
            HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
            return Status::Ok;
        }
        return Status::Unsupported;
    }

    std::chrono::milliseconds get_uptime() const noexcept override {
        return std::chrono::milliseconds(HAL_GetTick());
    }

    void delay(std::chrono::microseconds us) const noexcept override {
        uint32_t ticks = (SystemCoreClock / 1000000) * static_cast<uint32_t>(us.count());
        uint32_t start = DWT->CYCCNT;
        while ((DWT->CYCCNT - start) < ticks);
    }
};

} // namespace bsp
