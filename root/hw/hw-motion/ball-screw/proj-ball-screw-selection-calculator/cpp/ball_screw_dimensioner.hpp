#pragma once
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>

// Схеми закріплення опор кулькового гвинта
enum class MountingScheme {
    FixedFree,          // Жорстко - Вільний кінець
    SupportedSupported, // Оперто - Оперто
    FixedSupported,     // Жорстко - Оперто
    FixedFixed          // Жорстко - Жорстко
};

// Фаза робочого циклу лінійної осі
struct DutyPhase {
    double duration_s{0.0};       // Тривалість фази, с
    double speed_rpm{0.0};        // Частота обертання, об/хв
    double axial_force_N{0.0};    // Осьове навантаження, Н
};

// Геометричні та механічні параметри ШВП
struct BallScrewParams {
    double nominal_diameter_mm{25.0};        // Номінальний діаметр, мм
    double lead_mm{5.0};                     // Крок різьби, мм
    double root_diameter_mm{21.5};           // Внутрішній діаметр западин різьби, мм
    double length_mm{800.0};                 // Вільна довжина гвинта між опорами, мм
    double dynamic_rating_C_N{18500.0};      // Динамічна вантажопідйомність C, Н
    double static_rating_C0_N{38200.0};      // Статична вантажопідйомність C0, Н
    MountingScheme mounting{MountingScheme::FixedSupported}; // Схема встановлення опор
    double young_modulus_GPa{206.0};         // Модуль пружності Юнга для сталі, ГПа
    double thermal_expansion_coeff{11.7e-6}; // Коефіцієнт лінійного розширення, 1/°C
};

// Інженерний звіт верифікації
struct DimensioningReport {
    double equivalent_force_N{0.0};      // Еквівалентна динамічна сила Fm за ISO 3408
    double equivalent_speed_rpm{0.0};    // Еквівалентна частота обертання nm
    double life_hours{0.0};              // Розрахункова довговічність L10h у годинах
    double critical_speed_rpm{0.0};      // Критична частота згинального резонансу n_cr
    double max_operating_speed_rpm{0.0}; // Максимальна швидкість за робочим циклом
    double buckling_force_N{0.0};        // Критична сила поздовжнього вигину за Ейлером
    double max_axial_force_N{0.0};       // Максимальне осьове навантаження за циклом
    double static_safety_factor{0.0};    // Статичний коефіцієнт запасу S0 = C0 / F_max
    double thermal_expansion_um{0.0};    // Вільне теплове подовження гвинта, мкм
    double thermal_prestretch_N{0.0};    // Зусилля розтягу для повної термокомпенсації
    bool speed_safe{false};              // n_max <= 0.8 * n_cr
    bool buckling_safe{false};           // F_max <= 0.5 * F_cr
    bool static_safe{false};             // S0 >= 2.0
    bool life_adequate{false};           // L10h >= цільового ресурсу
};

class BallScrewDimensioner {
public:
    explicit BallScrewDimensioner(BallScrewParams params)
        : params_(params) {}

    // Коефіцієнт схеми опор для критичної швидкості
    static double get_critical_speed_factor(MountingScheme scheme) {
        switch (scheme) {
            case MountingScheme::FixedFree:          return 0.36;
            case MountingScheme::SupportedSupported: return 1.00;
            case MountingScheme::FixedSupported:     return 1.56;
            case MountingScheme::FixedFixed:         return 2.27;
        }
        return 1.0;
    }

    // Коефіцієнт схеми опор для ейлерової стійкості вигину
    static double get_buckling_factor(MountingScheme scheme) {
        switch (scheme) {
            case MountingScheme::FixedFree:          return 0.25;
            case MountingScheme::SupportedSupported: return 1.00;
            case MountingScheme::FixedSupported:     return 2.05;
            case MountingScheme::FixedFixed:         return 4.00;
        }
        return 1.0;
    }

    // Розрахунок характеристик циклу та надійності передачі
    DimensioningReport evaluate(const std::vector<DutyPhase>& cycle, double temp_rise_degC, double target_life_h = 20000.0) const {
        DimensioningReport rep;
        if (cycle.empty()) return rep;

        double total_time = 0.0;
        double sum_n_t = 0.0;
        double sum_f3_n_t = 0.0;
        double max_force = 0.0;
        double max_speed = 0.0;

        for (const auto& p : cycle) {
            total_time += p.duration_s;
            double abs_n = std::abs(p.speed_rpm);
            double abs_f = std::abs(p.axial_force_N);
            sum_n_t += abs_n * p.duration_s;
            sum_f3_n_t += std::pow(abs_f, 3.0) * abs_n * p.duration_s;
            if (abs_f > max_force) max_force = abs_f;
            if (abs_n > max_speed) max_speed = abs_n;
        }

        rep.max_operating_speed_rpm = max_speed;
        rep.max_axial_force_N = max_force;

        // Еквівалентна швидкість та навантаження за стандартом ISO 3408
        if (total_time > 0.0 && sum_n_t > 0.0) {
            rep.equivalent_speed_rpm = sum_n_t / total_time;
            rep.equivalent_force_N = std::cbrt(sum_f3_n_t / sum_n_t);
        }

        // Номінальний ресурс L10h у годинах роботи
        if (rep.equivalent_force_N > 0.0 && rep.equivalent_speed_rpm > 0.0) {
            double l10_rev = std::pow(params_.dynamic_rating_C_N / rep.equivalent_force_N, 3.0) * 1e6;
            rep.life_hours = l10_rev / (60.0 * rep.equivalent_speed_rpm);
        }

        // Критична частота обертання биття вала (об/хв)
        double lambda_n = get_critical_speed_factor(params_.mounting);
        constexpr double f_n_base = 9.7e6;
        rep.critical_speed_rpm = lambda_n * f_n_base * (params_.root_diameter_mm / std::pow(params_.length_mm, 2.0));

        // Граничне навантаження поздовжнього вигину за формулою Ейлера (Н)
        double lambda_k = get_buckling_factor(params_.mounting);
        double d_r_m = params_.root_diameter_mm * 1e-3;
        double L_m = params_.length_mm * 1e-3;
        double I = (M_PI * std::pow(d_r_m, 4.0)) / 64.0;
        double E = params_.young_modulus_GPa * 1e9;
        rep.buckling_force_N = lambda_k * (std::pow(M_PI, 2.0) * E * I) / std::pow(L_m, 2.0);

        // Статичний коефіцієнт запасу
        if (rep.max_axial_force_N > 0.0) {
            rep.static_safety_factor = params_.static_rating_C0_N / rep.max_axial_force_N;
        }

        // Теплове подовження вала та компенсаційне попереднє розтягування
        double L = params_.length_mm;
        rep.thermal_expansion_um = params_.thermal_expansion_coeff * L * temp_rise_degC * 1000.0;
        double A_m2 = M_PI * std::pow(d_r_m / 2.0, 2.0);
        rep.thermal_prestretch_N = E * A_m2 * params_.thermal_expansion_coeff * temp_rise_degC;

        // Критерії надійності та безпеки експлуатації
        rep.speed_safe = (rep.max_operating_speed_rpm <= 0.8 * rep.critical_speed_rpm);
        rep.buckling_safe = (rep.max_axial_force_N <= 0.5 * rep.buckling_force_N);
        rep.static_safe = (rep.static_safety_factor >= 2.0);
        rep.life_adequate = (rep.life_hours >= target_life_h);

        return rep;
    }

private:
    BallScrewParams params_;
};
