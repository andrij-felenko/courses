enum nf_ip_hook_priorities {
    NF_IP_PRI_FIRST         = INT_MIN,
    NF_IP_PRI_RAW_BEFORE_DEFRAG = -400,
    NF_IP_PRI_CONNTRACK_DEFRAG  = -400,
    NF_IP_PRI_RAW           = -300, /* Таблиця raw */
    NF_IP_PRI_SELINUX_FIRST = -225,
    NF_IP_PRI_CONNTRACK     = -200, /* Модуль nf_conntrack (ініціалізація станів) */
    NF_IP_PRI_MANGLE        = -150, /* Таблиця mangle */
    NF_IP_PRI_NAT_DST       = -100, /* Destination NAT (PREROUTING / OUTPUT) */
    NF_IP_PRI_FILTER        = 0,    /* Таблиця filter (стандартні правила брандмауера) */
    NF_IP_PRI_SECURITY      = 50,   /* Таблиця security (SELinux / SMACK) */
    NF_IP_PRI_NAT_SRC       = 100,  /* Source NAT (POSTROUTING / INPUT) */
    NF_IP_PRI_SELINUX_LAST  = 225,
    NF_IP_PRI_CONNTRACK_HELPER = 300,
    NF_IP_PRI_CONNTRACK_CONFIRM = INT_MAX  /* Підтвердження запису з'єднання при ACCEPT */
};
