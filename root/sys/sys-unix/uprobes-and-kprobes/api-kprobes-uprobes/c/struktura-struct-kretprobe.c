struct kretprobe {
    /* Базовий kprobe, який встановлюється на вхід у функцію */
    struct kprobe kp;

    /* Обробник, який викликається в момент завершення функції */
    kretprobe_handler_t handler;

    /* Обробник, який викликається на вході для підготовки даних */
    kretprobe_holder_t entry_handler;

    /* Максимальна кількість одночасно активних викликів цієї функції */
    int maxactive;

    /* Лічильник пропущених спрацьовувань через вичерпання maxactive */
    int nmissed;

    /* Розмір користувацьких даних (data_size), що передаються між entry та exit */
    size_t data_size;

    /* Захищений список примірників активних викликів */
    struct hlist_head free_instances;
    raw_spinlock_t lock;
};
