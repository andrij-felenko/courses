#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <linux/capability.h>

#define STACK_SIZE (1024 * 1024) /* 1 МБ стек для дочірнього процесу */
#define CGROUP_BASE "/sys/fs/cgroup/minicontainer"

struct container_config {
    const char *rootfs;
    const char *hostname;
    long memory_limit_bytes;
    long cpu_quota_usec;
    long cpu_period_usec;
    int sync_pipe[2];
    char **argv;
};

/* Обгортка над системним викликом pivot_root */
static int sys_pivot_root(const char *new_root, const char *put_old) {
    return syscall(SYS_pivot_root, new_root, put_old);
}

/* Скидання небезпечних Capabilities */
static int drop_capabilities(void) {
    const int caps_to_drop[] = {
        CAP_SYS_ADMIN,
        CAP_SYS_MODULE,
        CAP_SYS_RAWIO,
        CAP_SYS_PTRACE,
        CAP_NET_ADMIN,
        CAP_DAC_OVERRIDE
    };
    size_t count = sizeof(caps_to_drop) / sizeof(caps_to_drop[0]);

    for (size_t i = 0; i < count; i++) {
        if (prctl(PR_CAPBSET_DROP, caps_to_drop[i], 0, 0, 0) != 0) {
            /* Якщо ядро не підтримує якийсь cap або немає прав */
            if (errno != EINVAL) {
                perror("Помилка prctl(PR_CAPBSET_DROP)");
                return -1;
            }
        }
    }
    return 0;
}

/* Налаштування ізольованої файлової системи VFS */
static int setup_rootfs(const char *rootfs_path) {
    char old_root_path[512];

    /* 1. Запобігання витоку монтувань на хостову систему */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) != 0) {
        perror("Помилка переведення кореня в MS_PRIVATE");
        return -1;
    }

    /* 2. Bind-монтування кореневого каталогу на самого себе (вимога pivot_root) */
    if (mount(rootfs_path, rootfs_path, "bind", MS_BIND | MS_REC, NULL) != 0) {
        perror("Помилка bind mount rootfs");
        return -1;
    }

    /* 3. Створення каталогу для тимчасового зберігання старого кореня */
    snprintf(old_root_path, sizeof(old_root_path), "%s/.old_root", rootfs_path);
    if (mkdir(old_root_path, 0700) != 0 && errno != EEXIST) {
        perror("Помилка створення .old_root");
        return -1;
    }

    /* 4. Атомарний обмін кореневих точок монтування */
    if (sys_pivot_root(rootfs_path, old_root_path) != 0) {
        perror("Помилка pivot_root");
        return -1;
    }

    /* 5. Перехід у новий корінь */
    if (chdir("/") != 0) {
        perror("Помилка chdir до нового кореня");
        return -1;
    }

    /* 6. Демонтування та видалення старого хостового кореня */
    if (umount2("/.old_root", MNT_DETACH) != 0) {
        perror("Помилка umount2 .old_root");
        return -1;
    }
    rmdir("/.old_root");

    /* 7. Монтування обов'язкових віртуальних файлових систем */
    if (mount("proc", "/proc", "proc", MS_NOSUID | MS_NOEXEC | MS_NODEV, NULL) != 0) {
        perror("Помилка монтування /proc");
        return -1;
    }
    if (mount("sysfs", "/sys", "sysfs", MS_NOSUID | MS_NOEXEC | MS_NODEV | MS_RDONLY, NULL) != 0) {
        perror("Помилка монтування /sys");
        return -1;
    }
    if (mount("tmpfs", "/dev", "tmpfs", MS_NOSUID | MS_STRICTATIME, "mode=755") != 0) {
        perror("Помилка монтування /dev");
        return -1;
    }

    return 0;
}

/* Функція, що виконується в новому просторі процесів PID 1 */
static int container_entrypoint(void *arg) {
    struct container_config *cfg = (struct container_config *)arg;
    char sync_byte;

    /* Закриваємо записуючий кінець каналу */
    close(cfg->sync_pipe[1]);

    /* Блокуюче очікування завершення налаштування cgroups батьківським процесом */
    if (read(cfg->sync_pipe[0], &sync_byte, 1) != 1) {
        fprintf(stderr, "Помилка отримання сигналу синхронізації від батька\n");
        close(cfg->sync_pipe[0]);
        return 1;
    }
    close(cfg->sync_pipe[0]);

    /* Встановлення власного імені хоста */
    if (sethostname(cfg->hostname, strlen(cfg->hostname)) != 0) {
        perror("Помилка sethostname");
        return 1;
    }

    /* Налаштування ізольованого файлового дерева */
    if (setup_rootfs(cfg->rootfs) != 0) {
        fprintf(stderr, "Не вдалося ініціалізувати кореневу файлову систему\n");
        return 1;
    }

    /* Скидання небезпечних привілеїв */
    if (drop_capabilities() != 0) {
        fprintf(stderr, "Не вдалося скинути Linux Capabilities\n");
        return 1;
    }

    /* Заборона підвищення привілеїв через SUID */
    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        perror("Помилка активації PR_SET_NO_NEW_PRIVS");
        return 1;
    }

    /* Запуск цільової програми */
    printf("[minicontainer] Контейнер успішно запущено. Передача керування PID 1...\n");
    execvp(cfg->argv[0], cfg->argv);

    /* Якщо execvp повернув керування — сталася помилка */
    perror("Помилка виконання execvp");
    return 127;
}

/* Створення та конфігурація контрольної групи cgroups v2 */
static int setup_cgroups(pid_t child_pid, const struct container_config *cfg, char *cg_path_out, size_t max_len) {
    char file_path[512];
    FILE *f;

    snprintf(cg_path_out, max_len, "%s-%d", CGROUP_BASE, child_pid);

    /* Створення каталогу cgroup для контейнера */
    if (mkdir(cg_path_out, 0755) != 0 && errno != EEXIST) {
        perror("Помилка створення каталогу cgroup v2");
        return -1;
    }

    /* 1. Встановлення ліміту пам'яті (memory.max) */
    snprintf(file_path, sizeof(file_path), "%s/memory.max", cg_path_out);
    f = fopen(file_path, "w");
    if (!f) {
        perror("Помилка відкриття memory.max");
        return -1;
    }
    fprintf(f, "%ld\n", cfg->memory_limit_bytes);
    fclose(f);

    /* 2. Встановлення квоти CPU (cpu.max) */
    snprintf(file_path, sizeof(file_path), "%s/cpu.max", cg_path_out);
    f = fopen(file_path, "w");
    if (!f) {
        perror("Помилка відкриття cpu.max");
        return -1;
    }
    fprintf(f, "%ld %ld\n", cfg->cpu_quota_usec, cfg->cpu_period_usec);
    fclose(f);

    /* 3. Додавання PID дочірнього процесу в групу (cgroup.procs) */
    snprintf(file_path, sizeof(file_path), "%s/cgroup.procs", cg_path_out);
    f = fopen(file_path, "w");
    if (!f) {
        perror("Помилка відкриття cgroup.procs");
        return -1;
    }
    fprintf(f, "%d\n", child_pid);
    fclose(f);

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <шлях_до_rootfs> <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    /* Перевірка прав суперкористувача (потрібні для створення namespaces та mount) */
    if (geteuid() != 0) {
        fprintf(stderr, "Помилка: запуск контейнера вимагає прав root (sudo)\n");
        return 1;
    }

    struct container_config cfg = {
        .rootfs = argv[1],
        .hostname = "minicontainer",
        .memory_limit_bytes = 256 * 1024 * 1024, /* Ліміт пам'яті: 256 МіБ */
        .cpu_quota_usec = 100000,                /* Квота CPU: 1.0 ядро (100 мс) */
        .cpu_period_usec = 100000,               /* Період CFS: 100 мс */
        .argv = &argv[2]
    };

    /* Створення каналу синхронізації */
    if (pipe(cfg.sync_pipe) != 0) {
        perror("Помилка створення pipe");
        return 1;
    }

    /* Виділення пам'яті під стек дочірнього процесу */
    char *stack = malloc(STACK_SIZE);
    if (!stack) {
        perror("Помилка виділення стеку");
        return 1;
    }
    char *stack_top = stack + STACK_SIZE;

    /* Прапорці ізоляції просторів назв */
    int clone_flags = CLONE_NEWPID |  /* Власне дерево процесів */
                      CLONE_NEWNS  |  /* Власні точки монтування VFS */
                      CLONE_NEWUTS |  /* Власне ім'я хоста */
                      CLONE_NEWIPC |  /* Власні черги IPC */
                      CLONE_NEWNET |  /* Власний мережевий стек */
                      SIGCHLD;        /* Сигнал завершення батькові */

    printf("[minicontainer] Створення дочірнього процесу через clone()...\n");
    pid_t child_pid = clone(container_entrypoint, stack_top, clone_flags, &cfg);
    if (child_pid < 0) {
        perror("Помилка clone()");
        free(stack);
        return 1;
    }

    /* Закриваємо читаючий кінець каналу в батькові */
    close(cfg.sync_pipe[0]);

    /* Конфігурація cgroups v2 для запущеного процесу */
    char cg_path[256];
    printf("[minicontainer] Налаштування лімітів cgroups v2 для PID %d...\n", child_pid);
    if (setup_cgroups(child_pid, &cfg, cg_path, sizeof(cg_path)) != 0) {
        fprintf(stderr, "Аварійна зупинка: не вдалося налаштувати cgroups\n");
        kill(child_pid, SIGKILL);
        waitpid(child_pid, NULL, 0);
        free(stack);
        return 1;
    }

    /* Сповіщення дочірнього процесу про завершення налаштування cgroups */
    char sync_byte = 'G';
    write(cfg.sync_pipe[1], &sync_byte, 1);
    close(cfg.sync_pipe[1]);

    /* Очікування завершення виконання контейнера */
    int status;
    waitpid(child_pid, &status, 0);

    /* Очищення каталогу cgroup після завершення */
    rmdir(cg_path);
    free(stack);

    if (WIFEXITED(status)) {
        printf("[minicontainer] Контейнер завершив роботу з кодом %d\n", WEXITSTATUS(status));
    } else if (WIFSIGNALED(status)) {
        printf("[minicontainer] Контейнер убито сигналом %d\n", WTERMSIG(status));
    }

    return 0;
}
