/* zombies.c — один waitpid проти циклу.
 * gcc -O2 -Wall -o zombies zombies.c     запуск: ./zombies 40 one   або   ./zombies 40 loop
 */
#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/wait.h>

static volatile sig_atomic_t deliveries = 0;   /* запусків обробника */
static volatile sig_atomic_t reaped     = 0;   /* прибраних нащадків */

static void chld_one(int sig)                  /* ✗ одне доправлення — один wait */
{
    int saved = errno;
    deliveries++;
    if (waitpid(-1, NULL, WNOHANG) > 0) reaped++;
    errno = saved;
}

static void chld_loop(int sig)                 /* ✓ прийшло «подивись» — вигрібай геть усе */
{
    int saved = errno;
    deliveries++;
    while (waitpid(-1, NULL, WNOHANG) > 0) reaped++;
    errno = saved;
}

int main(int argc, char **argv)
{
    int n    = (argc > 1) ? atoi(argv[1]) : 40;
    int loop = (argc > 2 && strcmp(argv[2], "loop") == 0);
    int gate[2];
    struct sigaction sa;
    sigset_t chld;

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = loop ? chld_loop : chld_one;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    sigaction(SIGCHLD, &sa, NULL);

    if (pipe(gate) != 0) { perror("pipe"); return 1; }

    for (int i = 0; i < n; i++) {
        pid_t p = fork();
        if (p < 0) { perror("fork"); return 1; }
        if (p == 0) {
            char c;
            close(gate[1]);
            while (read(gate[0], &c, 1) < 0 && errno == EINTR)
                ;
            _exit(0);
        }
    }
    close(gate[0]);
    close(gate[1]);                    /* ворота відчинено для всіх воднораз */

    for (unsigned rest = 1; (rest = sleep(rest)) > 0; )
        ;                              /* кожен SIGCHLD уриває sleep — досипаємо решту */

    sigemptyset(&chld);
    sigaddset(&chld, SIGCHLD);
    sigprocmask(SIG_BLOCK, &chld, NULL);   /* спиняємо обробник, щоб порахувати чесно */

    int left = 0;
    while (waitpid(-1, NULL, WNOHANG) > 0) left++;

    printf("%s: нащадків %d, доправлень SIGCHLD %d, прибрано обробником %d, лишалося %d\n",
           loop ? "цикл  " : "один  ", n, (int) deliveries, (int) reaped, left);
    return 0;
}
