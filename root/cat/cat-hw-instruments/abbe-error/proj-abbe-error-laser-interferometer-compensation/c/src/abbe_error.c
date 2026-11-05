#include "abbe_error.h"
#include <string.h>
#include <ctype.h>

double abbe_angle_to_radians(double angle, angle_unit_t unit) {
    switch (unit) {
        case ANGLE_UNIT_ARCSEC:
            return angle * ABBE_ARCSEC_TO_RAD;
        case ANGLE_UNIT_URAD:
            return angle * ABBE_URAD_TO_RAD;
        case ANGLE_UNIT_MRAD:
            return angle * ABBE_MRAD_TO_RAD;
        case ANGLE_UNIT_RAD:
        default:
            return angle;
    }
}

bool abbe_parse_unit(const char *str, angle_unit_t *out_unit) {
    if (!str || !out_unit) {
        return false;
    }

    /* Приведення рядка до нижнього регістру без залежностей від локалі */
    char buf[32];
    size_t i = 0;
    while (str[i] != '\0' && i < sizeof(buf) - 1) {
        buf[i] = (char)tolower((unsigned char)str[i]);
        i++;
    }
    buf[i] = '\0';

    if (strcmp(buf, "arcsec") == 0 || strcmp(buf, "sec") == 0 || strcmp(buf, "as") == 0) {
        *out_unit = ANGLE_UNIT_ARCSEC;
        return true;
    }
    if (strcmp(buf, "urad") == 0 || strcmp(buf, "microrad") == 0 || strcmp(buf, "ur") == 0) {
        *out_unit = ANGLE_UNIT_URAD;
        return true;
    }
    if (strcmp(buf, "mrad") == 0 || strcmp(buf, "millirad") == 0) {
        *out_unit = ANGLE_UNIT_MRAD;
        return true;
    }
    if (strcmp(buf, "rad") == 0 || strcmp(buf, "radian") == 0 || strcmp(buf, "radians") == 0) {
        *out_unit = ANGLE_UNIT_RAD;
        return true;
    }

    return false;
}

const char *abbe_unit_to_string(angle_unit_t unit) {
    switch (unit) {
        case ANGLE_UNIT_ARCSEC:
            return "arcsec";
        case ANGLE_UNIT_URAD:
            return "urad";
        case ANGLE_UNIT_MRAD:
            return "mrad";
        case ANGLE_UNIT_RAD:
            return "rad";
        default:
            return "unknown";
    }
}

bool abbe_calculate_point(const abbe_arm_t *arm,
                          const angle_sample_t *sample,
                          angle_unit_t unit,
                          compensation_entry_t *out_entry) {
    if (!arm || !sample || !out_entry) {
        return false;
    }

    /* Переведення виміряних кутових зміщень у радіани */
    double pitch_rad = abbe_angle_to_radians(sample->pitch, unit);
    double yaw_rad   = abbe_angle_to_radians(sample->yaw, unit);

    /*
     * Кінематична модель похибки першого порядку для малих кутів (sin(theta) ≈ theta):
     * Поворот навколо осі Y (pitch, тангаж) при наявності вертикального плеча dz
     * зміщує робочу точку вздовж поздовжньої осі X:
     *   delta_x_pitch = dz * sin(theta_pitch) ≈ dz * theta_pitch
     *
     * Поворот навколо осі Z (yaw, рискання) при наявності горизонтального плеча dy
     * зміщує робочу точку вздовж поздовжньої осі X:
     *   delta_x_yaw = dy * sin(theta_yaw) ≈ dy * theta_yaw
     *
     * Сумарне лінійне відхилення (похибка позиціонування першого порядку):
     *   delta_x_total = delta_x_pitch + delta_x_yaw
     */
    double err_pitch = arm->dz * pitch_rad;
    double err_yaw   = arm->dy * yaw_rad;
    double total_err = err_pitch + err_yaw;

    /*
     * Компенсуюча поправка протилежна за знаком до похибки:
     *   correction = -total_error
     * Скоригована координата: X_corrected = X_nominal + correction = X_nominal - total_error
     */
    out_entry->position_x     = sample->position_x;
    out_entry->pitch_rad      = pitch_rad;
    out_entry->yaw_rad        = yaw_rad;
    out_entry->error_pitch_mm = err_pitch;
    out_entry->error_yaw_mm   = err_yaw;
    out_entry->total_error_mm = total_err;
    out_entry->correction_mm  = -total_err;

    return true;
}

bool abbe_calculate_batch(const abbe_arm_t *arm,
                          const angle_sample_t *samples,
                          size_t count,
                          angle_unit_t unit,
                          compensation_entry_t *out_entries) {
    if (!arm || !samples || !out_entries || count == 0) {
        return false;
    }

    for (size_t i = 0; i < count; i++) {
        if (!abbe_calculate_point(arm, &samples[i], unit, &out_entries[i])) {
            return false;
        }
    }

    return true;
}
