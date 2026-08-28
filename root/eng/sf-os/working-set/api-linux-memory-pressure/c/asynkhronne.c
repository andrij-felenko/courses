#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <errno.h>

/*
 * Реєстрація та очікування сповіщення про перевантаження пам'яті через PSI.
 */
int main(void) {
    const char *psi_path = "/proc/pressure/memory";
    int psi_fd = open(psi_path, O_RDWR | O_NONBLOCK);
    if (psi_fd < 0) {
        perror("Не вдалося відкрити /proc/pressure/memory");
        return EXIT_FAILURE;
    }

    /* Налаштування тригера: 100 мс простою у вікні 1 с */
    const char *trigger_spec = "some 100000 1000000";
    if (write(psi_fd, trigger_spec, strlen(trigger_spec)) < 0) {
        perror("Не вдалося записати тригер у PSI");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("epoll_create1 failed");
        close(psi_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLPRI; /* PSI генерує подію виняткового стану EPOLLPRI */
    ev.data.fd = psi_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, psi_fd, &ev) < 0) {
        perror("epoll_ctl failed");
        close(psi_fd);
        close(epoll_fd);
        return EXIT_FAILURE;
    }

    printf("Очікування подій Memory Pressure через PSI (поріг 10%% за 1 с)...\n");

    struct epoll_event events[1];
    int n = epoll_wait(epoll_fd, events, 1, 10000); /* Таймаут 10 секунд */

    if (n < 0) {
        perror("epoll_wait failed");
    } else if (n == 0) {
        printf("За 10 секунд поріг тиску пам'яті не перевищено (система стабільна).\n");
    } else {
        if (events[0].events & EPOLLPRI) {
            printf("УВАГА: Зафіксовано високий рівень тиску на пам'ять! Потрібне скидання кешів.\n");
        }
    }

    close(psi_fd);
    close(epoll_fd);
    return EXIT_SUCCESS;
}
