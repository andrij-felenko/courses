#define _XOPEN_SOURCE 600
#include <stdlib.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/ioctl.h>

/* Відкриття ведучого пристрою PTY Master */
int master_fd = posix_openpt(O_RDWR | O_NOCTTY | O_CLOEXEC);

/* Налаштування прав та розблокування Slave PTY */
grantpt(master_fd);
unlockpt(master_fd);

/* Отримання шляху до веденого вузла (наприклад, /dev/pts/3) */
char *slave_path = ptsname(master_fd);
