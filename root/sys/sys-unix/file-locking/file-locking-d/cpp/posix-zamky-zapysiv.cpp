#include <fcntl.h>
#include <system_error>

struct flock fl{};
fl.l_type   = F_WRLCK;   // F_RDLCK, F_WRLCK або F_UNLCK
fl.l_whence = SEEK_SET;  // від чого відлічувати l_start
fl.l_start  = 0;
fl.l_len    = 0;         // 0 — до кінця файлу

if (fcntl(fd, F_SETLKW, &fl) == -1) {
    throw std::system_error(errno, std::generic_category(), "fcntl F_SETLKW failed");
}
