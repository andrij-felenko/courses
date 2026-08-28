#define _GNU_SOURCE
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <stddef.h>
#include <stdio.h>
#include <errno.h>

int install_worker_seccomp_filter(void) {
    /* 1. Блокуємо підвищення привілеїв (обов'язкова передумова Seccomp) */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    /* 2. Масив інструкцій класичного Berkeley Packet Filter (cBPF) */
    struct sock_filter filter[] = {
        /* [0] Завантажуємо номер архітектури процесора з seccomp_data.arch */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        
        /* [1] Перевіряємо архітектуру x86_64; у разі невідповідності — вбиваємо процес */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* [2] Завантажуємо номер системного виклику з seccomp_data.nr */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* [3..12] Перевіряємо номер виклику проти дозволеного білого списку */
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

        /* За замовчуванням блокуємо виклик і повертаємо EPERM */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & SECCOMP_RET_DATA)),

        /* Дозвіл для системних викликів із білого списку */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    /* Завантажуємо BPF-фільтр у контекст поточного процесу */
    if (syscall(__NR_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) != 0) {
        perror("seccomp(SECCOMP_SET_MODE_FILTER)");
        return -1;
    }
    return 0;
}
