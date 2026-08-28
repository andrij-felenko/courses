#include <signal.h>
#include <time.h>

int timer_create(clockid_t clockid, struct sigevent *restrict sevp,
                 timer_t *restrict timerid);
int timer_settime(timer_t timerid, int flags,
                  const struct itimerspec *restrict new_value,
                        struct itimerspec *restrict old_value);
int timer_gettime(timer_t timerid, struct itimerspec *curr_value);
int timer_getoverrun(timer_t timerid);
int timer_delete(timer_t timerid);

struct itimerspec {
    struct timespec it_interval;  /* період */
    struct timespec it_value;     /* до першого спрацювання */
};

struct timespec {
    time_t tv_sec;                /* секунди */
    long   tv_nsec;               /* наносекунди, 0…999999999 */
};
