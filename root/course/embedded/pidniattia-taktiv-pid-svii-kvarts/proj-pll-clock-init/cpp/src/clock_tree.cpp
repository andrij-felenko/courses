#include "bsp/clock_tree.hpp"

#include "bsp/registers.hpp"

namespace bsp::clock {

using namespace bsp::soc;

namespace {

/* Після скидання ядро тактується внутрішнім RC на 16 МГц */
volatile std::uint32_t g_sysclk_hz = hsi_hz;

/* Секція .noinit не чиститься стартапом: лічильник аварій переживе перезапуск */
[[gnu::section(".noinit")]] volatile std::uint32_t g_css_events;

/* Гасимо силову частину: MOE=0 знімає всі шість виходів ШІМ мосту */
void force_safe_state() noexcept {
    tim1_bdtr() &= ~tim_bdtr_moe;
}

} // namespace

std::uint32_t sysclk_hz() noexcept { return g_sysclk_hz; }
void note_sysclk(std::uint32_t hz) noexcept { g_sysclk_hz = hz; }
std::uint32_t css_event_count() noexcept { return g_css_events; }

[[noreturn]] void system_reset() noexcept {
    scb_aircr() = sysresetreq;
    for (;;) {
    }
}

Result set_flash_latency(std::uint32_t wait_states) noexcept {
    mmio::modify(flash().acr, acr::latency.mask,
                 acr::latency(wait_states) | acr::prften | acr::icen | acr::dcen);

    /* Поле LATENCY перечитуємо: поки запис не набув чинності,
       підвищувати частоту не можна */
    if (!mmio::wait_until(flash().acr, acr::latency.mask,
                          acr::latency(wait_states), timeout_cycles)) {
        return std::unexpected(Error::flash_latency);
    }
    return {};
}

void reset_flash_caches() noexcept {
    /* ICRST/DCRST приймаються лише при вимкнених кешах — інакше в них
       лишиться сміття, прочитане за старими таймінгами */
    flash().acr &= ~(acr::icen | acr::dcen);
    flash().acr |= acr::icrst | acr::dcrst;
    flash().acr &= ~(acr::icrst | acr::dcrst);
    flash().acr |= acr::icen | acr::dcen;
}

Result set_voltage_scale(VoltageScale scale) noexcept {
    /* Інтерфейс PWR сидить на APB1 і після скидання не тактується */
    rcc().apb1enr |= apb1enr_pwren;
    static_cast<void>(rcc().apb1enr);   // холостий читок: запис на APB доходить із затримкою

    /* Поле VOS дозволено міняти лише при вимкненому PLL */
    mmio::modify(pwr().cr, pwr_cr::vos.mask,
                 pwr_cr::vos(static_cast<std::uint32_t>(scale)));

    if (!mmio::wait_until(pwr().csr, pwr_csr::vosrdy, pwr_csr::vosrdy, timeout_cycles)) {
        return std::unexpected(Error::voltage_timeout);
    }
    return {};
}

void set_bus_prescalers(std::uint32_t ahb, std::uint32_t apb1, std::uint32_t apb2) noexcept {
    /* Через modify, а не прямим записом: інакше стерли б налаштування MCO */
    mmio::modify(rcc().cfgr,
                 cfgr::hpre.mask | cfgr::ppre1.mask | cfgr::ppre2.mask,
                 cfgr::hpre(ahb) | cfgr::ppre1(apb1) | cfgr::ppre2(apb2));
}

void fallback_to_hsi() noexcept {
    rcc().cr |= cr::hsion;
    if (!mmio::wait_until(rcc().cr, cr::hsirdy, cr::hsirdy, timeout_cycles)) {
        system_reset();   // немає ні кварцу, ні внутрішнього RC — рятувати нічим
    }

    mmio::modify(rcc().cfgr, cfgr::sw.mask, cfgr::sw(cfgr::src_hsi));
    static_cast<void>(mmio::wait_until(rcc().cfgr, cfgr::sws.mask,
                                       cfgr::sws(cfgr::src_hsi), timeout_cycles));

    set_bus_prescalers(cfgr::ahb_div1, cfgr::apb_div1, cfgr::apb_div1);
    rcc().cr &= ~cr::pllon;
    static_cast<void>(set_flash_latency(flash_ws_16mhz));

    g_sysclk_hz = hsi_hz;
}

Result configure_pll_168mhz() noexcept {
    /* 1а. Напруга ядра: без Scale 1 кремній на 168 МГц не рахує */
    if (auto r = set_voltage_scale(VoltageScale::scale1); !r) {
        fallback_to_hsi();
        return r;
    }

    /* 1б. Затримки Flash піднімаємо ДО частоти: брак тактів очікування
       на 168 МГц дає HardFault на першій же інструкції */
    if (auto r = set_flash_latency(flash_ws_168mhz); !r) {
        fallback_to_hsi();
        return r;
    }

    /* 2. Генератор Пірса на зовнішньому кварці */
    rcc().cr |= cr::hseon;
    if (!mmio::wait_until(rcc().cr, cr::hserdy, cr::hserdy, timeout_cycles)) {
        rcc().cr &= ~cr::hseon;   // не тримаємо ввімкненим мертвий генератор
        fallback_to_hsi();
        return std::unexpected(Error::hse_timeout);
    }

    /* 3. Переддільники — до перемикання: APB1 має ліміт 45 МГц, APB2 — 90 МГц */
    set_bus_prescalers(cfgr::ahb_div1, cfgr::apb_div4, cfgr::apb_div2);

    /* 4. Коефіцієнти пишуться лише при вимкненому контурі */
    rcc().cr &= ~cr::pllon;
    static_cast<void>(mmio::wait_until(rcc().cr, cr::pllrdy, 0U, timeout_cycles));
    rcc().pllcfgr = pll168.encode_from_hse();

    /* 5. Запуск і очікування фазового захоплення */
    rcc().cr |= cr::pllon;
    if (!mmio::wait_until(rcc().cr, cr::pllrdy, cr::pllrdy, timeout_cycles)) {
        rcc().cr &= ~cr::pllon;
        fallback_to_hsi();
        return std::unexpected(Error::pll_timeout);
    }

    /* 6. Перемикання мультиплексора з підтвердженням від апаратури */
    mmio::modify(rcc().cfgr, cfgr::sw.mask, cfgr::sw(cfgr::src_pll));
    if (!mmio::wait_until(rcc().cfgr, cfgr::sws.mask,
                          cfgr::sws(cfgr::src_pll), timeout_cycles)) {
        fallback_to_hsi();
        return std::unexpected(Error::switch_timeout);
    }

    /* 7. Кварц справді тримає систему — вмикаємо його апаратний монітор */
    rcc().cr |= cr::csson;

    g_sysclk_hz = pll_hz;
    return {};
}

} // namespace bsp::clock

/* Немасковане переривання: єдиний штатний привід тут — зрив генерації кварцу */
extern "C" void NMI_Handler() {
    using namespace bsp::clock;
    using namespace bsp::soc;

    if ((rcc().cir & cir::cssf) == 0U) {
        system_reset();   // NMI не від CSS: причина невідома, безпечніше перезапуск
    }

    /* Автомат RCC уже сам перемкнув SYSCLK на HSI і вимкнув PLL, тож ці рядки
       виконуються на 16 МГц із 5 WS — зайві такти очікування нешкідливі */
    force_safe_state();

    rcc().cir |= cir::cssc;    // запис 1 у CSSC знімає прапорець CSSF
    rcc().cr &= ~cr::hseon;    // знімаємо дозвіл мертвого генератора

    note_sysclk(hsi_hz);
    ++g_css_events;            // причина аварії переживе перезапуск

    for (;;) {
        /* чекаємо на скидання від сторожового таймера: старт із чистого стану
           надійніший за спробу жити далі на невідомому тактуванні */
    }
}
