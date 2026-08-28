// SPDX-License-Identifier: GPL-2.0
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kthread.h>
#include <linux/sched.h>
#include <linux/spinlock.h>
#include <linux/completion.h>
#include <linux/interrupt.h>
#include <linux/delay.h>

static int mode = 1;
module_param(mode, int, 0444);
MODULE_PARM_DESC(mode, "1 — зворотний порядок замків, 2 — асиметрія за softirq");

static unsigned long work_done;      /* аби критична ділянка не була порожньою */

/* ── вправа 1: два замки у зворотному порядку ──────────────────────────── */

static DEFINE_SPINLOCK(lock_a);
static DEFINE_SPINLOCK(lock_b);
static DECLARE_COMPLETION(ab_done);

/* Потік, який відпрацював, не має права просто вийти: модуль можуть
   вивантажити, доки він ще всередині своєї функції. Тому чекаємо на
   kthread_stop() у ледачому сні, який нічого не коштує. */
static void park_until_stop(void)
{
    while (!kthread_should_stop())
        schedule_timeout_idle(HZ);
}

static int worker_ab(void *unused)
{
    spin_lock(&lock_a);
    spin_lock(&lock_b);          /* ребро lock_a → lock_b лягає в граф */
    work_done++;
    spin_unlock(&lock_b);
    spin_unlock(&lock_a);

    pr_info("ab: a→b пройшло тихо\n");
    complete(&ab_done);

    park_until_stop();
    return 0;
}

static int worker_ba(void *unused)
{
    wait_for_completion(&ab_done);   /* перший уже все відпустив */
    msleep(500);                     /* і ще пауза: перекриття неможливе */

    spin_lock(&lock_b);
    spin_lock(&lock_a);              /* ось на цьому рядку механізм і кричить */
    work_done++;
    spin_unlock(&lock_a);
    spin_unlock(&lock_b);

    pr_info("ba: b→a пройшло — і машина жива\n");

    park_until_stop();
    return 0;
}

/* ── вправа 2: той самий замок у задачі й у тасклеті ───────────────────── */

static DEFINE_SPINLOCK(shared_lock);

static void lab_tasklet_fn(struct tasklet_struct *t)
{
    spin_lock(&shared_lock);         /* контекст softirq */
    work_done++;
    spin_unlock(&shared_lock);
}
static DECLARE_TASKLET(lab_tasklet, lab_tasklet_fn);

static int worker_soft(void *unused)
{
    /* спершу — з контексту задачі, без жодної заборони нижніх половин */
    spin_lock(&shared_lock);
    work_done++;
    spin_unlock(&shared_lock);
    pr_info("soft: задача взяла замок звичайним spin_lock()\n");

    msleep(500);
    tasklet_schedule(&lab_tasklet);  /* тепер той самий замок — із softirq */

    park_until_stop();
    return 0;
}

/* ── збирання докупи ───────────────────────────────────────────────────── */

static struct task_struct *th1, *th2;

static int __init lab_init(void)
{
    if (mode == 1) {
        th1 = kthread_run(worker_ab, NULL, "lab_ab");
        if (IS_ERR(th1))
            return PTR_ERR(th1);

        th2 = kthread_run(worker_ba, NULL, "lab_ba");
        if (IS_ERR(th2)) {
            kthread_stop(th1);
            return PTR_ERR(th2);
        }
        return 0;
    }

    th1 = kthread_run(worker_soft, NULL, "lab_soft");
    return IS_ERR(th1) ? PTR_ERR(th1) : 0;
}

static void __exit lab_exit(void)
{
    if (th2)
        kthread_stop(th2);
    if (th1)
        kthread_stop(th1);
    tasklet_kill(&lab_tasklet);
    pr_info("вивантажуюсь, ділянок пройдено: %lu\n", work_done);
}

module_init(lab_init);
module_exit(lab_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Навмисні порушення порядку замків для перевірки lockdep");
