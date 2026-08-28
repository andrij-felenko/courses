#include <system_error>
#include <chrono>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

struct KeepAliveOptions {
    std::chrono::seconds idleTime{30};
    std::chrono::seconds probeInterval{5};
    int probeCount{3};
    std::chrono::milliseconds userTimeout{18000};
};

class SocketOptionTuner {
public:
    static std::error_code applyKeepAlive(int fd, const KeepAliveOptions& opts) noexcept {
        int enable = 1;
        if (::setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable)) < 0) {
            return std::error_code(errno, std::generic_category());
        }

        int idle = static_cast<int>(opts.idleTime.count());
#ifdef __linux__
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle, sizeof(idle)) < 0) {
            return std::error_code(errno, std::generic_category());
        }
#elif defined(__APPLE__) || defined(__FreeBSD__) || defined(__NetBSD__) || defined(__OpenBSD__)
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPALIVE, &idle, sizeof(idle)) < 0) {
            return std::error_code(errno, std::generic_category());
        }
#endif

        int intvl = static_cast<int>(opts.probeInterval.count());
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl, sizeof(intvl)) < 0) {
            return std::error_code(errno, std::generic_category());
        }

        int cnt = opts.probeCount;
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &cnt, sizeof(cnt)) < 0) {
            return std::error_code(errno, std::generic_category());
        }

#ifdef TCP_USER_TIMEOUT
        auto utMs = static_cast<unsigned int>(opts.userTimeout.count());
        if (utMs > 0) {
            if (::setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &utMs, sizeof(utMs)) < 0) {
                return std::error_code(errno, std::generic_category());
            }
        }
#endif

        return {};
    }
};
