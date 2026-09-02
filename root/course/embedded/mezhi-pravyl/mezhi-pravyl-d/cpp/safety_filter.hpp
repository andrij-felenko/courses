#pragma once

#include "power_budget.hpp"

namespace rover {

/* Результат такту швидкого контуру: сама уставка плюс усе, чим вона
 * пояснюється в лозі. */
struct Decision {
    Setpoint output{};
    Verdict  verdict{Verdict::Pass};
    float    barrier_h{0.0f};
    float    budget_a{0.0f};
    float    predicted_a{0.0f};
};

/* Детермінований фільтр безпеки: O(1), без циклів невідомої довжини,
 * без динамічної пам'яті й без права відмовити. */
class SafetyFilter {
public:
    SafetyFilter(const Params& p, const Limits& l) noexcept
        : params_{p}, limits_{l} {}

    // h(x) = d_obs − d_safe − v²/(2·a_brake)
    [[nodiscard]] float barrier_value(const VehicleState& st) const noexcept;

    [[nodiscard]] Decision enforce(const VehicleState& st, Setpoint candidate,
                                   float dt) const noexcept;

private:
    void braking_barrier(const VehicleState& st, Setpoint& u, Verdict& v,
                         float h, float dt) const noexcept;
    void traction_limit(Setpoint& u) const noexcept;
    void spend_current(const VehicleState& st, Setpoint& u, Verdict& v,
                       float dt) const noexcept;

    Params params_;
    Limits limits_;
};

} // namespace rover
