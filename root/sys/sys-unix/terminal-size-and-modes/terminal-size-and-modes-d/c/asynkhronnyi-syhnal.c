#include <signal.h>
#include <stdbool.h>

static volatile sig_atomic_t g_window_resized = 0;

static void handle_sigwinch(int sig) {
    (void)sig;
    g_window_resized = 1;
}

void setup_signals(void) {
    struct sigaction sa;
    sa.sa_handler = handle_sigwinch;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    sigaction(SIGWINCH, &sa, NULL);
}
