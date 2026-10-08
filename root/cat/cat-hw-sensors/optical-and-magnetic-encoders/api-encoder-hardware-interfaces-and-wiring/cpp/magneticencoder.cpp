#include <cstdint>
#include <functional>

class MagneticEncoder {
public:
    static constexpr uint16_t RegZeroPos = 0x0001;
    static constexpr uint16_t RegAGC     = 0x3FFD;
    static constexpr uint16_t CmdRead    = 0x4000;

    explicit MagneticEncoder(std::function<uint16_t(uint16_t)> spiTransfer)
        : transfer_(std::move(spiTransfer)) {}

    bool calibrateZero(uint16_t rawAngle) {
        uint16_t cmd = calcParity(RegZeroPos);
        uint16_t data = calcParity(rawAngle & 0x3FFF);
        
        transfer_(cmd);
        transfer_(data);

        return verifyFieldStrength();
    }

private:
    std::function<uint16_t(uint16_t)> transfer_;

    static uint16_t calcParity(uint16_t frame) {
        uint16_t count = 0;
        for (int i = 0; i < 16; ++i) {
            if (frame & (1 << i)) count++;
        }
        return (count % 2 != 0) ? (frame | 0x8000) : frame;
    }

    bool verifyFieldStrength() {
        uint16_t agcResp = transfer_(calcParity(RegAGC | CmdRead));
        uint8_t agcValue = static_cast<uint8_t>(agcResp & 0x00FF);
        return (agcValue >= 10 && agcValue <= 245);
    }
};
