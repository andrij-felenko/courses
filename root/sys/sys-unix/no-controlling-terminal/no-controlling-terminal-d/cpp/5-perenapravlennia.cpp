// Приклад традиційної демонізації на C++20 з RAII та expected
#include <cerrno>
#include <csignal>
#include <expected>
#include <fcntl.h>
#include <sys/stat.h>
#include <system_error>
#include <unistd.h>

namespace sys {

[[nodiscard]] std::expected<void, std::error_code> daemonize_traditional() noexcept {
    // 1. Перший fork
    pid_t pid = ::fork();
    if (pid < 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    if (pid > 0) {
        ::_exit(0);
    }

    // 2. Створення нового сеансу
    if (::setsid() < 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }

    ::signal(SIGHUP, SIG_IGN);

    // 3. Другий fork
    pid = ::fork();
    if (pid < 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    if (pid > 0) {
        ::_exit(0);
    }

    // 4. Скидання umask та зміна каталогу
    ::umask(0);
    if (::chdir("/") < 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }

    // 5. Перенаправлення 0, 1, 2 на /dev/null
    int null_fd = ::open("/dev/null", O_RDWR);
    if (null_fd < 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }

    ::dup2(null_fd, STDIN_FILENO);
    ::dup2(null_fd, STDOUT_FILENO);
    ::dup2(null_fd, STDERR_FILENO);

    if (null_fd > STDERR_FILENO) {
        ::close(null_fd);
    }

    return {};
}

} // namespace sys
