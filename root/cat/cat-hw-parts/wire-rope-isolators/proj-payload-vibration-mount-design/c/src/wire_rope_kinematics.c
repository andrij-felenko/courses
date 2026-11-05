#include "wire_rope_kinematics.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define GRAVITY_MSS 9.80665

void spatial_mount_init(spatial_mount_t *mount, isolator_spec_t spec, uint8_t isolator_count, double mass_kg) {
    if (!mount) return;

    mount->spec = spec;
    mount->isolator_count = (isolator_count > 0) ? isolator_count : 4;
    mount->payload_mass_kg = (mass_kg > 0.05) ? mass_kg : 1.0;

    /* Переведення кута нахилу в радіани */
    double rad = spec.tilt_angle_deg * (M_PI / 180.0);
    double sin_a = sin(rad);
    double cos_a = cos(rad);

    /* Векторна декомпозиція жорсткості однієї похилої опори під кутом theta:
       k_vert = k_comp * sin^2(theta) + k_shear * cos^2(theta)
       k_horiz = k_comp * cos^2(theta) + k_shear * sin^2(theta) */
    double k_v_single = (spec.k_compression_n_m * sin_a * sin_a) + 
                        (spec.k_shear_n_m * cos_a * cos_a);
    double k_h_single = (spec.k_compression_n_m * cos_a * cos_a) + 
                        (spec.k_shear_n_m * sin_a * sin_a);

    /* Сумарна жорсткість симетричного підвісу */
    mount->k_total_z_n_m = mount->isolator_count * k_v_single;
    mount->k_total_xy_n_m = (mount->isolator_count / 2.0) * (k_h_single + spec.k_shear_n_m);

    /* Власні частоти коливань: f0 = 1 / (2 * pi) * sqrt(K / m) */
    mount->f0_z_hz = (1.0 / (2.0 * M_PI)) * sqrt(mount->k_total_z_n_m / mount->payload_mass_kg);
    mount->f0_xy_hz = (1.0 / (2.0 * M_PI)) * sqrt(mount->k_total_xy_n_m / mount->payload_mass_kg);
}

double spatial_mount_calculate_dynamic_stroke(const spatial_mount_t *mount, double accel_g, bool is_vertical) {
    if (!mount) return 0.0;

    double dynamic_force_n = mount->payload_mass_kg * (accel_g * GRAVITY_MSS);
    double k_effective = is_vertical ? mount->k_total_z_n_m : mount->k_total_xy_n_m;

    if (k_effective <= 0.0) return 0.0;

    /* Деформація системи у метрах переводиться в міліметри */
    double displacement_m = dynamic_force_n / k_effective;
    return displacement_m * 1000.0;
}

mount_safety_status_t spatial_mount_check_bottoming(const spatial_mount_t *mount, double stroke_mm) {
    if (!mount || mount->spec.max_stroke_mm <= 0.0) {
        return MOUNT_STATUS_BOTTOMING_OUT;
    }

    if (stroke_mm >= mount->spec.max_stroke_mm) {
        return MOUNT_STATUS_BOTTOMING_OUT;
    } else if (stroke_mm >= mount->spec.max_stroke_mm * 0.80) {
        return MOUNT_STATUS_WARNING_STROKE;
    }

    return MOUNT_STATUS_SAFE;
}

const char* spatial_mount_get_status_name(mount_safety_status_t status) {
    switch (status) {
        case MOUNT_STATUS_SAFE:
            return "[НОРМА] Хід у зоні пружної амортизації";
        case MOUNT_STATUS_WARNING_STROKE:
            return "[УВАГА] Запас ходу демпфера менше 20%";
        case MOUNT_STATUS_BOTTOMING_OUT:
            return "[АВАРІЯ: ПРОБИВАННЯ] Жорсткий удар в упор!";
        default:
            return "Невідомий статус";
    }
}
