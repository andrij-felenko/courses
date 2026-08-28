#include <expected>
#include <filesystem>
#include <format>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

#include <openssl/bio.h>
#include <openssl/cms.h>
#include <openssl/err.h>
#include <openssl/pem.h>
#include <openssl/x509.h>
#include <openssl/x509_vfy.h>

namespace fs = std::filesystem;

namespace crypto {

// RAII делектори для об'єктів OpenSSL
struct OpenSslDeleter {
    void operator()(BIO* b) const noexcept { BIO_free(b); }
    void operator()(X509* x) const noexcept { X509_free(x); }
    void operator()(EVP_PKEY* k) const noexcept { EVP_PKEY_free(k); }
    void operator()(CMS_ContentInfo* c) const noexcept { CMS_ContentInfo_free(c); }
    void operator()(X509_STORE* s) const noexcept { X509_STORE_free(s); }
    void operator()(ASN1_OCTET_STRING* o) const noexcept { ASN1_OCTET_STRING_free(o); }
    void operator()(ASN1_OBJECT* o) const noexcept { ASN1_OBJECT_free(o); }
    void operator()(X509_CRL* c) const noexcept { X509_CRL_free(c); }
};

template <typename T>
using SslPtr = std::unique_ptr<T, OpenSslDeleter>;

[[nodiscard]] std::string get_openssl_errors() {
    SslPtr<BIO> bio_err{BIO_new(BIO_s_mem())};
    ERR_print_errors(bio_err.get());
    char* data = nullptr;
    long len = BIO_get_mem_data(bio_err.get(), &data);
    return (data && len > 0) ? std::string(data, static_cast<size_t>(len)) : "Невідома криптографічна помилка";
}

// Створення відокремленого підпису CMS
[[nodiscard]] std::expected<void, std::string> sign_detached(
    const fs::path& data_path,
    const fs::path& cert_path,
    const fs::path& key_path,
    const fs::path& out_p7s_path) noexcept {

    SslPtr<BIO> cert_bio{BIO_new_file(cert_path.string().c_str(), "r")};
    if (!cert_bio) return std::unexpected(std::format("Не вдалося відкрити {}", cert_path.string()));

    SslPtr<X509> cert{PEM_read_bio_X509(cert_bio.get(), nullptr, nullptr, nullptr)};
    if (!cert) return std::unexpected(std::format("Помилка сертифіката: {}", get_openssl_errors()));

    SslPtr<BIO> key_bio{BIO_new_file(key_path.string().c_str(), "r")};
    if (!key_bio) return std::unexpected(std::format("Не вдалося відкрити {}", key_path.string()));

    SslPtr<EVP_PKEY> pkey{PEM_read_bio_PrivateKey(key_bio.get(), nullptr, nullptr, nullptr)};
    if (!pkey) return std::unexpected(std::format("Помилка приватного ключа: {}", get_openssl_errors()));

    SslPtr<BIO> in_data{BIO_new_file(data_path.string().c_str(), "rb")};
    if (!in_data) return std::unexpected(std::format("Не вдалося відкрити {}", data_path.string()));

    constexpr unsigned int flags = CMS_DETACHED | CMS_BINARY | CMS_NOSMIMECAP | CMS_STREAM;
    SslPtr<CMS_ContentInfo> cms{CMS_sign(cert.get(), pkey.get(), nullptr, in_data.get(), flags)};
    if (!cms) return std::unexpected(std::format("CMS_sign помилка: {}", get_openssl_errors()));

    SslPtr<BIO> out_sig{BIO_new_file(out_p7s_path.string().c_str(), "wb")};
    if (!out_sig) return std::unexpected(std::format("Не вдалося створити {}", out_p7s_path.string()));

    if (!i2d_CMS_bio_stream(out_sig.get(), cms.get(), in_data.get(), flags)) {
        return std::unexpected(std::format("Помилка серіалізації DER: {}", get_openssl_errors()));
    }

    return {};
}

// Потокова перевірка відокремленого підпису CMS
[[nodiscard]] std::expected<void, std::string> verify_detached(
    const fs::path& data_path,
    const fs::path& sig_p7s_path,
    const fs::path& ca_path) noexcept {

    SslPtr<X509_STORE> store{X509_STORE_new()};
    if (!store) return std::unexpected("Помилка виділення пам'яті під X509_STORE");

    if (!X509_STORE_load_locations(store.get(), ca_path.string().c_str(), nullptr)) {
        return std::unexpected(std::format("Помилка завантаження CA {}: {}", ca_path.string(), get_openssl_errors()));
    }

    SslPtr<BIO> in_sig{BIO_new_file(sig_p7s_path.string().c_str(), "rb")};
    if (!in_sig) return std::unexpected(std::format("Не вдалося відкрити підпис {}", sig_p7s_path.string()));

    SslPtr<CMS_ContentInfo> cms{d2i_CMS_bio(in_sig.get(), nullptr)};
    if (!cms) return std::unexpected(std::format("Помилка парсингу DER CMS: {}", get_openssl_errors()));

    SslPtr<BIO> in_data{BIO_new_file(data_path.string().c_str(), "rb")};
    if (!in_data) return std::unexpected(std::format("Не вдалося відкрити дані {}", data_path.string()));

    constexpr unsigned int flags = CMS_BINARY;
    if (CMS_verify(cms.get(), nullptr, store.get(), in_data.get(), nullptr, flags) <= 0) {
        return std::unexpected(std::format("Перевірка CMS не пройдена: {}", get_openssl_errors()));
    }

    return {};
}

} // namespace crypto
