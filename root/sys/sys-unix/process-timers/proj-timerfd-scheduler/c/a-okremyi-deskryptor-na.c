#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>

enum policy { SKIP, CATCH_UP };

typedef struct {
    const char *name;
    int64_t     period_ns;
    enum policy policy;
    void      (*run)(void);

    int             fd;
    struct timespec origin;        /* спільний нуль фази */
    uint64_t        fired;         /* скільки спрацювань уже зараховано */
    uint64_t        skipped;
    int64_t         worst_late_ns;
} task;

static struct timespec ts_add_ns(struct timespec t, int64_t ns)
{
    int64_t x = t.tv_nsec + ns;
    t.tv_sec  += x / 1000000000LL;
    t.tv_nsec  = x % 1000000000LL;
    if (t.tv_nsec < 0) { t.tv_nsec += 1000000000LL; t.tv_sec -= 1; }
    return t;
}

static int64_t ts_sub_ns(struct timespec a, struct timespec b)   /* a − b */
{
    return (int64_t)(a.tv_sec - b.tv_sec) * 1000000000LL + (a.tv_nsec - b.tv_nsec);
}

static int task_arm(task *t, struct timespec origin, int epfd)
{
    t->fd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    if (t->fd < 0) return -1;
    t->origin = origin;

    struct itimerspec its = {
        .it_value    = ts_add_ns(origin, t->period_ns),        /* АБСОЛЮТНИЙ перший строк */
        .it_interval = { .tv_sec  = t->period_ns / 1000000000LL,
                         .tv_nsec = t->period_ns % 1000000000LL },
    };
    if (timerfd_settime(t->fd, TFD_TIMER_ABSTIME, &its, NULL) < 0) return -1;

    struct epoll_event ev = { .events = EPOLLIN, .data.ptr = t };
    return epoll_ctl(epfd, EPOLL_CTL_ADD, t->fd, &ev);
}
