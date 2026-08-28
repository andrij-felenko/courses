enum {
    IFLA_BOND_UNSPEC,
    IFLA_BOND_MODE,                /* u8: режим bonding (0-6) */
    IFLA_BOND_ACTIVE_SLAVE,         /* u32: ifindex активного slave пристрою */
    IFLA_BOND_MIIMON,               /* u32: інтервал MII моніторингу у мс */
    IFLA_BOND_UPDELAY,              /* u32: затримка увімкнення лінка у мс */
    IFLA_BOND_DOWNDELAY,            /* u32: затримка вимкнення лінка у мс */
    IFLA_BOND_USE_CARRIER,          /* u8: перевірка carrier netif (0/1) */
    IFLA_BOND_ARP_INTERVAL,         /* u32: інтервал відправки ARP у мс */
    IFLA_BOND_ARP_IP_TARGET,        /* вкладений контейнер IP-адрес targets */
    IFLA_BOND_ARP_VALIDATE,         /* u32: режим валідації вхідних ARP */
    IFLA_BOND_ARP_ALL_TARGETS,      /* u32: критерій доступності ARP цілей */
    IFLA_BOND_PRIMARY,              /* u32: ifindex первинного slave */
    IFLA_BOND_PRIMARY_RESELECT,     /* u8: режим переобрання primary */
    IFLA_BOND_FAIL_OVER_MAC,        /* u8: політика обробки MAC при failover */
    IFLA_BOND_XMIT_HASH_POLICY,     /* u8: політика хешування (0-4) */
    IFLA_BOND_RESEND_IGMP,          /* u32: кількість повторних IGMP пакетів */
    IFLA_BOND_NUM_PEER_NOTIF,       /* u8: кількість gratuitous ARP пакетів */
    IFLA_BOND_ALL_SLAVES_ACTIVE,    /* u8: обробка дубльованого трафіку */
    IFLA_BOND_MIN_LINKS,            /* u32: мін. кількість лінків для 802.3ad */
    IFLA_BOND_LP_INTERVAL,          /* u32: інтервал навчальних пакетів (tlb/alb) */
    IFLA_BOND_PACKETS_PER_SLAVE,    /* u32: кількість пакетів на slave (mode 0) */
    IFLA_BOND_AD_LACP_RATE,         /* u8: швидкість LACPDU (0=slow, 1=fast) */
    IFLA_BOND_AD_SELECT,            /* u8: режим вибору агрегатора LACP */
    IFLA_BOND_AD_INFO,              /* вкладений атрибут з деталями 802.3ad */
    IFLA_BOND_AD_ACTOR_SYS_PRIO,    /* u16: пріоритет Actor системи */
    IFLA_BOND_AD_USER_PORT_PRIO,    /* u16: пріоритет порту користувача */
    IFLA_BOND_AD_ACTOR_SYSTEM,      /* 6 байт: системна MAC-адреса Actor */
    IFLA_BOND_TLB_DYNAMIC_LB,       /* u8: динамічне балансування tlb (0/1) */
    __IFLA_BOND_MAX
};
