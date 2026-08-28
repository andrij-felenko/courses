#include <sys/signalfd.h>
#include <csignal>
#include <pthread.h>
#include <unistd.h>
#include <expected>
#include <system_error>

class SignalFileDescriptor {
public:
    static std::expected<int, std::error_code> create_for_termination() {
        sigset_t mask;
        sigemptyset(&mask);
        sigaddset(&mask, SIGINT);
        sigaddset(&mask, SIGTERM);

        // Блокуємо асинхронну доставку для поточного потоку
        if (::pthread_sigmask(SIG_BLOCK, &mask, nullptr) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int sfd = ::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
        if (sfd == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return sfd;
    }
};
