#include <cmath>

class QuadratureAngleProcessor {
public:
    /* Обчислення абсолютного кута в градусах [0..360) з компенсацією офсету та дисбалансу */
    static float calculateAngleDeg(float vSin, float vCos, float offSin, float offCos, float gainRatio) noexcept {
        const float sinCorr = vSin - offSin;
        const float cosCorr = (vCos - offCos) * gainRatio;
        
        float angleRad = std::atan2(sinCorr, cosCorr);
        float angleDeg = angleRad * (180.0f / 3.14159265358979323846f);
        
        if (angleDeg < 0.0f) {
            angleDeg += 360.0f;
        }
        return angleDeg;
    }
};
