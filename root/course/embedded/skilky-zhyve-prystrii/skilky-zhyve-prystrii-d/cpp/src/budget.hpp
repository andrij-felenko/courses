#pragma once

// Зведення енергетичного бюджету: паспортна ємність → фактично доступна,
// профіль циклу плюс саморозряд → сумарний струм, і звідси час автономності.
//
// Тут же перевірка імпульсної просадки. Якщо напруга під час передачі
// провалюється нижче порогу відсічки, рахувати години немає сенсу: пристрій
// піде в цикл перезавантажень із повною батареєю.

#include "cell.hpp"
#include "load_profile.hpp"

#include <expected>
#include <optional>
#include <string>

namespace autonomy {

struct Site {
    double cutoff_v{};      // поріг BOD плюс dropout стабілізатора
    double temp_c{};
    Days storage{};         // скільки комірка простояла в спокої до першого імпульсу
    double safety_factor{}; // k_safe — запас на розкид партії та старіння
};

enum class Limiter {
    Brownout,       // просадка нижче відсічки — пристрій перезавантажується
    SelfDischarge,  // стеля хімії: комірка витікає швидше, ніж її споживають
    ActivePhase,    // найдорожча фаза пробудження
    Sleep,          // струм сну разом зі струмом спокою стабілізатора
};

std::string_view describe(Limiter limiter) noexcept;

struct Buffer {
    double farads{};
    double esr_max_ohm{};
    bool hybrid_needed{};   // керамікою й танталом стільки не набрати
};

struct PulseCheck {
    double r_int_ohm{};
    double sag_v{};         // ΔV = I_pulse · R_int
    double v_term_v{};      // V_term = V_ocv − ΔV
    bool brownout{};

    double r_passivated_ohm{};
    double sag_storage_v{};
    double v_term_storage_v{};
    bool brownout_after_storage{};

    double headroom_v{};            // робоче плато мінус поріг відсічки
    std::optional<Buffer> buffer{}; // порожньо — буфер не потрібен
    bool buffer_impossible{};       // поріг вищий за плато: буфер не врятує
};

struct Estimate {
    // Водоспад втрат ємності.
    double eta_cutoff{};
    double eta_temp{};
    double eta_pulse{};
    double ocv_cutoff_v{};   // OCV, за якої імпульс уперше провалює поріг
    double c_after_cutoff_mah{};
    double c_after_temp_mah{};
    double c_eff_mah{};

    // Струми.
    double i_avg_ma{};
    double i_self_ma{};
    double i_total_ma{};

    // Час.
    Hours life{};
    Years life_years{};
    Years guaranteed{};
    Years naive{};          // паспортна ємність поділена на середній струм
    double optimism_ratio{};

    Limiter limiter{Limiter::ActivePhase};
    std::string limiter_note;

    PulseCheck pulse;
    Load load;
};

std::expected<Estimate, Error> estimate(const Cell& cell, const LoadProfile& profile, const Site& site);

}  // namespace autonomy
