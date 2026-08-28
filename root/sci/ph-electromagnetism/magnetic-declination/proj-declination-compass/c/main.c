/* c */
#include <math.h>
#include <stdbool.h>

#define M_PI_F 3.14159265358979323846f
#define MIN_H_FIELD_NT 2000.0f  /* Поріг надійності горизонтального поля (нТл) */

typedef struct {
    float bx_nt;   /* Виміряне поле вздовж осі X (нТл або мкТл) */
    float by_nt;   /* Виміряне поле вздовж осі Y (нТл або мкТл) */
    float bz_nt;   /* Виміряне поле вздовж осі Z (нТл або мкТл) */
    float roll_rad;   /* Кут крену апарата (радіани) */
    float pitch_rad;  /* Кут тангажу апарата (радіани) */
    float declination_deg; /* Місцеве магнітне схилення (градуси) */
} compass_input_t;

typedef struct {
    float heading_mag_deg;  /* Курс відносно магнітної півночі [0..360°) */
    float heading_true_deg; /* Істинний курс відносно географічної півночі [0..360°) */
    float h_intensity_nt;   /* Модуль горизонтального поля (нТл) */
    bool  is_valid;         /* Прапорець надійності (false поблизу полярних широт) */
} compass_output_t;

/* Нормалізація кута у діапазон [0.0 .. 360.0) градусів */
static float normalize_360(float angle_deg) {
    float normalized = fmodf(angle_deg, 360.0f);
    if (normalized < 0.0f) {
        normalized += 360.0f;
    }
    return normalized;
}

/* Обчислення істинного курсу за вимірюваннями магнітометра та кутів орієнтації */
bool compass_calculate_heading(const compass_input_t* input, compass_output_t* output) {
    if (!input || !output) {
        return false;
    }

    float cos_roll = cosf(input->roll_rad);
    float sin_roll = sinf(input->roll_rad);
    float cos_pitch = cosf(input->pitch_rad);
    float sin_pitch = sinf(input->pitch_rad);

    /* Проєкція 3D-вектора на горизонтальну площину (компенсація крену й тангажу) */
    float hx = input->bx_nt * cos_pitch +
               input->by_nt * sin_roll * sin_pitch +
               input->bz_nt * cos_roll * sin_pitch;

    float hy = input->by_nt * cos_roll -
               input->bz_nt * sin_roll;

    /* Обчислення модуля горизонтальної індукції H */
    output->h_intensity_nt = sqrtf(hx * hx + hy * hy);

    /* Перевірка сингулярності поблизу магнітних полюсів */
    if (output->h_intensity_nt < MIN_H_FIELD_NT) {
        output->heading_mag_deg = 0.0f;
        output->heading_true_deg = 0.0f;
        output->is_valid = false;
        return false;
    }

    /* Авіаційна конвенція курсу: 0° = Північ, 90° = Схід (через atan2(-Hy, Hx)) */
    float heading_mag_rad = atan2f(-hy, hx);
    output->heading_mag_deg = normalize_360(heading_mag_rad * (180.0f / M_PI_F));

    /* Внесення поправки магнітного схилення */
    output->heading_true_deg = normalize_360(output->heading_mag_deg + input->declination_deg);
    output->is_valid = true;

    return true;
}
