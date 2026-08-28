#include <iostream>
#include <string_view>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/fs.h>

class FsFreezeGuard {
public:
    static std::expected<FsFreezeGuard, std::error_code> acquire(std::string_view mount_path) {
        int fd = ::open(mount_path.data(), O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::ioctl(fd, FIFREEZE, 0) < 0) {
            int err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        return FsFreezeGuard(fd);
    }

    ~FsFreezeGuard() noexcept {
        if (fd_ >= 0) {
            ::ioctl(fd_, FITHAW, 0);
            ::close(fd_);
        }
    }

    FsFreezeGuard(const FsFreezeGuard&) = delete;
    FsFreezeGuard& operator=(const FsFreezeGuard&) = delete;

    FsFreezeGuard(FsFreezeGuard&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    FsFreezeGuard& operator=(FsFreezeGuard&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::ioctl(fd_, FITHAW, 0);
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept {
        return fd_;
    }

private:
    explicit FsFreezeGuard(int fd) noexcept : fd_(fd) {}
    int fd_{-1};
};
