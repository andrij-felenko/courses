#include <time.h>

static int arm_wallwatch(int fd)
{
    /* Абсолютний строк у далекому майбутньому: чекаємо не спрацювання,
       а скасування. Прапорець CANCEL_ON_SET чинний лише разом з ABSTIME
       і лише на CLOCK_REALTIME або CLOCK_REALTIME_ALARM. */
    struct itimerspec its = {
        .it_value = { .tv_sec = time(NULL) + 100LL * 365 * 24 * 3600 }
    };
    return timerfd_settime(fd, TFD_TIMER_ABSTIME | TFD_TIMER_CANCEL_ON_SET,
                           &its, NULL);
}

static int make_wallwatch(void)
{
    int fd = timerfd_create(CLOCK_REALTIME, TFD_CLOEXEC | TFD_NONBLOCK);
    if (fd < 0)
        return -1;
    if (arm_wallwatch(fd) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}
