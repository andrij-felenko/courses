#include <Arduino.h>
#include <math.h>

class RtdAfeReader {
private:
    float _rRef;
    float _r0;
    uint8_t _adcBits;

    // Коефіцієнти стандарту IEC 60751
    const float CVD_A = 3.9083e-3f;
    const float CVD_B = -5.775e-7f;

public:
    struct DiagnosticResult {
        float temperatureC;
        float resistanceOhms;
        bool isFault;
        const char* statusMessage;
    };

    RtdAfeReader(float rRef = 400.0f, float r0 = 100.0f, uint8_t adcBits = 15)
        : _rRef(rRef), _r0(r0), _adcBits(adcBits) {}

    DiagnosticResult processRawCode(uint32_t rawCode) {
        DiagnosticResult res;
        uint32_t maxCode = (1UL << _adcBits) - 1;

        // Перевірка прапорців аварійних станів ліній
        if (rawCode >= maxCode) {
            res.isFault = true;
            res.statusMessage = "Аварія: Обрив вимірювальної лінії";
            res.temperatureC = NAN;
            res.resistanceOhms = INFINITY;
            return res;
        }

        if (rawCode == 0) {
            res.isFault = true;
            res.statusMessage = "Аварія: Коротке замикання сенсора";
            res.temperatureC = NAN;
            res.resistanceOhms = 0.0f;
            return res;
        }

        res.isFault = false;
        res.statusMessage = "Норма";

        // Раціометрична конверсія цифрового коду в опір
        res.resistanceOhms = ((float)rawCode / (float)maxCode) * _rRef;

        // Математична лінеаризація Каллендара — Ван Дюзена
        float polyA = _r0 * CVD_A;
        float polyB = _r0 * CVD_B;
        float deltaR = _r0 - res.resistanceOhms;

        float disc = polyA * polyA - 4.0f * polyB * deltaR;
        if (disc >= 0.0f) {
            res.temperatureC = (-polyA + sqrtf(disc)) / (2.0f * polyB);
        } else {
            res.temperatureC = NAN;
            res.isFault = true;
            res.statusMessage = "Помилка: Математичне переповнення";
        }

        return res;
    }
};
