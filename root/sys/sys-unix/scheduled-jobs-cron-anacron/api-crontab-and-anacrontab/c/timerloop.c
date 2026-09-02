#define _GNU_SOURCE

#include "timerloop.h"

#include <errno.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/prctl.h>
#include <sys/timerfd.h>
#include <unistd.h>

#define TIMER_LOOP_MAX 8
#define EPOLL_BATCH    8

typedef struct {
    int fd;
    bool own_fd;              /* таймер створили ми — нам і закривати */
    timer_handler_t on_timer; /* один із двох обробників, другий NULL */
    fd_handler_t on_fd;
    void *user_data;
} source_t;

struct timer_loop {
    int epoll_fd;
    source_t sources[TIMER_LOOP_MAX];
    size_t count;
    volatile sig_atomic_t running;
};

timer_loop_t *timer_loop_create(void)
{
    timer_loop_t *loop = calloc(1, sizeof(*loop));
    if (loop == NULL) {
        return NULL;
    }
    loop->epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (loop->epoll_fd < 0) {
        perror("epoll_create1");
        free(loop);
        return NULL;
    }
    return loop;
}

void timer_loop_destroy(timer_loop_t *loop)
{
    if (loop == NULL) {
        return;
    }
    for (size_t i = 0; i < loop->count; i++) {
        if (loop->sources[i].own_fd) {
            close(loop->sources[i].fd);
        }
    }
    close(loop->epoll_fd);
    free(loop);
}

static int register_source(timer_loop_t *loop, const source_t *src)
{
    struct epoll_event ev;
    memset(&ev, 0, sizeof ev);
    ev.events = EPOLLIN;
    ev.data.u32 = (uint32_t)loop->count;
    if (epoll_ctl(loop->epoll_fd, EPOLL_CTL_ADD, src->fd, &ev) < 0) {
        perror("epoll_ctl");
        return -1;
    }
    loop->sources[loop->count++] = *src;
    return 0;
}

int timer_loop_add_timer(timer_loop_t *loop, int clockid,
                         const struct itimerspec *spec, int flags,
                         timer_handler_t handler, void *user_data)
{
    if (loop->count == TIMER_LOOP_MAX) {
        fprintf(stderr, "timer_loop: більше за %d джерел не тримаємо\n", TIMER_LOOP_MAX);
        return -1;
    }

    int tfd = timerfd_create(clockid, TFD_NONBLOCK | TFD_CLOEXEC);
    if (tfd < 0) {
        perror("timerfd_create");
        return -1;
    }
    if (timerfd_settime(tfd, flags, spec, NULL) < 0) {
        perror("timerfd_settime");
        close(tfd);
        return -1;
    }

    source_t src = {tfd, true, handler, NULL, user_data};
    if (register_source(loop, &src) != 0) {
        close(tfd);
        return -1;
    }
    return 0;
}

int timer_loop_add_fd(timer_loop_t *loop, int fd, fd_handler_t handler,
                      void *user_data)
{
    if (loop->count == TIMER_LOOP_MAX) {
        fprintf(stderr, "timer_loop: більше за %d джерел не тримаємо\n", TIMER_LOOP_MAX);
        return -1;
    }
    if (fd < 0) {
        errno = EBADF;
        return -1;
    }
    source_t src = {fd, false, NULL, handler, user_data};
    return register_source(loop, &src);
}

void timer_loop_stop(timer_loop_t *loop)
{
    if (loop != NULL) {
        loop->running = 0;
    }
}

int timer_loop_run(timer_loop_t *loop)
{
    struct epoll_event events[EPOLL_BATCH];

    loop->running = 1;
    while (loop->running) {
        int nfds = epoll_wait(loop->epoll_fd, events, EPOLL_BATCH, -1);
        if (nfds < 0) {
            if (errno == EINTR) {
                continue; /* сигнал: цикл сам перевірить прапорець running */
            }
            perror("epoll_wait");
            return -1;
        }

        for (int i = 0; i < nfds; i++) {
            uint32_t index = events[i].data.u32;
            if (index >= loop->count) {
                continue;
            }
            source_t *src = &loop->sources[index];

            if (src->on_fd != NULL) {
                src->on_fd(src->fd, src->user_data);
                continue;
            }

            uint64_t expirations = 0;
            ssize_t n = read(src->fd, &expirations, sizeof expirations);
            if (n == (ssize_t)sizeof expirations) {
                /* У лічильнику — скільки спрацьовувань накопичилося з минулого
                   читання; читання скидає його в нуль. */
                src->on_timer(expirations, src->user_data);
            } else if (n < 0 && errno == ECANCELED) {
                /* TFD_TIMER_CANCEL_ON_SET: годинник стрибнув. Будимо обробник
                   із нулем, щоб демон перерахував розклад. */
                src->on_timer(0, src->user_data);
            } else if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
                perror("read timerfd");
                return -1;
            }
        }
    }
    return 0;
}

int timer_loop_set_slack_ns(unsigned long slack_ns)
{
    if (prctl(PR_SET_TIMERSLACK, slack_ns, 0UL, 0UL, 0UL) != 0) {
        perror("prctl(PR_SET_TIMERSLACK)");
        return -1;
    }
    return 0;
}

long timer_loop_read_slack_ns(void)
{
    errno = 0;
    /* PR_GET_TIMERSLACK віддає значення кодом повернення, тож -1 буває і
       правильним числом — розрізняємо за errno. */
    int slack = prctl(PR_GET_TIMERSLACK, 0UL, 0UL, 0UL, 0UL);
    if (slack < 0 && errno != 0) {
        perror("prctl(PR_GET_TIMERSLACK)");
        return -1;
    }
    return (long)slack;
}
