#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>

#define syscall_nr (offsetof(struct seccomp_data, nr))
#define arch_nr (offsetof(struct seccomp_data, arch))

int install_minimal_cbpf_filter(void) {
    // 1. Встановлюємо NO_NEW_PRIVS
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    // 2. Формуємо масив BPF інструкцій
    struct sock_filter filter[] = {
        // [0] A = seccomp_data.arch
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, arch_nr),

        // [1] якщо arch == AUDIT_ARCH_X86_64, перейти до [2] (jt=0), інакше до [8] (jf=6 -> KILL)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 0, 6),

        // [2] A = seccomp_data.nr
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, syscall_nr),

        // Перевірка білого списку викликів
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read, 3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group, 1, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit, 0, 1),

        // [7] Дозволити системний виклик
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        // [8] Заблокувати та вбити процес
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    // 3. Завантажуємо фільтр
    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == -1) {
        perror("prctl(SECCOMP_MODE_FILTER)");
        return -1;
    }

    return 0;
}
