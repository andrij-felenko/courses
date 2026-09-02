#pragma once

#include <string_view>

namespace rover {

/* Уставка: те, чим повільний контур говорить зі швидким. */
struct Setpoint {
    float vx{0.0f};       // поздовжня швидкість, м/с
    float yaw_rate{0.0f}; // кутова швидкість рискання, рад/с
};

struct VehicleState {
    float vx{0.0f};
    float yaw_rate{0.0f};
    float range_ahead_m{0.0f};      // мінімум по передньому сектору лідара
    float tilt_rad{0.0f};
    float pack_ocv_v{0.0f};
    float pack_esr_ohm{0.0f};
    float yaw_disturbance_nm{0.0f}; // момент вітру, який тримають мотори
    bool  range_valid{true};
};

struct Params {
    float mass_kg{18.0f};
    float track_m{0.34f};        // колія: плече диференційної тяги
    float yaw_inertia{0.42f};    // I_z, кг·м²
    float yaw_damping{0.25f};    // Н·м·с/рад
    float roll_resist_n{3.5f};
    float drag_coeff{0.9f};      // Н·с²/м²
    float force_per_amp{6.0f};   // Н на ампер струму ОДНОГО борту
    float idle_current_a{0.9f};
};

struct Limits {
    float v_max{2.4f};
    float accel_max{1.6f};
    float brake_accel{3.0f};
    float yaw_rate_max{1.4f};
    float yaw_accel_max{4.0f};
    float lat_accel_max{2.6f};
    float obstacle_margin_m{0.6f};
    float tilt_max_rad{0.35f};
    float pack_min_v{13.8f};
    float pack_max_current_a{12.0f};
    float cbf_gamma{2.0f};       // γ в умові dh/dt + γ·h(x) ≥ 0
};

struct Obstacle {
    float x{0.0f};
    float y{0.0f};
    float radius{0.0f};
};

enum class Verdict {
    Pass,
    SpeedClamped,
    PowerLimited,
    YawLimited,
    TiltLimited,
    EmergencyStop
};

enum class Reject {
    NotFinite,      // NaN або нескінченність в уставці
    OutOfEnvelope,  // поза фізичною обгорткою апарата
    Stale,          // планувальник не встиг або завис
    NoPlan          // допустимої траєкторії не знайдено
};

[[nodiscard]] constexpr std::string_view name(Verdict v) noexcept
{
    switch (v) {
    case Verdict::Pass:          return "пропущено";
    case Verdict::SpeedClamped:  return "швидкість обрізано";
    case Verdict::PowerLimited:  return "струмовий бюджет";
    case Verdict::YawLimited:    return "момент обрізано";
    case Verdict::TiltLimited:   return "нахил";
    case Verdict::EmergencyStop: return "АВАРІЙНИЙ СТОП";
    }
    return "?";
}

[[nodiscard]] constexpr std::string_view name(Reject r) noexcept
{
    switch (r) {
    case Reject::NotFinite:     return "не число";
    case Reject::OutOfEnvelope: return "поза обгорткою";
    case Reject::Stale:         return "протермінований";
    case Reject::NoPlan:        return "плану немає";
    }
    return "?";
}

/* Вердикти впорядковані за тяжкістю: назовні йде найважчий за такт. */
[[nodiscard]] constexpr Verdict worse(Verdict a, Verdict b) noexcept
{
    return (static_cast<int>(b) > static_cast<int>(a)) ? b : a;
}

} // namespace rover
