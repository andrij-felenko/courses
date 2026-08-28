#include <sys/types.h>
#include <sys/wait.h>
#include <csignal>
#include <cerrno>

extern "C" void sigchld_handler(int sig) noexcept {
    const int saved_errno = errno;
    int status = 0;

    // Збираємо коди виходу всіх готових дочірніх процесів без блокування
    while (::waitpid(-1, &status, WNOHANG) > 0) {
        // Конкретна реакція на завершення процесу
    }

    errno = saved_errno;
}
