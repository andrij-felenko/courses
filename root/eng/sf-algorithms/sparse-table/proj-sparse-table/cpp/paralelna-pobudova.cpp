#include <vector>
#include <span>
#include <thread>
#include <algorithm>
#include <cstddef>
#include <cstdint>

/* Багатопотокова побудова розрідженої таблиці засобами C++20 */
template <typename T>
void build_parallel_cpp(std::span<T> table, std::span<const T> values, 
                        std::size_t levels, std::size_t num_threads = 0) 
{
    const std::size_t n = values.size();
    if (n == 0) return;
    if (num_threads == 0) num_threads = std::max(1u, std::thread::hardware_concurrency());

    /* Рівень 0 */
    std::copy(values.begin(), values.end(), table.begin());

    for (std::size_t j = 1; j < levels; ++j) {
        const std::size_t half = std::size_t{1} << (j - 1);
        const std::size_t len = std::size_t{1} << j;
        const std::size_t row_curr = j * n;
        const std::size_t row_prev = (j - 1) * n;
        const std::size_t limit = (n >= len) ? (n - len + 1) : 0;

        const std::size_t chunk = (limit + num_threads - 1) / num_threads;
        std::vector<std::jthread> workers;
        workers.reserve(num_threads);

        for (std::size_t t = 0; t < num_threads; ++t) {
            const std::size_t start = t * chunk;
            const std::size_t end = std::min(start + chunk, limit);
            if (start >= end) break;

            workers.emplace_back([&, start, end, half, row_curr, row_prev]() {
                for (std::size_t i = start; i < end; ++i) {
                    table[row_curr + i] = std::min(table[row_prev + i], 
                                                   table[row_prev + i + half]);
                }
            });
        }
    }
}
