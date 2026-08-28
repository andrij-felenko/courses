#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>
#include <span>
#include <vector>
#include <array>
#include <optional>
#include <cstdint>
#include <memory>
#include <string_view>
#include <algorithm>

namespace crypto {

constexpr size_t sha256_digest_len = 32;

// Безпечний контейнер для секретних байтів, що затирає пам'ять при знищенні (RAII)
template <size_t N>
struct secure_array {
    std::array<uint8_t, N> data{};

    ~secure_array() {
        OPENSSL_cleanse(data.data(), data.size());
    }

    [[nodiscard]] std::span<const uint8_t, N> as_span() const noexcept {
        return std::span<const uint8_t, N>(data);
    }
};

class hkdf_sha256 {
public:
    using prk_type = secure_array<sha256_digest_len>;

    // Етап Extract: IKM + Salt -> PRK
    static std::optional<prk_type> extract(
        std::span<const uint8_t> ikm,
        std::span<const uint8_t> salt = {})
    {
        prk_type prk;
        std::array<uint8_t, sha256_digest_len> default_salt{};

        std::span<const uint8_t> actual_salt = salt.empty() 
            ? std::span<const uint8_t>(default_salt) 
            : salt;

        unsigned int out_len = 0;
        uint8_t* res = HMAC(EVP_sha256(),
                            actual_salt.data(), static_cast<int>(actual_salt.size()),
                            ikm.data(), ikm.size(),
                            prk.data.data(), &out_len);

        if (!res || out_len != sha256_digest_len) {
            return std::nullopt;
        }
        return prk;
    }

    // Етап Expand: PRK + Info + okm_len -> OKM
    static std::optional<std::vector<uint8_t>> expand(
        const prk_type& prk,
        std::span<const uint8_t> info,
        size_t okm_len)
    {
        if (okm_len == 0 || okm_len > 255 * sha256_digest_len) {
            return std::nullopt;
        }

        std::vector<uint8_t> okm(okm_len);
        const size_t num_blocks = (okm_len + sha256_digest_len - 1) / sha256_digest_len;

        std::array<uint8_t, sha256_digest_len> t_block{};
        size_t t_len = 0;
        size_t bytes_copied = 0;

        std::unique_ptr<HMAC_CTX, decltype(&HMAC_CTX_free)> ctx(HMAC_CTX_new(), &HMAC_CTX_free);
        if (!ctx) return std::nullopt;

        for (uint8_t i = 1; i <= static_cast<uint8_t>(num_blocks); ++i) {
            if (!HMAC_Init_ex(ctx.get(), prk.data.data(), prk.data.size(), EVP_sha256(), nullptr)) {
                OPENSSL_cleanse(t_block.data(), t_block.size());
                return std::nullopt;
            }

            if (t_len > 0) {
                HMAC_Update(ctx.get(), t_block.data(), t_len);
            }
            if (!info.empty()) {
                HMAC_Update(ctx.get(), info.data(), info.size());
            }
            HMAC_Update(ctx.get(), &i, 1);

            unsigned int written = 0;
            HMAC_Final(ctx.get(), t_block.data(), &written);
            t_len = written;

            const size_t to_copy = std::min(okm_len - bytes_copied, sha256_digest_len);
            std::copy_n(t_block.begin(), to_copy, okm.begin() + bytes_copied);
            bytes_copied += to_copy;
        }

        OPENSSL_cleanse(t_block.data(), t_block.size());
        return okm;
    }
};

} // namespace crypto
