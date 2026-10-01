struct KnockEvent {
    uint32_t timestamp;
    uint16_t peakValue;
    float intensity;
};

class PiezoDataInterface {
public:
    uint16_t readRaw(uint8_t pin) {
        return analogRead(pin);
    }

    bool getEvent(KnockEvent &outEvent) {
        return false; // Заповнення структури при підтвердженому стуку
    }
};
