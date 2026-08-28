#include <signal.h>
#include <string.h>

static volatile sig_atomic_t stop_requested = 0;

static void on_term(int signo) {
    (void)signo;
    stop_requested = 1;          /* усе, що можна робити тут, — звести прапорець */
}

int install_term_handler(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);   /* поля, яких не заповнюємо, мають бути нульові */

    sa.sa_handler = on_term;
    sigemptyset(&sa.sa_mask);
    sigaddset(&sa.sa_mask, SIGINT);  /* на час обробника блокуємо ще й SIGINT */
    sa.sa_flags = SA_RESTART;        /* перервані виклики переграти, а не віддавати EINTR */

    if (sigaction(SIGTERM, &sa, NULL) == -1)
        return -1;
    return 0;
}
