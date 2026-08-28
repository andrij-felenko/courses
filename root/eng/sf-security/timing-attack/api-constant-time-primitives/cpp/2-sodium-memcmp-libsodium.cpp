#include <sodium.h>
#include <span>
#include <cstdint>

/* C++ обгортка з перевіркою розмірів */
[[nodiscard]] bool check_auth_tag(std::span<const uint8_t> tag1, std::span<const uint8_t> tag2) noexcept {
    if (tag1.size() != tag2.size()) {
        return false;
    }
    return sodium_memcmp(tag1.data(), tag2.data(), tag1.size()) == 0;
}
