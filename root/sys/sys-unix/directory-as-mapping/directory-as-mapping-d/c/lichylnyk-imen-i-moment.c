#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(void)
{
    int fd = open("/tmp/scratch", O_RDWR | O_CREAT | O_EXCL, 0600);
    if (fd < 0) { perror("open"); return 1; }

    /* Імені більше немає: у /tmp його не побачить ніхто, зокрема й ми самі. */
    if (unlink("/tmp/scratch") < 0) { perror("unlink"); return 1; }

    const char *msg = "дані живуть, доки живе дескриптор\n";
    write(fd, msg, strlen(msg));

    char buf[64] = {0};
    lseek(fd, 0, SEEK_SET);
    ssize_t n = read(fd, buf, sizeof buf - 1);
    printf("прочитано %zd байтів: %s", n, buf);

    close(fd);   /* аж тепер блоки звільняються */
    return 0;
}
