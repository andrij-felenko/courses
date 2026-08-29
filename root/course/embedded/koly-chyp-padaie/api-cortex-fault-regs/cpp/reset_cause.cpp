#include "reset_cause.hpp"

#include "trace.hpp"

#include <array>

namespace reset {
namespace {

constexpr std::array k_flags = std::to_array<trace::Flag>({
    { RCC_CSR_LPWRRSTF, "LPWRRSTF", "скидання з режиму низького споживання (Standby/Stop)" },
    { RCC_CSR_WWDGRSTF, "WWDGRSTF", "віконний сторож: оновлення поза дозволеним вікном" },
    { RCC_CSR_IWDGRSTF, "IWDGRSTF", "незалежний сторож: таймаут, код завис" },
    { RCC_CSR_SFTRSTF,  "SFTRSTF",  "програмне скидання (SYSRESETREQ / NVIC_SystemReset)" },
    { RCC_CSR_PORRSTF,  "PORRSTF",  "подача живлення або провал нижче порогу POR/PDR" },
    { RCC_CSR_PINRSTF,  "PINRSTF",  "зовнішній низький рівень на виводі NRST" },
    { RCC_CSR_BORRSTF,  "BORRSTF",  "детектор brown-out: напруга просіла нижче порогу" },
});

constexpr std::uint32_t k_all_causes =
    RCC_CSR_LPWRRSTF | RCC_CSR_WWDGRSTF | RCC_CSR_IWDGRSTF | RCC_CSR_SFTRSTF |
    RCC_CSR_PORRSTF  | RCC_CSR_PINRSTF  | RCC_CSR_BORRSTF;

}  // namespace

Status::Status(std::uint32_t raw)
    : raw_{raw}
    , causes_{static_cast<Cause>(raw & k_all_causes)}
{
}

Status Status::capture()
{
    const std::uint32_t raw = RCC->CSR;

    RCC->CSR |= RCC_CSR_RMVF;
    // RMVF самоочищається апаратно; знімаємо явно, щоб наступне читання CSR
    // не показувало слід власного запису.
    RCC->CSR &= ~RCC_CSR_RMVF;

    return Status{raw};
}

bool Status::hung() const
{
    return any(causes_ & (Cause::independent_wdt | Cause::window_wdt));
}

bool Status::cold() const
{
    return any(causes_ & (Cause::power_on | Cause::brown_out));
}

bool Status::requested() const
{
    return any(causes_ & Cause::software);
}

void Status::report() const
{
    trace::out() << "Причина скидання:\n";
    trace::reg("RCC->CSR", raw_);

    if (trace::print_flags(k_flags, raw_) == 0) {
        // Порожній CSR — не помилка: прапорці міг стерти завантажувач, або
        // ядро підняв відладчик без апаратного скидання.
        trace::out() << "    * жодного прапорця: CSR уже очищено раніше\n";
    }

    // Кілька бітів стоять одночасно доволі часто: PORRSTF і PINRSTF приходять
    // парою, бо внутрішній супервізор сам смикає лінію NRST. Тому судимо за
    // найсильнішим джерелом, а не за першим знайденим.
    if (hung()) {
        trace::out() << "  => попередній прогін ЗАВИС (сторож), шукай нескінченний цикл\n";
    } else if (cold()) {
        trace::out() << "  => холодний старт: вміст RAM недійсний\n";
    } else if (requested()) {
        trace::out() << "  => перезапуск замовила сама прошивка\n";
    }
}

}  // namespace reset
