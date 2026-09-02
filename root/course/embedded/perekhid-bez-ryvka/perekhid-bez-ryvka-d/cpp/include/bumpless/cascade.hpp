#pragma once

#include "bumpless/pid.hpp"
#include "bumpless/plant.hpp"

namespace bumpless {

struct CascadeMeasurement {
    float position{0.0f};
    float velocity{0.0f};
    float angle{0.0f};
};

[[nodiscard]] CascadeMeasurement measure(const LateralPlant& plant) noexcept;

struct CascadeConfig {
    PidConfig position{};
    PidConfig velocity{};
    PidConfig angle{};
    // Передавальні коефіцієнти між поверхами: вихід зовнішнього контуру
    // множиться на них, стаючи уставкою внутрішнього. У формулі статті
    // I_velocity = Angle_actual / Kp_angle це і є той дільник.
    float velocity_from_position_gain{1.0f};
    float angle_from_velocity_gain{1.0f};
    unsigned position_divider{50u}; // скільки швидких тактів на такт позиції
    unsigned velocity_divider{20u};
};

// Каскад «позиція -> швидкість -> кут -> привід» з рознесеними частотами.
class CascadeController {
public:
    explicit CascadeController(const CascadeConfig& cfg) noexcept
        : cfg_{cfg}
        , position_{cfg.position}
        , velocity_{cfg.velocity}
        , angle_{cfg.angle}
    {
    }

    // Половини транзакції. Нарізно їх викликає лише демонстрація розірваного
    // переходу; у польоті працює handover(), який робить обидві разом.
    void load_inner(const CascadeMeasurement& m, float prev_actuator) noexcept;
    void load_outer(const CascadeMeasurement& m, float target_position) noexcept;

    void handover(const CascadeMeasurement& m, float target_position,
                  float prev_actuator) noexcept;
    void start_naive(float target_position) noexcept;

    [[nodiscard]] float update(const CascadeMeasurement& m, float dt_fast) noexcept;

    [[nodiscard]] float last_actuator() const noexcept { return last_actuator_; }

private:
    CascadeConfig cfg_;
    BumplessPidController position_;
    BumplessPidController velocity_;
    BumplessPidController angle_;
    unsigned tick_{0u};
    float velocity_sp_{0.0f};
    float angle_sp_{0.0f};
    float last_actuator_{0.0f};
};

} // namespace bumpless
