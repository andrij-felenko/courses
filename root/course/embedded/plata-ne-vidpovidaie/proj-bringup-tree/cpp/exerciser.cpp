// Фаза 2: генератор контрольних сигналів на діагностичних майданчиках.
// Меандр дає осцилографу за секунду відповісти на два питання: чи ціла
// доріжка й чи справний двотактний вихідний буфер.
#include "bringup.hpp"

#include <array>

namespace bringup {
namespace {

constexpr std::uint32_t half_period_us = 5U;   // меандр ~100 кГц

constexpr std::array<mmio::Pin, 3> testpoints{{
    {mmio::porta, 5U},
    {mmio::porta, 6U},
    {mmio::porta, 7U},
}};

}  // namespace

std::span<const mmio::Pin> default_testpoints() noexcept
{
    return testpoints;
}

void exercise_testpoints(std::span<const mmio::Pin> pins, std::uint32_t cycles) noexcept
{
    if (pins.empty()) {
        return;
    }

    std::uint32_t set_mask = 0U;
    std::uint32_t reset_mask = 0U;

    for (const auto& pin : pins) {
        pin.enable_clock();
        pin.configure(mmio::Mode::output, mmio::OutputType::push_pull, mmio::Pull::none);
        set_mask |= pin.set_mask();
        reset_mask |= pin.reset_mask();
    }

    // Усі майданчики цієї фази — на одному порту, тож смикаємо їх одним
    // записом у BSRR: фронти виходять одночасні, і на екрані це видно.
    volatile std::uint32_t& bsrr = mmio::at(pins.front().port.base + 0x18U);

    for (std::uint32_t i = 0U; i < cycles; ++i) {
        bsrr = set_mask;
        mmio::delay_us(half_period_us);
        bsrr = reset_mask;
        mmio::delay_us(half_period_us);
    }

    // Лишаємо лінії в нулі: постійний високий рівень на непідключеному
    // виводі легко сплутати з результатом перевірки.
    bsrr = reset_mask;
}

}  // namespace bringup
