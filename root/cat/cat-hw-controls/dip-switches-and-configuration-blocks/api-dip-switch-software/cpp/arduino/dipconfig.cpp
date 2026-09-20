#include <Arduino.h>

struct DipConfig {
    uint8_t deviceAddress; // Біти 0..1
    bool highSpeedMode;    // Біт 2
    bool parityEnable;     // Біт 3
};

class DipSwitchDriver {
public:
    DipSwitchDriver(const uint8_t pins[4]) {
        for (uint8_t i = 0; i < 4; ++i) {
            pins_[i] = pins[i];
        }
    }

    void begin() {
        for (uint8_t i = 0; i < 4; ++i) {
            pinMode(pins_[i], INPUT_PULLUP);
        }
    }

    DipConfig readConfig() const {
        uint8_t raw = 0;
        for (uint8_t i = 0; i < 4; ++i) {
            if (digitalRead(pins_[i]) == HIGH) {
                raw |= (1 << i);
            }
        }

        // Інверсія 4 молодших бітів
        uint8_t direct = (~raw) & 0x0F;

        DipConfig config;
        config.deviceAddress = (direct & 0x03) >> 0;
        config.highSpeedMode = (direct & 0x04) >> 2;
        config.parityEnable  = (direct & 0x08) >> 3;
        return config;
    }

private:
    uint8_t pins_[4];
};
