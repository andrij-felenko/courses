#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kthread.h>
#include <linux/delay.h>

#define CREATE_TRACE_POINTS
#include "tp_sample_events.h"

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Antigravity Engineer");
MODULE_DESCRIPTION("Демонстрація статичної точки TRACE_EVENT у модулі ядра");

static struct task_struct *worker_thread;

static int sensor_worker(void *data) {
    int counter = 0;
    while (!kthread_should_stop()) {
        int simulated_value = (counter * 7) % 100;
        
        /* Виклик статичної точки трасування.
         * Якщо точка вимкнена у tracefs, це виконує одну інструкцію NOP.
         */
        trace_sample_sensor_read(1, simulated_value, "temp_zone_0");

        counter++;
        msleep_interruptible(200); /* Генерація 5 подій на секунду */
    }
    return 0;
}

static int __init sample_init(void) {
    pr_info("sample_tp_mod: Ініціалізація модуля\n");
    worker_thread = kthread_run(sensor_worker, NULL, "k_sensor_tp");
    if (IS_ERR(worker_thread)) {
        pr_err("sample_tp_mod: Не вдалося запустити kthread\n");
        return PTR_ERR(worker_thread);
    }
    return 0;
}

static void __exit sample_exit(void) {
    if (worker_thread) {
        kthread_stop(worker_thread);
    }
    pr_info("sample_tp_mod: Модуль успішно вивантажено\n");
}

module_init(sample_init);
module_exit(sample_exit);
