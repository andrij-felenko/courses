/* ============================================================================
   krok-3-zero-cross-relay.c — STM32 HAL: комутація реле синхронно з нулем фази
   ========================================================================== */

#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define RELAY_PIN               GPIO_PIN_1
#define RELAY_PORT              GPIOA
#define RELAY_PULLIN_TIME_US    6000    // Механічний час спрацьовування котушки
#define HALF_CYCLE_US           10000   // Напівперіод 50 Гц = 10 мс

static volatile bool s_target_state = false;
static volatile bool s_switch_pending = false;

extern TIM_HandleTypeDef htim2;

// Викликається з EXTI переривання оптопари при переході через 0
void mains_on_zero_cross_event(void) {
    if (s_switch_pending) {
        // Щоб контакт замикався на нулі, запускаємо таймер із затримкою:
        // delay = 10000 мкс - 6000 мкс = 4000 мкс
        uint32_t delay_ticks = HALF_CYCLE_US - RELAY_PULLIN_TIME_US;
        __HAL_TIM_SET_AUTORELOAD(&htim2, delay_ticks);
        __HAL_TIM_SET_COUNTER(&htim2, 0);
        HAL_TIM_Base_Start_IT(&htim2);
        s_switch_pending = false;
    }
}

// Обробник переривання таймера TIM2: спрацьовує в розраховану фазову точку
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM2) {
        HAL_TIM_Base_Stop_IT(&htim2);
        HAL_GPIO_WritePin(RELAY_PORT, RELAY_PIN, s_target_state ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }
}

void mains_schedule_relay_state(bool state) {
    s_target_state = state;
    s_switch_pending = true;
}
