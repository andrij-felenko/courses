static void BM_BinarySearch(benchmark::State& state) {
    const auto n = state.range(0);
    std::vector<int> v(n);
    std::iota(v.begin(), v.end(), 0);

    for (auto _ : state) {
        bool found = std::binary_search(v.begin(), v.end(), n / 2);
        benchmark::DoNotOptimize(found);
    }
    state.SetComplexityN(n);
}
BENCHMARK(BM_BinarySearch)->Range(64, 1 << 20)->Complexity(benchmark::oLogN);
