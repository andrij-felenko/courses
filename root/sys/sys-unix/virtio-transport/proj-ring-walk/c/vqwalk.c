/* vqwalk.c — обидва боки розділеної віртчерги над спільною пам'яттю.
 * gcc -O2 -Wall -Wextra -pthread vqwalk.c -o vqwalk                       */
#define _GNU_SOURCE
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/eventfd.h>

#define QSZ      8u                 /* розмір черги — степінь двійки */
#define QMASK    (QSZ - 1u)
#define NO_LINK  0xffffu            /* кінець списку вільних ланок   */

#define DESC_F_NEXT   1u
#define DESC_F_WRITE  2u

struct vring_desc {                 /* рівно 16 байтів */
        uint64_t addr;              /* зсув від початку ділянки, НЕ покажчик */
        uint32_t len;
        uint16_t flags;
        uint16_t next;
};

struct vring_avail {                /* усе, крім used_event, пише драйвер */
        _Atomic uint16_t flags;
        _Atomic uint16_t idx;
        _Atomic uint16_t ring[QSZ];
        _Atomic uint16_t used_event;   /* сюди пише ПРИСТРІЙ */
};

struct vring_used_elem { uint32_t id; uint32_t len; };

struct vring_used {                 /* усе, крім avail_event, пише пристрій */
        _Atomic uint16_t flags;
        _Atomic uint16_t idx;
        struct vring_used_elem ring[QSZ];
        _Atomic uint16_t avail_event;  /* сюди пише ДРАЙВЕР */
};

#define DESC_BYTES   (16u * QSZ)
#define AVAIL_BYTES  (6u + 2u * QSZ)
#define USED_BYTES   (6u + 8u * QSZ)

_Static_assert(sizeof(struct vring_desc) == 16, "ланка мусить бути рівно 16 Б");
_Static_assert(sizeof(struct vring_avail) == AVAIL_BYTES, "розкладка avail поїхала");
_Static_assert(offsetof(struct vring_used, avail_event) == USED_BYTES - 2u, "позначка не там");

#define ALIGN_UP(x, a)  (((x) + (a) - 1u) & ~((size_t)(a) - 1u))

#define DESC_OFF   0u
#define AVAIL_OFF  ALIGN_UP(DESC_OFF + DESC_BYTES, 2)    /* = 128 */
#define USED_OFF   ALIGN_UP(AVAIL_OFF + AVAIL_BYTES, 64) /* = 192, спека вимагає лише 4 */
#define POOL_OFF   ALIGN_UP(USED_OFF + USED_BYTES, 64)   /* = 320 */
#define SLOT       512u                                  /* буфери одного прохання */
#define REGION     (1u << 20)

struct side {
        uint8_t            *base;
        struct vring_desc  *desc;
        struct vring_avail *avail;
        struct vring_used  *used;
        int kickfd, callfd;
};

static _Noreturn void die(const char *m) { fprintf(stderr, "%s\n", m); abort(); }

static void vring_place(struct side *s, void *base)
{
        s->base  = base;
        s->desc  = (struct vring_desc  *)((uint8_t *)base + DESC_OFF);
        s->avail = (struct vring_avail *)((uint8_t *)base + AVAIL_OFF);
        s->used  = (struct vring_used  *)((uint8_t *)base + USED_OFF);
}

static void *xlate(const struct side *s, uint64_t off, uint32_t len)
{
        if (off > REGION || len > REGION - off)
                return NULL;                  /* адреса поза ділянкою — відмова */
        return s->base + off;
}
