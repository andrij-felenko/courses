/* Найменший обов'язок процесу з номером 1: забирати коди виходу всіх,
   кого до нього приписали, — і своїх дітей, і чужих сиріт. */
#include <sys/wait.h>
#include <signal.h>

int main(void)
{
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGCHLD);
    sigprocmask(SIG_BLOCK, &mask, NULL);   /* чекатимемо явно, а не в обробнику */

    /* ... тут PID 1 запускає все, що має працювати ... */

    for (;;) {
        int sig;
        sigwait(&mask, &sig);              /* прокинулися: хтось із нащадків помер */

        while (waitpid(-1, NULL, WNOHANG) > 0)
            ;                              /* смертей могло бути кілька на одне сповіщення */
    }
}
