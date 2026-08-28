#include <cstdint>
#include <chrono>

// Один прохід моделі та її вхід/вихід (реалізація залежить від платформи).
void model_infer(const float *input, float *output);
extern float g_input[INPUT_SIZE];
extern float g_output[OUTPUT_SIZE];

// Час у мікросекундах від монотонного годинника (не стрибає при зміні системного).
static uint64_t now_us() {
    using namespace std::chrono;
    return duration_cast<microseconds>(steady_clock::now().time_since_epoch()).count();
}

void measure_latency() {
    constexpr int N = 200;

    // 1) Прогрів: перші прогони завжди повільніші (кеш холодний,
    //    залізо ще не «розкрутилось»). Їх у статистику НЕ беремо.
    for (int i = 0; i < 20; ++i)
        model_infer(g_input, g_output);

    // 2) Заміри: кожен прохід — окремо, щоб бачити РОЗКИД, не лише суму.
    uint64_t worst = 0;
    uint64_t sum   = 0;
    for (int i = 0; i < N; ++i) {
        uint64_t t0 = now_us();
        model_infer(g_input, g_output);
        uint64_t dt = now_us() - t0;      // латентність цього кадру

        sum += dt;
        worst = std::max(worst, dt);      // стежимо за ХВОСТОМ
    }

    uint64_t mean = sum / N;
    // mean  — типова латентність; worst — найгірший кадр (наближення до p99).
    // Для бюджету 30 к/с придатність вирішує саме worst, а не mean:
    //   worst < 33000 мкс  →  укладаємось навіть у найгіршому кадрі.
    report(mean, worst);
}
