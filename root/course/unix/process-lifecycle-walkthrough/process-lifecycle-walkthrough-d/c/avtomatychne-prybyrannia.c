#include <signal.h>
#include <stddef.h>

void disable_zombies(void) {
    struct sigaction sa;
    sa.sa_handler = SIG_IGN;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_NOCLDWAIT; /* ядро автоматично знищує зомбі, не турбуючи батька */
    sigaction(SIGCHLD, &sa, NULL);
}
