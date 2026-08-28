#include <iostream>
#include <array>
#include <span>
#include <string_view>
#include <cstdint>
#include <algorithm>

namespace eol::boot {

enum class BootMode {
    FactoryLocked,
    CommunityUnlocked,
    AuthFailure
};

struct UnlockToken {
    static constexpr uint32_t MAGIC = 0x554E4C4B; // 'UNLK'

    uint32_t magic{0};
    std::array<uint32_t, 4> device_uid{};
    std::array<uint8_t, 64> signature_token{};
    uint32_t flags{0};

    [[nodiscard]] bool is_valid_for(std::span<const uint32_t, 4> expected_uid) const noexcept {
        if (magic != MAGIC) {
            return false;
        }
        if (!std::equal(device_uid.begin(), device_uid.end(), expected_uid.begin())) {
            return false;
        }
        return signature_token[0] != 0x00;
    }
};

class BootController {
public:
    static constexpr uint32_t HW_EFUSE_SECURE_BOOT_MASK = (1U << 0);
    static constexpr uint32_t HW_EFUSE_JTAG_DISABLE_MASK = (1U << 1);

    explicit BootController(uint32_t efuse_val, std::span<const uint32_t, 4> uid)
        : efuse_val_(efuse_val),
          fit_signature_enforce_((efuse_val & HW_EFUSE_SECURE_BOOT_MASK) != 0),
          allow_external_boot_(!fit_signature_enforce_) {
        std::copy(uid.begin(), uid.end(), device_uid_.begin());
    }

    [[nodiscard]] BootMode process_eol_transition(const UnlockToken* token = nullptr) noexcept {
        if ((efuse_val_ & HW_EFUSE_SECURE_BOOT_MASK) == 0) {
            fit_signature_enforce_ = false;
            allow_external_boot_ = true;
            return BootMode::CommunityUnlocked;
        }

        if (token != nullptr && token->is_valid_for(device_uid_)) {
            fit_signature_enforce_ = false;
            allow_external_boot_ = true;
            std::cout << "[BOOT] Авторизоване розблокування EOL успішне. Захист FIT деактивовано.\n";
            return BootMode::CommunityUnlocked;
        }

        std::cout << "[BOOT] Апаратний Secure Boot активний. Потрібен дійсний підпис вендора.\n";
        return BootMode::FactoryLocked;
    }

    [[nodiscard]] bool is_fit_signature_enforced() const noexcept { return fit_signature_enforce_; }
    [[nodiscard]] bool is_external_boot_allowed() const noexcept { return allow_external_boot_; }

private:
    uint32_t efuse_val_{0};
    std::array<uint32_t, 4> device_uid_{};
    bool fit_signature_enforce_{true};
    bool allow_external_boot_{false};
};

} // namespace eol::boot
