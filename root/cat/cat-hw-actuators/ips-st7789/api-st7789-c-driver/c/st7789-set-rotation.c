/* Встановлення орієнтації екрана з оновленням апаратних зміщень */
void st7789_set_rotation(st7789_t *dev, st7789_rotation_t rotation)
{
    if (!dev) return;

    dev->rotation = rotation;
    uint8_t madctl = ST7789_MADCTL_RGB;

    switch (rotation) {
        case ST7789_ROTATION_0:
            madctl |= 0x00;
            dev->width = 240;
            dev->height = 240;
            dev->offset_x = 0;
            dev->offset_y = 0;
            break;

        case ST7789_ROTATION_90:
            madctl |= (ST7789_MADCTL_MX | ST7789_MADCTL_MV);
            dev->width = 240;
            dev->height = 240;
            dev->offset_x = 0;
            dev->offset_y = 0;
            break;

        case ST7789_ROTATION_180:
            madctl |= (ST7789_MADCTL_MY | ST7789_MADCTL_MX);
            dev->width = 240;
            dev->height = 240;
            dev->offset_x = 0;
            dev->offset_y = 80;
            break;

        case ST7789_ROTATION_270:
            madctl |= (ST7789_MADCTL_MY | ST7789_MADCTL_MV);
            dev->width = 240;
            dev->height = 240;
            dev->offset_x = 80;
            dev->offset_y = 0;
            break;
    }

    st7789_write_cmd(dev, ST7789_CMD_MADCTL);
    st7789_write_data_byte(dev, madctl);
}

/* Встановлення прямокутного вікна адресації */
void st7789_set_address_window(st7789_t *dev, uint16_t x0, uint16_t y0, 
                               uint16_t x1, uint16_t y1)
{
    if (!dev) return;

    /* Програмне відсікання координат за фізичними межами екрана */
    if (x0 >= dev->width)  x0 = dev->width - 1;
    if (x1 >= dev->width)  x1 = dev->width - 1;
    if (y0 >= dev->height) y0 = dev->height - 1;
    if (y1 >= dev->height) y1 = dev->height - 1;

    /* Захист від некоректного порядку координат */
    if (x0 > x1) { uint16_t t = x0; x0 = x1; x1 = t; }
    if (y0 > y1) { uint16_t t = y0; y0 = y1; y1 = t; }

    /* Додавання апаратних зміщень до координат */
    uint16_t x_start = x0 + dev->offset_x;
    uint16_t x_end   = x1 + dev->offset_x;
    uint16_t y_start = y0 + dev->offset_y;
    uint16_t y_end   = y1 + dev->offset_y;

    /* 1. Встановлення межі колонок (CASET) */
    uint8_t caset_data[4] = {
        (uint8_t)(x_start >> 8),   /* Старший байт XS */
        (uint8_t)(x_start & 0xFF), /* Молодший байт XS */
        (uint8_t)(x_end >> 8),     /* Старший байт XE */
        (uint8_t)(x_end & 0xFF)    /* Молодший байт XE */
    };
    st7789_write_cmd(dev, ST7789_CMD_CASET);
    st7789_write_data(dev, caset_data, sizeof(caset_data));

    /* 2. Встановлення межі рядків (RASET) */
    uint8_t raset_data[4] = {
        (uint8_t)(y_start >> 8),   /* Старший байт YS */
        (uint8_t)(y_start & 0xFF), /* Молодший байт YS */
        (uint8_t)(y_end >> 8),     /* Старший байт YE */
        (uint8_t)(y_end & 0xFF)    /* Молодший байт YE */
    };
    st7789_write_cmd(dev, ST7789_CMD_RASET);
    st7789_write_data(dev, raset_data, sizeof(raset_data));

    /* 3. Команда початку запису даних у кадровий буфер */
    st7789_write_cmd(dev, ST7789_CMD_RAMWR);
}
