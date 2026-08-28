struct virtq_used_elem {
    le32 id;   /* Індекс головного дескриптора обробленого ланцюжка */
    le32 len;  /* Кількість байтів, які реально були записані пристроєм */
};

struct virtq_used {
    le16 flags;
    le16 idx;                             /* Монотонний лічильник оброблених буферів */
    struct virtq_used_elem ring[QUEUE_SIZE];
    le16 avail_event;                     /* Поріг придушення Doorbells */
};
