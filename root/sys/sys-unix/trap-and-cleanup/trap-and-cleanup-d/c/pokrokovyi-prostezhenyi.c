#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>

static void reraise_signal_handler(int sig) {
    // 1. Виконання термінового прибирання
    // (використовуючи async-signal-safe операції)
    
    // 2. Скидання диспозиції на дефолтну
    struct sigaction sa;
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(sig, &sa, NULL);

    // 3. Ретрансляція сигналу власному процесу
    raise(sig);
}
