// SPDX-License-Identifier: GPL-2.0
#include <linux/dma-mapping.h>
#include <linux/miscdevice.h>
#include <linux/mm.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/of_reserved_mem.h>
#include <linux/platform_device.h>

#define VDEC_BUF_SIZE  (24u << 20)             /* 8 кадрів 1920×1088 NV12 */
#define VDEC_ATTRS     DMA_ATTR_FORCE_CONTIGUOUS

struct vdec {
        struct device     *dev;
        struct miscdevice  misc;

        struct mutex       lock;                /* захищає все нижче */
        unsigned int       refs;                /* відкриття + живі відображення */
        void              *cpu;                 /* адреса буфера в ядрі */
        dma_addr_t         dma;                 /* та сама пам'ять очима пристрою */
};

static const struct file_operations vdec_fops;  /* тіло — наприкінці файла */
