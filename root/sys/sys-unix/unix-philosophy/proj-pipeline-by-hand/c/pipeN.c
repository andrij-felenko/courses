/* pipeN.c — «A : B : C : …» вручну.
   збірка: cc -std=c11 -Wall -Wextra -o pipeN pipeN.c
   запуск: ./pipeN tr -cs A-Za-z '\n' : tr A-Z a-z : sort : uniq -c : sort -rn : sed 10q */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAXN 64

static void die(const char *what) { perror(what); _exit(1); }

static int code_of(int st)
{
    if (WIFEXITED(st))   return WEXITSTATUS(st);
    if (WIFSIGNALED(st)) return 128 + WTERMSIG(st);
    return 1;
}

/* Покласти дескриптор from під номер to. Окремий випадок from == to
   безпечним НЕ є: dup2 у ньому нічого не робить і, зокрема, НЕ знімає
   позначку «закрити при exec» — тож знімаємо її самі.               */
static void move_fd(int from, int to)
{
    if (from == to) {
        int fl = fcntl(from, F_GETFD);
        if (fl < 0 || fcntl(from, F_SETFD, fl & ~FD_CLOEXEC) < 0) die("fcntl");
        return;
    }
    if (dup2(from, to) < 0) die("dup2");
    close(from);
}

int main(int argc, char **argv)
{
    char **cmd[MAXN];
    pid_t pids[MAXN];
    int n = 0;

    if (argc < 2) { fprintf(stderr, "як: %s КОМАНДА [АРГ…] [: КОМАНДА …]\n", argv[0]); return 2; }

    /* Ріжемо argv по ":" просто на місці: argv[argc] уже NULL за стандартом C,
       тож кожен відрізок стає готовим NULL-завершеним списком аргументів. */
    cmd[n++] = &argv[1];
    for (int i = 1; i < argc; i++)
        if (strcmp(argv[i], ":") == 0) {
            argv[i] = NULL;
            if (i + 1 < argc) {
                if (n == MAXN) { fprintf(stderr, "забагато ланок\n"); return 2; }
                cmd[n++] = &argv[i + 1];
            }
        }
    for (int i = 0; i < n; i++)
        if (cmd[i][0] == NULL) { fprintf(stderr, "порожня ланка %d\n", i + 1); return 2; }

    int prev = -1;                       /* звідки читає поточна ланка */
    for (int i = 0; i < n; i++) {
        int p[2] = { -1, -1 };
        int last = (i == n - 1);
        if (!last && pipe(p) < 0) die("pipe");

        pid_t pid = fork();
        if (pid < 0) die("fork");
        if (pid == 0) {
            if (prev != -1) move_fd(prev, STDIN_FILENO);   /* перша ланка лишає свій stdin */
            if (!last) {
                close(p[0]);                               /* читальний кінець — не наш */
                move_fd(p[1], STDOUT_FILENO);
            }
            signal(SIGPIPE, SIG_DFL);
            execvp(cmd[i][0], cmd[i]);
            perror(cmd[i][0]);
            _exit(127);
        }

        pids[i] = pid;
        if (prev != -1) close(prev);      /* дитина його вже успадкувала */
        if (!last) { close(p[1]); prev = p[0]; }
    }

    int pipefail = 0, lastcode = 0;
    for (int i = 0; i < n; i++) {
        int st;
        while (waitpid(pids[i], &st, 0) < 0)
            if (errno != EINTR) die("waitpid");
        int c = code_of(st);
        if (c) pipefail = c;
        if (i == n - 1) lastcode = c;
        fprintf(stderr, "  ланка %d (%s): %d\n", i + 1, cmd[i][0], c);
    }
    fprintf(stderr, "код конвеєра: %d (без pipefail) / %d (з pipefail)\n", lastcode, pipefail);
    return pipefail;
}
