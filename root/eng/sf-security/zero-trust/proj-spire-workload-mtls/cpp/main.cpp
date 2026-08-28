#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <vector>
#include <cstring>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

namespace zero_trust {

// RAII делетери для ресурсів C API OpenSSL
struct OpenSSLDeleter {
    void operator()(SSL_CTX* ctx) const noexcept { if (ctx) SSL_CTX_free(ctx); }
    void operator()(SSL* ssl) const noexcept { if (ssl) SSL_free(ssl); }
    void operator()(X509* cert) const noexcept { if (cert) X509_free(cert); }
    void operator()(EVP_PKEY* pkey) const noexcept { if (pkey) EVP_PKEY_free(pkey); }
    void operator()(BIO* bio) const noexcept { if (bio) BIO_free(bio); }
    void operator()(GENERAL_NAMES* gn) const noexcept { if (gn) GENERAL_NAMES_free(gn); }
};

using SslCtxPtr = std::unique_ptr<SSL_CTX, OpenSSLDeleter>;
using X509Ptr   = std::unique_ptr<X509, OpenSSLDeleter>;
using EvpKeyPtr = std::unique_ptr<EVP_PKEY, OpenSSLDeleter>;
using BioPtr    = std::unique_ptr<BIO, OpenSSLDeleter>;

enum class SecurityError {
    CertificateMissing,
    SanExtensionNotFound,
    InvalidSpiffeUri,
    ContextInitFailed,
    PermissionDenied
};

class SpiffeValidator {
public:
    // Витягування SPIFFE ID з розширення SAN URI
    static std::expected<std::string, SecurityError> extract_spiffe_id(X509* cert) noexcept {
        if (!cert) return std::unexpected(SecurityError::CertificateMissing);

        int san_loc = X509_get_ext_by_NID(cert, NID_subject_alt_name, -1);
        if (san_loc < 0) return std::unexpected(SecurityError::SanExtensionNotFound);

        X509_EXTENSION* ext = X509_get_ext(cert, san_loc);
        if (!ext) return std::unexpected(SecurityError::SanExtensionNotFound);

        std::unique_ptr<GENERAL_NAMES, OpenSSLDeleter> names(
            static_cast<GENERAL_NAMES*>(X509V3_EXT_d2i(ext))
        );
        if (!names) return std::unexpected(SecurityError::SanExtensionNotFound);

        int count = sk_GENERAL_NAME_num(names.get());
        for (int i = 0; i < count; ++i) {
            GENERAL_NAME* val = sk_GENERAL_NAME_value(names.get(), i);
            if (val->type == GEN_URI) {
                const char* uri_str = reinterpret_cast<const char*>(
                    ASN1_STRING_get0_data(val->d.uniformResourceIdentifier)
                );
                int uri_len = ASN1_STRING_length(val->d.uniformResourceIdentifier);
                std::string_view uri(uri_str, static_cast<std::size_t>(uri_len));

                if (uri.starts_with("spiffe://")) {
                    return std::string(uri);
                }
            }
        }

        return std::unexpected(SecurityError::InvalidSpiffeUri);
    }

    // Авторизація запиту (Deny-by-Default)
    static bool is_authorized(std::string_view spiffe_id,
                             std::string_view method,
                             std::string_view path) noexcept {
        if (spiffe_id == "spiffe://prod.corp/ns/billing/sa/checkout") {
            return (method == "POST" && path == "/v1/charge");
        }
        if (spiffe_id == "spiffe://prod.corp/ns/security/sa/auditor") {
            return (method == "GET");
        }
        return false;
    }
};

class SecureTlsContext {
public:
    static std::expected<SslCtxPtr, SecurityError> create(std::string_view cert_pem,
                                                          std::string_view key_pem,
                                                          std::string_view ca_bundle_pem) {
        SslCtxPtr ctx(SSL_CTX_new(TLS_server_method()));
        if (!ctx) return std::unexpected(SecurityError::ContextInitFailed);

        SSL_CTX_set_min_proto_version(ctx.get(), TLS1_3_VERSION);
        SSL_CTX_set_verify(ctx.get(), SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT, nullptr);

        // Завантаження CA зв'язки
        BioPtr ca_bio(BIO_new_mem_buf(ca_bundle_pem.data(), static_cast<int>(ca_bundle_pem.size())));
        STACK_OF(X509_INFO)* inf = PEM_X509_INFO_read_bio(ca_bio.get(), nullptr, nullptr, nullptr);
        if (inf) {
            X509_STORE* store = SSL_CTX_get_cert_store(ctx.get());
            for (int i = 0; i < sk_X509_INFO_num(inf); ++i) {
                X509_INFO* item = sk_X509_INFO_value(inf, i);
                if (item->x509) X509_STORE_add_cert(store, item->x509);
            }
            sk_X509_INFO_pop_free(inf, X509_INFO_free);
        }

        // Завантаження сертифіката
        BioPtr cert_bio(BIO_new_mem_buf(cert_pem.data(), static_cast<int>(cert_pem.size())));
        X509Ptr cert(PEM_read_bio_X509(cert_bio.get(), nullptr, nullptr, nullptr));
        if (!cert || SSL_CTX_use_certificate(ctx.get(), cert.get()) <= 0) {
            return std::unexpected(SecurityError::ContextInitFailed);
        }

        // Завантаження ключа
        BioPtr key_bio(BIO_new_mem_buf(key_pem.data(), static_cast<int>(key_pem.size())));
        EvpKeyPtr pkey(PEM_read_bio_PrivateKey(key_bio.get(), nullptr, nullptr, nullptr));
        if (!pkey || SSL_CTX_use_PrivateKey(ctx.get(), pkey.get()) <= 0) {
            return std::unexpected(SecurityError::ContextInitFailed);
        }

        return ctx;
    }
};

} // namespace zero_trust
