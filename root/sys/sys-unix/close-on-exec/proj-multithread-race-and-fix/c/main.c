#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <dirent.h>
#include <string.h>
#include <sys/wait.h>
#include <stdatomic.h>
#include <stdbool.h>

static atomic_bool g_running = true;
static atomic_int g_leaks_detected = 0;
static bool g_use_atomic_cloexec = false;

/* Підрахунок успадкованих дескрипторів у дочірньому процесі */
static void inspect_child_fds(void) {
    DIR *dir = opendir("/proc/self/fd");
    if (!dir) {
        _exit(1);
    }

    int dir_fd = dirfd(dir);
    struct dirent *entry;
    int leaked_count = 0;

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.')
            continue;

        int fd = atoi(entry->d_name);
        /* Дескриптори 0, 1, 2 — стандартні потоки, dir_fd — дескриптор opendir */
        if (fd > 2 && fd != dir_fd) {
            leaked_count++;
        }
    }

    closedir(dir);
    if (leaked_count > 0) {
        _exit(42); /* Спеціальний код виходу, що сигналізує батькові про витік */
    }
    _exit(0);
}

/* Потік-генератор: постійно відкриває та закриває тимчасові дескриптори */
static void *worker_loop(void *arg) {
    (void)arg;
    while (atomic_load(&g_running)) {
        int fd;
        if (g_use_atomic_cloexec) {
            /* Атомарне створення: прапорець встановлюється ядром одразу */
            fd = open("/dev/null", O_RDONLY | O_CLOEXEC);
        } else {
            /* Неатомарне відкриття: утворюється вікно гонитви перед fcntl */
            fd = open("/dev/null", O_RDONLY);
            if (fd >= 0) {
                int flags = fcntl(fd, F_GETFD);
                if (flags != -1) {
                    fcntl(fd, F_SETFD, flags | FD_CLOEXEC);
                }
            }
        }

        if (fd >= 0) {
            usleep(50); /* Коротка затримка, що імітує обробку даних */
            close(fd);
        }
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc > 1 && strcmp(argv[1], "--atomic") == 0) {
        g_use_atomic_cloexec = true;
        printf("=== Режим тестування: Атомарний O_CLOEXEC (гонитва усунена) ===\n");
    } else {
        printf("=== Режим тестування: Неатомарний open() + fcntl() (стан гонитви) ===\n");
    }

    pthread_t worker;
    if (pthread_create(&worker, NULL, worker_loop, NULL) != 0) {
        perror("pthread_create");
        return 1;
    }

    const int iterations = 500;
    for (int i = 0; i < iterations; i++) {
        pid_t pid = fork();
        if (pid < 0) {
            perror("fork");
            break;
        }

        if (pid == 0) {
            inspect_child_fds();
        }

        int status;
        waitpid(pid, &status, 0);
        if (WIFEXITED(status) && WEXITSTATUS(status) == 42) {
            atomic_fetch_add(&g_leaks_detected, 1);
        }
        usleep(150);
    }

    atomic_store(&g_running, false);
    pthread_join(worker, NULL);

    printf("Підсумок після %d ітерацій fork():\n", iterations);
    printf("  Зафіксовано витоків дескрипторів: %d\n", atomic_load(&g_leaks_detected));

    return 0;
}
