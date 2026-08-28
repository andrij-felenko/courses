/* доповнення до heartbeat.c: список замість одного знімка */
#include <linux/mutex.h>

static unsigned int rows = 200;
module_param(rows, uint, 0444);
MODULE_PARM_DESC(rows, "скільки рядків друкувати");

static DEFINE_MUTEX(hb_lock);
static atomic_t generation = ATOMIC_INIT(1);

static void *hb_start(struct seq_file *m, loff_t *pos)
{
    mutex_lock(&hb_lock);            /* замок беремо тут… */
    if (*pos >= rows)
        return NULL;
    return pos;                      /* курсор — сам лічильник позиції */
}

static void *hb_next(struct seq_file *m, void *v, loff_t *pos)
{
    ++*pos;
    return (*pos >= rows) ? NULL : pos;
}

static void hb_stop(struct seq_file *m, void *v)
{
    mutex_unlock(&hb_lock);          /* …і віддаємо тут */
}

static int hb_row(struct seq_file *m, void *v)
{
    seq_printf(m, "row %4lld  generation %d\n",
               *(loff_t *)v, atomic_read(&generation));
    return 0;
}

static const struct seq_operations hb_seq_ops = {
    .start = hb_start,
    .next  = hb_next,
    .stop  = hb_stop,
    .show  = hb_row,
};

static int hb_open(struct inode *inode, struct file *file)
{
    return seq_open(file, &hb_seq_ops);      /* замість single_open */
}
