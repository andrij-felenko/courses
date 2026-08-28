#include <stdint.h>

// Повертає час у мікросекундах (реалізація залежить від платформи).
uint64_t now_us(void);

extern void model_infer(const float *input, float *output);  // один прохід
extern float g_input[INPUT_SIZE];
extern float g_output[OUTPUT_SIZE];

void measure_latency(void) {
    const int N = 200;

    // 1) Прогрів: перші прогони завжди повільніші (кеш холодний,
    //    залізо ще не «розкрутилось»). Їх у статистику НЕ беремо.
    for (int i = 0; i < 20; i++)
        model_infer(g_input, g_output);

    // 2) Заміри: кожен прохід — окремо, щоб бачити РОЗКИД, не лише суму.
    uint64_t worst = 0;
    uint64_t sum   = 0;
    for (int i = 0; i < N; i++) {
        uint64_t t0 = now_us();
        model_infer(g_input, g_output);
        uint64_t dt = now_us() - t0;      // латентність цього кадру

        sum += dt;
        if (dt > worst) worst = dt;       // стежимо за ХВОСТОМ
    }

    uint64_t mean = sum / N;
    // mean  — типова латентність; worst — найгірший кадр (наближення до p99).
    // Для бюджету 30 к/с придатність вирішує саме worst, а не mean:
    //   worst < 33000 мкс  →  укладаємось навіть у найгіршому кадрі.
    report(mean, worst);
}
