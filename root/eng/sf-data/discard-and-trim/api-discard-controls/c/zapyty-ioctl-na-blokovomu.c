#include <linux/fs.h>     /* BLKDISCARD, BLKSECDISCARD, BLKZEROOUT */
#include <sys/ioctl.h>
#include <fcntl.h>
#include <stdint.h>

int fd = open("/dev/nvme0n1", O_WRONLY);        /* саме на запис */
uint64_t range[2] = { 1ULL << 30, 256ULL << 20 };   /* зсув 1 ГіБ, довжина 256 МіБ */

if (ioctl(fd, BLKDISCARD, range) < 0)
        perror("BLKDISCARD");
