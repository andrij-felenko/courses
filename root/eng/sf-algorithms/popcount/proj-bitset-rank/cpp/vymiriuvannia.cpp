#include <chrono>
#include <cstdint>
#include <cstdio>
#include <random>
#include <vector>

std::size_t count_hw(const std::uint64_t *w, std::size_t nw);    // окрема одиниця трансляції
std::size_t count_swar(const std::uint64_t *w, std::size_t nw);  // окрема одиниця трансляції

template <class F>
double ns_per_word(F f, const std::uint64_t *w, std::size_t nw, std::size_t &sink) {
    sink += f(w, nw);                                 // прогрів: сторінки й кеш
    std::size_t reps = (std::size_t{1} << 26) / nw;   // однаковий обсяг роботи на всіх розмірах
    if (reps == 0) reps = 1;
    auto t0 = std::chrono::steady_clock::now();
    for (std::size_t r = 0; r < reps; ++r) sink += f(w, nw);
    auto t1 = std::chrono::steady_clock::now();
    double sec = std::chrono::duration<double>(t1 - t0).count();
    return sec * 1e9 / (double)reps / (double)nw;
}

int main() {
    std::mt19937_64 rng(1);
    std::size_t sink = 0;
    std::printf("%8s %12s %12s %10s\n", "КіБ", "апарат", "SWAR", "ГБ/с");
    for (std::size_t kib = 4; kib <= (1u << 18); kib *= 4) {   // 4 КіБ … 256 МіБ
        std::vector<std::uint64_t> v(kib * 1024 / 8);
        for (auto &x : v) x = rng();
        double a = ns_per_word(count_hw,   v.data(), v.size(), sink);
        double b = ns_per_word(count_swar, v.data(), v.size(), sink);
        std::printf("%8zu %12.3f %12.3f %10.1f\n", kib, a, b, 8.0 / a);
    }
    std::printf("контрольна сума: %zu\n", sink);   // без цього рядка цикли зникнуть
}
