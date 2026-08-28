struct rtmsg {
    unsigned char rtm_family;   /* AF_INET або AF_INET6 */
    unsigned char rtm_dst_len;  /* Довжина маски призначення в бітах (CIDR) */
    unsigned char rtm_src_len;  /* Довжина маски джерела в бітах */
    unsigned char rtm_tos;      /* Тип обслуговування (Type of Service) */
    unsigned char rtm_table;    /* ID таблиці маршрутизації (RT_TABLE_MAIN, RT_TABLE_LOCAL, RT_TABLE_DEFAULT) */
    unsigned char rtm_protocol; /* Джерело маршруту (RTPROT_BOOT, RTPROT_STATIC, RTPROT_BGP, RTPROT_KERNEL) */
    unsigned char rtm_scope;    /* Область видимості маршруту (RT_SCOPE_UNIVERSE, RT_SCOPE_LINK, RT_SCOPE_NOWHERE) */
    unsigned char rtm_type;     /* Тип маршруту (RTN_UNICAST, RTN_LOCAL, RTN_BROADCAST, RTN_BLACKHOLE) */
    unsigned int  rtm_flags;    /* Прапорці маршрутизації RTM_F_* */
};
