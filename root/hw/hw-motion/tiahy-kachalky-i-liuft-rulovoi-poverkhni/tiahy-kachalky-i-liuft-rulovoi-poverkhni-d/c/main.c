/* Калькулятор аеродинамічного моменту та підбору тяг сервоприводу на C99 */
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double air_density_kg_m3;    /* густина повітря, кг/м3 (типово 1.225) */
    double max_speed_mps;        /* максимальна швидкість польоту v_ne, м/с */
} FlightConditions;

typedef struct {
    double span_m;               /* розмах рульової поверхні, м */
    double chord_m;              /* середня хорда руля від осі завіси, м */
    double max_deflection_deg;   /* максимальний кут відхилення руля, градуси */
    double ch_per_deg;           /* коефіцієнт шарнірного моменту на градус (0.003-0.005) */
} ControlSurface;

typedef struct {
    double r_servo_mm;           /* робоче плече качалки сервоприводу, мм */
    double r_horn_mm;            /* робоче плече кабанчика руля, мм */
    double rod_length_mm;        /* довжина тяги, мм */
    double rod_outer_d_mm;       /* зовнішній діаметр тяги/трубки, мм */
    double rod_inner_d_mm;       /* внутрішній діаметр (0 для суцільного стрижня), мм */
    double young_modulus_gpa;    /* модуль Юнга матеріалу, ГПа (сталь 210, карбон 130) */
    double efficiency;           /* ККД шарнірів (0.90 - 0.95) */
} LinkageSetup;

typedef struct {
    double dynamic_pressure_pa;  /* динамічний швидкісний напір q, Па */
    double hinge_moment_nm;      /* шарнірний аеродинамічний момент руля, Н·м */
    double pushrod_force_n;      /* осьове зусилля в тязі, Н */
    double euler_buckling_pcr_n; /* критична сила стійкості тяги за Ейлером, Н */
    double buckling_margin;      /* запас стійкості тяги на стиск (P_cr / F_rod) */
    double req_servo_torque_nm;  /* номінальний потрібний момент на валу серво, Н·м */
    double req_servo_torque_kgcm;/* момент у звичних модельних одиницях, кг·см */
    bool   is_safe;              /* чи задовольняє система критеріям стійкості */
} LinkageAnalysisResult;

LinkageAnalysisResult analyze_control_linkage(
    const FlightConditions *flight,
    const ControlSurface *surface,
    const LinkageSetup *linkage,
    double safety_factor)
{
    LinkageAnalysisResult res;

    /* 1. Динамічний напір q = 0.5 * rho * v^2 */
    res.dynamic_pressure_pa = 0.5 * flight->air_density_kg_m3 * 
                              flight->max_speed_mps * flight->max_speed_mps;

    /* 2. Площа руля S = b * c */
    double surface_area = surface->span_m * surface->chord_m;

    /* 3. Коефіцієнт шарнірного моменту C_h */
    double c_h = surface->ch_per_deg * surface->max_deflection_deg;

    /* 4. Шарнірний момент M_h = q * S * c * C_h */
    res.hinge_moment_nm = res.dynamic_pressure_pa * surface_area * surface->chord_m * c_h;

    /* 5. Зусилля в тязі F_rod = M_h / (r_horn * eta) */
    double r_horn_m = linkage->r_horn_mm * 1e-3;
    res.pushrod_force_n = res.hinge_moment_nm / (r_horn_m * linkage->efficiency);

    /* 6. Осьовий момент інерції перерізу тяги I = pi * (D^4 - d^4) / 64 */
    double D_m = linkage->rod_outer_d_mm * 1e-3;
    double d_m = linkage->rod_inner_d_mm * 1e-3;
    double I_moment = (M_PI * (pow(D_m, 4.0) - pow(d_m, 4.0))) / 64.0;

    /* 7. Критична сила стійкості Ейлера P_cr = (pi^2 * E * I) / L^2 */
    double L_m = linkage->rod_length_mm * 1e-3;
    double E_pa = linkage->young_modulus_gpa * 1e9;
    res.euler_buckling_pcr_n = (M_PI * M_PI * E_pa * I_moment) / (L_m * L_m);

    /* 8. Коефіцієнт запасу тяги на вигин */
    res.buckling_margin = (res.pushrod_force_n > 1e-6) 
                          ? (res.euler_buckling_pcr_n / res.pushrod_force_n) 
                          : 999.0;

    /* 9. Потрібний момент на сервоприводі M_servo = F_rod * r_servo * k_margin */
    double r_servo_m = linkage->r_servo_mm * 1e-3;
    res.req_servo_torque_nm = (res.hinge_moment_nm / linkage->efficiency) * 
                              (r_servo_m / r_horn_m) * safety_factor;

    /* Переведення в кг·см (1 Н·м ≈ 10.197 кг·см) */
    res.req_servo_torque_kgcm = res.req_servo_torque_nm * 10.19716;

    /* Перевірка критеріїв: запас тяги > 2.0 і момент > 0 */
    res.is_safe = (res.buckling_margin >= 2.0);

    return res;
}

int main(void) {
    FlightConditions flight = {
        .air_density_kg_m3 = 1.225,
        .max_speed_mps = 41.67       /* 150 км/год */
    };

    ControlSurface aileron = {
        .span_m = 0.45,              /* 450 мм розмах елерона */
        .chord_m = 0.055,            /* 55 мм хорда елерона */
        .max_deflection_deg = 20.0,  /* максимальне відхилення 20 градусів */
        .ch_per_deg = 0.0035         /* коефіцієнт C_h на градус */
    };

    /* Конфігурація А: тонкий сталевий дріт 1.2 мм */
    LinkageSetup steel_setup = {
        .r_servo_mm = 15.0,
        .r_horn_mm = 20.0,
        .rod_length_mm = 220.0,
        .rod_outer_d_mm = 1.2,
        .rod_inner_d_mm = 0.0,
        .young_modulus_gpa = 210.0,  /* Сталь */
        .efficiency = 0.92
    };

    /* Конфігурація Б: карбонова трубка 4.0/2.5 мм */
    LinkageSetup carbon_setup = {
        .r_servo_mm = 15.0,
        .r_horn_mm = 20.0,
        .rod_length_mm = 220.0,
        .rod_outer_d_mm = 4.0,
        .rod_inner_d_mm = 2.5,
        .young_modulus_gpa = 130.0,  /* Карбон CFRP */
        .efficiency = 0.95
    };

    LinkageAnalysisResult res_a = analyze_control_linkage(&flight, &aileron, &steel_setup, 2.2);
    LinkageAnalysisResult res_b = analyze_control_linkage(&flight, &aileron, &carbon_setup, 2.2);

    printf("=== РОЗРАХУНОК РУЛЬОВОЇ ТЯГИ ТА СЕРВОПРИВОДУ ===\n");
    printf("Швидкісний напір: %.1f Па\n", res_a.dynamic_pressure_pa);
    printf("Шарнірний момент руля: %.4f Н·м\n\n", res_a.hinge_moment_nm);

    printf("[ВАРІАНТ А: Сталевий дріт d=1.2 мм]\n");
    printf("  Зусилля в тязі: %.2f Н\n", res_a.pushrod_force_n);
    printf("  Критична сила Ейлера P_cr: %.2f Н\n", res_a.euler_buckling_pcr_n);
    printf("  Запас на поздовжній вигин: %.2f (безпечно: %s)\n", 
           res_a.buckling_margin, res_a.is_safe ? "ТАК" : "НІ, ВИГИН!");
    printf("  Потрібний момент серво: %.2f кг·см\n\n", res_a.req_servo_torque_kgcm);

    printf("[ВАРІАНТ Б: Карбонова трубка D=4.0 мм, d=2.5 мм]\n");
    printf("  Зусилля в тязі: %.2f Н\n", res_b.pushrod_force_n);
    printf("  Критична сила Ейлера P_cr: %.2f Н\n", res_b.euler_buckling_pcr_n);
    printf("  Запас на поздовжній вигин: %.2f (безпечно: %s)\n", 
           res_b.buckling_margin, res_b.is_safe ? "ТАК" : "НІ, ВИГИН!");
    printf("  Потрібний момент серво: %.2f кг·см\n", res_b.req_servo_torque_kgcm);

    return 0;
}
