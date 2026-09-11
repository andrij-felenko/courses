// Повна реалізація базового драйвера ST7789 мовою C++
#include <cstdint>

class ST7789_Driver {
public:
    static constexpr uint8_t CMD_SWRESET = 0x01;
    static constexpr uint8_t CMD_SLPOUT  = 0x11;
    static constexpr uint8_t CMD_INVON   = 0x21;
    static constexpr uint8_t CMD_DISPON  = 0x29;
    static constexpr uint8_t CMD_CASET   = 0x2A;
    static constexpr uint8_t CMD_RASET   = 0x2B;
    static constexpr uint8_t CMD_RAMWR   = 0x2C;
    static constexpr uint8_t CMD_MADCTL  = 0x36;
    static constexpr uint8_t CMD_COLMOD  = 0x3A;

    void init() {
        resetHardware();

        writeCmd(CMD_SWRESET);
        delayMs(120);

        writeCmd(CMD_SLPOUT);
        delayMs(120);

        writeCmd(CMD_COLMOD);
        writeDataByte(0x55); // 16 біт (RGB565)

        writeCmd(CMD_MADCTL);
        writeDataByte(0x00);

        writeCmd(CMD_INVON); // Інверсія для панелей IPS

        clear(0x0000); // Очищення чорним перед увімкненням

        writeCmd(CMD_DISPON);
        delayMs(20);

        setBacklight(true);
    }

    void setWindow(uint16_t xs, uint16_t ys, uint16_t xe, uint16_t ye) {
        const uint16_t adjXs = xs + offsetX;
        const uint16_t adjXe = xe + offsetX;
        const uint16_t adjYs = ys + offsetY;
        const uint16_t adjYe = ye + offsetY;

        const uint8_t colData[4] = {
            static_cast<uint8_t>(adjXs >> 8), static_cast<uint8_t>(adjXs & 0xFF),
            static_cast<uint8_t>(adjXe >> 8), static_cast<uint8_t>(adjXe & 0xFF)
        };

        const uint8_t rowData[4] = {
            static_cast<uint8_t>(adjYs >> 8), static_cast<uint8_t>(adjYs & 0xFF),
            static_cast<uint8_t>(adjYe >> 8), static_cast<uint8_t>(adjYe & 0xFF)
        };

        writeCmd(CMD_CASET);
        writeData(colData, sizeof(colData));

        writeCmd(CMD_RASET);
        writeData(rowData, sizeof(rowData));
    }

    void clear(uint16_t color) {
        setWindow(0, 0, 239, 239);
        writeCmd(CMD_RAMWR);

        const uint8_t colorBytes[2] = {
            static_cast<uint8_t>(color >> 8),
            static_cast<uint8_t>(color & 0xFF)
        };

        setDC(true);
        setCS(false);
        for (uint32_t i = 0; i < 240 * 240; ++i) {
            spiTransmit(colorBytes, sizeof(colorBytes));
        }
        setCS(true);
    }

private:
    uint16_t offsetX{0};
    uint16_t offsetY{80};

    virtual void setReset(bool state) = 0;
    virtual void setDC(bool state) = 0;
    virtual void setCS(bool state) = 0;
    virtual void setBacklight(bool state) = 0;
    virtual void spiTransmit(const uint8_t* data, uint16_t length) = 0;
    virtual void delayMs(uint32_t ms) = 0;

    void resetHardware() {
        setReset(true);
        delayMs(10);
        setReset(false);
        delayMs(20);
        setReset(true);
        delayMs(120);
    }

    void writeCmd(uint8_t cmd) {
        setDC(false);
        setCS(false);
        spiTransmit(&cmd, 1);
        setCS(true);
    }

    void writeDataByte(uint8_t data) {
        setDC(true);
        setCS(false);
        spiTransmit(&data, 1);
        setCS(true);
    }

    void writeData(const uint8_t* data, uint16_t length) {
        setDC(true);
        setCS(false);
        spiTransmit(data, length);
        setCS(true);
    }
};
