#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

static void die(const char *what) { perror(what); _exit(1); }

int main(int argc, char **argv)
{
    int with_shrink = !(argc > 1 && strcmp(argv[1], "--no-shrink") == 0);
    setvbuf(stdout, NULL, _IOLBF, 0);          /* щоб рядки не злипалися */

    int sv[2];
    if (socketpair(AF_UNIX, SOCK_SEQPACKET | SOCK_CLOEXEC, 0, sv) < 0)
        die("socketpair");

    pid_t pid = fork();
    if (pid < 0) die("fork");
    if (pid == 0) { close(sv[0]); consumer(sv[1]); _exit(0); }

    close(sv[1]);
    producer(sv[0], with_shrink);

    int st;
    if (waitpid(pid, &st, 0) > 0 && WIFSIGNALED(st))
        printf("[батько] споживач загинув від сигналу %d (%s)\n",
               WTERMSIG(st), strsignal(WTERMSIG(st)));
    return 0;
}
