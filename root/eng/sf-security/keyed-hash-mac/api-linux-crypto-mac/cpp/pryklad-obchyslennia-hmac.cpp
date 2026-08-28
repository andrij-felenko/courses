#include <array>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <span>
#include <string_view>
#include <expected>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/core_names.h>

namespace crypto {

struct EvpMacDeleter {
    void operator()(EVP_MAC* mac) const noexcept {
        if (mac) EVP_MAC_free(mac);
    }
};

struct EvpMacCtxDeleter {
    void operator()(EVP_MAC_CTX* ctx) const noexcept {
        if (ctx) EVP_MAC_CTX_free(ctx);
    }
};

using ScopedMac = std::unique_ptr<EVP_MAC, EvpMacDeleter>;
using ScopedMacCtx = std::unique_ptr<EVP_MAC_CTX, EvpMacCtxDeleter>;

enum class MacError {
    AlgorithmFetchFailed,
    ContextAllocationFailed,
    InitializationFailed,
    UpdateFailed,
    FinalizationFailed
};

[[nodiscard]] std::expected<std::array<uint8_t, 32>, MacError>
compute_hmac_sha256(std::span<const uint8_t> key,
                    std::span<const uint8_t> message) noexcept {
    ScopedMac mac(EVP_MAC_fetch(nullptr, "HMAC", nullptr));
    if (!mac) {
        return std::unexpected(MacError::AlgorithmFetchFailed);
    }

    ScopedMacCtx ctx(EVP_MAC_CTX_new(mac.get()));
    if (!ctx) {
        return std::unexpected(MacError::ContextAllocationFailed);
    }

    std::array<OSSL_PARAM, 2> params = {
        OSSL_PARAM_construct_utf8_string(OSSL_MAC_PARAM_DIGEST,
                                         const_cast<char*>("SHA256"), 0),
        OSSL_PARAM_construct_end()
    };

    if (EVP_MAC_init(ctx.get(), key.data(), key.size(), params.data()) != 1) {
        return std::unexpected(MacError::InitializationFailed);
    }

    if (EVP_MAC_update(ctx.get(), message.data(), message.size()) != 1) {
        return std::unexpected(MacError::UpdateFailed);
    }

    std::array<uint8_t, 32> tag{};
    size_t tag_len = 0;
    if (EVP_MAC_final(ctx.get(), tag.data(), &tag_len, tag.size()) != 1) {
        return std::unexpected(MacError::FinalizationFailed);
    }

    return tag;
}

} // namespace crypto
