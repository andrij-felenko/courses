#include <iostream>
#include <cmath>
#include <functional>
#include <iomanip>

namespace math::optimization {

constexpr double inv_phi = 0.61803398874989484820;

struct SearchResult {
    double min_x;
    double min_value;
    std::size_t eval_count;
};

/*
 * Обчислює мінімум унімодальної функції func на інтервалі [a, b].
 * Використовує std::function для гнучкої передачі лямбда-виразів та функторів.
 */
SearchResult golden_section_search(
    const std::function<double(double)>& func,
    double a,
    double b,
    double eps = 1e-7) 
{
    double x1 = b - inv_phi * (b - a);
    double x2 = a + inv_phi * (b - a);
    double f1 = func(x1);
    double f2 = func(x2);
    
    std::size_t evals = 2;

    while (std::abs(b - a) > eps) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            x1 = b - inv_phi * (b - a);
            f1 = func(x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = a + inv_phi * (b - a);
            f2 = func(x2);
        }
        ++evals;
    }

    double best_x = (a + b) / 2.0;
    return SearchResult{best_x, func(best_x), evals};
}

/* Швидкий шаблонний варіант без накладних витрат std::function */
template <typename Func>
SearchResult golden_section_search_template(
    Func&& func,
    double a,
    double b,
    double eps = 1e-7)
{
    double x1 = b - inv_phi * (b - a);
    double x2 = a + inv_phi * (b - a);
    double f1 = func(x1);
    double f2 = func(x2);
    std::size_t evals = 2;

    while (std::abs(b - a) > eps) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            x1 = b - inv_phi * (b - a);
            f1 = func(x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = a + inv_phi * (b - a);
            f2 = func(x2);
        }
        ++evals;
    }
    double best_x = (a + b) / 2.0;
    return SearchResult{best_x, func(best_x), evals};
}

} // namespace math::optimization

int main() {
    // Тестова функція з мінімумом у точці x = e ≈ 2.718281828
    auto f = [](double x) {
        return (x - std::exp(1.0)) * (x - std::exp(1.0)) + 5.0;
    };

    auto result = math::optimization::golden_section_search(f, 0.0, 5.0, 1e-8);

    std::cout << std::fixed << std::setprecision(8);
    std::cout << "C++ Result: min_x = " << result.min_x 
              << ", f(min_x) = " << result.min_value 
              << " (evals = " << result.eval_count << ")\n";

    return 0;
}
