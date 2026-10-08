#include <stdint.h>
#include <stdbool.h>

#define CALIB_POINTS_COUNT 5

typedef struct {
    uint16_t adc_code;
    float angle_deg;
} calib_point_t;

typedef struct {
    uint16_t adc_min_valid;
    uint16_t adc_max_valid;
    calib_point_t lut[CALIB_POINTS_COUNT];
} pot_sensor_t;

// Ініціалізація структури калібрування для потенціометра 300 градусів
static const pot_sensor_t g_pot_config = {
    .adc_min_valid = 150,   // Нижня мертва зона (нижче 150 - край доріжки)
    .adc_max_valid = 3950,  // Верхня мертва зона (вище 3950 - край доріжки)
    .lut = {
        {150,   0.0f},
        {1100, 72.5f},      // Враховано нелінійний прогин від навантаження
        {2050, 150.0f},
        {3000, 227.5f},
        {3950, 300.0f}
    }
};

/**
 * @brief Перетворення відліку АЦП у кут із компенсацією мертвих зон та нелінійності
 * @param sensor Вказівник на налаштування сенсора
 * @param raw_adc Сирий відлік АЦП
 * @param out_angle_deg Вказівник для збереження результату кута
 * @return true якщо відлік коректний, false якщо виявлено обрив або коротке замикання
 */
bool pot_process_adc_to_angle(const pot_sensor_t *sensor, uint16_t raw_adc, float *out_angle_deg) {
    // Перевірка на обрив лінії або коротке замикання (значний вихід за межі)
    if (raw_adc < (sensor->adc_min_valid / 2) || raw_adc > (sensor->adc_max_valid + 100)) {
        return false;
    }

    // 1. Клемпінг (обмеження) мертвих зон
    uint16_t clamped_adc = raw_adc;
    if (clamped_adc < sensor->adc_min_valid) {
        clamped_adc = sensor->adc_min_valid;
    } else if (clamped_adc > sensor->adc_max_valid) {
        clamped_adc = sensor->adc_max_valid;
    }

    // 2. Пошук інтервалу в таблиці калібрування
    for (int i = 0; i < CALIB_POINTS_COUNT - 1; i++) {
        uint16_t d_k = sensor->lut[i].adc_code;
        uint16_t d_k1 = sensor->lut[i + 1].adc_code;

        if (clamped_adc >= d_k && clamped_adc <= d_k1) {
            float theta_k = sensor->lut[i].angle_deg;
            float theta_k1 = sensor->lut[i + 1].angle_deg;

            // 3. Шматочно-лінійна інтерполяція
            float factor = (float)(clamped_adc - d_k) / (float)(d_k1 - d_k);
            *out_angle_deg = theta_k + factor * (theta_k1 - theta_k);
            return true;
        }
    }

    *out_angle_deg = sensor->lut[CALIB_POINTS_COUNT - 1].angle_deg;
    return true;
}
