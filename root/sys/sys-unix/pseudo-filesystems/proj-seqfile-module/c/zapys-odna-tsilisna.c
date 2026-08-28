#include <linux/string.h>    /* strim */
#include <linux/uaccess.h>   /* copy_from_user */

static ssize_t hb_write(struct file *file, const char __user *ubuf,
                        size_t count, loff_t *ppos)
{
    char cmd[16], *p;

    if (count == 0 || count >= sizeof cmd)
        return -EINVAL;              /* не влізло — це помилка, а не «запишемо частину» */
    if (copy_from_user(cmd, ubuf, count))
        return -EFAULT;
    cmd[count] = '\0';
    p = strim(cmd);                  /* прибрати \n, який додає echo */

    if (!strcmp(p, "bump"))
        atomic_inc(&generation);
    else if (!strcmp(p, "reset"))
        atomic_set(&generation, 1);
    else
        return -EINVAL;

    return count;                    /* спожито все */
}
