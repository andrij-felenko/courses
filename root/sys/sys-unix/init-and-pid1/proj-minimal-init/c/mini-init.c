/* mini-init.c — найменший чесний init для контейнера.
   Складання:  cc -O2 -Wall -o mini-init mini-init.c              */

#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "вжиток: %s <програма> [аргументи…]\n", argv[0]);
        return 2;
    }

    /* 1. Блокуємо все, на що збираємося реагувати, — ДО появи дитини.
          Синхронні пастки лишаємо відкритими: вони приходять від власної
          помилки, і блокувати їх стандарт прямо забороняє.            */
    sigset_t mask, orig;
    sigfillset(&mask);
    sigdelset(&mask, SIGSEGV);
    sigdelset(&mask, SIGBUS);
    sigdelset(&mask, SIGILL);
    sigdelset(&mask, SIGFPE);
    sigprocmask(SIG_BLOCK, &mask, &orig);

    /* 2. Запускаємо справжній застосунок. */
    pid_t child = fork();
    if (child < 0) {
        perror("fork");
        return 1;
    }
    if (child == 0) {
        sigprocmask(SIG_SETMASK, &orig, NULL);  /* маска переживає exec — знімаємо */
        execvp(argv[1], &argv[1]);
        perror(argv[1]);
        _exit(127);                             /* усталений код «команду не запущено» */
    }

    /* 3. Єдиний цикл: прокинувся від сигналу — розібрався — знову спати. */
    for (;;) {
        int sig;
        if (sigwait(&mask, &sig) != 0)
            continue;

        if (sig != SIGCHLD) {
            kill(child, sig);                   /* пересилаємо застосункові */
            continue;
        }

        /* Одне сповіщення може означати кілька смертей — ховаємо всіх. */
        for (;;) {
            int status;
            pid_t dead = waitpid(-1, &status, WNOHANG);

            if (dead <= 0)
                break;          /* 0 — живі ще є; -1 з ECHILD — ховати нікого */
            if (dead != child)
                continue;       /* чужа сирота: поховали й забули */

            if (WIFEXITED(status))
                return WEXITSTATUS(status);
            if (WIFSIGNALED(status))
                return 128 + WTERMSIG(status);
        }
    }
}
