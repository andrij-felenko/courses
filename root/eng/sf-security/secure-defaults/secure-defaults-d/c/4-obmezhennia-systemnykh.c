#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/prctl.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include <stddef.h>
#include <errno.h>

/* Встановлення безпечної маски та захищене створення файлу конфігурації */
int create_secure_config_file(const char* filepath) {
    /* 1. Безпечний дефолт umask: лише власник має права читання й запису */
    mode_t old_mask = umask(0077);

    /* 2. Створення з явними прапорцями безпеки: O_EXCL запобігає перетиранню симлінків */
    int fd = open(filepath, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    
    /* Відновлення системної маски */
    umask(old_mask);

    if (fd < 0) {
        return -1;
    }
    return fd;
}

/* Ініціалізація Seccomp-BPF з політикою Default Deny (KILL) */
int apply_strict_seccomp_sandbox(void) {
    /* Заборона отримання нових привілеїв через execve */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        return -1;
    }

    struct sock_filter filter[] = {
        /* Завантаження номера системного виклику: BPF_LD | BPF_W | BPF_ABS, offset 0 */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* Дозволені виклики: явний білий список */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_read, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_write, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit_group, 0, 1),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        /* БЕЗПЕЧНИЙ ДЕФОЛТ: Будь-який інший системний виклик негайно вбиває процес */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog) != 0) {
        return -1;
    }

    return 0;
}
