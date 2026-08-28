#include <cstdint>
#include <system_error>

enum class IIP3Mode : uint8_t {
    LowPower      = 0,
    Normal        = 1,
    HighLinearity = 2
};

struct MixerHardwareConfig {
    uint8_t  ifGainDb{12};
    bool     rfAttenEnable{false};
    IIP3Mode iip3Mode{IIP3Mode::Normal};
    uint8_t  loDivider{1};
};

class IntegratedRfMixer {
public:
    explicit IntegratedRfMixer(uint8_t csPin) : csPin_{csPin} {}

    bool initialize(const MixerHardwareConfig& config) {
        // 1. Увімкнення живлення аналогового блоку
        writeRegister(0x00, 0x0003);
        delayUs(20); // Затримка на вихід з релаксації

        // 2. Конфігурація підсилення
        uint16_t gainReg = (config.ifGainDb & 0x1F);
        if (config.rfAttenEnable) {
            gainReg |= (1 << 5);
        }
        writeRegister(0x01, gainReg);

        // 3. Конфігурація лінійності IIP3
        uint16_t biasReg = 0;
        switch (config.iip3Mode) {
            case IIP3Mode::LowPower:      biasReg = 0x0000; break;
            case IIP3Mode::Normal:        biasReg = 0x0003; break;
            case IIP3Mode::HighLinearity: biasReg = 0x0007; break;
        }
        writeRegister(0x02, biasReg);

        return true;
    }

private:
    uint8_t csPin_;

    void writeRegister(uint8_t reg, uint16_t value) {
        // Апаратно-залежний виклику SPI шини
    }
    void delayUs(uint32_t us) {
        // Апаратно-залежна таймерна затримка
    }
};
