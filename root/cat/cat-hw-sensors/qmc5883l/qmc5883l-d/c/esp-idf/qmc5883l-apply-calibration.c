#include <stdio.h>
#include <math.h>

typedef struct {
    float v_x, v_y, v_z; // Вектор зсуву Hard Iron
    float s_x, s_y, s_z; // Коефіцієнти масштабування Soft Iron
} mag_calib_t;

typedef struct {
    int16_t raw_x, raw_y, raw_z;
    float cal_x, cal_y, cal_z;
} mag_data_t;

void qmc5883l_apply_calibration(mag_data_t *data, const mag_calib_t *calib) {
    // Крок 1: Віднімання постійного зсуву Hard Iron
    float offset_x = (float)data->raw_x - calib->v_x;
    float offset_y = (float)data->raw_y - calib->v_y;
    float offset_z = (float)data->raw_z - calib->v_z;

    // Крок 2: Масштабування осей Soft Iron
    data->cal_x = offset_x * calib->s_x;
    data->cal_y = offset_y * calib->s_y;
    data->cal_z = offset_z * calib->s_z;
}

float qmc5883l_calculate_heading_2d(float cal_x, float cal_y, float declination_rad) {
    // Тригонометричний азимут atan2(Y, X)
    float heading = atan2f(cal_y, cal_x) + declination_rad;

    // Нормалізація в діапазон [0, 2π)
    if (heading < 0.0f) {
        heading += 2.0f * (float)M_PI;
    } else if (heading >= 2.0f * (float)M_PI) {
        heading -= 2.0f * (float)M_PI;
    }
    return heading * (180.0f / (float)M_PI); // Переведення в градуси
}
