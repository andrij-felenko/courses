#include <sys/uio.h>
#include <fcntl.h>
#include <unistd.h>
#include <span>
#include <system_error>
#include <linux/fs.h>   // RWF_HIPRI

int fd = ::open("/dev/nvme0n1", O_RDONLY | O_DIRECT);
struct iovec iov { .iov_base = buf, .iov_len = 4096 };

ssize_t nread = ::preadv2(fd, &iov, 1, offset, RWF_HIPRI);
if (nread < 0) {
    throw std::system_error(errno, std::generic_category(), "Помилка preadv2 HIPRI");
}
