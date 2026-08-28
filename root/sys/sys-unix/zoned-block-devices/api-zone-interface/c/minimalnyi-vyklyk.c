#include <linux/blkzoned.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>

int fd = open("/dev/nullb0", O_RDWR);      /* керуючі запити вимагають запису */

__u32 zone_sectors, zone_count;
ioctl(fd, BLKGETZONESZ,  &zone_sectors);
ioctl(fd, BLKGETNRZONES, &zone_count);

/* буфер = шапка плюс стільки описів, скільки хочемо дістати за раз */
const __u32 want = 8;
struct blk_zone_report *rep = malloc(sizeof(*rep) + want * sizeof(struct blk_zone));

rep->sector   = 0;                         /* обхід від початку пристрою */
rep->nr_zones = want;
rep->flags    = 0;

if (ioctl(fd, BLKREPORTZONE, rep) == 0) {
        int cap_ok = rep->flags & BLK_ZONE_REP_CAPACITY;

        for (__u32 i = 0; i < rep->nr_zones; i++) {      /* уже СКІЛЬКИ віддали */
                struct blk_zone *z = &rep->zones[i];

                printf("%llu: тип=%#x стан=%#x зайнято=%llu придатно=%llu\n",
                       z->start, z->type, z->cond,
                       z->wp - z->start,
                       cap_ok ? z->capacity : z->len);
        }
}

/* скинути другу зону */
struct blk_zone_range r = { .sector = zone_sectors, .nr_sectors = zone_sectors };
ioctl(fd, BLKRESETZONE, &r);
