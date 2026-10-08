// Зчитування PDO профілів та запит напруги USB PD (ESP-IDF / C)
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint8_t  profileIndex;
    uint16_t voltageMilliVolts;
    uint16_t maxCurrentMilliAmps;
} UsbPdPdoProfile;

// Функція вибору оптимального профілю живлення під опір картриджа R = 6.2 Ом
int selectOptimalPdProfile(const UsbPdPdoProfile* profiles, uint8_t count, float cartridgeResistance) {
    int bestIndex = -1;
    float maxSafePower = 0.0f;

    for (uint8_t i = 0; i < count; i++) {
        float voltage = profiles[i].voltageMilliVolts / 1000.0f;
        float maxCurr = profiles[i].maxCurrentMilliAmps / 1000.0f;
        
        // Обчислення пікового струму через нагрівач при цій напрузі
        float peakCurrent = voltage / cartridgeResistance;
        
        // Якщо струм перевищує ліміт джерела, струм буде обмежено джерелом або ШІМ
        float effectiveCurrent = (peakCurrent > maxCurr) ? maxCurr : peakCurrent;
        float power = voltage * effectiveCurrent;

        // Вибір профілю з максимальною безпечною потужністю
        if (power > maxSafePower) {
            maxSafePower = power;
            bestIndex = i;
        }
    }
    return bestIndex;
}
