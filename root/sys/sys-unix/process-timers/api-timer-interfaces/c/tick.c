/* cc -o tick tick.c   (для POSIX-таймерів у glibc до 2.34 знадобився б ще -lrt) */
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>
#include <sys/timerfd.h>

int main(void)
{
    int fd = timerfd_create(CLOCK_MONOTONIC, TFD_CLOEXEC);
    if (fd < 0) { perror("timerfd_create"); return 1; }

    struct itimerspec its = {
        .it_value    = { .tv_sec = 1, .tv_nsec = 0 },          /* перший строк */
        .it_interval = { .tv_sec = 0, .tv_nsec = 250000000 },  /* далі щочверть секунди */
    };
    if (timerfd_settime(fd, 0, &its, NULL) < 0) { perror("timerfd_settime"); return 1; }

    for (int i = 0; i < 8; i++) {
        uint64_t ticks;
        if (read(fd, &ticks, sizeof ticks) != (ssize_t)sizeof ticks) {
            perror("read");                       /* тут же ловиться ECANCELED */
            return 1;
        }
        printf("спрацювань від минулого читання: %llu\n", (unsigned long long)ticks);
    }
    close(fd);
    return 0;
}
