#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>
#include <openssl/param_build.h>
#include <openssl/core_names.h>

// RAII-обгортки для ресурсів OpenSSL 3.0
struct EvpPkeyDeleter { void operator()(EVP_PKEY* p) const { EVP_PKEY_free(p); } };
struct EvpMdCtxDeleter { void operator()(EVP_MD_CTX* p) const { EVP_MD_CTX_free(p); } };
struct OsslParamBldDeleter { void operator()(OSSL_PARAM_BLD* p) const { OSSL_PARAM_BLD_free(p); } };
struct OsslParamDeleter { void operator()(OSSL_PARAM* p) const { OSSL_PARAM_free(p); } };

using ScopedPkey = std::unique_ptr<EVP_PKEY, EvpPkeyDeleter>;
using ScopedMdCtx = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

// Допоміжна функція декодування Base64URL
std::vector<uint8_t> base64url_decode(std::string_view input) {
    std::string b64(input);
    for (char& c : b64) {
        if (c == '-') c = '+';
        else if (c == '_') c = '/';
    }
    while (b64.size() % 4 != 0) {
        b64.push_back('=');
    }

    std::vector<uint8_t> out(b64.size());
    BIO* bio = BIO_new_mem_buf(b64.data(), static_cast<int>(b64.size()));
    BIO* b64_filter = BIO_new(BIO_f_base64());
    BIO_set_flags(b64_filter, BIO_FLAGS_BASE64_NO_NL);
    bio = BIO_push(b64_filter, bio);

    int decoded_len = BIO_read(bio, out.data(), static_cast<int>(out.size()));
    BIO_free_all(bio);

    if (decoded_len < 0) {
        throw std::runtime_error("Помилка декодування Base64URL");
    }
    out.resize(decoded_len);
    return out;
}

// Побудова EVP_PKEY з публічних компонентів RSA (OpenSSL 3.0+)
ScopedPkey create_rsa_public_key(std::string_view n_b64url, std::string_view e_b64url) {
    auto n_bytes = base64url_decode(n_b64url);
    auto e_bytes = base64url_decode(e_b64url);

    std::unique_ptr<OSSL_PARAM_BLD, OsslParamBldDeleter> bld(OSSL_PARAM_BLD_new());
    if (!bld) throw std::runtime_error("Не вдалося створити OSSL_PARAM_BLD");

    BIGNUM* n_bn = BN_bin2bn(n_bytes.data(), static_cast<int>(n_bytes.size()), nullptr);
    BIGNUM* e_bn = BN_bin2bn(e_bytes.data(), static_cast<int>(e_bytes.size()), nullptr);

    OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_N, n_bn);
    OSSL_PARAM_BLD_push_BN(bld.get(), OSSL_PKEY_PARAM_RSA_E, e_bn);
    BN_free(n_bn);
    BN_free(e_bn);

    std::unique_ptr<OSSL_PARAM, OsslParamDeleter> params(OSSL_PARAM_BLD_to_param(bld.get()));
    if (!params) throw std::runtime_error("Не вдалося згенерувати OSSL_PARAM");

    EVP_PKEY_CTX* ctx = EVP_PKEY_CTX_new_from_name(nullptr, "RSA", nullptr);
    if (!ctx) throw std::runtime_error("Помилка створення EVP_PKEY_CTX");

    EVP_PKEY* pkey_raw = nullptr;
    EVP_PKEY_fromdata_init(ctx);
    if (EVP_PKEY_fromdata(ctx, &pkey_raw, EVP_PKEY_PUBLIC_KEY, params.get()) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        throw std::runtime_error("Помилка створення EVP_PKEY з параметрів RSA");
    }
    EVP_PKEY_CTX_free(ctx);

    return ScopedPkey(pkey_raw);
}

// Верифікація підпису RS256 для підписаного блоку JWT
bool verify_rs256_signature(
    std::string_view signed_data,
    std::string_view signature_b64url,
    EVP_PKEY* public_key
) {
    auto signature = base64url_decode(signature_b64url);

    ScopedMdCtx md_ctx(EVP_MD_CTX_new());
    if (!md_ctx) return false;

    if (EVP_DigestVerifyInit(md_ctx.get(), nullptr, EVP_sha256(), nullptr, public_key) <= 0) {
        return false;
    }

    if (EVP_DigestVerifyUpdate(md_ctx.get(), signed_data.data(), signed_data.size()) <= 0) {
        return false;
    }

    int rc = EVP_DigestVerifyFinal(md_ctx.get(), signature.data(), signature.size());
    return (rc == 1);
}
