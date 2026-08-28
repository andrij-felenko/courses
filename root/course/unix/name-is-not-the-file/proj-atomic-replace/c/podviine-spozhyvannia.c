#include <sys/ioctl.h>
#include <linux/fs.h>
#include <fcntl.h>
#include <unistd.h>

/* Швидке клонування метаданих без дублювання фізичних блоків даних (CoW) */
int clone_file_blocks(int src_fd, int dest_fd) {
    if (ioctl(dest_fd, FICLONE, src_fd) < 0) {
        return -1; /* ФС не підтримує reflink */
    }
    return 0;
}
