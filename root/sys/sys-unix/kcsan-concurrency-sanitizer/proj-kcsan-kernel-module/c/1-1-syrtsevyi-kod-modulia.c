#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/delay.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Observability Course");
MODULE_DESCRIPTION("KCSAN Data Race Demonstration Module");

static struct task_struct *writer_task;
static struct task_struct *reader_task;

/* Спільна структура даних між двома потоками ядра */
struct shared_device_state {
    int packets_counter;
    int is_ready;
    unsigned long last_update_jiffies;
};

static struct shared_device_state *global_dev;

/* Потік-письменник: оновлює лічильник та прапорці без блокувань */
static int writer_thread_func(void *arg)
{
    pr_info("kcsan_demo: Writer thread started on CPU %d\n", smp_processor_id());

    while (!kthread_should_stop()) {
        if (global_dev) {
            /* ПОМИЛКА: Несинхронізований звичайний запис у спільну пам'ять */
            global_dev->packets_counter++;
            global_dev->last_update_jiffies = jiffies;
            
            /* Імітація паузи перед встановленням прапорця готовності */
            udelay(5);
            global_dev->is_ready = 1;
        }
        msleep(20);
    }
    return 0;
}

/* Потік-читач: перевіряє прапорець та зчитує лічильник */
static int reader_thread_func(void *arg)
{
    pr_info("kcsan_demo: Reader thread started on CPU %d\n", smp_processor_id());

    while (!kthread_should_stop()) {
        if (global_dev) {
            /* ПОМИЛКА: Несинхронізоване читання прапорця та даних */
            if (global_dev->is_ready) {
                int count = global_dev->packets_counter;
                if (count % 100 == 0) {
                    pr_info("kcsan_demo: Milestone reached: %d packets\n", count);
                }
            }
        }
        msleep(15);
    }
    return 0;
}

static int __init kcsan_demo_init(void)
{
    pr_info("kcsan_demo: Initializing module and allocating state...\n");

    global_dev = kzalloc(sizeof(*global_dev), GFP_KERNEL);
    if (!global_dev)
        return -ENOMEM;

    /* Запуск двох потоків ядра */
    writer_task = kthread_run(writer_thread_func, NULL, "kcsan_writer_thread");
    if (IS_ERR(writer_task)) {
        pr_err("kcsan_demo: Failed to create writer thread\n");
        kfree(global_dev);
        return PTR_ERR(writer_task);
    }

    reader_task = kthread_run(reader_thread_func, NULL, "kcsan_reader_thread");
    if (IS_ERR(reader_task)) {
        pr_err("kcsan_demo: Failed to create reader thread\n");
        kthread_stop(writer_task);
        kfree(global_dev);
        return PTR_ERR(reader_task);
    }

    pr_info("kcsan_demo: Both threads running successfully\n");
    return 0;
}

static void __exit kcsan_demo_exit(void)
{
    pr_info("kcsan_demo: Stopping threads and unloading...\n");

    if (writer_task)
        kthread_stop(writer_task);
    if (reader_task)
        kthread_stop(reader_task);

    kfree(global_dev);
    pr_info("kcsan_demo: Module unloaded cleanly\n");
}

module_init(kcsan_demo_init);
module_exit(kcsan_demo_exit);
