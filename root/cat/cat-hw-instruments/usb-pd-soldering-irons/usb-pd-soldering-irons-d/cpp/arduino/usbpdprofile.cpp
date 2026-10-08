// Зчитування PDO профілів та запит напруги USB PD (Arduino / C++)
#include <Arduino.h>

struct UsbPdProfile {
    uint8_t  index;
    uint16_t voltagemV;
    uint16_t maxCurrentmA;
};

class PowerDeliveryManager {
public:
    int findBestProfile(const UsbPdProfile profiles[], uint8_t size, float rCartridge) {
        int targetIdx = -1;
        float highestPower = 0.0;

        for (uint8_t i = 0; i < size; i++) {
            float v = profiles[i].voltagemV / 1000.0f;
            float iMax = profiles[i].maxCurrentmA / 1000.0f;
            float iRequired = v / rCartridge;
            
            float iActual = min(iRequired, iMax);
            float calculatedPower = v * iActual;

            if (calculatedPower > highestPower) {
                highestPower = calculatedPower;
                targetIdx = i;
            }
        }
        return targetIdx;
    }
};
