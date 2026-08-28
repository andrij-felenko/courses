/* pulsegen.c — модуль ядра */
#include <linux/module.h>
#include <linux/miscdevice.h>
#include <linux/fs.h>
#include <linux/mutex.h>
#include <linux/string.h>
#include <linux/uaccess.h>
#include <linux/overflow.h>
#include "pulsegen.h"

#define PULSE_MAX_BURST    4096u
#define PULSE_MAX_SPAN_US  10000000u   /* стеля тривалості пачки: 10 с */

static DEFINE_MUTEX(pulse_lock);       /* накриває обидві змінні нижче */
static struct pulse_cfg cur_cfg = { .period_us = 1000, .duty_permille = 500 };
static u64 issued_total;

static long do_set_cfg(void __user *uarg)
{
        struct pulse_cfg c;

        if (copy_from_user(&c, uarg, sizeof(c)))
                return -EFAULT;
        if (c.period_us < 10 || c.period_us > 1000000)
                return -EINVAL;
        if (c.duty_permille == 0 || c.duty_permille > 999)
                return -EINVAL;

        mutex_lock(&pulse_lock);
        cur_cfg = c;
        mutex_unlock(&pulse_lock);
        return 0;
}

static long do_get_cfg(void __user *uarg)
{
        struct pulse_cfg c;

        memset(&c, 0, sizeof(c));          /* спершу нулі, потім поля */
        mutex_lock(&pulse_lock);
        c.period_us     = cur_cfg.period_us;
        c.duty_permille = cur_cfg.duty_permille;
        mutex_unlock(&pulse_lock);

        return copy_to_user(uarg, &c, sizeof(c)) ? -EFAULT : 0;
}

static long do_burst(void __user *uarg)
{
        struct pulse_burst b;
        u32 want, span_us;
        u64 total;

        if (copy_from_user(&b, uarg, sizeof(b)))
                return -EFAULT;
        if (b.__pad != 0 || b.issued != 0)  /* поля ядра мусять прийти нулями */
                return -EINVAL;

        want = b.want;
        if (want == 0 || want > PULSE_MAX_BURST)
                return -EINVAL;

        mutex_lock(&pulse_lock);
        if (check_mul_overflow(want, cur_cfg.period_us, &span_us) ||
            span_us > PULSE_MAX_SPAN_US) {
                mutex_unlock(&pulse_lock);
                return -EINVAL;
        }
        issued_total += want;              /* читання-зміна-запис під замком */
        total = issued_total;
        mutex_unlock(&pulse_lock);

        memset(&b, 0, sizeof(b));          /* доповнення теж піде нулем */
        b.want   = want;
        b.issued = total;

        return copy_to_user(uarg, &b, sizeof(b)) ? -EFAULT : 0;
}

static long pulse_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
        void __user *uarg = (void __user *)arg;

        switch (cmd) {
        case PULSE_SET_CFG: return do_set_cfg(uarg);
        case PULSE_GET_CFG: return do_get_cfg(uarg);
        case PULSE_BURST:   return do_burst(uarg);
        default:            return -ENOTTY;
        }
}

static const struct file_operations pulse_fops = {
        .owner          = THIS_MODULE,
        .unlocked_ioctl = pulse_ioctl,
        .compat_ioctl   = compat_ptr_ioctl,
};

static struct miscdevice pulse_misc = {
        .minor = MISC_DYNAMIC_MINOR,
        .name  = "pulsegen",
        .fops  = &pulse_fops,
        .mode  = 0600,
};
module_misc_device(pulse_misc);

MODULE_DESCRIPTION("Навчальний генератор імпульсів із керуванням через ioctl");
MODULE_LICENSE("GPL");
