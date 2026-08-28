struct nf_conn {
    struct nf_conntrack ct_general;
    spinlock_t lock;

    /* Двоповерховий масив для двох напрямків: ORIGINAL та REPLY */
    struct nf_conntrack_tuple_hash tuplehash[IP_CT_DIR_MAX];

    unsigned long status;      /* Бітові прапорці IPS_* */
    possible_net_t ct_net;     /* Посилання на мережевий namespace */

    struct timer_list timeout; /* Таймер видалення за застарілістю */

#if IS_ENABLED(CONFIG_NF_CONNTRACK_MARK)
    u32 mark;                  /* 32-бітний connmark */
#endif

    /* Вказівник на master-з'єднання (для RELATED потоків, наприклад FTP) */
    struct nf_conn *master;

    /* Динамічні розширення (NAT, helpers, timestamping, acct) */
    struct nf_ct_ext *ext;
};
