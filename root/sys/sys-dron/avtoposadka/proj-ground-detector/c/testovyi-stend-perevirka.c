#include <stdio.h>

void run_ground_detector_simulation(void) {
    ground_detector_params_t params = {
        .max_vz_abs = 0.15f,
        .max_gyro_abs = 0.20f,
        .hover_thr_ratio = 0.30f,
        .conf_threshold_land = 0.85f,
        .conf_threshold_drop = 0.20f,
        .time_rise_sec = 0.50f,
        .time_decay_sec = 0.25f,
        .disarm_ramp_time_sec = 0.40f
    };

    ground_detector_module_t detector;
    ground_detector_module_init(&detector, &params);

    float hover_thrust = 0.45f;
    float dt = 0.02f; // 50 Гц

    // Сценарій: Спуск -> Удар -> Підстрибування на 80 мс -> Повна зупинка
    for (int step = 0; step < 100; step++) {
        float time_sec = step * dt;
        float vz, gyro, accel_z, thrust;

        if (time_sec < 0.5f) {
            // Фаза 1: Керований спуск
            vz = -0.55f;
            gyro = 0.04f;
            accel_z = -9.81f;
            thrust = 0.40f;
        } else if (time_sec >= 0.5f && time_sec < 0.54f) {
            // Фаза 2: Перший удар об землю
            vz = -0.05f;
            gyro = 0.08f;
            accel_z = -18.5f; // Ударний сплеск
            thrust = 0.12f;
        } else if (time_sec >= 0.54f && time_sec < 0.62f) {
            // Фаза 3: Пружний відскок шасі у повітря (80 мс)
            vz = +0.25f;      // Дрон рухається вгору!
            gyro = 0.15f;
            accel_z = -8.5f;
            thrust = 0.10f;
        } else {
            // Фаза 4: Остаточна опора на твердий ґрунт
            vz = 0.01f;
            gyro = 0.02f;
            accel_z = -9.81f;
            thrust = 0.08f;
        }

        ground_detector_module_update(&detector, vz, gyro, accel_z, thrust, hover_thrust, dt);

        if (step % 10 == 0 || detector.disarm_requested) {
            printf("T=%.2fs | State=%d | Conf=%.2f | ThrScale=%.2f | FreezeI=%d | Disarm=%d\n",
                   time_sec, detector.state, detector.confidence,
                   detector.throttle_output_scale, detector.freeze_i_terms,
                   detector.disarm_requested);
        }

        if (detector.state == GROUND_STATE_DISARMED) {
            printf(">>> Успішне розброєння на часі T=%.2fs <<<\n", time_sec);
            break;
        }
    }
}
