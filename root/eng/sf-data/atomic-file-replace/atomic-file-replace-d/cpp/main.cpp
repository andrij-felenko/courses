#include <iostream>
#include <string>
#include <vector>
#include <span>
#include <filesystem>
#include <system_error>
#include <expected>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <libgen.h>

namespace fs = std::filesystem;

class FileDescriptorGuard {
public:
    explicit FileDescriptorGuard(int fd = -1) noexcept : fd_(fd) {}
    ~FileDescriptorGuard() noexcept { reset(); }

    FileDescriptorGuard(const FileDescriptorGuard&) = delete;
    FileDescriptorGuard& operator=(const FileDescriptorGuard&) = delete;

    FileDescriptorGuard(FileDescriptorGuard&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FileDescriptorGuard& operator=(FileDescriptorGuard&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = new_fd;
        }
    }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

private:
    int fd_;
};

class AtomicFileWriter {
public:
    static std::expected<void, std::error_code> save(
        const fs::path& target_path,
        std::span<const std::byte> payload) noexcept 
    {
        std::error_code ec;

        // 1. Зчитуємо права вихідного файлу
        mode_t target_mode = 0644;
        struct stat st{};
        if (::stat(target_path.c_str(), &st) == 0) {
            target_mode = st.st_mode & 0777;
        }

        // 2. Створюємо шаблон у тому самому каталозі
        std::string temp_pattern = (target_path.string() + ".tmp_XXXXXX");
        std::vector<char> tmpl_buf(temp_pattern.begin(), temp_pattern.end());
        tmpl_buf.push_back('\0');

        int raw_fd = ::mkstemp(tmpl_buf.data());
        if (raw_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        FileDescriptorGuard file_guard(raw_fd);
        fs::path temp_file_path(tmpl_buf.data());

        // Забезпечуємо очищення тимчасового файлу при виході з помилкою
        auto cleanup_guard = [&temp_file_path, &ec]() {
            fs::remove(temp_file_path, ec);
        };

        if (::fchmod(file_guard.get(), target_mode) != 0) {
            int err = errno;
            file_guard.reset();
            cleanup_guard();
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        // 3. Запис у циклі
        const auto* src = reinterpret_cast<const uint8_t*>(payload.data());
        size_t bytes_left = payload.size();
        while (bytes_left > 0) {
            ssize_t n = ::write(file_guard.get(), src, bytes_left);
            if (n < 0) {
                if (errno == EINTR) continue;
                int err = errno;
                file_guard.reset();
                cleanup_guard();
                return std::unexpected(std::error_code(err, std::generic_category()));
            }
            src += n;
            bytes_left -= static_cast<size_t>(n);
        }

        // 4. Синхронізація вмісту та інода
        if (::fsync(file_guard.get()) != 0) {
            int err = errno;
            file_guard.reset();
            cleanup_guard();
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        // Закриваємо дескриптор перед заміною
        file_guard.reset();

        // 5. Атомарне перейменування
        if (::rename(temp_file_path.c_str(), target_path.c_str()) != 0) {
            int err = errno;
            cleanup_guard();
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        // 6. Синхронізація батьківського каталогу
        fs::path parent_dir = target_path.parent_path();
        if (parent_dir.empty()) parent_dir = ".";

        FileDescriptorGuard dir_guard(::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY));
        if (dir_guard.isValid()) {
            ::fsync(dir_guard.get());
        }

        return {};
    }
};
