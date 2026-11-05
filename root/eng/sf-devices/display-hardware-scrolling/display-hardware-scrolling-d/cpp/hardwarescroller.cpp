#include <cstdint>

class HardwareScroller {
public:
    enum class Command : uint8_t {
        VscrDef = 0x33,
        VscrSadd = 0x37,
        RamWr = 0x2C
    };

    HardwareScroller(uint16_t tfa, uint16_t vsa, uint16_t bfa, uint16_t width)
        : tfa_(tfa), vsa_(vsa), bfa_(bfa), width_(width), current_vsp_(tfa) {}

    void init() {
        const uint8_t params[6] = {
            static_cast<uint8_t>(tfa_ >> 8), static_cast<uint8_t>(tfa_ & 0xFF),
            static_cast<uint8_t>(vsa_ >> 8), static_cast<uint8_t>(vsa_ & 0xFF),
            static_cast<uint8_t>(bfa_ >> 8), static_cast<uint8_t>(bfa_ & 0xFF)
        };
        writeCommand(Command::VscrDef);
        writeData(params, sizeof(params));
    }

    void scrollUp(uint16_t dy, const uint16_t* newLinePixels) {
        for (uint16_t step = 0; step < dy; ++step) {
            uint16_t writeY = current_vsp_;
            setAddressWindow(0, writeY, width_ - 1, writeY);

            writeCommand(Command::RamWr);
            writeData(reinterpret_cast<const uint8_t*>(newLinePixels), width_ * sizeof(uint16_t));

            current_vsp_++;
            if (current_vsp_ >= (tfa_ + vsa_)) {
                current_vsp_ = tfa_;
            }
        }

        const uint8_t vspBytes[2] = {
            static_cast<uint8_t>(current_vsp_ >> 8),
            static_cast<uint8_t>(current_vsp_ & 0xFF)
        };
        writeCommand(Command::VscrSadd);
        writeData(vspBytes, sizeof(vspBytes));
    }

private:
    uint16_t tfa_;
    uint16_t vsa_;
    uint16_t bfa_;
    uint16_t width_;
    uint16_t current_vsp_;

    // Низькорівневі методи реалізуються апаратно залежно від платформи
    void writeCommand(Command cmd);
    void writeData(const uint8_t* data, uint32_t len);
    void setAddressWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
};
