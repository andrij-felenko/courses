/**
 * @file st7789.c
 * @brief Реалізація драйвера дисплея ST7789 для мікроконтролерів.
 */

#include "st7789.h"

/* Внутрішня допоміжна функція передавання одиночного байта команди */
static void write_command(st7789_dev_t *dev, uint8_t cmd) {
    dev->hal.dc_write(0U); /* Режим команди */
    dev->hal.cs_write(0U); /* Активація дисплея */
    dev->hal.spi_send_blocking(&cmd, 1U);
    dev->hal.cs_write(1U); /* Деактивація лінії вибору */
}

/* Внутрішня допоміжна функція передавання масиву байтів даних */
static void write_data(st7789_dev_t *dev, const uint8_t *data, uint16_t length) {
    if (length == 0U) {
        return;
    }
    dev->hal.dc_write(1U); /* Режим даних */
    dev->hal.cs_write(0U); /* Активація дисплея */
    dev->hal.spi_send_blocking(data, length);
    dev->hal.cs_write(1U); /* Деактивація лінії вибору */
}

/* Внутрішня допоміжна функція передавання одного байта даних */
static void write_data_byte(st7789_dev_t *dev, uint8_t byte) {
    write_data(dev, &byte, 1U);
}

void st7789_init(st7789_dev_t *dev, const st7789_hal_t *hal, uint16_t x_offset, uint16_t y_offset) {
    dev->hal = *hal;
    dev->width = ST7789_WIDTH;
    dev->height = ST7789_HEIGHT;
    dev->x_offset = x_offset;
    dev->y_offset = y_offset;
    dev->dma_busy = false;

    /* 1. Апаратний цикл скидання контролера */
    dev->hal.cs_write(1U);
    dev->hal.dc_write(1U);
    dev->hal.rst_write(0U);
    dev->hal.delay_ms(20U);
    dev->hal.rst_write(1U);
    dev->hal.delay_ms(120U);

    /* 2. Програмне скидання внутрішніх регістрів */
    write_command(dev, ST7789_CMD_SWRESET);
    dev->hal.delay_ms(120U);

    /* 3. Вихід із режиму енергозбереження */
    write_command(dev, ST7789_CMD_SLPOUT);
    dev->hal.delay_ms(120U);

    /* 4. Конфігурація кольоровості: 16 біт (RGB565) */
    write_command(dev, ST7789_CMD_COLMOD);
    write_data_byte(dev, ST7789_COLOR_MODE_16BIT);
    dev->hal.delay_ms(10U);

    /* 5. Керування орієнтацією відображення: стандартний напрямок стовпчиків і рядків */
    write_command(dev, ST7789_CMD_MADCTL);
    write_data_byte(dev, 0x00U);

    /* 6. Налаштування тривалості гасіння рядків (Porch control) */
    write_command(dev, ST7789_CMD_PORCTRL);
    {
        const uint8_t porch_data[] = {0x0CU, 0x0CU, 0x00U, 0x33U, 0x33U};
        write_data(dev, porch_data, sizeof(porch_data));
    }

    /* 7. Налаштування напруги керування затворами матриці (Gate Control: Vgh=13.26V, Vgl=-10.43V) */
    write_command(dev, ST7789_CMD_GCTRL);
    write_data_byte(dev, 0x35U);

    /* 8. Рівень VCOM = 0.9V для мінімізації мерехтіння рідких кристалів */
    write_command(dev, ST7789_CMD_VCOMS);
    write_data_byte(dev, 0x19U);

    /* 9. Керування живленням LCM */
    write_command(dev, ST7789_CMD_LCMCTRL);
    write_data_byte(dev, 0x2CU);

    /* 10. Дозвіл керування параметрами VDV і VRH */
    write_command(dev, ST7789_CMD_VDVVRHEN);
    write_data_byte(dev, 0x01U);

    /* 11. Напруга VRH = 4.3V */
    write_command(dev, ST7789_CMD_VRHS);
    write_data_byte(dev, 0x12U);

    /* 12. Напруга VDV = 0V */
    write_command(dev, ST7789_CMD_VDVS);
    write_data_byte(dev, 0x20U);

    /* 13. Частота оновлення кадру: 60 Гц у нормальному режимі */
    write_command(dev, ST7789_CMD_FRCTRL2);
    write_data_byte(dev, 0x0FU);

    /* 14. Базова потужність і конфігурація стабілізатора */
    write_command(dev, ST7789_CMD_PWCTRL1);
    {
        const uint8_t pw_data[] = {0xA4U, 0xA1U};
        write_data(dev, pw_data, sizeof(pw_data));
    }

    /* 15. Калібрування кривої гамми (позитивна напівхвиля) */
    write_command(dev, ST7789_CMD_PVGAMCTRL);
    {
        const uint8_t gamma_pos[] = {
            0xD0U, 0x04U, 0x0DU, 0x11U, 0x13U, 0x2BU, 0x3FU,
            0x54U, 0x4CU, 0x18U, 0x0DU, 0x0BU, 0x1FU, 0x23U
        };
        write_data(dev, gamma_pos, sizeof(gamma_pos));
    }

    /* 16. Калібрування кривої гамми (негативна напівхвиля) */
    write_command(dev, ST7789_CMD_NVGAMCTRL);
    {
        const uint8_t gamma_neg[] = {
            0xD0U, 0x04U, 0x0CU, 0x11U, 0x13U, 0x2CU, 0x3FU,
            0x44U, 0x51U, 0x2FU, 0x1FU, 0x1FU, 0x20U, 0x23U
        };
        write_data(dev, gamma_neg, sizeof(gamma_neg));
    }

    /* 17. Обов'язкова інверсія кольору для панелей IPS (Normal Black) */
    write_command(dev, ST7789_CMD_INVON);
    dev->hal.delay_ms(10U);

    /* 18. Увімкнення нормального режиму відтворення */
    write_command(dev, ST7789_CMD_NORON);
    dev->hal.delay_ms(10U);

    /* 19. Активація відображення матриці */
    write_command(dev, ST7789_CMD_DISPON);
    dev->hal.delay_ms(120U);
}

void st7789_set_window(st7789_dev_t *dev, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    const uint16_t real_x0 = x0 + dev->x_offset;
    const uint16_t real_x1 = x1 + dev->x_offset;
    const uint16_t real_y0 = y0 + dev->y_offset;
    const uint16_t real_y1 = y1 + dev->y_offset;

    /* Встановлення вікна стовпчиків (Column Address Set) */
    write_command(dev, ST7789_CMD_CASET);
    {
        const uint8_t col_data[4] = {
            (uint8_t)(real_x0 >> 8U), (uint8_t)(real_x0 & 0xFFU),
            (uint8_t)(real_x1 >> 8U), (uint8_t)(real_x1 & 0xFFU)
        };
        write_data(dev, col_data, sizeof(col_data));
    }

    /* Встановлення вікна рядків (Row Address Set) */
    write_command(dev, ST7789_CMD_RASET);
    {
        const uint8_t row_data[4] = {
            (uint8_t)(real_y0 >> 8U), (uint8_t)(real_y0 & 0xFFU),
            (uint8_t)(real_y1 >> 8U), (uint8_t)(real_y1 & 0xFFU)
        };
        write_data(dev, row_data, sizeof(row_data));
    }

    /* Підготовка до безпосереднього запису масиву пікселів у відеопам'ять */
    write_command(dev, ST7789_CMD_RAMWR);
}

void st7789_send_line_dma(st7789_dev_t *dev, const uint16_t *line_buffer, uint16_t pixel_count) {
    /* Очікуємо закінчення попередньої транзакції, якщо попередня ще не завершилась */
    while (dev->dma_busy) {
        /* Очікування виставлення прапорця з обробника переривання DMA */
    }

    dev->dma_busy = true;

    /* Переводимо дисплей у режим даних і активуємо шину */
    dev->hal.dc_write(1U);
    dev->hal.cs_write(0U);

    /* Розмір буфера в байтах дорівнює pixel_count * 2 для 16-бітного RGB565 */
    const uint16_t byte_count = pixel_count * (uint16_t)sizeof(uint16_t);
    dev->hal.spi_send_dma((const uint8_t *)line_buffer, byte_count);
}

bool st7789_is_busy(const st7789_dev_t *dev) {
    return dev->dma_busy;
}

void st7789_wait_dma_finish(volatile st7789_dev_t *dev) {
    while (dev->dma_busy) {
        /* Чекаємо скидання dma_busy в st7789_dma_transfer_complete_callback */
    }
}

void st7789_dma_transfer_complete_callback(st7789_dev_t *dev) {
    /* Завершення передачі поточного рядка: піднімаємо CS і знімаємо прапорець зайнятості */
    dev->hal.cs_write(1U);
    dev->dma_busy = false;
}
