#include <pthread.h>          /* збірка: cc … -pthread */

int pthread_mutexattr_init   (pthread_mutexattr_t *attr);
int pthread_mutexattr_destroy(pthread_mutexattr_t *attr);

int pthread_mutexattr_setpshared    (pthread_mutexattr_t *attr, int pshared);
int pthread_mutexattr_setrobust     (pthread_mutexattr_t *attr, int robustness);
int pthread_mutexattr_setprotocol   (pthread_mutexattr_t *attr, int protocol);
int pthread_mutexattr_settype       (pthread_mutexattr_t *attr, int type);
int pthread_mutexattr_setprioceiling(pthread_mutexattr_t *attr, int ceiling);
