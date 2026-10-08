#include <sys/wait.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

void master_loop(int num_workers, int listen_fd) {
    for (int i = 0; i < num_workers; i++) {
        int sv[2];
        socketpair(AF_UNIX, SOCK_STREAM, 0, sv);

        pid_t pid = fork();
        if (pid == 0) {
            // Дитячий процес (Worker)
            close(sv[0]);
            drop_privileges("nobody", "/var/empty");
            // Обробка мережевого трафіку з listen_fd
            close(sv[1]);
            _exit(0);
        } else {
            // Батьківський процес (Master)
            close(sv[1]);
        }
    }

    // Цикл моніторингу за станом воркерів
    while (1) {
        int status;
        pid_t dead_pid = wait(&status);
        if (dead_pid > 0) {
            printf("Worker PID %d died. Respawning new worker...\n", dead_pid);
            // Перезапуск нового воркера
        }
    }
}
