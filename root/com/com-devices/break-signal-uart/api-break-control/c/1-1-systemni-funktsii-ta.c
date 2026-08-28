/* Системні виклики керування сигналом Break на мові C */
#include <termios.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* Відправка нормованого імпульсу Break */
int tcsendbreak(int fd, int duration);

/* Низькорівневе пряме увімкнення та вимкнення стану розриву */
int ioctl_set_break(int fd) {
    return ioctl(fd, TIOCSBRK);
}

int ioctl_clear_break(int fd) {
    return ioctl(fd, TIOCCBRK);
}
