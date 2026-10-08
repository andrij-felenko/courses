#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "pwm_driver.h"
#include "adc_current_sensor.h"
#include "towerpro_servo.h"

/**
 * @brief Обробник аварійної події заклинювання редуктора сервоприводу.
 */
static void on_servo_stall_detected(void *user_data, servo_model_t model, float current_rms_ma)
{
    (void)user_data;
    printf("\n[УВАГА / АВАРІЯ] Захист заклинювання спрацював!\n");
    printf("   Модель: %d, Виміряний RMS-струм: %.2f мА\n", (int)model, current_rms_ma);
    printf("   ШІМ-сигнал апаратно знято для збереження шестерень та обмоток двигуна.\n\n");
}

int main(void)
{
    printf("--- Система неблокуючого керування та струмового захисту Tower Pro ---\n\n");

    /* 1. Ініціалізація емуляції регістрів таймера та ШІМ-драйвера */
    TIM_TypeDef mock_timer = {0};
    pwm_driver_t pwm;
    uint32_t system_clock_hz = 16000000U; // 16 МГц

    if (pwm_driver_init(&pwm, &mock_timer, 1U, system_clock_hz) != 0) {
        printf("Помилка ініціалізації ШІМ-драйвера!\n");
        return -1;
    }
    printf("ШІМ-драйвер успішно ініціалізовано на Каналі 1 (Частота 50 Гц).\n");

    /* 2. Ініціалізація сенсора струму (Шунт = 0.1 Ом, Підсилення = 10.0, Ref = 3.3 В) */
    adc_sensor_t adc;
    if (adc_sensor_init(&adc, 0.1f, 10.0f, 3.3f) != 0) {
        printf("Помилка ініціалізації сенсора струму!\n");
        return -1;
    }
    printf("Сенсор струму АЦП ініціалізовано (Шунт: 0.1 Ом, Кпідс: 10.0).\n");

    /* 3. Конфігурація та ініціалізація сервоприводу MG90S з металевим редуктором */
    servo_config_t config = {
        .model = SERVO_MODEL_MG90S,
        .pwm = &pwm,
        .adc = &adc,
        .stall_cb = on_servo_stall_detected,
        .user_data = NULL
    };

    towerpro_servo_t servo;
    if (towerpro_servo_init(&servo, &config) != 0) {
        printf("Помилка ініціалізації сервоприводу Tower Pro MG90S!\n");
        return -1;
    }

    printf("Сервопривод: %s\n", servo.profile.model_name);
    printf("Поріг заклинювання: %.1f мА, Час таймауту: %u мс\n\n",
           servo.profile.stall_current_limit_ma, servo.profile.stall_timeout_ms);

    /* 4. Симуляція неблокуючого робочого циклу */
    uint32_t simulated_time_ms = 0U;

    printf("--- Етап 1: Нормальне позиціонування (Струм ~150 мА) ---\n");
    float angles_to_test[] = {0.0f, 45.0f, 90.0f, 135.0f, 180.0f};
    size_t num_angles = sizeof(angles_to_test) / sizeof(angles_to_test[0]);

    /* Сире значення ADC для ~150 мА: raw = 150 / 0.80586 ≈ 186 */
    uint16_t normal_raw_adc = 186U;

    for (size_t i = 0U; i < num_angles; ++i) {
        towerpro_servo_set_angle(&servo, angles_to_test[i]);
        printf("Крок %zu: Встановлено кут %.1f deg -> Тривалість ШІМ: %u us\n",
               i + 1, angles_to_test[i], pwm_driver_get_pulse_us(&pwm));

        /* Симуляція кількох вибірок АЦП у часі */
        for (int sample = 0; sample < 10; ++sample) {
            simulated_time_ms += 20U; // Кожні 20 мс
            towerpro_servo_process(&servo, normal_raw_adc, simulated_time_ms);
        }

        printf("   Поточний RMS-струм: %.2f мА, Стан: %s\n",
               towerpro_servo_get_current_rms(&servo),
               towerpro_servo_get_status(&servo) == SERVO_STATUS_OK ? "ОК" : "АВАРІЯ");
    }

    printf("\n--- Етап 2: Імітація механічного заклинювання (Струм ~850 мА) ---\n");
    /* Сире значення ADC для ~850 мА: raw = 850 / 0.80586 ≈ 1055 */
    uint16_t stall_raw_adc = 1055U; // ~850 mA

    /* Спробуємо повернути на 0 градусів */
    towerpro_servo_set_angle(&servo, 0.0f);

    /* Подаємо вибірки високого струму у часі (понад 500 мс) */
    for (int step = 0; step < 30; ++step) {
        simulated_time_ms += 20U;
        int res = towerpro_servo_process(&servo, stall_raw_adc, simulated_time_ms);
        if (res != 0) {
            printf("[%3u мс] Цикл зафіксував вимкнення ШІМ! Активність ШІМ: %s\n",
                   simulated_time_ms, pwm_driver_is_enabled(&pwm) ? "ТАК" : "НІ");
            break;
        }
    }

    printf("\n--- Етап 3: Відновлення роботи після усунення заклинювання ---\n");
    printf("Скидання прапорців аварії...\n");
    towerpro_servo_reset_fault(&servo);

    printf("Поточна активність ШІМ після скидання: %s\n", pwm_driver_is_enabled(&pwm) ? "ТАК" : "НІ");
    /* Повертаємо нормальне навантаження */
    for (int sample = 0; sample < 10; ++sample) {
        simulated_time_ms += 20U;
        towerpro_servo_process(&servo, 186U, simulated_time_ms); // ~150 mA
    }
    printf("Після відновлення RMS-струм: %.2f мА, Стан: %s\n",
           towerpro_servo_get_current_rms(&servo),
           towerpro_servo_get_status(&servo) == SERVO_STATUS_OK ? "ОК" : "АВАРІЯ");

    printf("\nДемонстрацію успішно завершено.\n");
    return 0;
}
