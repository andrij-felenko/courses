#include <array>
#include <chrono>
#include <cstddef>
#include <fcntl.h>
#include <iostream>
#include <print>
#include <string_view>
#include <system_error>
#include <thread>
#include <unistd.h>

class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) noexcept : fd_{fd} {}
    ~FileDescriptor() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

int main() {
    constexpr std::string_view path = "/tmp/trace_test.dat";
    FileDescriptor file{::open(path.data(), O_WRONLY | O_CREAT | O_TRUNC, 0644)};
    if (!file.valid()) {
        std::println(stderr, "Помилка відкриття: {}", std::make_error_code(std::errc(errno)).message());
        return 1;
    }

    std::array<char, 4096> buffer{};
    buffer.fill('A');

    std::println("PID: {} | Виконуємо write()...", ::getpid());
    const ssize_t written = ::write(file.get(), buffer.data(), buffer.size());
    if (written < 0) {
        std::println(stderr, "Помилка write: {}", std::make_error_code(std::errc(errno)).message());
        return 1;
    }

    std::println("Записано {} байтів у Page Cache. Очікування 2 секунди...", written);
    std::this_thread::sleep_for(std::chrono::seconds(2));

    std::println("Виконуємо fdatasync()...");
    if (::fdatasync(file.get()) < 0) {
        std::println(stderr, "Помилка fdatasync: {}", std::make_error_code(std::errc(errno)).message());
        return 1;
    }

    std::println("Синхронізацію завершено. Закриваємо файл.");
    ::unlink(path.data());
    return 0;
}
