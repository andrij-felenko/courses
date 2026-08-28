#pragma once

#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <optional>
#include <cstdint>
#include <chrono>
#include <algorithm>

#include <openssl/evp.h>
#include <openssl/ec.h>
#include <openssl/ecdsa.h>
#include <openssl/bn.h>
#include <openssl/param_build.h>
#include <openssl/core_names.h>

namespace dnssec {

enum class ValidationError {
    Expired,
    NotYetValid,
    KeyTagMismatch,
    MalformedKey,
    MalformedSignature,
    CryptoFailure,
    MemoryError
};

struct RRSIGRecord {
    uint16_t type_covered;
    uint8_t  algorithm;
    uint8_t  labels;
    uint32_t original_ttl;
    uint32_t expiration;
    uint32_t inception;
    uint16_t key_tag;
    std::string signer_name;
    std::vector<uint8_t> signature;
};

struct DNSKEYRecord {
    uint16_t flags;
    uint8_t  protocol;
    uint8_t  algorithm;
    std::vector<uint8_t> pubkey;
};

/* RAII Deleters для OpenSSL */
struct EVP_PKEY_deleter { void operator()(EVP_PKEY* p) const { EVP_PKEY_free(p); } };
struct EVP_PKEY_CTX_deleter { void operator()(EVP_PKEY_CTX* p) const { EVP_PKEY_CTX_free(p); } };
struct EVP_MD_CTX_deleter { void operator()(EVP_MD_CTX* p) const { EVP_MD_CTX_free(p); } };
struct OSSL_PARAM_BLD_deleter { void operator()(OSSL_PARAM_BLD* p) const { OSSL_PARAM_BLD_free(p); } };
struct OSSL_PARAM_deleter { void operator()(OSSL_PARAM* p) const { OSSL_PARAM_free(p); } };
struct BIGNUM_deleter { void operator()(BIGNUM* p) const { BN_free(p); } };
struct ECDSA_SIG_deleter { void operator()(ECDSA_SIG* p) const { ECDSA_SIG_free(p); } };

using ScopedEVP_PKEY = std::unique_ptr<EVP_PKEY, EVP_PKEY_deleter>;
using ScopedEVP_PKEY_CTX = std::unique_ptr<EVP_PKEY_CTX, EVP_PKEY_CTX_deleter>;
using ScopedEVP_MD_CTX = std::unique_ptr<EVP_MD_CTX, EVP_MD_CTX_deleter>;

class DNSSECValidator {
public:
    static uint16_t CalculateKeyTag(std::span<const uint8_t> rdata) noexcept {
        if (rdata.size() < 4) return 0;
        uint32_t ac = 0;
        for (size_t i = 0; i < rdata.size(); ++i) {
            ac += (i & 1) ? rdata[i] : (static_cast<uint32_t>(rdata[i]) << 8);
        }
        ac += (ac >> 16) & 0xFFFF;
        return static_cast<uint16_t>(ac & 0xFFFF);
    }

    static std::expected<void, ValidationError> VerifySignature(
        const RRSIGRecord& rrsig,
        const DNSKEYRecord& dnskey,
        std::span<const uint8_t> preimage,
        std::chrono::system_clock::time_point current_time
    ) {
        using namespace std::chrono;
        auto now_sec = duration_cast<seconds>(current_time.time_since_epoch()).count();
        constexpr int64_t skew_tolerance = 300;

        if (now_sec + skew_tolerance < static_cast<int64_t>(rrsig.inception)) {
            return std::unexpected(ValidationError::NotYetValid);
        }
        if (now_sec - skew_tolerance > static_cast<int64_t>(rrsig.expiration)) {
            return std::unexpected(ValidationError::Expired);
        }

        if (dnskey.algorithm != rrsig.algorithm) {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        ScopedEVP_PKEY pkey;
        std::vector<uint8_t> der_sig_storage;
        std::span<const uint8_t> sig_to_verify = rrsig.signature;

        if (rrsig.algorithm == 13) { // ECDSA P-256
            auto built_pkey = BuildECDSAPKey(dnskey.pubkey);
            if (!built_pkey) return std::unexpected(ValidationError::MalformedKey);
            pkey = std::move(*built_pkey);

            auto der_sig = RawECDSAToDER(rrsig.signature);
            if (!der_sig) return std::unexpected(ValidationError::MalformedSignature);
            der_sig_storage = std::move(*der_sig);
            sig_to_verify = der_sig_storage;
        } else if (rrsig.algorithm == 8) { // RSA-SHA256
            auto built_pkey = BuildRSAPKey(dnskey.pubkey);
            if (!built_pkey) return std::unexpected(ValidationError::MalformedKey);
            pkey = std::move(*built_pkey);
        } else {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        ScopedEVP_MD_CTX mctx(EVP_MD_CTX_new());
        if (!mctx) return std::unexpected(ValidationError::MemoryError);

        if (EVP_DigestVerifyInit(mctx.get(), nullptr, EVP_sha256(), nullptr, pkey.get()) <= 0) {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        if (EVP_DigestVerifyUpdate(mctx.get(), preimage.data(), preimage.size()) <= 0) {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        if (EVP_DigestVerifyFinal(mctx.get(), sig_to_verify.data(), sig_to_verify.size()) != 1) {
            return std::unexpected(ValidationError::CryptoFailure);
        }

        return {};
    }

private:
    static std::optional<ScopedEVP_PKEY> BuildECDSAPKey(std::span<const uint8_t> pubkey) {
        if (pubkey.size() != 64) return std::nullopt;

        std::vector<uint8_t> uncompressed_pt(65);
        uncompressed_pt[0] = 0x04;
        std::copy(pubkey.begin(), pubkey.end(), uncompressed_pt.begin() + 1);

        ScopedEVP_PKEY_CTX pctx(EVP_PKEY_CTX_new_from_name(nullptr, "EC", nullptr));
        if (!pctx || EVP_PKEY_fromdata_init(pctx.get()) <= 0) return std::nullopt;

        std::unique_ptr<OSSL_PARAM_BLD, OSSL_PARAM_BLD_deleter> bld(OSSL_PARAM_BLD_new());
        OSSL_PARAM_BLD_push_utf8_string(bld.get(), OSSL_PKEY_PARAM_GROUP_NAME, "prime256v1", 0);
        OSSL_PARAM_BLD_push_octet_string(bld.get(), OSSL_PKEY_PARAM_PUB_KEY, uncompressed_pt.data(), uncompressed_pt.size());

        std::unique_ptr<OSSL_PARAM, OSSL_PARAM_deleter> params(OSSL_PARAM_BLD_to_param(bld.get()));
        EVP_PKEY* raw_pkey = nullptr;
        if (EVP_PKEY_fromdata(pctx.get(), &raw_pkey, EVP_PKEY_PUBLIC_KEY, params.get()) <= 0) {
            return std::nullopt;
        }
        return ScopedEVP_PKEY(raw_pkey);
    }

    static std::optional<ScopedEVP_PKEY> BuildRSAPKey(std::span<const uint8_t> pubkey) {
        if (pubkey.size() < 3) return std::nullopt;
        size_t elen = pubkey[0];
        size_t offset = 1;
        if (elen == 0) {
            if (pubkey.size() < 5) return std::nullopt;
            elen = (static_cast<size_t>(pubkey[1]) << 8) | pubkey[2];
            offset = 3;
        }
        if (pubkey.size() < offset + elen) return std::nullopt;

        std::unique_ptr<BIGNUM, BIGNUM_deleter> e(BN_bin2bn(pubkey.data() + offset, static_cast<int>(elen), nullptr));
        std::unique_ptr<BIGNUM, BIGNUM_deleter> n(BN_bin2bn(pubkey.data() + offset + elen, static_cast<int>(pubkey.size() - offset - elen), nullptr));
        if (!e || !n) return std::nullopt;

        ScopedEVP_PKEY_CTX pctx(EVP_PKEY_CTX_new_from_name(nullptr, "RSA", nullptr));
        if (!pctx || EVP_PKEY_fromdata_init(pctx) <= 0) return std::nullopt;

        std::unique_ptr<OSSL_PARAM_BLD, OSSL_PARAM_BLD_deleter> bld(OSSL_PARAM_BLD_new());
        OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_N, n.get());
        OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_E, e.get());

        std::unique_ptr<OSSL_PARAM, OSSL_PARAM_deleter> params(OSSL_PARAM_BLD_to_param(bld.get()));
        EVP_PKEY* raw_pkey = nullptr;
        if (EVP_PKEY_fromdata(pctx.get(), &raw_pkey, EVP_PKEY_PUBLIC_KEY, params.get()) <= 0) {
            return std::nullopt;
        }
        return ScopedEVP_PKEY(raw_pkey);
    }

    static std::optional<std::vector<uint8_t>> RawECDSAToDER(std::span<const uint8_t> raw_sig) {
        if (raw_sig.size() != 64) return std::nullopt;

        std::unique_ptr<BIGNUM, BIGNUM_deleter> r(BN_bin2bn(raw_sig.data(), 32, nullptr));
        std::unique_ptr<BIGNUM, BIGNUM_deleter> s(BN_bin2bn(raw_sig.data() + 32, 32, nullptr));
        if (!r || !s) return std::nullopt;

        std::unique_ptr<ECDSA_SIG, ECDSA_SIG_deleter> sig(ECDSA_SIG_new());
        if (!sig) return std::nullopt;

        ECDSA_SIG_set0(sig.get(), r.release(), s.release());

        int der_len = i2d_ECDSA_SIG(sig.get(), nullptr);
        if (der_len <= 0) return std::nullopt;

        std::vector<uint8_t> der_buf(static_cast<size_t>(der_len));
        uint8_t* p = der_buf.data();
        i2d_ECDSA_SIG(sig.get(), &p);

        return der_buf;
    }
};

} // namespace dnssec
