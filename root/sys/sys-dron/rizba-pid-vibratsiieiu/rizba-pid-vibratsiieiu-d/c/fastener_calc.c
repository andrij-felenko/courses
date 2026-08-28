/* fastener_calc.c - Інженерний калькулятор моменту затягування та напружень */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    BOLT_GRADE_8_8,
    BOLT_GRADE_10_9,
    BOLT_GRADE_12_9,
    BOLT_GRADE_A2_70  /* Нержавіюча сталь */
} BoltGrade;

typedef enum {
    SURFACE_DRY_STEEL,      /* Суха сталь (mu = 0.20) */
    SURFACE_THREADLOCKER,   /* Анаеробний фіксатор різьби (mu = 0.13) */
    SURFACE_OILED           /* Змащена різьба (mu = 0.10) */
} LubricationState;

typedef struct {
    double nominal_dia_mm;      /* Номінальний діаметр d (мм) */
    double pitch_mm;            /* Крок різьби p (мм) */
    double bearing_inner_dia_mm;/* Внутрішній діаметр отвору d_h (мм) */
    double bearing_outer_dia_mm;/* Зовнішній діаметр опорного фланця d_w (мм) */
    BoltGrade grade;
    LubricationState lube;
    double clamp_material_limit_mpa; /* Границя міцності на стиск (карбон: 140 МПа) */
    double thread_shear_limit_mpa;   /* Границя зрізу внутрішньої різьби (6061-T6: 150 МПа) */
} FastenerSpec;

typedef struct {
    double stress_area_mm2;       /* Розрахункова площа A_s (мм²) */
    double target_preload_n;      /* Рекомендоване зусилля натягу F_p (Н) */
    double tightening_torque_nm;  /* Розрахунковий момент затягування T (Н·м) */
    double bearing_pressure_mpa;  /* Контактний тиск під головкою/шайбою (МПа) */
    bool is_bearing_safe;         /* Чи витримує матеріал тиск */
    double min_thread_engagement_mm; /* Мінімальна довжина різьби в алюмінії (мм) */
} FastenerResult;

static double get_yield_strength(BoltGrade grade) {
    switch (grade) {
        case BOLT_GRADE_8_8:   return 640.0;
        case BOLT_GRADE_10_9:  return 940.0;
        case BOLT_GRADE_12_9:  return 1080.0;
        case BOLT_GRADE_A2_70: return 450.0;
        default: return 640.0;
    }
}

static double get_tensile_strength(BoltGrade grade) {
    switch (grade) {
        case BOLT_GRADE_8_8:   return 800.0;
        case BOLT_GRADE_10_9:  return 1040.0;
        case BOLT_GRADE_12_9:  return 1220.0;
        case BOLT_GRADE_A2_70: return 700.0;
        default: return 800.0;
    }
}

static void get_friction_coeffs(LubricationState lube, double *mu_th, double *mu_b) {
    switch (lube) {
        case SURFACE_DRY_STEEL:
            *mu_th = 0.20; *mu_b = 0.20;
            break;
        case SURFACE_THREADLOCKER:
            *mu_th = 0.13; *mu_b = 0.13;
            break;
        case SURFACE_OILED:
            *mu_th = 0.10; *mu_b = 0.10;
            break;
    }
}

FastenerResult calculate_fastener_joint(const FastenerSpec *spec) {
    FastenerResult res;
    double d = spec->nominal_dia_mm;
    double p = spec->pitch_mm;
    
    /* 1. Розрахункова площа напруженого перерізу стрижня за ISO 898-1 */
    double d_s = d - 0.9382 * p;
    res.stress_area_mm2 = (M_PI / 4.0) * d_s * d_s;
    
    /* 2. Цільовий натяг болта: 85% від границі текучості матеріалу */
    double yield_str = get_yield_strength(spec->grade);
    res.target_preload_n = 0.85 * res.stress_area_mm2 * yield_str;
    
    /* 3. Момент затягування за формулою Келлермана-Кляйна (VDI 2230) */
    double mu_th, mu_b;
    get_friction_coeffs(spec->lube, &mu_th, &mu_b);
    
    double d_2 = d - 0.64952 * p;                    /* Середній діаметр різьби */
    double r_b = (spec->bearing_outer_dia_mm + spec->bearing_inner_dia_mm) / 4.0;
    double cos_half_alpha = 0.866025;                /* cos(30°) для метричного профілю 60° */
    
    double term_pitch   = p / (2.0 * M_PI);
    double term_thread  = (mu_th * d_2) / (2.0 * cos_half_alpha);
    double term_bearing = mu_b * r_b;
    
    /* T (Н·м) = F_p (Н) * (сума в метрах) */
    res.tightening_torque_nm = res.target_preload_n * (term_pitch + term_thread + term_bearing) / 1000.0;
    
    /* 4. Контактний тиск під фланцем або шайбою */
    double dw = spec->bearing_outer_dia_mm;
    double dh = spec->bearing_inner_dia_mm;
    double a_bearing = (M_PI / 4.0) * (dw * dw - dh * dh);
    
    res.bearing_pressure_mpa = res.target_preload_n / a_bearing;
    res.is_bearing_safe = (res.bearing_pressure_mpa <= spec->clamp_material_limit_mpa);
    
    /* 5. Довжина зачеплення різьби в алюмінії проти зрізу витків з запасом 1.25 */
    double tensile_str = get_tensile_strength(spec->grade);
    double shear_area_factor = M_PI * d * 0.75;
    res.min_thread_engagement_mm = 1.25 * (res.stress_area_mm2 * tensile_str) / 
                                   (shear_area_factor * spec->thread_shear_limit_mpa);
    
    return res;
}

int main(void) {
    FastenerSpec spec_m3 = {
        .nominal_dia_mm = 3.0,
        .pitch_mm = 0.5,
        .bearing_inner_dia_mm = 3.4,
        .bearing_outer_dia_mm = 7.0, /* Гвинт ISO 7380-2 з фланцем */
        .grade = BOLT_GRADE_10_9,
        .lube = SURFACE_THREADLOCKER,
        .clamp_material_limit_mpa = 140.0, /* Карбон CFRP */
        .thread_shear_limit_mpa = 150.0    /* Алюміній 6061-T6 */
    };
    
    FastenerResult r = calculate_fastener_joint(&spec_m3);
    
    printf("=== Розрахунок кріплення M3 (клас 10.9) у карбон та алюміній ===\n");
    printf("Площа розтягу A_s:          %.3f мм²\n", r.stress_area_mm2);
    printf("Рекомендований натяг F_p:   %.1f Н\n", r.target_preload_n);
    printf("Момент затягування T:       %.2f Н·м\n", r.tightening_torque_nm);
    printf("Контактний тиск під шайбою: %.1f МПа [%s]\n", 
           r.bearing_pressure_mpa, r.is_bearing_safe ? "БЕЗПЕЧНО" : "УВАГА: РОЗДАВЛЮВАННЯ");
    printf("Мін. довжина різьби в 6061: %.2f мм (%.1f · d)\n", 
           r.min_thread_engagement_mm, r.min_thread_engagement_mm / spec_m3.nominal_dia_mm);
    
    return 0;
}
