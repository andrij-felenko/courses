/* reader.c — коли саме ядро складає текст? */
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

static void dump(const char *tag, int fd)
{
    char buf[8192];
    lseek(fd, 0, SEEK_SET);                  /* почати вміст спочатку */
    ssize_t n = read(fd, buf, sizeof buf);
    if (n <= 0)
        return;                              /* помилка або порожньо — друкувати нічого */
    printf("--- %s ---\n%.*s", tag, (int)n, buf);
}

int main(void)
{
    int fd = open("/proc/heartbeat", O_RDONLY);
    dump("одразу після open", fd);
    sleep(3);
    dump("через три секунди, той самий дескриптор", fd);
    close(fd);
    return 0;
}
