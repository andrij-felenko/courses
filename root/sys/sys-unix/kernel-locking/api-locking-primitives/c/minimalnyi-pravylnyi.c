#include <linux/completion.h>
#include <linux/interrupt.h>
#include <linux/mutex.h>
#include <linux/slab.h>
#include <linux/spinlock.h>

struct my_dev {
    spinlock_t         lock;      /* список чіпає обробник → спін-замок       */
    struct list_head   events;
    struct mutex       cfg_lock;  /* налаштування чіпає лише задача → м'ютекс */
    struct dev_config  cfg;
    struct completion  done;      /* задача чекає, обробник сповіщає          */
    atomic_t           dropped;   /* лічильник із будь-якого контексту        */
};

static int dev_init(struct my_dev *d)
{
    spin_lock_init(&d->lock);
    INIT_LIST_HEAD(&d->events);
    mutex_init(&d->cfg_lock);
    init_completion(&d->done);
    atomic_set(&d->dropped, 0);
    return 0;
}

/* Шлях задачі. Виділення — ЗА межами замка: kmalloc(GFP_KERNEL) має право заснути. */
int dev_push(struct my_dev *d, u32 code)
{
    struct event *e = kmalloc(sizeof(*e), GFP_KERNEL);
    unsigned long flags;                      /* локальна, unsigned long      */

    if (!e)
        return -ENOMEM;
    e->code = code;

    spin_lock_irqsave(&d->lock, flags);       /* цей замок бере й обробник    */
    list_add_tail(&e->node, &d->events);
    spin_unlock_irqrestore(&d->lock, flags);
    return 0;
}

/* Шлях обробника. Переривання вже закриті — досить spin_lock(). */
static irqreturn_t dev_irq(int irq, void *arg)
{
    struct my_dev *d = arg;
    struct event *e = kmalloc(sizeof(*e), GFP_ATOMIC);   /* не GFP_KERNEL!    */

    if (!e) {
        atomic_inc(&d->dropped);              /* законно навіть звідси        */
        return IRQ_HANDLED;
    }
    e->code = read_status(d);

    spin_lock(&d->lock);
    list_add_tail(&e->node, &d->events);
    spin_unlock(&d->lock);

    complete(&d->done);                       /* сповістити — можна; узяти    */
    return IRQ_HANDLED;                       /* м'ютекс — ні                 */
}

/* Довга робота під сплячим замком — лише з контексту задачі. */
int dev_reconfigure(struct my_dev *d, const struct dev_config *new_cfg)
{
    if (mutex_lock_interruptible(&d->cfg_lock))
        return -ERESTARTSYS;

    d->cfg = *new_cfg;
    apply_config(d);                          /* може чекати на апаратуру     */

    mutex_unlock(&d->cfg_lock);               /* звільняє той самий, хто брав */
    return 0;
}
