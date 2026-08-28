#include <iostream>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

namespace netbox {

class SocketConfigurator {
public:
    enum class ErrorCode {
        KeepaliveFailed,
        IdleTimeoutFailed,
        IntervalFailed,
        CountFailed,
        NodelayFailed
    };

    static std::expected<void, ErrorCode> configure_resilient_socket(int fd) noexcept {
        // 1. Активація TCP Keepalive для утримання сесій у таблицях NAT
        int keepalive = 1;
        if (::setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive)) < 0) {
            return std::unexpected(ErrorCode::KeepaliveFailed);
        }

        // Час бездіяльності до першого зонду (25 с для запобігання скидання CGNAT)
        int keepidle = 25;
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &keepidle, sizeof(keepidle)) < 0) {
            return std::unexpected(ErrorCode::IdleTimeoutFailed);
        }

        // Інтервал між повторними зондами
        int keepintvl = 5;
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &keepintvl, sizeof(keepintvl)) < 0) {
            return std::unexpected(ErrorCode::IntervalFailed);
        }

        // Кількість невдалих зондів до розриву сокета
        int keepcnt = 3;
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &keepcnt, sizeof(keepcnt)) < 0) {
            return std::unexpected(ErrorCode::CountFailed);
        }

        // 2. Увімкнення TCP Fast Open на клієнті (RFC 7413, опціонально)
        int fastopen = 1;
        ::setsockopt(fd, IPPROTO_TCP, TCP_FASTOPEN_CONNECT, &fastopen, sizeof(fastopen));

        // 3. Вимкнення алгоритму Нейгла для мінімізації затримок на проміжних проксі
        int nodelay = 1;
        if (::setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay)) < 0) {
            return std::unexpected(ErrorCode::NodelayFailed);
        }

        return {};
    }
};

} // namespace netbox
