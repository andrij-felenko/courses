/* Ідіоматична C++ перевірка апаратних обмежень та монотонної версії */
#include <cstdint>
#include <expected>

enum class HardwareValidationError : uint8_t {
    TargetMismatch,
    RollbackBlocked
};

[[nodiscard]] constexpr std::expected<void, HardwareValidationError>
validateHardwareConstraints(uint16_t target_id, uint32_t package_version,
                            uint16_t device_id, uint32_t current_efuse_version) noexcept {
    if (target_id != device_id) {
        return std::unexpected(HardwareValidationError::TargetMismatch);
    }
    if (package_version < current_efuse_version) {
        return std::unexpected(HardwareValidationError::RollbackBlocked);
    }
    return {};
}
