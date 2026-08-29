#include "CompassMot.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>

namespace compassmot {
namespace {

constexpr std::size_t kMinSamples = 30;
constexpr double      kMinDenom   = 1.0e-3;
constexpr float       kMinField   = 5.0f;   // поле Землі — 25..65 мкТл

}  // namespace

float Vector3::norm() const noexcept
{
    return std::sqrt(x * x + y * y + z * z);
}

bool Vector3::finite() const noexcept
{
    return std::isfinite(x) && std::isfinite(y) && std::isfinite(z);
}

std::string_view describe(FitError err) noexcept
{
    switch (err) {
    case FitError::TooFewSamples: return "замало вибірок: прогін обірвався";
    case FitError::NoCurrentSpan: return "струм не змінювався: нахил не визначений";
    case FitError::NoBaseField:   return "базове поле близьке до нуля: компас не читається";
    case FitError::StoreFailed:   return "збій запису параметрів";
    }
    return "невідома помилка";
}

std::string_view verdict(float interference_pct) noexcept
{
    if (!std::isfinite(interference_pct)) {
        return "оцінка недійсна";
    }
    if (interference_pct < 10.0f) {
        return "відмінна компоновка: залишкова похибка курсу < 0.5°";
    }
    if (interference_pct <= 30.0f) {
        return "помірна завада: типово для компактної рами, дрейф < 1.5°";
    }
    return "критично: компас надто близько до силових трас, підняти щоглу";
}

// ------------------------------------------------------------------

Compensator::Compensator(Vector3 k,
                         std::chrono::duration<float> dt,
                         float cutoff_hz,
                         float max_current_a) noexcept
    : max_current_a_{max_current_a > 0.0f ? max_current_a : 250.0f}
{
    set_coefficients(k);

    // alpha = dt / (RC + dt), RC = 1 / (2π·fc). Фільтр вирівнює групову
    // затримку шунта з дециматором магнітометра: без нього на різкому
    // газі в очищеному полі лишаються тонкі піки.
    const float dt_sec = dt.count();
    if (dt_sec > 0.0f && cutoff_hz > 0.0f) {
        const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz);
        lpf_alpha_ = dt_sec / (rc + dt_sec);
    }
}

void Compensator::set_coefficients(Vector3 k) noexcept
{
    k_ = k.finite() ? k : Vector3{};
    active_ = k_.norm() > 1.0e-5f;
}

Vector3 Compensator::compensate(const Vector3& raw, float current_a) noexcept
{
    if (!active_ || !raw.finite()) {
        return raw;
    }
    if (!std::isfinite(current_a) || current_a < 0.0f || current_a > max_current_a_) {
        return raw;   // стан фільтра навмисно не чіпаємо
    }

    current_lpf_ += lpf_alpha_ * (current_a - current_lpf_);
    return raw - k_ * current_lpf_;
}

// ------------------------------------------------------------------

void OlsAccumulator::add(const Sample& s) noexcept
{
    if (!std::isfinite(s.current_a) || s.current_a < 0.0f || !s.field.finite()) {
        ++rejected_;
        return;
    }

    const Vector3 d = s.field - baseline_;
    const std::array<double, 3> dv{d.x, d.y, d.z};
    const double i = static_cast<double>(s.current_a);

    sum_i_  += i;
    sum_i2_ += i * i;
    for (std::size_t a = 0; a < 3; ++a) {
        sum_b_[a]  += dv[a];
        sum_b2_[a] += dv[a] * dv[a];
        sum_ib_[a] += i * dv[a];
    }
    i_max_ = std::max(i_max_, s.current_a);
    ++n_;
}

void OlsAccumulator::add(std::span<const Sample> batch) noexcept
{
    for (const Sample& s : batch) {
        add(s);
    }
}

std::expected<Fit, FitError> OlsAccumulator::solve() const noexcept
{
    if (n_ < kMinSamples) {
        return std::unexpected(FitError::TooFewSamples);
    }

    const double n = static_cast<double>(n_);
    const double denom = n * sum_i2_ - sum_i_ * sum_i_;   // спільний для трьох осей
    if (std::abs(denom) < kMinDenom) {
        return std::unexpected(FitError::NoCurrentSpan);
    }

    const float base_norm = baseline_.norm();
    if (!(base_norm > kMinField)) {
        return std::unexpected(FitError::NoBaseField);
    }

    Fit fit;
    std::array<float, 3> k{};
    for (std::size_t a = 0; a < 3; ++a) {
        const double num = n * sum_ib_[a] - sum_i_ * sum_b_[a];
        k[a] = static_cast<float>(num / denom);

        // R² однієї змінної — квадрат кореляції.
        const double var_b = n * sum_b2_[a] - sum_b_[a] * sum_b_[a];
        const double r2 = (var_b > 1.0e-9) ? (num * num) / (denom * var_b) : 0.0;
        fit.r2[a] = static_cast<float>(std::min(r2, 1.0));
    }

    fit.k = Vector3{k[0], k[1], k[2]};
    fit.i_max = i_max_;
    fit.samples = n_;
    fit.interference_pct = (fit.k.norm() * i_max_ / base_norm) * 100.0f;
    return fit;
}

}  // namespace compassmot
