// Контур струму векторного керування. Усе, що виконується всередині
// 25-мікросекундного вікна, оголошене з атрибутом секції .ramfunc:
// GCC вимагає бачити секцію вже на оголошенні, тому макрос стоїть тут,
// а не біля визначення в .cpp.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#define FOC_RAMFUNC [[gnu::section(".ramfunc"), gnu::noinline]]

namespace foc {

inline constexpr std::size_t kSineBits = 8U;
inline constexpr std::size_t kSineSize = std::size_t{1} << kSineBits;
inline constexpr float kDutyMin = 0.02f;   // запас на мертвий час
inline constexpr float kDutyMax = 0.98f;

struct Duties {
    float a{0.5f};
    float b{0.5f};
    float c{0.5f};
};

struct Dq {
    float d{0.0f};
    float q{0.0f};
};

// Електричний кут як фаза Q32: перехід через 2*pi — це просто переповнення
// лічильника, тож у критичному коді немає ні fmodf, ні гілки нормалізації.
class Phase {
public:
    constexpr Phase() noexcept = default;
    constexpr explicit Phase(std::uint32_t raw) noexcept : raw_{raw} {}

    static constexpr Phase step_for(float electrical_hz, float update_hz) noexcept
    {
        return Phase{static_cast<std::uint32_t>(
            static_cast<double>(electrical_hz) / update_hz * 4294967296.0)};
    }

    constexpr Phase& operator+=(Phase step) noexcept
    {
        raw_ += step.raw_;   // переповнення тут навмисне
        return *this;
    }

    [[nodiscard]] constexpr std::uint32_t raw() const noexcept { return raw_; }

private:
    std::uint32_t raw_{0};
};

// Таблиця з дублікатом нуля наприкінці: інтерполяція не потребує
// перевірки межі, а отже й переходу.
class SineTable {
public:
    void build() noexcept;
    [[nodiscard]] std::array<float, 2> sin_cos(Phase phase) const noexcept;

private:
    std::array<float, kSineSize + 1U> table_{};
};

class PiRegulator {
public:
    constexpr PiRegulator(float kp, float ki, float limit) noexcept
        : kp_{kp}, ki_{ki}, limit_{limit} {}

    [[nodiscard]] float step(float error) noexcept;

    constexpr void reset() noexcept { integral_ = 0.0f; }
    constexpr void scale_integral(float k) noexcept { integral_ *= k; }

private:
    float kp_;
    float ki_;
    float limit_;
    float integral_{0.0f};
};

class CurrentLoop {
public:
    void build_tables() noexcept;
    void reset() noexcept;
    constexpr void set_targets(Dq reference) noexcept { reference_ = reference; }

    // Повний крок контуру: Кларк, Парк, два ПІ, кругове обмеження,
    // зворотні перетворення та інжекція середньої точки.
    FOC_RAMFUNC Duties update(float ia, float ib, Phase theta, float vdc) noexcept;

private:
    SineTable sine_{};
    PiRegulator d_{2.5f, 0.08f, 12.0f};
    PiRegulator q_{2.5f, 0.08f, 12.0f};
    Dq reference_{};
};

}  // namespace foc
