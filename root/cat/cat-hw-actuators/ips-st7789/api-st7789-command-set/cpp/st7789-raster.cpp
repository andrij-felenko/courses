// Реалізація мовою C++
#include <cstdint>
#include <cstddef>

class ST7789_Raster : public ST7789_Display {
public:
    static constexpr uint8_t CMD_RAMWR = 0x2C;

    void fillRect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color) {
        if (w == 0 || h == 0) return;

        setWindow(x, y, x + w - 1, y + h - 1);
        writeCommand(CMD_RAMWR);

        const uint8_t colorBytes[2] = {
            static_cast<uint8_t>(color >> 8),
            static_cast<uint8_t>(color & 0xFF)
        };

        const uint32_t totalPixels = static_cast<uint32_t>(w) * h;
        for (uint32_t i = 0; i < totalPixels; ++i) {
            writeData(colorBytes, sizeof(colorBytes));
        }
    }

    void drawImage(uint16_t x, uint16_t y, uint16_t w, uint16_t h, const uint16_t* pixels) {
        if (w == 0 || h == 0 || pixels == nullptr) return;

        setWindow(x, y, x + w - 1, y + h - 1);
        writeCommand(CMD_RAMWR);

        const uint32_t totalPixels = static_cast<uint32_t>(w) * h;
        for (uint32_t i = 0; i < totalPixels; ++i) {
            const uint16_t c = pixels[i];
            const uint8_t colorBytes[2] = {
                static_cast<uint8_t>(c >> 8),
                static_cast<uint8_t>(c & 0xFF)
            };
            writeData(colorBytes, sizeof(colorBytes));
        }
    }
};
