#include "stm32f4xx_hal.h"

extern TIM_HandleTypeDef htim3;   // TIM3 у режимі PWM, ARR = 4095 → ті самі 12 біт

// дві обгортки — уся платформозалежність рушія
static uint32_t millis(void) { return HAL_GetTick(); }   // той самий лічильник мс

static const uint32_t chMap[] = { TIM_CHANNEL_1, TIM_CHANNEL_2 };
static void ledcWrite(uint8_t ch, uint32_t duty) {
    __HAL_TIM_SET_COMPARE(&htim3, chMap[ch], duty);      // duty 0..4095 лягає прямо в CCR
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM3_Init();          // PSC підібрано так, щоб при ARR = 4095 вийшло ~5 кГц
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
    buildLUT();
    buildShapeTables();

    animStart(0, ANIM_PINGPONG, shapeBreathe, 4000, false);
    queueStart(0, /*канал=*/1, /*invert=*/false, alarmThenCalm, 2);

    while (1) {
        uint32_t now = HAL_GetTick();
        animTick(now);     // посунути всі ефекти
        queueTick();       // просунути всі черги
        // ↓ цикл вільний: кнопки, зв'язок, давачі — усе живе тут, нічого не блоковано
    }
}
