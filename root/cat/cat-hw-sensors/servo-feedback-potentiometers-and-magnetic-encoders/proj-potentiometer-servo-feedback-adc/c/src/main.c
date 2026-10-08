#include <stdio.h>
#include <stdlib.h>
#include "adc_hal.h"
#include "servo_sensor.h"

#define MOVING_AVERAGE_WINDOW  8
#define EMA_ALPHA              0.25f

int main(void) {
    // Фіксація випадкового зерна для відтворюваності симуляції шуму
    srand(42);

    printf("=========================================================\n");
    printf("  СЕРВОПРИВОД: ДАТЧИКИ КУТА (ПОТЕНЦІОМЕТРИ/ЕНКОДЕРИ)\n");
    printf("=========================================================\n\n");

    // 1. Ініціалізація апаратного абстракційного рівня (HAL АЦП)
    adc_handle_t adc;
    if (!adc_hal_init(&adc, 1, ADC_RESOLUTION_12BIT, 3.3f)) {
        printf("[ПОМИЛКА] Не вдалося ініціалізувати АЦП!\n");
        return 1;
    }
    printf("[АЦП HAL] Ініціалізовано: Канал 1, 12-біт (0..4095), Vref = 3.30V\n");

    // 2. Виділення пам'яті для кільцевого буфера та ініціалізація серводетчика
    float rb_storage[MOVING_AVERAGE_WINDOW];
    servo_sensor_t sensor;
    servo_sensor_init(&sensor, &adc, rb_storage, MOVING_AVERAGE_WINDOW, EMA_ALPHA);
    printf("[ДАТЧИК] Створено кільцевий буфер N=%d, EMA alpha=%.2f\n", MOVING_AVERAGE_WINDOW, (double)EMA_ALPHA);

    // 3. Процедура дворівневого калібрування (Zero/Span Calibration)
    // Допустимо: Нульове положення (0.0°) -> напруга 0.20V (код ~248)
    //            Максимальне положення (180.0°) -> напруга 3.10V (код ~3847)
    //            Запас мертвих зон (deadband margin) = 30 кодувань АЦП
    uint16_t cal_zero_raw = 248;   // 0.20V на потенціометрі відповідає механічному упору 0°
    uint16_t cal_span_raw = 3847;  // 3.10V на потенціометрі відповідає механічному упору 180°
    float angle_zero = 0.0f;
    float angle_span = 180.0f;
    uint16_t deadband_margin = 30;

    if (!servo_sensor_calibrate(&sensor, cal_zero_raw, angle_zero, cal_span_raw, angle_span, deadband_margin)) {
        printf("[ПОМИЛКА] Калібрування не пройшло перевірку!\n");
        return 1;
    }
    printf("[КАЛІБРУВАННЯ] Успішно проведено:\n");
    printf("  Zero Point: ADC %u -> %.1f deg\n", cal_zero_raw, (double)angle_zero);
    printf("  Span Point: ADC %u -> %.1f deg\n", cal_span_raw, (double)angle_span);
    printf("  Deadband Low Threshold : ADC %u\n", sensor.calib.adc_deadband_low);
    printf("  Deadband High Threshold: ADC %u\n\n", sensor.calib.adc_deadband_high);

    // 4. Симуляція вимірювання фізичного кута повороту в кількох контрольних точках
    // Зверніть увагу: додається високочастотний електричний шум аналогової лінії (±0.04V)
    float test_target_angles[] = {0.0f, 0.0f, 45.0f, 90.0f, 135.0f, 180.0f, 180.0f};
    size_t num_tests = sizeof(test_target_angles) / sizeof(test_target_angles[0]);

    printf("--- ПОЧАТОК ФІЛЬТРАЦІЇ ТА ВИМІРЮВАННЯ В РЕАЛЬНОМУ ЧАСІ ---\n");
    printf("%-5s | %-12s | %-10s | %-12s | %-12s | %-10s\n", 
           "Крок", "Ціль (град)", "Сира напр.", "Сирий АЦП", "Фільтр. АЦП", "Кут (град)");
    printf("-----------------------------------------------------------------------------\n");

    int step = 1;
    for (size_t t = 0; t < num_tests; t++) {
        float target_deg = test_target_angles[t];
        
        // Розрахунок ідеальної напруги для цільового кута
        float target_norm = (target_deg - angle_zero) / (angle_span - angle_zero);
        float ideal_volts = 0.20f + target_norm * (3.10f - 0.20f);
        
        // Встановлення напруги зі зваженим шумом ±0.04V для перевірки роботоздатності фільтра
        adc_hal_set_simulated_input(&adc, ideal_volts, 0.04f);

        // Виконання вибірок у кожній точці для демонстрації згладжування ковзним середнім та EMA
        for (int sample = 0; sample < 5; sample++) {
            float calculated_angle = servo_sensor_read_angle(&sensor);
            float raw_volts = adc_hal_raw_to_volts(&adc, sensor.last_raw_adc);

            printf("#%-4d | %-12.1f | %-8.3f V | %-12u | %-12.2f | %-10.2f\n",
                   step++,
                   (double)target_deg,
                   (double)raw_volts,
                   sensor.last_raw_adc,
                   (double)sensor.last_filtered_adc,
                   (double)calculated_angle);
        }
    }

    printf("-----------------------------------------------------------------------------\n");
    printf("[УСПІХ] Симуляцію зчитування та двокаскадної фільтрації завершено.\n");

    return 0;
}
