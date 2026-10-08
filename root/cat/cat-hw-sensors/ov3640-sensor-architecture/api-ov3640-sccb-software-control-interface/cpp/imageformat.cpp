#include <cstdint>

enum class ImageFormat {
    Yuv422,
    Rgb565,
    RawRgb,
    Jpeg
};

enum class FrameResolution {
    Uxga,
    Svga,
    Vga,
    Cif
};

class Ov3640Configurator {
public:
    explicit Ov3640Configurator(Ov3640SccbDriver& driver) : driver_(driver) {}

    int setFormat(ImageFormat fmt) {
        uint8_t regVal = 0;
        switch (fmt) {
            case ImageFormat::Yuv422:  regVal = 0x00; break;
            case ImageFormat::Rgb565:  regVal = 0x06; break;
            case ImageFormat::RawRgb:  regVal = 0x01; break;
            case ImageFormat::Jpeg:    regVal = 0x10; break;
        }
        return driver_.writeReg(Ov3640SccbDriver::Bank::Dsp, 0x3602, regVal);
    }

    int setResolution(FrameResolution res) {
        uint8_t subValue = 0;
        switch (res) {
            case FrameResolution::Uxga: subValue = 0x00; break;
            case FrameResolution::Vga:  subValue = 0x04; break;
            case FrameResolution::Cif:  subValue = 0x08; break;
            default: return -1;
        }
        return driver_.writeReg(Ov3640SccbDriver::Bank::Dsp, 0x3620, subValue);
    }

private:
    Ov3640SccbDriver& driver_;
};
