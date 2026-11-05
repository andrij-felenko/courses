#include <cmath>
#include <cstdint>

class ScottTDemodulator {
public:
    struct Calibration {
        float offsetSinV{1.65f};
        float offsetCosV{1.65f};
        float scaleSin{1.0f};
        float scaleCos{1.0f};
        float vrefV{3.3f};
    };

    struct Result {
        float angleRad{0.0f};
        float angleDeg{0.0f};
        bool valid{false};
    };

    explicit ScottTDemodulator(const Calibration& calib = Calibration())
        : calib_(calib) {}

    void setCalibration(const Calibration& calib) {
        calib_ = calib;
    }

    Result compute(std::uint16_t adcSin, std::uint16_t adcCos, std::uint16_t adcMax = 4095) const {
        Result res;
        if (adcMax == 0) return res;

        const float vSin = (static_cast<float>(adcSin) / static_cast<float>(adcMax)) * calib_.vrefV;
        const float vCos = (static_cast<float>(adcCos) / static_cast<float>(adcMax)) * calib_.vrefV;

        const float normSin = (vSin - calib_.offsetSinV) * calib_.scaleSin;
        const float normCos = (vCos - calib_.offsetCosV) * calib_.scaleCos;

        const float magSq = normSin * normSin + normCos * normCos;
        if (magSq < 0.01f) {
            res.valid = false;
            return res;
        }

        constexpr float kPi = 3.14159265358979323846f;
        float angle = std::atan2(normSin, normCos);
        if (angle < 0.0f) {
            angle += 2.0f * kPi;
        }

        res.angleRad = angle;
        res.angleDeg = angle * (180.0f / kPi);
        res.valid = true;
        return res;
    }

private:
    Calibration calib_;
};
