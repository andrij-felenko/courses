#include <iostream>
#include <string_view>
#include <system_error>
#include <array>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <netinet/tcp.h>
#include <linux/tls.h>

namespace ktls {

// RAII обгортка для безпечного керування дескрипторами файлів та сокетів
class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
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
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// Ідіоматична C++ обгортка конфігурації та відправки kTLS
class TlsSocketSession {
public:
    using KeyArray = std::array<uint8_t, TLS_CIPHER_AES_GCM_128_KEY_SIZE>;
    using IvArray = std::array<uint8_t, TLS_CIPHER_AES_GCM_128_IV_SIZE>;
    using SaltArray = std::array<uint8_t, TLS_CIPHER_AES_GCM_128_SALT_SIZE>;

    // Ініціалізація kTLS TX на сокеті
    static std::error_code enable_ktls_tx(int client_fd, 
                                          const KeyArray& key, 
                                          const IvArray& iv, 
                                          const SaltArray& salt) noexcept
    {
        // 1. Активація модуля ULP "tls"
        constexpr std::string_view ulp_name = "tls";
        if (::setsockopt(client_fd, IPPROTO_TCP, TCP_ULP, ulp_name.data(), ulp_name.size()) < 0) {
            return std::error_code(errno, std::generic_category());
        }

        // 2. Заповнення двійкової структури для ядра
        struct tls12_crypto_info_aes_gcm_128 crypto_info{};
        crypto_info.info.version = TLS_1_2_VERSION;
        crypto_info.info.cipher_type = TLS_CIPHER_AES_GCM_128;

        std::memcpy(crypto_info.key, key.data(), key.size());
        std::memcpy(crypto_info.iv, iv.data(), iv.size());
        std::memcpy(crypto_info.salt, salt.data(), salt.size());

        // 3. Передача ключів сесії у ядро
        if (::setsockopt(client_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info)) < 0) {
            return std::error_code(errno, std::generic_category());
        }

        return {};
    }

    // Безкопійна відправка файлу через sendfile з повним контролем помилок
    static std::pair<size_t, std::error_code> send_zero_copy_file(int client_fd, std::string_view filepath) noexcept {
        SocketHandle file_fd(::open(filepath.data(), O_RDONLY));
        if (!file_fd.valid()) {
            return {0, std::error_code(errno, std::generic_category())};
        }

        struct stat st{};
        if (::fstat(file_fd.get(), &st) < 0) {
            return {0, std::error_code(errno, std::generic_category())};
        }

        off_t offset = 0;
        size_t total_to_send = st.st_size;
        size_t total_sent = 0;

        while (total_sent < total_to_send) {
            ssize_t sent = ::sendfile(client_fd, file_fd.get(), &offset, total_to_send - total_sent);
            if (sent < 0) {
                if (errno == EINTR) {
                    continue;
                }
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    break; // Сокет переповнено у неблокуючому режимі
                }
                return {total_sent, std::error_code(errno, std::generic_category())};
            }
            if (sent == 0) {
                break;
            }
            total_sent += static_cast<size_t>(sent);
        }

        return {total_sent, std::error_code{}};
    }
};

} // namespace ktls
