#include <sys/uio.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/fs.h>   /* RWF_HIPRI */

int fd = open("/dev/nvme0n1", O_RDONLY | O_DIRECT);
struct iovec iov = { .iov_base = buf, .iov_len = 4096 };

/* Системний виклик блокує потік, виконуючи spin loop у ядрі */
ssize_t nread = preadv2(fd, &iov, 1, offset, RWF_HIPRI);
