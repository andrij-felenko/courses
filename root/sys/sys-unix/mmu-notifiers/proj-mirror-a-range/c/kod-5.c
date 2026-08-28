static int mirror_open(struct inode *inode, struct file *file)
{
        struct mirror *m = kzalloc(sizeof(*m), GFP_KERNEL);

        if (!m)
                return -ENOMEM;
        mutex_init(&m->setup);
        mutex_init(&m->lock);
        file->private_data = m;
        return 0;
}

static long mirror_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
        struct mirror *m = file->private_data;
        struct mirror_range r;
        long ret;

        if (copy_from_user(&r, (void __user *)arg, sizeof(r)))
                return -EFAULT;

        mutex_lock(&m->setup);
        switch (cmd) {
        case MIRROR_IOC_ATTACH:
                ret = mirror_attach(m, r.start, r.length);
                break;
        case MIRROR_IOC_FAULT:
                if (!m->attached || !r.length ||
                    !IS_ALIGNED(r.start, PAGE_SIZE) || !IS_ALIGNED(r.length, PAGE_SIZE) ||
                    r.start < m->start || r.length > (m->npages << PAGE_SHIFT) ||
                    r.start + r.length > m->start + (m->npages << PAGE_SHIFT))
                        ret = -EINVAL;
                else
                        ret = mirror_fault(m, r.start, r.length);
                break;
        default:
                ret = -ENOTTY;
        }
        mutex_unlock(&m->setup);
        return ret;
}

static const struct file_operations mirror_fops = {
        .owner          = THIS_MODULE,
        .open           = mirror_open,
        .release        = mirror_release,
        .unlocked_ioctl = mirror_ioctl,
        .compat_ioctl   = compat_ptr_ioctl,
        .llseek         = noop_llseek,
};

static struct miscdevice mirror_dev = {
        .minor = MISC_DYNAMIC_MINOR,
        .name  = "mirror",
        .fops  = &mirror_fops,
};
module_misc_device(mirror_dev);
MODULE_LICENSE("GPL");
