#include <sys/time.h>

int getitimer(int which, struct itimerval *curr_value);
int setitimer(int which, const struct itimerval *restrict new_value,
                               struct itimerval *restrict old_value);

struct itimerval {
    struct timeval it_interval;  /* період переозброєння; нулі — одноразовий */
    struct timeval it_value;     /* до першого спрацювання; нулі — роззброїти */
};

struct timeval {
    time_t      tv_sec;          /* секунди */
    suseconds_t tv_usec;         /* мікросекунди, 0…999999 */
};
