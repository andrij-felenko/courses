#include <cmath>
#include <iostream>
#include <numbers>
#include <random>

void run_differentiator_benchmark_cpp() {
    TrackingDifferentiator track({.alpha = 0.45f, .beta = 0.15f, .gamma = 0.02f, .max_acceleration = 5000.0f});
    TustinDifferentiator2nd tustin(20.0f);

    constexpr float dt_nominal = 0.001f;
    constexpr float freq = 2.0f;
    constexpr float pi = std::numbers::pi_v<float>;

    float prev_meas = 0.0f;
    float peak_naive_err = 0.0f;
    float peak_tustin_err = 0.0f;
    float peak_track_err = 0.0f;

    std::mt19937 gen(42);
    std::uniform_real_distribution<float> jitter_dist(-0.02f * dt_nominal, 0.02f * dt_nominal);

    for (int step = 0; step < 2000; ++step) {
        const float t = static_cast<float>(step) * dt_nominal;
        const float true_pos = std::sin(2.0f * pi * freq * t);
        const float true_vel = 2.0f * pi * freq * std::cos(2.0f * pi * freq * t);

        constexpr float quant_step = 2.0f / 4096.0f;
        const float meas_pos = std::round(true_pos / quant_step) * quant_step;
        const float dt = dt_nominal + jitter_dist(gen);

        const float naive_vel = (step == 0) ? 0.0f : (meas_pos - prev_meas) / dt;
        prev_meas = meas_pos;

        const float tustin_vel = tustin.update(meas_pos, dt);

        track.update(meas_pos, dt);
        const float track_vel = track.velocity();

        if (step > 100) {
            peak_naive_err = std::max(peak_naive_err, std::abs(naive_vel - true_vel));
            peak_tustin_err = std::max(peak_tustin_err, std::abs(tustin_vel - true_vel));
            peak_track_err = std::max(peak_track_err, std::abs(track_vel - true_vel));
        }
    }

    std::cout << "=== Результати тестування чисельного диференціювання (C++20) ===\n";
    std::cout << "Наївна різниця (Δx/Δt):  пікова похибка = " << peak_naive_err << " рад/с\n";
    std::cout << "Фільтр Тастіна (20 Гц):   пікова похибка = " << peak_tustin_err << " рад/с\n";
    std::cout << "Спостерігач Alpha-Beta-Gamma: пікова похибка = " << peak_track_err << " рад/с\n";
}
