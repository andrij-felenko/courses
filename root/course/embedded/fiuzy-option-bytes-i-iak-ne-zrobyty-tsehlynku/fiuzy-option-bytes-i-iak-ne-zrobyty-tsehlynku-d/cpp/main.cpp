#include <cstdint>
#include <expected>
#include <span>

namespace mcu::flash {

/* Регістри контролера Flash */
struct FlashRegisters {
    volatile uint32_t ACR;
    volatile uint32_t reserved0;
    volatile uint32_t KEYR;
    volatile uint32_t OPTKEYR;
    volatile uint32_t SR;
    volatile uint32_t CR;
    volatile uint32_t reserved1[2];
    volatile uint32_t OPTR;
};

inline auto* const regs = reinterpret_cast<FlashRegisters*>(0x40022000UL);

/* Бітові маски та константи */
enum class CrBits : uint32_t {
    Lock      = 1UL << 31,
    OptLock   = 1UL << 30,
    OblLaunch = 1UL << 27,
    OptStart  = 1UL << 17
};

enum class SrBits : uint32_t {
    Busy      = 1UL << 16,
    PgsErr    = 1UL << 7,
    WrpErr    = 1UL << 4
};

enum class RdpLevel : uint8_t {
    Level0 = 0xAA, // Відкритий режим зневадження
    Level1 = 0xBB  // Захист пам'яті (Level 2 навмисно виключено з enum)
};

enum class FlashError {
    BusyTimeout,
    UnlockFailed,
    WriteFailed
};

/* RAII-обгортка для безпечного блокування / розблокування Flash */
class OptionBytesGuard {
public:
    OptionBytesGuard() = default;

    [[nodiscard]] bool unlock() noexcept {
        if (!wait_ready()) return false;

        if (regs->CR & static_cast<uint32_t>(CrBits::Lock)) {
            regs->KEYR = 0x45670123UL;
            regs->KEYR = 0xCDEF89ABUL;
            if (regs->CR & static_cast<uint32_t>(CrBits::Lock)) return false;
        }

        if (regs->CR & static_cast<uint32_t>(CrBits::OptLock)) {
            regs->OPTKEYR = 0x08192A3BUL;
            regs->OPTKEYR = 0x4C5D6E7FUL;
            if (regs->CR & static_cast<uint32_t>(CrBits::OptLock)) return false;
        }

        unlocked_ = true;
        return true;
    }

    ~OptionBytesGuard() noexcept {
        if (unlocked_) {
            regs->CR |= (static_cast<uint32_t>(CrBits::OptLock) |
                         static_cast<uint32_t>(CrBits::Lock));
        }
    }

    OptionBytesGuard(const OptionBytesGuard&) = delete;
    OptionBytesGuard& operator=(const OptionBytesGuard&) = delete;

    static bool wait_ready(uint32_t timeout_cycles = 1'000'000UL) noexcept {
        while ((regs->SR & static_cast<uint32_t>(SrBits::Busy)) && --timeout_cycles) {
            asm volatile("nop");
        }
        return timeout_cycles > 0;
    }

private:
    bool unlocked_{false};
};

/* Безпечна функція зміни рівня RDP */
[[nodiscard]] std::expected<void, FlashError> set_rdp(RdpLevel level) noexcept {
    OptionBytesGuard guard;
    if (!guard.unlock()) {
        return std::unexpected(FlashError::UnlockFailed);
    }

    // Очищення прапорців помилок
    regs->SR = static_cast<uint32_t>(SrBits::PgsErr) | static_cast<uint32_t>(SrBits::WrpErr);

    // Модифікація регістру
    uint32_t optr = regs->OPTR;
    optr &= ~0xFFUL;
    optr |= static_cast<uint32_t>(level);
    regs->OPTR = optr;

    // Старт програмування
    regs->CR |= static_cast<uint32_t>(CrBits::OptStart);

    if (!OptionBytesGuard::wait_ready()) {
        return std::unexpected(FlashError::BusyTimeout);
    }

    if (regs->SR & (static_cast<uint32_t>(SrBits::PgsErr) | static_cast<uint32_t>(SrBits::WrpErr))) {
        return std::unexpected(FlashError::WriteFailed);
    }

    // Апаратне завантаження нових опцій
    regs->CR |= static_cast<uint32_t>(CrBits::OblLaunch);

    return {};
}

} // namespace mcu::flash
