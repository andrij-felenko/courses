// SPDX-License-Identifier: GPL-2.0
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/gpio/driver.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/of.h>
#include <linux/spinlock.h>

#define GPIO_DATA_IN   0x00  /* Читання поточного стану пінів */
#define GPIO_DIR       0x04  /* Напрямок: 0 — вхід, 1 — вихід */
#define GPIO_INT_MASK  0x08  /* Дозвіл переривань: 1 — дозволено */
#define GPIO_INT_STAT  0x0C  /* Статус: Write-1-to-Clear */
#define GPIO_INT_TYPE  0x10  /* Чутливість: 0 — рівень, 1 — фронт */

#define MY_GPIO_NR_PINS 32

struct my_gpio_chip {
    struct gpio_chip  gc;
    void __iomem     *base;
    raw_spinlock_t    lock;       /* Захист MMIO регістрів у hardirq */
    int               parent_irq; /* Системний номер батьківського GIC */
};

/* Заборона генерації переривання на контакті */
static void my_gpio_irq_mask(struct irq_data *d)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    irq_hw_number_t hwirq = irqd_to_hwirq(d);
    unsigned long flags;
    u32 mask;

    raw_spin_lock_irqsave(&chip->lock, flags);
    mask = readl_relaxed(chip->base + GPIO_INT_MASK);
    mask &= ~BIT(hwirq);
    writel_relaxed(mask, chip->base + GPIO_INT_MASK);
    raw_spin_unlock_irqrestore(&chip->lock, flags);
}

/* Дозвіл генерації переривання на контакті */
static void my_gpio_irq_unmask(struct irq_data *d)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    irq_hw_number_t hwirq = irqd_to_hwirq(d);
    unsigned long flags;
    u32 mask;

    raw_spin_lock_irqsave(&chip->lock, flags);
    mask = readl_relaxed(chip->base + GPIO_INT_MASK);
    mask |= BIT(hwirq);
    writel_relaxed(mask, chip->base + GPIO_INT_MASK);
    raw_spin_unlock_irqrestore(&chip->lock, flags);
}

/* Квитування спрацьовування: скидання прапорця в регістрі статусу */
static void my_gpio_irq_ack(struct irq_data *d)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    irq_hw_number_t hwirq = irqd_to_hwirq(d);

    /* Апаратне скидання біта записом 1 (Write-1-to-Clear) без блокування */
    writel_relaxed(BIT(hwirq), chip->base + GPIO_INT_STAT);
}

/* Програмування електричної чутливості лінії */
static int my_gpio_irq_set_type(struct irq_data *d, unsigned int type)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    irq_hw_number_t hwirq = irqd_to_hwirq(d);
    unsigned long flags;
    u32 reg_val;

    raw_spin_lock_irqsave(&chip->lock, flags);
    reg_val = readl_relaxed(chip->base + GPIO_INT_TYPE);

    if (type & IRQ_TYPE_EDGE_BOTH) {
        reg_val |= BIT(hwirq);  /* Режим фронту */
        irq_set_handler_locked(d, handle_edge_irq);
    } else if (type & IRQ_TYPE_LEVEL_MASK) {
        reg_val &= ~BIT(hwirq); /* Режим рівня */
        irq_set_handler_locked(d, handle_level_irq);
    } else {
        raw_spin_unlock_irqrestore(&chip->lock, flags);
        return -EINVAL;
    }

    writel_relaxed(reg_val, chip->base + GPIO_INT_TYPE);
    raw_spin_unlock_irqrestore(&chip->lock, flags);
    return 0;
}

/* Налаштування пробудження системи з режиму сну */
static int my_gpio_irq_set_wake(struct irq_data *d, unsigned int on)
{
    struct gpio_chip *gc = irq_data_get_irq_chip_data(d);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);

    /* Передаємо запит батьківському контролеру переривань */
    return irq_set_irq_wake(chip->parent_irq, on);
}

static const struct irq_chip my_gpio_irqchip = {
    .name         = "my-gpio-irq",
    .irq_mask     = my_gpio_irq_mask,
    .irq_unmask   = my_gpio_irq_unmask,
    .irq_ack      = my_gpio_irq_ack,
    .irq_set_type = my_gpio_irq_set_type,
    .irq_set_wake = my_gpio_irq_set_wake,
    .flags        = IRQCHIP_IMMUTABLE,
};

/* Батьківський каскадний демультиплексор */
static void my_gpio_irq_handler(struct irq_desc *desc)
{
    struct gpio_chip *gc = irq_desc_get_handler_data(desc);
    struct my_gpio_chip *chip = gpiochip_get_data(gc);
    struct irq_chip *parent_chip = irq_desc_get_chip(desc);
    unsigned long pending;
    int hwirq;

    chained_irq_enter(parent_chip, desc);

    /* Зчитуємо активні події, які не замасковані */
    pending = readl_relaxed(chip->base + GPIO_INT_STAT);
    pending &= readl_relaxed(chip->base + GPIO_INT_MASK);

    /* Викликаємо диспетчер для кожного активного піна */
    for_each_set_bit(hwirq, &pending, MY_GPIO_NR_PINS) {
        generic_handle_domain_irq(gc->irq.domain, hwirq);
    }

    chained_irq_exit(parent_chip, desc);
}

/* Зондування та ініціалізація периферійного пристрою */
static int my_gpio_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct my_gpio_chip *chip;
    struct gpio_irq_chip *girq;
    int ret;

    chip = devm_kzalloc(dev, sizeof(*chip), GFP_KERNEL);
    if (!chip)
        return -ENOMEM;

    chip->base = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(chip->base))
        return PTR_ERR(chip->base);

    chip->parent_irq = platform_get_irq(pdev, 0);
    if (chip->parent_irq < 0)
        return chip->parent_irq;

    raw_spin_lock_init(&chip->lock);

    /* Забороняємо всі переривання на старті та очищуємо старі прапорці */
    writel_relaxed(0x00000000, chip->base + GPIO_INT_MASK);
    writel_relaxed(0xFFFFFFFF, chip->base + GPIO_INT_STAT);

    /* Налаштування базових параметрів GPIO */
    chip->gc.label = dev_name(dev);
    chip->gc.base = -1;
    chip->gc.ngpio = MY_GPIO_NR_PINS;
    chip->gc.parent = dev;
    chip->gc.owner = THIS_MODULE;

    /* Інтеграція підсистеми переривань у gpiochip */
    girq = &chip->gc.irq;
    gpio_irq_chip_set_chip(girq, &my_gpio_irqchip);
    girq->parent_handler = my_gpio_irq_handler;
    girq->num_parents = 1;
    girq->parents = devm_kcalloc(dev, 1, sizeof(*girq->parents), GFP_KERNEL);
    if (!girq->parents)
        return -ENOMEM;

    girq->parents[0] = chip->parent_irq;
    girq->default_type = IRQ_TYPE_NONE;
    girq->handler = handle_bad_irq;

    ret = devm_gpiochip_add_data(dev, &chip->gc, chip);
    if (ret)
        return dev_err_probe(dev, ret, "Не вдалося зареєструвати gpiochip\n");

    return 0;
}

static const struct of_device_id my_gpio_of_match[] = {
    { .compatible = "custom,my-gpio-controller" },
    { /* кінець таблиці */ }
};
MODULE_DEVICE_TABLE(of, my_gpio_of_match);

static struct platform_driver my_gpio_driver = {
    .probe = my_gpio_probe,
    .driver = {
        .name = "my-gpio-controller",
        .of_match_table = my_gpio_of_match,
    },
};
module_platform_driver(my_gpio_driver);

MODULE_AUTHOR("Linux Kernel Developer");
MODULE_DESCRIPTION("Драйвер контролера GPIO з підтримкою переривань irqchip");
MODULE_LICENSE("GPL");
