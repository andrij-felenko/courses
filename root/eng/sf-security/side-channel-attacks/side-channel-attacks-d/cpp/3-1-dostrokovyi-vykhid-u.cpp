#include <cstdint>
#include <cstddef>
#include <span>

[[nodiscard]] bool insecure_verify(std::span<const uint8_t> expected_mac,
                                   std::span<const uint8_t> user_mac) noexcept {
    if (expected_mac.size() != user_mac.size()) {
        return false;
    }
    for (size_t i = 0; i < expected_mac.size(); ++i) {
        if (expected_mac[i] != user_mac[i]) {
            return false; // Достроковий вихід при першому неспівпалому байті
        }
    }
    return true;
}
