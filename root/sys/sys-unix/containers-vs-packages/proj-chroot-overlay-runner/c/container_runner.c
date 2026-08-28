/* container_runner.c — Мінімальний контейнерний рушій мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sched.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <errno.h>

#define STACK_SIZE (1024 * 1024)

struct container_config {
    const char *lower_dir;
    const char *upper_dir;
    const char *work_dir;
    const char *merged_dir;
    const char *hostname;
};

static int ensure_dir(const char *path) {
    if (mkdir(path, 0755) < 0 && errno != EEXIST) {
        perror("mkdir failed");
        return -1;
    }
    return 0;
}

static int child_main(void *arg) {
    struct container_config *cfg = (struct container_config *)arg;
    char mount_opts[1024];

    /* 1. Налаштування нового hostname в UTS namespace */
    if (sethostname(cfg->hostname, strlen(cfg->hostname)) < 0) {
        perror("sethostname failed");
        return -1;
    }

    /* 2. Захист від поширення монтів у хостовий namespace */
    if (mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) < 0) {
        perror("mount MS_PRIVATE failed");
        return -1;
    }

    /* 3. Формування опцій для драйвера OverlayFS */
    snprintf(mount_opts, sizeof(mount_opts),
             "lowerdir=%s,upperdir=%s,workdir=%s",
             cfg->lower_dir, cfg->upper_dir, cfg->work_dir);

    /* 4. Монтування OverlayFS у каталог merged */
    if (mount("overlay", cfg->merged_dir, "overlay", 0, mount_opts) < 0) {
        perror("mount overlayfs failed");
        return -1;
    }

    /* 5. Зміна кореневого каталогу на merged */
    if (chroot(cfg->merged_dir) < 0) {
        perror("chroot failed");
        umount(cfg->merged_dir);
        return -1;
    }

    if (chdir("/") < 0) {
        perror("chdir root failed");
        return -1;
    }

    /* 6. Монтування /proc для нового PID namespace */
    ensure_dir("/proc");
    if (mount("proc", "/proc", "proc", 0, NULL) < 0) {
        perror("mount /proc failed");
        return -1;
    }

    printf("[Child Container] Rootfs й namespaces успішно ініціалізовано!\n");
    printf("[Child Container] Запуск /bin/sh (PID у контейнері = %d)...\n", getpid());

    /* 7. Запуск оболонки усередині контейнера */
    char *const argv[] = { "/bin/sh", NULL };
    char *const envp[] = { "PATH=/bin:/usr/bin", "TERM=xterm", NULL };

    execve("/bin/sh", argv, envp);

    /* У разі помилки execve */
    perror("execve failed");
    return -1;
}

int main(int argc, char *argv[]) {
    (void)argc; (void)argv;
    struct container_config cfg = {
        .lower_dir  = "/tmp/mini_container/lower",
        .upper_dir  = "/tmp/mini_container/upper",
        .work_dir   = "/tmp/mini_container/work",
        .merged_dir = "/tmp/mini_container/merged",
        .hostname   = "isolated-container"
    };

    printf("[Host] Підготовка каталогів для OverlayFS...\n");
    if (ensure_dir("/tmp/mini_container") < 0 ||
        ensure_dir(cfg.lower_dir) < 0 ||
        ensure_dir(cfg.upper_dir) < 0 ||
        ensure_dir(cfg.work_dir) < 0 ||
        ensure_dir(cfg.merged_dir) < 0) {
        fprintf(stderr, "Помилка створення каталогів\n");
        return EXIT_FAILURE;
    }

    /* Виділення стеку для дочірнього процесу */
    char *stack = malloc(STACK_SIZE);
    if (!stack) {
        perror("malloc stack failed");
        return EXIT_FAILURE;
    }

    printf("[Host] Створення дочірнього процесу через clone()...\n");
    int flags = CLONE_NEWNS | CLONE_NEWPID | CLONE_NEWUTS | SIGCHLD;
    pid_t child_pid = clone(child_main, stack + STACK_SIZE, flags, &cfg);

    if (child_pid < 0) {
        perror("clone failed");
        free(stack);
        return EXIT_FAILURE;
    }

    printf("[Host] Дочірній процес запуск з PID %d на хості.\n", child_pid);

    int status;
    waitpid(child_pid, &status, 0);

    printf("[Host] Контейнер завершив роботу з кодом %d.\n", WEXITSTATUS(status));

    /* Очищення монтування після виходу контейнера */
    umount(cfg.merged_dir);
    free(stack);
    return EXIT_SUCCESS;
}
