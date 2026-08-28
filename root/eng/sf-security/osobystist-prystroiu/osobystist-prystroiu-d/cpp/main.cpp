#include <span>
#include <memory>
#include <expected>
#include "mbedtls/ssl.h"
#include "mbedtls/pk.h"

namespace device_identity {

enum class CryptoError {
    HardwareFailure,
    InvalidDigestLength,
    BufferOverflow
};

class HardwareSecurityModule {
public:
    explicit HardwareSecurityModule(uint8_t slot) noexcept : key_slot_(slot) {}

    [[nodiscard]] std::expected<size_t, CryptoError>
    sign_digest(std::span<const uint8_t> digest, std::span<uint8_t> out_sig) const noexcept {
        if (digest.size() != 32 || out_sig.size() < 72) {
            return std::unexpected(CryptoError::InvalidDigestLength);
        }
        /* Делегування операції підпису апаратному драйверу Secure Element */
        size_t sig_len = 0;
        if (secure_element_sign(key_slot_, digest.data(), digest.size(),
                                out_sig.data(), &sig_len) != 0) {
            return std::unexpected(CryptoError::HardwareFailure);
        }
        return sig_len;
    }

    [[nodiscard]] uint8_t slot() const noexcept { return key_slot_; }

private:
    uint8_t key_slot_;
};

/* Прив'язка С++ об'єкта до mbedTLS C-структури */
void bind_hsm_to_pk_context(mbedtls_pk_context& pk, HardwareSecurityModule& hsm) noexcept {
    pk.pk_info = mbedtls_pk_info_from_type(MBEDTLS_PK_OPAQUE);
    pk.pk_ctx  = std::addressof(hsm);
}

} // namespace device_identity
