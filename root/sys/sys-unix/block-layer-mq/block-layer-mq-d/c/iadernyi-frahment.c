/* Фрагмент реєстрації драйвера блокового пристрою blk-mq у ядрі Linux */
#include <linux/module.h>
#include <linux/blk-mq.h>

static blk_status_t my_queue_rq(struct blk_mq_hw_ctx *hctx,
                                const struct blk_mq_queue_data *bd)
{
    struct request *rq = bd->rq;
    
    /* Отримання тегу, виділеного під даний запит */
    unsigned int tag = rq->tag;
    
    /* Драйвер починає обробку запиту на hardware hctx */
    blk_mq_start_request(rq);
    
    /* ... Програмування регістрів контролера або DMA ... */
    
    /* Завершення запиту у разі успіху */
    blk_mq_end_request(rq, BLK_STS_OK);
    return BLK_STS_OK;
}

static struct blk_mq_ops my_mq_ops = {
    .queue_rq = my_queue_rq,
};

/* Ініціалізація набору тегів при завантаженні драйвера */
static int init_my_tag_set(struct blk_mq_tag_set *tag_set)
{
    tag_set->ops = &my_mq_ops;
    tag_set->nr_hw_queues = num_online_cpus(); /* 1:1 mapping */
    tag_set->queue_depth = 128;                /* Глибина апаратної черги */
    tag_set->numa_node = NUMA_NO_NODE;
    tag_set->flags = BLK_MQ_F_SHOULD_MERGE;
    
    return blk_mq_alloc_tag_set(tag_set);
}
