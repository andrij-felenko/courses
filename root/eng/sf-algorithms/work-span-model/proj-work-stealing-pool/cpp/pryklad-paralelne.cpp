#include <numeric>
#include <future>

long long parallel_reduce(std::span<const int> data, WorkStealingPool &pool) {
    constexpr size_t threshold = 1000;
    if (data.size() <= threshold) {
        return std::accumulate(data.begin(), data.end(), 0LL);
    }

    size_t mid = data.size() / 2;
    auto left_span = data.subspan(0, mid);
    auto right_span = data.subspan(mid);

    std::promise<long long> right_promise;
    auto right_future = right_promise.get_future();

    // Відправляємо праву частину в пул (spawn)
    pool.submit([right_span, &right_promise, &pool]() {
        right_promise.set_value(parallel_reduce(right_span, pool));
    });

    // Ліва частина виконується поточним потоком безпосередньо
    long long left_sum = parallel_reduce(left_span, pool);

    // Очікування результату правої гілки (sync)
    long long right_sum = right_future.get();

    return left_sum + right_sum;
}
