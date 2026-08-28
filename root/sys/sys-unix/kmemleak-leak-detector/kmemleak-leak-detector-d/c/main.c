struct kmemleak_object {
    raw_spinlock_t lock;
    unsigned int flags;        /* Прапорці стану: KMEMLEAK_GREY, KMEMLEAK_NO_SCAN */
    struct rb_node rb_node;    /* Вузол для включення у червоно-чорне дерево */
    unsigned long pointer;     /* Початкова віртуальна адреса виділеної пам'яті */
    size_t size;               /* Розмір виділеного блоку у байтах */
    int min_count;             /* Поріг досяжності (за замовчуванням 1) */
    int count;                 /* Поточний лічильник знайдених посилань */
    unsigned long trace[16];   /* Стек викликів на момент алокації */
};
