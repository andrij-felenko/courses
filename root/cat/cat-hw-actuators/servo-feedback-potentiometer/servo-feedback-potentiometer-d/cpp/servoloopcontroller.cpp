#include <cstdint>
#include <cstdlib>
#include <algorithm>

class ServoLoopController {
public:
    ServoLoopController(int16_t deadband, float kp, int16_t max_pwm)
        : deadband_(deadband), kp_(kp), maxPwm_(max_pwm) {}

    // Оновлення контуру регулювання
    int16_t update(int16_t target_adc, int16_t current_adc) {
        int16_t error = target_adc - current_adc;
        
        // Перевірка потрапляння в зону нечутливості
        if (std::abs(error) <= deadband_) {
            return 0;
        }
        
        // Зсув помилки на величину зони нечутливості для плавного старту
        int16_t effective_error = (error > 0) ? (error - deadband_) : (error + deadband_);
        
        // Розрахунок пропорційного впливу з обмеженням насичення
        float raw_pwm = kp_ * static_cast<float>(effective_error);
        float clamped_pwm = std::clamp(raw_pwm, -static_cast<float>(maxPwm_), static_cast<float>(maxPwm_));
        
        return static_cast<int16_t>(clamped_pwm);
    }

private:
    int16_t deadband_;
    float kp_;
    int16_t maxPwm_;
};
