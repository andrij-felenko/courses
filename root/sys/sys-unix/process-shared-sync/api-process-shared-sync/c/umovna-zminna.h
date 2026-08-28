int pthread_condattr_setpshared(pthread_condattr_t *attr, int pshared);
int pthread_condattr_setclock  (pthread_condattr_t *attr, clockid_t clock_id);

int pthread_cond_init     (pthread_cond_t *restrict cond,
                           const pthread_condattr_t *restrict attr);
int pthread_cond_destroy  (pthread_cond_t *cond);
int pthread_cond_wait     (pthread_cond_t *restrict cond,
                           pthread_mutex_t *restrict mutex);
int pthread_cond_timedwait(pthread_cond_t *restrict cond,
                           pthread_mutex_t *restrict mutex,
                           const struct timespec *restrict abstime);
int pthread_cond_clockwait(pthread_cond_t *restrict cond,
                           pthread_mutex_t *restrict mutex, clockid_t clockid,
                           const struct timespec *restrict abstime);
int pthread_cond_signal   (pthread_cond_t *cond);
int pthread_cond_broadcast(pthread_cond_t *cond);
