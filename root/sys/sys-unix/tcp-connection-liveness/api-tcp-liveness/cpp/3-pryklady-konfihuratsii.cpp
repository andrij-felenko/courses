#include <iostream>
#include <system_error>
#include <chrono>
#include <cerrno>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

class SocketLivenessConfigurator {
public:
    struct Options {
        std::chrono::seconds idle_time{60};
        std::chrono::seconds probe_interval{10};
        int probe_count{5};
        std::chrono::milliseconds user_timeout{15000};
    };

    static void apply(int fd, const Options& opts) {
        const int enable = 1;
        if (::setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to set SO_KEEPALIVE");
        }

        const int idle_sec = static_cast<int>(opts.idle_time.count());
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle_sec, sizeof(idle_sec)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPIDLE");
        }

        const int intvl_sec = static_cast<int>(opts.probe_interval.count());
        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &intvl_sec, sizeof(intvl_sec)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPINTVL");
        }

        if (::setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &opts.probe_count, sizeof(opts.probe_count)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to set TCP_KEEPCNT");
        }

        if (opts.user_timeout.count() > 0) {
            const auto timeout_ms = static_cast<unsigned int>(opts.user_timeout.count());
            if (::setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &timeout_ms, sizeof(timeout_ms)) < 0) {
                throw std::system_error(errno, std::generic_category(), "Failed to set TCP_USER_TIMEOUT");
            }
        }
    }
};
