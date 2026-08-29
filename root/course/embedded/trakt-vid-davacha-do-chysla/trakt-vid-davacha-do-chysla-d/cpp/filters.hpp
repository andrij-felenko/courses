#pragma once

// Цифрова частина тракту (розділ 5). Арифметика цілочисельна навмисно: цей самий
// код має йти в переривання АЦП на ядрі без апаратної плаваючої коми. Довжини
// вікон — параметри шаблонів, бо вони відомі на етапі складання прошивки й
// визначають розмір буфера.

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

// Ділення з округленням до найближчого: цілочисельне ділення в C++ відкидає
// дробову частину в бік нуля й дає систематичний зсув на пів кванта.
[[nodiscard]] constexpr std::int32_t divRound(std::int64_t numerator,
                                              std::int64_t denominator) noexcept
{
    if (denominator == 0) {
        return 0;
    }
    const std::int64_t half = denominator / 2;
    const bool sameSign = (numerator >= 0) == (denominator > 0);
    const std::int64_t result = sameSign ? (numerator + half) / denominator
                                         : (numerator - half) / denominator;
    return static_cast<std::int32_t>(result);
}

// Рухоме середнє на кільцевому буфері. Вікно в рівно один період завади дає
// нуль АЧХ точно на її частоті: сума синусоїди за повний період — нуль.
template <std::size_t Window>
class MovingAverage {
    static_assert(Window >= 2, "вікно з одного відліку нічого не усереднює");

public:
    std::int32_t update(std::int32_t sample) noexcept
    {
        sum_ -= buffer_[index_];
        buffer_[index_] = sample;
        sum_ += sample;
        index_ = (index_ + 1) % Window;

        if (filled_ < Window) {
            ++filled_;
        }
        return divRound(sum_, static_cast<std::int64_t>(filled_));
    }

    // Поки вікно неповне, заваду фільтр ще не вирізає — калібруватися по такому
    // відліку не можна.
    [[nodiscard]] bool ready() const noexcept { return filled_ >= Window; }

    void reset() noexcept
    {
        buffer_.fill(0);
        sum_ = 0;
        index_ = 0;
        filled_ = 0;
    }

private:
    std::array<std::int32_t, Window> buffer_{};
    std::int64_t sum_{0};
    std::size_t  index_{0};
    std::size_t  filled_{0};
};

// Експоненційне згладжування y[n] = y[n-1] + (x[n] - y[n-1]) >> Shift.
// Накопичувач тримається у форматі Q(Shift): без цих додаткових розрядів
// різниця на молодших квантах губиться і фільтр застрягає на цілому числі.
template <unsigned Shift>
class ExponentialSmoother {
    static_assert(Shift >= 1 && Shift <= 15, "поза цим діапазоном фільтра просто немає");

public:
    std::int32_t update(std::int32_t sample) noexcept
    {
        if (!primed_) {
            // Перший відлік заряджає накопичувач одразу, інакше показання
            // повзтиме до робочої точки з нуля цілу секунду.
            accumulator_ = static_cast<std::int64_t>(sample) << Shift;
            primed_ = true;
            return sample;
        }

        accumulator_ += sample - (accumulator_ >> Shift);
        return static_cast<std::int32_t>(accumulator_ >> Shift);
    }

    void reset() noexcept
    {
        accumulator_ = 0;
        primed_ = false;
    }

private:
    std::int64_t accumulator_{0};
    bool         primed_{false};
};

// Проріджувач «накопичити й скинути»: збирає Factor відліків швидкого потоку
// й віддає один повільного. Це і є передискретизація з розділу 3.
//
// Результат — у форматі Q(log2(Scale)): усереднення ста відліків дає близько
// 3.3 додаткових розряди, і повернення до цілих кодів викинуло б увесь виграш.
template <std::size_t Factor, std::int32_t Scale = 16>
class Decimator {
    static_assert(Factor >= 2, "проріджування на одиницю — це відсутність проріджування");

public:
    [[nodiscard]] std::optional<std::int32_t> push(std::int32_t sample) noexcept
    {
        sum_ += sample;
        if (++count_ < Factor) {
            return std::nullopt;
        }

        const std::int32_t averaged =
            divRound(sum_ * Scale, static_cast<std::int64_t>(Factor));
        sum_ = 0;
        count_ = 0;
        return averaged;
    }

    static constexpr std::int32_t scale() noexcept { return Scale; }

private:
    std::int64_t sum_{0};
    std::size_t  count_{0};
};
