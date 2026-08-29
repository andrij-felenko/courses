// board.hpp — плата як об'єкт: шина SPI з вибором кристала на RAII,
// лінія DRDY, годинник і форматований вивід у термінал.
//
// На відміну від C-версії, тут немає окремого «контракту порту»: власником
// CS є сама шина, і опустити його інакше, ніж через охоронця Selection,
// просто нема як. Забути підняти CS у гілці помилки стає неможливо.
#pragma once

#include <algorithm>
#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <format>
#include <span>
#include <string_view>
#include <utility>

namespace board {

// Тактування, GPIO, SPI, UART. Один раз на початку main().
void init();

// Стан виводу DRDY: true, коли готовий новий результат перетворення.
// Вивід активний низьким рівнем, інверсія лишається тут.
[[nodiscard]] bool data_ready() noexcept;

// Монотонний час від старту.
[[nodiscard]] std::chrono::milliseconds uptime() noexcept;

void sleep(std::chrono::milliseconds delay) noexcept;

// Рядок у термінал, із переведенням каретки.
void write_line(std::string_view text) noexcept;

class SpiBus {
public:
    // Охоронець вибору кристала: опускає CS у конструкторі, підіймає в
    // деструкторі. Некопійовний і нерухомий — існує рівно на час обміну.
    class Selection {
    public:
        explicit Selection(SpiBus& bus) noexcept;
        ~Selection() noexcept;

        Selection(const Selection&) = delete;
        Selection& operator=(const Selection&) = delete;
        Selection(Selection&&) = delete;
        Selection& operator=(Selection&&) = delete;

    private:
        SpiBus& bus_;
    };

    // Повертається як prvalue, тож ані копії, ані переміщення не потрібно:
    //     auto cs = bus.select();
    [[nodiscard]] Selection select() noexcept { return Selection{*this}; }

    // Повнодуплексний обмін. Розміри span мусять збігатися — інакше false.
    // Помилка тут означає апаратну відмову контролера SPI, а не затримку.
    [[nodiscard]] bool transfer(std::span<const std::uint8_t> tx,
                                std::span<std::uint8_t> rx) noexcept;

private:
    friend class Selection;

    void assert_cs() noexcept;
    void release_cs() noexcept;
};

// Форматований вивід поверх write_line. Буфер фіксований: динамічної
// пам'яті на цій платі немає й не буде.
template <typename... Args>
void log(std::format_string<Args...> fmt, Args&&... args) noexcept
{
    std::array<char, 192> buffer{};

    auto result = std::format_to_n(buffer.begin(), buffer.size(), fmt,
                                   std::forward<Args>(args)...);

    // format_to_n повертає потрібну довжину, а не записану — обрізаємо самі.
    const auto written = std::min<std::size_t>(static_cast<std::size_t>(result.size),
                                               buffer.size());
    write_line(std::string_view{buffer.data(), written});
}

}  // namespace board
