#include <sys/ioctl.h>
#include <linux/fs.h>
#include <cerrno>
#include <system_error>

// Повертає true, якщо блоки поділено; false — якщо ФС не підтримує reflink.
// При справжній помилці кидає std::system_error.
bool try_clone(int dest_fd, int src_fd)
{
    if (::ioctl(dest_fd, FICLONE, src_fd) == 0) {
        return true;
    }
    if (errno == EOPNOTSUPP || errno == EINVAL || errno == EXDEV) {
        return false;
    }
    throw std::system_error(errno, std::generic_category(), "FICLONE ioctl failed");
}
