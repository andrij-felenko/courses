// Задання координат прямокутної області ST7789 з апаратною корекцією зміщення
void st7789_set_address_window(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2, uint8_t rotation)
{
    uint16_t x_offset = 0;
    uint16_t y_offset = 0;

    // Компенсація посадки матриці 240x240 у кадровому буфері 240x320
    switch (rotation) {
        case 0: // Портретна орієнтація (0°)
            x_offset = 0;
            y_offset = 0;
            break;
        case 1: // Альбомна орієнтація (90°)
            x_offset = 0;
            y_offset = 0;
            break;
        case 2: // Перевернута портретна (180°)
            x_offset = 0;
            y_offset = 80; // Зсув матриці на 80 рядків уздовж непідключеної області RAM
            break;
        case 3: // Перевернута альбомна (270°)
            x_offset = 80;
            y_offset = 0;
            break;
    }

    // Вікно стовпчиків (CASET: 0x2A) — кінцева координата передається включно
    st7789_write_cmd(0x2A);
    st7789_write_data_u16(x1 + x_offset);
    st7789_write_data_u16(x2 + x_offset);

    // Вікно рядків (RASET: 0x2B)
    st7789_write_cmd(0x2B);
    st7789_write_data_u16(y1 + y_offset);
    st7789_write_data_u16(y2 + y_offset);

    // Команда запису пікселів у пам'ять дисплея (RAMWR: 0x2C)
    st7789_write_cmd(0x2C);
}
