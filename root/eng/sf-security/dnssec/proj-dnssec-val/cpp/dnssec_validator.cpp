// dnssec_validator.cpp — Ідіоматична реалізація валідатора DNSSEC на C++20
#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <algorithm>
#include <expected>
#include <memory>
#include <cstdint>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/ec.h>
#include <openssl/ecdsa.h>

namespace dnssec {

enum class ValidationError {
    InvalidTimeWindow,
    UnsupportedAlgorithm,
    KeyTagMismatch,
    MalformedKeyData,
    CryptoFailure,
    SignatureInvalid
};

struct RRSig {
    uint16_t type_covered;
    uint8_t  algorithm;
    uint8_t  labels;
    uint32_t original_ttl;
    uint32_t sig_expiration;
    uint32_t sig_inception;
    uint16_t key_tag;
    std::span<const uint8_t> signer_name;
    std::span<const uint8_t> signature;
};

struct DNSKey {
    uint16_t flags;
    uint8_t  protocol;
    uint8_t  algorithm;
    std::span<const uint8_t> pubkey;
    std::span<const uint8_t> rdata_raw;
};

struct RREntry {
    std::span<const uint8_t> rdata;
};

// RAII обгортки для структур OpenSSL
struct EvpMdCtxDeleter { void operator()(EVP_MD_CTX* ctx) const { EVP_MD_CTX_free(ctx); } };
using EvpMdCtxPtr = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

struct EcdsaSigDeleter { void operator()(ECDSA_SIG* s) const { ECDSA_SIG_free(s); } };
using EcdsaSigPtr = std::unique_ptr<ECDSA_SIG, EcdsaSigDeleter>;

struct EcKeyDeleter { void operator()(EC_KEY* k) const { EC_KEY_free(k); } };
using EcKeyPtr = std::unique_ptr<EC_KEY, EcKeyDeleter>;

// 1. Обчислення Key Tag за RFC 4034
[[nodiscard]] constexpr uint16_t calculate_key_tag(std::span<const uint8_t> rdata) noexcept {
    uint32_t ac = 0;
    for (size_t i = 0; i < rdata.size(); ++i) {
        ac += (i & 1) ? static_cast<uint32_t>(rdata[i]) : (static_cast<uint32_t>(rdata[i]) << 8);
    }
    ac += (ac >> 16) & 0xFFFF;
    return static_cast<uint16_t>(ac & 0xFFFF);
}

// 2. Валідація відкритого ключа за записом DS у батьківській зоні
[[nodiscard]] std::expected<bool, ValidationError>
verify_ds_record(std::span<const uint8_t> owner_wire,
                 const DNSKey& key,
                 std::span<const uint8_t> expected_digest) {
    if (expected_digest.size() != SHA256_DIGEST_LENGTH) {
        return std::unexpected(ValidationError::MalformedKeyData);
    }

    EvpMdCtxPtr ctx(EVP_MD_CTX_new());
    if (!ctx) return std::unexpected(ValidationError::CryptoFailure);

    std::array<uint8_t, SHA256_DIGEST_LENGTH> calc_digest{};
    if (EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) <= 0 ||
        EVP_DigestUpdate(ctx.get(), owner_wire.data(), owner_wire.size()) <= 0 ||
        EVP_DigestUpdate(ctx.get(), key.rdata_raw.data(), key.rdata_raw.size()) <= 0 ||
        EVP_DigestFinal_ex(ctx.get(), calc_digest.data(), nullptr) <= 0) {
        return std::unexpected(ValidationError::CryptoFailure);
    }

    return (CRYPTO_memcmp(calc_digest.data(), expected_digest.data(), SHA256_DIGEST_LENGTH) == 0);
}

// 3. Повна валідація набору RRset
[[nodiscard]] std::expected<bool, ValidationError>
validate_rrset(const RRSig& sig,
               std::span<const uint8_t> owner_wire,
               uint16_t rr_class,
               std::vector<RREntry>& entries,
               const DNSKey& key,
               uint32_t current_time) {
    if (current_time < sig.sig_inception || current_time > sig.sig_expiration) {
        return std::unexpected(ValidationError::InvalidTimeWindow);
    }

    if (sig.algorithm != 13 || key.algorithm != 13) {
        return std::unexpected(ValidationError::UnsupportedAlgorithm);
    }

    if (sig.key_tag != calculate_key_tag(key.rdata_raw)) {
        return std::unexpected(ValidationError::KeyTagMismatch);
    }

    // Канонічне впорядкування записів набору за вмістом RDATA
    std::ranges::sort(entries, [](const RREntry& a, const RREntry& b) {
        auto min_len = std::min(a.rdata.size(), b.rdata.size());
        auto cmp = std::memcmp(a.rdata.data(), b.rdata.data(), min_len);
        if (cmp != 0) return cmp < 0;
        return a.rdata.size() < b.rdata.size();
    });

    EvpMdCtxPtr md_ctx(EVP_MD_CTX_new());
    if (!md_ctx || EVP_DigestInit_ex(md_ctx.get(), EVP_sha256(), nullptr) <= 0) {
        return std::unexpected(ValidationError::CryptoFailure);
    }

    // Підписний заголовок RRSIG
    std::array<uint8_t, 18> hdr = {
        static_cast<uint8_t>(sig.type_covered >> 8),
        static_cast<uint8_t>(sig.type_covered & 0xFF),
        sig.algorithm,
        sig.labels,
        static_cast<uint8_t>((sig.original_ttl >> 24) & 0xFF),
        static_cast<uint8_t>((sig.original_ttl >> 16) & 0xFF),
        static_cast<uint8_t>((sig.original_ttl >> 8) & 0xFF),
        static_cast<uint8_t>(sig.original_ttl & 0xFF),
        static_cast<uint8_t>((sig.sig_expiration >> 24) & 0xFF),
        static_cast<uint8_t>((sig.sig_expiration >> 16) & 0xFF),
        static_cast<uint8_t>((sig.sig_expiration >> 8) & 0xFF),
        static_cast<uint8_t>(sig.sig_expiration & 0xFF),
        static_cast<uint8_t>((sig.sig_inception >> 24) & 0xFF),
        static_cast<uint8_t>((sig.sig_inception >> 16) & 0xFF),
        static_cast<uint8_t>((sig.sig_inception >> 8) & 0xFF),
        static_cast<uint8_t>(sig.sig_inception & 0xFF),
        static_cast<uint8_t>(sig.key_tag >> 8),
        static_cast<uint8_t>(sig.key_tag & 0xFF)
    };

    EVP_DigestUpdate(md_ctx.get(), hdr.data(), hdr.size());
    EVP_DigestUpdate(md_ctx.get(), sig.signer_name.data(), sig.signer_name.size());

    // Підписні записи
    std::array<uint8_t, 10> prefix = {
        hdr[0], hdr[1],
        static_cast<uint8_t>(rr_class >> 8),
        static_cast<uint8_t>(rr_class & 0xFF),
        hdr[4], hdr[5], hdr[6], hdr[7], // Original TTL
        0, 0 // RDLENGTH
    };

    for (const auto& entry : entries) {
        EVP_DigestUpdate(md_ctx.get(), owner_wire.data(), owner_wire.size());
        prefix[8] = static_cast<uint8_t>(entry.rdata.size() >> 8);
        prefix[9] = static_cast<uint8_t>(entry.rdata.size() & 0xFF);
        EVP_DigestUpdate(md_ctx.get(), prefix.data(), prefix.size());
        EVP_DigestUpdate(md_ctx.get(), entry.rdata.data(), entry.rdata.size());
    }

    std::array<uint8_t, SHA256_DIGEST_LENGTH> digest{};
    EVP_DigestFinal_ex(md_ctx.get(), digest.data(), nullptr);

    if (key.pubkey.size() != 64 || sig.signature.size() != 64) {
        return std::unexpected(ValidationError::MalformedKeyData);
    }

    std::array<uint8_t, 65> uncompressed_pt = {0x04};
    std::copy_n(key.pubkey.begin(), 64, uncompressed_pt.begin() + 1);

    EcKeyPtr eckey(EC_KEY_new_by_curve_name(NID_X9_62_prime256v1));
    if (!eckey || EC_KEY_oct2key(eckey.get(), uncompressed_pt.data(), uncompressed_pt.size(), nullptr) <= 0) {
        return std::unexpected(ValidationError::MalformedKeyData);
    }

    EcdsaSigPtr ec_sig(ECDSA_SIG_new());
    BIGNUM* r = BN_bin2bn(sig.signature.data(), 32, nullptr);
    BIGNUM* s = BN_bin2bn(sig.signature.data() + 32, 32, nullptr);
    ECDSA_SIG_set0(ec_sig.get(), r, s);

    int status = ECDSA_do_verify(digest.data(), digest.size(), ec_sig.get(), eckey.get());
    if (status != 1) {
        return std::unexpected(ValidationError::SignatureInvalid);
    }

    return true;
}

} // namespace dnssec
