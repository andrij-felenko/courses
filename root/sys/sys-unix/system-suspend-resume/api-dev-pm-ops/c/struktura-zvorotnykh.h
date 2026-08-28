struct dev_pm_ops {
    /* Підготовка та фіналізація системного переходу */
    int (*prepare)(struct device *dev);
    void (*complete)(struct device *dev);

    /* Стандартний цикл системного сну (Suspend-to-RAM / s2idle) */
    int (*suspend)(struct device *dev);
    int (*resume)(struct device *dev);

    /* Пізні та ранні виклики (обробка доменів живлення та шин) */
    int (*suspend_late)(struct device *dev);
    int (*resume_early)(struct device *dev);

    /* Виклики з вимкненими перериваннями пристроїв (Atomic Noirq) */
    int (*suspend_noirq)(struct device *dev);
    int (*resume_noirq)(struct device *dev);

    /* Фази заморожування при гібернації (створення знімка RAM) */
    int (*freeze)(struct device *dev);
    int (*thaw)(struct device *dev);
    int (*poweroff)(struct device *dev);
    int (*restore)(struct device *dev);

    int (*freeze_late)(struct device *dev);
    int (*thaw_early)(struct device *dev);
    int (*poweroff_late)(struct device *dev);
    int (*restore_early)(struct device *dev);

    int (*freeze_noirq)(struct device *dev);
    int (*thaw_noirq)(struct device *dev);
    int (*poweroff_noirq)(struct device *dev);
    int (*restore_noirq)(struct device *dev);

    /* Динамічне керування живленням на ходу (Runtime PM) */
    int (*runtime_suspend)(struct device *dev);
    int (*runtime_resume)(struct device *dev);
    int (*runtime_idle)(struct device *dev);
};
