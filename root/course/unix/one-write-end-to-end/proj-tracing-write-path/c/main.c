#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    const char *path = "/tmp/trace_test.dat";
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    char buffer[4096];
    memset(buffer, 'A', sizeof(buffer));

    printf("PID: %d | Виконуємо write()...\n", getpid());
    ssize_t written = write(fd, buffer, sizeof(buffer));
    if (written < 0) {
        perror("write");
        close(fd);
        return 1;
    }

    printf("Записано %zd байтів у Page Cache. Очікування 2 секунди...\n", written);
    sleep(2);

    printf("Виконуємо fdatasync()...\n");
    if (fdatasync(fd) < 0) {
        perror("fdatasync");
        close(fd);
        return 1;
    }

    printf("Синхронізацію завершено. Закриваємо файл.\n");
    close(fd);
    unlink(path);
    return 0;
}
