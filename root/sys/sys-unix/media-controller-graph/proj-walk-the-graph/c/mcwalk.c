/* mcwalk.c — прочитати граф, знайти тракт «сенсор → /dev/videoN», скласти його.
 * Збірка: cc -O2 -Wall -o mcwalk mcwalk.c
 * Запуск:  ./mcwalk /dev/media0 /dev/video0 1920 1080                          */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <linux/media.h>
#include <linux/media-bus-format.h>
#include <linux/v4l2-subdev.h>
#include <linux/videodev2.h>

static int xioctl(int fd, unsigned long req, void *arg)
{
    int r;
    do { r = ioctl(fd, req, arg); } while (r < 0 && errno == EINTR);
    return r;
}

static void *xcalloc(size_t n, size_t sz)
{
    void *p = calloc(n ? n : 1, sz);
    if (!p) { perror("calloc"); exit(1); }
    return p;
}

struct graph {
    struct media_v2_entity    *ent;  __u32 nent;
    struct media_v2_interface *itf;  __u32 nitf;
    struct media_v2_pad       *pad;  __u32 npad;
    struct media_v2_link      *lnk;  __u32 nlnk;
};

static int graph_read(int fd, struct graph *g)
{
    struct media_v2_topology t;

    for (int attempt = 0; attempt < 4; attempt++) {
        memset(&t, 0, sizeof t);
        if (xioctl(fd, MEDIA_IOC_G_TOPOLOGY, &t) < 0)   /* прохід 1: самі кількості */
            return -1;

        free(g->ent); free(g->itf); free(g->pad); free(g->lnk);
        g->nent = t.num_entities;   g->ent = xcalloc(g->nent, sizeof *g->ent);
        g->nitf = t.num_interfaces; g->itf = xcalloc(g->nitf, sizeof *g->itf);
        g->npad = t.num_pads;       g->pad = xcalloc(g->npad, sizeof *g->pad);
        g->nlnk = t.num_links;      g->lnk = xcalloc(g->nlnk, sizeof *g->lnk);

        t.ptr_entities   = (__u64)(uintptr_t)g->ent;
        t.ptr_interfaces = (__u64)(uintptr_t)g->itf;
        t.ptr_pads       = (__u64)(uintptr_t)g->pad;
        t.ptr_links      = (__u64)(uintptr_t)g->lnk;

        if (xioctl(fd, MEDIA_IOC_G_TOPOLOGY, &t) == 0)  /* прохід 2: масиви */
            return 0;
        if (errno != ENOSPC)         /* ENOSPC — граф змінився, читаємо його заново */
            return -1;
    }
    errno = ENOSPC;
    return -1;
}
