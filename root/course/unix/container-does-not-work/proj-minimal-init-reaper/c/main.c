#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/signalfd.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <poll.h>
#include <errno.h>

static void reap_zombies(pid_t primary_child, int *primary_status, int *primary_exited) {
    pid_t pid;
    int status;

    while ((pid = waitpid(-1, &status, WNOHANG)) > 0) {
        if (pid == primary_child) {
            *primary_status = status;
            *primary_exited = 1;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <команда> [аргументи...]\n", argv[0]);
        return 1;
    }

    /* 1. Оголошення себе збирачем сиріт (subreaper) на випадок запуску не під PID 1 */
    if (prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) < 0) {
        perror("prctl(PR_SET_CHILD_SUBREAPER)");
    }

    /* 2. Блокування сигналів для перехоплення через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGQUIT);
    sigaddset(&mask, SIGHUP);
    sigaddset(&mask, SIGCHLD);

    if (sigprocmask(SIG_BLOCK, &mask, NULL) < 0) {
        perror("sigprocmask");
        return 1;
    }

    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd < 0) {
        perror("signalfd");
        return 1;
    }

    /* 3. Породження цільового процесу застосунку */
    pid_t child_pid = fork();
    if (child_pid < 0) {
        perror("fork");
        close(sfd);
        return 1;
    }

    if (child_pid == 0) {
        /* Дочірній процес: розблокування сигналів перед запуском */
        sigprocmask(SIG_UNBLOCK, &mask, NULL);
        close(sfd);

        /* Створення власної групи процесів для ізольованої доставки сигналів */
        setpgid(0, 0);

        execvp(argv[1], &argv[1]);
        perror("execvp");
        _exit(127);
    }

    /* 4. Головний цикл супервізора */
    struct pollfd pfd = { .fd = sfd, .events = POLLIN, .revents = 0 };
    int primary_exited = 0;
    int primary_status = 0;

    while (1) {
        int ret = poll(&pfd, 1, -1);
        if (ret < 0) {
            if (errno == EINTR) continue;
            perror("poll");
            break;
        }

        if (pfd.revents & POLLIN) {
            struct signalfd_siginfo fdsi;
            ssize_t s = read(sfd, &fdsi, sizeof(fdsi));
            if (s != sizeof(fdsi)) continue;

            if (fdsi.ssi_signo == SIGCHLD) {
                reap_zombies(child_pid, &primary_status, &primary_exited);
                if (primary_exited) {
                    /* Головний процес завершився, дозбируємо залишкових сиріт */
                    reap_zombies(child_pid, &primary_status, &primary_exited);
                    break;
                }
            } else {
                /* Трансляція сигналів усій групі процесів дочірньої програми */
                kill(-child_pid, (int)fdsi.ssi_signo);
            }
        }
    }

    close(sfd);

    /* 5. Трансляція коду завершення */
    if (WIFEXITED(primary_status)) {
        return WEXITSTATUS(primary_status);
    } else if (WIFSIGNALED(primary_status)) {
        return 128 + WTERMSIG(primary_status);
    }

    return 1;
}
