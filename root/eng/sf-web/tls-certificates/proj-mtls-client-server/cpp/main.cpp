#include <iostream>
#include <memory>
#include <string_view>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/x509v3.h>

// RAII обгортки для C-ресурсів OpenSSL та файлових дескрипторів
struct SslCtxDeleter { void operator()(SSL_CTX *ctx) const noexcept { SSL_CTX_free(ctx); } };
struct SslDeleter    { void operator()(SSL *ssl) const noexcept { SSL_free(ssl); } };
struct SocketCloser  { void operator()(int *fd) const noexcept { if (fd && *fd >= 0) { close(*fd); delete fd; } } };

using UniqueSslCtx = std::unique_ptr<SSL_CTX, SslCtxDeleter>;
using UniqueSsl    = std::unique_ptr<SSL, SslDeleter>;
using UniqueSocket = std::unique_ptr<int, SocketCloser>;

class MtlsClient {
public:
    MtlsClient(std::string_view ca_file, std::string_view cert_file, std::string_view key_file) {
        ctx_.reset(SSL_CTX_new(TLS_client_method()));
        if (!ctx_) {
            throw std::runtime_error("Не вдалося створити SSL_CTX");
        }

        SSL_CTX_set_verify(ctx_.get(), SSL_VERIFY_PEER, nullptr);
        if (SSL_CTX_load_verify_locations(ctx_.get(), ca_file.data(), nullptr) != 1) {
            throw std::runtime_error("Не вдалося завантажити CA бандл");
        }

        if (SSL_CTX_use_certificate_chain_file(ctx_.get(), cert_file.data()) <= 0 ||
            SSL_CTX_use_PrivateKey_file(ctx_.get(), key_file.data(), SSL_FILETYPE_PEM) <= 0 ||
            SSL_CTX_check_private_key(ctx_.get()) != 1) {
            throw std::runtime_error("Помилка завантаження клієнтського сертифіката/ключа");
        }

        X509_VERIFY_PARAM *param = SSL_CTX_get0_param(ctx_.get());
        X509_VERIFY_PARAM_set1_host(param, "localhost", 0);
    }

    void execute_get(std::string_view host, uint16_t port) {
        int raw_sock = socket(AF_INET, SOCK_STREAM, 0);
        if (raw_sock < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення сокета");
        }
        UniqueSocket sock(new int(raw_sock));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        if (connect(*sock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка TCP-з'єднання");
        }

        UniqueSsl ssl(SSL_new(ctx_.get()));
        SSL_set_fd(ssl.get(), *sock);
        SSL_set_tlsext_host_name(ssl.get(), host.data());

        if (SSL_connect(ssl.get()) <= 0) {
            char err_buf[256];
            ERR_error_string_n(ERR_get_error(), err_buf, sizeof(err_buf));
            throw std::runtime_error(std::string("TLS Handshake failed: ") + err_buf);
        }

        std::cout << "[+] Встановлено mTLS сесію (" << SSL_get_version(ssl.get())
                  << ", шифр " << SSL_get_cipher(ssl.get()) << ")\n";

        std::string req = "GET / HTTP/1.1\r\nHost: " + std::string(host) + "\r\nConnection: close\r\n\r\n";
        SSL_write(ssl.get(), req.data(), static_cast<int>(req.size()));

        char resp_buf[1024];
        int bytes = SSL_read(ssl.get(), resp_buf, sizeof(resp_buf) - 1);
        if (bytes > 0) {
            resp_buf[bytes] = '\0';
            std::cout << "[+] Відповідь сервера:\n" << resp_buf << "\n";
        }

        SSL_shutdown(ssl.get());
    }

private:
    UniqueSslCtx ctx_;
};

int main() {
    try {
        MtlsClient client("ca.crt", "client.crt", "client.key");
        client.execute_get("localhost", 8443);
    } catch (const std::exception &ex) {
        std::cerr << "[!] Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
