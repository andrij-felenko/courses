/* y2038-kernel.c — чи є в ядра 64-бітна пара до clock_gettime */
#define _GNU_SOURCE
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

/* Саме так виглядає struct __kernel_timespec: секунди — рівно 64 біти,
   що б про time_t не думала бібліотека C. */
struct kernel_timespec64 {
    long long tv_sec;
    long long tv_nsec;
};

int main(void)
{
#ifdef __NR_clock_gettime64
    struct kernel_timespec64 ts = { 0, 0 };

    if (syscall(__NR_clock_gettime64, CLOCK_REALTIME, &ts) == 0) {
        printf("clock_gettime64 (№%ld) працює, tv_sec = %lld\n",
               (long)__NR_clock_gettime64, ts.tv_sec);
        return 0;
    }
    if (errno == ENOSYS) {
        puts("clock_gettime64 відсутній: ядро старше за 5.1 (травень 2019)");
        return 1;
    }
    printf("clock_gettime64 повернув помилку: %s\n", strerror(errno));
    return 1;
#else
    puts("номера clock_gettime64 немає в заголовках: або архітектура 64-бітна "
         "(там звичайний clock_gettime уже 64-бітний), або заголовки застарілі");
    return 0;
#endif
}
