struct blk_mq_ops {
    /* Обов'язковий метод: передача запиту безпосередньо у контролер пристрою */
    blk_status_t (*queue_rq)(struct blk_mq_hw_ctx *hctx,
                             const struct blk_mq_queue_data *bd);

    /* Необов'язковий метод: сповіщення про завершення пакетної відправки (batch) */
    void (*commit_rqs)(struct blk_mq_hw_ctx *hctx);

    /* Необов'язковий метод: обробка завершення запиту на вищому рівні */
    void (*complete)(struct request *rq);

    /* Метод обробки таймауту операції (коли пристрій не відповів вчасно) */
    enum blk_eh_timer_return (*timeout)(struct request *rq);

    /* Конструктор та деструктор апаратного контексту hctx */
    int (*init_hctx)(struct blk_mq_hw_ctx *hctx, void *data, unsigned int idx);
    void (*exit_hctx)(struct blk_mq_hw_ctx *hctx, unsigned int idx);

    /* Конструктор та деструктор приватних даних у структурі request */
    int (*init_request)(struct blk_mq_tag_set *set, struct request *rq,
                        unsigned int hctx_idx, unsigned int numa_node);
    void (*exit_request)(struct blk_mq_tag_set *set, struct request *rq,
                         unsigned int hctx_idx);

    /* Колбек для побудови топології мапінгу CPU -> hctx (нічого не повертає) */
    void (*map_queues)(struct blk_mq_tag_set *set);

    /* Метод опитування стану пристрою (для черг HCTX_TYPE_POLL) */
    int (*poll)(struct blk_mq_hw_ctx *hctx, struct io_comp_batch *iob);
};
