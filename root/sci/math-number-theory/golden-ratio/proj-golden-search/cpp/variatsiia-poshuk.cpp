#include <vector>
#include <functional>
#include <cmath>

namespace math::optimization {

double fibonacci_search(
    const std::function<double(double)>& func,
    double a,
    double b,
    std::size_t n)
{
    std::vector<unsigned long long> F(n + 1);
    F[0] = 0; F[1] = 1;
    for (std::size_t i = 2; i <= n; ++i) F[i] = F[i - 1] + F[i - 2];

    double x1 = a + static_cast<double>(F[n - 2]) / F[n] * (b - a);
    double x2 = a + static_cast<double>(F[n - 1]) / F[n] * (b - a);
    double f1 = func(x1);
    double f2 = func(x2);

    for (std::size_t k = n; k > 2; --k) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            x1 = a + static_cast<double>(F[k - 3]) / F[k - 1] * (b - a);
            f1 = func(x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = a + static_cast<double>(F[k - 2]) / F[k - 1] * (b - a);
            f2 = func(x2);
        }
    }
    return (a + b) / 2.0;
}

} // namespace math::optimization
