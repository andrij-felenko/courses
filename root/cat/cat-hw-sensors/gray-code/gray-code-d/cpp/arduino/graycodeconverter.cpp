#include <Arduino.h>

class GrayCodeConverter {
public:
    // Конвертація звичайного двійкового числа в код Ґрея
    static uint16_t binaryToGray(uint16_t binary) {
        return binary ^ (binary >> 1);
    }

    // Логарифмічне декодування 16-бітного коду Ґрея у двійковий формат
    static uint16_t grayToBinary(uint16_t gray) {
        gray ^= (gray >> 1);
        gray ^= (gray >> 2);
        gray ^= (gray >> 4);
        gray ^= (gray >> 8);
        return gray;
    }

    // Декодування урізаного коду Ґрея з перевіркою коректності діапазону
    static bool decodeExcessGray(uint16_t rawGray, uint16_t resolution, uint8_t bitDepth, uint16_t &outAngle) {
        uint16_t totalStates = 1U << bitDepth;
        uint16_t shiftOffset = (totalStates - resolution) / 2;

        uint16_t shiftedBinary = grayToBinary(rawGray);

        if (shiftedBinary < shiftOffset || shiftedBinary >= (shiftOffset + resolution)) {
            return false; // Зчитано хибну кодову комбінацію
        }

        outAngle = shiftedBinary - shiftOffset;
        return true;
    }
};
