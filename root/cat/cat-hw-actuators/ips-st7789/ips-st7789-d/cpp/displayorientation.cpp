// Реалізація розрахунку вікна та орієнтації на C++
#include <cstdint>
#include <algorithm>

enum class DisplayOrientation {
    PortraitNormal,   // 0 градусів
    LandscapeRight,   // 90 градусів за стрілкою
    PortraitInverted, // 180 градусів
    LandscapeLeft     // 270 градусів
};

class ST7789WindowEngine {
public:
    static constexpr uint16_t NativeWidth  = 240;
    static constexpr uint16_t NativeHeight = 240;

    void setOrientation(DisplayOrientation orientation) {
        uint8_t madctl = 0;
        switch (orientation) {
            case DisplayOrientation::PortraitNormal:
                madctl = 0x00;
                xOffset_ = 0;
                yOffset_ = 0;
                width_  = NativeWidth;
                height_ = NativeHeight;
                break;
            case DisplayOrientation::LandscapeRight:
                madctl = 0x60;
                xOffset_ = 0;
                yOffset_ = 0;
                width_  = NativeHeight;
                height_ = NativeWidth;
                break;
            case DisplayOrientation::PortraitInverted:
                madctl = 0xC0;
                xOffset_ = 0;
                yOffset_ = 80; // Зсув 80 рядків для 180°
                width_  = NativeWidth;
                height_ = NativeHeight;
                break;
            case DisplayOrientation::LandscapeLeft:
                madctl = 0xA0;
                xOffset_ = 80; // Зсув 80 рядків для 270°
                yOffset_ = 0;
                width_  = NativeHeight;
                height_ = NativeWidth;
                break;
        }
        sendRegister(0x36, &madctl, 1);
    }

    bool openWindow(int16_t x0, int16_t y0, int16_t x1, int16_t y1) {
        if (x0 >= width_ || y0 >= height_ || x1 < 0 || y1 < 0) {
            return false;
        }

        const uint16_t xs = std::max<int16_t>(0, x0) + xOffset_;
        const uint16_t xe = std::min<int16_t>(width_ - 1, x1) + xOffset_;
        const uint16_t ys = std::max<int16_t>(0, y0) + yOffset_;
        const uint16_t ye = std::min<int16_t>(height_ - 1, y1) + yOffset_;

        const uint8_t colParams[4] = {
            static_cast<uint8_t>(xs >> 8), static_cast<uint8_t>(xs & 0xFF),
            static_cast<uint8_t>(xe >> 8), static_cast<uint8_t>(xe & 0xFF)
        };
        sendRegister(0x2A, colParams, 4); // CASET

        const uint8_t rowParams[4] = {
            static_cast<uint8_t>(ys >> 8), static_cast<uint8_t>(ys & 0xFF),
            static_cast<uint8_t>(ye >> 8), static_cast<uint8_t>(ye & 0xFF)
        };
        sendRegister(0x2B, rowParams, 4); // RASET

        sendCmd(0x2C); // RAMWR: готовність приймати піксельний потік
        return true;
    }

private:
    uint16_t xOffset_ = 0;
    uint16_t yOffset_ = 0;
    uint16_t width_  = NativeWidth;
    uint16_t height_ = NativeHeight;

    virtual void sendCmd(uint8_t cmd) = 0;
    virtual void sendRegister(uint8_t cmd, const uint8_t* data, size_t len) = 0;
};
