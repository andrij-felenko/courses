#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sched.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/mount.h>
#include <fcntl.h>
#include <signal.h>

// Виклик зовнішніх setuid-утиліт newuidmap / newgidmap
static int execute_map_helper(const char *helper, pid_t pid, const char *inside_id, const char *outside_id, const char *count) {
    pid_t map_pid = fork();
    if (map_pid == -1) {
        perror("fork helper failed");
        return -1;
    }

    if (map_pid == 0) {
        char pid_str[16];
        snprintf(pid_str, sizeof(pid_str), "%d", pid);
        
        // Передаємо аргументи: helper PID inside_id outside_id count
        execlp(helper, helper, pid_str, inside_id, outside_id, count, NULL);
        perror("execlp helper failed");
        _exit(EXIT_FAILURE);
    }

    int status = 0;
    if (waitpid(map_pid, &status, 0) == -1) {
        perror("waitpid helper failed");
        return -1;
    }

    return (WIFEXITED(status) && WEXITSTATUS(status) == 0) ? 0 : -1;
}

int main(void) {
    printf("[Init] Starting Rootless Container Setup Demo...\n");

    // Створюємо Pipe для двосторонньої синхронізації
    int sync_pipe[2];
    if (pipe(sync_pipe) == -1) {
        perror("pipe creation failed");
        return EXIT_FAILURE;
    }

    uid_t parent_uid = getuid();
    gid_t parent_gid = getgid();

    printf("[Parent] Host User UID: %d, GID: %d\n", parent_uid, parent_gid);

    pid_t child_pid = fork();
    if (child_pid == -1) {
        perror("fork child failed");
        return EXIT_FAILURE;
    }

    if (child_pid == 0) {
        // --- Дочірній процес (Контейнер) ---
        close(sync_pipe[0]); // Закриваємо читальний кінець у дитині

        printf("[Child] Creating User Namespace (CLONE_NEWUSER) & Mount Namespace (CLONE_NEWNS)...\n");
        if (unshare(CLONE_NEWUSER | CLONE_NEWNS) == -1) {
            perror("unshare failed");
            _exit(EXIT_FAILURE);
        }

        // Повідомляємо батька, що namespace створено
        char signal_byte = 'R';
        if (write(sync_pipe[1], &signal_byte, 1) != 1) {
            perror("write sync signal failed");
            _exit(EXIT_FAILURE);
        }

        // Блокуємося і чекаємо, поки батьківський процес виконає newuidmap
        if (read(sync_pipe[1], &signal_byte, 1) != 1) {
            perror("read finish sync failed");
            _exit(EXIT_FAILURE);
        }
        close(sync_pipe[1]);

        // Перевіряємо отримані ідентифікатори
        uid_t inner_uid = getuid();
        gid_t inner_gid = getgid();
        printf("[Child] Inner Container Credentials: UID=%d, GID=%d\n", inner_uid, inner_gid);

        if (inner_uid != 0) {
            fprintf(stderr, "[Child] Error: Failed to escalate to Root inside namespace!\n");
            _exit(EXIT_FAILURE);
        }

        printf("[Child] Successfully gained Root (UID 0) inside container!\n");

        // Звертаємо увагу: оскільки дитина має CAP_SYS_ADMIN у своєму Mount Namespace,
        // вона може виконувати непривілейоване монтування tmpfs
        printf("[Child] Mounting isolated tmpfs filesystem on /tmp...\n");
        if (mount("tmpfs", "/tmp", "tmpfs", 0, "size=16M") == -1) {
            perror("mount tmpfs failed");
            // Продовжуємо виконання, навіть якщо монтування не вдалося
        } else {
            printf("[Child] Successfully mounted private tmpfs on /tmp!\n");
        }

        // Замінюємо процес на bash
        char *exec_args[] = { "/bin/bash", NULL };
        printf("[Child] Executing interactive shell...\n\n");
        execvp(exec_args[0], exec_args);

        perror("execvp failed");
        _exit(EXIT_FAILURE);
    }

    // --- Батьківський процес (Оркестратор) ---
    close(sync_pipe[1]); // Закриваємо записувальний кінець у батька

    // Чекаємо готовності дочірнього процесу
    char sync_buf = 0;
    if (read(sync_pipe[0], &sync_buf, 1) != 1) {
        perror("read initial sync failed");
        kill(child_pid, SIGKILL);
        return EXIT_FAILURE;
    }

    printf("[Parent] Child PID %d created namespaces. Executing newuidmap & newgidmap...\n", child_pid);

    char uid_str[16], gid_str[16];
    snprintf(uid_str, sizeof(uid_str), "%d", parent_uid);
    snprintf(gid_str, sizeof(gid_str), "%d", parent_gid);

    // Запускаємо newuidmap: 0 -> parent_uid (1 count)
    if (execute_map_helper("newuidmap", child_pid, "0", uid_str, "1") != 0) {
        fprintf(stderr, "[Parent] Fatal: newuidmap failed for PID %d\n", child_pid);
        kill(child_pid, SIGKILL);
        return EXIT_FAILURE;
    }

    // Запускаємо newgidmap: 0 -> parent_gid (1 count)
    if (execute_map_helper("newgidmap", child_pid, "0", gid_str, "1") != 0) {
        fprintf(stderr, "[Parent] Fatal: newgidmap failed for PID %d\n", child_pid);
        kill(child_pid, SIGKILL);
        return EXIT_FAILURE;
    }

    printf("[Parent] Mappings successfully configured. Unblocking child...\n");

    // Розблоковуємо дочірній процес
    sync_buf = 'G';
    if (write(sync_pipe[0], &sync_buf, 1) != 1) {
        perror("write unblock signal failed");
        kill(child_pid, SIGKILL);
        return EXIT_FAILURE;
    }
    close(sync_pipe[0]);

    // Чекаємо завершення дочірнього процесу
    int child_status = 0;
    waitpid(child_pid, &child_status, 0);
    printf("[Parent] Child container process exited with status %d.\n", child_status);

    return EXIT_SUCCESS;
}
