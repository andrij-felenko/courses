#include "flash_options.hpp"

#include "mmio.hpp"
#include "supply.hpp"

namespace optbytes {
namespace {

// Скільки холостих обертів чекаємо зняття BSY. Запис службової сторінки
// триває одиниці мілісекунд; мільйон обертів — із запасом на будь-якій
// частоті ядра й водночас гарантія, що ми не зависнемо назавжди.
constexpr std::uint32_t kTimeoutLoops = 1'000'000UL;

// Нижче цього порога запис не починаємо — рівно той сценарій, у якому
// комірка лишається в проміжному стані й чип більше не стартує.
constexpr supply::Threshold kWriteThreshold = supply::Threshold::V2_9;

[[nodiscard]] bool wait_ready() noexcept
{
    for (std::uint32_t guard = kTimeoutLoops; guard != 0UL; --guard) {
        if (!hal::flash_busy()) {
            return true;
        }
    }
    return false;
}

void clear_errors() noexcept
{
    // прапорці помилок скидаються записом одиниці
    hal::flash().SR = hal::kFlashSrErrors | hal::raw(hal::FlashSr::Eop);
}

void spin(std::uint32_t loops) noexcept
{
    for (volatile std::uint32_t i = 0; i < loops; ++i) {
    }
}

} // namespace

// Розблокування живе рівно стільки, скільки триває операція: вихід із будь-якої
// гілки — це виклик деструктора, а не забутий FLASH->CR |= LOCK у кінці функції.
class OptionBytes::Session {
public:
    Session() noexcept
    {
        if (!wait_ready()) {
            return;
        }

        auto& flash = hal::flash();

        // Крок 1: LOCK основного контролера. Поки він стоїть, OPTLOCK
        // не знімається взагалі.
        if ((flash.CR & hal::raw(hal::FlashCr::Lock)) != 0UL) {
            flash.KEYR = hal::kFlashKey1;
            flash.KEYR = hal::kFlashKey2;
            if ((flash.CR & hal::raw(hal::FlashCr::Lock)) != 0UL) {
                return;
            }
        }

        // Крок 2: окремі ключі на сектор Option Bytes.
        if ((flash.CR & hal::raw(hal::FlashCr::OptLock)) != 0UL) {
            flash.OPTKEYR = hal::kOptKey1;
            flash.OPTKEYR = hal::kOptKey2;
            if ((flash.CR & hal::raw(hal::FlashCr::OptLock)) != 0UL) {
                return;
            }
        }

        unlocked_ = true;
    }

    ~Session() noexcept
    {
        hal::flash().CR |= hal::raw(hal::FlashCr::OptLock);
        hal::flash().CR |= hal::raw(hal::FlashCr::Lock);
    }

    Session(const Session&) = delete;
    Session& operator=(const Session&) = delete;

    [[nodiscard]] bool unlocked() const noexcept { return unlocked_; }

private:
    bool unlocked_{false};
};

Config OptionBytes::read() noexcept
{
    return decode(hal::flash().OPTR);
}

std::expected<void, Error> OptionBytes::apply(const Config& wanted) noexcept
{
    const Config current = read();

    if (auto verdict = check(current, wanted); !verdict) {
        return std::unexpected(Error{verdict.error()});
    }

    {
        supply::Monitor monitor{kWriteThreshold};
        if (!monitor.vdd_above_threshold()) {
            return std::unexpected(Error{Hardware::SupplyTooLow});
        }
    }

    if (!wait_ready()) {
        return std::unexpected(Error{Hardware::BusyTimeout});
    }
    clear_errors();

    Session session;
    if (!session.unlocked()) {
        return std::unexpected(Error{Hardware::UnlockRejected});
    }

    auto& flash = hal::flash();
    flash.OPTR = encode(wanted, flash.OPTR);
    flash.CR |= hal::raw(hal::FlashCr::OptStart);

    if (!wait_ready()) {
        return std::unexpected(Error{Hardware::BusyTimeout});
    }

    if ((flash.SR & hal::kFlashSrErrors) != 0UL) {
        clear_errors();
        return std::unexpected(Error{Hardware::ProgrammingError});
    }
    flash.SR = hal::raw(hal::FlashSr::Eop);

    // Звірка: розбіжність означає напівзаписану комірку, а далі йти не можна.
    if (read() != wanted) {
        return std::unexpected(Error{Hardware::VerifyMismatch});
    }

    // OBL_LAUNCH приймається лише поки OPTLOCK знятий, тому Session іще жива.
    flash.CR |= hal::raw(hal::FlashCr::OblLaunch);
    spin(kTimeoutLoops);

    return std::unexpected(Error{Hardware::ReloadStalled});
}

std::string_view describe(Hardware error) noexcept
{
    switch (error) {
    case Hardware::SupplyTooLow:     return "живлення: VDD нижче порога запису";
    case Hardware::BusyTimeout:      return "контролер Flash не звільнив BSY";
    case Hardware::UnlockRejected:   return "ключі не зняли блокування";
    case Hardware::ProgrammingError: return "апаратна помилка запису";
    case Hardware::VerifyMismatch:   return "записане не збіглося з бажаним";
    case Hardware::ReloadStalled:    return "записано, але OBL_LAUNCH не скинув чип";
    }
    return "невідома апаратна відмова";
}

std::string_view describe(const Error& error) noexcept
{
    return std::visit([](auto code) { return describe(code); }, error);
}

} // namespace optbytes
