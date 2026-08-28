#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <format>
#include <memory>
#include <system_error>
#include <array>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <signal.h>

namespace {
constexpr std::string_view FIFO_PATH = "/tmp/app_events.fifo";
constexpr size_t MAX_MSG_SIZE = 512;

class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) ::close(fd_);
        fd_ = new_fd;
    }

private:
    int fd_;
};

void run_server() {
    ::unlink(FIFO_PATH.data());
    if (::mkfifo(FIFO_PATH.data(), 0666) < 0 && errno != EEXIST) {
        throw std::system_error(errno, std::generic_category(), "mkfifo failed");
    }

    std::cout << "[Сервер C++] FIFO створено: " << FIFO_PATH << '\n';

    // Відкриваємо O_RDWR, щоб read() не завершувався з 0 (EOF) при від'єднанні клієнтів
    UniqueFd server_fd(::open(FIFO_PATH.data(), O_RDWR));
    if (!server_fd.valid()) {
        throw std::system_error(errno, std::generic_category(), "open FIFO failed");
    }

    std::cout << "[Сервер C++] Очікування подій...\n";

    std::array<char, MAX_MSG_SIZE> buffer{};
    while (true) {
        ssize_t bytes_read = ::read(server_fd.get(), buffer.data(), buffer.size() - 1);
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0';
            std::cout << "[Подія] " << buffer.data();
            std::cout.flush();
        } else if (bytes_read < 0) {
            if (errno == EINTR) continue;
            std::cerr << "Помилка читання з FIFO: " << std::strerror(errno) << '\n';
            break;
        }
    }

    ::unlink(FIFO_PATH.data());
}

void send_event(std::string_view service_name, std::string_view message) {
    // Відкриваємо неблокуюче на запис
    UniqueFd client_fd(::open(FIFO_PATH.data(), O_WRONLY | O_NONBLOCK));
    if (!client_fd.valid()) {
        if (errno == ENXIO) {
            std::cerr << "[Клієнт] Помилка: Сервер логів не активний (немає читача).\n";
            return;
        }
        throw std::system_error(errno, std::generic_category(), "open client FIFO");
    }

    // Ігноруємо SIGPIPE локально
    struct sigaction sa{};
    sa.sa_handler = SIG_IGN;
    ::sigaction(SIGPIPE, &sa, nullptr);

    auto now = std::chrono::system_clock::now();
    std::string record = std::format("[{:%Y-%m-%d %H:%M:%S}] [{}] (PID:{}): {}\n",
                                     now, service_name, ::getpid(), message);

    if (record.size() > MAX_MSG_SIZE) {
        record.resize(MAX_MSG_SIZE - 1);
        record += '\n';
    }

    ssize_t written = ::write(client_fd.get(), record.data(), record.size());
    if (written < 0) {
        if (errno == EPIPE) {
            std::cerr << "[Клієнт] Канал зламано (EPIPE).\n";
        } else {
            std::cerr << "Помилка запису в FIFO: " << std::strerror(errno) << '\n';
        }
    }
}
} // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc > 1 && std::string_view(argv[1]) == "server") {
            run_server();
        } else if (argc > 3 && std::string_view(argv[1]) == "client") {
            send_event(argv[2], argv[3]);
        } else {
            std::cout << "Використання:\n"
                      << "  " << argv[0] << " server                  — запустити сервер\n"
                      << "  " << argv[0] << " client <сервіс> <текст> — надіслати подію\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
