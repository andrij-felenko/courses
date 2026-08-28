#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

static volatile sig_atomic_t g_signal_pending = 0;

static void sig_handler(int sig) {
    g_signal_pending = sig;
    // Всередині C-обробника дозволені лише Async-Signal-Safe системні виклики
    const char msg[] = "Сигнал перехоплено, планується завершення...\n";
    write(STDERR_FILENO, msg, sizeof(msg) - 1);
}

void setup_signal_handlers(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = sig_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
}
