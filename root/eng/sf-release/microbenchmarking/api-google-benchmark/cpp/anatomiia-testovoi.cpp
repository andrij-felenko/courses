#include <benchmark/benchmark.h>
#include <vector>
#include <numeric>

static void BM_VectorAccumulate(benchmark::State& state) {
    const auto size = static_cast<std::size_t>(state.range(0));
    std::vector<int> data(size, 42);

    // Головний вимірювальний цикл: бібліотека автоматично підбирає
    // кількість проходів для досягнення стабільного часу заміру
    for (auto _ : state) {
        int sum = std::accumulate(data.begin(), data.end(), 0);
        benchmark::DoNotOptimize(sum);
    }

    // Реєстрація метрик оброблених даних
    state.SetBytesProcessed(static_cast<int64_t>(state.iterations()) *
                            static_cast<int64_t>(size * sizeof(int)));
    state.SetItemsProcessed(static_cast<int64_t>(state.iterations()) *
                            static_cast<int64_t>(size));
}
BENCHMARK(BM_VectorAccumulate)->Range(64, 1 << 16);
