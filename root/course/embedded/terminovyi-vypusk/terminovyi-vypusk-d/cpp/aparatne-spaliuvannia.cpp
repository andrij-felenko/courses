#include "emergency_fw_header.hpp"
#include <cstdint>

extern "C" uint32_t hw_efuse_read_security_version();
extern "C" bool hw_efuse_burn_security_version(uint32_t new_version);

namespace emergency {

[[nodiscard]] bool commitSecurityVersion(const Header& header) noexcept {
    const uint32_t currentEfuseVer = hw_efuse_read_security_version();
    
    // Блокування відкату: образ зі старим лічильником не приймається
    if (header.securityCounter < currentEfuseVer) {
        return false;
    }

    // Апаратне спалювання монотонного лічильника до нової версії
    if (header.securityCounter > currentEfuseVer) {
        if (!hw_efuse_burn_security_version(header.securityCounter)) {
            return false;
        }
    }

    return true;
}

} // namespace emergency
