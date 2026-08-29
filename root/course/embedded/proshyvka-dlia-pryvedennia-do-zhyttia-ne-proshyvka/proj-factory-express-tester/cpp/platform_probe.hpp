#pragma once

#include <cstdint>

#include "fct.hpp"
#include "hal.hpp"

// Фаза 0: живлення й тактування. Доки ці два тести не пройшли, енергоємні
// модулі не вмикають узагалі.

namespace fct {

inline constexpr std::int32_t kVrefintCalMv = 3000;  // калібрування зняте при 3.000 В
inline constexpr std::int32_t kAdcFullScale = 4095;
inline constexpr std::int32_t kVddaNominalMv = 3300;
inline constexpr std::int32_t kVcoreNominalMv = 1800;
inline constexpr std::int32_t kVcoreDivider = 2;
inline constexpr std::int32_t kRailTolerancePct = 3;

inline constexpr std::uint16_t kInrushLimitMa = 400;
inline constexpr std::uint16_t kInrushLimitUs = 3000;
inline constexpr std::uint16_t kIqMinUa = 100;
inline constexpr std::uint16_t kIqMaxUa = 2500;

inline constexpr std::uint32_t kHseNominalHz = 24'000'000;
inline constexpr std::uint32_t kHseToleranceHz = 12'000;
inline constexpr std::uint32_t kPllLockTimeoutUs = 5'000;

// V_DDA = 3.000 В * CAL / RAW. Потрібна і тесту живлення, і сторожуванню
// напруги під час пропалювання OTP.
[[nodiscard]] inline std::expected<std::int32_t, Failure> read_vdda_mv() noexcept
{
    const auto raw = hal::adc_read(hal::AdcChannel::Vrefint, 2000);
    if (!raw) {
        return fail(Error::Timeout, "АЦП: канал VREFINT не відповідає");
    }
    if (*raw == 0) {
        return fail(Error::Fail, "VREFINT дає нуль: АЦП не запустився");
    }
    return kVrefintCalMv * static_cast<std::int32_t>(hal::vrefint_cal()) /
           static_cast<std::int32_t>(*raw);
}

[[nodiscard]] constexpr bool within_tolerance(std::int32_t value_mv,
                                              std::int32_t nominal_mv) noexcept
{
    const std::int32_t delta = value_mv > nominal_mv ? value_mv - nominal_mv
                                                     : nominal_mv - value_mv;
    return delta * 100 <= nominal_mv * kRailTolerancePct;
}

inline Outcome test_power_rails() noexcept
{
    // Кроки 1–2 зняв сам стенд ще до відпускання RESET: прошивка забирає
    // журнал і виносить по ньому вердикт.
    const auto log = hal::stand_power_log(50'000);
    if (!log) {
        return fail(Error::Timeout, "Стенд не віддав журнал фази 0");
    }
    if (log->inrush_peak_ma > kInrushLimitMa &&
        log->inrush_duration_us > kInrushLimitUs) {
        return fail(Error::Fail, "Струм ввімкнення: коротке в силовій шині",
                    log->inrush_peak_ma, "mA");
    }
    if (log->iq_ua > kIqMaxUa) {
        return fail(Error::Fail,
                    "Струм спокою завищений: діоди захисту, BGA або флюс",
                    log->iq_ua, "uA");
    }
    if (log->iq_ua < kIqMinUa) {
        return fail(Error::Fail, "Струм спокою нижчий за норму: плата не живиться",
                    log->iq_ua, "uA");
    }

    const auto vdda = read_vdda_mv();
    if (!vdda) {
        return std::unexpected(vdda.error());
    }
    if (!within_tolerance(*vdda, kVddaNominalMv)) {
        return fail(Error::Fail, "V_DDA поза допуском ±3%", *vdda, "mV");
    }

    const auto core_raw = hal::adc_read(hal::AdcChannel::Vcore, 2000);
    if (!core_raw) {
        return fail(Error::Timeout, "АЦП: канал V_CORE не відповідає");
    }
    const std::int32_t vcore_mv =
        static_cast<std::int32_t>(*core_raw) * *vdda * kVcoreDivider / kAdcFullScale;
    if (!within_tolerance(vcore_mv, kVcoreNominalMv)) {
        return fail(Error::Fail, "V_CORE поза допуском ±3%", vcore_mv, "mV");
    }

    return pass("Рейки в допуску", vcore_mv, "mV");
}

inline Outcome test_clock_pll() noexcept
{
    const auto hse = hal::measure_hse_hz(10);
    if (!hse) {
        return fail(Error::Fail, "HSE не збуджується: кварц або навантажувальні C");
    }
    const std::int32_t drift = static_cast<std::int32_t>(*hse) -
                               static_cast<std::int32_t>(kHseNominalHz);
    if (static_cast<std::uint32_t>(drift < 0 ? -drift : drift) > kHseToleranceHz) {
        return fail(Error::Fail, "Частота HSE поза грубим допуском",
                    static_cast<std::int32_t>(*hse), "Hz");
    }

    hal::pll_start();
    const Deadline lock{kPllLockTimeoutUs};
    while (!hal::pll_locked()) {
        if (lock.expired()) {
            // Саме тут звичайна прошивка вішається у while(!LOCK).
            return fail(Error::Timeout, "PLL не захопився за 5 мс");
        }
    }

    return pass("HSE збуджений, PLL захопився",
                static_cast<std::int32_t>(lock.elapsed_us()), "us");
}

}  // namespace fct
