#pragma once

#include "link.hpp"
#include "pio.hpp"
#include "vehicle.hpp"

namespace hitl {

// Квазілінійна модель Макруера:
// Y_p(s) = K_p * (T_L*s + 1)/(T_I*s + 1) * exp(-tau_p*s) * 1/(T_N*s + 1)
struct PilotParams {
    float kp{1.0f};             // базове підсилення
    float lead_tc{0.0f};        // випередження (Lead), с
    float lag_tc{0.02f};        // згладжування (Lag), с
    float neuromuscular_tc{0.10f};  // в'язкопружність м'язів кисті, с
    float reaction_delay{0.15f};    // чиста фізіологічна затримка, с
    float omega_c{2.5f};        // частота зрізу, під яку людина себе підганяє
};

// Закон перетину: параметри підбираються так, щоб розімкнений контур
// Y_p*Y_c біля omega_c мав вигляд інтегратора з чистою затримкою.
[[nodiscard]] PilotParams TuneByCrossoverLaw(const ObjectDynamics& obj,
                                             float omega_c);

// Запас по фазі БЕЗ чистих затримок — те саме PM_0 з формули
// PM = PM_0 - (180/pi)*omega_c*tau.
[[nodiscard]] float PhaseMarginWithoutDelay(const PilotParams& p,
                                            const ObjectDynamics& obj,
                                            float omega_c) noexcept;

// Крива Expo пульта: u = (1 - k)*x + k*x^3
[[nodiscard]] float RcExpo(float x, float k_expo) noexcept;

class Pilot {
public:
    Pilot(const PilotParams& params, float dt);

    float Update(float seen_error, float now, float dt);

    [[nodiscard]] float panic() const noexcept { return panic_; }
    [[nodiscard]] float gain() const noexcept;
    [[nodiscard]] const PilotParams& params() const noexcept { return p_; }

private:
    PilotParams p_;
    DelayLine<float> reaction_;  // чиста затримка сприйняття
    PioMonitor wobble_;          // людина стежить за розгойдуванням, не за похибкою
    float lag_state_{0.0f};
    float neuromuscular_{0.0f};
    float panic_{0.0f};
};

}  // namespace hitl
