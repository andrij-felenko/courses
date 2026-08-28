#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>
#include <errno.h>

static void sigchld_handler(int sig) {
    (void)sig;
    int saved_errno = errno; /* обробник сигналу зобов'язаний зберегти errno */
    pid_t pid;
    int status;

    /* Вичищаємо ВСІХ дітей, що встигли завершитися до цього моменту */
    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        /* Обробка результату pid і status */
    }

    errno = saved_errno;
}
