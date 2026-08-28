/* pulsectl.c — простір користувача */
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include "pulsegen.h"

int main(void)
{
        int fd = open("/dev/pulsegen", O_RDWR);
        if (fd < 0) { perror("open /dev/pulsegen"); return 1; }

        struct pulse_cfg c = { .period_us = 2500, .duty_permille = 300 };
        if (ioctl(fd, PULSE_SET_CFG, &c) < 0) { perror("SET_CFG"); return 1; }

        memset(&c, 0, sizeof(c));
        if (ioctl(fd, PULSE_GET_CFG, &c) < 0) { perror("GET_CFG"); return 1; }
        printf("період %u мкс, заповнення %u‰\n", c.period_us, c.duty_permille);

        struct pulse_burst b = { .want = 64 };   /* решта полів — нулі */
        if (ioctl(fd, PULSE_BURST, &b) < 0) { perror("BURST"); return 1; }
        printf("видано %u, усього %llu\n", b.want, (unsigned long long)b.issued);

        if (ioctl(fd, _IO('Z', 0), 0) < 0)       /* команда чужої підсистеми */
                printf("чужа команда: %s\n", strerror(errno));

        close(fd);
        return 0;
}
