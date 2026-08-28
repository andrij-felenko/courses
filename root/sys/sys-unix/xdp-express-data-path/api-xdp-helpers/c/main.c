struct xdp_buff {
    void *data;             /* Початок пакету */
    void *data_end;         /* Кінець пакету */
    void *data_meta;        /* Початок метаданих */
    void *data_hard_start;  /* Фізичний початок allocated сторінки пам'яті */
    struct xdp_rxq_info *rxq;/* Метадані про RX-чергу та драйвер */
    struct xdp_mem_info mem;/* Інформація про модель управління пам'яттю (PAGE_POOL) */
    enum xdp_mem_type type; /* Тип пам'яті (MEM_TYPE_PAGE_POOL, MEM_TYPE_PAGE_SHARED) */
    u32 flags;              /* Прапорці (наприклад, XDP_FLAGS_MB для multi-buffer) */
};
