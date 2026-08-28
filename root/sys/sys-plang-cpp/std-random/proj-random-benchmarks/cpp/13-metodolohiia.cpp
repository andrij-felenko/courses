#include <benchmark/benchmark.h>
#include <random>

static void BM_MersenneTwister(benchmark::State& state) {
    std::mt19937 rng(42);
    for (auto _ : state) {
        benchmark::DoNotOptimize(rng());
    }
}
BENCHMARK(BM_MersenneTwister);

static void BM_PCG32(benchmark::State& state) {
    // Власний генератор PCG32
    pcg32_engine rng(42);
    for (auto _ : state) {
        benchmark::DoNotOptimize(rng());
    }
}
BENCHMARK(BM_PCG32);

BENCHMARK_MAIN();
