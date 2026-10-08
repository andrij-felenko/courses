#include <SPI.h>

// Апаратна обгортка шини SPI для двопровідних світлодіодів APA102/SK9822
class TwoWireLedDriver {
private:
    uint32_t busFrequency;
public:
    TwoWireLedDriver(uint32_t clockHz = 10000000UL) : busFrequency(clockHz) {}

    void begin() {
        // Запуск периферійного модуля SPI (автоматичне призначення виводів SCK та MOSI)
        SPI.begin();
    }

    void transferBuffer(const uint8_t* frameBuffer, size_t length) {
        // Налаштування високошвидкісного сеансу передачі без затримки CPU
        SPI.beginTransaction(SPISettings(busFrequency, MSBFIRST, SPI_MODE0));
        SPI.transfer(const_cast<uint8_t*>(frameBuffer), length);
        SPI.endTransaction();
    }
};
