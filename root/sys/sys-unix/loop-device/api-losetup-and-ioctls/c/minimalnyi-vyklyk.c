#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/loop.h>

int main(void)
{
        int  ctl = open("/dev/loop-control", O_RDWR);
        int  n   = ioctl(ctl, LOOP_CTL_GET_FREE);   /* номер вільного пристрою */
        char path[32];
        snprintf(path, sizeof path, "/dev/loop%d", n);

        int img = open("disk.img", O_RDWR);
        int dev = open(path, O_RDWR);

        struct loop_config cfg;
        memset(&cfg, 0, sizeof cfg);                /* __reserved і решта — нулі */
        cfg.fd             = img;
        cfg.block_size     = 4096;
        cfg.info.lo_offset = 1048576;               /* початок першого розділу */
        cfg.info.lo_flags  = LO_FLAGS_AUTOCLEAR | LO_FLAGS_PARTSCAN;

        if (ioctl(dev, LOOP_CONFIGURE, &cfg) < 0)
                perror("LOOP_CONFIGURE");

        close(img);                                 /* ядро тримає власне посилання */
        /* … робота з /dev/loopN … */

        ioctl(dev, LOOP_CLR_FD, 0);
        close(dev);
        close(ctl);
        return 0;
}
