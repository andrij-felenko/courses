/* main.c — точка входу цільової прошивки: єдине місце, де переносна
 * логіка зустрічається з конкретною платою. */
#include "bsp_target_stm32.h"
#include "supervisor.h"

#include "stm32f4xx_hal.h"

/* Згенеровані CubeMX ініціалізатори периферії. */
void SystemClock_Config(void);
void MX_GPIO_Init(void);
void MX_ADC1_Init(void);
void MX_I2C1_Init(void);
void MX_RTC_Init(void);

/* Плата не змогла піднятися: блимаємо аварійним світлодіодом,
 * поки сторожовий таймер не перезавантажить систему. */
static void fatal_blink(void)
{
    for (;;) {
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_4);
        HAL_Delay(200);
    }
}

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_I2C1_Init();
    MX_RTC_Init();

    if (stm32_bsp_init() != BSP_STATUS_OK) {
        fatal_blink();
    }

    supervisor_t sup;
    /* Ось і все впровадження залежності: адреса таблиці методів. */
    if (supervisor_init(&sup, &stm32_bsp_driver) != BSP_STATUS_OK) {
        fatal_blink();
    }

    for (;;) {
        supervisor_run_cycle(&sup);

        /* Після критичного розряду супервізор уже відспав годину —
         * другий сон поспіль лише з'їв би час реакції на заряджання. */
        if (!sup.is_critical_shutdown) {
            stm32_bsp_driver.enter_low_power(BOARD_SLEEP_MODE_LIGHT,
                                             SUPERVISOR_CYCLE_PERIOD_MS);
        }
    }
}
