#include <array>
#include <cstdint>
#include <optional>
#include <span>
#include <algorithm>

namespace sensing {

enum class CalibStatus {
    Ok,
    ClampedLow,
    ClampedHigh
};

struct CompensationResult {
    float value;
    CalibStatus status;
};

/* Шаблонний клас двовимірної таблиці калібрування на фіксованій сітці */
template <std::size_t NumX, std::size_t NumT>
class LookupTable2D {
public:
    static_assert(NumX >= 2 && NumT >= 2, "Сітка повинна містити щонайменше 2x2 вузли");

    constexpr LookupTable2D(std::array<float, NumX> x_nodes,
                            std::array<float, NumT> t_nodes,
                            std::array<std::array<float, NumX>, NumT> values)
        : x_grid_{x_nodes}, t_grid_{t_nodes}, table_{values} {}

    [[nodiscard]] CompensationResult evaluate(float raw_x, float raw_t) const noexcept {
        CalibStatus status = CalibStatus::Ok;

        /* Clamping вхідного сигналу X */
        float x = raw_x;
        if (x <= x_grid_.front()) {
            x = x_grid_.front();
            status = CalibStatus::ClampedLow;
        } else if (x >= x_grid_.back()) {
            x = x_grid_.back();
            status = CalibStatus::ClampedHigh;
        }

        /* Clamping температури T */
        float t = raw_t;
        if (t <= t_grid_.front()) {
            t = t_grid_.front();
            status = CalibStatus::ClampedLow;
        } else if (t >= t_grid_.back()) {
            t = t_grid_.back();
            status = CalibStatus::ClampedHigh;
        }

        /* Пошук комірки сітки бінарним розбиттям через std::upper_bound */
        auto it_x = std::upper_bound(x_grid_.begin(), x_grid_.end() - 1, x);
        const std::size_t i = (it_x == x_grid_.begin()) ? 0 : std::distance(x_grid_.begin(), it_x) - 1;

        auto it_t = std::upper_bound(t_grid_.begin(), t_grid_.end() - 1, t);
        const std::size_t j = (it_t == t_grid_.begin()) ? 0 : std::distance(t_grid_.begin(), it_t) - 1;

        /* Нормалізовані локальні змінні u та v */
        const float dx = x_grid_[i + 1] - x_grid_[i];
        const float dt = t_grid_[j + 1] - t_grid_[j];
        const float u = (dx > 1e-7f) ? ((x - x_grid_[i]) / dx) : 0.0f;
        const float v = (dt > 1e-7f) ? ((t - t_grid_[j]) / dt) : 0.0f;

        /* Кутові значення */
        const float q11 = table_[j][i];
        const float q21 = table_[j][i + 1];
        const float q12 = table_[j + 1][i];
        const float q22 = table_[j + 1][i + 1];

        /* Білінійна інтерполяція */
        const float r1 = q11 + u * (q21 - q11);
        const float r2 = q12 + u * (q22 - q12);
        const float result = r1 + v * (r2 - r1);

        return {result, status};
    }

private:
    std::array<float, NumX> x_grid_;
    std::array<float, NumT> t_grid_;
    std::array<std::array<float, NumX>, NumT> table_;
};

/* Клас поліноміальної моделі другого порядку P(U, T) */
class Polynomial2D {
public:
    struct Coefficients {
        float c00{0.0f}, c10{0.0f}, c01{0.0f};
        float c11{0.0f};
        float c20{0.0f}, c02{0.0f};
        float c21{0.0f}, c12{0.0f};
        float c22{0.0f};
    };

    constexpr explicit Polynomial2D(const Coefficients& coeffs) noexcept : c_{coeffs} {}

    [[nodiscard]] constexpr float evaluate(float u, float t) const noexcept {
        const float term_const = c_.c00 + t * (c_.c01 + t * c_.c02);
        const float term_u1    = c_.c10 + t * (c_.c11 + t * c_.c12);
        const float term_u2    = c_.c20 + t * (c_.c21 + t * c_.c22);
        return term_const + u * (term_u1 + u * term_u2);
    }

private:
    Coefficients c_;
};

} // namespace sensing
