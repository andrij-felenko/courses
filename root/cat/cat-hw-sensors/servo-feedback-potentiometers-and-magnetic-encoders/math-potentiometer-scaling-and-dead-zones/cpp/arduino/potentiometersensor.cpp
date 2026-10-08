#include <Arduino.h>

class PotentiometerSensor {
public:
    struct CalibPoint {
        uint16_t adcCode;
        float angleDeg;
    };

    static constexpr size_t NUM_POINTS = 5;

    PotentiometerSensor(uint16_t minValid, uint16_t maxValid, const CalibPoint points[NUM_POINTS])
        : m_minValid(minValid), m_maxValid(maxValid) {
        for (size_t i = 0; i < NUM_POINTS; ++i) {
            m_lut[i] = points[i];
        }
    }

    bool readAngle(uint16_t rawAdc, float &outAngle) const {
        // Перевірка апаратного збою (обрив або коротке замикання)
        if (rawAdc < (m_minValid / 2) || rawAdc > (m_maxValid + 100)) {
            return false;
        }

        // Обмеження мертвих зон (клемпінг)
        uint16_t clampedAdc = constrain(rawAdc, m_minValid, m_maxValid);

        // Пошук сегмента та лінійна інтерполяція
        for (size_t i = 0; i < NUM_POINTS - 1; ++i) {
            if (clampedAdc >= m_lut[i].adcCode && clampedAdc <= m_lut[i + 1].adcCode) {
                float spanAdc = static_cast<float>(m_lut[i + 1].adcCode - m_lut[i].adcCode);
                float spanAngle = m_lut[i + 1].angleDeg - m_lut[i].angleDeg;
                float progress = static_cast<float>(clampedAdc - m_lut[i].adcCode) / spanAdc;

                outAngle = m_lut[i].angleDeg + progress * spanAngle;
                return true;
            }
        }

        outAngle = m_lut[NUM_POINTS - 1].angleDeg;
        return true;
    }

private:
    uint16_t m_minValid;
    uint16_t m_maxValid;
    CalibPoint m_lut[NUM_POINTS];
};
