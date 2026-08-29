#include "pilot.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>
#include <stdexcept>

namespace hitl {
namespace {
constexpr float kDegPerRad = 180.0f / std::numbers::pi_v<float>;
constexpr float kPanicThreshold = 0.18f;  // рад (~10°) розмаху — межа спокою
constexpr float kPanicRise = 2.0f;        // переляк накопичується, с
constexpr float kPanicFall = 1.0f;        // і відпускає, с
constexpr float kPanicGain = 2.0f;        // максимум K_p зростає втричі
}  // namespace

PilotParams TuneByCrossoverLaw(const ObjectDynamics& obj, float omega_c) {
    if (omega_c <= 0.0f || obj.gain <= 0.0f) {
        throw std::invalid_argument{"частота зрізу й підсилення об'єкта мають бути додатні"};
    }
    PilotParams p;
    p.omega_c = omega_c;

    if (obj.integrating) {
        // Y_c = G/s: потрібний нахил уже є в самому об'єкті, людині вистачає
        // чистого підсилення (T_L = 0). Саме тому Rate «дається легко».
        p.lead_tc = 0.0f;
        p.kp = omega_c / obj.gain;
        return p;
    }

    // Y_c = G/(T*s + 1): щоб дістати на omega_c нахил інтегратора, людина
    // додає випередження й піднімає підсилення до |Y_p*Y_c| = 1.
    const float wt = obj.lag_tc * omega_c;
    const float mag_c = obj.gain / std::sqrt(1.0f + wt * wt);
    p.lead_tc = 0.05f;
    const float lead = std::hypot(1.0f, p.lead_tc * omega_c);
    const float neuro = std::hypot(1.0f, p.neuromuscular_tc * omega_c);
    p.kp = neuro / (mag_c * lead);
    return p;
}

float PhaseMarginWithoutDelay(const PilotParams& p, const ObjectDynamics& obj,
                              float omega_c) noexcept {
    float phase = obj.integrating ? -90.0f : 0.0f;      // вільний інтегратор
    phase -= kDegPerRad * std::atan(obj.lag_tc * omega_c);        // інерція об'єкта
    phase -= kDegPerRad * std::atan(p.neuromuscular_tc * omega_c);  // м'язи
    phase += kDegPerRad * std::atan(p.lead_tc * omega_c);         // випередження
    phase -= kDegPerRad * std::atan(p.lag_tc * omega_c);          // згладжування
    return 180.0f + phase;
}

float RcExpo(float x, float k_expo) noexcept {
    const float k = std::clamp(k_expo, 0.0f, 1.0f);
    return (1.0f - k) * x + k * x * x * x;
}

Pilot::Pilot(const PilotParams& params, float dt)
    : p_{params},
      reaction_{params.reaction_delay, 0.0f, false, 0xA11CEu},
      wobble_{dt} {
    if (dt <= 0.0f || p_.lag_tc < dt) {
        throw std::invalid_argument{"крок симуляції не влазить у ланку згладжування"};
    }
}

float Pilot::Update(float seen_error, float now, float dt) {
    // 1. Чиста фізіологічна затримка exp(-tau_p*s). Амплітуду вона не чіпає —
    //    саме тому й підступна: коливання проходять без послаблення.
    reaction_.Push(seen_error, now);
    const float e = reaction_.Pop(now);

    // 2. Ланка (T_L*s + 1)/(T_I*s + 1) у формі стану:
    //    dx/dt = (e - x)/T_I,  y = (T_L/T_I)*e + (1 - T_L/T_I)*x.
    const float alpha = std::min(1.0f, dt / p_.lag_tc);
    lag_state_ += alpha * (e - lag_state_);
    const float ratio = p_.lead_tc / p_.lag_tc;
    const float y = ratio * e + (1.0f - ratio) * lag_state_;

    // 3. Пастка підсилення. Побачивши, що апарат розгойдується, людина
    //    інстинктивно тисне сильніше — і сама піднімає частоту зрізу, а з
    //    нею й фазовий набіг затримки.
    wobble_.Update(e);
    const float target = wobble_.amplitude() > kPanicThreshold ? 1.0f : 0.0f;
    const float tc = target > panic_ ? kPanicRise : kPanicFall;
    panic_ += (target - panic_) * (dt / tc);

    // 4. Нервово-м'язовий фільтр 1/(T_N*s + 1): рука не рухається миттєво.
    const float beta = dt / (p_.neuromuscular_tc + dt);
    neuromuscular_ += beta * (gain() * y - neuromuscular_);

    // 5. Хід стіка скінченний — далі край механіки.
    neuromuscular_ = std::clamp(neuromuscular_, -1.0f, 1.0f);
    return neuromuscular_;
}

float Pilot::gain() const noexcept { return p_.kp * (1.0f + kPanicGain * panic_); }

}  // namespace hitl
