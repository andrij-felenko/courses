#include <cstdint>
#include <string_view>

#include "flash_options.hpp"
#include "mmio.hpp"

// Сценарій випуску: прошивка на вже змонтованій платі один раз доводить
// Option Bytes до потрібного стану й голосно каже, чому саме не стала цього
// робити. Канал діагностики — ITM: він живий, доки живий налагоджувач.
namespace trace {
namespace {

volatile std::uint32_t& stim0_status = *reinterpret_cast<volatile std::uint32_t*>(0xE000'0000UL);
volatile std::uint8_t&  stim0_byte   = *reinterpret_cast<volatile std::uint8_t*>(0xE000'0000UL);
volatile std::uint32_t& itm_ter      = *reinterpret_cast<volatile std::uint32_t*>(0xE000'0E00UL);
volatile std::uint32_t& core_demcr   = *reinterpret_cast<volatile std::uint32_t*>(0xE000'EDFCUL);

constexpr std::uint32_t kTrcEna = 1UL << 24;

void put(char c) noexcept
{
    // Без підключеного налагоджувача ITM не приймає нічого, і чекати
    // на готовність порту означало б зависнути назавжди.
    if ((core_demcr & kTrcEna) == 0UL || (itm_ter & 1UL) == 0UL) {
        return;
    }
    for (std::uint32_t guard = 100'000UL; stim0_status == 0UL; --guard) {
        if (guard == 0UL) {
            return;
        }
    }
    stim0_byte = static_cast<std::uint8_t>(c);
}

} // namespace

void write(std::string_view text) noexcept
{
    for (char c : text) {
        put(c);
    }
}

void hex32(std::uint32_t value) noexcept
{
    constexpr std::string_view digits = "0123456789ABCDEF";
    write("0x");
    for (int shift = 28; shift >= 0; shift -= 4) {
        put(digits[(value >> shift) & 0xFUL]);
    }
}

} // namespace trace

namespace {

using namespace optbytes;

std::string_view rdp_name(Rdp v) noexcept
{
    switch (v) {
    case Rdp::Open:      return "Level 0 (0xAA)";
    case Rdp::Protected: return "Level 1";
    case Rdp::Sealed:    return "Level 2 (0xCC)";
    }
    return "?";
}

std::string_view bor_name(Bor v) noexcept
{
    switch (v) {
    case Bor::Level0: return "BOR 0 (~1.7 В)";
    case Bor::Level1: return "BOR 1 (~2.0 В)";
    case Bor::Level2: return "BOR 2 (~2.2 В)";
    case Bor::Level3: return "BOR 3 (~2.5 В)";
    case Bor::Level4: return "BOR 4 (~2.8 В)";
    }
    return "BOR ?";
}

std::string_view nrst_name(NrstMode v) noexcept
{
    switch (v) {
    case NrstMode::ResetInput:       return "NRST вхід скидання";
    case NrstMode::Gpio:             return "NRST як GPIO";
    case NrstMode::ResetInputOutput: return "NRST вхід/вихід скидання";
    case NrstMode::Reserved:         return "NRST зарезервовано";
    }
    return "NRST ?";
}

void dump(std::string_view label, const Config& cfg) noexcept
{
    trace::write(label);
    trace::write(": ");
    trace::write(rdp_name(cfg.rdp));
    trace::write(" | ");
    trace::write(bor_name(cfg.bor));
    trace::write(cfg.iwdg == Watchdog::Software ? " | IWDG програмний" : " | IWDG апаратний");
    trace::write(" | ");
    trace::write(nrst_name(cfg.nrst));
    trace::write(cfg.boot == Boot::FromPin ? " | BOOT0 з ніжки\n" : " | BOOT0 з опції\n");
}

// Цільова конфігурація серійного виробу. Кожне поле тут — рішення, яке
// в разі помилки коштує партії плат.
constexpr Config kWanted{
    .rdp  = Rdp::Protected,             // прошивку закрито, чип іще можна стерти
    .bor  = Bor::Level4,                // 2.8 В: нижче Flash бреше на 170 МГц
    .iwdg = Watchdog::Software,         // апаратний старт WDG зациклив би довгу ініціалізацію
    .nrst = NrstMode::ResetInputOutput, // ніжка скидання лишається скиданням
    .boot = Boot::FromPin,              // страпінг у системний завантажувач лишається
};

static_assert(check(decode(kFactoryOptr), kWanted).has_value(),
              "цільова конфігурація мусить проходити власну політику");

} // namespace

int main()
{
    trace::write("\n== Option Bytes ==\n");
    trace::write("сире слово OPTR: ");
    trace::hex32(hal::flash().OPTR);
    trace::write("\n");

    const Config current = OptionBytes::read();
    dump("поточна", current);
    dump("бажана ", kWanted);

    if (current == kWanted) {
        // Службова сторінка має свій ресурс перезапису, та й кожен зайвий
        // запис — це ще один шанс спіймати просідання живлення.
        trace::write("збіг: у Flash не пишемо нічого\n");
    } else if (auto result = OptionBytes::apply(kWanted); !result) {
        // Успішний шлях сюди не повертається — чип уже перезавантажився.
        trace::write("не застосовано: ");
        trace::write(describe(result.error()));
        trace::write("\n");
    }

    // Свідомо не йдемо ні в сон, ні в переналаштування PA13/PA14: саме ці
    // два рухи в перших рядках main() і залишають ST-Link без відповіді.
    for (;;) {
    }
}
