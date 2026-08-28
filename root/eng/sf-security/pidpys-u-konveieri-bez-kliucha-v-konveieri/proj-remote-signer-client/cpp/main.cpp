#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <expected>
#include <iomanip>
#include <sstream>
#include <openssl/evp.h>
#include <openssl/ssl.h>
#include <openssl/bio.h>
#include <openssl/err.h>

namespace signing {

// RAII обгортки для структур OpenSSL
struct EvpMdCtxDeleter { void operator()(EVP_MD_CTX *ctx) const { if (ctx) EVP_MD_CTX_free(ctx); } };
struct SslCtxDeleter   { void operator()(SSL_CTX *ctx) const   { if (ctx) SSL_CTX_free(ctx); } };
struct BioDeleter      { void operator()(BIO *bio) const       { if (bio) BIO_free_all(bio); } };

using ScopedMdCtx  = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;
using ScopedSslCtx = std::unique_ptr<SSL_CTX, SslCtxDeleter>;
using ScopedBio    = std::unique_ptr<BIO, BioDeleter>;

constexpr size_t DigestSize = 32;
constexpr size_t BufferSize = 8192;

using DigestArray = std::array<uint8_t, DigestSize>;

// Потокове обчислення SHA-256
std::expected<DigestArray, std::string> compute_sha256(std::string_view filepath) {
    std::ifstream file(filepath.data(), std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected("Неможливо відкрити цільовий файл: " + std::string(filepath));
    }

    ScopedMdCtx ctx(EVP_MD_CTX_new());
    if (!ctx || EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) != 1) {
        return std::unexpected("Помилка ініціалізації EVP контексту");
    }

    std::vector<char> buffer(BufferSize);
    while (file.read(buffer.data(), buffer.size()) || file.gcount() > 0) {
        if (EVP_DigestUpdate(ctx.get(), buffer.data(), file.gcount()) != 1) {
            return std::unexpected("Помилка оновлення EVP дайджесту");
        }
    }

    DigestArray digest{};
    unsigned int len = 0;
    if (EVP_DigestFinal_ex(ctx.get(), digest.data(), &len) != 1 || len != DigestSize) {
        return std::unexpected("Помилка фіналізації EVP дайджесту");
    }

    return digest;
}

std::string to_hex(std::span<const uint8_t> bytes) {
    std::ostringstream oss;
    for (uint8_t b : bytes) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    return oss.str();
}

class RemoteSignerClient {
public:
    RemoteSignerClient(std::string host_port, std::string ca_path, std::string cert_path = "", std::string key_path = "")
        : host_port_(std::move(host_port)), ca_path_(std::move(ca_path)), cert_path_(std::move(cert_path)), key_path_(std::move(key_path)) {}

    std::expected<std::string, std::string> sign(std::string_view hex_digest, std::string_view oidc_token, std::string_view key_alias) {
        ScopedSslCtx ctx(SSL_CTX_new(TLS_client_method()));
        if (!ctx) return std::unexpected("Помилка створення SSL_CTX");

        SSL_CTX_set_min_proto_version(ctx.get(), TLS1_3_VERSION);

        if (SSL_CTX_load_verify_locations(ctx.get(), ca_path_.c_str(), nullptr) != 1) {
            return std::unexpected("Помилка завантаження CA сертифіката");
        }

        if (!cert_path_.empty() && !key_path_.empty()) {
            if (SSL_CTX_use_certificate_file(ctx.get(), cert_path_.c_str(), SSL_FILETYPE_PEM) != 1 ||
                SSL_CTX_use_PrivateKey_file(ctx.get(), key_path_.c_str(), SSL_FILETYPE_PEM) != 1) {
                return std::unexpected("Помилка налаштування клієнтського сертифіката mTLS");
            }
        }

        ScopedBio bio(BIO_new_ssl_connect(ctx.get()));
        if (!bio) return std::unexpected("Помилка створення BIO з'єднання");

        BIO_set_conn_hostname(bio.get(), host_port_.c_str());

        SSL *ssl = nullptr;
        BIO_get_ssl(bio.get(), &ssl);
        if (!ssl) return std::unexpected("Неможливо отримати SSL об'єкт із BIO");

        SSL_set_tlsext_host_name(ssl, "signing.internal.acme.net");

        if (BIO_do_connect(bio.get()) <= 0) {
            return std::unexpected("Помилка встановлення захищеного TCP/TLS з'єднання");
        }

        std::string json_body = "{\"digest\":\"" + std::string(hex_digest) +
                                "\",\"algorithm\":\"ECDSA_P256\",\"oidc_token\":\"" +
                                std::string(oidc_token) + "\",\"key_alias\":\"" +
                                std::string(key_alias) + "\"}";

        std::string request = "POST /api/v1/sign HTTP/1.1\r\n"
                              "Host: signing.internal.acme.net\r\n"
                              "Content-Type: application/json\r\n"
                              "Content-Length: " + std::to_string(json_body.size()) + "\r\n"
                              "Connection: close\r\n\r\n" + json_body;

        BIO_write(bio.get(), request.data(), static_cast<int>(request.size()));

        std::vector<char> resp_buf(BufferSize);
        std::string response;
        int read_bytes = 0;
        while ((read_bytes = BIO_read(bio.get(), resp_buf.data(), static_cast<int>(resp_buf.size()))) > 0) {
            response.append(resp_buf.data(), read_bytes);
        }

        return response;
    }

private:
    std::string host_port_;
    std::string ca_path_;
    std::string cert_path_;
    std::string key_path_;
};

} // namespace signing

int main(int argc, char *argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_артефакту> <oidc_token>\n";
        return 1;
    }

    auto digest_res = signing::compute_sha256(argv[1]);
    if (!digest_res) {
        std::cerr << "Помилка гешування: " << digest_res.error() << '\n';
        return 1;
    }

    std::string hex_hash = signing::to_hex(*digest_res);
    signing::RemoteSignerClient client("10.240.12.45:8443", "ca.crt", "runner.crt", "runner.key");

    auto sign_res = client.sign(hex_hash, argv[2], "firmware-prod");
    if (!sign_res) {
        std::cerr << "Помилка віддаленого підпису: " << sign_res.error() << '\n';
        return 1;
    }

    std::cout << "Сервіс успішно згенерував підпис:\n" << *sign_res << '\n';
    return 0;
}
