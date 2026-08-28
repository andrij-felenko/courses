/* heartbeat.c — файл у /proc, вміст якого народжується під час читання */
#include <linux/atomic.h>
#include <linux/init.h>
#include <linux/jiffies.h>
#include <linux/module.h>
#include <linux/proc_fs.h>
#include <linux/sched.h>
#include <linux/seq_file.h>

#define PROC_NAME "heartbeat"

static struct proc_dir_entry *entry;
static atomic_t shows = ATOMIC_INIT(0);   /* скільки разів кликали show() */

static int hb_show(struct seq_file *m, void *v)
{
    seq_printf(m, "uptime_ms   %u\n", jiffies_to_msecs(jiffies - INITIAL_JIFFIES));
    seq_printf(m, "reader_pid  %d\n", current->pid);
    seq_printf(m, "reader_comm %s\n", current->comm);
    seq_printf(m, "shows       %d\n", atomic_inc_return(&shows));
    return 0;
}

static int hb_open(struct inode *inode, struct file *file)
{
    return single_open(file, hb_show, NULL);
}

static const struct proc_ops hb_ops = {
    .proc_open    = hb_open,
    .proc_read    = seq_read,
    .proc_lseek   = seq_lseek,
    .proc_release = single_release,
};

static int __init hb_init(void)
{
    entry = proc_create(PROC_NAME, 0444, NULL, &hb_ops);
    if (!entry)
        return -ENOMEM;
    return 0;
}

static void __exit hb_exit(void)
{
    proc_remove(entry);
}

module_init(hb_init);
module_exit(hb_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Файл у /proc, вміст якого не існує між читаннями");
