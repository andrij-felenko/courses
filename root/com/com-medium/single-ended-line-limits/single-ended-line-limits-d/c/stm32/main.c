/* Налаштування GPIO у мікроконтролерах STM32 (HAL / LL)
 * Для ліній SPI або UART на частотах до 10-20 МГц слід обирати
 * помірну швидкість наростання замість максимальної VERY_HIGH. */

GPIO_InitTypeDef gpio = {0};
gpio.Pin = GPIO_PIN_5 | GPIO_PIN_7; // SCK, MOSI
gpio.Mode = GPIO_MODE_AF_PP;
gpio.Pull = GPIO_NOPULL;

/* GPIO_SPEED_FREQ_LOW     : t_rise ≈ 20-50 нс (ідеально для I2C, UART)
 * GPIO_SPEED_FREQ_MEDIUM  : t_rise ≈ 10-15 нс (для SPI до 10-15 МГц)
 * GPIO_SPEED_FREQ_HIGH    : t_rise ≈ 4-6 нс
 * GPIO_SPEED_FREQ_VERY_HIGH: t_rise ≈ 1.2-2 нс (джерело сильного дзвону!) */
gpio.Speed = GPIO_SPEED_FREQ_MEDIUM;

HAL_GPIO_Init(GPIOA, &gpio);
