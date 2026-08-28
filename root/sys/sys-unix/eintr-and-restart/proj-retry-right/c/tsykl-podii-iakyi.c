#include <sys/epoll.h>
#include <time.h>

static volatile sig_atomic_t want_stop;    /* виставляє обробник SIGTERM */
static volatile sig_atomic_t want_reload;  /* виставляє обробник SIGHUP  */

static long now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

int run_loop(int ep, int budget_ms) {
    struct epoll_event ev[64];
    long deadline = now_ms() + budget_ms;

    for (;;) {
        if (want_stop)   return 0;
        if (want_reload) { want_reload = 0; reload_config(); }

        long left = deadline - now_ms();
        if (left < 0) left = 0;

        int n = epoll_wait(ep, ev, 64, (int) left);
        if (n < 0) {
            if (errno == EINTR) continue;   /* не помилка: просто новий оберт */
            return -1;                      /* EBADF, EINVAL, EFAULT — поломка */
        }
        if (n == 0) { on_timeout(); deadline = now_ms() + budget_ms; continue; }
        for (int i = 0; i < n; i++) dispatch(&ev[i]);
    }
}
