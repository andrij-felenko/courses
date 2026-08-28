/* rcudemo.c — список псевдопристроїв, який читають без замка */
#include <linux/init.h>
#include <linux/kstrtox.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/proc_fs.h>
#include <linux/rculist.h>
#include <linux/seq_file.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/uaccess.h>

struct pdev {
    struct list_head node;
    struct rcu_head  rcu;      /* службове поле для call_rcu() */
    unsigned int     id;
    char             name[24];
};

static LIST_HEAD(pdev_list);
static DEFINE_MUTEX(pdev_mutex);          /* ЛИШЕ між письменниками */
static unsigned int next_id = 1;          /* під pdev_mutex */
static atomic_t freed = ATOMIC_INIT(0);   /* скільки записів уже звільнено */

/* ── читач ── */
static int pdev_show(struct seq_file *m, void *v)
{
    struct pdev *p;

    rcu_read_lock();
    list_for_each_entry_rcu(p, &pdev_list, node)
        seq_printf(m, "%u %s\n", p->id, p->name);
    rcu_read_unlock();

    seq_printf(m, "# freed %d\n", atomic_read(&freed));
    return 0;
}

/* ── письменник: додати ── */
static int pdev_add(const char *name)
{
    struct pdev *p = kzalloc(sizeof(*p), GFP_KERNEL);

    if (!p)
        return -ENOMEM;
    strscpy(p->name, name, sizeof(p->name));   /* поля — ДО публікації */

    mutex_lock(&pdev_mutex);
    p->id = next_id++;
    list_add_tail_rcu(&p->node, &pdev_list);   /* тут вузол стає видимим */
    mutex_unlock(&pdev_mutex);
    return 0;
}

/* ── письменник: вилучити ── */
static void pdev_free_rcu(struct rcu_head *head)
{
    struct pdev *p = container_of(head, struct pdev, rcu);

    atomic_inc(&freed);
    pr_info("rcudemo: звільнено %u %s\n", p->id, p->name);
    kfree(p);
}

static int pdev_del(unsigned int id)
{
    struct pdev *p;
    int ret = -ENOENT;

    mutex_lock(&pdev_mutex);
    list_for_each_entry(p, &pdev_list, node) {   /* під м'ютексом — звичайний обхід */
        if (p->id != id)
            continue;
        list_del_rcu(&p->node);            /* зник для нових читачів */
        call_rcu(&p->rcu, pdev_free_rcu);  /* звільнити після періоду відстрочки */
        ret = 0;
        break;
    }
    mutex_unlock(&pdev_mutex);
    return ret;
}

/* ── обв'язка /proc: розбір команди й реєстрація файлу ── */
static int pdev_open(struct inode *inode, struct file *file)
{
    return single_open(file, pdev_show, NULL);
}

static ssize_t pdev_write(struct file *f, const char __user *ubuf,
                          size_t count, loff_t *ppos)
{
    char cmd[40], *arg;
    unsigned int id;
    int ret;

    if (count == 0 || count >= sizeof(cmd))
        return -EINVAL;
    if (copy_from_user(cmd, ubuf, count))
        return -EFAULT;
    cmd[count] = '\0';
    arg = strim(cmd);

    if (!strncmp(arg, "add ", 4))
        ret = pdev_add(strim(arg + 4));
    else if (!strncmp(arg, "del ", 4))
        ret = kstrtouint(strim(arg + 4), 10, &id) ? -EINVAL : pdev_del(id);
    else
        return -EINVAL;

    return ret ? ret : count;
}

static const struct proc_ops pdev_proc_ops = {
    .proc_open    = pdev_open,
    .proc_read    = seq_read,
    .proc_write   = pdev_write,
    .proc_lseek   = seq_lseek,
    .proc_release = single_release,
};

static struct proc_dir_entry *entry;

static int __init rcudemo_init(void)
{
    entry = proc_create("rcudemo", 0644, NULL, &pdev_proc_ops);
    return entry ? 0 : -ENOMEM;
}

/* rcudemo_exit() — далі, у розділі про rcu_barrier();
   за ним у файлі йдуть module_init/module_exit і MODULE_LICENSE("GPL"). */
