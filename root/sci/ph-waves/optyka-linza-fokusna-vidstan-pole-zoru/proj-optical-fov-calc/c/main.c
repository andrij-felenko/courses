#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define RAD_TO_DEG(rad) ((rad) * (180.0 / M_PI))
#define DEG_TO_RAD(deg) ((deg) * (M_PI / 180.0))

/* Структура специфікації світлочутливої матриці сенсора */
typedef struct {
    double width_mm;          /* Фізична ширина світлочутливої зони (мм) */
    double height_mm;         /* Фізична висота світлочутливої зони (мм) */
    double pixel_pitch_um;    /* Фізичний розмір пікселя (мікрометри) */
    int res_x;                /* Кількість пікселів по горизонталі */
    int res_y;                /* Кількість пікселів по вертикалі */
} SensorSpec;

/* Результати кутового поля зору FOV */
typedef struct {
    double hfov_deg;          /* Горизонтальний кут поля зору (градуси) */
    double vfov_deg;          /* Вертикальний кут поля зору (градуси) */
    double dfov_deg;          /* Діагональний кут поля зору (градуси) */
    double ifov_mrad;         /* Миттєве кутове поле зору одного пікселя (мілірадіани) */
    double diag_mm;           /* Діагональ світлочутливої матриці (мм) */
    double crop_factor;       /* Кроп-фактор відносно Full Frame (36x24 мм) */
} OpticalFovResult;

/* Результат розрахунку фокусної відстані для цільової сцени */
typedef struct {
    double required_f_mm;     /* Необхідна фокусна відстань об'єктива (мм) */
    double magnification;     /* Оптичне лінійне збільшення системи */
    double sensor_distance_mm;/* Фактична відстань від задньої головної площини до сенсора */
    bool is_macro;            /* Ознака макрорежиму (збільшення M > 0.1) */
} FocalLengthResult;

/* Результат пірометричного розрахунку плями візування */
typedef struct {
    double spot_diameter_mm;  /* Діаметр плями вимірювання на заданій відстані (мм) */
    double ds_ratio;          /* Оптичний показник візування D:S */
    double ifov_deg;          /* Повний кут конуса візування сенсора (градуси) */
} PyrometerSpotResult;

/* Статус виконання обчислень */
typedef enum {
    OPTIC_OK = 0,
    OPTIC_ERR_INVALID_PARAM = -1,
    OPTIC_ERR_ZERO_DIVISION = -2,
    OPTIC_ERR_DISTANCE_TOO_SHORT = -3
} OpticStatus;

/* Обчислення кутів FOV та роздільної здатності сенсора */
OpticStatus calc_sensor_fov(const SensorSpec* sensor, double focal_length_mm, 
                            double working_distance_mm, OpticalFovResult* out_res) {
    if (!sensor || !out_res || focal_length_mm <= 0.0 || sensor->width_mm <= 0.0 || sensor->height_mm <= 0.0) {
        return OPTIC_ERR_INVALID_PARAM;
    }

    double diag_mm = sqrt(sensor->width_mm * sensor->width_mm + sensor->height_mm * sensor->height_mm);
    const double full_frame_diag_mm = 43.266615; /* sqrt(36^2 + 24^2) */
    out_res->diag_mm = diag_mm;
    out_res->crop_factor = full_frame_diag_mm / diag_mm;

    /* Розрахунок ефективної відстані до площини зображення d_i */
    double d_i_mm = focal_length_mm;
    if (working_distance_mm > 0.0) {
        if (working_distance_mm <= focal_length_mm) {
            return OPTIC_ERR_DISTANCE_TOO_SHORT;
        }
        /* Формула тонкої лінзи: 1/d_i = 1/f - 1/d_o */
        d_i_mm = (focal_length_mm * working_distance_mm) / (working_distance_mm - focal_length_mm);
    }

    /* FOV = 2 * arctan(dimension / (2 * d_i)) */
    out_res->hfov_deg = RAD_TO_DEG(2.0 * atan(sensor->width_mm / (2.0 * d_i_mm)));
    out_res->vfov_deg = RAD_TO_DEG(2.0 * atan(sensor->height_mm / (2.0 * d_i_mm)));
    out_res->dfov_deg = RAD_TO_DEG(2.0 * atan(diag_mm / (2.0 * d_i_mm)));

    /* IFOV = pixel_pitch / focal_length (у мілірадіанах) */
    if (sensor->pixel_pitch_um > 0.0) {
        out_res->ifov_mrad = (sensor->pixel_pitch_um / 1000.0) / focal_length_mm * 1000.0;
    } else if (sensor->res_x > 0) {
        double pitch_calc_um = (sensor->width_mm / (double)sensor->res_x) * 1000.0;
        out_res->ifov_mrad = (pitch_calc_um / 1000.0) / focal_length_mm * 1000.0;
    } else {
        out_res->ifov_mrad = 0.0;
    }

    return OPTIC_OK;
}

/* Підбір фокусної відстані за шириною поля огляду W та дистанцією WD */
OpticStatus calc_focal_length_for_scene(double field_width_mm, double working_distance_mm,
                                        double sensor_width_mm, FocalLengthResult* out_res) {
    if (!out_res || field_width_mm <= 0.0 || working_distance_mm <= 0.0 || sensor_width_mm <= 0.0) {
        return OPTIC_ERR_INVALID_PARAM;
    }

    /* Оптичне лінійне збільшення M = w_sensor / W_field */
    double m = sensor_width_mm / field_width_mm;
    out_res->magnification = m;
    out_res->is_macro = (m >= 0.1);

    /* Необхідна фокусна відстань з урахуванням кінцевої дистанції: f = WD * M / (1 + M) */
    out_res->required_f_mm = working_distance_mm * m / (1.0 + m);
    out_res->sensor_distance_mm = out_res->required_f_mm * (1.0 + m);

    return OPTIC_OK;
}

/* Розрахунок пірометричної плями візування D:S */
OpticStatus calc_pyrometer_spot(double ds_ratio, double aperture_diam_mm,
                                double distance_mm, PyrometerSpotResult* out_res) {
    if (!out_res || ds_ratio <= 0.0 || distance_mm < 0.0) {
        return OPTIC_ERR_INVALID_PARAM;
    }

    out_res->ds_ratio = ds_ratio;
    /* Діаметр плями S = Aperture + Distance / (D:S) */
    out_res->spot_diameter_mm = aperture_diam_mm + (distance_mm / ds_ratio);
    
    /* Еквівалентний кут візування (градуси) */
    double half_angle_rad = atan(1.0 / (2.0 * ds_ratio));
    out_res->ifov_deg = RAD_TO_DEG(2.0 * half_angle_rad);

    return OPTIC_OK;
}
