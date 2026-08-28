#include <fcntl.h>
#include <unistd.h>
#include <sys/file.h>
#include <filesystem>
#include <string>
#include <system_error>
#include <memory>

#if defined(__APPLE__)
#include <sys/fcntl.h>
#endif

namespace fs = std::filesystem;

class PosixFileDescriptor {
public:
    explicit PosixFileDescriptor(int fd = -1) : fd_(fd) {}
    ~PosixFileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    PosixFileDescriptor(const PosixFileDescriptor&) = delete;
    PosixFileDescriptor& operator=(const PosixFileDescriptor&) = delete;

    PosixFileDescriptor(PosixFileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    PosixFileDescriptor& operator=(PosixFileDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

    void sync() {
        if (fd_ < 0) return;
#if defined(__APPLE__)
        if (::fcntl(fd_, F_FULLFSYNC) != 0) {
            throw std::system_error(errno, std::generic_category(), "F_FULLFSYNC failed");
        }
#else
        if (::fsync(fd_) != 0) {
            throw std::system_error(errno, std::generic_category(), "fsync failed");
        }
#endif
    }

    bool try_lock_exclusive() {
        return fd_ >= 0 && ::flock(fd_, LOCK_EX | LOCK_NB) == 0;
    }

private:
    int fd_{-1};
};

class PosixAtomicStorage {
public:
    static PosixFileDescriptor open_temp(const fs::path& temp_path) {
        int fd = ::open(temp_path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0644);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "open O_EXCL failed");
        }
        return PosixFileDescriptor(fd);
    }

    static void commit_replace(const fs::path& temp_path, const fs::path& target_path) {
        if (::rename(temp_path.c_str(), target_path.c_str()) != 0) {
            throw std::system_error(errno, std::generic_category(), "rename failed");
        }

        // Фіксація запису в таблиці батьківського каталогу
        fs::path parent_dir = target_path.parent_path();
        if (parent_dir.empty()) parent_dir = ".";
        
        int dir_fd = ::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
        if (dir_fd >= 0) {
            PosixFileDescriptor dir_guard(dir_fd);
            dir_guard.sync();
        }
    }
};
