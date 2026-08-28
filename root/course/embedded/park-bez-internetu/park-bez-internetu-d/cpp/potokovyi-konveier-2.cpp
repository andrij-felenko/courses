/* Ідіоматична C++ версія валідатора з використанням std::span та std::expected */
#include <span>
#include <expected>
#include <cstdint>

enum class PackageError { InvalidSignature, RollbackBlocked, HardwareMismatch };

std::expected<void, PackageError> validatePackage(
    const UpkgHeader& hdr,
    std::span<const uint8_t, 32> root_public_key,
    uint32_t current_efuse_version,
    uint16_t my_hardware_id) 
{
    if (hdr.target_hw_id != my_hardware_id) {
        return std::unexpected(PackageError::HardwareMismatch);
    }
    if (hdr.version_monotonic < current_efuse_version) {
        return std::unexpected(PackageError::RollbackBlocked);
    }
    
    auto signed_bytes = std::span<const uint8_t>(
        reinterpret_cast<const uint8_t*>(&hdr), sizeof(UpkgHeader) - 64
    );
    
    if (!ed25519_verify(signed_bytes, hdr.signature, root_public_key)) {
        return std::unexpected(PackageError::InvalidSignature);
    }
    
    return {};
}
