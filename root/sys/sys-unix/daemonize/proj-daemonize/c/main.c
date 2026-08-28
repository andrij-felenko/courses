/* main.c — служба, яка вміє обидва режими.
   cc -std=c11 -D_GNU_SOURCE -o echod main.c daemonize.c              */

#include <syslog.h>

int daemonize(const char *pidpath);
void daemon_ready(void);
void daemon_fail(const char *stage);

int main(int argc, char **argv)
{
    int background = !(argc > 1 && strcmp(argv[1], "--foreground") == 0);

    if (background && daemonize("/run/echod.pid") < 0) {
        perror("daemonize");
        return 1;
    }

    int lsock = listen_on(9000);          /* СПРАВЖНЯ ініціалізація */
    if (lsock < 0) {
        daemon_fail("listen");            /* помилка їде в трубу, до термінала */
        return 1;
    }

    openlog("echod", LOG_PID, LOG_DAEMON);
    syslog(LOG_INFO, "піднялися, слухаємо 9000");

    daemon_ready();                       /* аж ТЕПЕР пускач виходить із нулем */

    serve_forever(lsock);                 /* головний цикл */
    return 0;
}
