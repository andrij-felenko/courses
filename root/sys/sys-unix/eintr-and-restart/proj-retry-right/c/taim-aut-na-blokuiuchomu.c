#include <signal.h>

static volatile sig_atomic_t alarm_fired;

static void on_alarm(int sig) { (void) sig; alarm_fired = 1; }

ssize_t read_deadline(int fd, void *buf, size_t len, unsigned sec) {
    struct sigaction sa = {0};
    sa.sa_handler = on_alarm;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;                     /* саме тут: БЕЗ SA_RESTART */
    if (sigaction(SIGALRM, &sa, NULL) < 0) return -1;

    alarm_fired = 0;
    alarm(sec);
    ssize_t n     = read(fd, buf, len);  /* один виклик, БЕЗ петлі на EINTR */
    int     saved = errno;               /* alarm() нижче зіпсує errno */
    alarm(0);

    if (n < 0 && saved == EINTR && alarm_fired) { errno = ETIMEDOUT; return -1; }
    errno = saved;
    return n;
}
