// Одне випробування: спалах, очікування фронту від фотоприймача, результат.
// Порожній std::optional означає втрачений кадр — окремого коду помилки й
// магічного значення «-1» тут не потрібно.
#pragma once

#include <atomic>
#include <cstdint>
#include <optional>

#include "board.hpp"

namespace latency {

class MeasurementRig {
public:
    // Захисний таймаут: усе, що довше чверті секунди, — не затримка тракту,
    // а втрачений кадр (обрив відеопотоку, пакет, що не долетів).
    static constexpr board::Microseconds kTimeout{250000};

    // Блокує потік до відгуку або таймауту. std::nullopt — кадр утрачено.
    [[nodiscard]] std::optional<board::Microseconds> run_trial() noexcept;

    // Викликається ЛИШЕ з обробника переривання EXTI0.
    void on_capture(board::Microseconds timestamp) noexcept;

private:
    // Поля ділять обробник переривання й головний потік. Атомарність тут не
    // про паралельні ядра, а про порядок: без release/acquire компілятор має
    // право виставити «результат готовий» раніше за сам результат.
    std::atomic<std::uint32_t> start_us_{0};
    std::atomic<std::uint32_t> capture_us_{0};
    std::atomic<bool> armed_{false};
    std::atomic<bool> ready_{false};
};

// Єдиний екземпляр стенда — з ним пов'язаний вектор EXTI0.
[[nodiscard]] MeasurementRig &rig() noexcept;

} // namespace latency
