struct sigevent sev = {0};
sev.sigev_notify = SIGEV_SIGNAL;
sev.sigev_signo  = SIGRTMIN;             /* реальночасовий: такі стають у чергу */
sev.sigev_value.sival_ptr = session;     /* ось хто спрацював */

timer_t tid;
timer_create(CLOCK_MONOTONIC, &sev, &tid);

struct itimerspec its = {
    .it_value    = { .tv_sec = 0, .tv_nsec = 250000000 },   /* перший строк */
    .it_interval = { .tv_sec = 0, .tv_nsec = 250000000 },   /* і далі щочверть секунди */
};
timer_settime(tid, 0, &its, NULL);
