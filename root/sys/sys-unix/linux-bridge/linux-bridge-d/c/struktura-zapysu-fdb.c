struct net_bridge_fdb_entry {
    struct rhash_head       rhlist;
    struct net_bridge_port  *dst;           /* Порт виходу */
    struct net_bridge_fdb_key key;          /* Ключ: { MAC-адреса, VLAN ID } */
    struct rcu_head         rcu;
    unsigned long           updated;        /* Час останньої активності (jiffies) */
    unsigned long           used;
    u16                     flags;          /* BR_FDB_LOCAL, BR_FDB_STATIC */
    u8                      is_local:1,     /* 1 = MAC належить самому хосту */
                            is_static:1,    /* 1 = статично заданий адміністратором */
                            is_dynamic:1,   /* 1 = вивчений автоматично */
                            added_by_user:1;
};
