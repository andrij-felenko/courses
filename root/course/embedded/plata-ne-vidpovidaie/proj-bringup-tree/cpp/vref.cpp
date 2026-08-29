// Фаза 4: реальна напруга VDDA через внутрішнє опорне джерело.
// Джерело стабільне, а сходинка АЦП пропорційна живленню: чим меншим кодом
// виміряне незмінне VREFINT, тим вища напруга на VDDA.
#include "bringup.hpp"

namespace bringup {
namespace {

namespace adc = mmio::adc1;
namespace rcc = mmio::rcc;

constexpr std::uint32_t nominal_vref_mv = 1210U;   // типове VREFINT для F4
constexpr std::uint32_t full_scale = 4095U;        // 12 біт
constexpr std::uint32_t cal_vdda_mv = 3300U;       // напруга зняття константи
constexpr std::uint32_t stabilization_us = 20U;    // tSTAB після ADON
constexpr std::uint32_t eoc_tries = 100'000U;

[[nodiscard]] std::uint16_t read_factory_cal() noexcept
{
    return *reinterpret_cast<const volatile std::uint16_t*>(adc::vrefint_cal);
}

}  // namespace

Result<SupplyMeasurement> measure_vdda() noexcept
{
    rcc::apb2enr::set(rcc::adc1en);
    static_cast<void>(rcc::apb2enr::read());

    // Дільник /4 дає 4 МГц при PCLK2 16 МГц; TSVREFE підключає внутрішній
    // канал опорного джерела до мультиплексора входів.
    adc::ccr::modify(adc::adcpre_mask, adc::adcpre_div4 | adc::tsvrefe);

    // Канал 17 має високий внутрішній опір і потребує щонайменше 10 мкс
    // вибірки, тому беремо максимальні 480 тактів (поле 0b111).
    adc::smpr1::set(7U << ((adc::channel_vrefint - 10U) * 3U));

    adc::cr1::write(0U);   // 12 біт, без сканування й переривань
    adc::sqr1::write(0U);  // послідовність з одного каналу
    adc::sqr3::write(adc::channel_vrefint);

    adc::cr2::set(adc::adon);
    mmio::delay_us(stabilization_us);

    adc::sr::write(0U);
    adc::cr2::set(adc::swstart);

    const bool converted = mmio::wait_until([] { return adc::sr::any(adc::eoc); }, eoc_tries);
    const std::uint16_t raw = static_cast<std::uint16_t>(adc::dr::read() & 0x0FFFU);
    adc::cr2::clear(adc::adon);

    if (!converted || raw == 0U) {
        // Нуль на стабільному джерелі означає мертву аналогову частину:
        // обірвану VDDA після феритової бусини або пробитий вхід.
        return std::unexpected(Error::adc_timeout);
    }

    SupplyMeasurement measurement{};
    measurement.vrefint_raw = raw;
    measurement.factory_cal = read_factory_cal();

    if (measurement.factory_cal != 0U && measurement.factory_cal != 0xFFFFU) {
        // VDDA = 3.30 В · ADC_CAL / ADC_DATA, рахуємо в мілівольтах цілими.
        measurement.vdda_mv = (cal_vdda_mv * measurement.factory_cal) / raw;
        return measurement;
    }

    // Комірку не запрограмовано (буває на F405/F407): лишається типове
    // значення джерела, і точність падає з одного відсотка до кількох.
    measurement.factory_cal = 0U;
    measurement.nominal_fallback = true;
    measurement.vdda_mv = (full_scale * nominal_vref_mv) / raw;
    return measurement;
}

}  // namespace bringup
