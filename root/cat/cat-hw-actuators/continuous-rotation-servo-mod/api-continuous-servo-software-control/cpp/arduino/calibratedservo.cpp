class CalibratedServo {
private:
    Servo servoDevice;
    int pinNumber;
    uint16_t calibratedNeutralUs;
    uint16_t deadbandUs;

public:
    CalibratedServo(int pin) 
        : pinNumber(pin), calibratedNeutralUs(1500), deadbandUs(15) {}

    void setCalibration(uint16_t exactZeroUs, uint16_t deadband) {
        calibratedNeutralUs = exactZeroUs;
        deadbandUs = deadband;
    }

    void writeTargetPulse(uint16_t targetUs) {
        int32_t diff = (int32_t)targetUs - calibratedNeutralUs;
        
        // Перевірка входження в мертву зону (deadband)
        if (abs(diff) <= deadbandUs) {
            servoDevice.writeMicroseconds(calibratedNeutralUs);
        } else {
            servoDevice.writeMicroseconds(targetUs);
        }
    }
};
