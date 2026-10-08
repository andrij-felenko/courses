#include <cmath>

struct SensorCalibration {
    float offCos{0.0f};     // Постійний зсув косинуса, В
    float offSin{0.0f};     // Постійний зсув синуса, В
    float gainRatio{1.0f};  // Співвідношення амплітуд (A_cos / A_sin)
    float sinPhi{0.0f};     // Синус кута фазового відхилення sin(phi_err)
    float cosPhi{1.0f};     // Косинус кута фазового відхилення cos(phi_err)
};

class AngleCalculator {
public:
    /* Обчислення абсолютного кута в градусах [0..360) з повною матричною корекцією */
    [[nodiscard]] static float calculateCalibratedAngle(float rawCos, float rawSin, const SensorCalibration& cal) noexcept {
        // 1. Усунення постійного зсуву нуля (офсету)
        const float vCNorm = rawCos - cal.offCos;
        const float vSNorm = (rawSin - cal.offSin) * cal.gainRatio;
        
        // 2. Ортогоналізація фазового зсуву (компенсація похибки 90 градусів)
        const float vCosCorr = vCNorm;
        const float vSinCorr = (vSNorm - vCNorm * cal.sinPhi) / cal.cosPhi;
        
        // 3. Обчислення арктангенса двох аргументів
        const float angleRad = std::atan2(vSinCorr, vCosCorr);
        float angleDeg = angleRad * (180.0f / 3.14159265358979323846f);
        
        // 4. Нормалізація результату до діапазону [0, 360) градусів
        if (angleDeg < 0.0f) {
            angleDeg += 360.0f;
        }
        return angleDeg;
    }
};
