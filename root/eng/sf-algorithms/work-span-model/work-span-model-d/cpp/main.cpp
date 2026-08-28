#include <iostream>
#include <vector>
#include <span>
#include <numeric>
#include <future>
#include <execution>

constexpr size_t CUTOFF_THRESHOLD = 5000;

// Рекурсивна функція з логарифмічною глибиною T_inf = O(log N)
double parallel_sum_span(std::span<const double> data) {
    if (data.size() <= CUTOFF_THRESHOLD) {
        return std::accumulate(data.begin(), data.end(), 0.0);
    }

    size_t mid = data.size() / 2;
    auto left_half = data.subspan(0, mid);
    auto right_half = data.subspan(mid);

    // Породження асинхронної гілки (spawn)
    std::future<double> left_future = std::async(
        std::launch::async,
        [left_half]() { return parallel_sum_span(left_half); }
    );

    // Обчислення правої гілки в поточному потоці
    double right_result = parallel_sum_span(right_half);

    // Синхронізація результатів (sync)
    double left_result = left_future.get();

    return left_result + right_result;
}
