#include "m3_countersink_calc.h"
#include <math.h>

bool calc_geometry(float plate_thickness, GeometryResult *out_geom) {
    if (!out_geom || plate_thickness <= 0.0f) {
        return false;
    }

    out_geom->plate_thickness = plate_thickness;
    
    /* Глибина конічної фаски 90° для потайного гвинта М3:
       h_k = (d_k - d_h) / 2 = (6.0 - 3.4) / 2 = 1.30 мм */
    out_geom->countersink_depth = (M3_HEAD_DIAMETER - M3_HOLE_DIAMETER) / 2.0f;
    
    /* Залишкова циліндрична частина (поясок) під конусом:
       t_rem = t_plate - h_k */
    out_geom->residual_thickness = plate_thickness - out_geom->countersink_depth;
    
    /* Критерій ножового краю: якщо залишкова товщина менше 0.5 мм 
       або загальна товщина листа менше 1.5 мм — високий ризик зрізу кромки */
    if (out_geom->residual_thickness < 0.5f || plate_thickness < 1.5f) {
        out_geom->knife_edge_risk = true;
    } else {
        out_geom->knife_edge_risk = false;
    }

    return true;
}

float calc_screw_preload(ScrewClass screw_cls, float friction_coeff) {
    (void)friction_coeff;
    /* Номінальне напруження від межі текучості S_y для М3 (коефіцієнт використання 0.75):
       Площа натягу S_t для М3 ≈ 5.03 мм² */
    float tensile_stress_area = 5.03f; /* мм² */
    float yield_strength_mpa = 640.0f;  /* За замовчуванням для класу 8.8 */

    switch (screw_cls) {
        case SCREW_CLASS_8_8:
            yield_strength_mpa = 640.0f; /* 0.8 * 800 МПа */
            break;
        case SCREW_CLASS_10_9:
            yield_strength_mpa = 900.0f; /* 0.9 * 1000 МПа */
            break;
        case SCREW_CLASS_12_9:
            yield_strength_mpa = 1080.0f;/* 0.9 * 1200 МПа */
            break;
        case SCREW_CLASS_A2_70:
            yield_strength_mpa = 450.0f; /* Нержавіюча сталь A2-70 */
            break;
    }

    /* Допустиме зусилля затягування F_p = 0.75 * S_y * A_t */
    float preload = 0.75f * yield_strength_mpa * tensile_stress_area;
    return preload; /* Н */
}

float calc_tightening_torque(float preload_n, float nominal_d, float friction_coeff) {
    /* Формула затягування за закручувальним моментом: M = K * d * F_p 
       Де K — коефіцієнт зав'язки (приблизно 0.2 для стандартного тертя) */
    float k_factor = 0.2f + (friction_coeff - 0.14f) * 0.5f;
    if (k_factor < 0.15f) k_factor = 0.15f;
    
    float diameter_m = nominal_d / 1000.0f; /* переведення в метри */
    float torque_nm = k_factor * diameter_m * preload_n;
    return torque_nm; /* Н*м */
}

static float get_allowable_pressure(HousingMaterial material) {
    switch (material) {
        case MATERIAL_ALUMINUM_6061_T6: return 200.0f; /* МПа */
        case MATERIAL_STEEL_Q235:       return 300.0f; /* МПа */
        case MATERIAL_BRASS_C36000:     return 180.0f; /* МПа */
        case MATERIAL_PLASTIC_ABS:      return 45.0f;  /* МПа */
    }
    return 100.0f;
}

bool verify_m3_countersink_joint(float plate_thickness,
                                 HousingMaterial material,
                                 ScrewClass screw_cls,
                                 float friction_coeff,
                                 GeometryResult *out_geom,
                                 StrengthResult *out_strength) {
    if (!out_geom || !out_strength) {
        return false;
    }

    if (!calc_geometry(plate_thickness, out_geom)) {
        return false;
    }

    float preload = calc_screw_preload(screw_cls, friction_coeff);
    float torque = calc_tightening_torque(preload, M3_DIAMETER_NOMINAL, friction_coeff);

    out_strength->preload_force_n = preload;
    out_strength->tightening_torque_nm = torque;
    out_strength->allowable_pressure_mpa = get_allowable_pressure(material);

    /* Розрахунок контактної площі під потайною голівкою 90°:
       A_k = pi/4 * (d_k^2 - d_h^2) */
    float area_mm2 = (3.14159265f / 4.0f) * (M3_HEAD_DIAMETER * M3_HEAD_DIAMETER - 
                                            M3_HOLE_DIAMETER * M3_HOLE_DIAMETER);
    
    /* Контактний тиск p = F_p / A_k (у МПа, якщо сила в Н і площа в мм²) */
    out_strength->contact_pressure_mpa = preload / area_mm2;

    if (out_strength->contact_pressure_mpa > out_strength->allowable_pressure_mpa) {
        out_strength->pressure_exceeded = true;
    } else {
        out_strength->pressure_exceeded = false;
    }

    /* Загальний статус надійності: немає ризику ножового краю і немає перевищення тиску */
    bool is_safe = (!out_geom->knife_edge_risk) && (!out_strength->pressure_exceeded);
    return is_safe;
}
