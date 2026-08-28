// cpp_openssl_ktls.cpp - Використання OpenSSL 3.0 з kTLS та RAII-обгортками на C++20
#include <iostream>
#include <memory>
#include <vector>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

// Кастомні делітери для розумних вказівників OpenSSL
struct SslCtxDeleter {
    void operator()(SSL_CTX* ctx) const noexcept { SSL_CTX_free(ctx); }
};
struct SslDeleter {
    void operator()(SSL* ssl) const noexcept { SSL_free(ssl); }
};

using SslCtxPtr = std::unique_ptr<SSL_CTX, SslCtxDeleter>;
using SslPtr = std::unique_ptr<SSL, SslDeleter>;

class KtlsServerSession {
    SslPtr ssl_;
    int sock_fd_;

public:
    KtlsServerSession(SslPtr ssl, int sock_fd) noexcept
        : ssl_(std::move(ssl)), sock_fd_(sock_fd) {}

    // Перевірка стану апаратного або програмного kTLS ядра
    [[nodiscard]] bool is_ktls_tx_active() const noexcept {
        BIO* wbio = SSL_get_wbio(ssl_.get());
        return wbio && BIO_get_ktls_send(wbio);
    }

    // Автоматичний вибір між Zero-Copy sendfile() та SSL_write()
    std::expected<size_t, std::error_code> transmit_file(int file_fd, size_t file_size) {
        if (is_ktls_tx_active()) {
            std::cout << "[C++ kTLS Engine] Zero-Copy sendfile() напрямок увімкнено.\n";
            off_t offset = 0;
            ssize_t bytes = ::sendfile(sock_fd_, file_fd, &offset, file_size);
            if (bytes < 0) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            return static_cast<size_t>(bytes);
        }

        std::cout << "[C++ Userspace Engine] Фолбек на цикл SSL_write().\n";
        std::vector<char> buffer(65536);
        size_t total_written = 0;
        ssize_t read_bytes = 0;

        while ((read_bytes = ::read(file_fd, buffer.data(), buffer.size())) > 0) {
            int ret = SSL_write(ssl_.get(), buffer.data(), static_cast<int>(read_bytes));
            if (ret <= 0) {
                return std::unexpected(std::make_error_code(std::errc::io_error));
            }
            total_written += static_cast<size_t>(ret);
        }

        if (read_bytes < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return total_written;
    }
};
