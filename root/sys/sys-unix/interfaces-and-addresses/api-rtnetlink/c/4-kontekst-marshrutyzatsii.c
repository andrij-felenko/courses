struct rtmsg {
    unsigned char rtm_family;   /* AF_INET або AF_INET6 */
    unsigned char rtm_dst_len;  /* Довжина маски призначення (CIDR, наприклад 24) */
    unsigned char rtm_src_len;  /* Довжина маски джерела (для Source-Based Routing) */
    unsigned char rtm_tos;      /* Тип обслуговування (Type of Service) */
    unsigned char rtm_table;    /* Ідентифікатор таблиці (RT_TABLE_MAIN, RT_TABLE_LOCAL) */
    unsigned char rtm_protocol; /* Походження маршруту (RTPROT_BOOT, RTPROT_STATIC, RTPROT_BGP) */
    unsigned char rtm_scope;    /* Область видимості (RT_SCOPE_UNIVERSE, RT_SCOPE_LINK) */
    unsigned char rtm_type;     /* Тип маршруту (RTN_UNICAST, RTN_LOCAL, RTN_BLACKHOLE) */
    unsigned int  rtm_flags;    /* Прапорці маршруту (RTM_F_CLONED, RTM_F_PREFIX) */
};
