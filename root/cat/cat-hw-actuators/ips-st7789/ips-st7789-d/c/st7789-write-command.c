/* Реалізація базового протоколу передачі команд та ініціалізації на C */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Оголошення зовнішніх апаратних функцій платформи */
extern void platform_spi_write_byte(uint8_t data);
extern void platform_spi_write_buffer(const uint8_t *data, size_t len);
extern void platform_gpio_set_cs(bool level);
extern void platform_gpio_set_dc(bool level);
extern void platform_delay_ms(uint32_t ms);

/* Надсилання одного байта команди (DC = 0) */
void st7789_write_command(uint8_t cmd) {
    platform_gpio_set_dc(false); /* Режим команди */
    platform_gpio_set_cs(false); /* Вибір пристрою */
    platform_spi_write_byte(cmd);
    platform_gpio_set_cs(true);  /* Деактивація вибору */
}

/* Надсилання байта даних чи параметра (DC = 1) */
void st7789_write_data_byte(uint8_t data) {
    platform_gpio_set_dc(true);  /* Режим даних */
    platform_gpio_set_cs(false);
    platform_spi_write_byte(data);
    platform_gpio_set_cs(true);
}

/* Послідовність початкової ініціалізації ST7789 для 1.3" IPS */
void st7789_init_display(void) {
    st7789_write_command(0x01); /* SWRESET: Програмне скидання */
    platform_delay_ms(150);     /* Очікування завершення скидання */

    st7789_write_command(0x11); /* SLPOUT: Вихід зі сплячого режиму */
    platform_delay_ms(120);     /* Очікування стабілізації помп заряду */

    st7789_write_command(0x3A); /* COLMOD: Встановлення формату пікселя */
    st7789_write_data_byte(0x55); /* 16-бітний колір RGB565 (2 байти/піксель) */

    st7789_write_command(0x36); /* MADCTL: Напрямок сканування пам'яті */
    st7789_write_data_byte(0x00); /* Стандартна орієнтація, RGB порядок субпікселів */

    st7789_write_command(0x21); /* INVON: Обов'язкова інверсія для normally black IPS */
    platform_delay_ms(10);

    st7789_write_command(0x29); /* DISPON: Ввімкнення виводу зображення */
    platform_delay_ms(20);
}
