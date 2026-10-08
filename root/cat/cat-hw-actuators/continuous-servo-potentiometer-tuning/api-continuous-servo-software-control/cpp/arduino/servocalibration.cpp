#include <Arduino.h>

struct ServoCalibration {
    int16_t offsetUs;       // Програмний зсув нейтралі (наприклад, +18 мкс)
    uint16_t deadbandUs;    // Напівширина зони нечутливості (наприклад, 15 мкс)
};

uint16_t applyOffsetAndDeadband(float inputSpeed, const ServoCalibration& cal) {
    const uint16_t baseNeutralUs = 1500;
    uint16_t correctedNeutral = baseNeutralUs + cal.offsetUs;
    
    float absSpeed = fabsf(inputSpeed);
    float deadbandNorm = static_cast<float>(cal.deadbandUs) / 500.0f;
    
    // Перевірка потрапляння у зону deadband
    if (absSpeed <= deadbandNorm) {
        return correctedNeutral;
    }
    
    // Масштабування для плавного старту від межі deadband
    float scaledSpeed = (absSpeed - deadbandNorm) / (1.0f - deadbandNorm);
    if (inputSpeed < 0.0f) scaledSpeed = -scaledSpeed;
    
    int16_t pulseDelta = lroundf(scaledSpeed * 500.0f);
    return static_cast<uint16_t>(correctedNeutral + pulseDelta);
}
