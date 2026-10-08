#include <algorithm>

class PidController {
public:
    PidController(float kp, float ki, float kd, float dt, float out_min, float out_max, float alpha)
        : k_p_(kp), k_i_(ki), k_d_(kd), dt_(dt),
          out_min_(out_min), out_max_(out_max), alpha_(alpha),
          i_term_(0.0f), prev_meas_(0.0f), filt_temp_(0.0f), is_first_run_(true) {}

    float compute(float target_temp, float raw_temp) {
        // 1. Цифрова фільтрація сигналу термопари K-типу
        if (is_first_run_) {
            filt_temp_ = raw_temp;
            prev_meas_ = raw_temp;
            is_first_run_ = false;
        } else {
            filt_temp_ = alpha_ * raw_temp + (1.0f - alpha_) * filt_temp_;
        }

        // 2. Обчислення похибки регулювання
        const float error = target_temp - filt_temp_;

        // 3. Пропорційна складова
        const float p_term = k_p_ * error;

        // 4. Прогнозна інтегральна складова
        const float next_i_term = i_term_ + k_i_ * error * dt_;

        // 5. Диференціальна складова за вимірюванням
        const float d_term = -k_d_ * (filt_temp_ - prev_meas_) / dt_;
        prev_meas_ = filt_temp_;

        // 6. Сумарне вихідне значення
        const float raw_output = p_term + next_i_term + d_term;

        // 7. Обмеження виходу з захистом Anti-Windup
        float output = std::clamp(raw_output, out_min_, out_max_);
        if (raw_output == output) {
            i_term_ = next_i_term; // Оновлення інтегратора лише при відсутності насичення
        }

        return output;
    }

    void reset() {
        i_term_ = 0.0f;
        is_first_run_ = true;
    }

    float getFilteredTemperature() const {
        return filt_temp_;
    }

private:
    float k_p_;
    float k_i_;
    float k_d_;
    float dt_;
    float out_min_;
    float out_max_;
    float alpha_;

    float i_term_;
    float prev_meas_;
    float filt_temp_;
    bool  is_first_run_;
};
