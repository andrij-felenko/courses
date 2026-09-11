// Реалізація мовою C++ у стилі драйверного класу
#include <cstdint>

class ST7789_Display {
public:
    static constexpr uint8_t CMD_CASET = 0x2A;
    static constexpr uint8_t CMD_RASET = 0x2B;

    void setWindow(uint16_t xs, uint16_t ys, uint16_t xe, uint16_t ye) {
        const uint8_t colData[4] = {
            static_cast<uint8_t>(xs >> 8),
            static_cast<uint8_t>(xs & 0xFF),
            static_cast<uint8_t>(xe >> 8),
            static_cast<uint8_t>(xe & 0xFF)
        };

        const uint8_t rowData[4] = {
            static_cast<uint8_t>(ys >> 8),
            static_cast<uint8_t>(ys & 0xFF),
            static_cast<uint8_t>(ye >> 8),
            static_cast<uint8_t>(ye & 0xFF)
        };

        writeCommand(CMD_CASET);
        writeData(colData, sizeof(colData));

        writeCommand(CMD_RASET);
        writeData(rowData, sizeof(rowData));
    }

private:
    void writeCommand(uint8_t cmd);
    void writeData(const uint8_t* data, uint16_t length);
};
