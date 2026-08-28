struct net_bridge {
    spinlock_t              lock;
    spinlock_t              hash_lock;
    struct list_head        port_list;          /* Список підключених портів */
    struct net_device       *dev;               /* Власний net_device моста */
    struct rhashtable       fdb_hash_tbl;       /* Таблиця комутації FDB */
    
    /* Параметри STP (Spanning Tree Protocol) */
    bridge_id               bridge_id;          /* Пріоритет + MAC-адреса */
    unsigned long           ageing_time;        /* Час застарівання FDB (jiffies) */
    u8                      stp_enabled;        /* 0=OFF, 1=KERNEL, 2=USER */
    
    /* Фільтрація VLAN */
    u8                      vlan_filtering;     /* Прапорець vlan_filtering (0 або 1) */
    u16                     default_pvid;       /* PVID за замовчуванням (зазвичай 1) */
    struct net_bridge_vlan_group __rcu *vlgrp;  /* База конфігурацій VLAN */
    
    /* Багатоадресна розсилка (Multicast Snooping) */
    struct net_bridge_mdb_htable __rcu *mdb;    /* База даних Multicast (MDB) */
    u8                      multicast_snooping; /* 1 = увімкнено IGMP snooping */
};
