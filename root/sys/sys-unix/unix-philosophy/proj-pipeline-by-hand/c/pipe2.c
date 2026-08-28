/* pipe2.c — «tr -cs A-Za-z '\n' | sort» вручну, без оболонки.
   збірка: cc -std=c11 -Wall -Wextra -o pipe2 pipe2.c            */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

/* "\\n" — це ДВА символи, зворотна скісна й n: саме їх дає оболонка,
   коли пишуть '\n', а розкриває їх сам tr.                        */
static char *A[] = { "tr", "-cs", "A-Za-z", "\\n", NULL };
static char *B[] = { "sort", NULL };

static void die(const char *what) { perror(what); _exit(1); }

/* Код виходу так, як його рахує оболонка: 128 + номер сигналу,
   коли процес не вийшов сам, а був убитий.                        */
static int code_of(int st)
{
    if (WIFEXITED(st))   return WEXITSTATUS(st);
    if (WIFSIGNALED(st)) return 128 + WTERMSIG(st);
    return 1;
}

int main(void)
{
    int p[2];                              /* p[0] — читати, p[1] — писати */
    if (pipe(p) < 0) die("pipe");

    pid_t a = fork();
    if (a < 0) die("fork");
    if (a == 0) {                          /* ліва ланка: вивід — у канал */
        if (dup2(p[1], STDOUT_FILENO) < 0) die("dup2");
        close(p[0]);                       /* читальний кінець їй не потрібен */
        close(p[1]);                       /* оригінал теж: копія вже під №1  */
        signal(SIGPIPE, SIG_DFL);          /* не успадкувати чуже ігнорування */
        execvp(A[0], A);
        perror(A[0]);
        _exit(127);                        /* угода оболонок: 127 — не знайдено */
    }

    pid_t b = fork();
    if (b < 0) die("fork");
    if (b == 0) {                          /* права ланка: ввід — із каналу */
        if (dup2(p[0], STDIN_FILENO) < 0) die("dup2");
        close(p[0]);
        close(p[1]);
        signal(SIGPIPE, SIG_DFL);
        execvp(B[0], B);
        perror(B[0]);
        _exit(127);
    }

    close(p[0]);                           /* батько не бере участі в передачі */
    close(p[1]);                           /* ← найважливіші два рядки файлу   */

    int sa = 0, sb = 0;
    while (waitpid(a, &sa, 0) < 0) if (errno != EINTR) die("waitpid");
    while (waitpid(b, &sb, 0) < 0) if (errno != EINTR) die("waitpid");

    int ca = code_of(sa), cb = code_of(sb);
    fprintf(stderr, "ланки: %d %d | без pipefail: %d | з pipefail: %d\n",
            ca, cb, cb, cb ? cb : ca);
    return cb ? cb : ca;
}
