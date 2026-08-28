#include <iostream>
#include <vector>
#include <span>
#include <string_view>
#include <system_error>
#include <expected>
#include <cstddef>
#include <unistd.h>
#include <grp.h>
#include <sched.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>

namespace sandbox {

constexpr uid_t kUnprivilegedUid = 65534; // nobody
constexpr gid_t kUnprivilegedGid = 65534; // nogroup

class [[nodiscard]] ScopedDescriptor {
public:
    explicit ScopedDescriptor(int fd = -1) noexcept : fd_{fd} {}
    ~ScopedDescriptor() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;
    ScopedDescriptor(ScopedDescriptor&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
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

private:
    int fd_;
};

class SeccompFilterBuilder {
public:
    SeccompFilterBuilder() {
        // Завантаження архітектури та перевірка x86_64
        instructions_.push_back(BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))));
        instructions_.push_back(BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0));
        instructions_.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS));

        // Завантаження номера системного виклику
        instructions_.push_back(BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))));
    }

    void allow_syscall(int syscall_number) {
        allowed_syscalls_.push_back(syscall_number);
    }

    std::expected<void, std::error_code> apply() {
        for (size_t i = 0; i < allowed_syscalls_.size(); ++i) {
            auto remaining = static_cast<uint8_t>(allowed_syscalls_.size() - 1 - i);
            instructions_.push_back(BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, 
                                             static_cast<uint32_t>(allowed_syscalls_[i]), 
                                             remaining, 0));
        }

        // Дія за замовчуванням при збігу — дозволити
        instructions_.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW));
        // Усі інші системні виклики призводять до негайного знищення процесу
        instructions_.push_back(BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS));

        struct sock_fprog prog {
            .len = static_cast<unsigned short>(instructions_.size()),
            .filter = instructions_.data(),
        };

        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return {};
    }

private:
    std::vector<struct sock_filter> instructions_;
    std::vector<int> allowed_syscalls_;
};

void run_sandboxed_worker(int input_fd, int output_fd) {
    // 1. Закриття всіх сторонніх файлових дескрипторів
    for (int fd = 3; fd < 1024; ++fd) {
        if (fd != input_fd && fd != output_fd) {
            ::close(fd);
        }
    }

    // 2. Очищення списку додаткових груп
    if (::setgroups(0, nullptr) != 0 && errno != EPERM) {
        std::_Exit(1);
    }

    // 3. Скидання привілеїв GID та UID (real, effective, saved)
    if (::setresgid(kUnprivilegedGid, kUnprivilegedGid, kUnprivilegedGid) != 0) {
        std::_Exit(1);
    }
    if (::setresuid(kUnprivilegedUid, kUnprivilegedUid, kUnprivilegedUid) != 0) {
        std::_Exit(1);
    }

    // 4. Ізоляція просторів імен (Network + Mount)
    [[maybe_unused]] auto ns_res = ::unshare(CLONE_NEWNS | CLONE_NEWNET);

    // 5. Накладання суворого BPF-фільтра
    SeccompFilterBuilder sandbox;
    sandbox.allow_syscall(SYS_read);
    sandbox.allow_syscall(SYS_write);
    sandbox.allow_syscall(SYS_exit_group);
    sandbox.allow_syscall(SYS_futex);
    sandbox.allow_syscall(SYS_sigreturn);

    if (auto res = sandbox.apply(); !res.has_value()) {
        std::_Exit(1);
    }

    // 6. Безпечне виконання розбору даних
    char buffer[256];
    const auto bytes_read = ::read(input_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        constexpr std::string_view response = "OK: Пакет валідовано в C++ пісочнику\n";
        [[maybe_unused]] auto written = ::write(output_fd, response.data(), response.size());
    }

    std::_Exit(0);
}

} // namespace sandbox
