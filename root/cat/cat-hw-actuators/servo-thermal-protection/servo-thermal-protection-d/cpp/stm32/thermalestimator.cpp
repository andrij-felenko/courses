#include <cstdint>
#include <algorithm>

class ThermalEstimator {
public:
    struct Config {
        float r_w;        // Активний опір обмотки (Ом)
        float r_th;       // Тепловий опір (К/Вт)
        float tau;        // Теплова часова константа (с)
        float t_amb;      // Температура довкілля (°C)
        float t_warn;     // Поріг початку тротлінгу (°C)
        float t_crit;     // Поріг критичного вимкнення (°C)
        float i_nom;      // Номінальний струм (А)
    };

    enum class State {
        Normal,
        Throttling,
        Critical
    };

    ThermalEstimator(const Config& config)
        : cfg_(config), t_est_(config.t_amb), state_(State::Normal) {}

    void update(float i_phase_rms, float dt) {
        // Теплова потужність втрат Джоуля: P = I² · R
        float p_loss = i_phase_rms * i_phase_rms * cfg_.r_w;
        
        // Розрахунок дискретного приросту температури з урахуванням охолодження
        float t_target = p_loss * cfg_.r_th;
        float dt_est = ((t_target - (t_est_ - cfg_.t_amb)) / cfg_.tau) * dt;
        t_est_ += dt_est;

        // Оновлення стану захисту
        if (t_est_ >= cfg_.t_crit) {
            state_ = State::Critical;
        } else if (t_est_ >= cfg_.t_warn) {
            state_ = State::Throttling;
        } else {
            state_ = State::Normal;
        }
    }

    float getCurrentLimit() const {
        if (state_ == State::Critical) {
            return 0.0f; // Повне вимкнення струму
        }
        if (state_ == State::Throttling) {
            // Лінійна інтерполяція обмеження струму
            float scale = 1.0f - (t_est_ - cfg_.t_warn) / (cfg_.t_crit - cfg_.t_warn);
            return cfg_.i_nom * std::max(0.0f, scale);
        }
        return cfg_.i_nom; // 100% дозволений струм
    }

    float getEstimatedTemperature() const { return t_est_; }
    State getState() const { return state_; }

private:
    Config cfg_;
    float t_est_;
    State state_;
};
