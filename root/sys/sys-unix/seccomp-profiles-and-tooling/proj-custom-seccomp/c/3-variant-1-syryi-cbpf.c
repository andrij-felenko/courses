#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <unistd.h>
#include <errno.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/audit.h>
#include <linux/filter.h>
#include <linux/seccomp.h>

#define syscall_nr (offsetof(struct seccomp_data, nr))
#define arch_nr (offsetof(struct seccomp_data, arch))

int apply_cbpf_worker_sandbox(void) {
    // 1. Обов'язкове вимкнення отримання нових привілеїв
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    struct sock_filter filter[] = {
        // [0] Завантажити номер архітектури у регістр A
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, arch_nr),
        // [1] Перевірити AUDIT_ARCH_X86_64; якщо рівно — перейти далі (jt=0), якщо хиба — перестрибнути до KILL у [10] (jf=8)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 0, 8),

        // [2] Завантажити номер системного виклику у регістр A
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, syscall_nr),

        // Перевірка дозволених викликів білого списку
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read, 5, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_brk, 3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_mmap, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group, 1, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit, 0, 1),

        // [9] ALLOW — дозволити системний виклик
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        // [10] KILL — негайно вбити процес для будь-якого іншого виклику
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) == -1) {
        perror("prctl(SECCOMP_MODE_FILTER)");
        return -1;
    }

    return 0;
}

int main(void) {
    printf("Активація сирого cBPF фільтра...\n");
    if (apply_cbpf_worker_sandbox() < 0) {
        fprintf(stderr, "Помилка встановлення пісочниці\n");
        return 1;
    }

    write(STDOUT_FILENO, "Пісочниця працює успішно!\n", 48);
    return 0;
}
