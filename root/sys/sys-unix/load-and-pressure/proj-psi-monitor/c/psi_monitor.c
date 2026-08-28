/* psi_monitor.c — Демон спостереження за тиском пам'яті на C (POSIX) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/epoll.h>
#include <sys/types.h>

#define MAX_EVENTS 8
#define BUFFER_SIZE 256

/* Налаштування тригера: 150 мс затримки в 1-секундному вікні */
static const char *TRIGGER_SPEC = "some 150000 1000000";
static const char *PRESSURE_PATH = "/proc/pressure/memory";

static int setup_psi_trigger(const char *path, const char *spec) {
    int fd = open(path, O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        perror("Помилка відкриття вузла PSI");
        return -1;
    }

    ssize_t written = write(fd, spec, strlen(spec));
    if (written < 0) {
        perror("Помилка реєстрації тригера PSI");
        close(fd);
        return -1;
    }

    return fd;
}

static void read_current_pressure(const char *path) {
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return;

    char buf[BUFFER_SIZE];
    ssize_t bytes = read(fd, buf, sizeof(buf) - 1);
    if (bytes > 0) {
        buf[bytes] = '\0';
        printf("--- Поточні метрики тиску ---\n%s-----------------------------\n", buf);
    }
    close(fd);
}

int main(void) {
    printf("[PSI Monitor] Запуск демона спостереження...\n");

    int psi_fd = setup_psi_trigger(PRESSURE_PATH, TRIGGER_SPEC);
    if (psi_fd < 0) {
        fprintf(stderr, "Критична помилка: не вдалося налаштувати PSI тригер.\n");
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (epoll_fd < 0) {
        perror("Помилка створення epoll");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));
    ev.events = EPOLLPRI; // Враховуємо лише події підвищеного пріоритету (PSI trigger)
    ev.data.fd = psi_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, psi_fd, &ev) < 0) {
        perror("Помилка додавання fd до epoll");
        close(epoll_fd);
        close(psi_fd);
        return EXIT_FAILURE;
    }

    printf("[PSI Monitor] Тригер успішно встановлено: \"%s\" для %s\n", TRIGGER_SPEC, PRESSURE_PATH);
    printf("[PSI Monitor] Очікування подій тиску...\n");

    struct epoll_event events[MAX_EVENTS];
    int running = 1;
    int alert_count = 0;

    while (running) {
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("Помилка epoll_wait");
            break;
        }

        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == psi_fd && (events[i].events & EPOLLPRI)) {
                alert_count++;
                printf("\n⚠️  [СПЛЕКСТ ТИСКУ #%d] Тригер PSI спрацював! Пам'ять зазнає затримок!\n", alert_count);
                read_current_pressure(PRESSURE_PATH);
            }
        }
    }

    close(epoll_fd);
    close(psi_fd);
    return EXIT_SUCCESS;
}
