/* kdemo.c — модуль із власним потоком ядра */
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/kthread.h>
#include <linux/wait.h>
#include <linux/slab.h>
#include <linux/sched.h>
#include <linux/smp.h>
#include <linux/err.h>
#include <linux/sysfs.h>

struct kdemo {
    struct task_struct *task;
    wait_queue_head_t   waitq;
    bool                has_work;
    unsigned long       rounds;
};

static struct kdemo *demo;

/* ── усе життя потоку — це одна функція ────────────────────────────── */
static int kdemo_thread(void *arg)
{
    struct kdemo *d = arg;
    void *scratch;

    scratch = kmalloc(PAGE_SIZE, GFP_KERNEL);
    if (!scratch) {
        pr_err("немає пам'яті під буфер\n");
        goto wait_for_stop;      /* саме goto, а не return: пастка 3 */
    }

    pr_info("потік %s стартував, pid=%d\n", current->comm, current->pid);

    while (!kthread_should_stop()) {
        wait_event_interruptible(d->waitq,
                                 READ_ONCE(d->has_work) ||
                                 kthread_should_stop());
        if (kthread_should_stop())
            break;

        WRITE_ONCE(d->has_work, false);

        memset(scratch, 0, PAGE_SIZE);      /* справжня робота: тут спати МОЖНА */
        d->rounds++;
        pr_info("коло %lu на CPU%u\n", d->rounds, raw_smp_processor_id());
    }

    kfree(scratch);
    pr_info("потік виходить, зроблено кіл: %lu\n", d->rounds);
    return 0;

wait_for_stop:
    /* здатися можна; мовчки повернутися — ні: на нас чекатиме kthread_stop() */
    set_current_state(TASK_INTERRUPTIBLE);
    while (!kthread_should_stop()) {
        schedule();
        set_current_state(TASK_INTERRUPTIBLE);
    }
    __set_current_state(TASK_RUNNING);
    return -ENOMEM;
}

/* ── штовхнути потік ззовні: запис у /sys/module/kdemo/parameters/kick ── */
static int kdemo_kick_set(const char *val, const struct kernel_param *kp)
{
    if (!demo)
        return -ENODEV;

    WRITE_ONCE(demo->has_work, true);       /* спершу факт... */
    wake_up_interruptible(&demo->waitq);    /* ...і аж потім побудка */
    return 0;
}

static int kdemo_kick_get(char *buf, const struct kernel_param *kp)
{
    return sysfs_emit(buf, "%lu\n", demo ? READ_ONCE(demo->rounds) : 0UL);
}

static const struct kernel_param_ops kdemo_kick_ops = {
    .set = kdemo_kick_set,
    .get = kdemo_kick_get,
};
module_param_cb(kick, &kdemo_kick_ops, NULL, 0644);
MODULE_PARM_DESC(kick, "запис — розбудити потік; читання — скільки кіл зроблено");

/* ── завантаження й вивантаження ───────────────────────────────────── */
static int __init kdemo_init(void)
{
    struct task_struct *t;

    demo = kzalloc(sizeof(*demo), GFP_KERNEL);
    if (!demo)
        return -ENOMEM;

    init_waitqueue_head(&demo->waitq);

    t = kthread_run(kdemo_thread, demo, "kdemo/%d", 0);
    if (IS_ERR(t)) {
        int err = PTR_ERR(t);

        pr_err("kthread_run: %d\n", err);
        kfree(demo);
        demo = NULL;
        return err;
    }

    demo->task = t;
    pr_info("завантажено, потік pid=%d\n", task_pid_nr(t));
    return 0;
}

static void __exit kdemo_exit(void)
{
    int ret = kthread_stop(demo->task);   /* повернеться лише з мертвим потоком */

    pr_info("потік завершився з кодом %d\n", ret);
    kfree(demo);
    demo = NULL;
}

module_init(kdemo_init);
module_exit(kdemo_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Потік ядра: запуск, побудка, зупинка");
