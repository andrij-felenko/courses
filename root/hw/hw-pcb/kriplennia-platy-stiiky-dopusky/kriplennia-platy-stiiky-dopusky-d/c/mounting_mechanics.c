/*
 * mounting_mechanics.c — модуль перевірки механіки кріплення плати (C99).
 */

#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define IPC9704_MAX_MICROSTRAIN  500.0   /* Безпечна межа за IPC/JEDEC-9704 */
#define FR4_YOUNG_MODULUS_GPA    20.0    /* Модуль Юнга FR-4, ГПа */

typedef struct {
    double screw_diameter_mm;     /* Номінальний діаметр гвинта (наприклад, 3.0 для M3) */
    double washer_diameter_mm;    /* Зовнішній діаметр шайби (7.0 для DIN 125A) */
    double nut_factor_k;          /* Коефіцієнт тертя різьби (0.20 для цинкованої сталі) */
    double torque_nm;             /* Крутний момент затягування, Н·м */
    double pcb_thickness_mm;      /* Товщина текстоліту плати, мм */
    double standoff_span_mm;      /* Відстань між сусідніми стійками, мм */
    double standoff_height_err_mm;/* Висотне биття стійок (Δh), мм */
} MountingConfig;

typedef struct {
    double clamp_force_n;         /* Осьове стискаюче зусилля, Н */
    double contact_pressure_mpa;  /* Контактний тиск під шайбою, МПа */
    double surface_microstrain;   /* Відносна деформація поверхні плати, με */
    double min_keepout_radius_mm; /* Мінімальний радіус зони заборони SMD, мм */
    bool   is_safe_ipc9704;       /* Прапорець відповідності нормі IPC-9704 */
} MountingAnalysisResult;

/*
 * Розрахунок механічних параметрів кріпильного вузла
 */
MountingAnalysisResult analyze_mounting_node(const MountingConfig *cfg) {
    MountingAnalysisResult res;

    /* 1. Осьова сила стискання: F = T / (K * d) */
    double d_meters = cfg->screw_diameter_mm * 1e-3;
    res.clamp_force_n = cfg->torque_nm / (cfg->nut_factor_k * d_meters);

    /* 2. Площа контакту шайби: A = (pi/4) * (D_wash^2 - D_hole^2) */
    /* Приймаємо діаметр отвору як d_screw + 0.2 мм */
    double d_hole = cfg->screw_diameter_mm + 0.2;
    double area_mm2 = (M_PI / 4.0) * (pow(cfg->washer_diameter_mm, 2) - pow(d_hole, 2));
    res.contact_pressure_mpa = res.clamp_force_n / area_mm2;

    /* 3. Згинальна мікродеформація поверхні плати: ε = (6 * t * Δh) / L^2 */
    double t_m = cfg->pcb_thickness_mm * 1e-3;
    double dh_m = cfg->standoff_height_err_mm * 1e-3;
    double l_m = cfg->standoff_span_mm * 1e-3;
    
    double strain_abs = (6.0 * t_m * dh_m) / (l_m * l_m);
    res.surface_microstrain = strain_abs * 1e6; /* переведення в με */

    /* 4. Мінімальний радіус зони заборони (Keepout): R_washer + 1.25 мм */
    res.min_keepout_radius_mm = (cfg->washer_diameter_mm / 2.0) + 1.25;

    /* 5. Перевірка відповідності безпечному порогу IPC-9704 */
    res.is_safe_ipc9704 = (res.surface_microstrain <= IPC9704_MAX_MICROSTRAIN);

    return res;
}

int main(void) {
    MountingConfig m3_node = {
        .screw_diameter_mm      = 3.0,
        .washer_diameter_mm     = 7.0,
        .nut_factor_k           = 0.20,
        .torque_nm              = 0.60,
        .pcb_thickness_mm       = 1.60,
        .standoff_span_mm       = 60.0,
        .standoff_height_err_mm = 0.25
    };

    MountingAnalysisResult r = analyze_mounting_node(&m3_node);

    printf("=== АНАЛІЗ КРІПИЛЬНОГО ВУЗЛА M3 ===\n");
    printf("Осьове зусилля стискання F_clamp:   %.1f Н\n", r.clamp_force_n);
    printf("Контактний тиск під шайбою:       %.2f МПа\n", r.contact_pressure_mpa);
    printf("Поверхнева деформація текстоліту: %.1f με\n", r.surface_microstrain);
    printf("Радіус зони заборони SMD (Keepout): %.2f мм\n", r.min_keepout_radius_mm);
    printf("Статус IPC/JEDEC-9704 (<=500 με):  %s\n",
           r.is_safe_ipc9704 ? "БЕЗПЕЧНО" : "НЕБЕЗПЕЧНО: РИЗИК ЗЛАМУ MLCC");

    return 0;
}
