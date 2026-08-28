#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура вхідних геометричних і матеріальних параметрів */
typedef struct {
    double cord_diameter_mm;     /* Діаметр перерізу O-кільця d_s */
    double gland_width_mm;       /* Ширина паза W */
    double gland_depth_mm;       /* Глибина паза H */
    double perimeter_mm;         /* Повний периметр ущільнення L_perim */
    double bolt_spacing_mm;      /* Відстань між кріпильними гвинтами L_bolt */
    double flange_thickness_mm;  /* Товщина стінки фланця t */
    double flange_width_mm;      /* Ширина полиці фланця b */
    double shore_a;              /* Твердість за Шором А (30..90) */
    double mat_young_modulus_mpa;/* Модуль Юнга корпусу (ABS=2000, Алюміній=70000) */
    double internal_volume_l;    /* Внутрішній вільний об'єм корпусу V */
    double temp_hot_c;           /* Робоча температура всередині T_hot */
    double temp_cold_c;          /* Температура зовнішнього середовища T_cold */
    double target_time_sec;      /* Бажаний час вирівнювання тиску tau */
    double vent_permeability;    /* Проникність мембрани, мл/(хв*см^2) при 7 кПа */
} GasketInput;

/* Структура вихідних розрахункових результатів */
typedef struct {
    double compression_ratio_pct;/* Ступінь стиснення C (%) */
    double gland_fill_pct;       /* Заповнення паза F (%) */
    double elastomer_modulus_mpa;/* Розрахунковий модуль Юнга гуми E (МПа) */
    double linear_force_n_per_mm;/* Погонна сила притискання f_lin (Н/мм) */
    double total_clamp_force_n;  /* Повна сила стиснення F_total (Н) */
    double bolt_force_n;         /* Сила на один гвинт (Н) */
    double flange_deflection_mm; /* Прогин фланця delta_max (мм) */
    double max_allowable_defl_mm;/* Граничний допустимий прогин (мм) */
    double thermal_vacuum_kpa;   /* Термічне розрідження Delta_P (кПа) */
    double required_airflow_ml_min; /* Необхідна витрата повітря (мл/хв) */
    double min_vent_area_cm2;    /* Мінімальна площа мембрани (см^2) */
    bool is_compression_ok;
    bool is_fill_ok;
    bool is_deflection_ok;
    bool is_design_valid;
} GasketResult;

/* Головна функція розрахунку параметрів ущільнення та вентиляції */
bool calculate_gasket_seal(const GasketInput *in, GasketResult *out) {
    if (!in || !out) return false;
    if (in->cord_diameter_mm <= 0.0 || in->gland_width_mm <= 0.0 || in->gland_depth_mm <= 0.0) return false;
    if (in->shore_a <= 10.0 || in->shore_a >= 98.0) return false;

    /* 1. Стиснення та заповнення паза */
    out->compression_ratio_pct = ((in->cord_diameter_mm - in->gland_depth_mm) / in->cord_diameter_mm) * 100.0;
    
    double a_seal = (M_PI * in->cord_diameter_mm * in->cord_diameter_mm) / 4.0;
    double a_gland = in->gland_width_mm * in->gland_depth_mm;
    out->gland_fill_pct = (a_seal / a_gland) * 100.0;

    /* 2. Модуль пружності та контактне навантаження */
    out->elastomer_modulus_mpa = (15.75 + 2.15 * in->shore_a) / (100.0 - in->shore_a);
    
    double comp_frac = out->compression_ratio_pct / 100.0;
    if (comp_frac < 0.0) comp_frac = 0.0;
    
    out->linear_force_n_per_mm = out->elastomer_modulus_mpa * in->cord_diameter_mm *
        (1.25 * pow(comp_frac, 1.5) + 0.1 * pow(comp_frac, 3.0));
    
    out->total_clamp_force_n = out->linear_force_n_per_mm * in->perimeter_mm;
    
    double bolt_count = in->perimeter_mm / in->bolt_spacing_mm;
    if (bolt_count < 1.0) bolt_count = 1.0;
    out->bolt_force_n = out->total_clamp_force_n / bolt_count;

    /* 3. Жорсткість і прогин фланця */
    double i_flange = (in->flange_width_mm * pow(in->flange_thickness_mm, 3.0)) / 12.0;
    out->flange_deflection_mm = (out->linear_force_n_per_mm * pow(in->bolt_spacing_mm, 4.0)) /
        (384.0 * in->mat_young_modulus_mpa * i_flange);
    out->max_allowable_defl_mm = 0.05 * in->cord_diameter_mm;

    /* 4. Термічний вакуум і розмір мембрани */
    double t_hot_k = in->temp_hot_c + 273.15;
    double t_cold_k = in->temp_cold_c + 273.15;
    double p_atm_kpa = 101.325;
    
    if (t_hot_k > t_cold_k) {
        out->thermal_vacuum_kpa = p_atm_kpa * (1.0 - (t_cold_k / t_hot_k));
    } else {
        out->thermal_vacuum_kpa = 0.0;
    }

    double tau_min = in->target_time_sec / 60.0;
    if (tau_min <= 0.0) tau_min = 1.0;
    
    out->required_airflow_ml_min = (in->internal_volume_l * 1000.0 * (out->thermal_vacuum_kpa / p_atm_kpa)) / tau_min;
    
    double delta_p_norm = out->thermal_vacuum_kpa / 7.0; /* Нормування на 7 кПа */
    if (delta_p_norm < 0.1) delta_p_norm = 0.1;
    
    out->min_vent_area_cm2 = out->required_airflow_ml_min / (in->vent_permeability * delta_p_norm);

    /* 5. Перевірка критеріїв надійності */
    out->is_compression_ok = (out->compression_ratio_pct >= 18.0 && out->compression_ratio_pct <= 32.0);
    out->is_fill_ok = (out->gland_fill_pct >= 65.0 && out->gland_fill_pct <= 85.0);
    out->is_deflection_ok = (out->flange_deflection_mm <= out->max_allowable_defl_mm);
    
    out->is_design_valid = out->is_compression_ok && out->is_fill_ok && out->is_deflection_ok;
    return true;
}
