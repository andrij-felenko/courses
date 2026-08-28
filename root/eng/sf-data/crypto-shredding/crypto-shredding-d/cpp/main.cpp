#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <memory>
#include <optional>
#include <string_view>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>

constexpr size_t AES_256_KEY_SIZE = 32;
constexpr size_t GCM_IV_SIZE      = 12;
constexpr size_t GCM_TAG_SIZE     = 16;

/* RAII-обгортка для автоматичного стирання секретних ключів у пам'яті */
template <size_t N>
class SecureBuffer {
public:
    SecureBuffer() noexcept { data_.fill(0); }
    ~SecureBuffer() noexcept { OPENSSL_cleanse(data_.data(), data_.size()); }

    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;

    SecureBuffer(SecureBuffer&& other) noexcept : data_(other.data_), is_valid_(other.is_valid_) {
        other.shred();
    }

    SecureBuffer& operator=(SecureBuffer&& other) noexcept {
        if (this != &other) {
            shred();
            data_ = other.data_;
            is_valid_ = other.is_valid_;
            other.shred();
        }
        return *this;
    }

    [[nodiscard]] std::span<uint8_t, N> span() noexcept { return std::span<uint8_t, N>(data_); }
    [[nodiscard]] std::span<const uint8_t, N> span() const noexcept { return std::span<const uint8_t, N>(data_); }
    [[nodiscard]] bool isValid() const noexcept { return is_valid_; }
    void markValid() noexcept { is_valid_ = true; }
    void shred() noexcept {
        OPENSSL_cleanse(data_.data(), data_.size());
        is_valid_ = false;
    }

private:
    std::array<uint8_t, N> data_;
    bool is_valid_{false};
};

using SubjectKeyDEK = SecureBuffer<AES_256_KEY_SIZE>;

struct EncryptedField {
    std::array<uint8_t, GCM_IV_SIZE> iv;
    std::array<uint8_t, GCM_TAG_SIZE> tag;
    std::vector<uint8_t> ciphertext;
};

/* Спеціальний делетер для RAII-керування контекстом OpenSSL EVP */
struct EvpCipherCtxDeleter {
    void operator()(EVP_CIPHER_CTX* ctx) const noexcept {
        if (ctx) EVP_CIPHER_CTX_free(ctx);
    }
};
using ScopedEvpCtx = std::unique_ptr<EVP_CIPHER_CTX, EvpCipherCtxDeleter>;

class CryptoEngine {
public:
    [[nodiscard]] static std::optional<SubjectKeyDEK> generateSubjectKey() noexcept {
        SubjectKeyDEK dek;
        if (RAND_bytes(dek.span().data(), static_cast<int>(AES_256_KEY_SIZE)) != 1) {
            return std::nullopt;
        }
        dek.markValid();
        return dek;
    }

    [[nodiscard]] static std::optional<EncryptedField> encryptField(
        const SubjectKeyDEK& key,
        std::span<const uint8_t> plaintext) noexcept {

        if (!key.isValid() || plaintext.empty()) return std::nullopt;

        EncryptedField out;
        if (RAND_bytes(out.iv.data(), static_cast<int>(GCM_IV_SIZE)) != 1) {
            return std::nullopt;
        }

        out.ciphertext.resize(plaintext.size());
        ScopedEvpCtx ctx(EVP_CIPHER_CTX_new());
        if (!ctx) return std::nullopt;

        int len = 0;
        if (EVP_EncryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, nullptr) != 1 ||
            EVP_EncryptInit_ex(ctx.get(), nullptr, nullptr, key.span().data(), out.iv.data()) != 1 ||
            EVP_EncryptUpdate(ctx.get(), out.ciphertext.data(), &len, plaintext.data(), static_cast<int>(plaintext.size())) != 1) {
            return std::nullopt;
        }

        int finalLen = 0;
        if (EVP_EncryptFinal_ex(ctx.get(), out.ciphertext.data() + len, &finalLen) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_GET_TAG, GCM_TAG_SIZE, out.tag.data()) != 1) {
            return std::nullopt;
        }

        out.ciphertext.resize(static_cast<size_t>(len + finalLen));
        return out;
    }

    [[nodiscard]] static std::optional<std::vector<uint8_t>> decryptField(
        const SubjectKeyDEK& key,
        const EncryptedField& field) noexcept {

        if (!key.isValid() || field.ciphertext.empty()) return std::nullopt;

        ScopedEvpCtx ctx(EVP_CIPHER_CTX_new());
        if (!ctx) return std::nullopt;

        std::vector<uint8_t> plaintext(field.ciphertext.size());
        int len = 0;

        if (EVP_DecryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, nullptr) != 1 ||
            EVP_DecryptInit_ex(ctx.get(), nullptr, nullptr, key.span().data(), field.iv.data()) != 1 ||
            EVP_DecryptUpdate(ctx.get(), plaintext.data(), &len, field.ciphertext.data(), static_cast<int>(field.ciphertext.size())) != 1) {
            return std::nullopt;
        }

        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_TAG, GCM_TAG_SIZE, const_cast<uint8_t*>(field.tag.data())) != 1) {
            return std::nullopt;
        }

        int finalLen = 0;
        if (EVP_DecryptFinal_ex(ctx.get(), plaintext.data() + len, &finalLen) != 1) {
            /* Помилка автентифікації GMAC: ключ не підходить або шифротекст змінено */
            OPENSSL_cleanse(plaintext.data(), plaintext.size());
            return std::nullopt;
        }

        plaintext.resize(static_cast<size_t>(len + finalLen));
        return plaintext;
    }
};
