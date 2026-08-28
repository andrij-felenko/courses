#define _XOPEN_SOURCE 600
#define _DEFAULT_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>

static struct termios saved;      /* режим НАШОГО термінала до втручання */
static int master = -1;
static int winch_pipe[2];         /* самотруба: обробник SIGWINCH → цикл */

static void restore(void) { tcsetattr(STDIN_FILENO, TCSAFLUSH, &saved); }

static void on_winch(int sig) {
    int e = errno;                /* обробник не сміє псувати чужий errno */
    (void)sig;
    write(winch_pipe[1], "!", 1);
    errno = e;
}

static void push_winsize(void) {
    struct winsize ws;
    if (ioctl(STDIN_FILENO, TIOCGWINSZ, &ws) == 0)
        ioctl(master, TIOCSWINSZ, &ws);   /* SIGWINCH дитині надішле ядро само */
}

static int write_all(int fd, const char *p, size_t n) {
    while (n > 0) {
        ssize_t w = write(fd, p, n);
        if (w < 0) { if (errno == EINTR) continue; return -1; }
        p += w; n -= (size_t)w;
    }
    return 0;
}

int main(int argc, char **argv) {
    const char *shell = (argc > 1) ? argv[1] : "/bin/sh";

    if (tcgetattr(STDIN_FILENO, &saved) < 0) {
        fprintf(stderr, "стандартний вхід — не термінал\n");
        return 1;
    }

    master = posix_openpt(O_RDWR | O_NOCTTY);
    if (master < 0 || grantpt(master) < 0 || unlockpt(master) < 0) {
        perror("псевдотермінал"); return 1;
    }
    int slave = open(ptsname(master), O_RDWR);
    if (slave < 0) { perror("підлеглий кінець"); return 1; }

    tcsetattr(master, TCSANOW, &saved);   /* дитині — наші erase, kill, ISIG */
    push_winsize();                       /* і наш розмір ще до старту */

    pid_t pid = fork();
    if (pid < 0) { perror("fork"); return 1; }
    if (pid == 0) {
        close(master);
        setsid();                         /* власний сеанс без керуючого термінала */
        ioctl(slave, TIOCSCTTY, 0);       /* керуючим стає підлеглий кінець */
        dup2(slave, STDIN_FILENO);
        dup2(slave, STDOUT_FILENO);
        dup2(slave, STDERR_FILENO);
        if (slave > STDERR_FILENO) close(slave);
        execl(shell, shell, (char *)NULL);
        _exit(127);
    }
    close(slave);                         /* інакше EIO не прийде НІКОЛИ */

    struct termios raw = saved;
    cfmakeraw(&raw);
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
    atexit(restore);

    if (pipe(winch_pipe) < 0) { perror("pipe"); return 1; }
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_winch;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    sigaction(SIGWINCH, &sa, NULL);

    struct pollfd p[3] = {
        { STDIN_FILENO,  POLLIN, 0 },
        { master,        POLLIN, 0 },
        { winch_pipe[0], POLLIN, 0 },
    };
    char buf[4096];

    for (;;) {
        if (poll(p, 3, -1) < 0) {
            if (errno == EINTR) continue;
            break;
        }
        if (p[2].revents & POLLIN) {              /* вікно змінили */
            char drain[64];
            read(winch_pipe[0], drain, sizeof drain);
            push_winsize();
        }
        if (p[0].revents & POLLIN) {              /* клавіші → ведучий кінець */
            ssize_t n = read(STDIN_FILENO, buf, sizeof buf);
            if (n < 0 && errno == EINTR) continue;
            if (n <= 0) break;
            if (write_all(master, buf, (size_t)n) < 0) break;
        }
        if (p[1].revents & (POLLIN | POLLHUP)) {  /* вивід дитини → наш екран */
            ssize_t n = read(master, buf, sizeof buf);
            if (n < 0 && errno == EINTR) continue;
            if (n <= 0) break;                    /* 0 або EIO — розмова скінчилася */
            if (write_all(STDOUT_FILENO, buf, (size_t)n) < 0) break;
        }
    }

    int status = 0;
    while (waitpid(pid, &status, 0) < 0 && errno == EINTR)
        ;
    restore();
    return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
}
