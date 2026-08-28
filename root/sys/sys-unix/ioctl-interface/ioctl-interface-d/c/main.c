static long uart_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
{
        struct uart_dev *dev = f->private_data;
        struct uart_cfg cfg;

        switch (cmd) {
        case UART_SET_BAUD:
                if (copy_from_user(&cfg, (void __user *)arg, sizeof(cfg)))
                        return -EFAULT;
                if (cfg.baud == 0 || cfg.baud > 4000000)
                        return -EINVAL;
                return uart_apply_baud(dev, cfg.baud);

        case UART_GET_BAUD:
                memset(&cfg, 0, sizeof(cfg));
                cfg.baud = dev->baud;
                if (copy_to_user((void __user *)arg, &cfg, sizeof(cfg)))
                        return -EFAULT;
                return 0;

        default:
                return -ENOTTY;
        }
}
