#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>

static int g_self_pipe_tx = -1;

static void self_pipe_signal_handler(int signo) {
    int saved_errno = errno;
    char sig_byte = (char)signo;
    // write() є async-signal-safe функцією за стандартом POSIX
    (void)write(g_self_pipe_tx, &sig_byte, 1);
    errno = saved_errno; // Відновлюємо errno для потоку, що був перерваний
}

int init_self_pipe(int *out_rx_fd) {
    int fds[2];
    if (pipe(fds) == -1) return -1;

    // Робимо обидва кінці неблокуючими та закриваємо при exec
    fcntl(fds[0], F_SETFL, O_NONBLOCK);
    fcntl(fds[1], F_SETFL, O_NONBLOCK);
    fcntl(fds[0], F_SETFD, FD_CLOEXEC);
    fcntl(fds[1], F_SETFD, FD_CLOEXEC);

    g_self_pipe_tx = fds[1];
    *out_rx_fd = fds[0];

    struct sigaction sa;
    sa.sa_handler = self_pipe_signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
    return 0;
}
