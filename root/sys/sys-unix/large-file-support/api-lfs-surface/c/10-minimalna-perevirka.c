#include <stdio.h>
#include <inttypes.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

int main(int argc, char **argv)
{
    printf("sizeof(off_t) = %zu\n", sizeof(off_t));

    if (argc < 2)
        return 0;

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "open: %s (errno %d)\n", strerror(errno), errno);
        return 1;                     /* тут і буде EOVERFLOW = 75 */
    }

    off_t end = lseek(fd, 0, SEEK_END);
    if (end == (off_t)-1) {
        fprintf(stderr, "lseek: %s (errno %d)\n", strerror(errno), errno);
        close(fd);
        return 1;
    }

    /* у власний вивід — явна ширина, а не off_t */
    printf("розмір у байтах = %" PRId64 "\n", (int64_t)end);
    close(fd);
    return 0;
}
