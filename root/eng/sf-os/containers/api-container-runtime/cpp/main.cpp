#include <cstdlib>
#include <fcntl.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <string_view>
#include <system_error>

/* Відкриття ведучого пристрою PTY Master */
int master_fd = ::posix_openpt(O_RDWR | O_NOCTTY | O_CLOEXEC);
if (master_fd < 0) {
    throw std::system_error(errno, std::generic_category(), "posix_openpt failed");
}

/* Налаштування прав та розблокування Slave PTY */
::grantpt(master_fd);
::unlockpt(master_fd);

/* Отримання шляху до веденого вузла */
std::string_view slave_path = ::ptsname(master_fd);
