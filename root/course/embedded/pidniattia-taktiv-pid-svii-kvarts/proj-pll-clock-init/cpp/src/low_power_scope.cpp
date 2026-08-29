#include "bsp/low_power_scope.hpp"

#include "bsp/registers.hpp"

namespace bsp::clock {

using namespace bsp::soc;

Result enter_low_power() noexcept {
    /* 1. Спершу мультиплексор. Поки ядро живиться з PLL, чіпати ні сам контур,
       ні затримки Flash не можна: інструкцію просто нічим буде вичитати */
    rcc().cr |= cr::hsion;
    if (!mmio::wait_until(rcc().cr, cr::hsirdy, cr::hsirdy, timeout_cycles)) {
        return std::unexpected(Error::hsi_timeout);
    }

    mmio::modify(rcc().cfgr, cfgr::sw.mask, cfgr::sw(cfgr::src_hsi));
    if (!mmio::wait_until(rcc().cfgr, cfgr::sws.mask,
                          cfgr::sws(cfgr::src_hsi), timeout_cycles)) {
        return std::unexpected(Error::switch_timeout);
    }
    note_sysclk(hsi_hz);

    /* 2. Шини на /1: на 16 МГц дільники APB лише крали б периферії частоту */
    set_bus_prescalers(cfgr::ahb_div1, cfgr::apb_div1, cfgr::apb_div1);

    /* 3. PLL більше нікого не тактує. HSE лишаємо крутитися: повернення на
       повну швидкість тоді коштує мікросекунди, і монітор CSS лишається чинним */
    rcc().cr &= ~cr::pllon;
    static_cast<void>(mmio::wait_until(rcc().cr, cr::pllrdy, 0U, timeout_cycles));

    /* 4. Аж тепер зменшуємо затримки Flash і скидаємо кеші */
    if (auto r = set_flash_latency(flash_ws_16mhz); !r) {
        return r;
    }
    reset_flash_caches();

    /* 5. Останньою опускаємо напругу ядра — це дозволено лише при вимкненому PLL */
    return set_voltage_scale(VoltageScale::scale3);
}

Result enter_full_speed() noexcept {
    /* 1. Напруга ядра — перша: розганяти кремній на 1.0 В не можна */
    if (auto r = set_voltage_scale(VoltageScale::scale1); !r) {
        return r;
    }

    /* 2. Затримки Flash піднімаємо ще на 16 МГц */
    if (auto r = set_flash_latency(flash_ws_168mhz); !r) {
        return r;
    }

    /* 3. Кварц ми не гасили, але після зриву CSS його могло вже не бути */
    rcc().cr |= cr::hseon;
    if (!mmio::wait_until(rcc().cr, cr::hserdy, cr::hserdy, timeout_cycles)) {
        fallback_to_hsi();
        return std::unexpected(Error::hse_timeout);
    }

    /* 4. Дільники шин — до підняття SYSCLK */
    set_bus_prescalers(cfgr::ahb_div1, cfgr::apb_div4, cfgr::apb_div2);

    /* 5. Контур: коефіцієнти в PLLCFGR лишилися з ініціалізації */
    rcc().cr |= cr::pllon;
    if (!mmio::wait_until(rcc().cr, cr::pllrdy, cr::pllrdy, timeout_cycles)) {
        rcc().cr &= ~cr::pllon;
        return std::unexpected(Error::pll_timeout);
    }

    /* 6. І тільки тепер мультиплексор на вихід PLL */
    mmio::modify(rcc().cfgr, cfgr::sw.mask, cfgr::sw(cfgr::src_pll));
    if (!mmio::wait_until(rcc().cfgr, cfgr::sws.mask,
                          cfgr::sws(cfgr::src_pll), timeout_cycles)) {
        fallback_to_hsi();
        return std::unexpected(Error::switch_timeout);
    }

    note_sysclk(pll_hz);
    return {};
}

LowPowerScope::LowPowerScope() noexcept
    : lowered_(enter_low_power().has_value()) {}

LowPowerScope::~LowPowerScope() {
    if (!lowered_) {
        return;   // не знижували — нема чого й піднімати
    }
    if (!enter_full_speed()) {
        /* Повернути розрахункове тактування не вдалося. Далі виконувати код
           на невідомій частоті небезпечніше, ніж перезапуститись */
        system_reset();
    }
}

} // namespace bsp::clock
