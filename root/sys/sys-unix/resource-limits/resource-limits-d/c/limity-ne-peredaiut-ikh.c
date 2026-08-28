#include <sys/resource.h>
#include <unistd.h>

/* Запустити програму з власною межею на кількість дескрипторів. */
pid_t run_limited(char *const argv[], rlim_t nofile)
{
    pid_t pid = fork();
    if (pid != 0)
        return pid;                     /* батько лишається зі своїми межами */

    struct rlimit rl = { .rlim_cur = nofile, .rlim_max = nofile };
    if (setrlimit(RLIMIT_NOFILE, &rl) != 0)
        _exit(127);

    execvp(argv[0], argv);              /* межа переживе заміну образу */
    _exit(127);
}
