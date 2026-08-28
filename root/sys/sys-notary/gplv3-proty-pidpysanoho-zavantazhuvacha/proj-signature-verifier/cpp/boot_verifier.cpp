// boot_verifier.hpp / boot_verifier.cpp — Ідіоматична реалізація на сучасному C++20
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include <expected>
#include <array>
#include <algorithm>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/pem.h>

namespace bootsec {

inline constexpr uint32_t SecureBootMagic = 0x53454355U; // "SECU"

struct alignas(4) ImageHeader {
    uint32_t magic;
    uint32_t header_version;
    uint32_t firmware_version;
    uint32_t payload_size;
    uint32_t signature_size;
    std::array<uint8_t, 16> key_id;
    std::array<uint8_t, 28> reserved;
};

enum class VerifyError {
    InvalidMagic,
    RollbackDetected,
    ImageTooShort,
    UnknownKey,
    SignatureInvalid,
    CryptoEngineFault
};

struct EvpPkeyDeleter {
    void operator()(EVP_PKEY* ptr) const noexcept {
        if (ptr) EVP_PKEY_free(ptr);
    }
};
using UniquePkey = std::unique_ptr<EVP_PKEY, EvpPkeyDeleter>;

struct EvpMdCtxDeleter {
    void operator()(EVP_MD_CTX* ptr) const noexcept {
        if (ptr) EVP_MD_CTX_free(ptr);
    }
};
using UniqueMdCtx = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

struct KeyRecord {
    std::array<uint8_t, 16> key_id;
    UniquePkey pubkey;
    bool is_user_mok;
};

class BootImageVerifier {
public:
    explicit BootImageVerifier(uint32_t min_anti_rollback)
        : min_anti_rollback_ver_(min_anti_rollback) {}

    bool register_key(std::array<uint8_t, 16> id, std::string_view pem_key, bool is_mok) {
        BIO* bio = BIO_new_mem_buf(pem_key.data(), static_cast<int>(pem_key.size()));
        if (!bio) return false;

        EVP_PKEY* raw_pkey = PEM_read_bio_PUBKEY(bio, nullptr, nullptr, nullptr);
        BIO_free(bio);
        if (!raw_pkey) return false;

        keys_.push_back(KeyRecord{id, UniquePkey(raw_pkey), is_mok});
        return true;
    }

    struct VerifyOutcome {
        bool is_user_mok_authorized;
        uint32_t fw_version;
        std::span<const uint8_t> payload;
    };

    [[nodiscard]] std::expected<VerifyOutcome, VerifyError>
    verify(std::span<const uint8_t> raw_image) const noexcept {
        if (raw_image.size() < sizeof(ImageHeader)) {
            return std::unexpected(VerifyError::ImageTooShort);
        }

        ImageHeader header{};
        std::memcpy(&header, raw_image.data(), sizeof(ImageHeader));

        if (header.magic != SecureBootMagic) {
            return std::unexpected(VerifyError::InvalidMagic);
        }

        if (header.firmware_version < min_anti_rollback_ver_) {
            return std::unexpected(VerifyError::RollbackDetected);
        }

        // Захист від цілочисельного переповнення розміру
        if (header.payload_size > raw_image.size() || header.signature_size > raw_image.size()) {
            return std::unexpected(VerifyError::ImageTooShort);
        }

        const size_t expected_size = sizeof(ImageHeader) + header.payload_size + header.signature_size;
        if (expected_size < sizeof(ImageHeader) || raw_image.size() < expected_size) {
            return std::unexpected(VerifyError::ImageTooShort);
        }

        const auto payload_span = raw_image.subspan(sizeof(ImageHeader), header.payload_size);
        const auto sig_span = raw_image.subspan(sizeof(ImageHeader) + header.payload_size, header.signature_size);

        // Пошук сертифіката у внутрішньому сховищі ключів
        const auto it = std::find_if(keys_.begin(), keys_.end(), [&](const KeyRecord& k) {
            return k.key_id == header.key_id;
        });

        if (it == keys_.end() || !it->pubkey) {
            return std::unexpected(VerifyError::UnknownKey);
        }

        UniqueMdCtx ctx(EVP_MD_CTX_new());
        if (!ctx) {
            return std::unexpected(VerifyError::CryptoEngineFault);
        }

        if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha256(), nullptr, it->pubkey.get()) != 1) {
            return std::unexpected(VerifyError::CryptoEngineFault);
        }

        if (EVP_DigestVerifyUpdate(ctx.get(), payload_span.data(), payload_span.size()) != 1) {
            return std::unexpected(VerifyError::CryptoEngineFault);
        }

        if (EVP_DigestVerifyFinal(ctx.get(), sig_span.data(), sig_span.size()) != 1) {
            return std::unexpected(VerifyError::SignatureInvalid);
        }

        return VerifyOutcome{
            .is_user_mok_authorized = it->is_user_mok,
            .fw_version = header.firmware_version,
            .payload = payload_span
        };
    }

private:
    uint32_t min_anti_rollback_ver_{0};
    std::vector<KeyRecord> keys_{};
};

} // namespace bootsec
