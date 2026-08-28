// C++20: Типобезпечні інтервали часу з std::chrono без важкої емуляції
#include <cstdint>
#include <chrono>

using namespace std::chrono_literals;

// 32-бітний інтервал часу без 64-бітної емуляції
using mcu_ticks_t = std::chrono::duration<uint32_t, std::milli>;

void process_timer(mcu_ticks_t now) noexcept {
    // std::chrono::duration_cast оптимізується компілятором в одну машинну команду
    auto seconds = std::chrono::duration_cast<std::chrono::seconds>(now);
    (void)seconds;
}
