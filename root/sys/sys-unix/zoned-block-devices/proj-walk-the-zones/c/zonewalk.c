/* zonewalk.c — обхід зон зонованого пристрою і три досліди над вказівником.
   збірка:  cc -O2 -Wall -Wextra -D_FILE_OFFSET_BITS=64 -o zonewalk zonewalk.c
   запуск:  sudo ./zonewalk /dev/nullb0            — лише таблиця
            sudo ./zonewalk /dev/nullb0 --write    — таблиця й досліди (ПИШЕ!) */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/blkzoned.h>
#include <linux/fs.h>

#define SECT  512u   /* про зони ядро звітує в 512-байтових секторах — завжди */
#define BATCH 64u    /* скільки зон просити одним звітом: рівно 4 КіБ описів */

static const char *type_name(unsigned t)
{
    switch (t) {
    case BLK_ZONE_TYPE_CONVENTIONAL:  return "звичайна";
    case BLK_ZONE_TYPE_SEQWRITE_REQ:  return "послідовна";
    case BLK_ZONE_TYPE_SEQWRITE_PREF: return "послідовна (м'яка)";
    default:                          return "?";
    }
}

static const char *cond_name(unsigned c)
{
    switch (c) {
    case BLK_ZONE_COND_NOT_WP:   return "без вказівника";
    case BLK_ZONE_COND_EMPTY:    return "порожня";
    case BLK_ZONE_COND_IMP_OPEN: return "відкрита неявно";
    case BLK_ZONE_COND_EXP_OPEN: return "відкрита явно";
    case BLK_ZONE_COND_CLOSED:   return "закрита";
    case BLK_ZONE_COND_READONLY: return "лише читання";
    case BLK_ZONE_COND_FULL:     return "повна";
    case BLK_ZONE_COND_OFFLINE:  return "відключена";
    default:                     return "?";
    }
}

/* Буфер під звіт: шапка плюс місце під n описів зон. */
static struct blk_zone_report *rep_alloc(unsigned n)
{
    struct blk_zone_report *r =
        calloc(1, sizeof(*r) + (size_t)n * sizeof(struct blk_zone));

    if (!r) { perror("calloc"); exit(1); }
    return r;
}

/* Звіт починаючи з сектора from. Драйвер має право віддати МЕНШЕ зон, ніж
   просили, і переписує nr_zones фактичною кількістю — саме її й повертаємо. */
static unsigned zones_report(int fd, uint64_t from, unsigned want,
                             struct blk_zone_report *r)
{
    r->sector = from;
    r->nr_zones = want;
    r->flags = 0;
    if (ioctl(fd, BLKREPORTZONE, r) < 0) { perror("BLKREPORTZONE"); exit(1); }
    return r->nr_zones;
}

/* Свіжий опис однієї зони — тієї, якій належить сектор sector. */
static struct blk_zone zone_at(int fd, uint64_t sector)
{
    struct blk_zone_report *r = rep_alloc(1);
    struct blk_zone z;

    if (zones_report(fd, sector, 1, r) != 1) {
        fprintf(stderr, "звіту про зону при секторі %llu немає\n",
                (unsigned long long)sector);
        exit(1);
    }
    z = r->zones[0];
    free(r);
    return z;
}
