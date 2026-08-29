#include "bsp/mco.hpp"

#include "bsp/clock_tree.hpp"
#include "bsp/registers.hpp"

namespace bsp::mco {

using namespace bsp::soc;

namespace {

constexpr std::uint32_t pin = 8;

/* Коди дільника лежать у регістрі не по порядку: 0b000 це /1,
   а 0b100..0b111 — це /2../5, тобто значення мінус два */
constexpr std::uint32_t divisor_of(Prescaler p) noexcept {
    const auto raw = static_cast<std::uint32_t>(p);
    return raw == 0U ? 1U : raw - 2U;
}

static_assert(divisor_of(Prescaler::div1) == 1);
static_assert(divisor_of(Prescaler::div4) == 4);
static_assert(divisor_of(Prescaler::div5) == 5);

} // namespace

void enable_on_pa8(Source source, Prescaler prescaler) noexcept {
    /* 1. Джерело й дільник обираємо ДО того, як вивід стане альтернативною
       функцією: інакше на пін вилізе перехідний процес мультиплексора */
    mmio::modify(rcc().cfgr, cfgr::mco1.mask | cfgr::mco1pre.mask,
                 cfgr::mco1(static_cast<std::uint32_t>(source))
                     | cfgr::mco1pre(static_cast<std::uint32_t>(prescaler)));

    /* 2. Тактування порту GPIOA */
    rcc().ahb1enr |= ahb1enr_gpioaen;
    static_cast<void>(rcc().ahb1enr);   // запис на AHB доходить із затримкою в такт

    /* 3. PA8 у режим альтернативної функції (10b), AF0 = MCO1 (пін 8 — у afr[1]) */
    mmio::modify(gpioa().moder, 0x3U << (pin * 2), 0x2U << (pin * 2));
    gpioa().afr[1] &= ~(0xFU << ((pin - 8) * 4));

    /* 4. Push-pull без підтяжок: на 42 МГц підтяжка не встигне перезарядити ємність */
    gpioa().otyper &= ~(1U << pin);
    gpioa().pupdr &= ~(0x3U << (pin * 2));

    /* 5. Найшвидший драйвер виходу (11b) — інакше замість прямокутника
       осцилограф покаже завалені фронти */
    gpioa().ospeedr |= 0x3U << (pin * 2);
}

std::uint32_t expected_hz(Prescaler prescaler) noexcept {
    return clock::sysclk_hz() / divisor_of(prescaler);
}

} // namespace bsp::mco
