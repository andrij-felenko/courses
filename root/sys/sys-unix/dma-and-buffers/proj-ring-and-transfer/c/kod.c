// SPDX-License-Identifier: GPL-2.0
#include <linux/bits.h>
#include <linux/dma-mapping.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/kernel.h>
#include <linux/scatterlist.h>
#include <linux/spinlock.h>

#define RING_LEN     256u          /* степінь двійки — щоб обгортати маскою */
#define DESC_OWN     BIT(31)       /* 1 — дескриптор у пристрою */
#define DESC_EOR     BIT(30)       /* останній сегмент запиту */
#define DESC_ERR     BIT(29)       /* пристрій виставив помилку */

#define REG_RING_LO  0x00
#define REG_RING_HI  0x04
#define REG_TAIL     0x08
#define REG_IRQ_ACK  0x10

/* Так дескриптор бачить контролер: 16 байтів у ЙОГО порядку байтів. */
struct hw_desc {
        __le64 addr;
        __le32 len;
        __le32 flags;
};

/* Одна передача з погляду драйвера. */
struct xfer {
        struct sg_table        *sgt;
        enum dma_data_direction dir;      /* запам'ятали при map — знімемо тим самим */
        void (*done)(struct xfer *x, int err);
};

struct engine {
        struct device  *dev;
        void __iomem   *regs;

        struct hw_desc *ring;             /* узгоджена пам'ять: спільна з пристроєм */
        dma_addr_t      ring_dma;

        struct xfer    *owner[RING_LEN];  /* звичайна пам'ять ядра: чий це слот */
        unsigned int    tail;             /* куди пише драйвер */
        unsigned int    head;             /* звідки забирає завершені */
        spinlock_t      lock;
};
