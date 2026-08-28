struct watchdog_device {
    int id;                         /* Унікальний номер у системі */
    struct device *parent;          /* Базовий пристрій шини (platform/PCI) */
    const struct watchdog_info *info; /* Метадані UAPI */
    const struct watchdog_ops *ops;  /* Таблиця callback-функцій */
    const struct watchdog_gov *gov;  /* Поточний Pretimeout Governor */
    unsigned int bootstatus;        /* Причина останнього скидання */
    unsigned int timeout;           /* Поточний таймаут у секундах */
    unsigned int pretimeout;        /* Поточний інтервал Pretimeout */
    unsigned int min_timeout;       /* Мінімальний апаратний таймаут */
    unsigned int max_timeout;       /* Максимальний апаратний таймаут */
    unsigned long status;           /* Прапорці стану драйвера (WDOG_*) */
    unsigned int max_hw_heartbeat_ms; /* Максимальний апаратний інтервал між пінгами */
    struct watchdog_core_data *wd_data; /* Внутрішній контекст ядра: hrtimer, черга, м'ютекс */
};
