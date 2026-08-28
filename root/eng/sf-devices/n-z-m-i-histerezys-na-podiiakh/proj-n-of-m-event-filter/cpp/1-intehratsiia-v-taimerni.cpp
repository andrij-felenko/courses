#include "main.h"
#include "event_filter_modern.hpp"

using namespace embedded::filter;

// Типобезпечні C++ фільтри без глобальних C-структур
static ModernEventFilter<16, 12, 4>        buttonFilter{false};
static ModernEventFilter<8, 6, 2, 5000>    sensorFilter{false};

extern "C" void TIM6_DAC_IRQHandler() noexcept {
    if (LL_TIM_IsActiveFlag_UPDATE(TIM6)) {
        LL_TIM_ClearFlag_UPDATE(TIM6);

        const bool raw_btn = (LL_GPIO_IsInputPinSet(GPIOC, LL_GPIO_PIN_13) == 0);
        const bool raw_sns = (LL_GPIO_IsInputPinSet(GPIOA, LL_GPIO_PIN_0) != 0);

        buttonFilter.Update(raw_btn);
        sensorFilter.Update(raw_sns);
    }
}
