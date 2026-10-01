#include <stm32g4xx_ll_tim.h>
#include <stm32g4xx_ll_bus.h>

class ComplementaryPwm {
public:
    static void initTimer1() {
        LL_APB2_GRP1_EnableClock(LL_APB2_GRP1_PERIPH_TIM1);

        LL_TIM_SetPrescaler(TIM1, 0);
        LL_TIM_SetAutoReload(TIM1, 4249);
        LL_TIM_OC_SetMode(TIM1, LL_TIM_CHANNEL_CH1, LL_TIM_OCMODE_PWM1);
        LL_TIM_OC_SetCompareCH1(TIM1, 2125);
        
        // Встановлення тривалості мертвильного інтервалу
        LL_TIM_OC_SetDeadTime(TIM1, 85);
        LL_TIM_CC_EnableChannel(TIM1, LL_TIM_CHANNEL_CH1 | LL_TIM_CHANNEL_CH1N);
        LL_TIM_EnableAllOutputs(TIM1);
        LL_TIM_EnableCounter(TIM1);
    }
};
