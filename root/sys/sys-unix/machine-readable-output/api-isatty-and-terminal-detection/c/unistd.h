/* Сигнатури інтерфейсів термінала мовою C */
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>

int isatty(int fd);
char *ttyname(int fd);
int ttyname_r(int fd, char *buf, size_t buflen);
int tcgetattr(int fd, struct termios *termios_p);
int tcsetattr(int fd, int optional_actions, const struct termios *termios_p);
int ioctl(int fd, unsigned long request, ...);
