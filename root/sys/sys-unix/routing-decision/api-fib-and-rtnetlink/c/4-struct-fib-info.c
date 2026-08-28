struct fib_info {
    struct hlist_node   fib_hash;
    struct hlist_node   fib_lhash;
    atomic_t            fib_treeref;  /* Лічильник посилань від дерев маршрутизації */
    atomic_t            fib_clntref;  /* Лічильник посилань від сокетів/клієнтів */
    u32                 fib_metrics;  /* Метрики (MTU, rtt, window) */
    u32                 fib_priority; /* Метрика/пріоритет (RTA_PRIORITY) */
    u32                 fib_prefsrc;  /* Preferred Source IP */
    u32                 fib_flags;    /* Прапорці (RTNH_F_DEAD тощо) */
    unsigned char       fib_protocol; /* Протокол джерела (RTPROT_BGP тощо) */
    unsigned char       fib_nhs;      /* Кількість nexthops (для ECMP) */
    struct fib_nh_common fib_nh[0];   /* Масив структур наступного хопу */
};
