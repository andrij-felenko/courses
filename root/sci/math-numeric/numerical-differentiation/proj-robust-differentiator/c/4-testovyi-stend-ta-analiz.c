#include <stdio.h>
#include <stdlib.h>
#include <math.h>

void run_differentiator_benchmark(void) {
    TrackingDifferentiator track;
    track_diff_init(&track, 0.45f, 0.15f, 0.02f, 5000.0f);

    TustinDifferentiator2nd tustin;
    tustin2_init(&tustin, 20.0f);

    const float dt_nominal = 0.001f; /* 1 кГц */
    const float freq = 2.0f;          /* 2 Гц рух */
    float prev_meas = 0.0f;
    float peak_naive_err = 0.0f;
    float peak_tustin_err = 0.0f;
    float peak_track_err = 0.0f;

    for (int step = 0; step < 2000; ++step) {
        float t = step * dt_nominal;
        float true_pos = sinf(2.0f * PI_F * freq * t);
        float true_vel = 2.0f * PI_F * freq * cosf(2.0f * PI_F * freq * t);

        /* Моделювання квантування енкодера: 4096 поділок на діапазон [-1, 1] */
        float quant_step = 2.0f / 4096.0f;
        float meas_pos = roundf(true_pos / quant_step) * quant_step;

        /* Моделювання часового джиттера таймера ±2% */
        float jitter = ((float)rand() / (float)RAND_MAX - 0.5f) * 0.04f * dt_nominal;
        float dt = dt_nominal + jitter;

        /* 1. Наївна зворотна різниця */
        float naive_vel = (step == 0) ? 0.0f : (meas_pos - prev_meas) / dt;
        prev_meas = meas_pos;

        /* 2. Фільтр Тастіна */
        float tustin_vel = tustin2_update(&tustin, meas_pos, dt);

        /* 3. Спостерігач Tracking */
        track_diff_update(&track, meas_pos, dt);
        float track_vel = track.vel;

        if (step > 100) { /* пропуск перехідного процесу */
            float err_naive = fabsf(naive_vel - true_vel);
            float err_tustin = fabsf(tustin_vel - true_vel);
            float err_track = fabsf(track_vel - true_vel);

            if (err_naive > peak_naive_err)   peak_naive_err = err_naive;
            if (err_tustin > peak_tustin_err) peak_tustin_err = err_tustin;
            if (err_track > peak_track_err)   peak_track_err = err_track;
        }
    }

    printf("=== Результати тестування чисельного диференціювання ===\n");
    printf("Наївна різниця (Δx/Δt):  пікова похибка = %.2f рад/с\n", peak_naive_err);
    printf("Фільтр Тастіна (20 Гц):   пікова похибка = %.2f рад/с\n", peak_tustin_err);
    printf("Спостерігач Alpha-Beta-Gamma: пікова похибка = %.2f рад/с\n", peak_track_err);
}
