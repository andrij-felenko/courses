#include <iostream>
#include <string_view>
#include <filesystem>
#include <expected>
#include <span>
#include <vector>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <cstddef>

namespace security {

class [[nodiscard]] SecureFileDescriptor {
public:
    explicit SecureFileDescriptor(int fd) noexcept : fd_(fd) {}
    ~SecureFileDescriptor() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SecureFileDescriptor(const SecureFileDescriptor&) = delete;
    SecureFileDescriptor& operator=(const SecureFileDescriptor&) = delete;

    SecureFileDescriptor(SecureFileDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    SecureFileDescriptor& operator=(SecureFileDescriptor&& other) noexcept {
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
    int fd_{-1};
};

[[nodiscard]] std::expected<SecureFileDescriptor, int> create_secure_config_file(std::string_view filepath) noexcept {
    // Встановлення безпечної маски для ізоляції файлу
    const mode_t old_mask = ::umask(0077);

    const int fd = ::open(filepath.data(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    ::umask(old_mask);

    if (fd < 0) {
        return std::unexpected(errno);
    }
    return SecureFileDescriptor(fd);
}

[[nodiscard]] std::expected<void, int> apply_strict_seccomp_sandbox() noexcept {
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        return std::unexpected(errno);
    }

    const std::vector<sock_filter> filter = {
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        // Явний білий список системних викликів
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        // Дефолтна дія: знищення процесу при спробі несанкціонованого виклику
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
    };

    const sock_fprog prog = {
        .len = static_cast<unsigned short>(filter.size()),
        .filter = const_cast<sock_filter*>(filter.data()),
    };

    if (::prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) {
        return std::unexpected(errno);
    }

    return {};
}

} // namespace security
