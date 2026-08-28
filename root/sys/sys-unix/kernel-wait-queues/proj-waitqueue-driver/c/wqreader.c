/* wqreader.c — блокувальне читання по одному байту */
#include <fcntl.h>
#include <unistd.h>

int main(void)
{
    int fd = open("/dev/wqdemo", O_RDONLY);
    char b;

    if (fd < 0) return 1;
    while (read(fd, &b, 1) > 0)
        ;
    return 0;
}
