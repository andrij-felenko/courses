#include <cstdint>
#include <cmath>
#include <algorithm>

class ServoControllerCpp {
private:
    uint16_t deadbandAdc;
    float kp;
    float filteredAdc;

public:
    ServoControllerCpp(uint16_t deadband, float gain)
        : deadbandAdc(deadband), kp(gain), filteredAdc(0.0f) {}

    int16_t computeOutput(uint16_t rawAdc, uint16_t setpointAdc) {
        // Експоненційне згладжування шумів потенціометра (alpha = 0.2)
        filteredAdc = 0.2f * static_cast<float>(rawAdc) + 0.8f * filteredAdc;

        float error = static_cast<float>(setpointAdc) - filteredAdc;

        // Перевірка зони нечутливості
        if (std::abs(error) <= static_cast<float>(deadbandAdc)) {
            return 0;
        }

        // Зсув похибки на межу deadband для запобігання стрибкам моменту
        float effectiveError = (error > 0.0f) ? (error - deadbandAdc) : (error + deadbandAdc);

        // Обчислення пропорційного керування ШІМ
        float output = effectiveError * kp;
        return static_cast<int16_t>(std::clamp(output, -1000.0f, 1000.0f));
    }
};
