// ===========================================================================
//  mag_cal/linear_solver.hpp — щільна система N×N методом Гаусса з частковим
//  вибором головного елемента. Шаблон, бо розмір системи відомий у типі:
//  ані буферів на купі, ані перевірок розміру під час виконання.
// ===========================================================================
#pragma once

#include <array>
#include <cmath>
#include <cstddef>
#include <optional>
#include <utility>

namespace mag_cal {

// Матриця й вектор приймаються за значенням: розв'язувач руйнує їх під час
// прямого ходу, і копія тут чесніша за прихований вихідний параметр.
template <std::size_t N>
[[nodiscard]] std::optional<std::array<float, N>> solve_linear(
    std::array<std::array<float, N>, N> a, std::array<float, N> x) noexcept {
    constexpr float kPivotFloor = 1e-8F;

    for (std::size_t i = 0; i < N; ++i) {
        // Головний елемент: найбільший за модулем у стовпці нижче діагоналі
        std::size_t pivot_row = i;
        float pivot_abs = std::abs(a[i][i]);
        for (std::size_t k = i + 1; k < N; ++k) {
            const float v = std::abs(a[k][i]);
            if (v > pivot_abs) {
                pivot_abs = v;
                pivot_row = k;
            }
        }

        if (!(pivot_abs > kPivotFloor)) {
            return std::nullopt;   // система вироджена
        }

        if (pivot_row != i) {
            std::swap(a[i], a[pivot_row]);
            std::swap(x[i], x[pivot_row]);
        }

        const float inv_pivot = 1.0F / a[i][i];
        for (std::size_t k = i + 1; k < N; ++k) {
            const float factor = a[k][i] * inv_pivot;
            if (factor == 0.0F) {
                continue;
            }
            for (std::size_t j = i; j < N; ++j) {
                a[k][j] -= factor * a[i][j];
            }
            x[k] -= factor * x[i];
        }
    }

    // Зворотний хід
    for (std::size_t i = N; i-- > 0;) {
        float sum = x[i];
        for (std::size_t j = i + 1; j < N; ++j) {
            sum -= a[i][j] * x[j];
        }
        x[i] = sum / a[i][i];
        if (!std::isfinite(x[i])) {
            return std::nullopt;
        }
    }
    return x;
}

}  // namespace mag_cal
