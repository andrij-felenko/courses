#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <spawn.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

extern char **environ;

#ifdef __GLIBC_PREREQ
# if __GLIBC_PREREQ(2, 34)
#  define HAVE_ADDCLOSEFROM 1
# endif
#endif

/* Будівничі повертають номер помилки; тримаємо перший ненульовий. */
#define STEP(call) do { if (rc == 0) rc = (call); } while (0)

/* 0 — усе гаразд і статус у *status; інакше номер помилки запуску. */
static int run_sort(const char *lines, const char *out_path, int *status)
{
    posix_spawn_file_actions_t fa;
    posix_spawnattr_t at;
    sigset_t empty, all;
    char *argv[] = { "sort", "-n", NULL };
    int pfd[2], rc;
    pid_t pid;

    if (pipe2(pfd, O_CLOEXEC) == -1)     /* обидва кінці — з FD_CLOEXEC */
        return errno;                    /* pipe2 — стара домовленість: −1 і errno */

    rc = posix_spawn_file_actions_init(&fa);
    if (rc != 0) {
        close(pfd[0]); close(pfd[1]);
        return rc;
    }
    rc = posix_spawnattr_init(&at);
    if (rc != 0) {
        posix_spawn_file_actions_destroy(&fa);
        close(pfd[0]); close(pfd[1]);
        return rc;
    }

    /* Дії виконаються рівно в цьому порядку. */
    STEP(posix_spawn_file_actions_adddup2(&fa, pfd[0], STDIN_FILENO));
    STEP(posix_spawn_file_actions_addopen(&fa, STDOUT_FILENO, out_path,
                                          O_WRONLY | O_CREAT | O_TRUNC, 0644));
    STEP(posix_spawn_file_actions_addopen(&fa, STDERR_FILENO, "/dev/null",
                                          O_WRONLY, 0));
#ifdef HAVE_ADDCLOSEFROM
    STEP(posix_spawn_file_actions_addclosefrom_np(&fa, 3));  /* тільки останнім! */
#endif

    sigemptyset(&empty);
    sigfillset(&all);
    STEP(posix_spawnattr_setsigmask(&at, &empty));    /* чиста маска */
    STEP(posix_spawnattr_setsigdefault(&at, &all));   /* жодного успадкованого SIG_IGN */
    STEP(posix_spawnattr_setpgroup(&at, 0));          /* власна група процесів */
    STEP(posix_spawnattr_setflags(&at, POSIX_SPAWN_SETSIGMASK
                                     | POSIX_SPAWN_SETSIGDEF
                                     | POSIX_SPAWN_SETPGROUP));

    if (rc == 0)
        rc = posix_spawnp(&pid, "sort", &fa, &at, argv, environ);

    posix_spawn_file_actions_destroy(&fa);
    posix_spawnattr_destroy(&at);
    close(pfd[0]);                       /* кінець на читання лишається дитині */

    if (rc != 0) {
        close(pfd[1]);
        return rc;
    }

    write(pfd[1], lines, strlen(lines));
    close(pfd[1]);                       /* закриття = кінець вводу для sort */

    return waitpid(pid, status, 0) == -1 ? errno : 0;
}

int main(void)
{
    int status = 0;

    signal(SIGPIPE, SIG_IGN);            /* інакше мертвий sort уб'є нас під час write */

    int err = run_sort("30\n4\n100\n7\n", "sorted.txt", &status);
    if (err != 0) {
        fprintf(stderr, "запустити не вдалося: %s\n", strerror(err));
        return 1;
    }
    if (WIFEXITED(status) && WEXITSTATUS(status) == 127)
        fprintf(stderr, "код 127: на цій системі так звітують про невдалий запуск\n");
    return 0;
}
