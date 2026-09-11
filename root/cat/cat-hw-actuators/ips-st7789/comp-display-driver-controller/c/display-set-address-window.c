#include <stdint.h>

// Низькорівневі прототипи передачі, реалізовані платформою
void display_write_command(uint8_t cmd);
void display_write_data_byte(uint8_t data);
void display_write_data_stream(const uint8_t *data, uint32_t length);

// Встановлення прямокутного вікна адресації в пам'яті GRAM
void display_set_address_window(uint16_t x_start, uint16_t y_start,
                                uint16_t x_end,   uint16_t y_end)
{
    // 1. Задання меж стовпців (CASET, 0x2A)
    display_write_command(0x2A);
    display_write_data_byte((uint8_t)(x_start >> 8));
    display_write_data_byte((uint8_t)(x_start & 0xFF));
    display_write_data_byte((uint8_t)(x_end >> 8));
    display_write_data_byte((uint8_t)(x_end & 0xFF));

    // 2. Задання меж рядків (RASET, 0x2B)
    display_write_command(0x2B);
    display_write_data_byte((uint8_t)(y_start >> 8));
    display_write_data_byte((uint8_t)(y_start & 0xFF));
    display_write_data_byte((uint8_t)(y_end >> 8));
    display_write_data_byte((uint8_t)(y_end & 0xFF));

    // 3. Підготовка до запису пікселів у буфер (RAMWR, 0x2C)
    display_write_command(0x2C);
}

// Заливка прямокутної області однорідним кольором (формат RGB565)
void display_fill_rectangle(uint16_t x, uint16_t y,
                            uint16_t width, uint16_t height,
                            uint16_t color_rgb565)
{
    uint32_t total_pixels = (uint32_t)width * height;
    uint8_t high_byte = (uint8_t)(color_rgb565 >> 8);
    uint8_t low_byte  = (uint8_t)(color_rgb565 & 0xFF);

    // Визначаємо вікно для апаратного автоінкременту
    display_set_address_window(x, y, x + width - 1, y + height - 1);

    // Безперервний потік пікселів: лічильник переміщується автоматично
    for (uint32_t i = 0; i < total_pixels; i++) {
        display_write_data_byte(high_byte);
        display_write_data_byte(low_byte);
    }
}
