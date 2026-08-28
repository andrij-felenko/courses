#define _GNU_SOURCE
#include <sys/resource.h>
#include <unistd.h>

/* Запустити чужу програму так, щоб вона не змогла ані взяти більше
   за nofile дескрипторів, ані повернути цю межу собі назад. */
static pid_t spawn_fenced(char *const argv[], rlim_t nofile, rlim_t cpu_sec)
{
    pid_t pid = fork();
    if (pid != 0)
        return pid;                       /* батько своїх меж не чіпав */

    /* Обидва поля разом: rlim_cur > rlim_max дало б EINVAL. */
    struct rlimit rl = { .rlim_cur = nofile, .rlim_max = nofile };
    if (setrlimit(RLIMIT_NOFILE, &rl) != 0)
        _exit(125);

    rl.rlim_cur = cpu_sec;                /* м'яка межа → SIGXCPU */
    rl.rlim_max = cpu_sec + 1;            /* ще секунда → SIGKILL */
    if (setrlimit(RLIMIT_CPU, &rl) != 0)
        _exit(125);

    /* Без цього чужа програма успадкує наші відкриті файли — і сокет бази,
       і журнал; кожен із них ще й з'їв би номер із її нової межі. */
    if (close_range(3, ~0U, 0) != 0)      /* Linux 5.9, glibc 2.34 */
        _exit(125);

    execvp(argv[0], argv);
    _exit(127);
}
