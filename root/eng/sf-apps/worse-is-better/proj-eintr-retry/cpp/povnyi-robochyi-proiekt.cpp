#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <csignal>
#include <unistd.h>
#include <cerrno>
#include <cstring>
#include <array>
#include <expected>
#include <system_error>

namespace {
    std::atomic<int> g_signal_counter{0};

    void signal_handler(int sig) noexcept {
        (void)sig;
        g_signal_counter.fetch_add(1, std::memory_order_relaxed);
    }
}

// RAII-обгортка для файлових дескрипторів
class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    int get() const noexcept { return fd_; }
    void reset() noexcept {
        if (fd_ != -1) {
            ::close(fd_);
            fd_ = -1;
        }
    }

private:
    int fd_{-1};
};

struct Pipe {
    FileDescriptor reader;
    FileDescriptor writer;

    static std::expected<Pipe, std::error_code> create() {
        int fds[2];
        if (::pipe(fds) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return Pipe{FileDescriptor(fds[0]), FileDescriptor(fds[1])};
    }
};

int main() {
    // Встановлюємо обробник сигналу SIGUSR1 без SA_RESTART
    struct sigaction sa{};
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    if (::sigaction(SIGUSR1, &sa, nullptr) == -1) {
        std::cerr << "Помилка встановлення sigaction\n";
        return 1;
    }

    auto pipe_res = Pipe::create();
    if (!pipe_res) {
        std::cerr << "Помилка створення pipe: " << pipe_res.error().message() << "\n";
        return 1;
    }
    auto pipe = std::move(*pipe_res);

    // Фоновий потік надсилає сигнали
    std::thread spammer([]() {
        for (int i = 0; i < 6; ++i) {
            std::this_thread::sleep_for(std::chrono::milliseconds(25));
            ::kill(::getpid(), SIGUSR1);
        }
    });

    const char message[] = "System Programming in C++23\n";
    ::write(pipe.writer.get(), message, sizeof(message));

    std::array<char, 128> buffer{};
    std::size_t total_read = 0;
    std::size_t target_count = sizeof(message);
    int eintr_retries = 0;

    std::cout << "[Головний потік] Очікування читання з каналу під шквалом сигналів...\n";

    while (total_read < target_count) {
        ssize_t res = ::read(pipe.reader.get(), buffer.data() + total_read, target_count - total_read);
        if (res == -1) {
            if (errno == EINTR) {
                eintr_retries++;
                std::cout << "  -> [Перехоплено EINTR #" << eintr_retries << "] Перезапуск операції...\n";
                continue;
            }
            std::cerr << "Помилка читання: " << std::generic_category().message(errno) << "\n";
            break;
        }
        if (res == 0) {
            std::cout << "[Головний потік] Отримано EOF\n";
            break;
        }
        total_read += static_cast<std::size_t>(res);
    }

    std::cout << "[Головний потік] Прочитано " << total_read << " байтів: " << buffer.data();
    std::cout << "[Підсумок] Зафіксовано сигналів: " << g_signal_counter.load() 
              << ", виконано перезапусків: " << eintr_retries << "\n";

    spammer.join();
    return 0;
}
