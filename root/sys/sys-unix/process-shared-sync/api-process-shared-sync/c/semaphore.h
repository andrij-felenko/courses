#include <semaphore.h>

int    sem_init     (sem_t *sem, int pshared, unsigned int value);
int    sem_destroy  (sem_t *sem);
sem_t *sem_open     (const char *name, int oflag,
                     ... /* mode_t mode, unsigned int value */);
int    sem_close    (sem_t *sem);
int    sem_unlink   (const char *name);

int    sem_wait     (sem_t *sem);
int    sem_trywait  (sem_t *sem);
int    sem_timedwait(sem_t *restrict sem,
                     const struct timespec *restrict abs_timeout);
int    sem_clockwait(sem_t *restrict sem, clockid_t clockid,
                     const struct timespec *restrict abs_timeout);
int    sem_post     (sem_t *sem);
int    sem_getvalue (sem_t *restrict sem, int *restrict sval);
