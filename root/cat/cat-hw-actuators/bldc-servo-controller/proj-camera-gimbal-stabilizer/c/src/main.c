#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#include "pwm_driver.h"
#include "imu_spi.h"
#include "foc_math.h"
#include "notch_filter.h"

/**
 * @file main.c
 * @brief Головний модуль керування безколекторним сервоконтролером.
 */

int main(void) {
    printf("=== Запуск прошивки інтегрального BLDC сервоконтролера ===\n");

    /* 1. Ініціалізація периферифійного модуля трифазного комплементарного ШІМ */
    pwm_config_t pwm_cfg = {
        .timer_clock_hz = 168000000U, /* 168 МГц системна тактова частота */
        .pwm_freq_hz    = 20000U,     /* 20 кГц частота ШІМ */
        .dead_time_ns   = 1200U       /* 1.2 мкс дед-тайм для захисту інвертора */
    };

    if (pwm_driver_init(&pwm_cfg) != 0) {
        printf("[ПОМИЛКА] Збій ініціалізації ШІМ-драйвера!\n");
        return -1;
    }
    printf("[OK] ШІМ-таймер сконфігуровано: Center-Aligned Mode 1, ARR = %u відліків, DTG = 0x%02X\n",
           pwm_driver_get_period_ticks(),
           pwm_calculate_dtg(pwm_cfg.timer_clock_hz, pwm_cfg.dead_time_ns));

    /* 2. Ініціалізація SPI-драйвера та інерціального модуля IMU */
    if (imu_spi_init() != 0) {
        printf("[ПОМИЛКА] IMU не відповідає по шині SPI!\n");
        return -1;
    }
    printf("[OK] IMU сенсор успішно ініціалізовано по шині SPI (Mode 3, 8 Мбіт/с)\n");

    /* 3. Ініціалізація двоосьового цифрового Notch-фільтра для приглушення механічного резонансу
     * Налаштовуємо режекторний фільтр на 400 Гц з добротністю Q = 5.0 при частоті дискретизації 20 кГц.
     */
    notch_filter_2axis_t imu_notch;
    notch_filter_2axis_init(&imu_notch, 400.0f, 5.0f, 20000.0f);
    printf("[OK] Двоосьовий Notch-фільтр настроєно: f0 = 400 Гц, Q = 5.0, fs = 20000 Гц\n");

    /* Вмикаємо силові виходи інвертора (MOE bit) */
    pwm_driver_enable_outputs(true);
    printf("[OK] Силові виходи ШІМ-інвертора активовано (MOE = 1)\n\n");

    /* 4. Високочастотний цикл керування FOC (Field-Oriented Control) */
    printf("--- Старт циклу керування (50 ітерацій) ---\n");

    float rotor_theta = 0.0f;       /* Кут ротора в радіанах */
    float target_iq = 2.5f;         /* Заданий струм моменту (А) */
    float target_id = 0.0f;         /* Заданий струм намагнічування (А) */
    const float v_dc = 24.0f;       /* Напруга шини живлення DC (В) */
    const float dt = 1.0f / 20000.0f; /* Період дискретизації (50 мкс) */

    for (int step = 0; step < 50; step++) {
        /* А. Опитування IMU через SPI */
        imu_data_t imu_val;
        if (imu_read_data(&imu_val) != 0) {
            printf("[ПОМИЛКА] Збій зчитування IMU на кроці %d\n", step);
            break;
        }

        /* Б. Додавання штучної механічної вібрації 400 Гц для демонстрації роботи режекторного фільтра */
        float resonance_noise = 15.0f * sinf(2.0f * M_PI * 400.0f * (float)step * dt);
        float raw_gyro_x = imu_val.gyro_dps[0] + resonance_noise;
        float raw_gyro_y = imu_val.gyro_dps[1] + resonance_noise;

        /* В. Двоосьова Notch-фільтрація сигналів гіроскопа */
        float filtered_gyro_x = 0.0f;
        float filtered_gyro_y = 0.0f;
        notch_filter_2axis_process(&imu_notch, raw_gyro_x, raw_gyro_y, &filtered_gyro_x, &filtered_gyro_y);

        /* Г. Оновлення кута ротора */
        rotor_theta += 100.0f * dt; /* Симуляція обертання ротора 100 рад/с */
        rotor_theta = foc_normalize_angle(rotor_theta);

        /* Д. Симуляція виміряних фазних струмів статора i_a, i_b, i_c */
        float i_a = 2.5f * sinf(rotor_theta);
        float i_b = 2.5f * sinf(rotor_theta - (2.0f * M_PI / 3.0f));
        float i_c = 2.5f * sinf(rotor_theta + (2.0f * M_PI / 3.0f));

        /* Е. Пряме перетворення Кларка (i_a, i_b, i_c -> i_alpha, i_beta) */
        foc_alphabeta_t i_ab;
        foc_clarke_transform(i_a, i_b, i_c, &i_ab);

        /* Ж. Пряме перетворення Парка (i_alpha, i_beta -> i_d, i_q) */
        foc_dq_t i_dq;
        foc_park_transform(&i_ab, rotor_theta, &i_dq);

        /* З. Простий регулятор струму (PI-регулятори) */
        float error_d = target_id - i_dq.d;
        float error_q = target_iq - i_dq.q;
        float v_d = error_d * 2.0f;
        float v_q = error_q * 2.0f + 8.0f; /* Опорна напруга проти-ЕРС */

        /* И. Зворотне перетворення Парка (v_d, v_q -> v_alpha, v_beta) */
        foc_dq_t v_dq = { .d = v_d, .q = v_q };
        foc_alphabeta_t v_ab;
        foc_inv_park_transform(&v_dq, rotor_theta, &v_ab);

        /* К. Просторове векторне ШІМ-перетворення (SVPWM) */
        float duty_a = 0.0f, duty_b = 0.0f, duty_c = 0.0f;
        foc_svpwm(v_ab.alpha, v_ab.beta, v_dc, &duty_a, &duty_b, &duty_c);

        /* Л. Швидке оновлення регістрів таймера ШІМ */
        pwm_driver_set_duty_cycles(duty_a, duty_b, duty_c);

        /* Виведення телеметрії кожні 10 кроків */
        if (step % 10 == 0) {
            printf("Крок %02d | Гіро X Вхід: %6.1f, Фільтр: %6.1f | Id: %5.2f A, Iq: %5.2f A | Duty A/B/C: %.2f / %.2f / %.2f\n",
                   step, raw_gyro_x, filtered_gyro_x, i_dq.d, i_dq.q, duty_a, duty_b, duty_c);
        }
    }

    /* Безпечне вимкнення інвертора */
    pwm_driver_enable_outputs(false);
    printf("\n[OK] Цикл керування завершено успішно. Інвертор переведено в безпечний стан Hi-Z.\n");

    return 0;
}
