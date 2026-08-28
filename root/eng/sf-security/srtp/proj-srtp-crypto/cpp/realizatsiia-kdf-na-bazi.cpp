#include <cstdint>
#include <array>
#include <span>
#include <cstring>
#include <expected>
#include <openssl/aes.h>

struct SessionKeys {
    std::array<std::uint8_t, 16> enc_key{};   // k_e (128 біт)
    std::array<std::uint8_t, 20> auth_key{};  // k_a (160 біт)
    std::array<std::uint8_t, 14> salt_key{};  // k_s (112 біт)
};

enum class KdfError {
    AesKeyInitFailed
};

class SrtpKdf {
public:
    static constexpr std::uint8_t LabelEncrypt = 0x00;
    static constexpr std::uint8_t LabelAuth    = 0x01;
    static constexpr std::uint8_t LabelSalt    = 0x02;

    static std::expected<SessionKeys, KdfError> derive(
        std::span<const std::uint8_t, 16> master_key,
        std::span<const std::uint8_t, 14> master_salt) noexcept {
        
        AES_KEY aes_ctx{};
        if (AES_set_encrypt_key(master_key.data(), 128, &aes_ctx) != 0) {
            return std::unexpected(KdfError::AesKeyInitFailed);
        }

        SessionKeys keys{};
        derive_key(aes_ctx, master_salt, LabelEncrypt, keys.enc_key);
        derive_key(aes_ctx, master_salt, LabelAuth, keys.auth_key);
        derive_key(aes_ctx, master_salt, LabelSalt, keys.salt_key);

        return keys;
    }

private:
    static void derive_key(const AES_KEY& aes_ctx,
                           std::span<const std::uint8_t, 14> master_salt,
                           std::uint8_t label,
                           std::span<std::uint8_t> out_buf) noexcept {
        std::array<std::uint8_t, 16> iv{};
        std::memcpy(iv.data(), master_salt.data(), 14);
        iv[7] ^= label;

        std::array<std::uint8_t, 32> keystream{};
        std::size_t generated = 0;
        std::uint16_t block_counter = 0;

        while (generated < out_buf.size()) {
            iv[14] = static_cast<std::uint8_t>(block_counter >> 8);
            iv[15] = static_cast<std::uint8_t>(block_counter & 0xFF);

            AES_encrypt(iv.data(), &keystream[generated], &aes_ctx);
            generated += 16;
            ++block_counter;
        }

        std::memcpy(out_buf.data(), keystream.data(), out_buf.size());
    }
};
