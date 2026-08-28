#include <iostream>
#include <string_view>
#include <expected>
#include <format>
#include <system_error>
#include <unistd.h>
#include <sys/syscall.h>
#include <fcntl.h>

#ifndef __NR_fsopen
#define __NR_fsopen 430
#define __NR_fsconfig 431
#define __NR_fsmount 432
#define __NR_move_mount 429
#endif

class ScopedDescriptor {
    int fd_ = -1;
public:
    explicit ScopedDescriptor(int fd) noexcept : fd_(fd) {}
    ~ScopedDescriptor() noexcept { if (fd_ >= 0) ::close(fd_); }
    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;
    ScopedDescriptor(ScopedDescriptor&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    int release() noexcept { int tmp = fd_; fd_ = -1; return tmp; }
};

[[nodiscard]] std::expected<void, std::string>
mountViaModernApi(std::string_view source, std::string_view target, std::string_view fstype) {
    /* 1. fsopen */
    ScopedDescriptor fsContext(static_cast<int>(::syscall(__NR_fsopen, fstype.data(), 0)));
    if (!fsContext.valid()) {
        return std::unexpected(std::format("Збій fsopen('{}'): {}", fstype, std::generic_category().message(errno)));
    }

    /* 2. fsconfig налаштування джерела */
    if (::syscall(__NR_fsconfig, fsContext.get(), 1 /* FSCONFIG_SET_STRING */, "source", source.data(), 0) < 0) {
        return std::unexpected(std::format("Збій конфігурації source: {}", std::generic_category().message(errno)));
    }

    /* 3. fsconfig валідація суперблоку */
    if (::syscall(__NR_fsconfig, fsContext.get(), 6 /* FSCONFIG_CMD_CREATE */, nullptr, nullptr, 0) < 0) {
        return std::unexpected(std::format("Збій створення суперблоку: {}", std::generic_category().message(errno)));
    }

    /* 4. fsmount */
    ScopedDescriptor mntTree(static_cast<int>(::syscall(__NR_fsmount, fsContext.get(), 0, 0)));
    if (!mntTree.valid()) {
        return std::unexpected(std::format("Збій fsmount: {}", std::generic_category().message(errno)));
    }

    /* 5. move_mount */
    if (::syscall(__NR_move_mount, mntTree.get(), "", AT_FDCWD, target.data(), 0x00000004) < 0) {
        return std::unexpected(std::format("Збій move_mount на '{}': {}", target, std::generic_category().message(errno)));
    }

    return {};
}
