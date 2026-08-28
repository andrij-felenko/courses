#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <expected>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

class ScopedFileDescriptor {
    int fd_{-1};
public:
    explicit ScopedFileDescriptor(int fd) noexcept : fd_(fd) {}
    ~ScopedFileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    
    ScopedFileDescriptor(const ScopedFileDescriptor&) = delete;
    ScopedFileDescriptor& operator=(const ScopedFileDescriptor&) = delete;
    ScopedFileDescriptor(ScopedFileDescriptor&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    ScopedFileDescriptor& operator=(ScopedFileDescriptor&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
    int release() noexcept { int tmp = fd_; fd_ = -1; return tmp; }
};

[[nodiscard]] std::expected<void, std::error_code> 
atomic_write_file(const fs::path& target_path, std::string_view payload, mode_t default_mode = 0644) {
    std::error_code ec;
    const fs::path parent_dir = target_path.parent_path().empty() ? fs::current_path() : target_path.parent_path();
    
    mode_t target_mode = default_mode;
    uid_t target_uid = static_cast<uid_t>(-1);
    gid_t target_gid = static_cast<gid_t>(-1);
    bool has_original = false;

    struct stat st{};
    if (::stat(target_path.c_str(), &st) == 0) {
        target_mode = st.st_mode & 07777;
        target_uid = st.st_uid;
        target_gid = st.st_gid;
        has_original = true;
    }

    const fs::path temp_path = parent_dir / (".tmp_atomic_" + std::to_string(::getpid()) + "_" + std::to_string(payload.size()));

    ScopedFileDescriptor fd{::open(temp_path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, target_mode)};
    if (!fd.is_valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // Лямбда-охоронець для автоматичного прибирання тимчасового файлу при помилці
    bool success = false;
    auto auto_cleanup = [&temp_path, &success]() {
        if (!success) {
            ::unlink(temp_path.c_str());
        }
    };
    struct CleanupGuard {
        decltype(auto_cleanup)& cleaner;
        ~CleanupGuard() { cleaner(); }
    } guard{auto_cleanup};

    if (has_original && ::geteuid() == 0) {
        if (::fchown(fd.get(), target_uid, target_gid) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
    }

    const char* ptr = payload.data();
    size_t remaining = payload.size();
    while (remaining > 0) {
        ssize_t written = ::write(fd.get(), ptr, remaining);
        if (written < 0) {
            if (errno == EINTR) continue;
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        ptr += written;
        remaining -= static_cast<size_t>(written);
    }

    if (::fsync(fd.get()) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // Закриваємо файл перед викликом rename
    int raw_fd = fd.release();
    if (::close(raw_fd) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::rename(temp_path.c_str(), target_path.c_str()) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    success = true; // Успішно перейменовано, прибирати тимчасовий файл не потрібно

    // Скидаємо блок батьківського каталогу на носій
    ScopedFileDescriptor dir_fd{::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC)};
    if (dir_fd.is_valid()) {
        ::fsync(dir_fd.get());
    }

    return {};
}
