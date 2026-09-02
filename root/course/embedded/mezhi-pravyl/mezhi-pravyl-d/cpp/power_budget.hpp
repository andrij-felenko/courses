#pragma once

#include "rover.hpp"

/* Електромеханічний зв'язок: V_term = E_ocv − I_total·ESR. Через цю модель
 * маневр обходу й захист осередків б'ються за той самий ресурс. */

namespace rover::power {

struct Draw {
    float propulsion_a{0.0f};
    float yaw_a{0.0f};
    float total_a{0.0f};
    float terminal_v{0.0f};
};

[[nodiscard]] float drag_force(const Params& p, float v) noexcept;

/* Момент, який мусять дати мотори, щоб за dt вийти на yaw_rate_cmd. */
[[nodiscard]] float yaw_torque(const Params& p, const VehicleState& st,
                               float yaw_rate_cmd, float dt) noexcept;

/* Обернена задача: яку кутову швидкість дає дозволений момент. */
[[nodiscard]] float yaw_rate_for_torque(const Params& p, const VehicleState& st,
                                        float torque_nm, float dt) noexcept;

[[nodiscard]] float yaw_current(const Params& p, float torque_nm) noexcept;

[[nodiscard]] Draw predict(const Params& p, const VehicleState& st,
                           Setpoint cmd, float dt) noexcept;

/* Скільки струму можна взяти, поки клеми не просіли під pack_min_v. */
[[nodiscard]] float budget(const Limits& lim, const VehicleState& st) noexcept;

} // namespace rover::power
