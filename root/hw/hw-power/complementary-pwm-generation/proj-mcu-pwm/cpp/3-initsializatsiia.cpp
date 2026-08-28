#include "stm32f4xx_ll_tim.h"
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"

namespace power_control {

class HalfBridgePwmDriver {
public:
    struct Config {
        uint32_t timer_clk_hz{168'000'000};
        uint32_t pwm_freq_hz{50'000};
        uint32_t dead_time_ns{150};
    };

    explicit HalfBridgePwmDriver(const Config& cfg) noexcept : config_(cfg) {}

    void initialize() noexcept {
        enable_peripheral_clocks();
        configure_gpios();
        configure_timebase();
        configure_channel();
        configure_break_deadtime();

        LL_TIM_EnableARRPreload(TIM1);
        LL_TIM_EnableAllOutputs(TIM1);
        LL_TIM_EnableCounter(TIM1);
    }

    void set_duty_cycle(float duty_ratio) noexcept {
        const uint32_t arr = LL_TIM_GetAutoReload(TIM1);
        const uint32_t ccr = static_cast<uint32_t>(duty_ratio * static_cast<float>(arr));
        LL_TIM_OC_SetCompareCH1(TIM1, ccr);
    }

    bool is_break_triggered() const noexcept {
        return LL_TIM_IsActiveFlag_BRK(TIM1) != 0;
    }

    void clear_break_and_rearm() noexcept {
        LL_TIM_ClearFlag_BRK(TIM1);
        LL_TIM_EnableAllOutputs(TIM1); // Повторне зведення біта MOE
    }

private:
    Config config_;

    void enable_peripheral_clocks() noexcept {
        LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_TIM1);
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
        LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
    }

    void configure_gpios() noexcept {
        LL_GPIO_InitTypeDef gpio = {};
        gpio.Pin = LL_GPIO_PIN_8;
        gpio.Mode = LL_GPIO_MODE_ALTERNATE;
        gpio.Speed = LL_GPIO_SPEED_FREQ_VERY_HIGH;
        gpio.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
        gpio.Alternate = LL_GPIO_AF_1;
        LL_GPIO_Init(GPIOA, &gpio);

        gpio.Pin = LL_GPIO_PIN_13;
        LL_GPIO_Init(GPIOB, &gpio);

        gpio.Pin = LL_GPIO_PIN_6;
        gpio.Pull = LL_GPIO_PULL_DOWN;
        LL_GPIO_Init(GPIOA, &gpio);
    }

    void configure_timebase() noexcept {
        const uint32_t arr = config_.timer_clk_hz / (2 * config_.pwm_freq_hz);
        LL_TIM_InitTypeDef tb = {};
        tb.Prescaler = 0;
        tb.CounterMode = LL_TIM_COUNTERMODE_CENTER_UP_DOWN;
        tb.Autoreload = arr - 1;
        tb.ClockDivision = LL_TIM_CLOCKDIVISION_DIV1;
        LL_TIM_Init(TIM1, &tb);
    }

    void configure_channel() noexcept {
        LL_TIM_OC_InitTypeDef oc = {};
        oc.OCMode = LL_TIM_OCMODE_PWM1;
        oc.OCState = LL_TIM_OCSTATE_ENABLE;
        oc.OCNState = LL_TIM_OCNSTATE_ENABLE;
        oc.OCPolarity = LL_TIM_OCPOLARITY_HIGH;
        oc.OCNPolarity = LL_TIM_OCNPOLARITY_HIGH;
        oc.OCIdleState = LL_TIM_OCIDLESTATE_LOW;
        oc.OCNIdleState = LL_TIM_OCIDLESTATE_LOW;
        oc.CompareValue = LL_TIM_GetAutoReload(TIM1) / 2;
        LL_TIM_OC_Init(TIM1, LL_TIM_CHANNEL_CH1, &oc);
        LL_TIM_OC_EnablePreload(TIM1, LL_TIM_CHANNEL_CH1);
    }

    void configure_break_deadtime() noexcept {
        const uint8_t dtg = Stm32DeadTimeCalculator::calculate_dtg(
            config_.dead_time_ns, config_.timer_clk_hz);

        LL_TIM_BDTR_InitTypeDef bdtr = {};
        bdtr.OSSRState = LL_TIM_OSSR_ENABLE;
        bdtr.OSSIState = LL_TIM_OSSI_ENABLE;
        bdtr.LockLevel = LL_TIM_LOCKLEVEL_1;
        bdtr.DeadTime = dtg;
        bdtr.BreakState = LL_TIM_BREAK_ENABLE;
        bdtr.BreakPolarity = LL_TIM_BREAK_POLARITY_HIGH;
        bdtr.BreakFilter = LL_TIM_BREAK_FILTER_FDIV1_N4;
        bdtr.AutomaticOutput = LL_TIM_AUTOMATIC_OUTPUT_DISABLE;
        LL_TIM_BDTR_Init(TIM1, &bdtr);
    }
};

} // namespace power_control
