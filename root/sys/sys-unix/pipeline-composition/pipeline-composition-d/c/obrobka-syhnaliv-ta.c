#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>

void handle_sigpipe_gracefully(int write_fd) {
    // Ігноруємо SIGPIPE, щоб write() повернув EPIPE замість падіння процесу
    signal(SIGPIPE, SIG_IGN);

    const char *msg = "Data packet\n";
    if (write(write_fd, msg, 12) == -1) {
        if (errno == EPIPE) {
            fprintf(stderr, "Reader closed the pipe! Stop writing.\n");
        }
    }
}
