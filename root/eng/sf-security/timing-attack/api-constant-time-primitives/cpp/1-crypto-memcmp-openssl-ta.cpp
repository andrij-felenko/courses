#include <openssl/crypto.h>
#include <span>
#include <cstdint>

/* Безпечна C++ обгортка для spans */
[[nodiscard]] bool verify_token(std::span<const uint8_t> user_buf, std::span<const uint8_t> secret_buf) noexcept {
    if (user_buf.size() != secret_buf.size()) {
        return false;
    }
    return CRYPTO_memcmp(user_buf.data(), secret_buf.data(), user_buf.size()) == 0;
}
