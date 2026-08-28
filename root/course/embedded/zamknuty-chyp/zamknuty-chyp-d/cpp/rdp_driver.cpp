// rdp_driver.cpp — Реалізація драйвера Option Bytes на C++20
#include "rdp_driver.hpp"

namespace security {

std::expected<void, ProtectionError> ReadoutProtection::wait_ready() noexcept {
    uint32_t timeout = 500000U;
    while ((regs()->sr & SrBusyBit) != 0U) {
        if (--timeout == 0U) {
            return std::unexpected(ProtectionError::ControllerBusy);
        }
    }
    return {};
}

std::expected<void, ProtectionError> ReadoutProtection::unlock_options() noexcept {
    if ((regs()->optcr & OptcrLock) == 0U) {
        return {}; // Вже відкрито
    }

    regs()->optkeyr = OptKey1;
    regs()->optkeyr = OptKey2;

    if ((regs()->optcr & OptcrLock) != 0U) {
        return std::unexpected(ProtectionError::UnlockFailed);
    }
    return {};
}

void ReadoutProtection::lock_options() noexcept {
    regs()->optcr |= OptcrLock;
}

std::expected<RdpLevel, ProtectionError> ReadoutProtection::get_current_level() noexcept {
    const uint32_t optcr = regs()->optcr;
    const uint8_t rdp_byte = static_cast<uint8_t>((optcr & OptcrRdpMsk) >> OptcrRdpPos);

    if (rdp_byte == static_cast<uint8_t>(RdpLevel::Level0)) {
        return RdpLevel::Level0;
    }
    if (rdp_byte == static_cast<uint8_t>(RdpLevel::Level2)) {
        return RdpLevel::Level2;
    }
    return RdpLevel::Level1;
}

std::expected<void, ProtectionError> ReadoutProtection::set_level(RdpLevel target) noexcept {
    auto current = get_current_level();
    if (!current.has_value()) {
        return std::unexpected(current.error());
    }

    if (*current == RdpLevel::Level2) {
        return std::unexpected(ProtectionError::AlreadyAtLevel2);
    }

    if (*current == target) {
        return {};
    }

    auto wait_res = wait_ready();
    if (!wait_res.has_value()) return wait_res;

    auto unlock_res = unlock_options();
    if (!unlock_res.has_value()) return unlock_res;

    uint32_t optcr_val = regs()->optcr;
    optcr_val &= ~OptcrRdpMsk;
    optcr_val &= ~(3U << 2); // Скидання конфігурації BOR
    optcr_val |= (static_cast<uint32_t>(target) << OptcrRdpPos);
    optcr_val |= OptcrBorLv3; // Активація найвищого порогу BOR

    regs()->optcr = optcr_val;
    regs()->optcr |= OptcrStart;

    auto write_wait = wait_ready();
    lock_options();

    if (!write_wait.has_value()) return write_wait;

    auto verified = get_current_level();
    if (!verified.has_value() || *verified != target) {
        return std::unexpected(ProtectionError::VerificationFailed);
    }

    return {};
}

bool ReadoutProtection::is_fully_hardened() noexcept {
    auto lvl = get_current_level();
    if (!lvl.has_value()) return false;

    // Стійка до глітчингу подвійна перевірка
    const bool is_l2 = (*lvl == RdpLevel::Level2);
    volatile uint32_t token_direct  = is_l2 ? 0x5A5AA5A5U : 0x00000000U;
    volatile uint32_t token_inverse = (!is_l2) ? 0xA5A55A5AU : 0x00000000U;

    return (token_direct == 0x5A5AA5A5U) && (token_inverse == 0x00000000U);
}

} // namespace security
