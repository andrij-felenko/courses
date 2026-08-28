#include "stm32f4xx_hal.h"

#define WELD_PORT       GPIOB
#define WELD_PIN        GPIO_PIN_12   // затвор силового MOSFET-ключа
#define PULSE1_US     1500            // «пробити»: 1.5 мс
#define GAP_US        3000            // пауза між імпульсами: 3 мс
#define PULSE2_US     5000            // «зварити»: 5 мс

// HAL_Delay міряє лише мілісекунди — замало. Беремо вільний таймер,
// накручений подільником на 1 МГц: один тик = одна мікросекунда.
extern TIM_HandleTypeDef htim6;

static void delay_us(uint16_t us)
{
    __HAL_TIM_SET_COUNTER(&htim6, 0);
    while (__HAL_TIM_GET_COUNTER(&htim6) < us) { }
}

void fire_weld(void)
{
    __disable_irq();   // жодного переривання посеред імпульсу

    HAL_GPIO_WritePin(WELD_PORT, WELD_PIN, GPIO_PIN_SET);    // пробити оксид
    delay_us(PULSE1_US);
    HAL_GPIO_WritePin(WELD_PORT, WELD_PIN, GPIO_PIN_RESET);

    delay_us(GAP_US);                                        // пауза

    HAL_GPIO_WritePin(WELD_PORT, WELD_PIN, GPIO_PIN_SET);    // сплавити ядро
    delay_us(PULSE2_US);
    HAL_GPIO_WritePin(WELD_PORT, WELD_PIN, GPIO_PIN_RESET);

    __enable_irq();
}
