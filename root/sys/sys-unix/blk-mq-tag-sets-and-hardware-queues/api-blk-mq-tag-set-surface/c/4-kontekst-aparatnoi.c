struct blk_mq_hw_ctx {
    /* Спінлок, що захищає локальний список диспетчеризації */
    spinlock_t              lock;

    /* Список запитів, готових до передачі драйверу (dispatch list) */
    struct list_head        dispatch;

    /* Ковзне середнє «зайнятості» відправки: росте на BLK_STS_RESOURCE */
    unsigned int            dispatch_busy;

    /* Маска логічних CPU, які прив'язані до цієї hctx */
    cpumask_var_t           cpumask;

    /* Вказівник на пул тегів, що використовується цією hctx */
    struct blk_mq_tags     *tags;

    /* Окремий пул тегів планувальника (коли планувальник підключено) */
    struct blk_mq_tags     *sched_tags;

    /* Приватні дані I/O планувальника: тип знає лише сам планувальник */
    void                   *sched_data;

    /* Вказівник на батьківську чергу пристрою request_queue */
    struct request_queue   *queue;

    /* Індекс цієї hctx у загальному масиві пристрою (від 0 до nr_hw_queues-1) */
    unsigned int            queue_num;

    /* Прапорці стану черги BLK_MQ_S_* (наприклад, BLK_MQ_S_STOPPED) */
    unsigned long           state;

    /* Відкладена робота kworker для фонової відправки запитів */
    struct delayed_work     run_work;
};
