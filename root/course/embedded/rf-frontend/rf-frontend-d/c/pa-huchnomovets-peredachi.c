// Перевірка «на пальцях»: у скільки разів далі добиває сигнал
#include <math.h>

float range_gain(float gain_db) {
    // потужність ~ 1/d², отже d ~ 1/sqrt(P);
    // +gain_db децибел => множник потужності 10^(gain/10)
    float power_ratio = powf(10.0f, gain_db / 10.0f); // 21 dB -> ×125.9
    return sqrtf(power_ratio);                         // дальність ~ sqrt
}
// range_gain(21.0f) ≈ 11.2  → приблизно в 11 разів далі
