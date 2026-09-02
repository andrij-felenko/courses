#pragma once

#include <cstdint>
#include <expected>
#include <string_view>

// Конфігурація як значення: розкладка слова OPTR, порівняння й правила
// безпечних переходів. Тут немає жодного звертання до заліза, тому все
// це рахується на етапі компіляції — і перевіряється static_assert'ами.
namespace optbytes {

enum class Rdp : std::uint8_t {
    Open      = 0xAA, // відкритий доступ SWD
    Protected = 0xBB, // Flash закрита, зняття захисту = Mass Erase
    Sealed    = 0xCC, // незворотне вимкнення зневадження
};

enum class Bor : std::uint8_t {
    Level0 = 0, // ~1.7 В
    Level1 = 1, // ~2.0 В
    Level2 = 2, // ~2.2 В
    Level3 = 3, // ~2.5 В
    Level4 = 4, // ~2.8 В
};

enum class Watchdog : std::uint8_t {
    Hardware = 0, // лічильник біжить з першого такту після подачі живлення
    Software = 1,
};

enum class NrstMode : std::uint8_t {
    Reserved        = 0,
    ResetInput      = 1,
    Gpio            = 2, // ніжка скидання стала звичайним GPIO
    ResetInputOutput = 3,
};

enum class Boot : std::uint8_t {
    FromPin = 0, // страпінг у системний завантажувач працює
    Fixed   = 1, // ніжку BOOT0 вимкнено
};

struct Config {
    Rdp rdp{Rdp::Open};
    Bor bor{Bor::Level0};
    Watchdog iwdg{Watchdog::Software};
    NrstMode nrst{NrstMode::ResetInputOutput};
    Boot boot{Boot::FromPin};

    bool operator==(const Config&) const = default;
};

// Розкладка полів FLASH_OPTR
inline constexpr std::uint32_t kRdpMask   = 0x0000'00FFUL;
inline constexpr std::uint32_t kBorShift  = 8;
inline constexpr std::uint32_t kBorMask   = 0x7UL << kBorShift;
inline constexpr std::uint32_t kIwdgSw    = 1UL << 16;
inline constexpr std::uint32_t kSwBoot0   = 1UL << 26;
inline constexpr std::uint32_t kNBoot0    = 1UL << 27;
inline constexpr std::uint32_t kNrstShift = 28;
inline constexpr std::uint32_t kNrstMask  = 0x3UL << kNrstShift;

// Робоча точка плати: 170 МГц із вбудованої Flash вимагають щонайменше 2.8 В.
inline constexpr Bor kMinBorForMaxClock = Bor::Level4;

constexpr Config decode(std::uint32_t optr) noexcept
{
    const auto rdp_byte = static_cast<std::uint8_t>(optr & kRdpMask);

    Config cfg{};
    // Усе, що не 0xAA і не 0xCC, апаратно означає Level 1. Нормалізуємо,
    // інакше порівняння «те саме?» брехало б на чипі з RDP = 0x00.
    if (rdp_byte == static_cast<std::uint8_t>(Rdp::Open)) {
        cfg.rdp = Rdp::Open;
    } else if (rdp_byte == static_cast<std::uint8_t>(Rdp::Sealed)) {
        cfg.rdp = Rdp::Sealed;
    } else {
        cfg.rdp = Rdp::Protected;
    }

    cfg.bor  = static_cast<Bor>((optr & kBorMask) >> kBorShift);
    cfg.iwdg = (optr & kIwdgSw) ? Watchdog::Software : Watchdog::Hardware;
    cfg.nrst = static_cast<NrstMode>((optr & kNrstMask) >> kNrstShift);
    cfg.boot = (optr & kSwBoot0) ? Boot::FromPin : Boot::Fixed;
    return cfg;
}

// Чужі поля слова (WWDG_SW, nRST_STOP, DBANK…) переносяться без змін:
// сліпе обнулення зламало б налаштування, яких ця стаття не стосується.
constexpr std::uint32_t encode(const Config& cfg, std::uint32_t optr) noexcept
{
    optr &= ~(kRdpMask | kBorMask | kIwdgSw | kNrstMask);
    optr |= static_cast<std::uint32_t>(cfg.rdp) & kRdpMask;
    optr |= (static_cast<std::uint32_t>(cfg.bor) << kBorShift) & kBorMask;
    optr |= (static_cast<std::uint32_t>(cfg.nrst) << kNrstShift) & kNrstMask;

    if (cfg.iwdg == Watchdog::Software) {
        optr |= kIwdgSw;
    }

    if (cfg.boot == Boot::FromPin) {
        optr |= kSwBoot0; // nBOOT0 у цьому режимі не має значення
    } else {
        optr &= ~kSwBoot0;
        optr |= kNBoot0;
    }
    return optr;
}

enum class Policy : std::uint8_t {
    AlreadySealed,     // чип уже в Level 2
    WouldSealForever,  // просять записати 0xCC
    WouldMassErase,    // зняття захисту стерло б усю Flash разом із цим кодом
    BorTooLow,         // поріг нижчий за потрібний робочій частоті
    ResetPinLost,      // ніжка скидання перестала б бути скиданням
    BootPinLost,       // страпінг BOOT0 перестав би працювати
};

constexpr std::string_view describe(Policy p) noexcept
{
    switch (p) {
    case Policy::AlreadySealed:    return "політика: чип уже в RDP Level 2";
    case Policy::WouldSealForever: return "політика: запис RDP Level 2 незворотний";
    case Policy::WouldMassErase:   return "політика: зняття захисту стерло б усю Flash";
    case Policy::BorTooLow:        return "політика: поріг BOR замалий для робочої частоти";
    case Policy::ResetPinLost:     return "політика: ніжка скидання мусить лишитися скиданням";
    case Policy::BootPinLost:      return "політика: страпінг BOOT0 мусить лишитися живим";
    }
    return "політика: невідоме порушення";
}

// Єдине місце, де живуть правила «як не зробити цеглинку».
constexpr std::expected<void, Policy> check(const Config& current,
                                            const Config& wanted) noexcept
{
    if (current.rdp == Rdp::Sealed) {
        return std::unexpected(Policy::AlreadySealed);
    }
    if (wanted.rdp == Rdp::Sealed) {
        return std::unexpected(Policy::WouldSealForever);
    }
    if (current.rdp != Rdp::Open && wanted.rdp == Rdp::Open) {
        return std::unexpected(Policy::WouldMassErase);
    }
    if (wanted.bor < kMinBorForMaxClock) {
        return std::unexpected(Policy::BorTooLow);
    }
    if (wanted.nrst == NrstMode::Gpio || wanted.nrst == NrstMode::Reserved) {
        return std::unexpected(Policy::ResetPinLost);
    }
    if (wanted.boot == Boot::Fixed) {
        return std::unexpected(Policy::BootPinLost);
    }
    return {};
}

// Значення заводського чипа G4: RDP = 0xAA, BOR 0, IWDG програмний,
// NRST вхід/вихід, BOOT0 з ніжки.
inline constexpr std::uint32_t kFactoryOptr = 0x3FEF'F8AAUL;

static_assert(decode(kFactoryOptr).rdp == Rdp::Open);
static_assert(decode(kFactoryOptr).boot == Boot::FromPin);
static_assert(decode(kFactoryOptr).iwdg == Watchdog::Software);
static_assert(encode(decode(kFactoryOptr), kFactoryOptr) == kFactoryOptr,
              "розкладання й збирання слова OPTR мають бути взаємно оберненими");

// Правила політики перевіряються ще до того, як код побачить залізо.
static_assert(check(decode(kFactoryOptr),
                    Config{Rdp::Sealed, Bor::Level4, Watchdog::Software,
                           NrstMode::ResetInputOutput, Boot::FromPin})
                  .error() == Policy::WouldSealForever);
static_assert(check(decode(kFactoryOptr),
                    Config{Rdp::Protected, Bor::Level4, Watchdog::Software,
                           NrstMode::Gpio, Boot::FromPin})
                  .error() == Policy::ResetPinLost);
static_assert(check(decode(kFactoryOptr),
                    Config{Rdp::Protected, Bor::Level4, Watchdog::Software,
                           NrstMode::ResetInputOutput, Boot::FromPin})
                  .has_value());

} // namespace optbytes
