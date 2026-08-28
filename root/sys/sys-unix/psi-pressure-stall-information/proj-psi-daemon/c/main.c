#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <signal.h>
#include <errno.h>

#define PSI_MEMORY_PATH "/proc/pressure/memory"
#define TRIGGER_CMD "some 150000 1000000"
#define BUFFER_SIZE 512

static volatile sig_atomic_t g_running = 1;

static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

static void parse_and_log_psi(const char *buffer) {
    float avg10 = 0.0f, avg60 = 0.0f, avg300 = 0.0f;
    unsigned long long total = 0;

    if (sscanf(buffer, "some avg10=%f avg60=%f avg300=%f total=%llu",
               &avg10, &avg60, &avg300, &total) == 4) {
        printf("[PSI MONITOR C] КРИТИЧНИЙ ТИСК! avg10=%.2f%% avg60=%.2f%% total=%llu us\n",
               avg10, avg60, total);
    } else {
        printf("[PSI MONITOR C] Сирий вивід PSI:\n%s\n", buffer);
    }
}

static void handle_psi_event(int psi_fd) {
    char buf[BUFFER_SIZE];
    
    /* Переміщення вказівника на початок файлу перед читанням */
    if (lseek(psi_fd, 0, SEEK_SET) < 0) {
        perror("Помилка lseek на psi_fd");
        return;
    }

    ssize_t bytes_read = read(psi_fd, buf, sizeof(buf) - 1);
    if (bytes_read > 0) {
        buf[bytes_read] = '\0';
        parse_and_log_psi(buf);
        // Тут здійснюються дії OOM Remediation (наприклад, запис '1' у cgroup.kill)
    } else if (bytes_read < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("Помилка читання даних PSI");
        }
    }
}

int main(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    int psi_fd = open(PSI_MEMORY_PATH, O_RDWR | O_NONBLOCK);
    if (psi_fd < 0) {
        perror("Не вдалося відкрити " PSI_MEMORY_PATH);
        return EXIT_FAILURE;
    }

    /* Запис тригера: some 150ms / 1000ms */
    ssize_t written = write(psi_fd, TRIGGER_CMD, strlen(TRIGGER_CMD));
    if (written < 0) {
        perror("Не вдалося записати тригер PSI");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("Не вдалося створити epoll instance");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = EPOLLPRI;
    ev.data.fd = psi_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, psi_fd, &ev) < 0) {
        perror("Не вдалося додати psi_fd до epoll");
        close(epoll_fd);
        close(psi_fd);
        return EXIT_FAILURE;
    }

    printf("Демон PSI (C) запущений. Очікування на події тиску пам'яті...\n");

    struct epoll_event events[1];
    while (g_running) {
        int nfds = epoll_wait(epoll_fd, events, 1, 1000);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("Помилка в epoll_wait");
            break;
        }

        if (nfds > 0 && (events[0].events & EPOLLPRI)) {
            handle_psi_event(psi_fd);
        }
    }

    printf("Завершення роботи демона PSI (C)...\n");
    close(epoll_fd);
    close(psi_fd);
    return EXIT_SUCCESS;
}
