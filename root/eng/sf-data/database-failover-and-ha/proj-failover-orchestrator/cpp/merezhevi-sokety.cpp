#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <chrono>
#include <expected>
#include <system_error>

namespace db::ha {

struct SocketTimeoutConfig {
    std::chrono::seconds keepidle{2};
    std::chrono::seconds keepintvl{1};
    int keepcnt{3};
    std::chrono::milliseconds user_timeout{4000};
};

[[nodiscard]] inline std::expected<void, std::error_code> configure_safety_timeouts(
    int sockfd,
    const SocketTimeoutConfig& cfg = {}) noexcept
{
    const int keepalive = 1;
    if (::setsockopt(sockfd, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive)) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    const int idle = static_cast<int>(cfg.keepidle.count());
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPIDLE, &idle, sizeof(idle)) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    const int intvl = static_cast<int>(cfg.keepintvl.count());
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl, sizeof(intvl)) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPCNT, &cfg.keepcnt, sizeof(cfg.keepcnt)) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    const auto user_timeout_ms = static_cast<unsigned int>(cfg.user_timeout.count());
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_USER_TIMEOUT, &user_timeout_ms, sizeof(user_timeout_ms)) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}

} // namespace db::ha
