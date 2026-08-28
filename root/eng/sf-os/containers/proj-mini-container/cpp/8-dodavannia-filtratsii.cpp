#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <cstddef>
#include <vector>

static bool applySeccompFilter() noexcept {
    const std::vector<sock_filter> filter = {
        // 1. Перевірка архітектури
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(seccomp_data, arch))),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        // 2. Завантаження номера виклику
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(seccomp_data, nr))),

        // 3. Блокування reboot
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_reboot, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        // 4. Блокування kexec_load
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_kexec_load, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        // 5. Блокування init_module
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_init_module, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        // 6. Дозвіл решти викликів
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
    };

    const sock_fprog prog = {
        .len = static_cast<unsigned short>(filter.size()),
        .filter = const_cast<sock_filter*>(filter.data())
    };

    return ::prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == 0;
}
