#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <sys/syscall.h>

#define MAX_PAYLOAD 512

/* Структура безпечного DTO для повернення розібраних даних */
typedef struct {
    uint32_t magic;
    uint32_t width;
    uint32_t height;
    uint32_t checksum;
} ParsedHeaderDTO;

/* Встановлення фільтра Seccomp-BPF */
static int install_sandbox_filter(void) {
    struct sock_filter filter[] = {
        /* [0] Перевірка архітектури: завантажити seccomp_data.arch */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
#if defined(__x86_64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
#elif defined(__aarch64__)
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_AARCH64, 1, 0),
#else
#error "Непідтримувана архітектура CPU"
#endif
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* [3] Завантажити номер системного виклику: seccomp_data.nr */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* Білий список дозволених системних викликів */
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

        /* Усі інші системні виклики (open, execve, socket) знищують процес */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS)
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    /* Заборона на підняття привілеїв (обов'язково для непривілейованого seccomp) */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        return -1;
    }

    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) != 0) {
        return -1;
    }
    return 0;
}

/* Логіка парсера всередині ізольованого воркера */
static void run_parser_worker(int ipc_fd) {
    if (install_sandbox_filter() != 0) {
        _exit(127);
    }

    uint8_t input_buf[MAX_PAYLOAD];
    ssize_t n = read(ipc_fd, input_buf, sizeof(input_buf));
    if (n < 16) {
        _exit(1);
    }

    /* Простий парсинг заголовка формату: Magic(4) | W(4) | H(4) | CRC(4) */
    ParsedHeaderDTO result;
    memcpy(&result.magic, input_buf, 4);
    memcpy(&result.width, input_buf + 4, 4);
    memcpy(&result.height, input_buf + 8, 4);
    memcpy(&result.checksum, input_buf + 12, 4);

    /* Перевірка магічного байта */
    if (result.magic != 0x54494646) { /* "TIFF" */
        _exit(2);
    }

    /* Надсилання безпечного результату майстру */
    if (write(ipc_fd, &result, sizeof(result)) != (ssize_t)sizeof(result)) {
        _exit(3);
    }

    _exit(0);
}

/* Головний привілейований процес (Master) */
int main(void) {
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_SEQPACKET, 0, sv) != 0) {
        perror("socketpair");
        return EXIT_FAILURE;
    }

    pid_t child_pid = fork();
    if (child_pid < 0) {
        perror("fork");
        close(sv[0]);
        close(sv[1]);
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        /* Дочірній процес */
        close(sv[0]); /* Закриваємо сторону майстра */
        run_parser_worker(sv[1]);
    }

    /* Батьківський процес */
    close(sv[1]); /* Закриваємо сторону воркера */

    /* Імітація вхідного пакету від зовнішнього клієнта */
    uint8_t untrusted_input[16] = {
        0x46, 0x46, 0x49, 0x54, /* Magic: "TIFF" у little-endian */
        0x00, 0x04, 0x00, 0x00, /* Width: 1024 */
        0x00, 0x03, 0x00, 0x00, /* Height: 768 */
        0xEF, 0xBE, 0xAD, 0xDE  /* Checksum */
    };

    /* Передача сирих даних у пісочницю */
    if (write(sv[0], untrusted_input, sizeof(untrusted_input)) != sizeof(untrusted_input)) {
        perror("master write");
    }

    /* Очікування безпечного результату від воркера */
    ParsedHeaderDTO header;
    ssize_t read_bytes = read(sv[0], &header, sizeof(header));

    int status = 0;
    waitpid(child_pid, &status, 0);

    if (WIFSIGNALED(status)) {
        int sig = WTERMSIG(status);
        if (sig == SIGSYS) {
            printf("[SECURITY ALERT] Воркер знищено ядром через спробу забороненого системного виклику (SIGSYS)!\n");
        } else {
            printf("[ALERT] Воркер загинув від сигналу %d\n", sig);
        }
    } else if (WIFEXITED(status) && WEXITSTATUS(status) == 0 && read_bytes == sizeof(header)) {
        printf("[OK] Заголовок успішно розібрано у пісочниці: Width=%u, Height=%u\n", header.width, header.height);
    } else {
        printf("[ERROR] Воркер завершився з кодом помилки %d\n", WEXITSTATUS(status));
    }

    close(sv[0]);
    return EXIT_SUCCESS;
}
