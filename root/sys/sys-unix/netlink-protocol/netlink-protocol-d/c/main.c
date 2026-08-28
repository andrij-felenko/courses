struct rtmsg {
    unsigned char rtm_family;   /* AF_INET або AF_INET6 */
    unsigned char rtm_dst_len;  /* Довжина маски призначення (CIDR) */
    unsigned char rtm_src_len;  /* Довжина маски джерела */
    unsigned char rtm_tos;      /* Тип обслуговування */
    unsigned char rtm_table;    /* Таблиця маршрутизації (RT_TABLE_MAIN, RT_TABLE_LOCAL) */
    unsigned char rtm_protocol; /* Джерело маршруту (RTPROT_STATIC, RTPROT_BOOT, RTPROT_BGP) */
    unsigned char rtm_scope;    /* Область видимості маршруту (RT_SCOPE_UNIVERSE, RT_SCOPE_LINK) */
    unsigned char rtm_type;     /* Тип (RTN_UNICAST, RTN_LOCAL, RTN_BROADCAST) */
    unsigned int  rtm_flags;    /* Прапорці RTM_F_* */
};
