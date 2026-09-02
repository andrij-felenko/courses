#pragma once

// Захисний інтервал старту. Той самий механізм, що й у C-версії, але вікно
// вимірюється в std::chrono, а не в «магічних» мілісекундах-числах.

#include <chrono>

namespace mcu::boot {

enum class GuardResult {
    Proceed,          // вікно минуло — периферію вмикати можна
    HeldByOperator    // кнопку відновлення затиснуто
};

// Вікно, за яке налагоджувач встигає перехопити ядро.
inline constexpr std::chrono::milliseconds kGuardWindow{2000};
inline constexpr std::chrono::milliseconds kDebounce{20};

// Тримає блок налагодження живим у SLEEP/STOP/STANDBY.
void keep_debug_in_low_power() noexcept;

// Чи вже сидить налагоджувач на шині (біт C_DEBUGEN у DHCSR).
[[nodiscard]] bool debugger_attached() noexcept;

// Витримує вікно, стежачи за кнопкою відновлення.
[[nodiscard]] GuardResult guard(std::chrono::milliseconds window) noexcept;

// Безпечний вічний цикл: ядро живе, DAP відповідає.
[[noreturn]] void park() noexcept;

}  // namespace mcu::boot
