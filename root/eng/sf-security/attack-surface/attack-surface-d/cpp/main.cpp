#include <iostream>
#include <string_view>
#include <system_error>
#include <expected>
#include <cstring>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <linux/seccomp.h>

namespace secure_server {

constexpr uint16_t kSecurePort = 8443;
constexpr uid_t kNobodyUid = 65534;
constexpr gid_t kNobodyGid = 65534;

class [[nodiscard]] ServerSocket {
public:
    static std::expected<ServerSocket, std::error_code> create_loopback(uint16_t port) {
        int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int opt = 1;
        ::setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in address{};
        address.sin_family = AF_INET;
        // Мінімізація поверхні: прив'язка суворо до локальної петлі 127.0.0.1
        address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        address.sin_port = htons(port);

        if (::bind(fd, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0) {
            ::close(fd);
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::listen(fd, 5) < 0) {
            ::close(fd);
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return ServerSocket(fd);
    }

    ~ServerSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ServerSocket(const ServerSocket&) = delete;
    ServerSocket& operator=(const ServerSocket&) = delete;

    ServerSocket(ServerSocket&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    ServerSocket& operator=(ServerSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

private:
    explicit ServerSocket(int fd) noexcept : fd_{fd} {}
    int fd_;
};

[[nodiscard]] std::expected<void, std::error_code> harden_worker() noexcept {
    // 1. Заборона підвищення привілеїв у дочірніх процесах
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 2. Скидання привілеїв до непривілейованого користувача nobody
    if (::setgid(kNobodyGid) != 0 || ::setuid(kNobodyUid) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 3. Активація суворого режиму Seccomp
    if (::prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}

} // namespace secure_server
