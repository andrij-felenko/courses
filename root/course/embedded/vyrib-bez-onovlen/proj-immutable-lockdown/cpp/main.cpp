#include <cstdint>
#include <cstddef>
#include <array>
#include <expected>
#include <span>

namespace hardware::security {

enum class LockError : std::uint8_t {
    OtpDataMissingOrCorrupt,
    FlashControllerBusy,
    OptionUnlockFailed,
    WriteFailed,
    VerificationFailed
};

class FlashOptionRegisters {
private:
    static constexpr std::uintptr_t kFlashBase = 0x40022000UL;
    
    struct HardwareLayout {
        volatile std::uint32_t acr;
        volatile std::uint32_t keyr;
        volatile std::uint32_t optkeyr;
        volatile std::uint32_t sr;
        volatile std::uint32_t cr;
        volatile std::uint32_t optr;
        volatile std::uint32_t wrp1ar;
    };

    static constexpr std::uint32_t kKey1 = 0x45670123UL;
    static constexpr std::uint32_t kKey2 = 0xCDEF89ABUL;
    static constexpr std::uint32_t kOptKey1 = 0x08192A3BUL;
    static constexpr std::uint32_t kOptKey2 = 0x4C5D6E7FUL;

    static constexpr std::uint32_t kSrBusy = 1UL << 16;
    static constexpr std::uint32_t kSrWrpErr = 1UL << 4;
    static constexpr std::uint32_t kSrPgaErr = 1UL << 5;

    static constexpr std::uint32_t kCrLock = 1UL << 31;
    static constexpr std::uint32_t kCrOptLock = 1UL << 30;
    static constexpr std::uint32_t kCrOptStart = 1UL << 17;
    static constexpr std::uint32_t kCrOblLaunch = 1UL << 27;

    static constexpr std::uint8_t kRdpLevel2 = 0xCC;
    static constexpr std::uintptr_t kOtpStart = 0x1FFF7000UL;
    static constexpr std::uint32_t kOtpMagic = 0x5345414CUL; /* "SEAL" */

    static HardwareLayout& hw() noexcept {
        return *reinterpret_cast<HardwareLayout*>(kFlashBase);
    }

public:
    /* RAII-обгортка для гарантованого повторного блокування Option Bytes */
    class OptionLockGuard {
    public:
        OptionLockGuard() = default;
        ~OptionLockGuard() noexcept {
            hw().cr |= (kCrOptLock | kCrLock);
        }
        OptionLockGuard(const OptionLockGuard&) = delete;
        OptionLockGuard& operator=(const OptionLockGuard&) = delete;
    };

    static bool is_otp_provisioned() noexcept {
        auto otp = reinterpret_cast<const volatile std::uint32_t*>(kOtpStart);
        if (otp[0] != kOtpMagic) {
            return false;
        }
        std::uint32_t checksum = 0;
        for (std::size_t i = 1; i < 8; ++i) {
            checksum ^= otp[i];
        }
        return (checksum != 0 && checksum != 0xFFFFFFFFUL);
    }

    static std::expected<void, LockError> wait_ready(std::uint32_t timeout) noexcept {
        while (hw().sr & kSrBusy) {
            if (--timeout == 0) {
                return std::unexpected(LockError::FlashControllerBusy);
            }
        }
        if (hw().sr & (kSrWrpErr | kSrPgaErr)) {
            hw().sr = kSrWrpErr | kSrPgaErr;
            return std::unexpected(LockError::WriteFailed);
        }
        return {};
    }

    static std::expected<OptionLockGuard, LockError> unlock_options() noexcept {
        if (hw().cr & kCrLock) {
            hw().keyr = kKey1;
            hw().keyr = kKey2;
        }
        if (hw().cr & kCrLock) {
            return std::unexpected(LockError::OptionUnlockFailed);
        }

        if (hw().cr & kCrOptLock) {
            hw().optkeyr = kOptKey1;
            hw().optkeyr = kOptKey2;
        }
        if (hw().cr & kCrOptLock) {
            return std::unexpected(LockError::OptionUnlockFailed);
        }

        return OptionLockGuard{};
    }

    static std::expected<void, LockError> perform_factory_lockdown(
        std::uint8_t start_page, std::uint8_t end_page) noexcept 
    {
        if (!is_otp_provisioned()) {
            return std::unexpected(LockError::OtpDataMissingOrCorrupt);
        }

        auto ready = wait_ready(500000);
        if (!ready) return ready;

        auto guard = unlock_options();
        if (!guard) return std::unexpected(guard.error());

        /* Налаштування апаратного захисту діапазону сторінок від запису */
        hw().wrp1ar = (static_cast<std::uint32_t>(end_page) << 16) | start_page;

        /* Встановлення незворотного рівня RDP Level 2 */
        std::uint32_t optr = hw().optr;
        optr &= ~0xFFUL;
        optr |= kRdpLevel2;
        hw().optr = optr;

        /* Запуск запису конфігураційних бітів */
        hw().cr |= kCrOptStart;
        ready = wait_ready(500000);
        if (!ready) return ready;

        /* Перезапуск контролера з новими бітами захисту */
        hw().cr |= kCrOblLaunch;

        while (true) {
            #if defined(__GNUC__) || defined(__clang__)
            asm volatile("nop");
            #endif
        }
    }
};

} // namespace hardware::security
