#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/resource.h>
#include <unistd.h>

int main(void)
{
    struct rlimit rl;

    if (getrlimit(RLIMIT_NOFILE, &rl) != 0) {
        perror("getrlimit");
        return 1;
    }
    printf("на старті:  м'який %llu  жорсткий %llu\n",
           (unsigned long long)rl.rlim_cur, (unsigned long long)rl.rlim_max);

    rl.rlim_cur = rl.rlim_max;              /* угору до жорсткого — прав не треба */
    if (setrlimit(RLIMIT_NOFILE, &rl) != 0)
        perror("setrlimit");                /* не фатально: міряємо те, що дали */
    getrlimit(RLIMIT_NOFILE, &rl);          /* що вийшло насправді */

    int first = -1, last = -1;
    long n = 0;

    for (;;) {
        int fd = open("/dev/null", O_RDONLY | O_CLOEXEC);
        if (fd < 0)
            break;
        if (first < 0)
            first = fd;
        last = fd;
        n++;
    }
    int stop = errno;                       /* зберегти до першого printf */

    printf("м'який тепер %llu; відкрито ще %ld\n",
           (unsigned long long)rl.rlim_cur, n);
    printf("номери від %d до %d; зупинив: %s (errno %d)\n",
           first, last, strerror(stop), stop);
    return 0;
}
