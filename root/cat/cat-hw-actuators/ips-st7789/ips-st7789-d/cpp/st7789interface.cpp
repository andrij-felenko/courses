// Об'єктно-орієнтований драйвер базового інтерфейсу на C++
#include <cstdint>
#include <cstddef>

class ST7789Interface {
public:
    ST7789Interface() = default;

    void writeCommand(uint8_t cmd) {
        setDC(false); // Встановлення лінії DC у стан команди
        setCS(false); // Активація вибору мікросхеми
        spiTransmit(&cmd, 1);
        setCS(true);
    }

    void writeData(const uint8_t* buffer, size_t length) {
        setDC(true);  // Встановлення лінії DC у стан даних
        setCS(false);
        spiTransmit(buffer, length);
        setCS(true);
    }

    void init() {
        writeCommand(0x01); // SWRESET
        delayMs(150);

        writeCommand(0x11); // SLPOUT
        delayMs(120);

        writeCommand(0x3A); // COLMOD
        const uint8_t colorFormat = 0x55; // 16 біт (RGB565)
        writeData(&colorFormat, 1);

        writeCommand(0x36); // MADCTL
        const uint8_t scanControl = 0x00;
        writeData(&scanControl, 1);

        writeCommand(0x21); // INVON для IPS матриці
        delayMs(10);

        writeCommand(0x29); // DISPON
        delayMs(20);
    }

private:
    // Апаратно-залежні низькорівневі методи платформи
    virtual void spiTransmit(const uint8_t* data, size_t len) = 0;
    virtual void setCS(bool state) = 0;
    virtual void setDC(bool state) = 0;
    virtual void delayMs(uint32_t ms) = 0;
};
