#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>

// Переміщує байти між файловим дескриптором та каналом без копіювання
ssize_t splice(int fd_in, loff_t *off_in, int fd_out, loff_t *off_out, size_t len, unsigned int flags);

// Дублює байти з одного каналу у інший без їхнього видалення з першого
ssize_t tee(int fd_in, int fd_out, size_t len, unsigned int flags);

// Мапить сторінки пам'яті користувача безпосередньо у буфер каналу
ssize_t vmsplice(int fd, const struct iovec *iov, unsigned long nr_segs, unsigned int flags);
