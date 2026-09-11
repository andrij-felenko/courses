#include <SPI.h>

// Визначення керуючих пінів дисплея
const int PIN_CS  = 10;
const int PIN_DC  = 9;
const int PIN_RST = 8;

// Налаштування шини SPI: 20 МГц, старший біт уперед, режим Mode 0
SPISettings spi_settings(20000000, MSBFIRST, SPI_MODE0);

// Надсилання одного байта команди
void st7789_write_command(uint8_t cmd) {
    SPI.beginTransaction(spi_settings);
    digitalWrite(PIN_DC, LOW);   // Низький рівень: передача коду операції
    digitalWrite(PIN_CS, LOW);   // Активація вибору пристрою
    SPI.transfer(cmd);
    digitalWrite(PIN_CS, HIGH);  // Деактивація вибору
    SPI.endTransaction();
}

// Надсилання масиву байтів даних або параметрів
void st7789_write_data(const uint8_t *data, size_t len) {
    if (len == 0) return;
    SPI.beginTransaction(spi_settings);
    digitalWrite(PIN_DC, HIGH);  // Високий рівень: передача даних або аргументів
    digitalWrite(PIN_CS, LOW);   // Активація вибору пристрою
    for (size_t i = 0; i < len; i++) {
        SPI.transfer(data[i]);
    }
    digitalWrite(PIN_CS, HIGH);  // Деактивація вибору
    SPI.endTransaction();
}
