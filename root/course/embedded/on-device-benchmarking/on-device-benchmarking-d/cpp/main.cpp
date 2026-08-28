#include <chrono>
#include <vector>
#include <algorithm>
#include <cstdio>

// Монотонний годинник: не стрибне назад, навіть якщо систему підкрутять.
using clk = std::chrono::steady_clock;

static double ms_since(clk::time_point t0) {
    auto dt = clk::now() - t0;
    return std::chrono::duration<double, std::milli>(dt).count();
}

void benchmark(Model& net, const Frame& frame) {
    // 1) ПРОГРІВ — результат викидаємо: розганяємо чіп, гріємо кеш.
    for (int i = 0; i < 20; ++i) {
        net.infer(frame);
        net.synchronize();      // дочекатися прискорювача (інакше міряємо чергу!)
    }

    // 2) ВИМІР — збираємо ВСІ часи, а не лише суму (потрібні для перцентилів).
    const int N = 300;          // багато прогонів: хвіст видно лише на масі
    std::vector<double> times;
    times.reserve(N);
    for (int i = 0; i < N; ++i) {
        auto t0 = clk::now();
        net.infer(frame);
        net.synchronize();      // БАР'ЄР: тепер таймер ловить усе обчислення
        times.push_back(ms_since(t0));
    }

    // 3) СТАТИСТИКА — середнє бреше, тож рахуємо й перцентилі.
    std::sort(times.begin(), times.end());
    double sum = 0;
    for (double t : times) sum += t;
    double mean = sum / N;
    double p50  = times[N * 50 / 100];
    double p99  = times[N * 99 / 100];
    double worst = times.back();

    printf("середнє %.1f | p50 %.1f | p99 %.1f | гірший %.1f мс  (%.1f FPS за p99)\n",
           mean, p50, p99, worst, 1000.0 / p99);
}
