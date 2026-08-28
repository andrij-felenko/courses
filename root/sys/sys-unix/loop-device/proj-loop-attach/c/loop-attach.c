// loop-attach.c — те, що робить losetup, власними руками.
// збірка:  cc -O2 -Wall -Wextra -o loop-attach loop-attach.c
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/loop.h>

#define TRIES     16          /* стільки ж спроб робить losetup */
#define PAUSE_NS  25000000L   /* 25 мс між ними */

struct attach_req {
    int         fd_img;      /* уже відкритий образ */
    const char *img_path;    /* лише напис у lo_file_name, ядро ним не користується */
    uint64_t    offset;      /* байтів від початку файлу до сектора 0 */
    uint64_t    sizelimit;   /* 0 — до кінця файлу */
    uint32_t    block_size;  /* 0 — типовий; інакше степінь двійки,
                                від 512 до розміру сторінки (на x86 — 4096) */
    int         direct_io;   /* прохання працювати повз кеш сторінок господаря */
};

static void pause_a_bit(void)
{
    struct timespec ts = { 0, PAUSE_NS };
    nanosleep(&ts, NULL);
}

/* Вузол у /dev створює devtmpfs, права доводить udev — між поверненням
   номера й придатним вузлом є вікно. O_RDWR обов'язковий: пристрій,
   відкритий лише на читання, ядро зробить захищеним від запису. */
static int open_loop_node(int n)
{
    char path[32];
    snprintf(path, sizeof path, "/dev/loop%d", n);
    for (int i = 0; i < TRIES; i++) {
        int fd = open(path, O_RDWR | O_CLOEXEC);
        if (fd >= 0)
            return fd;
        if (errno != ENOENT && errno != EACCES)
            return -1;
        pause_a_bit();
    }
    errno = ETIMEDOUT;
    return -1;
}

/* Повертає дескриптор налаштованого пристрою, номер кладе в *out_n. */
static int loop_attach(int fd_ctl, const struct attach_req *r, int *out_n)
{
    for (int attempt = 0; attempt < TRIES; attempt++) {
        int n = ioctl(fd_ctl, LOOP_CTL_GET_FREE);
        if (n < 0)
            return -1;

        int fd_dev = open_loop_node(n);
        if (fd_dev < 0)
            return -1;

        struct loop_config cfg;
        memset(&cfg, 0, sizeof cfg);
        cfg.fd                = (uint32_t) r->fd_img;
        cfg.block_size        = r->block_size;
        cfg.info.lo_offset    = r->offset;
        cfg.info.lo_sizelimit = r->sizelimit;
        if (r->direct_io)
            cfg.info.lo_flags |= LO_FLAGS_DIRECT_IO;
        snprintf((char *) cfg.info.lo_file_name, LO_NAME_SIZE, "%s", r->img_path);

        if (ioctl(fd_dev, LOOP_CONFIGURE, &cfg) == 0) {
            *out_n = n;
            return fd_dev;
        }

        int err = errno;
        close(fd_dev);
        if (err != EBUSY) {   /* EBUSY — номер перехопили; решта помилок фатальні */
            errno = err;
            return -1;
        }
    }
    errno = EBUSY;
    return -1;
}

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "вжиток: %s образ [зсув-у-байтах]\n", argv[0]);
        return 2;
    }
    struct attach_req r = {
        .img_path   = argv[1],
        .offset     = (argc > 2) ? strtoull(argv[2], NULL, 0) : 0,
        .sizelimit  = 0,
        .block_size = 512,
        .direct_io  = 1,
    };

    int fd_ctl = open("/dev/loop-control", O_RDWR | O_CLOEXEC);
    if (fd_ctl < 0) { perror("/dev/loop-control"); return 1; }

    r.fd_img = open(r.img_path, O_RDWR | O_CLOEXEC);
    if (r.fd_img < 0) { perror(r.img_path); return 1; }

    int n = -1;
    int fd_dev = loop_attach(fd_ctl, &r, &n);
    if (fd_dev < 0) { perror("LOOP_CONFIGURE"); return 1; }

    /* образ нам більше не потрібен: ядро тримає власне посилання на файл */
    close(r.fd_img);
    printf("/dev/loop%d ← %s, зсув %llu\n",
           n, r.img_path, (unsigned long long) r.offset);

    struct loop_info64 info;
    if (ioctl(fd_dev, LOOP_GET_STATUS64, &info) == 0)
        printf("прямий ввід-вивід: %s\n",
               (info.lo_flags & LO_FLAGS_DIRECT_IO) ? "увімкнено" : "ядро його зняло");

    unsigned char sec[512];
    if (pread(fd_dev, sec, sizeof sec, 0) == (ssize_t) sizeof sec) {
        for (int i = 0; i < 32; i++)
            printf("%02x%s", sec[i], (i % 16 == 15) ? "\n" : " ");
        printf("підпис 0x55aa наприкінці сектора: %s\n",
               (sec[510] == 0x55 && sec[511] == 0xaa) ? "є" : "немає");
    } else {
        perror("pread");
    }

    if (ioctl(fd_dev, LOOP_CLR_FD) < 0)
        perror("LOOP_CLR_FD");
    close(fd_dev);   /* прив'язка розпадається саме тут */
    close(fd_ctl);
    return 0;
}
