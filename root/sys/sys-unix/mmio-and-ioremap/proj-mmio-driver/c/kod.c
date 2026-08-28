// SPDX-License-Identifier: GPL-2.0
#include <linux/clk.h>
#include <linux/dma-mapping.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/ktime.h>
#include <linux/module.h>
#include <linux/platform_device.h>

#define REG_ID          0x000   /* лише читання: сигнатура блока   */
#define REG_CTRL        0x004
#define REG_IRQ_CAUSE   0x00c   /* запис одиниці скидає біт        */
#define REG_RING_LO     0x010
#define REG_RING_HI     0x014
#define REG_TX_KICK     0x018   /* дзвінок: тут — номер дескриптора */
#define REG_TX_DONE     0x01c

#define MYETH_ID        0x4d594554      /* 'MYET', якщо читати число зі старшого байта */
#define CTRL_ENABLE     BIT(0)
#define IRQ_TX_DONE     BIT(0)

#define RING_LEN        64
#define BUF_LEN         2048

struct tx_desc {
        __le64 addr;
        __le32 len;
        __le32 flags;
};
#define DESC_OWN        cpu_to_le32(BIT(31))

struct myeth {
        struct device  *dev;
        void __iomem   *regs;           /* адреса вікна для процесора */
        struct tx_desc *ring;           /* кільце: адреса для процесора */
        dma_addr_t      ring_dma;       /* кільце: адреса для пристрою  */
        void           *buf;
        dma_addr_t      buf_dma;
        unsigned int    head;
        unsigned int    entries;        /* входів у обробник */
        unsigned int    foreign;        /* з них не наших    */
        unsigned int    sent;           /* дзвінків          */
};

static unsigned int kicks;
module_param(kicks, uint, 0444);
MODULE_PARM_DESC(kicks, "скільки дескрипторів проштовхнути одразу після probe");

static unsigned int bench;
module_param(bench, uint, 0444);
MODULE_PARM_DESC(bench, "скільки читань регістра зробити для заміру");

/* ── гарячий шлях: дескриптор і дзвінок ─────────────────────────────── */

static void myeth_kick(struct myeth *p, dma_addr_t buf, u32 len)
{
        struct tx_desc *d = &p->ring[p->head];

        d->addr = cpu_to_le64(buf);
        d->len  = cpu_to_le32(len);
        /* Прапорець власності — останнім і окремо: до цього рядка
           дескриптор наш, після нього вже пристрою.                */
        d->flags = DESC_OWN;

        /* Бар'єра руками нема — його несе перший writel. Саме він
           гарантує, що три записи вище лягли раніше за дзвінок.    */
        writel(p->head, p->regs + REG_TX_KICK);

        p->head = (p->head + 1) % RING_LEN;
        p->sent++;
}

static irqreturn_t myeth_isr(int irq, void *data)
{
        struct myeth *p = data;
        u32 cause = readl(p->regs + REG_IRQ_CAUSE);

        p->entries++;
        if (!cause) {
                p->foreign++;
                return IRQ_NONE;        /* лінія спільна: озвався не наш блок */
        }

        if (cause & IRQ_TX_DONE)
                readl(p->regs + REG_TX_DONE);   /* тут звільняли б буфери */

        writel(cause, p->regs + REG_IRQ_CAUSE);
        readl(p->regs + REG_IRQ_CAUSE);         /* проштовхнути скидання */

        return IRQ_HANDLED;
}

/* ── замір ціни бар'єрів ────────────────────────────────────────────── */

static void myeth_bench(struct myeth *p, unsigned int n)
{
        unsigned long flags;
        ktime_t t0, t1, t2;
        unsigned int i;
        u32 sink = 0;

        /* Замір, а не робочий код: інакше цикл міряв би планувальник,
           а не шину. Переривання вимкнено на весь прохід, тож n беруть
           таким, щоб не вийти за пару десятків мілісекунд.      */
        local_irq_save(flags);

        t0 = ktime_get();
        for (i = 0; i < n; i++)
                sink += readl(p->regs + REG_ID);
        t1 = ktime_get();
        for (i = 0; i < n; i++)
                sink += readl_relaxed(p->regs + REG_ID);
        t2 = ktime_get();

        local_irq_restore(flags);

        dev_info(p->dev, "%u доступів: readl %lld нс, readl_relaxed %lld нс (сума %#x)\n",
                 n, ktime_to_ns(ktime_sub(t1, t0)),
                 ktime_to_ns(ktime_sub(t2, t1)), sink);
}

/* ── прив'язка ──────────────────────────────────────────────────────── */

static int myeth_probe(struct platform_device *pdev)
{
        struct device *dev = &pdev->dev;
        struct myeth *p;
        struct clk *clk;
        unsigned int i;
        int irq, ret;
        u32 id;

        p = devm_kzalloc(dev, sizeof(*p), GFP_KERNEL);
        if (!p)
                return -ENOMEM;
        p->dev = dev;
        platform_set_drvdata(pdev, p);

        /* Займає діапазон у /proc/iomem, відображає його й вішає
           звільнення на знищення пристрою.                        */
        p->regs = devm_platform_ioremap_resource(pdev, 0);
        if (IS_ERR(p->regs))
                return PTR_ERR(p->regs);

        /* Такт — ПЕРЕД першим читанням регістра, а не після. */
        clk = devm_clk_get_enabled(dev, NULL);
        if (IS_ERR(clk))
                return dev_err_probe(dev, PTR_ERR(clk), "нема такту блока\n");

        id = readl(p->regs + REG_ID);
        if (id != MYETH_ID)
                return dev_err_probe(dev, -ENODEV,
                                     "сигнатура %#010x%s\n", id,
                                     id == 0xffffffff ? " — ніхто не озвався" : "");

        ret = dma_set_mask_and_coherent(dev, DMA_BIT_MASK(32));
        if (ret)
                return ret;

        p->ring = dmam_alloc_coherent(dev, RING_LEN * sizeof(*p->ring),
                                      &p->ring_dma, GFP_KERNEL);
        p->buf  = dmam_alloc_coherent(dev, BUF_LEN, &p->buf_dma, GFP_KERNEL);
        if (!p->ring || !p->buf)
                return -ENOMEM;

        writel(lower_32_bits(p->ring_dma), p->regs + REG_RING_LO);
        writel(upper_32_bits(p->ring_dma), p->regs + REG_RING_HI);

        irq = platform_get_irq(pdev, 0);
        if (irq < 0)
                return irq;

        /* Обробник реєструємо, поки пристрій ще мовчить: після
           наступного рядка переривання прилетить будь-якої миті. */
        ret = devm_request_irq(dev, irq, myeth_isr, IRQF_SHARED,
                               dev_name(dev), p);
        if (ret)
                return ret;

        writel(CTRL_ENABLE, p->regs + REG_CTRL);

        for (i = 0; i < kicks; i++)
                myeth_kick(p, p->buf_dma, 64);
        if (bench)
                myeth_bench(p, bench);

        dev_info(dev, "регістри %p, кільце %p / шинна %pad\n",
                 p->regs, p->ring, &p->ring_dma);
        return 0;
}

static void myeth_remove(struct platform_device *pdev)
{
        struct myeth *p = platform_get_drvdata(pdev);

        /* Порядок протилежний до probe, і в цьому вся суть: спершу
           глушимо джерело, і лише тоді devres знімає обробник.     */
        writel(0, p->regs + REG_CTRL);
        writel(~0u, p->regs + REG_IRQ_CAUSE);
        readl(p->regs + REG_IRQ_CAUSE);

        dev_info(p->dev, "дзвінків %u, входів у обробник %u, з них чужих %u\n",
                 p->sent, p->entries, p->foreign);
}

static const struct of_device_id myeth_of[] = {
        { .compatible = "example,myeth" },
        { }
};
MODULE_DEVICE_TABLE(of, myeth_of);

static struct platform_driver myeth_driver = {
        .probe  = myeth_probe,
        .remove = myeth_remove,
        .driver = {
                .name           = "myeth",
                .of_match_table = myeth_of,
        },
};
module_platform_driver(myeth_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Показовий платформний драйвер: ioremap, кільце, дзвінок");
