#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int create_basic_pipe(void) {
    int fds[2];
    
    // Створюємо канал: fds[0] - читання, fds[1] - запис
    if (pipe(fds) == -1) {
        perror("pipe failed");
        return -1;
    }
    
    printf("Read FD: %d, Write FD: %d\n", fds[0], fds[1]);
    return 0;
}
