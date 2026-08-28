/* pinbufctl.c — простір користувача */
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>
#include "pinbuf.h"

static void show_pins(const char *when)
{
        FILE *f = fopen("/proc/vmstat", "r");
        char name[64];
        unsigned long long v;

        printf("%-16s", when);
        while (fscanf(f, "%63s %llu", name, &v) == 2)
                if (!strncmp(name, "nr_foll_pin_", 12))
                        printf(" %s=%llu", name, v);
        putchar('\n');
        fclose(f);
}

int main(void)
{
        int fd = open("/dev/pinbuf", O_RDWR);
        if (fd < 0) { perror("open /dev/pinbuf"); return 1; }

        void *base;
        if (posix_memalign(&base, 4096, 16384)) return 1;
        memset(base, 1, 16384);

        unsigned char *p = (unsigned char *)base + 13;   /* навмисно не з краю */
        struct pinbuf_req r = { .addr = (uintptr_t)p, .len = 8500 };

        show_pins("до");
        if (ioctl(fd, PINBUF_XFER, &r) < 0) { perror("XFER"); return 1; }
        printf("сума %llu, сторінок %u, сегментів %u, перший байт 0x%02x\n",
               (unsigned long long)r.sum, r.pages, r.segs, p[0]);
        show_pins("після");

        /* Ділянка лише для читання: FOLL_WRITE не має що з нею робити. */
        void *ro = mmap(NULL, 4096, PROT_READ, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        struct pinbuf_req r2 = { .addr = (uintptr_t)ro, .len = 4096 };
        if (ioctl(fd, PINBUF_XFER, &r2) < 0)
                printf("лише для читання: %s\n", strerror(errno));

        /* Часткова вдача: просимо дві сторінки, друга не відображена. */
        unsigned char *two = mmap(NULL, 8192, PROT_READ | PROT_WRITE,
                                  MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        munmap(two + 4096, 4096);
        struct pinbuf_req r3 = { .addr = (uintptr_t)two, .len = 8192 };
        if (ioctl(fd, PINBUF_XFER, &r3) < 0)
                printf("часткова вдача: %s\n", strerror(errno));
        show_pins("після часткової");

        close(fd);
        return 0;
}
