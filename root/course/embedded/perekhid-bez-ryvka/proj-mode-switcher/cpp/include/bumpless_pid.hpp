#pragma once

#include <expected>
#include <optional>

namespace fc {

struct PidGains {
    float kp{0.0f};
    float ki{0.0f};
    float kd{0.0f};
    float kff{0.0f};              // пряма гілка від уставки
    float out_min{0.0f};
    float out_max{1.0f};
    float i_min{0.0f};
    float i_max{0.9f};
    float slew_rate_max{0.0f};    // м/с; 0 — уставка переставляється стрибком
};

enum class HandoverError {
    SensorUnusable,   // вимір непридатний, захоплювати нема від чого
    OutputUnusable    // невідомо, що зараз стоїть на приводі
};

// ПІД з безривковою передачею повноважень. Швидкість виміру приходить
// ззовні (від фузії сенсорів); std::nullopt означає «нема», і тоді
// похідна рахується чисельно.
class BumplessPid {
public:
    constexpr explicit BumplessPid(const PidGains& gains) noexcept : gains_{gains} {}

    // Повертає залишковий стрибок виходу: нуль, якщо інтегратор зарядили
    // точно, ненуль — якщо він уперся в межу.
    [[nodiscard]] std::expected<float, HandoverError>
    handover(float meas, std::optional<float> meas_rate,
             float target_sp, float prev_out) noexcept;

    float update(float meas, std::optional<float> meas_rate, float dt) noexcept;

    void retarget(float target_sp) noexcept;

    [[nodiscard]] float output() const noexcept { return last_out_; }
    [[nodiscard]] float setpoint() const noexcept { return current_sp_; }
    [[nodiscard]] float integral() const noexcept { return integral_; }
    [[nodiscard]] bool ready() const noexcept { return ready_; }
    [[nodiscard]] unsigned bad_samples() const noexcept { return bad_samples_; }

private:
    PidGains gains_;
    float integral_{0.0f};
    float prev_meas_{0.0f};
    float target_sp_{0.0f};
    float current_sp_{0.0f};
    float last_out_{0.0f};
    bool ready_{false};
    unsigned bad_samples_{0};
};

}  // namespace fc
