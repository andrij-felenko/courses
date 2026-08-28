#include <iostream>
#include <array>
#include <span>
#include <memory>
#include <string_view>
#include <expected>
#include <openssl/evp.h>
#include <openssl/kdf.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>

namespace crypto {

inline constexpr size_t KeySize = 32;
inline constexpr size_t IvSize = 12;

struct SessionKeys {
    std::array<uint8_t, KeySize> client_write_key{};
    std::array<uint8_t, KeySize> server_write_key{};
    std::array<uint8_t, IvSize>  client_write_iv{};
    std::array<uint8_t, IvSize>  server_write_iv{};

    ~SessionKeys() {
        OPENSSL_cleanse(client_write_key.data(), client_write_key.size());
        OPENSSL_cleanse(server_write_key.data(), server_write_key.size());
        OPENSSL_cleanse(client_write_iv.data(), client_write_iv.size());
        OPENSSL_cleanse(server_write_iv.data(), server_write_iv.size());
    }
};

/* RAII-обгортка для EVP_PKEY з автоматичним затиранням */
struct EvpKeyDeleter {
    void operator()(EVP_PKEY* p) const noexcept {
        if (p) EVP_PKEY_free(p);
    }
};
using UniquePkey = std::unique_ptr<EVP_PKEY, EvpKeyDeleter>;

struct EvpCtxDeleter {
    void operator()(EVP_PKEY_CTX* c) const noexcept {
        if (c) EVP_PKEY_CTX_free(c);
    }
};
using UniquePkeyCtx = std::unique_ptr<EVP_PKEY_CTX, EvpCtxDeleter>;

class EphemeralX25519 {
public:
    static std::expected<UniquePkey, std::string_view> generate_keypair() {
        UniquePkeyCtx pctx(EVP_PKEY_CTX_new_id(EVP_PKEY_X25519, nullptr));
        if (!pctx) return std::unexpected("Failed to create X25519 context");

        EVP_PKEY* raw_key = nullptr;
        if (EVP_PKEY_keygen_init(pctx.get()) <= 0 ||
            EVP_PKEY_keygen(pctx.get(), &raw_key) <= 0) {
            return std::unexpected("Failed to generate X25519 keypair");
        }
        return UniquePkey(raw_key);
    }

    static std::expected<std::array<uint8_t, KeySize>, std::string_view>
    compute_shared_secret(EVP_PKEY* our_priv, EVP_PKEY* peer_pub) {
        UniquePkeyCtx ctx(EVP_PKEY_CTX_new(our_priv, nullptr));
        if (!ctx) return std::unexpected("Failed to initialize derivation context");

        if (EVP_PKEY_derive_init(ctx.get()) <= 0 ||
            EVP_PKEY_derive_set_peer(ctx.get(), peer_pub) <= 0) {
            return std::unexpected("Failed to set peer public key");
        }

        std::array<uint8_t, KeySize> secret{};
        size_t out_len = KeySize;
        if (EVP_PKEY_derive(ctx.get(), secret.data(), &out_len) <= 0 || out_len != KeySize) {
            OPENSSL_cleanse(secret.data(), secret.size());
            return std::unexpected("Shared secret derivation failed");
        }
        return secret;
    }

    static std::expected<SessionKeys, std::string_view>
    derive_session_keys(std::span<const uint8_t, KeySize> secret,
                        std::span<const uint8_t> salt,
                        std::string_view info) {
        std::unique_ptr<EVP_KDF, decltype(&EVP_KDF_free)> kdf(
            EVP_KDF_fetch(nullptr, "HKDF", nullptr), &EVP_KDF_free);
        if (!kdf) return std::unexpected("HKDF implementation not found");

        std::unique_ptr<EVP_KDF_CTX, decltype(&EVP_KDF_CTX_free)> kctx(
            EVP_KDF_CTX_new(kdf.get()), &EVP_KDF_CTX_free);
        if (!kctx) return std::unexpected("Failed to create HKDF context");

        char digest_name[] = "SHA256";
        std::array<OSSL_PARAM, 5> params = {
            OSSL_PARAM_construct_utf8_string("digest", digest_name, sizeof(digest_name)),
            OSSL_PARAM_construct_octet_string("key", const_cast<uint8_t*>(secret.data()), secret.size()),
            OSSL_PARAM_construct_octet_string("salt", const_cast<uint8_t*>(salt.data()), salt.size()),
            OSSL_PARAM_construct_octet_string("info", const_cast<char*>(info.data()), info.size()),
            OSSL_PARAM_construct_end()
        };

        constexpr size_t total_material_len = 2 * KeySize + 2 * IvSize;
        std::array<uint8_t, total_material_len> out_material{};

        int ret = EVP_KDF_derive(kctx.get(), out_material.data(), out_material.size(), params.data());
        if (ret <= 0) {
            OPENSSL_cleanse(out_material.data(), out_material.size());
            return std::unexpected("HKDF key derivation execution failed");
        }

        SessionKeys keys;
        std::copy_n(out_material.data(), KeySize, keys.client_write_key.begin());
        std::copy_n(out_material.data() + KeySize, KeySize, keys.server_write_key.begin());
        std::copy_n(out_material.data() + 2 * KeySize, IvSize, keys.client_write_iv.begin());
        std::copy_n(out_material.data() + 2 * KeySize + IvSize, IvSize, keys.server_write_iv.begin());

        OPENSSL_cleanse(out_material.data(), out_material.size());
        return keys;
    }
};

} // namespace crypto

int main() {
    auto client_kp = crypto::EphemeralX25519::generate_keypair();
    auto server_kp = crypto::EphemeralX25519::generate_keypair();
    if (!client_kp || !server_kp) return 1;

    auto client_sec = crypto::EphemeralX25519::compute_shared_secret(client_kp->get(), server_kp->get());
    auto server_sec = crypto::EphemeralX25519::compute_shared_secret(server_kp->get(), client_kp->get());
    if (!client_sec || !server_sec) return 1;

    // Константний час перевірки збігу секретів
    if (CRYPTO_memcmp(client_sec->data(), server_sec->data(), crypto::KeySize) != 0) {
        return 1;
    }

    std::array<uint8_t, 16> salt{};
    RAND_bytes(salt.data(), static_cast<int>(salt.size()));

    auto client_keys = crypto::EphemeralX25519::derive_session_keys(*client_sec, salt, "tls13-session-v1");
    auto server_keys = crypto::EphemeralX25519::derive_session_keys(*server_sec, salt, "tls13-session-v1");

    // Затирання проміжних секретів
    OPENSSL_cleanse(client_sec->data(), client_sec->size());
    OPENSSL_cleanse(server_sec->data(), server_sec->size());

    return (client_keys && server_keys) ? 0 : 1;
}
