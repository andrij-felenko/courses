#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stddef.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/syscall.h>
#include <sys/prctl.h>
#include <sys/sysmacros.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>

#define STACK_SIZE (1024 * 1024)
#define CGROUP_PATH "/sys/fs/cgroup/minibox"

struct container_config {
    const char *rootfs;
    char **argv;
    int sync_pipe[2];
};

static int pivot_root_syscall(const char *new_root, const char *put_old) {
    return syscall(SYS_pivot_root, new_root, put_old);
}

static int write_file(const char *path, const char *value) {
    int fd = open(path, O_WRONLY | O_TRUNC);
    if (fd < 0) return -1;
    size_t len = strlen(value);
    ssize_t written = write(fd, value, len);
    close(fd);
    return (written == (ssize_t)len) ? 0 : -1;
}

static int setup_cgroup(pid_t pid) {
    mkdir(CGROUP_PATH, 0755);

    char pid_str[32];
    snprintf(pid_str, sizeof(pid_str), "%d\n", pid);

    char procs_path[256];
    snprintf(procs_path, sizeof(procs_path), "%s/cgroup.procs", CGROUP_PATH);
    if (write_file(procs_path, pid_str) < 0) {
        perror("cgroup.procs");
        return -1;
    }

    char mem_path[256];
    snprintf(mem_path, sizeof(mem_path), "%s/memory.max", CGROUP_PATH);
    write_file(mem_path, "67108864\n"); /* 64 MB */

    char cpu_path[256];
    snprintf(cpu_path, sizeof(cpu_path), "%s/cpu.max", CGROUP_PATH);
    write_file(cpu_path, "20000 100000\n"); /* 20% одного ядра */

    char pids_path[256];
    snprintf(pids_path, sizeof(pids_path), "%s/pids.max", CGROUP_PATH);
    write_file(pids_path, "32\n"); /* Максимум 32 процеси */

    return 0;
}

static int install_seccomp_filter(void) {
    struct sock_filter filter[] = {
        /* 1. Перевірка архітектури процесора (x86_64) */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, arch))),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL_PROCESS),

        /* 2. Завантаження номера системного виклику */
        BPF_STMT(BPF_LD | BPF_W | BPF_ABS, (offsetof(struct seccomp_data, nr))),

        /* 3. Блокування небезпечних для хоста системних викликів */
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_reboot, 5, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_kexec_load, 4, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_init_module, 3, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_finit_module, 2, 0),
        BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_swapon, 1, 0),

        /* 4. Дозвіл для всіх інших системних викликів */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),

        /* 5. Повернення помилки EPERM для заборонених викликів */
        BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ERRNO | (EPERM & 0xffff))
    };

    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) {
        perror("prctl(NO_NEW_PRIVS)");
        return -1;
    }

    if (syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, 0, &prog) < 0) {
        perror("seccomp");
        return -1;
    }

    return 0;
}

static int setup_rootfs(const char *rootfs) {
    /* 1. Ізоляція дерева монтування від хоста */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) < 0) {
        perror("mount MS_PRIVATE");
        return -1;
    }

    /* 2. Bind mount для перетворення каталогу rootfs на точку монтування VFS */
    if (mount(rootfs, rootfs, NULL, MS_BIND | MS_REC, NULL) < 0) {
        perror("mount bind rootfs");
        return -1;
    }

    /* 3. Створення підкаталогу для тимчасового перенесення старого кореня */
    char old_root[512];
    snprintf(old_root, sizeof(old_root), "%s/.old_root", rootfs);
    mkdir(old_root, 0700);

    /* 4. Атомарний обмін кореневих дерев */
    if (pivot_root_syscall(rootfs, old_root) < 0) {
        perror("pivot_root");
        return -1;
    }

    if (chdir("/") < 0) {
        perror("chdir /");
        return -1;
    }

    /* 5. Відмонтування старого кореня та видалення точки монтування */
    if (umount2("/.old_root", MNT_DETACH) < 0) {
        perror("umount2 .old_root");
        return -1;
    }
    rmdir("/.old_root");

    /* 6. Монтування приватних віртуальних файлових систем */
    mkdir("/proc", 0755);
    if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) < 0) {
        perror("mount /proc");
        return -1;
    }

    mkdir("/sys", 0755);
    if (mount("sysfs", "/sys", "sysfs", MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL) < 0) {
        perror("mount /sys");
        return -1;
    }

    mkdir("/dev", 0755);
    mount("tmpfs", "/dev", "tmpfs", MS_NOSUID | MS_STRICTATIME, "mode=755");

    /* Створення мінімального набору файлів пристроїв */
    mknod("/dev/null", S_IFCHR | 0666, makedev(1, 3));
    mknod("/dev/zero", S_IFCHR | 0666, makedev(1, 5));
    mknod("/dev/urandom", S_IFCHR | 0666, makedev(1, 9));

    return 0;
}

static int container_entry(void *arg) {
    struct container_config *cfg = (struct container_config *)arg;

    /* Закриваємо записуючий дескриптор і чекаємо налаштування cgroups */
    close(cfg->sync_pipe[1]);
    char ch;
    if (read(cfg->sync_pipe[0], &ch, 1) != 0) {
        /* EOF означає успішну ініціалізацію батьківським процесом */
    }
    close(cfg->sync_pipe[0]);

    sethostname("minibox", 7);

    if (setup_rootfs(cfg->rootfs) < 0) {
        fprintf(stderr, "Помилка налаштування файлового середовища rootfs\n");
        return 1;
    }

    if (install_seccomp_filter() < 0) {
        fprintf(stderr, "Помилка завантаження фільтра seccomp\n");
        return 1;
    }

    /* Запуск цільової програми всередині контейнера */
    execvp(cfg->argv[0], cfg->argv);
    perror("execvp");
    return 1;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <шлях_до_rootfs> <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    if (getuid() != 0) {
        fprintf(stderr, "Помилка: потрібні права суперкористувача (root)\n");
        return 1;
    }

    struct container_config cfg;
    cfg.rootfs = argv[1];
    cfg.argv = &argv[2];

    if (pipe(cfg.sync_pipe) < 0) {
        perror("pipe");
        return 1;
    }

    char *stack = malloc(STACK_SIZE);
    if (!stack) {
        perror("malloc stack");
        return 1;
    }
    char *stack_top = stack + STACK_SIZE;

    int clone_flags = CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS |
                      CLONE_NEWIPC | CLONE_NEWNET | CLONE_NEWCGROUP | SIGCHLD;

    pid_t child_pid = clone(container_entry, stack_top, clone_flags, &cfg);
    if (child_pid < 0) {
        perror("clone");
        free(stack);
        return 1;
    }

    /* Батьківський процес закриває читаючий кінець каналу */
    close(cfg.sync_pipe[0]);

    /* Налаштування контрольних груп для дочірнього процесу */
    if (setup_cgroup(child_pid) < 0) {
        fprintf(stderr, "Не вдалося налаштувати cgroup для PID %d\n", child_pid);
        kill(child_pid, SIGKILL);
        close(cfg.sync_pipe[1]);
        free(stack);
        return 1;
    }

    /* Надсилаємо сигнал розблокування дочірньому процесу */
    close(cfg.sync_pipe[1]);

    int status;
    waitpid(child_pid, &status, 0);

    /* Зачистка каталогів cgroups */
    rmdir(CGROUP_PATH);
    free(stack);

    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return 0;
}
