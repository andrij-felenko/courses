#include <sys/uio.h>

struct iovec {
    void  *iov_base;    /* Початкова адреса буфера в пам'яті */
    size_t iov_len;     /* Довжина буфера в байтах */
};

ssize_t readv(int fd, const struct iovec *iov, int iovcnt);
ssize_t writev(int fd, const struct iovec *iov, int iovcnt);

ssize_t preadv2(int fd, const struct iovec *iov, int iovcnt,
                off_t offset, int flags);
ssize_t pwritev2(int fd, const struct iovec *iov, int iovcnt,
                 off_t offset, int flags);
