#include <Wire.h>

#define OLED_I2C_ADDR       0x3C
#define OLED_WIDTH          128
#define OLED_HEIGHT         32
#define OLED_BUFFER_SIZE    (OLED_WIDTH * OLED_HEIGHT / 8)

class OLEDDisplay {
private:
    uint8_t buffer[OLED_BUFFER_SIZE];

public:
    OLEDDisplay() {
        clear();
    }

    void clear() {
        memset(buffer, 0, sizeof(buffer));
    }

    void setPixel(int16_t x, int16_t y, bool enable) {
        if (x < 0 || x >= OLED_WIDTH || y < 0 || y >= OLED_HEIGHT) {
            return;
        }

        uint16_t index = x + ((y / 8) * OLED_WIDTH);
        uint8_t bitMask = 1 << (y % 8);

        if (enable) {
            buffer[index] |= bitMask;
        } else {
            buffer[index] &= ~bitMask;
        }
    }

    void display() {
        // Передача даних сторінками для сумісності з замовчувальним режимом SSD1306
        for (uint8_t page = 0; page < 4; page++) {
            Wire.beginTransmission(OLED_I2C_ADDR);
            Wire.write(0x00); // Режим команд
            Wire.write(0xB0 + page); // Установка адреси сторінки (0xB0..0xB3)
            Wire.write(0x00); // Молодший нібл стовпчика (0x00)
            Wire.write(0x10); // Старший нібл стовпчика (0x10)
            Wire.endTransmission();

            Wire.beginTransmission(OLED_I2C_ADDR);
            Wire.write(0x40); // Режим даних
            Wire.write(&buffer[page * OLED_WIDTH], OLED_WIDTH);
            Wire.endTransmission();
        }
    }
};
