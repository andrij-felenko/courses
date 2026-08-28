#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <linux/dm-ioctl.h>

static char buf[16 * 1024];

static struct dm_ioctl *hdr(const char *name)
{
        struct dm_ioctl *p = (struct dm_ioctl *) buf;

        memset(buf, 0, sizeof buf);
        p->version[0] = DM_VERSION_MAJOR;   /* ядро впише свою й поверне */
        p->version[1] = DM_VERSION_MINOR;
        p->version[2] = DM_VERSION_PATCHLEVEL;
        p->data_size  = sizeof buf;
        p->data_start = sizeof *p;          /* 312 — уже кратне восьми */
        strncpy(p->name, name, DM_NAME_LEN - 1);
        return p;
}

int main(void)
{
        int fd = open("/dev/mapper/control", O_RDWR);
        if (fd < 0) { perror("open"); return 1; }

        /* 1. порожній пристрій: з'являється /dev/dm-N зі своєю парою номерів */
        if (ioctl(fd, DM_DEV_CREATE, hdr("demo")) < 0) { perror("CREATE"); return 1; }

        /* 2. таблиця з одного відрізка — лягає НЕАКТИВНОЮ */
        struct dm_ioctl *p = hdr("demo");
        p->target_count = 1;

        struct dm_target_spec *ts = (struct dm_target_spec *) (buf + p->data_start);
        ts->sector_start = 0;
        ts->length       = 2048;                       /* 1 МіБ у секторах по 512 */
        strcpy(ts->target_type, "linear");

        char *args = (char *) (ts + 1);
        strcpy(args, "/dev/loop0 0");
        unsigned n = strlen(args) + 1;      /* разом із нульовим байтом */
        n = (n + 7) & ~7u;                  /* доповнення до кратності восьми */
        ts->next     = sizeof *ts + n;
        p->data_size = p->data_start + ts->next;

        if (ioctl(fd, DM_TABLE_LOAD, p) < 0) { perror("LOAD"); return 1; }

        /* 3. поновлення: DM_SUSPEND_FLAG ЗНЯТО — неактивна таблиця стає живою */
        if (ioctl(fd, DM_DEV_SUSPEND, hdr("demo")) < 0) { perror("RESUME"); return 1; }

        close(fd);
        return 0;
}
