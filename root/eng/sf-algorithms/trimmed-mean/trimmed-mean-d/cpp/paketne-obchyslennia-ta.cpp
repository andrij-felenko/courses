#include <algorithm>
#include <numeric>
#include <span>
#include <optional>
#include <vector>

/* Обчислення усіченого середнього для довільного діапазону значень */
[[nodiscard]] std::optional<double> calculate_trimmed_mean(std::span<double> data, std::size_t k) {
    const std::size_t n = data.size();
    if (n == 0 || 2 * k >= n) {
        return std::nullopt;
    }

    if (k == 0) {
        const double sum = std::accumulate(data.begin(), data.end(), 0.0);
        return sum / static_cast<double>(n);
    }

    /* nth_element переставляє k-й найменший елемент на позицію data.begin() + k */
    auto k_left = data.begin() + static_cast<std::ptrdiff_t>(k);
    std::nth_element(data.begin(), k_left, data.end());

    /* Другий виклик фіксує правий край на позиції data.end() - k */
    auto k_right = data.end() - static_cast<std::ptrdiff_t>(k);
    std::nth_element(k_left + 1, k_right, data.end());

    /* Усі елементи між k_left та k_right належать центральному ядру */
    const double sum = std::accumulate(k_left, k_right, 0.0);
    const auto active_count = static_cast<double>(n - 2 * k);

    return sum / active_count;
}
