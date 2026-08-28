#include <errno.h>
#include <unistd.h>
#include <sys/timerfd.h>

/* Періодичний таймер, що рахує сон і, якщо дозволено, будить машину. */
static int make_alarm(int64_t period_ns)
{
    int fd = timerfd_create(CLOCK_BOOTTIME_ALARM, TFD_CLOEXEC | TFD_NONBLOCK);
    if (fd < 0 && errno == EPERM)          /* немає CAP_WAKE_ALARM */
        fd = timerfd_create(CLOCK_BOOTTIME, TFD_CLOEXEC | TFD_NONBLOCK);
    if (fd < 0)
        return -1;

    struct timespec p = { .tv_sec  = period_ns / 1000000000LL,
                          .tv_nsec = period_ns % 1000000000LL };
    struct itimerspec its = { .it_value = p, .it_interval = p };
    if (timerfd_settime(fd, 0, &its, NULL) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}
