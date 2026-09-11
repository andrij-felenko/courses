/* Апаратний драйвер ліній керування ST7789 на базі STM32 HAL */
#include "main.h"

#define LCD_DC_PORT   GPIOB
#define LCD_DC_PIN    GPIO_PIN_1
#define LCD_RES_PORT  GPIOB
#define LCD_RES_PIN   GPIO_PIN_2

extern SPI_HandleTypeDef hspi1;

/* Апаратне скидання дисплея з дотриманням часових меж */
void st7789_hw_reset(void) {
    /* Активний імпульс низького рівня */
    HAL_GPIO_WritePin(LCD_RES_PORT, LCD_RES_PIN, GPIO_PIN_RESET);
    HAL_Delay(1); /* 1 мс — гарантовано більше за мінімальні 10 мкс */

    /* Звільнення шини скидання у високий рівень */
    HAL_GPIO_WritePin(LCD_RES_PORT, LCD_RES_PIN, GPIO_PIN_SET);

    /* Пауза 120 мс для стабілізації внутрішніх помп напруги */
    HAL_Delay(120);
}

/* Передавання однобайтної команди: лінія DC = 0 */
void st7789_write_command(uint8_t cmd) {
    HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_RESET);
    HAL_SPI_Transmit(&hspi1, &cmd, 1, HAL_MAX_DELAY);
}

/* Передавання одного байта параметра або конфігурації: лінія DC = 1 */
void st7789_write_data(uint8_t data) {
    HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);
    HAL_SPI_Transmit(&hspi1, &data, 1, HAL_MAX_DELAY);
}

/* Швидкісне надсилання масиву піксельних даних у фреймбуфер */
void st7789_write_pixel_buffer(const uint8_t *buffer, uint16_t length) {
    HAL_GPIO_WritePin(LCD_DC_PORT, LCD_DC_PIN, GPIO_PIN_SET);
    HAL_SPI_Transmit(&hspi1, (uint8_t *)buffer, length, HAL_MAX_DELAY);
}
