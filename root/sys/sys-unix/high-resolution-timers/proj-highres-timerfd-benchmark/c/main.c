#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>
#include <sys/timerfd.h>
#include <sys/epoll.h>
#include <errno.h>

#define ITERATIONS 10000
#define PERIOD_NS  500000LL /* 500 мікросекунд */

static inline int64_t timespec_to_ns(const struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000000LL + ts->tv_nsec;
}

int main(void) {
    /* 1. Створюємо таймерний дескриптор hrtimer для монотонного годинника */
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC);
    if (tfd == -1) {
        perror("timerfd_create");
        return EXIT_FAILURE;
    }

    /* 2. Задаємо період 500 мікросекунд і АБСОЛЮТНИЙ момент першого тику.
          Абсолютна позначка (TFD_TIMER_ABSTIME) потрібна, щоб ядро й програма
          відлічували сітку від одного й того самого нуля: якби нулем був час
          перед timerfd_settime(), у кожен вимір увійшла б ще й тривалість
          самого системного виклику — а це той самий порядок, що й джиттер. */
    struct timespec start_ts;
    clock_gettime(CLOCK_MONOTONIC, &start_ts);
    int64_t first_ns = timespec_to_ns(&start_ts) + 10000000LL; /* старт через 10 мс */

    struct itimerspec new_val = {0};
    new_val.it_interval.tv_sec = 0;
    new_val.it_interval.tv_nsec = PERIOD_NS;
    new_val.it_value.tv_sec = (time_t)(first_ns / 1000000000LL);
    new_val.it_value.tv_nsec = (long)(first_ns % 1000000000LL);

    if (timerfd_settime(tfd, TFD_TIMER_ABSTIME, &new_val, NULL) == -1) {
        perror("timerfd_settime");
        close(tfd);
        return EXIT_FAILURE;
    }

    /* 3. Створюємо epoll дескриптор для очікування подій */
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) {
        perror("epoll_create1");
        close(tfd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = tfd;
    if (epoll_ctl(epfd, EPOLL_CTL_ADD, tfd, &ev) == -1) {
        perror("epoll_ctl");
        close(epfd);
        close(tfd);
        return EXIT_FAILURE;
    }

    int64_t expected_target = first_ns;
    int64_t min_jitter = 1000000000LL;
    int64_t max_jitter = -1000000000LL;
    int64_t total_jitter = 0;

    printf("Розпочинаємо вимірювання 10000 тиків з періодом %lld нс...\n", PERIOD_NS);

    for (int i = 0; i < ITERATIONS; i++) {
        struct epoll_event events[1];
        int nfds = epoll_wait(epfd, events, 1, -1);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        uint64_t expirations = 0;
        ssize_t s = read(tfd, &expirations, sizeof(expirations));
        if (s != sizeof(expirations)) {
            perror("read");
            break;
        }

        struct timespec now_ts;
        clock_gettime(CLOCK_MONOTONIC, &now_ts);
        int64_t now_ns = timespec_to_ns(&now_ts);

        int64_t jitter = now_ns - expected_target;
        if (jitter < min_jitter) min_jitter = jitter;
        if (jitter > max_jitter) max_jitter = jitter;
        total_jitter += (jitter < 0 ? -jitter : jitter);

        /* Коригуємо плановий дедлайн з урахуванням можливо пропущених ітерацій */
        expected_target += (int64_t)expirations * PERIOD_NS;
    }

    printf("\n=== Результати вимірювання джиттера timerfd (10000 тиків) ===\n");
    printf("Мінімальний джиттер : %6.3f мкс\n", (double)min_jitter / 1000.0);
    printf("Максимальний джиттер: %6.3f мкс\n", (double)max_jitter / 1000.0);
    printf("Середнє відхилення  : %6.3f мкс\n", (double)total_jitter / (ITERATIONS * 1000.0));

    close(epfd);
    close(tfd);
    return EXIT_SUCCESS;
}
