#include <cstdint>

#include "mcu/registers.hpp"
#include "mcu/startup.hpp"

namespace {

constexpr std::uint32_t hsi_hz = 16'000'000U;
constexpr std::uint32_t sysclk_hz = 168'000'000U;

/* PLL: VCO_in = HSE / M = 1 МГц, VCO_out = ×N = 336 МГц,
   SYSCLK = VCO_out / P = 168 МГц, гілка USB = VCO_out / Q = 48 МГц */
constexpr std::uint32_t pll_m = 8;
constexpr std::uint32_t pll_n = 336;
constexpr std::uint32_t pll_p = 2; /* поле PLLP кодує дільник 2 як 0b00 */
constexpr std::uint32_t pll_q = 7;

constexpr std::uint32_t pllcfgr_value = pll_m | (pll_n << 6)
                                      | (((pll_p / 2) - 1) << 16)
                                      | mcu::rcc::pllsrc_hse | (pll_q << 24);

/* Скільки разів опитуємо прапорець, перш ніж визнати відмову.
   Лічильник, а не таймер: на цьому етапі таймерів іще немає. */
constexpr std::uint32_t poll_limit = 0x0005'0000U;

template <typename Reg>
[[nodiscard]] bool poll_until(std::uint32_t mask, std::uint32_t expected) noexcept
{
    for (std::uint32_t guard = 0; guard < poll_limit; ++guard) {
        if ((Reg::read() & mask) == expected) {
            return true;
        }
    }
    return false;
}

/* Повернення дерева тактування до заводського стану: після програмного
   скидання регістри RCC зберігають конфігурацію попереднього запуску,
   а заводити PLL поверх чужих налаштувань не можна. */
void reset_clock_tree() noexcept
{
    namespace rcc = mcu::rcc;
    rcc::cr::set(rcc::hsi_on);   /* внутрішній RC лишається запасним завжди */
    rcc::cfgr::write(0U);        /* SYSCLK = HSI, дільники шин = 1 */
    rcc::cr::clear(rcc::hse_on | rcc::css_on | rcc::pll_on);
    rcc::pllcfgr::write(rcc::pllcfgr_reset);
    rcc::cr::clear(rcc::hse_bypass);
    rcc::cir::write(0U);         /* усі переривання RCC вимкнено й очищено */
}

} // namespace

namespace mcu {

startup_result configure_clock() noexcept
{
    reset_clock_tree();

    rcc::cr::set(rcc::hse_on);
    if (!poll_until<rcc::cr>(rcc::hse_ready, rcc::hse_ready)) {
        /* Кварц не завівся: не розпаяний, тріснув або замерз. Лишаємось
           на HSI — 16 МГц повільно, зате прошивка жива й може про це
           повідомити. Затримки Flash на такій частоті не потрібні. */
        flash::acr::write(flash::prefetch | flash::icache | flash::dcache);
        core_clock_hz = hsi_hz;
        return std::unexpected{startup_error::hse_not_ready};
    }

    /* Затримки Flash ставимо ДО підняття частоти: на 168 МГц пам'ять
       фізично не встигає віддати слово за такт, і ядро читало б сміття
       замість інструкцій. */
    flash::acr::write(flash::prefetch | flash::icache | flash::dcache
                      | flash::latency_5ws);

    /* Дільники шин: AHB 168 МГц, APB1 42 МГц (стеля 42), APB2 84 МГц */
    rcc::cfgr::write(rcc::hpre_div1 | rcc::ppre1_div4 | rcc::ppre2_div2);
    rcc::pllcfgr::write(pllcfgr_value);

    rcc::cr::set(rcc::pll_on);
    if (!poll_until<rcc::cr>(rcc::pll_ready, rcc::pll_ready)) {
        /* PLL не захопився. Зайві такти очікування Flash на 16 МГц
           нікому не шкодять, лише трохи гальмують. */
        core_clock_hz = hsi_hz;
        return std::unexpected{startup_error::pll_not_locked};
    }

    /* Поле SW лише просить перемкнутися; підтверджує це поле SWS */
    rcc::cfgr::modify(rcc::sw_mask, rcc::sw_pll);
    if (!poll_until<rcc::cfgr>(rcc::sws_mask, rcc::sws_pll)) {
        core_clock_hz = hsi_hz;
        return std::unexpected{startup_error::clock_switch_failed};
    }

    core_clock_hz = sysclk_hz;
    rcc::cr::set(rcc::css_on); /* тепер стежимо за зривом кварцу */
    return {};
}

} // namespace mcu
