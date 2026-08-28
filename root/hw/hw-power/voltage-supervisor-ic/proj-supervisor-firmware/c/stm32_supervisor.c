/* stm32_supervisor.c — C-реалізація */
#include "main.h"
#include <stdint.h>
#include <stdbool.h>

#define TASK_SENSOR_BIT   (1U << 0)
#define TASK_CONTROL_BIT  (1U << 1)
#define TASK_COMMS_BIT    (1U << 2)
#define TASKS_ALL_MASK    (TASK_SENSOR_BIT | TASK_CONTROL_BIT | TASK_COMMS_BIT)

static volatile uint32_t s_health_flags = 0;
static volatile bool s_power_fail_active = false;
static uint32_t s_last_wdt_kick_ms = 0;

void Task_ReportHealth(uint32_t task_bit) {
    __disable_irq();
    s_health_flags |= task_bit;
    __enable_irq();
}

/* Обробник раннього переривання зникнення живлення PFI (EXTI Line) */
void EXTI0_IRQHandler(void) {
    if (__HAL_GPIO_EXTI_GET_IT(PFO_PIN_Pin) != RESET) {
        __HAL_GPIO_EXTI_CLEAR_IT(PFO_PIN_Pin);
        s_power_fail_active = true;

        /* 1. Негайне відключення потужних периферійних модулів */
        HAL_GPIO_WritePin(PERIPH_PWR_EN_GPIO_Port, PERIPH_PWR_EN_Pin, GPIO_PIN_RESET);
        
        /* 2. Аварійне збереження стану в енергонезалежну FRAM через SPI */
        Save_Critical_State_Emergency();
    }
}

/* Періодична функція обслуговування віконного сторожа */
void WDT_Service_Routine(void) {
    if (s_power_fail_active) {
        return; /* Не обслуговуємо сторож, дозволяємо чисте апаратне скидання */
    }

    uint32_t now = HAL_GetTick();
    uint32_t delta = now - s_last_wdt_kick_ms;

    /* Вікно супервізора: min 35 мс, max 85 мс */
    if (delta >= 45 && delta <= 75) {
        if ((s_health_flags & TASKS_ALL_MASK) == TASKS_ALL_MASK) {
            /* Усі задачі відзвітували — смикаємо вивід WDI */
            HAL_GPIO_TogglePin(WDI_GPIO_Port, WDI_Pin);
            s_health_flags = 0;
            s_last_wdt_kick_ms = now;
        }
    }
}
