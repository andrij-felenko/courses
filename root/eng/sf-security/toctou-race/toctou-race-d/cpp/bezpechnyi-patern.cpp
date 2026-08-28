#include <iostream>
#include <string_view>
#include <expected>
#include <system_error>
#include <memory>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>

class SafeFileDescriptor {
public:
    explicit SafeFileDescriptor(int fd) : fd_(fd) {}
    ~SafeFileDescriptor() { if (fd_ >= 0) ::close(fd_); }

    SafeFileDescriptor(const SafeFileDescriptor&) = delete;
    SafeFileDescriptor& operator=(const SafeFileDescriptor&) = delete;
    SafeFileDescriptor(SafeFileDescriptor&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SafeFileDescriptor& operator=(SafeFileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

private:
    int fd_ = -1;
};

enum class FileError {
    SymlinkDetected,
    NotRegularFile,
    SystemError,
    WriteFailed
};

std::expected<void, FileError> safe_write_report_cpp(int dirfd, std::string_view filename, std::string_view data) {
    // 1. Атомарне відкриття через openat із забороною симлінків
    SafeFileDescriptor file(::openat(dirfd, filename.data(), O_WRONLY | O_NOFOLLOW | O_CLOEXEC));
    if (!file.is_valid()) {
        if (errno == ELOOP) {
            return std::unexpected(FileError::SymlinkDetected);
        }
        return std::unexpected(FileError::SystemError);
    }

    // 2. Отримання метаданих закріпленого інода
    struct stat st{};
    if (::fstat(file.get(), &st) != 0) {
        return std::unexpected(FileError::SystemError);
    }

    // 3. Перевірка типу файлу
    if (!S_ISREG(st.st_mode)) {
        return std::unexpected(FileError::NotRegularFile);
    }

    // 4. Запис у гарантовано безпечний інод
    ssize_t written = ::write(file.get(), data.data(), data.size());
    if (written != static_cast<ssize_t>(data.size())) {
        return std::unexpected(FileError::WriteFailed);
    }

    return {};
}
