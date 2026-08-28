// C++20 implementation: RAII-wrapped TLS 1.3 Client using OpenSSL
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <system_error>
#include <array>
#include <cstring>

#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/socket.h>

#include <openssl/ssl.h>
#include <openssl/err.h>

namespace tls {

struct SslCtxDeleter {
    void operator()(SSL_CTX* ctx) const noexcept { if (ctx) SSL_CTX_free(ctx); }
};
struct SslDeleter {
    void operator()(SSL* ssl) const noexcept { if (ssl) SSL_free(ssl); }
};

using CtxPtr = std::unique_ptr<SSL_CTX, SslCtxDeleter>;
using SslPtr = std::unique_ptr<SSL, SslDeleter>;

class TlsClient {
public:
    explicit TlsClient(std::string_view host, std::string_view port) 
        : host_(host), port_(port) {
        
        ctx_ = CtxPtr(SSL_CTX_new(TLS_client_method()));
        if (!ctx_) {
            throw std::runtime_error("Failed to create SSL_CTX");
        }

        if (!SSL_CTX_set_min_proto_version(ctx_.get(), TLS1_3_VERSION) ||
            !SSL_CTX_set_max_proto_version(ctx_.get(), TLS1_3_VERSION)) {
            throw std::runtime_error("Failed to set TLS 1.3 protocol version");
        }

        SSL_CTX_set_default_verify_paths(ctx_.get());
    }

    void connect() {
        int raw_fd = connect_socket();
        sock_fd_ = raw_fd;

        ssl_ = SslPtr(SSL_new(ctx_.get()));
        if (!ssl_) {
            close(sock_fd_);
            throw std::runtime_error("Failed to create SSL object");
        }

        SSL_set_fd(ssl_.get(), sock_fd_);
        SSL_set_tlsext_host_name(ssl_.get(), host_.c_str());
        SSL_set1_host(ssl_.get(), host_.c_str());
        SSL_set_verify(ssl_.get(), SSL_VERIFY_PEER, nullptr);

        if (SSL_connect(ssl_.get()) <= 0) {
            close(sock_fd_);
            throw std::runtime_error("TLS Handshake failed");
        }
    }

    void send(std::string_view data) {
        if (SSL_write(ssl_.get(), data.data(), static_cast<int>(data.size())) <= 0) {
            throw std::runtime_error("SSL_write failed");
        }
    }

    std::string receive() {
        std::array<char, 1024> buffer;
        int bytes = SSL_read(ssl_.get(), buffer.data(), static_cast<int>(buffer.size() - 1));
        if (bytes <= 0) {
            return "";
        }
        return std::string(buffer.data(), static_cast<size_t>(bytes));
    }

    ~TlsClient() {
        if (ssl_) {
            SSL_shutdown(ssl_.get());
        }
        if (sock_fd_ >= 0) {
            close(sock_fd_);
        }
    }

    [[nodiscard]] std::string cipher_name() const {
        return SSL_get_cipher(ssl_.get());
    }

    [[nodiscard]] std::string version() const {
        return SSL_get_version(ssl_.get());
    }

private:
    int connect_socket() {
        struct addrinfo hints{}, *res = nullptr;
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_STREAM;

        if (getaddrinfo(host_.c_str(), port_.c_str(), &hints, &res) != 0) {
            throw std::runtime_error("getaddrinfo failed");
        }

        int fd = -1;
        for (auto* p = res; p != nullptr; p = p->ai_next) {
            fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
            if (fd < 0) continue;
            if (::connect(fd, p->ai_addr, p->ai_addrlen) == 0) break;
            close(fd);
            fd = -1;
        }

        freeaddrinfo(res);
        if (fd < 0) {
            throw std::runtime_error("Could not connect to host socket");
        }
        return fd;
    }

    std::string host_;
    std::string port_;
    CtxPtr ctx_{nullptr};
    SslPtr ssl_{nullptr};
    int sock_fd_{-1};
};

} // namespace tls

int main() {
    try {
        tls::TlsClient client("example.com", "443");
        std::cout << "Connecting via TLS 1.3...\n";
        client.connect();

        std::cout << "Connected! Version: " << client.version() 
                  << ", Cipher: " << client.cipher_name() << "\n";

        client.send("GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n");
        std::string response = client.receive();
        std::cout << "Response excerpt:\n" << response.substr(0, 150) << "...\n";

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
