// TIM2: мілісекундна база часу й приклад правильного квитування прапорця.
#pragma once

#include <atomic>
#include <cstdint>

namespace isr {

class Timer {
public:
    // Верхня половина. Кличеться з extern "C" TIM2_IRQHandler().
    static void handle_irq() noexcept;

    // Час від запуску. Складається з двох слів, тому знімається під
    // критичною секцією — інакше між читанням молодшої та старшої
    // половини може влізти саме те переривання, яке їх і змінює.
    [[nodiscard]] static std::uint64_t ms_since_boot() noexcept;

    // Скільки разів NVIC заходив у обробник, не заставши там прапорця.
    // Ненульове значення означає, що квитування не встигає за виходом.
    [[nodiscard]] static std::uint32_t spurious_entries() noexcept;

private:
    static std::atomic<std::uint32_t> ticks_;
    static std::atomic<std::uint32_t> wraps_;
    static std::atomic<std::uint32_t> spurious_;
};

} // namespace isr
