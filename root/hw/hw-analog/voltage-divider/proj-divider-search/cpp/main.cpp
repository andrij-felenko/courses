#include <cstdint>
#include <cstddef>

// e_series — усі значення E24 по декадах (відсортовані), в омах.
// Ціль (бажане R1/R2) задаємо дробом num/den, щоб працювати без плаваючої коми.
struct Pair { std::uint32_t r1, r2; };

// Найближче до ТОЧНОГО ідеалу goal/den значення у відсортованій таблиці ряду.
// goal = num·R2 — чисельник ідеального R1 = goal/den, den — спільний знаменник цілі.
// Важливо: ідеал НЕ округлюємо до цілого — інакше на межі між двома E24 обрали б гірший.
static std::uint32_t nearest(const std::uint32_t* e, std::size_t n,
                             std::uint64_t goal, std::uint32_t den) {
    std::size_t lo = 0, hi = n;
    while (lo < hi) {                      // межа: перший e[i], для якого e[i]·den >= goal
        std::size_t mid = lo + (hi - lo) / 2;
        if ((std::uint64_t)e[mid] * den < goal) lo = mid + 1; else hi = mid;
    }
    if (lo == 0) return e[0];
    if (lo == n) return e[n - 1];
    // Відстані рахуємо ТОЧНО, навхрест цілими: |e·den − goal| (спільний den при виборі зникає).
    std::uint64_t hi_dist = (std::uint64_t)e[lo] * den - goal;      // e[lo]·den >= goal
    std::uint64_t lo_dist = goal - (std::uint64_t)e[lo - 1] * den;  // e[lo-1]·den <= goal
    return hi_dist < lo_dist ? e[lo] : e[lo - 1];
}

Pair find_pair(std::uint32_t num, std::uint32_t den,
               const std::uint32_t* e, std::size_t n) {
    Pair best{0, 0};
    std::uint64_t best_num = 1, best_den = 0;          // best_err = best_num/best_den = ∞
    for (std::size_t j = 0; j < n; ++j) {
        std::uint32_t r2 = e[j];
        std::uint64_t goal = (std::uint64_t)num * r2;             // чисельник ідеального R1
        std::uint32_t r1 = nearest(e, n, goal, den);             // двійковий пошук за ТОЧНИМ ідеалом
        // err = |r1·den − num·R2| / (num·R2); порівнюємо дроби навхрест, без ділення
        std::uint64_t diff = (std::uint64_t)r1 * den;
        std::uint64_t err_num = diff > goal ? diff - goal : goal - diff;
        std::uint64_t err_den = goal;                            // масштаб похибки: err_num/goal
        // err_num/err_den < best_num/best_den  ⟺  err_num·best_den < best_num·err_den
        if (err_num * best_den < best_num * err_den) {
            best_num = err_num; best_den = err_den; best = Pair{r1, r2};
        }
    }
    return best;
}
