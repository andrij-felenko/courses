/* c */
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

typedef struct {
    float heading_deg;     /* Справжній азимут (0..360°) */
    float inclination_deg; /* Кут магнітного нахилу (-90..+90°) */
    float pitch_deg;       /* Тангаж пристрою (-90..+90°) */
    float roll_deg;        /* Крен пристрою (-180..+180°) */
    float total_field_uT;  /* Повний модуль магнітного поля */
    bool  is_valid;        /* Прапорець коректності даних */
} orientation_result_t;

/**
 * @brief Обчислення скомпенсованого курсу та кута нахилу.
 * @param accel Дані акселерометра [м/с²] або [g]
 * @param mag Дані магнітометра [мкТл] або [Гаус]
 * @param declination_rad Месцеве магнітне схилення в радіанах
 */
orientation_result_t calculate_tilt_compensated_heading(
    const vector3f_t accel,
    const vector3f_t mag,
    float declination_rad
) {
    orientation_result_t res = {0};

    /* Перевірка на нульовий модуль прискорення */
    float accel_norm_sq = accel.x * accel.x + accel.y * accel.y + accel.z * accel.z;
    if (accel_norm_sq < 1e-4f) {
        res.is_valid = false;
        return res;
    }

    /* 1. Обчислення кутів тангажу та крену */
    float roll  = atan2f(accel.y, accel.z);
    float pitch = atan2f(-accel.x, sqrtf(accel.y * accel.y + accel.z * accel.z));

    float cos_roll  = cosf(roll);
    float sin_roll  = sinf(roll);
    float cos_pitch = cosf(pitch);
    float sin_pitch = sinf(pitch);

    /* 2. Проєкція магнітометра на горизонтальну площину */
    float b_xh = mag.x * cos_pitch + mag.y * sin_roll * sin_pitch + mag.z * cos_roll * sin_pitch;
    float b_yh = mag.y * cos_roll - mag.z * sin_roll;
    float b_zh = -mag.x * sin_pitch + mag.y * sin_roll * cos_pitch + mag.z * cos_roll * cos_pitch;

    /* 3. Магнітний курс (азимут) */
    float heading_rad = atan2f(-b_yh, b_xh) + declination_rad;

    /* Нормалізація в діапазон [0, 2π) */
    while (heading_rad < 0.0f) heading_rad += 2.0f * M_PI;
    while (heading_rad >= 2.0f * M_PI) heading_rad -= 2.0f * M_PI;

    /* 4. Повний модуль поля та кут нахилу */
    float b_total = sqrtf(mag.x * mag.x + mag.y * mag.y + mag.z * mag.z);
    float inclination_rad = 0.0f;
    if (b_total > 1e-4f) {
        inclination_rad = asinf(b_zh / b_total);
    }

    /* Запис результатів у градусах */
    res.heading_deg     = heading_rad * (180.0f / M_PI);
    res.inclination_deg = inclination_rad * (180.0f / M_PI);
    res.pitch_deg       = pitch * (180.0f / M_PI);
    res.roll_deg        = roll * (180.0f / M_PI);
    res.total_field_uT  = b_total;
    res.is_valid        = true;

    return res;
}
