static const struct file_operations accel_driver_fops = {
    .owner          = THIS_MODULE,
    .open           = accel_open,
    .release        = drm_release,
    .unlocked_ioctl = drm_ioctl,
    .compat_ioctl   = drm_compat_ioctl,
    .mmap           = drm_gem_mmap,
    .poll           = drm_poll,
    .read           = drm_read,
    .llseek         = noop_llseek,
};
