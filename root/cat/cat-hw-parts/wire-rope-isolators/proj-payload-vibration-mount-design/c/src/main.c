#include "wire_rope_kinematics.h"
#include <stdio.h>

int main(void) {
    printf("====================================================================\n");
    printf("  МОДУЛЬ ВЕКТОРНОГО РОЗРАХУНКУ ПРОСТОРОВОГО ВІБРОПІДВІСУ 45° (C99) \n");
    printf("====================================================================\n");

    /* Специфікація комбінованого ізолятора (трос сталевий 1.5 мм + силіконовий демпфер) */
    isolator_spec_t isolator = {
        .k_compression_n_m = 6500.0, /* стиск під кутом */
        .k_shear_n_m       = 2400.0, /* зсув */
        .max_stroke_mm     = 8.5,    /* конструктивний зазор до жорсткого упору */
        .tilt_angle_deg    = 45.0    /* просторова орієнтація 45 градусів */
    };

    spatial_mount_t mount;
    double payload_mass = 1.35; /* 1.35 кг блок авіоніки */
    spatial_mount_init(&mount, isolator, 4, payload_mass);

    printf("Конфігурація підвісу:\n");
    printf(" - Маса навантаження       : %.2f кг\n", mount.payload_mass_kg);
    printf(" - Кількість опор          : %u шт.\n", mount.isolator_count);
    printf(" - Кут нахилу до горизонту : %.1f град\n", mount.spec.tilt_angle_deg);
    printf(" - Сумарна жорсткість K_z   : %.1f Н/м\n", mount.k_total_z_n_m);
    printf(" - Сумарна жорсткість K_xy  : %.1f Н/м\n", mount.k_total_xy_n_m);
    printf(" - Резонансна частота f0_z  : %.2f Гц\n", mount.f0_z_hz);
    printf(" - Резонансна частота f0_xy : %.2f Гц\n", mount.f0_xy_hz);
    printf(" - Межа віброізоляції f_iso : %.2f Гц\n", mount.f0_z_hz * 1.4142);
    printf("--------------------------------------------------------------------\n");
    printf("Моделювання реакції на вертикальні ударні перевантаження:\n");
    printf(" Перевантаження | Сила удару (Н) | Динамічний хід | Статус безпеки\n");
    printf("--------------------------------------------------------------------\n");

    double shock_levels[] = { 2.0, 5.0, 8.0, 10.0, 12.0, 15.0 };
    size_t count = sizeof(shock_levels) / sizeof(shock_levels[0]);

    for (size_t i = 0; i < count; i++) {
        double g_load = shock_levels[i];
        double stroke = spatial_mount_calculate_dynamic_stroke(&mount, g_load, true);
        mount_safety_status_t status = spatial_mount_check_bottoming(&mount, stroke);
        double force = mount.payload_mass_kg * g_load * 9.80665;

        printf("   %4.1f G      |   %7.1f Н     |    %5.2f мм    | %s\n",
               g_load, force, stroke, spatial_mount_get_status_name(status));
    }

    printf("====================================================================\n");
    return 0;
}
