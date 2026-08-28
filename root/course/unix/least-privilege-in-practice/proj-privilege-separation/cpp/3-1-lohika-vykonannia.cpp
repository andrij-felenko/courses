#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <cstddef>
#include <expected>
#include <system_error>
#include <array>

[[nodiscard]] std::expected<void, std::error_code> install_worker_seccomp() noexcept {
    // Встановлення прапорця блокування нових привілеїв
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    constexpr std::array filter = {
        // Перевірка архітектури CPU
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        // Завантаження номера виклику
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        // Білий список системних викликів
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read,            10, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write,           9, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_recvmsg,         8, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_sendmsg,         7, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_close,           6, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_epoll_wait,      5, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_epoll_ctl,       4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_futex,           3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_restart_syscall, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group,      1, 0),

        // Блокування всіх інших викликів із кодом помилки EPERM
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        // Дозвіл для системних викликів із білого списку
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog{
        .len = static_cast<unsigned short>(filter.size()),
        .filter = const_cast<struct sock_filter*>(filter.data()),
    };

    if (::syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
