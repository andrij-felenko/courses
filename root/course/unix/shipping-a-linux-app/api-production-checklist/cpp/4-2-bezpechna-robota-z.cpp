#include <sys/types.h>
#include <sys/socket.h>
#include <csignal>
#include <unistd.h>
#include <cstddef>
#include <expected>
#include <system_error>
#include <iostream>
#include <span>

// Безпечна передача даних через сокет засобами C++23
[[nodiscard]] std::expected<size_t, std::error_code> safe_socket_send(int fd, std::span<const char> data) noexcept {
    const ssize_t res = ::send(fd, data.data(), data.size(), MSG_NOSIGNAL);
    if (res < 0) {
        const int err = errno;
        if (err == EPIPE || err == ECONNRESET) {
            std::cerr << "<4>Клієнт достроково закрив TCP-з'єднання\n";
        }
        return std::unexpected(std::error_code(err, std::generic_category()));
    }
    return static_cast<size_t>(res);
}

// Встановлення ігнорування SIGPIPE на рівні процесу
void init_signal_protection() noexcept {
    struct sigaction sa{};
    sa.sa_handler = SIG_IGN;
    ::sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    ::sigaction(SIGPIPE, &sa, nullptr);
}
