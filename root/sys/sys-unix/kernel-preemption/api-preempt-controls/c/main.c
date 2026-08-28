#include <linux/list.h>
#include <linux/local_lock.h>
#include <linux/slab.h>
#include <linux/spinlock.h>

/* 1. Виділення пам'яті — ЗА межами замка, а не під ним. */
struct entry { struct list_head node; int value; };

static DEFINE_SPINLOCK(list_lock);
static LIST_HEAD(entries);

int add_entry(int value)
{
    struct entry *e = kmalloc(sizeof(*e), GFP_KERNEL);   /* має право заснути */
    if (!e)
        return -ENOMEM;
    e->value = value;

    spin_lock(&list_lock);           /* звичайне ядро: тут витіснення вимкнене */
    list_add(&e->node, &entries);    /* під замком — тільки коротке зв'язування */
    spin_unlock(&list_lock);
    return 0;
}

/* 2. Дані свого ядра процесора: замок замість голої заборони витіснення. */
static DEFINE_PER_CPU(local_lock_t, cnt_lock) = INIT_LOCAL_LOCK(cnt_lock);
static DEFINE_PER_CPU(unsigned long, hits);

void count_hit(void)
{
    local_lock(&cnt_lock);           /* звичайне ядро — preempt_disable()    */
    this_cpu_inc(hits);              /* PREEMPT_RT — спін-замок цього ядра   */
    local_unlock(&cnt_lock);
}
