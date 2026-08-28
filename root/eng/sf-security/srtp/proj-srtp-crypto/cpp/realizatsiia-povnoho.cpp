#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <cstring>
#include <memory>
#include <expected>
#include <openssl/aes.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

enum class ProtectError {
    AesInitFailed,
    HmacInitFailed
};

enum class UnprotectError {
    PacketTooShort,
    AuthFailed,
    AesInitFailed,
    HmacInitFailed
};

struct HmacCtxDeleter {
    void operator()(HMAC_CTX* ctx) const noexcept {
        if (ctx) HMAC_CTX_free(ctx);
    }
};
using UniqueHmacCtx = std::unique_ptr<HMAC_CTX, HmacCtxDeleter>;

class SrtpPipeline {
public:
    static std::expected<std::size_t, ProtectError> protect(
        const SessionKeys& keys,
        std::span<std::uint8_t> rtp_buffer,
        std::size_t header_len,
        std::size_t payload_len,
        std::uint32_t ssrc,
        std::uint64_t index,
        std::uint32_t roc) noexcept {

        if (rtp_buffer.size() < header_len + payload_len + 10) {
            return std::unexpected(ProtectError::HmacInitFailed);
        }

        std::array<std::uint8_t, 16> iv{};
        build_iv(keys.salt_key, ssrc, index, iv);

        AES_KEY aes_ctx{};
        if (AES_set_encrypt_key(keys.enc_key.data(), 128, &aes_ctx) != 0) {
            return std::unexpected(ProtectError::AesInitFailed);
        }

        std::array<std::uint8_t, 16> ecount_buf{};
        unsigned int num = 0;
        AES_ctr128_encrypt(rtp_buffer.data() + header_len,
                           rtp_buffer.data() + header_len,
                           payload_len, &aes_ctx, iv.data(),
                           ecount_buf.data(), &num);

        UniqueHmacCtx hmac(HMAC_CTX_new());
        if (!hmac) {
            return std::unexpected(ProtectError::HmacInitFailed);
        }

        HMAC_Init_ex(hmac.get(), keys.auth_key.data(), 20, EVP_sha1(), nullptr);
        HMAC_Update(hmac.get(), rtp_buffer.data(), header_len + payload_len);

        const std::array<std::uint8_t, 4> roc_be = {
            static_cast<std::uint8_t>(roc >> 24),
            static_cast<std::uint8_t>(roc >> 16),
            static_cast<std::uint8_t>(roc >> 8),
            static_cast<std::uint8_t>(roc & 0xFF)
        };
        HMAC_Update(hmac.get(), roc_be.data(), roc_be.size());

        std::array<std::uint8_t, 32> mac_out{};
        unsigned int mac_len = 0;
        HMAC_Final(hmac.get(), mac_out.data(), &mac_len);

        std::memcpy(rtp_buffer.data() + header_len + payload_len, mac_out.data(), 10);
        return header_len + payload_len + 10;
    }

    static std::expected<std::size_t, UnprotectError> unprotect(
        const SessionKeys& keys,
        std::span<std::uint8_t> packet_buffer,
        std::size_t header_len,
        std::uint32_t ssrc,
        std::uint64_t index,
        std::uint32_t roc_est) noexcept {

        if (packet_buffer.size() < header_len + 10) {
            return std::unexpected(UnprotectError::PacketTooShort);
        }

        const std::size_t payload_len = packet_buffer.size() - header_len - 10;
        const std::uint8_t* received_tag = packet_buffer.data() + header_len + payload_len;

        UniqueHmacCtx hmac(HMAC_CTX_new());
        if (!hmac) {
            return std::unexpected(UnprotectError::HmacInitFailed);
        }

        HMAC_Init_ex(hmac.get(), keys.auth_key.data(), 20, EVP_sha1(), nullptr);
        HMAC_Update(hmac.get(), packet_buffer.data(), header_len + payload_len);

        const std::array<std::uint8_t, 4> roc_be = {
            static_cast<std::uint8_t>(roc_est >> 24),
            static_cast<std::uint8_t>(roc_est >> 16),
            static_cast<std::uint8_t>(roc_est >> 8),
            static_cast<std::uint8_t>(roc_est & 0xFF)
        };
        HMAC_Update(hmac.get(), roc_be.data(), roc_be.size());

        std::array<std::uint8_t, 32> mac_calc{};
        unsigned int mac_len = 0;
        HMAC_Final(hmac.get(), mac_calc.data(), &mac_len);

        if (CRYPTO_memcmp(received_tag, mac_calc.data(), 10) != 0) {
            return std::unexpected(UnprotectError::AuthFailed);
        }

        std::array<std::uint8_t, 16> iv{};
        build_iv(keys.salt_key, ssrc, index, iv);

        AES_KEY aes_ctx{};
        if (AES_set_encrypt_key(keys.enc_key.data(), 128, &aes_ctx) != 0) {
            return std::unexpected(UnprotectError::AesInitFailed);
        }

        std::array<std::uint8_t, 16> ecount_buf{};
        unsigned int num = 0;
        AES_ctr128_encrypt(packet_buffer.data() + header_len,
                           packet_buffer.data() + header_len,
                           payload_len, &aes_ctx, iv.data(),
                           ecount_buf.data(), &num);

        return payload_len;
    }

private:
    static void build_iv(std::span<const std::uint8_t, 14> salt,
                         std::uint32_t ssrc,
                         std::uint64_t index,
                         std::span<std::uint8_t, 16> iv) noexcept {
        std::memcpy(iv.data(), salt.data(), 14);
        iv[14] = 0;
        iv[15] = 0;

        iv[4] ^= static_cast<std::uint8_t>(ssrc >> 24);
        iv[5] ^= static_cast<std::uint8_t>(ssrc >> 16);
        iv[6] ^= static_cast<std::uint8_t>(ssrc >> 8);
        iv[7] ^= static_cast<std::uint8_t>(ssrc & 0xFF);

        for (int b = 0; b < 6; ++b) {
            iv[8 + b] ^= static_cast<std::uint8_t>((index >> (8 * (5 - b))) & 0xFF);
        }
    }
};
