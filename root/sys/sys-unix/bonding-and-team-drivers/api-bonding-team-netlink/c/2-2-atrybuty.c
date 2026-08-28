enum {
    IFLA_BOND_SLAVE_UNSPEC,
    IFLA_BOND_SLAVE_STATE,          /* u8: стан slave (0=ACTIVE, 1=BACKUP) */
    IFLA_BOND_SLAVE_MII_STATUS,     /* u8: статус MII (0=LINK_UP, 1=LINK_FAIL) */
    IFLA_BOND_SLAVE_LINK_FAILURE_COUNT, /* u32: лічильник аварійних падінь лінка */
    IFLA_BOND_SLAVE_PERM_HWADDR,    /* 6 байт: оригінальна MAC-адреса карти */
    IFLA_BOND_SLAVE_QUEUE_ID,       /* u16: ідентифікатор черги передачі */
    IFLA_BOND_SLAVE_AD_AGGREGATOR_ID,/* u16: ідентифікатор агрегатора LACP */
    IFLA_BOND_SLAVE_AD_ACTOR_OPER_PORT_STATE, /* u8: стан автомата LACP Actor */
    IFLA_BOND_SLAVE_AD_PARTNER_OPER_PORT_STATE, /* u8: стан автомата LACP Partner */
    __IFLA_BOND_SLAVE_MAX
};
