/* sysmon.c — Системний демон фонового моніторингу на C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <syslog.h>
#include <signal.h>

static volatile int keep_running = 1;

void handle_signal(int sig) {
    if (sig == SIGINT || sig == SIGTERM) {
        keep_running = 0;
    }
}

int main(void) {
    openlog("sysmon", LOG_PID | LOG_CONS, LOG_DAEMON);
    syslog(LOG_INFO, "Демон sysmon успішно запущено.");

    struct sigaction sa;
    sa.sa_handler = handle_signal;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    while (keep_running) {
        syslog(LOG_INFO, "sysmon: системний статус OK");
        sleep(5);
    }

    syslog(LOG_INFO, "Демон sysmon зупинено за сигналом.");
    closelog();
    return 0;
}
