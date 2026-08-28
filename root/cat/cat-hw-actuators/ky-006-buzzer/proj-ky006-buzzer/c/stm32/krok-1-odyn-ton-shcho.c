#include "main.h"     // CubeMX: ніжка зумера — вихід TIM3_CH1 у режимі PWM

extern TIM_HandleTypeDef htim3;

#define BUZ_TIM      (&htim3)
#define BUZ_CH       TIM_CHANNEL_1
#define BUZ_TICK_HZ  1000000U   // прескалер уже поділив таймер до 1 МГц

static uint32_t toneOffAt = 0;  // HAL_GetTick(), коли вимкнути тон
static bool     toneOn    = false;

// Тон = ШІМ 50 % на потрібній частоті: період кладемо в ARR, половину — в CCR.
static void buzzerTone(uint32_t freq)   // ← тутешній відповідник tone()
{
    uint32_t arr = BUZ_TICK_HZ / freq - 1U;
    __HAL_TIM_SET_AUTORELOAD(BUZ_TIM, arr);
    __HAL_TIM_SET_COMPARE(BUZ_TIM, BUZ_CH, arr / 2U);
    HAL_TIM_PWM_Start(BUZ_TIM, BUZ_CH);
}

static void buzzerOff(void)             // ← тутешній відповідник noTone()
{
    HAL_TIM_PWM_Stop(BUZ_TIM, BUZ_CH);
}

void beep(uint32_t freq, uint32_t dur)
{
    buzzerTone(freq);                 // таймер жене меандр; ми не чекаємо
    toneOffAt = HAL_GetTick() + dur;  // запам'ятали ДЕДЛАЙН, а не «спимо dur мс»
    toneOn    = true;
}

// Кликати на КОЖНОМУ витку while(1): гляне на годинник і вимкне тон, коли час.
void buzzerUpdate(void)
{
    if (toneOn && HAL_GetTick() >= toneOffAt) {
        buzzerOff();
        toneOn = false;
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM3_Init();

    beep(1000, 200);                // пікнули 1 кГц на 200 мс
    while (1) {
        buzzerUpdate();             // ← зумер обслуговується тут, фоном
        // ...будь-яка інша робота: кнопки, давачі, мотор — усе жваве...
    }
}
