#include "reset_cause.hpp"

#include <array>

#include "bitnames.hpp"
#include "trace.hpp"
#include "stm32f4xx.h"

namespace reset {
namespace {

struct Entry {
    std::uint32_t    csr_bit;
    Source           source;
    std::string_view text;
};

// Порядок навмисний: від найцікавішого для розслідування до найбуденнішого.
// PORRSTF стоїть останнім, бо після холодного старту він горить завжди
// і сам собою нічого не пояснює.
constexpr std::array kEntries{
    Entry{RCC_CSR_IWDGRSTF, Source::Iwdg, "IWDGRSTF  незалежний сторож: програма зависла"},
    Entry{RCC_CSR_WWDGRSTF, Source::Wwdg, "WWDGRSTF  віконний сторож: порушено таймінг"},
    Entry{RCC_CSR_SFTRSTF, Source::Software, "SFTRSTF   програмне скидання (SYSRESETREQ)"},
    Entry{RCC_CSR_BORRSTF, Source::Brownout, "BORRSTF   просідання живлення нижче порогу"},
    Entry{RCC_CSR_LPWRRSTF, Source::LowPower, "LPWRRSTF  збій виходу з режиму низького споживання"},
    Entry{RCC_CSR_PINRSTF, Source::Pin, "PINRSTF   зовнішній сигнал на піні NRST"},
    Entry{RCC_CSR_PORRSTF, Source::PowerOn, "PORRSTF   холодний старт (подача живлення)"},
};

// Без function-local static: у прошивці без підтримки динамічної ініціалізації
// сторожі Meyers-синглтона зайві, а стан тут тривіальний.
constinit Causes g_causes{};
constinit bool   g_captured = false;

} // namespace

void Causes::print() const
{
    trace::out.line("RCC->CSR=", trace::Hex{raw_csr_});

    if (empty()) {
        // Жодного відомого біта: найчастіше прапорці вже стер чужий стартовий код.
        trace::out.line("причина скидання: невідома (прапорці вже стерті)");
        return;
    }

    for (const Entry& entry : kEntries) {
        if (has(entry.source)) {
            trace::out.line("  * ", entry.text);
        }
    }
}

const Causes& capture()
{
    if (g_captured) {
        return g_causes; // прапорці вже стерті — апаратуру перепитувати марно
    }

    const std::uint32_t csr = RCC->CSR;

    Source sources = Source::None;
    for (const Entry& entry : kEntries) {
        if ((csr & entry.csr_bit) != 0U) {
            sources |= entry.source;
        }
    }

    // Стираємо липкі прапорці одразу. Інакше PORRSTF від найпершого ввімкнення
    // на заводі житиме роками й змішається з причиною завтрашньої аварії в полі.
    RCC->CSR |= RCC_CSR_RMVF;
    __DSB();

    g_causes    = Causes{sources, csr};
    g_captured  = true;
    return g_causes;
}

} // namespace reset
