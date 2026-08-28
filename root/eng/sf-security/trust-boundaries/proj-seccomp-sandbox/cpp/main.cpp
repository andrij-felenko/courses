#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <unistd.h>

#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <cstring>
#include <memory>

namespace sandbox {

inline constexpr size_t kMaxPayload = 512;

struct ParsedHeaderDTO {
    uint32_t magic{0};
    uint32_t width{0};
    uint32_t height{0};
    uint32_t checksum{0};
};

class [[nodiscard]] ScopedDescriptor {
public:
    explicit ScopedDescriptor(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedDescriptor() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;

    ScopedDescriptor(ScopedDescriptor&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

private:
    int fd_{-1};
};

class SeccompFilterBuilder {
public:
    static std::expected<void, std::error_code> apply_strict_sandbox() noexcept {
        struct sock_filter filter[] = {
            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
#if defined(__x86_64__)
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
#elif defined(__aarch64__)
            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_AARCH64, 1, 0),
#else
#error "Непідтримувана архітектура процесора"
#endif
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

            BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_read, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_write, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_exit_group, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_rt_sigreturn, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_brk, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_mmap, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_munmap, 0, 1),
            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

            BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
        };

        struct sock_fprog prog = {
            .len = static_cast<unsigned short>(sizeof(filter) / sizeof(filter[0])),
            .filter = filter,
        };

        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (::syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) != 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
};

class IsolatedWorker {
public:
    static void execute(ScopedDescriptor ipc_channel) noexcept {
        auto result = SeccompFilterBuilder::apply_strict_sandbox();
        if (!result) {
            ::_exit(127);
        }

        std::array<uint8_t, kMaxPayload> buffer{};
        ssize_t bytes_read = ::read(ipc_channel.get(), buffer.data(), buffer.size());
        if (bytes_read < 16) {
            ::_exit(1);
        }

        ParsedHeaderDTO header{};
        std::memcpy(&header.magic, buffer.data(), 4);
        std::memcpy(&header.width, buffer.data() + 4, 4);
        std::memcpy(&header.height, buffer.data() + 8, 4);
        std::memcpy(&header.checksum, buffer.data() + 12, 4);

        if (header.magic != 0x54494646) { // "TIFF"
            ::_exit(2);
        }

        if (::write(ipc_channel.get(), &header, sizeof(header)) != sizeof(header)) {
            ::_exit(3);
        }

        ::_exit(0);
    }
};

class MasterHost {
public:
    static std::expected<ParsedHeaderDTO, std::string> process_untrusted_payload(std::span<const uint8_t> payload) {
        int sv[2];
        if (::socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) != 0) {
            return std::unexpected("Не вдалося створити socketpair");
        }

        ScopedDescriptor master_sock(sv[0]);
        ScopedDescriptor worker_sock(sv[1]);

        pid_t pid = ::fork();
        if (pid < 0) {
            return std::unexpected("Помилка fork()");
        }

        if (pid == 0) {
            master_sock.~ScopedDescriptor();
            IsolatedWorker::execute(std::move(worker_sock));
        }

        worker_sock.~ScopedDescriptor();

        if (::write(master_sock.get(), payload.data(), payload.size()) != static_cast<ssize_t>(payload.size())) {
            return std::unexpected("Помилка запису в сокет воркера");
        }

        ParsedHeaderDTO header{};
        ssize_t read_bytes = ::read(master_sock.get(), &header, sizeof(header));

        int status = 0;
        ::waitpid(pid, &status, 0);

        if (WIFSIGNALED(status)) {
            if (WTERMSIG(status) == SIGSYS) {
                return std::unexpected("SECURITY VIOLATION: Воркер знищено сигналом SIGSYS за спробу недозволеного системного виклику!");
            }
            return std::unexpected("Воркер завершився аварійно");
        }

        if (WIFEXITED(status) && WEXITSTATUS(status) == 0 && read_bytes == sizeof(header)) {
            return header;
        }

        return std::unexpected("Воркер повернув помилку валідації");
    }
};

} // namespace sandbox

int main() {
    const std::array<uint8_t, 16> sample_packet = {
        0x46, 0x46, 0x49, 0x54, // "TIFF"
        0x00, 0x08, 0x00, 0x00, // Width: 2048
        0x00, 0x06, 0x00, 0x00, // Height: 1536
        0xAA, 0xBB, 0xCC, 0xDD
    };

    auto result = sandbox::MasterHost::process_untrusted_payload(sample_packet);
    if (result) {
        std::cout << "[C++ OK] Розібрано в пісочниці: " << result->width << "x" << result->height << std::endl;
    } else {
        std::cerr << "[C++ ERROR] " << result.error() << std::endl;
    }

    return 0;
}
