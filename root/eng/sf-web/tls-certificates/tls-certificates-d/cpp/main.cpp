#include <iostream>
#include <memory>
#include <string_view>
#include <stdexcept>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

// RAII обгортки для управління ресурсами OpenSSL та файловими сокетами
struct SslCtxCleaner { void operator()(SSL_CTX *ctx) const noexcept { SSL_CTX_free(ctx); } };
struct SslCleaner    { void operator()(SSL *ssl) const noexcept { SSL_free(ssl); } };
struct FdCleaner     { void operator()(int *fd) const noexcept { if (fd && *fd >= 0) { close(*fd); delete fd; } } };

using ScopedSslCtx = std::unique_ptr<SSL_CTX, SslCtxCleaner>;
using ScopedSsl    = std::unique_ptr<SSL, SslCleaner>;
using ScopedSocket = std::unique_ptr<int, FdCleaner>;

class TlsSecureClient {
public:
    TlsSecureClient(std::string_view ca_bundle_path,
                    std::string_view client_cert = "",
                    std::string_view client_key = "") {
        ctx_.reset(SSL_CTX_new(TLS_client_method()));
        if (!ctx_) {
            throw std::runtime_error("Не вдалося ініціалізувати SSL_CTX");
        }

        // Обов'язкова перевірка сертифіката віддаленого вузла
        SSL_CTX_set_verify(ctx_.get(), SSL_VERIFY_PEER, nullptr);

        if (SSL_CTX_load_verify_locations(ctx_.get(), ca_bundle_path.data(), nullptr) != 1) {
            throw std::runtime_error("Помилка завантаження CA бандла: " + std::string(ca_bundle_path));
        }

        SSL_CTX_set_min_proto_version(ctx_.get(), TLS1_2_VERSION);

        // Якщо передано сертифікат і ключ клієнта — вмикаємо mTLS
        if (!client_cert.empty() && !client_key.empty()) {
            if (SSL_CTX_use_certificate_chain_file(ctx_.get(), client_cert.data()) <= 0 ||
                SSL_CTX_use_PrivateKey_file(ctx_.get(), client_key.data(), SSL_FILETYPE_PEM) <= 0 ||
                SSL_CTX_check_private_key(ctx_.get()) != 1) {
                throw std::runtime_error("Помилка завантаження ключів mTLS клієнта");
            }
        }
    }

    void execute_get_request(std::string_view hostname, uint16_t port, std::string_view path) {
        // Налаштовуємо перевірку SAN для цільового хоста
        X509_VERIFY_PARAM *param = SSL_CTX_get0_param(ctx_.get());
        X509_VERIFY_PARAM_set_hostflags(param, X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS);
        if (X509_VERIFY_PARAM_set1_host(param, hostname.data(), 0) != 1) {
            throw std::runtime_error("Не вдалося встановити цільовий хост для валідації SAN");
        }

        int raw_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (raw_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення сокета");
        }
        ScopedSocket sock(new int(raw_fd));

        struct hostent *he = gethostbyname(hostname.data());
        if (!he) {
            throw std::runtime_error("Не вдалося розв'язати DNS ім'я: " + std::string(hostname));
        }

        sockaddr_in saddr{};
        saddr.sin_family = AF_INET;
        saddr.sin_port = htons(port);
        std::memcpy(&saddr.sin_addr.s_addr, he->h_addr_list[0], he->h_length);

        if (connect(*sock, reinterpret_cast<sockaddr*>(&saddr), sizeof(saddr)) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка встановлення TCP з'єднання");
        }

        ScopedSsl ssl(SSL_new(ctx_.get()));
        SSL_set_fd(ssl.get(), *sock);
        SSL_set_tlsext_host_name(ssl.get(), hostname.data());

        if (SSL_connect(ssl.get()) <= 0) {
            long v_res = SSL_get_verify_result(ssl.get());
            char err_buf[256];
            ERR_error_string_n(ERR_get_error(), err_buf, sizeof(err_buf));
            std::string reason = "TLS Handshake failed: " + std::string(err_buf) +
                                 " | Verify error: " + X509_verify_cert_error_string(v_res);
            throw std::runtime_error(reason);
        }

        std::cout << "[✓] TLS-сесія активна з " << hostname << " [Шифр: " << SSL_get_cipher(ssl.get()) << "]\n";

        std::string req = "GET " + std::string(path) + " HTTP/1.1\r\nHost: " +
                          std::string(hostname) + "\r\nConnection: close\r\n\r\n";
        SSL_write(ssl.get(), req.data(), static_cast<int>(req.size()));

        char buffer[1024];
        int bytes = SSL_read(ssl.get(), buffer, sizeof(buffer) - 1);
        if (bytes > 0) {
            buffer[bytes] = '\0';
            std::cout << "[✓] Відповідь сервера:\n" << buffer << "\n";
        }

        SSL_shutdown(ssl.get());
    }

private:
    ScopedSslCtx ctx_;
};

int main() {
    try {
        TlsSecureClient client("corp-ca.pem", "client.crt", "client.key");
        client.execute_get_request("api.internal.corp", 443, "/v1/status");
    } catch (const std::exception &ex) {
        std::cerr << "[✗] Виняток: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
