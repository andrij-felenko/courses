#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <span>
#include <expected>
#include <array>
#include <openssl/x509.h>
#include <openssl/x509v3.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/evp.h>

namespace crypto {

/* Користувацькі деструктори для об'єктів OpenSSL (RAII) */
struct OpenSSLDeleter {
    void operator()(BIO *b) const noexcept { if (b) BIO_free(b); }
    void operator()(X509 *x) const noexcept { if (x) X509_free(x); }
    void operator()(X509_STORE *s) const noexcept { if (s) X509_STORE_free(s); }
    void operator()(X509_STORE_CTX *c) const noexcept { if (c) X509_STORE_CTX_free(c); }
    void operator()(EVP_MD_CTX *m) const noexcept { if (m) EVP_MD_CTX_free(m); }
    void operator()(STACK_OF(X509) *st) const noexcept { if (st) sk_X509_free(st); }
    void operator()(void *p) const noexcept { if (p) OPENSSL_free(p); }
};

using BioPtr         = std::unique_ptr<BIO, OpenSSLDeleter>;
using X509Ptr        = std::unique_ptr<X509, OpenSSLDeleter>;
using StorePtr       = std::unique_ptr<X509_STORE, OpenSSLDeleter>;
using StoreCtxPtr    = std::unique_ptr<X509_STORE_CTX, OpenSSLDeleter>;
using MdCtxPtr       = std::unique_ptr<EVP_MD_CTX, OpenSSLDeleter>;
using X509StackPtr   = std::unique_ptr<STACK_OF(X509), OpenSSLDeleter>;

struct VerificationSuccess {
    std::array<uint8_t, 32> spki_sha256;
    std::string subject_name;
    std::string issuer_name;
};

struct VerificationFailure {
    int error_code;
    std::string error_message;
};

class CertificateVerifier {
public:
    /* Додавання довіреного кореневого сертифіката (Trust Anchor) */
    bool add_trusted_root_pem(std::string_view root_pem) {
        if (!store_) {
            store_.reset(X509_STORE_new());
            if (!store_) return false;
        }

        BioPtr bio(BIO_new_mem_buf(root_pem.data(), static_cast<int>(root_pem.size())));
        if (!bio) return false;

        X509Ptr root(PEM_read_bio_X509(bio.get(), nullptr, nullptr, nullptr));
        if (!root) return false;

        return X509_STORE_add_cert(store_.get(), root.get()) == 1;
    }

    /* Верифікація кінцевого сертифіката з проміжними та перевіркою SAN */
    std::expected<VerificationSuccess, VerificationFailure> verify_chain(
        std::string_view leaf_pem,
        std::span<const std::string> intermediates_pem,
        std::string_view expected_hostname
    ) const {
        if (!store_) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Trust store is uninitialized"
            });
        }

        BioPtr leaf_bio(BIO_new_mem_buf(leaf_pem.data(), static_cast<int>(leaf_pem.size())));
        if (!leaf_bio) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Failed to allocate leaf BIO buffer"
            });
        }

        X509Ptr leaf(PEM_read_bio_X509(leaf_bio.get(), nullptr, nullptr, nullptr));
        if (!leaf) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Failed to parse leaf certificate PEM"
            });
        }

        X509StackPtr untrusted_stack(sk_X509_new_null());
        if (!untrusted_stack) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Failed to allocate intermediate stack"
            });
        }

        std::vector<X509Ptr> parsed_intermediates;
        for (const auto &interm_str : intermediates_pem) {
            BioPtr bio(BIO_new_mem_buf(interm_str.data(), static_cast<int>(interm_str.size())));
            if (!bio) continue;
            X509Ptr cert(PEM_read_bio_X509(bio.get(), nullptr, nullptr, nullptr));
            if (cert) {
                sk_X509_push(untrusted_stack.get(), cert.get());
                parsed_intermediates.push_back(std::move(cert));
            }
        }

        StoreCtxPtr ctx(X509_STORE_CTX_new());
        if (!ctx || X509_STORE_CTX_init(ctx.get(), store_.get(), leaf.get(), untrusted_stack.get()) != 1) {
            return std::unexpected(VerificationFailure{
                X509_V_ERR_UNSPECIFIED, "Failed to initialize X509_STORE_CTX"
            });
        }

        if (!expected_hostname.empty()) {
            X509_VERIFY_PARAM *param = X509_STORE_CTX_get0_param(ctx.get());
            X509_VERIFY_PARAM_set_hostflags(param, X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS);
            if (X509_VERIFY_PARAM_set1_host(param, expected_hostname.data(), expected_hostname.size()) != 1) {
                return std::unexpected(VerificationFailure{
                    X509_V_ERR_UNSPECIFIED, "Failed to configure hostname verification parameters"
                });
            }
        }

        if (X509_verify_cert(ctx.get()) != 1) {
            int err = X509_STORE_CTX_get_error(ctx.get());
            return std::unexpected(VerificationFailure{
                err, X509_verify_cert_error_string(err)
            });
        }

        VerificationSuccess success;
        success.spki_sha256 = extract_spki_sha256(leaf.get());
        
        char buf[256];
        X509_NAME_oneline(X509_get_subject_name(leaf.get()), buf, sizeof(buf));
        success.subject_name = buf;
        X509_NAME_oneline(X509_get_issuer_name(leaf.get()), buf, sizeof(buf));
        success.issuer_name = buf;

        return success;
    }

private:
    StorePtr store_;

    static std::array<uint8_t, 32> extract_spki_sha256(X509 *cert) {
        std::array<uint8_t, 32> hash{};
        X509_PUBKEY *pubkey = X509_get_X509_PUBKEY(cert);
        if (!pubkey) return hash;

        unsigned char *spki_der = nullptr;
        int len = i2d_X509_PUBKEY(pubkey, &spki_der);
        std::unique_ptr<unsigned char, OpenSSLDeleter> spki_guard(spki_der);

        if (len > 0 && spki_der) {
            MdCtxPtr md_ctx(EVP_MD_CTX_new());
            if (md_ctx &&
                EVP_DigestInit_ex(md_ctx.get(), EVP_sha256(), nullptr) &&
                EVP_DigestUpdate(md_ctx.get(), spki_der, static_cast<size_t>(len))) {
                EVP_DigestFinal_ex(md_ctx.get(), hash.data(), nullptr);
            }
        }
        return hash;
    }
};

} // namespace crypto
