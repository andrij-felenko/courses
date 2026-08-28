#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/slab.h>
#include <linux/compiler.h>
#include <linux/kcsan-checks.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Observability Course");
MODULE_DESCRIPTION("KCSAN Data Race Fixed Demo Module");

static struct task_struct *writer_task;
static struct task_struct *reader_task;

struct shared_device_state {
    int packets_counter;
    int is_ready;
    unsigned long last_update_jiffies;
};

static struct shared_device_state *global_dev;

static int writer_thread_func_fixed(void *arg)
{
    while (!kthread_should_stop()) {
        if (global_dev) {
            /* 1. Твердження: Лише цей потік має право змінювати packets_counter */
            ASSERT_EXCLUSIVE_WRITER(global_dev->packets_counter);

            int current_cnt = READ_ONCE(global_dev->packets_counter);
            
            /* 2. Атомарний маркований запис */
            WRITE_ONCE(global_dev->packets_counter, current_cnt + 1);
            WRITE_ONCE(global_dev->last_update_jiffies, jiffies);
            
            /* 3. Упорядковане встановлення прапорця готовності */
            smp_store_release(&global_dev->is_ready, 1);
        }
        msleep(20);
    }
    return 0;
}

static int reader_thread_func_fixed(void *arg)
{
    while (!kthread_should_stop()) {
        if (global_dev) {
            /* 1. Впорядковане читання прапорця із семантикою Acquire */
            if (smp_load_acquire(&global_dev->is_ready)) {
                /* 2. Марковане читання лічильника */
                int count = READ_ONCE(global_dev->packets_counter);
                if (count % 100 == 0) {
                    pr_info("kcsan_demo_fixed: Safe read milestone: %d\n", count);
                }
            }
        }
        msleep(15);
    }
    return 0;
}

static int __init kcsan_demo_fixed_init(void)
{
    pr_info("kcsan_demo_fixed: Initializing sanitized module...\n");

    global_dev = kzalloc(sizeof(*global_dev), GFP_KERNEL);
    if (!global_dev)
        return -ENOMEM;

    writer_task = kthread_run(writer_thread_func_fixed, NULL, "kcsan_w_fixed");
    reader_task = kthread_run(reader_thread_func_fixed, NULL, "kcsan_r_fixed");

    return 0;
}

static void __exit kcsan_demo_fixed_exit(void)
{
    if (writer_task)
        kthread_stop(writer_task);
    if (reader_task)
        kthread_stop(reader_task);

    kfree(global_dev);
    pr_info("kcsan_demo_fixed: Unloaded cleanly without KCSAN warnings\n");
}

module_init(kcsan_demo_fixed_init);
module_exit(kcsan_demo_fixed_exit);
