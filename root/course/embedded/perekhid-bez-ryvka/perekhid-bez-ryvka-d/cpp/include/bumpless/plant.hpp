#pragma once

namespace bumpless {

inline constexpr float kGravity = 9.80665f;

// Вертикальний канал квадрокоптера. Тяга нормалізована: газ висіння точно
// врівноважує вагу, тож саме це число й тримає в собі інтегратор.
class QuadPlant {
public:
    QuadPlant(float mass_kg, float hover_throttle, float altitude_m) noexcept;

    void step(float throttle, float dt) noexcept;

    [[nodiscard]] float altitude() const noexcept { return altitude_; }
    [[nodiscard]] float vertical_speed() const noexcept { return vz_; }
    [[nodiscard]] float load_factor() const noexcept { return 1.0f + accel_ / kGravity; }

private:
    float mass_;
    float thrust_max_;
    float drag_{0.65f}; // Н на (м/с)
    float altitude_;
    float vz_{0.0f};
    float accel_{0.0f};
};

struct LateralParams {
    float rate_gain{3.5f};  // рад/с на одиницю команди
    float trim_bias{0.15f}; // сталий паразитний момент, од. команди
    float wind_accel{1.5f}; // боковий вітер, м/с^2
    float drag{0.05f};      // 1/с
};

// Боковий канал: команда приводу задає кутову швидкість крену, кут дає
// горизонтальне прискорення.
class LateralPlant {
public:
    explicit LateralPlant(LateralParams params) noexcept : params_{params} {}

    void step(float actuator, float dt) noexcept;

    [[nodiscard]] float position() const noexcept { return position_; }
    [[nodiscard]] float velocity() const noexcept { return velocity_; }
    [[nodiscard]] float angle() const noexcept { return angle_; }

private:
    LateralParams params_;
    float position_{0.0f};
    float velocity_{0.0f};
    float angle_{0.0f};
};

// Сервопривід з обмеженою швидкістю перекладки й люфтом трансмісії:
// автопілот знає команду, вал живе своїм життям.
class Servo {
public:
    Servo(float rate_max_dps, float deadband_deg, float position_deg) noexcept
        : rate_max_{rate_max_dps}, deadband_{deadband_deg}, position_{position_deg}
    {
    }

    float step(float command_deg, float dt) noexcept;

    [[nodiscard]] float position() const noexcept { return position_; }

private:
    float rate_max_;
    float deadband_;
    float position_;
};

} // namespace bumpless
