#include <span>
#include <algorithm>
#include <numeric>

/* Ідіоматична C++ реалізація пошуку зміщення через std::span */
[[nodiscard]] int wsola_find_best_shift_cpp(
    std::span<const float> ref,
    std::span<const float> search_region,
    int seek_range) noexcept {
    
    const size_t L = ref.size();
    float max_corr = -1e30f;
    int best_delta = 0;

    for (int d = -seek_range; d <= seek_range; ++d) {
        const size_t offset = static_cast<size_t>(d + seek_range);
        auto cand = search_region.subspan(offset, L);

        // Скалярний добуток через стандартний алгоритм
        const float corr = std::inner_product(
            ref.begin(), ref.end(), cand.begin(), 0.0f);

        if (corr > max_corr) {
            max_corr = corr;
            best_delta = d;
        }
    }

    return best_delta;
}
