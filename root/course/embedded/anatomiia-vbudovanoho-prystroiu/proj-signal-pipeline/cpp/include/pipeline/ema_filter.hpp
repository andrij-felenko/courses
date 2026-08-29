#pragma once

#include <cstdint>

namespace pipeline {

/// Експоненційний фільтр першого порядку: alpha = 1 / 2^Shift.
/// Зсув — параметр типу, а не поле: компілятор підставляє його в інструкцію,
/// тож у прошивці лишається одне віднімання, один зсув і одне додавання.
template <std::uint8_t Shift>
class EmaFilter {
    static_assert(Shift >= 1 && Shift <= 12,
                  "Shift == 0 знерухомив би фільтр, завеликий зсув обнулив би приріст");

public:
    constexpr std::int32_t update(std::int32_t sample) noexcept
    {
        // Перший відлік беремо як є: інакше фільтр повз би від нуля до робочої
        // точки кілька сотень періодів, а регулятор вважав би це помилкою.
        if (!primed_) {
            value_ = sample;
            primed_ = true;
            return value_;
        }
        value_ += (sample - value_) >> Shift;
        return value_;
    }

    [[nodiscard]] constexpr std::int32_t value() const noexcept { return value_; }

    constexpr void reset() noexcept
    {
        value_ = 0;
        primed_ = false;
    }

private:
    std::int32_t value_{0};
    bool primed_{false};
};

} // namespace pipeline
