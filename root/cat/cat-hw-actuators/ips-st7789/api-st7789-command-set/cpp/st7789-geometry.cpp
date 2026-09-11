// Реалізація мовою C++
#include <cstdint>

class ST7789_Geometry : public ST7789_Display {
public:
    enum class Rotation : uint8_t {
        Deg0   = 0,
        Deg90  = 1,
        Deg180 = 2,
        Deg270 = 3
    };

    void setRotation(Rotation rot) {
        uint8_t madctl = 0;

        switch (rot) {
            case Rotation::Deg0:
                madctl = 0x00;
                offsetX = 0;
                offsetY = 80;
                break;
            case Rotation::Deg90:
                madctl = 0x40 | 0x20; // MX | MV
                offsetX = 80;
                offsetY = 0;
                break;
            case Rotation::Deg180:
                madctl = 0x40 | 0x80; // MX | MY
                offsetX = 0;
                offsetY = 0;
                break;
            case Rotation::Deg270:
                madctl = 0x80 | 0x20; // MY | MV
                offsetX = 0;
                offsetY = 0;
                break;
        }

        writeCommand(0x36); // MADCTL
        writeData(&madctl, 1);
    }

    void setWindowWithOffset(uint16_t xs, uint16_t ys, uint16_t xe, uint16_t ye) {
        setWindow(xs + offsetX, ys + offsetY, xe + offsetX, ye + offsetY);
    }

private:
    uint16_t offsetX{0};
    uint16_t offsetY{80};
};
