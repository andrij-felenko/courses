#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define STACK_SIZE (1024 * 1024)

typedef struct {
    int pipe_fd[2];
    uid_t parent_uid;
    gid_t parent_gid;
} child_args_t;

static int write_proc_file(const char *path, const char *content) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        perror("open proc file failed");
        return -1;
    }
    ssize_t len = strlen(content);
    if (write(fd, content, len) != len) {
        perror("write proc file failed");
        close(fd);
        return -1;
    }
    close(fd);
    return 0;
}

static int child_entry(void *arg) {
    child_args_t *args = (child_args_t *)arg;
    char ch;

    // Закриваємо сторону запису pipe у нащадку
    close(args->pipe_fd[1]);

    // Очікуємо сигнал від батька про завершення мапінгу (блокуюче читання)
    if (read(args->pipe_fd[0], &ch, 1) != 0) {
        fprintf(stderr, "Помилка очікування синхронізації у дочірньому процесі\n");
        return 1;
    }
    close(args->pipe_fd[0]);

    printf("[Child] Перевірка ідентифікаторів усередині User Namespace:\n");
    printf("[Child]   UID = %d (euid = %d)\n", getuid(), geteuid());
    printf("[Child]   GID = %d (egid = %d)\n", getgid(), getegid());

    // Запускаємо тестову shell-оболонку
    char *exec_args[] = { "/bin/sh", "-c", "id && capsh --print 2>/dev/null || true", NULL };
    execvp(exec_args[0], exec_args);

    perror("execvp failed");
    return 1;
}

int main(void) {
    child_args_t args;
    args.parent_uid = getuid();
    args.parent_gid = getgid();

    if (pipe(args.pipe_fd) < 0) {
        perror("pipe creation failed");
        return 1;
    }

    char *child_stack = malloc(STACK_SIZE);
    if (!child_stack) {
        perror("malloc stack failed");
        return 1;
    }

    // Створюємо дочірній процес у новому User Namespace
    pid_t pid = clone(child_entry, child_stack + STACK_SIZE,
                      CLONE_NEWUSER | SIGCHLD, &args);
    if (pid < 0) {
        perror("clone failed");
        free(child_stack);
        return 1;
    }

    printf("[Parent] Створено дочірній процес PID = %d у новому User Namespace\n", pid);

    // 1. Блокуємо setgroups для дочірнього процесу
    char path[256];
    snprintf(path, sizeof(path), "/proc/%d/setgroups", pid);
    if (write_proc_file(path, "deny") < 0) {
        kill(pid, SIGKILL);
        return 1;
    }

    // 2. Налаштовуємо uid_map: 0 -> parent_uid (1 count)
    snprintf(path, sizeof(path), "/proc/%d/uid_map", pid);
    char map_buf[128];
    snprintf(map_buf, sizeof(map_buf), "0 %d 1\n", args.parent_uid);
    if (write_proc_file(path, map_buf) < 0) {
        kill(pid, SIGKILL);
        return 1;
    }

    // 3. Налаштовуємо gid_map: 0 -> parent_gid (1 count)
    snprintf(path, sizeof(path), "/proc/%d/gid_map", pid);
    snprintf(map_buf, sizeof(map_buf), "0 %d 1\n", args.parent_gid);
    if (write_proc_file(path, map_buf) < 0) {
        kill(pid, SIGKILL);
        return 1;
    }

    printf("[Parent] Мапінг UID/GID успішно записано у procfs\n");

    // Сигналізуємо нащадку через закриття pipe
    close(args.pipe_fd[1]);
    close(args.pipe_fd[0]);

    // Очікуємо завершення дочірнього процесу
    int status;
    waitpid(pid, &status, 0);
    free(child_stack);

    printf("[Parent] Дочірній процес завершився з кодом %d\n", WEXITSTATUS(status));
    return 0;
}
