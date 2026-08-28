#include <unistd.h>
#include <fcntl.h>
#include <csignal>
#include <cerrno>
#include <expected>
#include <system_error>

class SelfPipe {
public:
    static std::expected<int, std::error_code> initialize() {
        int fds[2];
        if (::pipe(fds) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ::fcntl(fds[0], F_SETFL, O_NONBLOCK);
        ::fcntl(fds[1], F_SETFL, O_NONBLOCK);
        ::fcntl(fds[0], F_SETFD, FD_CLOEXEC);
        ::fcntl(fds[1], F_SETFD, FD_CLOEXEC);

        tx_fd_ = fds[1];

        struct sigaction sa{};
        sa.sa_handler = &SelfPipe::signal_handler;
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = SA_RESTART;
        ::sigaction(SIGINT, &sa, nullptr);
        ::sigaction(SIGTERM, &sa, nullptr);

        return fds[0]; // Повертаємо дескриптор для моніторингу в epoll/kqueue
    }

private:
    static inline int tx_fd_{-1};

    static void signal_handler(int signo) noexcept {
        int saved_errno = errno;
        char byte = static_cast<char>(signo);
        [[maybe_unused]] auto res = ::write(tx_fd_, &byte, 1);
        errno = saved_errno;
    }
};
