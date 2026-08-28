#include <vector>
#include <span>
#include <cstdint>

// Функція злиття двох локальних вибірок у глобальну вибірку
template <typename T>
std::vector<T> merge_reservoirs(
    std::span<const T> sample_a, std::uint64_t total_a,
    std::span<const T> sample_b, std::uint64_t total_b,
    std::size_t target_k, std::uint64_t seed = 0x5a17e10ULL
) {
    WeightedReservoirSampler<T> merger(target_k, seed);

    double weight_a = sample_a.empty() ? 0.0 : (static_cast<double>(total_a) / sample_a.size());
    double weight_b = sample_b.empty() ? 0.0 : (static_cast<double>(total_b) / sample_b.size());

    for (const auto& item : sample_a) {
        merger.push(item, weight_a);
    }
    for (const auto& item : sample_b) {
        merger.push(item, weight_b);
    }

    return merger.extract_sample();
}
