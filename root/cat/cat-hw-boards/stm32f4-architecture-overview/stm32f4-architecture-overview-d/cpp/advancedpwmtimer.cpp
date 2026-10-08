// C++: Обгортка конфігурації генерації симетричного ШІМ-сигналу таймера TIM1 для силового інвертора
#include "stm32f4xx_ll_tim.h"
#include "stm32f4xx_ll_bus.h"

class AdvancedPwmTimer {
private:
    TIM_TypeDef* m_timer;

public:
    explicit AdvancedPwmTimer(TIM_TypeDef* timer) : m_timer(timer) {}

    void init_center_aligned_pwm(uint32_t period_ticks) {
        // Увімкнення тактування таймера TIM1 на шині APB2 (168 МГц після подвоювача)
        LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_TIM1);

        // Налаштування режиму рахунку від центру (Center-aligned mode 1)
        LL_TIM_SetCounterMode(m_timer, LL_TIM_COUNTERMODE_CENTER_DOWN);
        LL_TIM_SetAutoReload(m_timer, period_ticks);

        // Налаштування каналу 1 у режим PWM1 з комплементарними виходами
        LL_TIM_OC_SetMode(m_timer, LL_TIM_CHANNEL_CH1, LL_TIM_OCMODE_PWM1);
        LL_TIM_OC_SetCompareCH1(m_timer, period_ticks / 2);

        // Увімкнення виходів та запуск таймера
        LL_TIM_EnableAllOutputs(m_timer);
        LL_TIM_EnableCounter(m_timer);
    }
};
