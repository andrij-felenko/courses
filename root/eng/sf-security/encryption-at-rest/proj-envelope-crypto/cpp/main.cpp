#include <iostream>
#include <span>
#include <vector>
#include <memory>
#include <array>
#include <expected>
#include <algorithm>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>

constexpr size_t KeySize256 = 32;
constexpr size_t GcmIvSize  = 12;
constexpr size_t GcmTagSize = 16;

// RAII занулювач для безпечного очищення конфіденційних буферів
template <size_t N>
struct SecureBuffer {
    std::array<uint8_t, N> data{};

    ~SecureBuffer() {
        OPENSSL_cleanse(data.data(), data.size());
    }

    SecureBuffer() = default;
    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;
};

// RAII обгортка над EVP_CIPHER_CTX
struct EvpCipherCtxDeleter {
    void operator()(EVP_CIPHER_CTX* ctx) const noexcept {
        if (ctx) EVP_CIPHER_CTX_free(ctx);
    }
};
using UniqueCipherCtx = std::unique_ptr<EVP_CIPHER_CTX, EvpCipherCtxDeleter>;

enum class CryptoError {
    RngFailure,
    ContextInitFailure,
    EncryptionFailure,
    DecryptionTagMismatch,
    AllocationError
};

struct SealedEnvelope {
    std::array<uint8_t, KeySize256 + GcmTagSize> wrapped_dek{};
    std::array<uint8_t, GcmIvSize> iv_dek{};
    std::array<uint8_t, GcmIvSize> iv_data{};
    std::array<uint8_t, GcmTagSize> tag_data{};
    std::vector<uint8_t> ciphertext;
};

class EnvelopeCrypto {
public:
    static std::expected<SealedEnvelope, CryptoError> Seal(
        std::span<const uint8_t, KeySize256> kek,
        std::span<const uint8_t> aad,
        std::span<const uint8_t> plaintext) 
    {
        SecureBuffer<KeySize256> raw_dek;
        SealedEnvelope env;
        env.ciphertext.resize(plaintext.size());

        if (RAND_bytes(raw_dek.data.data(), static_cast<int>(KeySize256)) != 1 ||
            RAND_bytes(env.iv_dek.data(), static_cast<int>(GcmIvSize)) != 1 ||
            RAND_bytes(env.iv_data.data(), static_cast<int>(GcmIvSize)) != 1) {
            return std::unexpected(CryptoError::RngFailure);
        }

        // 1. Шифрування корисних даних за допомогою DEK
        auto data_enc_res = AesGcmEncrypt(
            raw_dek.data, env.iv_data, aad, plaintext, env.ciphertext, env.tag_data);
        if (!data_enc_res) return std::unexpected(data_enc_res.error());

        // 2. Обгортання DEK за допомогою KEK
        std::array<uint8_t, GcmTagSize> dek_tag{};
        auto dek_enc_res = AesGcmEncrypt(
            kek, env.iv_dek, aad, raw_dek.data,
            std::span<uint8_t>(env.wrapped_dek.data(), KeySize256), dek_tag);
        if (!dek_enc_res) return std::unexpected(dek_enc_res.error());

        std::copy(dek_tag.begin(), dek_tag.end(), env.wrapped_dek.begin() + KeySize256);
        return env;
    }

    static std::expected<std::vector<uint8_t>, CryptoError> Open(
        std::span<const uint8_t, KeySize256> kek,
        std::span<const uint8_t> aad,
        const SealedEnvelope& env) 
    {
        SecureBuffer<KeySize256> raw_dek;

        // 1. Розгортання DEK
        std::span<const uint8_t, KeySize256> wrapped_dek_span(env.wrapped_dek.data(), KeySize256);
        std::span<const uint8_t, GcmTagSize> dek_tag_span(env.wrapped_dek.data() + KeySize256, GcmTagSize);

        auto dek_dec_res = AesGcmDecrypt(
            kek, env.iv_dek, aad, wrapped_dek_span, dek_tag_span, raw_dek.data);
        if (!dek_dec_res) return std::unexpected(CryptoError::DecryptionTagMismatch);

        // 2. Розшифрування корисного навантаження
        std::vector<uint8_t> plaintext(env.ciphertext.size());
        auto data_dec_res = AesGcmDecrypt(
            raw_dek.data, env.iv_data, aad, env.ciphertext, env.tag_data, plaintext);
        if (!data_dec_res) return std::unexpected(CryptoError::DecryptionTagMismatch);

        return plaintext;
    }

private:
    static std::expected<void, CryptoError> AesGcmEncrypt(
        std::span<const uint8_t> key, std::span<const uint8_t> iv,
        std::span<const uint8_t> aad, std::span<const uint8_t> plain,
        std::span<uint8_t> cipher, std::span<uint8_t, GcmTagSize> tag) 
    {
        UniqueCipherCtx ctx(EVP_CIPHER_CTX_new());
        if (!ctx) return std::unexpected(CryptoError::ContextInitFailure);

        int len = 0;
        if (EVP_EncryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_IVLEN, static_cast<int>(iv.size()), nullptr) != 1 ||
            EVP_EncryptInit_ex(ctx.get(), nullptr, nullptr, key.data(), iv.data()) != 1) {
            return std::unexpected(CryptoError::EncryptionFailure);
        }

        if (!aad.empty()) {
            if (EVP_EncryptUpdate(ctx.get(), nullptr, &len, aad.data(), static_cast<int>(aad.size())) != 1)
                return std::unexpected(CryptoError::EncryptionFailure);
        }

        if (EVP_EncryptUpdate(ctx.get(), cipher.data(), &len, plain.data(), static_cast<int>(plain.size())) != 1 ||
            EVP_EncryptFinal_ex(ctx.get(), cipher.data() + len, &len) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_GET_TAG, static_cast<int>(GcmTagSize), tag.data()) != 1) {
            return std::unexpected(CryptoError::EncryptionFailure);
        }

        return {};
    }

    static std::expected<void, CryptoError> AesGcmDecrypt(
        std::span<const uint8_t> key, std::span<const uint8_t> iv,
        std::span<const uint8_t> aad, std::span<const uint8_t> cipher,
        std::span<const uint8_t, GcmTagSize> tag, std::span<uint8_t> plain) 
    {
        UniqueCipherCtx ctx(EVP_CIPHER_CTX_new());
        if (!ctx) return std::unexpected(CryptoError::ContextInitFailure);

        int len = 0;
        if (EVP_DecryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_IVLEN, static_cast<int>(iv.size()), nullptr) != 1 ||
            EVP_DecryptInit_ex(ctx.get(), nullptr, nullptr, key.data(), iv.data()) != 1) {
            return std::unexpected(CryptoError::ContextInitFailure);
        }

        if (!aad.empty()) {
            if (EVP_DecryptUpdate(ctx.get(), nullptr, &len, aad.data(), static_cast<int>(aad.size())) != 1)
                return std::unexpected(CryptoError::ContextInitFailure);
        }

        if (EVP_DecryptUpdate(ctx.get(), plain.data(), &len, cipher.data(), static_cast<int>(cipher.size())) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_TAG, static_cast<int>(GcmTagSize), const_cast<uint8_t*>(tag.data())) != 1 ||
            EVP_DecryptFinal_ex(ctx.get(), plain.data() + len, &len) != 1) {
            return std::unexpected(CryptoError::DecryptionTagMismatch);
        }

        return {};
    }
};
