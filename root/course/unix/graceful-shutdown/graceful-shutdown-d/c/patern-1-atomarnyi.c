#include <signal.h>
#include <unistd.h>
#include <sys/epoll.h>

static volatile sig_atomic_t g_terminate = 0;

static void signal_handler(int signo) {
    (void)signo;
    g_terminate = 1;
}

int run_server(int epfd) {
    struct sigaction sa;
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGTERM, &sa, NULL);

    struct epoll_event events[64];
    while (!g_terminate) {
        /* УВАГА: Пастка блокуючого сну! */
        int nfds = epoll_wait(epfd, events, 64, -1);
        if (nfds == -1) {
            /* Якщо прапорець SA_RESTART не встановлено, epoll_wait переривається з EINTR */
            continue;
        }
        /* Обробка вводу-виводу */
    }
    return 0;
}
