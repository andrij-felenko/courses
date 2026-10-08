// Алгоритм векторної компенсації crosstalk та offset у C++ (Arduino Framework)
#include <Arduino.h>
#include <cmath>

struct TofCalibParams {
    float iCross;    // Синфазна складова crosstalk
    float qCross;    // Квадратурна складова crosstalk
    float dOffsetM;  // Системний зсув у метрах
    float fModHz;    // Частота модуляції в Гц
};

class TofSignalProcessor {
private:
    TofCalibParams cal;
    static constexpr float SPEED_OF_LIGHT = 3.0e8f;

public:
    explicit TofSignalProcessor(const TofCalibParams &params) : cal(params) {}

    // Обчислення скоригованої відстані за квадратурними відліками
    float computeCorrectedDistance(float iMeas, float qMeas) const {
        // 1. Віднімання вектора завади від захисного скла
        float iTarget = iMeas - cal.iCross;
        float qTarget = qMeas - cal.qCross;

        // 2. Відновлення фази корисного відбитка від цілі
        float phiTarget = std::atan2(qTarget, iTarget);
        if (phiTarget < 0.0f) {
            phiTarget += 2.0f * M_PI;
        }

        // 3. Розрахунок відстані та застосування системного зсуву
        float dUncorrected = (SPEED_OF_LIGHT * phiTarget) / (4.0f * M_PI * cal.fModHz);
        return dUncorrected - cal.dOffsetM;
    }
};
