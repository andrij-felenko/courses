// headless_probe.cpp
// g++ -std=c++20 -Wall -Wextra -o headless_probe headless_probe.cpp

#include <array>
#include <cerrno>
#include <cstring>
#include <expected>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <system_error>
#include <termios.h>
#include <unistd.h>

namespace sys {

// RAII обгортка для володіння файловим дескриптором
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_{-1} {}
    explicit UniqueFd(int fd) noexcept : fd_{fd} {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    explicit operator bool() const noexcept { return valid(); }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

struct TerminalStatus {
    bool stdin_is_tty{false};
    bool stdout_is_tty{false};
    bool stderr_is_tty{false};
    int kernel_tty_nr{0};
    bool dev_tty_accessible{false};
    int dev_tty_error{0};
};

// Читання tty_nr з /proc/self/stat
[[nodiscard]] std::expected<int, std::error_code> get_kernel_tty_nr() {
    std::ifstream stat_file("/proc/self/stat");
    if (!stat_file.is_open()) {
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    std::string line;
    if (!std::getline(stat_file, line)) {
        return std::unexpected(std::make_error_code(std::errc::io_error));
    }

    const auto rparen = line.rfind(')');
    if (rparen == std::string::npos || rparen + 2 >= line.size()) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    std::string_view rest{line.data() + rparen + 2, line.size() - (rparen + 2)};
    char state{};
    int ppid{}, pgrp{}, session{}, tty_nr{};
    if (sscanf(rest.data(), "%c %d %d %d %d", &state, &ppid, &pgrp, &session, &tty_nr) != 5) {
        return std::unexpected(std::make_error_code(std::errc::protocol_error));
    }

    return tty_nr;
}

// Повний аудит контексту виконання
[[nodiscard]] TerminalStatus inspect_environment() {
    TerminalStatus status;
    status.stdin_is_tty = (::isatty(STDIN_FILENO) == 1);
    status.stdout_is_tty = (::isatty(STDOUT_FILENO) == 1);
    status.stderr_is_tty = (::isatty(STDERR_FILENO) == 1);

    auto tty_res = get_kernel_tty_nr();
    status.kernel_tty_nr = tty_res.value_or(-1);

    UniqueFd tty_fd{::open("/dev/tty", O_RDWR | O_NOCTTY | O_CLOEXEC)};
    if (tty_fd) {
        status.dev_tty_accessible = true;
        status.dev_tty_error = 0;
    } else {
        status.dev_tty_accessible = false;
        status.dev_tty_error = errno;
    }

    return status;
}

// Безпечне отримання пароля
[[nodiscard]] std::expected<std::string, std::error_code>
read_secret_safe(std::string_view prompt) {
    UniqueFd tty_fd{::open("/dev/tty", O_RDWR | O_NOCTTY | O_CLOEXEC)};

    if (tty_fd) {
        // Інтерактивний термінал доступний
        struct termios orig_termios{}, raw_termios{};
        ::tcgetattr(tty_fd.get(), &orig_termios);
        raw_termios = orig_termios;
        raw_termios.c_lflag &= ~static_cast<tcflag_t>(ECHO);

        ::tcsetattr(tty_fd.get(), TCSAFLUSH, &raw_termios);
        ::dprintf(tty_fd.get(), "%.*s", static_cast<int>(prompt.size()), prompt.data());

        std::array<char, 256> buf{};
        FILE* fp = ::fdopen(tty_fd.get(), "r");
        char* res = fp ? ::fgets(buf.data(), static_cast<int>(buf.size()), fp) : nullptr;

        ::tcsetattr(tty_fd.get(), TCSAFLUSH, &orig_termios);
        ::dprintf(tty_fd.get(), "\n");

        if (!res) {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }

        std::string secret{buf.data()};
        if (!secret.empty() && secret.back() == '\n') {
            secret.pop_back();
        }
        return secret;
    }

    if (errno == ENXIO || errno == ENOENT || errno == ENODEV) {
        // Headless режим: безпечний fallback на стандартний ввід
        std::cerr << "[headless] /dev/tty недоступний (" << std::strerror(errno)
                  << "). Читаємо секрет зі stdin...\n";
        std::string secret;
        if (!std::getline(std::cin, secret)) {
            return std::unexpected(std::make_error_code(std::errc::io_error));
        }
        return secret;
    }

    return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
}

} // namespace sys

int main() {
    // Вмикаємо лінійну буферизацію для уникнення застрягання логів у пайпах
    ::setvbuf(stdout, nullptr, _IOLBF, 0);

    const auto status = sys::inspect_environment();

    std::cout << "=== ДІАГНОСТИКА ТЕРМІНАЛЬНОГО КОНТЕКСТУ (C++20) ===\n";
    std::cout << "STDIN  isatty: " << (status.stdin_is_tty ? "ТАК" : "НІ") << "\n";
    std::cout << "STDOUT isatty: " << (status.stdout_is_tty ? "ТАК" : "НІ") << "\n";
    std::cout << "STDERR isatty: " << (status.stderr_is_tty ? "ТАК" : "НІ") << "\n";
    std::cout << "Kernel tty_nr: " << status.kernel_tty_nr
              << (status.kernel_tty_nr == 0 ? " (керуючий термінал ВІДСУТНІЙ)" : "") << "\n";

    if (status.dev_tty_accessible) {
        std::cout << "open(\"/dev/tty\"): УСПІХ\n";
    } else {
        std::cout << "open(\"/dev/tty\"): ПОМИЛКА " << status.dev_tty_error << " ("
                  << std::strerror(status.dev_tty_error) << ")\n";
        if (status.dev_tty_error == ENXIO) {
            std::cout << "  -> ENXIO: гарантовано неінтерактивне середовище.\n";
        }
    }

    std::cout << "\n--- ТЕСТ ВВЕДЕННЯ ПАРОЛЯ ---\n";
    auto secret = sys::read_secret_safe("Введіть токен доступу: ");
    if (secret) {
        std::cout << "Секрет успішно зчитано! Довжина: " << secret->size() << " байтів.\n";
    } else {
        std::cerr << "Помилка читання секрету: " << secret.error().message() << "\n";
        return 1;
    }

    return 0;
}
