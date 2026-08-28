#include <fcntl.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/input.h>

#define NLONGS(n)     (((n) + 8 * sizeof(long) - 1) / (8 * sizeof(long)))
#define TESTBIT(a, b) ((a)[(b) / (8 * sizeof(long))] >> ((b) % (8 * sizeof(long))) & 1)

int main(void)
{
    int fd = open("/dev/input/event0", O_RDONLY | O_NONBLOCK);
    if (fd < 0) { perror("open"); return 1; }

    int clk = CLOCK_MONOTONIC;
    ioctl(fd, EVIOCSCLOCKID, &clk);          /* доки черга ще порожня */

    char name[256] = "";
    ioctl(fd, EVIOCGNAME(sizeof name - 1), name);

    unsigned long types[NLONGS(EV_CNT)] = {0};
    ioctl(fd, EVIOCGBIT(0, sizeof types), types);

    printf("%s:%s%s%s\n", name,
           TESTBIT(types, EV_KEY) ? " клавіші"   : "",
           TESTBIT(types, EV_REL) ? " відносні"  : "",
           TESTBIT(types, EV_ABS) ? " абсолютні" : "");

    if (TESTBIT(types, EV_ABS)) {
        struct input_absinfo abs;
        if (ioctl(fd, EVIOCGABS(ABS_X), &abs) == 0)
            printf("ABS_X: %d..%d, шум %d, %d одиниць на мм\n",
                   abs.minimum, abs.maximum, abs.fuzz, abs.resolution);
    }

    close(fd);
    return 0;
}
