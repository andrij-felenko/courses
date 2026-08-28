#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

/* Повертає 0 і номер дитини в *out, або errno невдалого запуску. */
static int spawn(char *const argv[], pid_t *out)
{
    int pfd[2];
    if (pipe2(pfd, O_CLOEXEC) == -1)      /* обидва кінці закриються при exec */
        return errno;

    pid_t pid = fork();
    if (pid == -1) {
        int e = errno;
        close(pfd[0]);
        close(pfd[1]);
        return e;
    }

    if (pid == 0) {                       /* дитина */
        close(pfd[0]);
        execvp(argv[0], argv);            /* далі — лише гілка відмови */
        int e = errno;
        write(pfd[1], &e, sizeof e);      /* труба ще жива: заміни не сталося */
        _exit(127);
    }

    close(pfd[1]);                        /* кінець на запис лишається в дитини */

    int e = 0;
    ssize_t n = read(pfd[0], &e, sizeof e);
    close(pfd[0]);

    if (n == (ssize_t)sizeof e) {         /* дитина встигла поскаржитися */
        waitpid(pid, NULL, 0);
        return e;
    }
    *out = pid;                           /* n == 0: труба закрилася на exec */
    return 0;
}

int main(void)
{
    pid_t pid;
    int err = spawn((char *[]){ "gzip", "-9", "data.bin", NULL }, &pid);
    if (err != 0) {
        fprintf(stderr, "запуск не вдався: %s\n", strerror(err));
        return 1;
    }

    int status;
    waitpid(pid, &status, 0);
    printf("pid=%d exit=%d\n", pid, WIFEXITED(status) ? WEXITSTATUS(status) : -1);
    return 0;
}
