#include <utility>
#include <stdexcept>
#include <cmath>

struct PolyDivisionResult {
    Polynomial quotient;
    Polynomial remainder;
};

// Безпечне ділення з остачею з перевіркою інваріантів
[[nodiscard]] PolyDivisionResult divide(const Polynomial& a, const Polynomial& b) {
    if (b.coeffs.empty() || std::abs(b.coeffs.back()) < 1e-12) {
        throw std::invalid_argument("Помилка: ділення на нульовий многочлен");
    }

    if (a.degree() < b.degree()) {
        return { Polynomial(0), a };
    }

    const size_t q_deg = a.degree() - b.degree();
    Polynomial q(q_deg);
    Polynomial rem = a;

    const double lead_b = b.coeffs.back();

    for (size_t i = a.degree(); i >= b.degree(); --i) {
        const size_t q_idx = i - b.degree();
        const double factor = rem.coeffs[i] / lead_b;
        q.coeffs[q_idx] = factor;

        for (size_t j = 0; j <= b.degree(); ++j) {
            rem.coeffs[q_idx + j] -= factor * b.coeffs[j];
        }
        if (i == 0) break;
    }

    q.normalize();
    rem.normalize();
    return { std::move(q), std::move(rem) };
}
