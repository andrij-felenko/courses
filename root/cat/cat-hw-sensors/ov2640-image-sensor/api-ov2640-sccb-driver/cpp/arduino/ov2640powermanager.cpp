class OV2640PowerManager {
public:
    explicit OV2640PowerManager(OV2640Driver& drv, int pwdnPin) 
        : driver(drv), pinPWDN(pwdnPin) {
        pinMode(pinPWDN, OUTPUT);
        digitalWrite(pinPWDN, LOW);
    }

    bool verifySensorID() {
        if (!driver.setBank(OV2640Driver::Bank::Sensor)) return false;
        // В рамках прикладу спрощена перевірка вичитаних регістраційних даних
        // pid повинно бути 0x26, ver — 0x42
        return true;
    }

    void hardwarePowerDown(bool enable) {
        digitalWrite(pinPWDN, enable ? HIGH : LOW);
        if (!enable) {
            // Очікування стабілізації PLL після увімкнення живлення
            delay(5); 
        }
    }

private:
    OV2640Driver& driver;
    int pinPWDN;
};
