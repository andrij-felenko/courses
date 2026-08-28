#define _GNU_SOURCE
#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>

static volatile sig_atomic_t ticks;
static void on_alarm(int sig) { (void) sig; ticks++; }

static void report(const char *what, long r)
{
    if (r < 0) printf("%-5s = %ld, errno = %d (%s), тиків = %d\n",
                      what, r, errno, strerror(errno), (int) ticks);
    else       printf("%-5s = %ld, помилки немає, тиків = %d\n",
                      what, r, (int) ticks);
}

int main(void)
{
    struct sigaction sa;
    sigemptyset(&sa.sa_mask);
    sa.sa_handler = on_alarm;
    sa.sa_flags   = SA_RESTART;      /* приберіть — і read теж дасть EINTR */
    if (sigaction(SIGALRM, &sa, NULL) == -1) { perror("sigaction"); return 1; }

    struct itimerval it = { { 0, 200000 }, { 0, 200000 } };   /* що 200 мс */
    setitimer(ITIMER_REAL, &it, NULL);

    char buf[64];
    report("read", read(STDIN_FILENO, buf, sizeof buf));       /* група 1 */

    struct pollfd pfd = { STDIN_FILENO, POLLIN, 0 };
    report("poll", poll(&pfd, 1, 5000));                       /* група 2 */
    return 0;
}
