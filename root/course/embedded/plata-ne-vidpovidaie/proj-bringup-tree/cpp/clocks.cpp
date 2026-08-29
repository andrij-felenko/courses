// Фаза 1: верифікація тактових доменів.
#include "bringup.hpp"

namespace bringup {
namespace {

namespace rcc = mmio::rcc;

// HSE 8 МГц → VCO 336 МГц → SYSCLK 168 МГц (M=8, N=336, P=2, Q=7).
constexpr std::uint32_t pll_m = 8U;
constexpr std::uint32_t pll_n = 336U;
constexpr std::uint32_t pll_p = 2U;
constexpr std::uint32_t pll_q = 7U;

// 200000 ітерацій при 16 МГц ≈ 50 мс — із запасом більше за час
// розгойдування кварцу (типово 2–5 мс).
constexpr std::uint32_t hsi_tries = 10'000U;
constexpr std::uint32_t hse_tries = 200'000U;
constexpr std::uint32_t pll_tries = 50'000U;

}  // namespace

Result<ClockStatus> verify_clocks() noexcept
{
    ClockStatus status;

    // HSI не залежить від жодного зовнішнього компонента: якщо не готове
    // воно — справа не в платі, а в самому кристалі.
    rcc::cr::set(rcc::hsion);
    status.hsi_ready = mmio::wait_until([] { return rcc::cr::any(rcc::hsirdy); }, hsi_tries);

    // Явно лишаємося на HSI й чекаємо підтвердження в полі SWS.
    rcc::cfgr::clear(rcc::sw_mask);
    static_cast<void>(mmio::wait_until([] { return !rcc::cfgr::any(rcc::sws_mask); }, hsi_tries));

    // Запуск кварцу. Найчастіший дефект — невдалі C1/C2: від'ємний опір
    // інвертора не перекриває втрат кристала, і HSERDY не встає ніколи.
    rcc::cr::set(rcc::hseon);
    status.hse_ready = mmio::wait_until([] { return rcc::cr::any(rcc::hserdy); }, hse_tries);
    if (!status.hse_ready) {
        rcc::cr::clear(rcc::hseon);   // не гріємо драйвер, який не заводиться
        return std::unexpected(Error::hse_timeout);
    }

    // PLLCFGR дозволено чіпати лише при вимкненій петлі.
    rcc::cr::clear(rcc::pllon);
    static_cast<void>(mmio::wait_until([] { return !rcc::cr::any(rcc::pllrdy); }, pll_tries));

    rcc::pllcfgr::write((pll_m << 0)
                        | (pll_n << 6)
                        | (((pll_p / 2U) - 1U) << 16)
                        | rcc::pllsrc_hse
                        | (pll_q << 24));

    rcc::cr::set(rcc::pllon);
    status.pll_ready = mmio::wait_until([] { return rcc::cr::any(rcc::pllrdy); }, pll_tries);
    rcc::cr::clear(rcc::pllon);   // захоплення перевірили — далі знову HSI
    if (!status.pll_ready) {
        return std::unexpected(Error::pll_timeout);
    }

    return status;
}

}  // namespace bringup
