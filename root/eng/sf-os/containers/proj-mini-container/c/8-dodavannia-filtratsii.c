#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>

static int apply_seccomp_filter(void) {
    struct sock_filter filter[] = {
        /* 1. Завантаження номера системної архітектури в акумулятор BPF */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        /* Перевірка архітектури x86_64; якщо не збігається — вбити процес */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* 2. Завантаження номера системного виклику в акумулятор */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* 3. Блокування виклику reboot (перезавантаження сервера) */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_reboot, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        /* 4. Блокування виклику kexec_load (заміна ядра на льоту) */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_kexec_load, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        /* 5. Блокування виклику init_module (завантаження драйверів) */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_init_module, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        /* 6. Дозвіл для всіх інших системних викликів */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW)
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) {
        perror("Помилка завантаження фільтра Seccomp-BPF");
        return -1;
    }
    return 0;
}
