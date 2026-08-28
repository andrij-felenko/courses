#include <algorithm>
#include <cmath>
#include <cstddef>
#include <functional>
#include <limits>
#include <vector>

using Vec = std::vector<double>;
using Mat = std::vector<Vec>;                 // J[i][j] = ∂fᵢ/∂xⱼ
using Fun = std::function<Vec(const Vec&)>;   // F: ℝⁿ → ℝᵐ

// Однобічні різниці. f0 = F(x) приходить ззовні: у методі Ньютона
// це нев'язка, яку однаково вже порахували.
// scale[j] — типовий масштаб j-ї змінної в її власних одиницях, строго > 0.
Mat jacobianForward(const Fun& F, const Vec& x, const Vec& f0, const Vec& scale)
{
    static const double rt = std::sqrt(std::numeric_limits<double>::epsilon()); // ≈1.49e-8
    const std::size_t n = x.size(), m = f0.size();
    Mat J(m, Vec(n));
    Vec xt = x;
    for (std::size_t j = 0; j < n; ++j) {
        const double step = rt * std::max(std::abs(x[j]), scale[j]);
        volatile double bumped = x[j] + step;   // volatile — щоб компілятор
        const double h = bumped - x[j];         // не «спростив» цей рядок
        xt[j] = bumped;
        const Vec f1 = F(xt);
        xt[j] = x[j];
        for (std::size_t i = 0; i < m; ++i)
            J[i][j] = (f1[i] - f0[i]) / h;
    }
    return J;
}
