// cpp_ktls_raw.cpp - Ідіоматична реалізація kTLS на мові C++20 (RAII, std::expected, std::span)
#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <linux/tls.h>
#include <sys/sendfile.h>

// RAII обгортка для безпечного управління сокетним дескриптором
class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd) noexcept : fd_(fd) {}
    ~SocketHandle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

// Контейнер криптографічних параметрів із фіксованими розмірами поверхонь
struct KtlsKeys {
    std::span<const uint8_t, 16> key;
    std::span<const uint8_t, 8>  iv;
    std::span<const uint8_t, 4>  salt;
    uint64_t seq_num{0};
};

// Налаштування вихідного kTLS з використанням сучасного обробника std::expected
std::expected<void, std::error_code> configure_ktls_tx(int sock_fd, const KtlsKeys& keys) {
    // 1. Активація модуля ULP "tls" у ядрі
    if (::setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls")) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 2. Формування бінарної структури ядра
    struct tls12_crypto_info_aes_gcm_128 crypto_info{};
    crypto_info.info.version = TLS_1_2_VERSION;
    crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

    std::memcpy(crypto_info.key, keys.key.data(), keys.key.size());
    std::memcpy(crypto_info.iv, keys.iv.data(), keys.iv.size());
    std::memcpy(crypto_info.salt, keys.salt.data(), keys.salt.size());
    std::memcpy(crypto_info.rec_seq, &keys.seq_num, sizeof(keys.seq_num));

    // 3. Передача конфігурації у підсистему SOL_TLS
    if (::setsockopt(sock_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}

// Високоефективний потік даних із файлу у сокет через sendfile()
std::expected<size_t, std::error_code> stream_file_ktls(int sock_fd, int file_fd, off_t offset, size_t count) {
    ssize_t bytes_sent = ::sendfile(sock_fd, file_fd, &offset, count);
    if (bytes_sent < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<size_t>(bytes_sent);
}
