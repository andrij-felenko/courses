#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <sys/signalfd.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <pthread.h>
#include <time.h>

#define MAX_EVENTS 32
#define SHUTDOWN_TIMEOUT_SEC 5
#define WORKER_COUNT 4

typedef struct {
    int id;
    pthread_t thread;
    bool running;
    pthread_mutex_t lock;
    pthread_cond_t cond;
    int active_jobs;
    bool stop_requested;
} worker_t;

typedef struct {
    int epoll_fd;
    int signal_fd;
    int listen_fd;
    bool is_draining;
    worker_t workers[WORKER_COUNT];
    pthread_mutex_t state_lock;
} server_coordinator_t;

static void* worker_loop(void* arg) {
    worker_t* w = (worker_t*)arg;
    while (true) {
        pthread_mutex_lock(&w->lock);
        while (w->active_jobs == 0 && !w->stop_requested) {
            pthread_cond_wait(&w->cond, &w->lock);
        }

        if (w->stop_requested && w->active_jobs == 0) {
            pthread_mutex_unlock(&w->lock);
            break;
        }

        /* Імітація обробки активного запиту */
        w->active_jobs--;
        pthread_mutex_unlock(&w->lock);

        usleep(100000); /* 100 мс корисної роботи */
    }
    return NULL;
}

static void coordinator_init(server_coordinator_t* coord) {
    memset(coord, 0, sizeof(*coord));
    pthread_mutex_init(&coord->state_lock, NULL);

    /* 1. Блокуємо сигнали для використання signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);
    pthread_sigmask(SIG_BLOCK, &mask, NULL);

    coord->signal_fd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (coord->signal_fd < 0) {
        perror("signalfd failed");
        exit(EXIT_FAILURE);
    }

    /* 2. Створюємо epoll */
    coord->epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (coord->epoll_fd < 0) {
        perror("epoll_create1 failed");
        exit(EXIT_FAILURE);
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = coord->signal_fd;
    epoll_ctl(coord->epoll_fd, EPOLL_CTL_ADD, coord->signal_fd, &ev);

    /* 3. Ініціалізуємо воркерів */
    for (int i = 0; i < WORKER_COUNT; ++i) {
        coord->workers[i].id = i;
        coord->workers[i].running = true;
        coord->workers[i].active_jobs = 0;
        coord->workers[i].stop_requested = false;
        pthread_mutex_init(&coord->workers[i].lock, NULL);
        pthread_cond_init(&coord->workers[i].cond, NULL);
        pthread_create(&coord->workers[i].thread, NULL, worker_loop, &coord->workers[i]);
    }
}

static void coordinator_drain_and_shutdown(server_coordinator_t* coord) {
    printf("[Coordinator] Отримано сигнал зупинки. Фаза 1: Unreadiness та закриття слухача.\n");
    
    pthread_mutex_lock(&coord->state_lock);
    coord->is_draining = true;
    if (coord->listen_fd >= 0) {
        epoll_ctl(coord->epoll_fd, EPOLL_CTL_DEL, coord->listen_fd, NULL);
        close(coord->listen_fd);
        coord->listen_fd = -1;
    }
    pthread_mutex_unlock(&coord->state_lock);

    printf("[Coordinator] Фаза 2: Зупинка прийому задач воркерами та очікування завершення.\n");
    for (int i = 0; i < WORKER_COUNT; ++i) {
        pthread_mutex_lock(&coord->workers[i].lock);
        coord->workers[i].stop_requested = true;
        pthread_cond_broadcast(&coord->workers[i].cond);
        pthread_mutex_unlock(&coord->workers[i].lock);
    }

    /* Сторожовий таймер очікування воркерів */
    struct timespec start_time, current_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    for (int i = 0; i < WORKER_COUNT; ++i) {
        void* res;
        pthread_join(coord->workers[i].thread, &res);
        pthread_mutex_destroy(&coord->workers[i].lock);
        pthread_cond_destroy(&coord->workers[i].cond);
        printf("[Coordinator] Воркер %d успішно зупинився.\n", i);
    }

    printf("[Coordinator] Фаза 3: Змивання буферів логів і закриття ресурсів.\n");
    fflush(stdout);
    fflush(stderr);

    if (coord->signal_fd >= 0) close(coord->signal_fd);
    if (coord->epoll_fd >= 0) close(coord->epoll_fd);
    pthread_mutex_destroy(&coord->state_lock);

    printf("[Coordinator] Штатне вимкнення завершено успішно (exit code 0).\n");
}

int main(void) {
    server_coordinator_t coord;
    coordinator_init(&coord);

    printf("[Server] Сервер запущено. Очікування подій або сигналів (Ctrl+C)...\n");

    /* Додаємо тестове навантаження */
    for (int i = 0; i < WORKER_COUNT; ++i) {
        pthread_mutex_lock(&coord.workers[i].lock);
        coord.workers[i].active_jobs = 3;
        pthread_cond_signal(&coord.workers[i].cond);
        pthread_mutex_unlock(&coord.workers[i].lock);
    }

    struct epoll_event events[MAX_EVENTS];
    bool running = true;

    while (running) {
        int nfds = epoll_wait(coord.epoll_fd, events, MAX_EVENTS, -1);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait failed");
            break;
        }

        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == coord.signal_fd) {
                struct signalfd_siginfo fdsi;
                ssize_t s = read(coord.signal_fd, &fdsi, sizeof(fdsi));
                if (s == sizeof(fdsi)) {
                    printf("\n[Server] Спіймано сигнал %d (%s).\n", 
                           fdsi.ssi_signo, strsignal(fdsi.ssi_signo));
                    running = false;
                    break;
                }
            }
        }
    }

    coordinator_drain_and_shutdown(&coord);
    return 0;
}
