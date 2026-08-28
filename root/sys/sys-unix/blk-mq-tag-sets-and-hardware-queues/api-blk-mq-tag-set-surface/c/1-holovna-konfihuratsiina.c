struct blk_mq_tag_set {
    /* Таблиця функцій зворотного виклику низькорівневого драйвера */
    const struct blk_mq_ops *ops;

    /* Загальна кількість апаратних диспетчерських черг (hctx) */
    unsigned int            nr_hw_queues;

    /* Кількість тегів НА ОДНУ апаратну чергу, разом із резервованими */
    unsigned int            queue_depth;

    /* Кількість тегів, резервованих для високопріоритетних/системних запитів */
    unsigned int            reserved_tags;

    /* Розмір приватних даних драйвера (в байтах), що додаються до кожної struct request */
    unsigned int            cmd_size;

    /* Ідентифікатор NUMA-вузла для оптимального виділення пам'яті під структури */
    int                     numa_node;

    /* Таймаут виконання операцій вводу-виводу у системних тиках (jiffies) */
    unsigned int            timeout;

    /* Бітові прапори конфігурації поведінки черги (BLK_MQ_F_*) */
    unsigned int            flags;

    /* Нетипізований вказівник на приватну контекстну структуру драйвера */
    void                   *driver_data;

    /* Масив пулів тегів: рівно один елемент на кожну апаратну чергу */
    struct blk_mq_tags    **tags;

    /* Масиви відображення процесорних ядер на апаратні черги (для різних типів I/O) */
    struct blk_mq_queue_map map[HCTX_MAX_TYPES];

    /* Кількість активних типів черг у масиві map (Default, Read, Poll) */
    unsigned int            nr_maps;

    /* Зв'язаний список усіх блокових черг (request_queue), які ділять цей tag_set */
    struct list_head        tag_list;

    /* М'ютекс для синхронізації змін у списку tag_list */
    struct mutex            tag_list_lock;
};
