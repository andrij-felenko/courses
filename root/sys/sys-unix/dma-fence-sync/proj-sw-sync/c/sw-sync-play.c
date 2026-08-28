/* sw-sync-play.c — огорожі руками, без жодного GPU.
 * Потрібні: ядро з CONFIG_SW_SYNC=y, змонтований debugfs, права root.
 * Збірка:   cc -O2 -Wall -o sw-sync-play sw-sync-play.c
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
#include <linux/types.h>
#include <linux/sync_file.h>   /* SYNC_IOC_MERGE, SYNC_IOC_FILE_INFO — це uapi */

/* А це — переписане з drivers/dma-buf/sw_sync.c: у заголовках його немає. */
struct sw_sync_create_fence_data {
        __u32 value;
        char  name[32];
        __s32 fence;           /* сюди ядро покладе дескриптор огорожі */
};
#define SW_SYNC_IOC_MAGIC        'W'
#define SW_SYNC_IOC_CREATE_FENCE _IOWR(SW_SYNC_IOC_MAGIC, 0, \
                                       struct sw_sync_create_fence_data)
#define SW_SYNC_IOC_INC          _IOW(SW_SYNC_IOC_MAGIC, 1, __u32)

#define SW_SYNC_PATH "/sys/kernel/debug/sync/sw_sync"

static void die(const char *what)
{
        fprintf(stderr, "%s: %s\n", what, strerror(errno));
        exit(1);
}

/* нова шкала: власний лічильник із нуля, власний контекст огорож */
static int timeline_open(void)
{
        int fd = open(SW_SYNC_PATH, O_RDWR);
        if (fd < 0)
                die("open " SW_SYNC_PATH " (CONFIG_SW_SYNC? debugfs? root?)");
        return fd;
}

/* огорожа, що впаде, коли лічильник шкали дійде до value */
static int fence_create(int timeline, unsigned value)
{
        struct sw_sync_create_fence_data d;

        memset(&d, 0, sizeof d);
        d.value = value;
        if (ioctl(timeline, SW_SYNC_IOC_CREATE_FENCE, &d) < 0)
                die("CREATE_FENCE");
        return d.fence;
}

/* ЗСУВ лічильника, не нове його значення */
static void timeline_inc(int timeline, unsigned by)
{
        if (ioctl(timeline, SW_SYNC_IOC_INC, &by) < 0)
                die("INC");
}

/* стан огорожі без засинання: 1 — спрацювала, 0 — ще ні */
static int fence_ready(int fence_fd)
{
        struct pollfd p = { .fd = fence_fd, .events = POLLIN };
        int n = poll(&p, 1, 0);          /* нульове очікування — лише знімок */

        if (n < 0)
                die("poll");
        return n > 0 && (p.revents & POLLIN);
}

static int fence_merge(const char *name, int a, int b)
{
        struct sync_merge_data d;

        memset(&d, 0, sizeof d);
        strncpy(d.name, name, sizeof d.name - 1);
        d.fd2 = b;
        if (ioctl(a, SYNC_IOC_MERGE, &d) < 0)
                die("MERGE");
        return d.fence;                  /* новий дескриптор; a і b живі далі */
}

/* скільки огорож усередині дескриптора і в якому вони стані */
static void fence_info(const char *tag, int fence_fd)
{
        struct sync_fence_info *fences;
        struct sync_file_info info;
        unsigned i;

        memset(&info, 0, sizeof info);   /* num_fences = 0 — питаємо лише кількість */
        if (ioctl(fence_fd, SYNC_IOC_FILE_INFO, &info) < 0)
                die("FILE_INFO (лічба)");

        fences = calloc(info.num_fences, sizeof *fences);
        if (!fences)
                die("calloc");
        info.sync_fence_info = (__u64)(uintptr_t)fences;
        if (ioctl(fence_fd, SYNC_IOC_FILE_INFO, &info) < 0)
                die("FILE_INFO (дані)");

        printf("%-14s «%s», стан %d, огорож усередині: %u\n",
               tag, info.name, info.status, info.num_fences);
        for (i = 0; i < info.num_fences; i++)
                printf("               %s/%s стан %d\n", fences[i].driver_name,
                       fences[i].obj_name, fences[i].status);
        free(fences);
}
