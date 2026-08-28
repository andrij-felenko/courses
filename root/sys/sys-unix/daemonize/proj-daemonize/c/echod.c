/* echod.c — жодного розділення.
   cc -std=c11 -o echod echod.c $(pkg-config --libs libsystemd)       */

#include <systemd/sd-daemon.h>

static volatile sig_atomic_t stop_flag = 0;

static void on_term(int sig) { (void)sig; stop_flag = 1; }

int main(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_term;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTERM, &sa, NULL);        /* БЕЗ SA_RESTART — свідомо */

    sa.sa_handler = SIG_IGN;
    sigaction(SIGPIPE, &sa, NULL);

    int lsock = listen_on(9000);
    if (lsock < 0) {
        fprintf(stderr, "listen: %s\n", strerror(errno));   /* stderr → журнал */
        return 1;
    }
    fprintf(stderr, "піднялися, слухаємо 9000\n");

    sd_notify(0, "READY=1");              /* те саме, що байт у трубу */

    while (!stop_flag)
        serve_once(lsock);                /* accept() поверне EINTR при SIGTERM */

    sd_notify(0, "STOPPING=1");
    close(lsock);
    return 0;
}
