/* Типовий код "годування собаки" у просторі користувача 1990-х (C/POSIX) */
#include <fcntl.h>
#include <unistd.h>

int main(void) {
    int fd = open("/dev/watchdog", O_WRONLY);
    if (fd < 0) return 1;
    while (1) {
        write(fd, "\0", 1);
        sleep(10);
    }
    close(fd);
    return 0;
}
