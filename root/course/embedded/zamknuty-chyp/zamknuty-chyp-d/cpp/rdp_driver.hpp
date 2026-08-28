// rdp_driver.hpp — Драйвер апаратного захисту Option Bytes (Modern C++20)
#pragma once

#include <cstdint>
#include <concepts>
#include <expected>
#include <span>

namespace security {

enum class RdpLevel : uint8_t {
    Level0 = 0xAA, // Відкрито для налагодження
    Level1 = 0x55, // Захищено від читання
    Level2 = 0xCC  // Незворотне блокування кремнію
};

enum class ProtectionError : uint8_t {
    ControllerBusy,
    UnlockFailed,
    WriteError,
    VerificationFailed,
    AlreadyAtLevel2
};

class ReadoutProtection {
public:
    ReadoutProtection() = delete;

    [[nodiscard]] static std::expected<RdpLevel, ProtectionError> get_current_level() noexcept;
    [[nodiscard]] static std::expected<void, ProtectionError> set_level(RdpLevel target) noexcept;
    [[nodiscard]] static bool is_fully_hardened() noexcept;

private:
    static constexpr uintptr_t FlashBase = 0x40023C00U;
    
    struct FlashRegisters {
        volatile uint32_t acr;
        volatile uint32_t keyr;
        volatile uint32_t optkeyr;
        volatile uint32_t sr;
        volatile uint32_t cr;
        volatile uint32_t optcr;
    };

    static inline auto* regs() noexcept {
        return reinterpret_cast<FlashRegisters*>(FlashBase);
    }

    static constexpr uint32_t OptKey1 = 0x08192A3BU;
    static constexpr uint32_t OptKey2 = 0x4C5D6E7FU;
    
    static constexpr uint32_t SrBusyBit   = 1U << 16;
    static constexpr uint32_t OptcrLock   = 1U << 0;
    static constexpr uint32_t OptcrStart  = 1U << 1;
    static constexpr uint32_t OptcrBorLv3 = 0U << 2; // Максимальний поріг BOR
    static constexpr uint32_t OptcrRdpPos = 8U;
    static constexpr uint32_t OptcrRdpMsk = 0xFFU << OptcrRdpPos;

    [[nodiscard]] static std::expected<void, ProtectionError> wait_ready() noexcept;
    [[nodiscard]] static std::expected<void, ProtectionError> unlock_options() noexcept;
    static void lock_options() noexcept;
};

} // namespace security
