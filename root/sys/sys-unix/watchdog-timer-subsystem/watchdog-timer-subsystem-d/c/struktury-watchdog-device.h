struct watchdog_ops {
    struct module *owner;
    /* Обов'язкові операції драйвера */
    int (*start)(struct watchdog_device *);
    int (*stop)(struct watchdog_device *);
    /* Необов'язкові розширені операції */
    int (*ping)(struct watchdog_device *);
    unsigned int (*status)(struct watchdog_device *);
    int (*set_timeout)(struct watchdog_device *, unsigned int);
    int (*set_pretimeout)(struct watchdog_device *, unsigned int);
    unsigned int (*get_timeleft)(struct watchdog_device *);
    long (*ioctl)(struct watchdog_device *, unsigned int, unsigned long);
};
