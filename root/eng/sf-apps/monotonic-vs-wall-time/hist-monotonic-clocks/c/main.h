pthread_condattr_t attr;
pthread_condattr_init(&attr);
pthread_condattr_setclock(&attr, CLOCK_MONOTONIC);  /* редакція 6: годинник — на змінну */
pthread_cond_init(&cv, &attr);

struct timespec deadline;
clock_gettime(CLOCK_MONOTONIC, &deadline);
deadline.tv_sec += 30;                              /* абсолютний момент за СТАЛИМ годинником */
pthread_cond_timedwait(&cv, &m, &deadline);

/* редакція 8: годинник називають у самому очікуванні */
pthread_cond_clockwait(&cv, &m, CLOCK_MONOTONIC, &deadline);
