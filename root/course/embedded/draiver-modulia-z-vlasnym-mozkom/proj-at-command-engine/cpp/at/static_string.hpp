#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <string_view>

namespace at {

/* Рядок фіксованої місткості. Заміняє char[N] + strncpy: сам стежить за
   завершальним нулем і чесно каже, що не вліз, замість мовчазного обрізання
   (обрізана AT-команда — це інша команда, і модуль виконає саме її). */
template <std::size_t Capacity>
class StaticString {
public:
    static_assert(Capacity >= 2);

    constexpr StaticString() = default;

    /* Окремий конструктор від const char* потрібен не для краси: без нього
       StaticString s = "AT+CSQ" вимагало б двох користувацьких перетворень
       поспіль (char* → string_view → StaticString), а таке не компілюється. */
    constexpr StaticString(const char* text) noexcept : StaticString{std::string_view{text}} {}

    constexpr StaticString(std::string_view text) noexcept
    {
        const std::size_t fit = std::min(text.size(), Capacity - 1);
        std::copy_n(text.begin(), fit, data_.begin());
        data_[fit] = '\0';
        size_ = fit;
        truncated_ = (fit != text.size());
    }

    [[nodiscard]] constexpr std::string_view view() const noexcept { return {data_.data(), size_}; }
    [[nodiscard]] constexpr const char* c_str() const noexcept { return data_.data(); }
    [[nodiscard]] constexpr std::size_t size() const noexcept { return size_; }
    [[nodiscard]] constexpr bool empty() const noexcept { return size_ == 0; }
    [[nodiscard]] constexpr bool truncated() const noexcept { return truncated_; }

    [[nodiscard]] constexpr bool operator==(std::string_view other) const noexcept
    {
        return view() == other;
    }

    constexpr void clear() noexcept
    {
        data_[0] = '\0';
        size_ = 0;
        truncated_ = false;
    }

private:
    std::array<char, Capacity> data_{};
    std::size_t size_{0};
    bool truncated_{false};
};

}  // namespace at
