#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/counter.h>
#include <linux/io.h>
#include <linux/interrupt.h>

struct my_encoder_priv {
    void __iomem *regs;
    int irq;
};

/* Припустимі режими роботи лічильника */
static const enum counter_function my_encoder_functions[] = {
    COUNTER_FUNCTION_QUADRATURE_X4,
    COUNTER_FUNCTION_PULSE_DIRECTION,
};

/* Припустимі дії для синапсів фаз A і B */
static const enum counter_synapse_action my_encoder_synapse_actions[] = {
    COUNTER_SYNAPSE_ACTION_BOTH_EDGES,
    COUNTER_SYNAPSE_ACTION_NONE,
};

/* Опис вхідних сигналів (Phase A, Phase B) */
static struct counter_signal my_encoder_signals[] = {
    {
        .id = 0,
        .name = "Channel A",
    },
    {
        .id = 1,
        .name = "Channel B",
    },
};

/* Зв'язок сигналів A та B із лічильником */
static struct counter_synapse my_encoder_synapses[] = {
    {
        .actions_list = my_encoder_synapse_actions,
        .num_actions = ARRAY_SIZE(my_encoder_synapse_actions),
        .signal = &my_encoder_signals[0],
    },
    {
        .actions_list = my_encoder_synapse_actions,
        .num_actions = ARRAY_SIZE(my_encoder_synapse_actions),
        .signal = &my_encoder_signals[1],
    },
};

/* Опис об'єкта Count */
static struct counter_count my_encoder_counts[] = {
    {
        .id = 0,
        .name = "Channel 0 Position",
        .functions_list = my_encoder_functions,
        .num_functions = ARRAY_SIZE(my_encoder_functions),
        .synapses = my_encoder_synapses,
        .num_synapses = ARRAY_SIZE(my_encoder_synapses),
    },
};

/* Реалізація колбеків читання та запису */
static int my_encoder_count_read(struct counter_device *counter,
                                 struct counter_count *count,
                                 u64 *val)
{
    struct my_encoder_priv *priv = counter_priv(counter);
    *val = readl(priv->regs + 0x04); /* Регістр поточного значення */
    return 0;
}

static int my_encoder_count_write(struct counter_device *counter,
                                  struct counter_count *count,
                                  u64 val)
{
    struct my_encoder_priv *priv = counter_priv(counter);
    writel((u32)val, priv->regs + 0x04);
    return 0;
}

static int my_encoder_function_read(struct counter_device *counter,
                                    struct counter_count *count,
                                    enum counter_function *function)
{
    *function = COUNTER_FUNCTION_QUADRATURE_X4;
    return 0;
}

static const struct counter_ops my_encoder_ops = {
    .count_read = my_encoder_count_read,
    .count_write = my_encoder_count_write,
    .function_read = my_encoder_function_read,
};

/* Обробник апаратного переривання (IRQ) */
static irqreturn_t my_encoder_irq_handler(int irq, void *dev_id)
{
    struct counter_device *counter = dev_id;
    struct my_encoder_priv *priv = counter_priv(counter);
    u32 status = readl(priv->regs + 0x08); /* Регістр статусу переривання */

    if (status & 0x01) { /* Переповнення (Overflow) */
        writel(0x01, priv->regs + 0x08); /* Скидання прапорця */
        counter_push_event(counter, COUNTER_EVENT_OVERFLOW, 0);
        return IRQ_HANDLED;
    }

    return IRQ_NONE;
}

static int my_encoder_probe(struct platform_device *pdev)
{
    struct counter_device *counter;
    struct my_encoder_priv *priv;
    void __iomem *regs;
    int irq, ret;

    regs = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(regs))
        return PTR_ERR(regs);

    irq = platform_get_irq(pdev, 0);
    if (irq < 0)
        return irq;

    counter = devm_counter_alloc(&pdev->dev, sizeof(*priv));
    if (!counter)
        return -ENOMEM;

    priv = counter_priv(counter);
    priv->regs = regs;
    priv->irq = irq;

    counter->name = dev_name(&pdev->dev);
    counter->parent = &pdev->dev;
    counter->ops = &my_encoder_ops;
    counter->signals = my_encoder_signals;
    counter->num_signals = ARRAY_SIZE(my_encoder_signals);
    counter->counts = my_encoder_counts;
    counter->num_counts = ARRAY_SIZE(my_encoder_counts);

    ret = devm_request_irq(&pdev->dev, irq, my_encoder_irq_handler,
                           IRQF_SHARED, dev_name(&pdev->dev), counter);
    if (ret)
        return ret;

    return devm_counter_add(&pdev->dev, counter);
}

static const struct of_device_id my_encoder_of_match[] = {
    { .compatible = "vendor,quad-encoder-v1" },
    { /* sentinel */ }
};
MODULE_DEVICE_TABLE(of, my_encoder_of_match);

static struct platform_driver my_encoder_driver = {
    .probe = my_encoder_probe,
    .driver = {
        .name = "my-quad-encoder",
        .of_match_table = my_encoder_of_match,
    },
};
module_platform_driver(my_encoder_driver);

MODULE_AUTHOR("Industrial Embedded Developer");
MODULE_DESCRIPTION("Generic Hardware Quadrature Encoder Driver");
MODULE_LICENSE("GPL");
