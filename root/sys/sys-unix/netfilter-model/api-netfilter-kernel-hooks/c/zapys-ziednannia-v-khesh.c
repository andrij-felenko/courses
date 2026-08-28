enum ip_conntrack_dir {
    IP_CT_DIR_ORIGINAL = 0,        /* Напрямок від ініціатора (прямий потік) */
    IP_CT_DIR_REPLY    = 1,        /* Напрямок відповіді (зворотний потік) */
    IP_CT_DIR_MAX
};

struct nf_conntrack_tuple_hash {
    struct hlist_nulls_node   hnnode; /* Вузол зв'язаного списку хеш-кошика */
    struct nf_conntrack_tuple tuple;  /* Кортеж для даного напрямку */
};

struct nf_conn {
    struct sk_buff_head       head;
    possible_net_t            ct_net;
    
    /* Двостороння пара кортежів: [0] = ORIGINAL, [1] = REPLY */
    struct nf_conntrack_tuple_hash tuplehash[IP_CT_DIR_MAX];
    
    unsigned long             status; /* Бітова маска станів (IPS_CONFIRMED, IPS_NAT_MASK тощо) */
    typedef atomic_t          refcnt;
    struct timer_list         timeout;/* Таймер застарівання з'єднання */
    
    /* Бітові прапорці станів з'єднання */
    u_int32_t                 mark;   /* Маркер пакета (ct mark) */
    u_int32_t                 secmark;/* Сек'юріті-мітка SELinux */
    
    /* Розширення: помічники (helpers), NAT-структури, аккаунтинг */
    struct nf_ct_ext          *ext;
};
