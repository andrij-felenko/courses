/* 1. Виділення та ініціалізація внутрішніх бітових карт sbitmap і масивів tags */
int blk_mq_alloc_tag_set(struct blk_mq_tag_set *set);

/* 2. Звільнення всіх виділених ресурсів та таблиць мапінгу */
void blk_mq_free_tag_set(struct blk_mq_tag_set *set);

/* 3. Створення та прив'язка черги request_queue на основі готового tag_set.
 *    Донедавна вона звалася blk_mq_init_queue(set); у сучасних ядрах приймає
 *    ще й обмеження пристрою та приватний вказівник драйвера. */
struct request_queue *blk_mq_alloc_queue(struct blk_mq_tag_set *set,
                                         struct queue_limits *lim,
                                         void *queuedata);

/* 4. Динамічна зміна кількості апаратних черг (наприклад, при зміні векторів MSI-X) */
void blk_mq_update_nr_hw_queues(struct blk_mq_tag_set *set, int nr_hw_queues);

/* 5. Зміна глибини СПІЛЬНОГО пулу тегів (для tag_set із BLK_MQ_F_TAG_QUEUE_SHARED) */
void blk_mq_tag_resize_shared_tags(struct blk_mq_tag_set *set, unsigned int size);

/* 6. Заморожування та розморожування черги при зміні конфігурації */
void blk_mq_freeze_queue(struct request_queue *q);
void blk_mq_unfreeze_queue(struct request_queue *q);

/* 7. Зупинка та відновлення диспетчеризації апаратних черг */
void blk_mq_stop_hw_queues(struct request_queue *q);
void blk_mq_start_hw_queues(struct request_queue *q);
