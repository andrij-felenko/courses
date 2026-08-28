/* Системна перевірка дескриптора на належність до термінала мовою C */
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <errno.h>

int check_descriptor_is_tty(int fd) {
    struct termios t;
    if (ioctl(fd, TCGETS, &t) == 0) {
        return 1; /* Дескриптор вказує на активний TTY */
    }
    if (errno == ENOTTY) {
        return 0; /* Дескриптор вказує на pipe, регулярний файл або сокет */
    }
    return -1; /* Помилка EBADF (недійсний дескриптор) */
}
