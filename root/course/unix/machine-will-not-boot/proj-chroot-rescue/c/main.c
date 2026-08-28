#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/wait.h>

#define MAX_MOUNTS 16

typedef struct {
    char target_path[256];
    int is_mounted;
} MountEntry;

typedef struct {
    MountEntry entries[MAX_MOUNTS];
    size_t count;
} MountStack;

static void mount_stack_init(MountStack *stack) {
    stack->count = 0;
}

static int mount_stack_push(MountStack *stack, const char *path) {
    if (stack->count >= MAX_MOUNTS) {
        fprintf(stderr, "Помилка: переповнення стека точок монтування\n");
        return -1;
    }
    strncpy(stack->entries[stack->count].target_path, path, sizeof(stack->entries[0].target_path) - 1);
    stack->entries[stack->count].target_path[sizeof(stack->entries[0].target_path) - 1] = '\0';
    stack->entries[stack->count].is_mounted = 1;
    stack->count++;
    return 0;
}

static void mount_stack_cleanup(MountStack *stack) {
    while (stack->count > 0) {
        stack->count--;
        if (stack->entries[stack->count].is_mounted) {
            printf("[Cleanup] Розмонтування: %s\n", stack->entries[stack->count].target_path);
            if (umount2(stack->entries[stack->count].target_path, MNT_DETACH) != 0) {
                fprintf(stderr, "Попередження: не вдалося розмонтувати %s: %s\n",
                        stack->entries[stack->count].target_path, strerror(errno));
            }
        }
    }
}

static int ensure_dir_exists(const char *path) {
    struct stat st;
    if (stat(path, &st) == 0) {
        if (S_ISDIR(st.st_mode)) return 0;
        fprintf(stderr, "Помилка: %s існує, але не є каталогом\n", path);
        return -1;
    }
    if (mkdir(path, 0755) != 0 && errno != EEXIST) {
        fprintf(stderr, "Помилка створення каталогу %s: %s\n", path, strerror(errno));
        return -1;
    }
    return 0;
}

int setup_and_enter_chroot(const char *target_root, char *const argv_exec[]) {
    if (geteuid() != 0) {
        fprintf(stderr, "Помилка: для монтування та chroot потрібні права root (CAP_SYS_ADMIN)\n");
        return -1;
    }

    MountStack stack;
    mount_stack_init(&stack);

    char proc_path[512], sys_path[512], dev_path[512], run_path[512];
    snprintf(proc_path, sizeof(proc_path), "%s/proc", target_root);
    snprintf(sys_path, sizeof(sys_path), "%s/sys", target_root);
    snprintf(dev_path, sizeof(dev_path), "%s/dev", target_root);
    snprintf(run_path, sizeof(run_path), "%s/run", target_root);

    if (ensure_dir_exists(proc_path) || ensure_dir_exists(sys_path) ||
        ensure_dir_exists(dev_path) || ensure_dir_exists(run_path)) {
        mount_stack_cleanup(&stack);
        return -1;
    }

    // 1. Монтування procfs
    printf("[Mount] Підключення proc -> %s\n", proc_path);
    if (mount("proc", proc_path, "proc", 0, NULL) != 0) {
        fprintf(stderr, "Помилка монтування proc: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }
    mount_stack_push(&stack, proc_path);

    // 2. Рекурсивне прив'язування /sys + rslave
    printf("[Mount] Підключення --rbind /sys -> %s\n", sys_path);
    if (mount("/sys", sys_path, NULL, MS_BIND | MS_REC, NULL) != 0) {
        fprintf(stderr, "Помилка rbind sys: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }
    mount_stack_push(&stack, sys_path);
    mount(NULL, sys_path, NULL, MS_SLAVE | MS_REC, NULL);

    // 3. Рекурсивне прив'язування /dev + rslave
    printf("[Mount] Підключення --rbind /dev -> %s\n", dev_path);
    if (mount("/dev", dev_path, NULL, MS_BIND | MS_REC, NULL) != 0) {
        fprintf(stderr, "Помилка rbind dev: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }
    mount_stack_push(&stack, dev_path);
    mount(NULL, dev_path, NULL, MS_SLAVE | MS_REC, NULL);

    // 4. Рекурсивне прив'язування /run + rslave
    printf("[Mount] Підключення --rbind /run -> %s\n", run_path);
    if (mount("/run", run_path, NULL, MS_BIND | MS_REC, NULL) != 0) {
        fprintf(stderr, "Помилка rbind run: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }
    mount_stack_push(&stack, run_path);
    mount(NULL, run_path, NULL, MS_SLAVE | MS_REC, NULL);

    // 5. Вхід у chroot через fork
    pid_t pid = fork();
    if (pid < 0) {
        fprintf(stderr, "Помилка створення процесу fork: %s\n", strerror(errno));
        mount_stack_cleanup(&stack);
        return -1;
    }

    if (pid == 0) {
        // Дочірній процес: зміна кореня
        if (chroot(target_root) != 0) {
            fprintf(stderr, "Помилка виконання chroot: %s\n", strerror(errno));
            exit(EXIT_FAILURE);
        }
        if (chdir("/") != 0) {
            fprintf(stderr, "Помилка переходу в корінь chdir(/): %s\n", strerror(errno));
            exit(EXIT_FAILURE);
        }

        // Встановлення базових змінних середовища
        setenv("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", 1);
        setenv("HOME", "/root", 1);
        setenv("TERM", "xterm-256color", 0);

        printf("\n=== Успішний вхід у ремонтне середовище CHROOT ===\n\n");
        execv(argv_exec[0], argv_exec);

        fprintf(stderr, "Помилка запуску оболонки %s: %s\n", argv_exec[0], strerror(errno));
        exit(EXIT_FAILURE);
    }

    // Батьківський процес очікує завершення сеансу ремонту
    int status = 0;
    waitpid(pid, &status, 0);

    printf("\n=== Завершення сеансу chroot. Початок очищення ===\n");
    mount_stack_cleanup(&stack);
    return WIFEXITED(status) ? WEXITSTATUS(status) : -1;
}

int main(int argc, char *argv[]) {
    const char *target = (argc > 1) ? argv[1] : "/mnt";
    char *default_shell[] = {"/bin/bash", "-l", NULL};
    char **cmd = (argc > 2) ? &argv[2] : default_shell;

    return setup_and_enter_chroot(target, cmd);
}
