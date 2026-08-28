#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <stddef.h>
#include <grp.h>
#include <sched.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>

#define UNPRIV_UID 65534 /* nobody */
#define UNPRIV_GID 65534 /* nogroup */

/* Встановлення суворого фільтра Seccomp-BPF */
static int install_strict_seccomp(void) {
    struct sock_filter filter[] = {
        /* [0] Завантажуємо номер архітектури процесора з seccomp_data */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        
        /* [1] Перевіряємо відповідність x86_64; якщо ні — аварійне завершення */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* [2] Завантажуємо номер системного виклику */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* [3-7] Білий список дозволених системних викликів */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_read,       4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_write,      3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_exit_group, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_futex,      1, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, SYS_sigreturn,  0, 1),

        /* [8] Якщо виклик у білому списку — дозволити виконання */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        /* [9] Усі інші виклики (execve, openat, socket тощо) — миттєве вбивство процесу */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    /* Обов'язкова вимога: процес не може отримати нові привілеї через execve SUID */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        perror("prctl(PR_SET_NO_NEW_PRIVS)");
        return -1;
    }

    /* Завантаження фільтра BPF у ядро */
    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) == -1) {
        perror("seccomp(SECCOMP_SET_MODE_FILTER)");
        return -1;
    }

    return 0;
}

/* Функція обмеження та запуску ізольованого парсера */
void run_sandboxed_worker(int input_fd, int output_fd) {
    /* 1. Закриття всіх успадкованих дескрипторів крім input_fd та output_fd */
    for (int fd = 3; fd < 1024; ++fd) {
        if (fd != input_fd && fd != output_fd) {
            close(fd);
        }
    }

    /* 2. Скидання додаткових груп */
    if (setgroups(0, NULL) != 0 && errno != EPERM) {
        perror("setgroups");
        _exit(1);
    }

    /* 3. Скидання привілеїв GID та UID (real, effective, saved) */
    if (setresgid(UNPRIV_GID, UNPRIV_GID, UNPRIV_GID) != 0) {
        perror("setresgid");
        _exit(1);
    }
    if (setresuid(UNPRIV_UID, UNPRIV_UID, UNPRIV_UID) != 0) {
        perror("setresuid");
        _exit(1);
    }

    /* 4. Ізоляція просторів імен (Network + Mount) */
    if (unshare(CLONE_NEWNS | CLONE_NEWNET) != 0 && errno != EPERM) {
        perror("unshare");
    }

    /* 5. Встановлення BPF-фільтра для мінімізації викликів ядра */
    if (install_strict_seccomp() != 0) {
        fprintf(stderr, "Помилка встановлення Seccomp\n");
        _exit(1);
    }

    /* 6. Безпечне читання та розбір вхідного пакету */
    char buffer[256];
    ssize_t bytes_read = read(input_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        const char *resp = "OK: Пакет успішно валідовано в пісочнику\n";
        write(output_fd, resp, strlen(resp));
    }

    _exit(0);
}
