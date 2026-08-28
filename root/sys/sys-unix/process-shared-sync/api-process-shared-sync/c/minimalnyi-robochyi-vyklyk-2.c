#include <fcntl.h>          /* O_CREAT */
#include <semaphore.h>
#include <sys/stat.h>       /* права 0666 */

sem_t *s = sem_open("/frames", O_CREAT, 0666, 0);
if (s == SEM_FAILED) { perror("sem_open"); return 1; }   /* тут perror доречний */

struct timespec ts;
clock_gettime(CLOCK_MONOTONIC, &ts);
ts.tv_sec += 2;                                /* абсолютний строк, не тривалість */

int r;
while ((r = sem_clockwait(s, CLOCK_MONOTONIC, &ts)) == -1 && errno == EINTR)
    ;                                          /* строк той самий — цикл не подовжує чекання */

if (r == -1 && errno == ETIMEDOUT)
    fputs("порція роботи так і не з'явилася\n", stderr);
