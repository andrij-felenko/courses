#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/mutex.h>
#include <linux/kthread.h>
#include <linux/delay.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Lockdep Educational Demo");
MODULE_DESCRIPTION("Module demonstrating Lockdep ABBA detection");

/* Оголошення двох статичних класів м'ютексів */
static DEFINE_MUTEX(lock_alpha);
static DEFINE_MUTEX(lock_beta);

static struct task_struct *thread_1;
static struct task_struct *thread_2;

/* Перший потік: Порядок захоплення Alpha -> Beta */
static int worker_thread_1(void *arg)
{
    pr_info("LockdepDemo: Thread 1 starting. Sequence: Alpha -> Beta\n");
    
    mutex_lock(&lock_alpha);
    pr_info("LockdepDemo: Thread 1 acquired Alpha\n");
    
    /* Затримка для перекриття часу виконання потоків */
    msleep(50); 
    
    mutex_lock(&lock_beta);
    pr_info("LockdepDemo: Thread 1 acquired Beta\n");
    
    mutex_unlock(&lock_beta);
    mutex_unlock(&lock_alpha);
    
    pr_info("LockdepDemo: Thread 1 finished cleanly\n");
    return 0;
}

/* Другий потік: Порядок захоплення Beta -> Alpha */
static int worker_thread_2(void *arg)
{
    pr_info("LockdepDemo: Thread 2 starting. Sequence: Beta -> Alpha\n");
    
    mutex_lock(&lock_beta);
    pr_info("LockdepDemo: Thread 2 acquired Beta\n");
    
    msleep(50);
    
    /* Спроба взяти Alpha утримуючи Beta -> Формування ребра Beta -> Alpha */
    mutex_lock(&lock_alpha);
    pr_info("LockdepDemo: Thread 2 acquired Alpha\n");
    
    mutex_unlock(&lock_alpha);
    mutex_unlock(&lock_beta);
    
    pr_info("LockdepDemo: Thread 2 finished cleanly\n");
    return 0;
}

static int __init lockdep_demo_init(void)
{
    pr_info("LockdepDemo: Loading module...\n");
    
    /* Запуск двох фонових потоків ядра */
    thread_1 = kthread_run(worker_thread_1, NULL, "lockdep_wrk1");
    thread_2 = kthread_run(worker_thread_2, NULL, "lockdep_wrk2");
    
    return 0;
}

static void __exit lockdep_demo_exit(void)
{
    pr_info("LockdepDemo: Unloading module\n");
}

module_init(lockdep_demo_init);
module_exit(lockdep_demo_exit);
