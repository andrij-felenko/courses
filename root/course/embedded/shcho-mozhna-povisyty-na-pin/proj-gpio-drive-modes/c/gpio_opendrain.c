/* Файл: gpio_opendrain.c — C реалізація відкритого стоку */
#include "stm32f4xx_ll_gpio.h"

void gpio_init_open_drain(GPIO_TypeDef *port, uint32_t pin)
{
    LL_GPIO_InitTypeDef init;
    init.Pin        = pin;
    init.Mode       = LL_GPIO_MODE_OUTPUT;
    init.OutputType = LL_GPIO_OUTPUT_OPENDRAIN; /* Відкритий стік */
    init.Speed      = LL_GPIO_SPEED_FREQ_MEDIUM;   /* Помірна швидкість */
    init.Pull       = LL_GPIO_PULL_NO;          /* Зовнішня підтяжка на платі */

    LL_GPIO_Init(port, &init);

    /* За замовчуванням відпускаємо вивід у стан Hi-Z (високий рівень від зовнішнього резистора) */
    LL_GPIO_SetOutputPin(port, pin);
}
