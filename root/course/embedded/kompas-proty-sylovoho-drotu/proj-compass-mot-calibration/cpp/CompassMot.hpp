// CompassMot.hpp — модель завади від струму: компенсатор і регресія OLS.
// Про мотори, газ і регламент прогону цей заголовок не знає нічого.
#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <expected>
#include <span>
#include <string_view>

namespace compassmot {

struct Vector3 {
    float x{};
    float y{};
    float z{};

    [[nodiscard]] constexpr Vector3 operator+(const Vector3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    [[nodiscard]] constexpr Vector3 operator-(const Vector3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    [[nodiscard]] constexpr Vector3 operator*(float s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] float norm() const noexcept;
    [[nodiscard]] bool finite() const noexcept;
};

// Одна точка стендових даних.
struct Sample {
    float   current_a{};
    Vector3 field;      // мкТл, СИРЕ показання магнітометра
};

struct Fit {
    Vector3              k;                  // мкТл/А
    std::array<float, 3> r2{};               // якість підгонки по осях
    float                interference_pct{}; // ||ΔB(I_max)|| / ||B_base||
    float                i_max{};            // струм, на якому оцінено заваду
    std::size_t          samples{};
};

enum class FitError {
    TooFewSamples,   // прогін обірвався надто рано
    NoCurrentSpan,   // струм не змінювався — нахилу з даних не дістати
    NoBaseField,     // базове поле ~0: компас не читається
    StoreFailed      // параметри не лягли в енергонезалежну пам'ять
};

[[nodiscard]] std::string_view describe(FitError err) noexcept;
// Три смуги придатності компоновки.
[[nodiscard]] std::string_view verdict(float interference_pct) noexcept;

// ------------------------------------------------------------------
// Потоковий компенсатор: B_clean = B_meas − k · I_filt
// ------------------------------------------------------------------
class Compensator {
public:
    Compensator(Vector3 k,
                std::chrono::duration<float> dt,
                float cutoff_hz,
                float max_current_a) noexcept;

    void set_coefficients(Vector3 k) noexcept;
    void reset() noexcept { current_lpf_ = 0.0f; }

    [[nodiscard]] const Vector3& coefficients() const noexcept { return k_; }
    [[nodiscard]] bool active() const noexcept { return active_; }

    // Один такт польотного циклу. Збрехав давач струму — віддаємо сире
    // поле незмінним: гірше за некомпенсоване тільки хибно компенсоване.
    [[nodiscard]] Vector3 compensate(const Vector3& raw, float current_a) noexcept;

private:
    Vector3 k_{};
    float   lpf_alpha_{1.0f};
    float   current_lpf_{0.0f};
    float   max_current_a_{250.0f};
    bool    active_{false};
};

// ------------------------------------------------------------------
// Накопичувач найменших квадратів
// ------------------------------------------------------------------
class OlsAccumulator {
public:
    explicit OlsAccumulator(Vector3 baseline) noexcept : baseline_{baseline} {}

    void add(const Sample& s) noexcept;
    void add(std::span<const Sample> batch) noexcept;   // для розбору лога

    [[nodiscard]] std::expected<Fit, FitError> solve() const noexcept;

    [[nodiscard]] std::size_t count() const noexcept { return n_; }
    [[nodiscard]] std::size_t rejected() const noexcept { return rejected_; }
    [[nodiscard]] const Vector3& baseline() const noexcept { return baseline_; }

private:
    // Суми — у double: тисяча вибірок по I² з'їдає мантису float.
    Vector3                baseline_{};
    double                 sum_i_{0.0};
    double                 sum_i2_{0.0};
    std::array<double, 3>  sum_b_{};
    std::array<double, 3>  sum_b2_{};
    std::array<double, 3>  sum_ib_{};
    float                  i_max_{0.0f};
    std::size_t            n_{0};
    std::size_t            rejected_{0};
};

}  // namespace compassmot
