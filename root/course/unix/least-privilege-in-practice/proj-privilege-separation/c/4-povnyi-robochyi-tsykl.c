#define _GNU_SOURCE
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <unistd.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#define TARGET_UID 65534 /* nobody */
#define TARGET_GID 65534 /* nogroup */
#define LISTEN_PORT 8080

/* Оголошення допоміжних функцій */
int send_fd(int socket_fd, int fd_to_send);
int recv_fd(int socket_fd);
int install_worker_seccomp_filter(void);

/* Робочий цикл непривілейованого воркера */
void run_worker(int channel_fd) {
    /* 1. Очищуємо додаткові групи суперкористувача */
    if (setgroups(0, NULL) != 0) {
        perror("worker: setgroups");
        exit(EXIT_FAILURE);
    }

    /* 2. Безповоротно скидаємо GID та UID */
    if (setresgid(TARGET_GID, TARGET_GID, TARGET_GID) != 0) {
        perror("worker: setresgid");
        exit(EXIT_FAILURE);
    }
    if (setresuid(TARGET_UID, TARGET_UID, TARGET_UID) != 0) {
        perror("worker: setresuid");
        exit(EXIT_FAILURE);
    }

    /* 3. Вмикаємо пісочницю Seccomp-BPF */
    if (install_worker_seccomp_filter() != 0) {
        fprintf(stderr, "worker: не вдалося активувати seccomp\n");
        exit(EXIT_FAILURE);
    }

    printf("[Worker PID %d] Успішно скинув права до UID %d і увійшов у пісочницю\n",
           getpid(), getuid());

    /* 4. Головний цикл обробки підключень */
    while (1) {
        int client_fd = recv_fd(channel_fd);
        if (client_fd < 0) {
            break; /* Майстер закрив сокет зв'язку або завершив роботу */
        }

        const char response[] = "HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!";
        write(client_fd, response, sizeof(response) - 1);
        close(client_fd);
    }
    exit(EXIT_SUCCESS);
}

int main(void) {
    int channel[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, channel) != 0) {
        perror("socketpair");
        return EXIT_FAILURE;
    }

    pid_t worker_pid = fork();
    if (worker_pid < 0) {
        perror("fork");
        return EXIT_FAILURE;
    }

    if (worker_pid == 0) {
        /* Дочірній процес: закриваємо дескриптор сторони майстра */
        close(channel[0]);
        run_worker(channel[1]);
    }

    /* Батьківський процес (Master): закриваємо дескриптор сторони воркера */
    close(channel[1]);
    int master_chan = channel[0];

    /* Відкриваємо мережевий сокет */
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        perror("master: socket");
        return EXIT_FAILURE;
    }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(LISTEN_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        perror("master: bind");
        return EXIT_FAILURE;
    }

    if (listen(listen_fd, 128) != 0) {
        perror("master: listen");
        return EXIT_FAILURE;
    }

    printf("[Master PID %d] Слухає порт %d, передає клієнтів воркеру PID %d\n",
           getpid(), LISTEN_PORT, worker_pid);

    /* Майстер приймає з'єднання і делегує дескриптор воркеру */
    for (int i = 0; i < 5; ++i) {
        int client_fd = accept(listen_fd, NULL, NULL);
        if (client_fd < 0) {
            perror("master: accept");
            continue;
        }

        if (send_fd(master_chan, client_fd) != 0) {
            fprintf(stderr, "master: помилка передачі дескриптора\n");
        }
        /* Закриваємо власну копію дескриптора в майстрі */
        close(client_fd);
    }

    close(listen_fd);
    close(master_chan);
    waitpid(worker_pid, NULL, 0);
    printf("[Master] Роботу завершено штатно.\n");
    return EXIT_SUCCESS;
}
