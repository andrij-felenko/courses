class AS5048_PWM_Decoder {
private:
    uint8_t pwmPin;

public:
    AS5048_PWM_Decoder(uint8_t pin) : pwmPin(pin) {}

    void begin() {
        pinMode(pwmPin, INPUT);
    }

    bool readAngle(float &angleDeg) {
        // Вимірювання тривалості високого та низького рівнів у мікросекундах
        unsigned long highTime = pulseIn(pwmPin, HIGH, 3000);
        unsigned long lowTime  = pulseIn(pwmPin, LOW, 3000);

        if (highTime == 0 || lowTime == 0) return false;

        unsigned long period = highTime + lowTime;
        if (period < 970 || period > 1080) return false;

        float tHigh = (float)highTime;
        float tInit = 4.0f;
        float tData = (tHigh > tInit) ? (tHigh - tInit) : 0.0f;
        if (tData > 1023.0f) tData = 1023.0f;

        float rawAngle = (tData / 1023.0f) * 16383.0f;
        angleDeg = rawAngle * 360.0f / 16384.0f;
        return true;
    }
};
