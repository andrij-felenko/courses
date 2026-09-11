#include <stdint.h>
#include <stddef.h>

/**
 * @brief Дескриптор дисплея ST7789 з апаратно-незалежним шаром (HAL).
 */
typedef struct st7789 {
    /* Покажчики на апаратні функції платформи */
    void (*spi_write)(const uint8_t *data, size_t length, void *user_data);
    void (*set_cs)(uint8_t level, void *user_data);
    void (*set_dc)(uint8_t level, void *user_data);
    void (*set_rst)(uint8_t level, void *user_data);
    void (*set_blk)(uint8_t level, void *user_data);
    void (*delay_ms)(uint32_t ms);

    /* Геометрія та параметри відображення */
    uint16_t width;      /* Поточна ширина екрана в пікселях */
    uint16_t height;     /* Поточна висота екрана в пікселях */
    uint8_t  rotation;   /* Кут повороту (0: 0°, 1: 90°, 2: 180°, 3: 270°) */
    uint16_t x_offset;   /* Апаратне зміщення по осі X у пам'яті GRAM */
    uint16_t y_offset;   /* Апаратне зміщення по осі Y у пам'яті GRAM */

    /* Контекст користувача для прив'язки до заліза */
    void *user_data;
} st7789_t;
