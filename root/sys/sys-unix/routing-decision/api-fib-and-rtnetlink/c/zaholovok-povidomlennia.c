#include <linux/rtnetlink.h>

struct rtmsg {
    unsigned char rtm_family;   /* Сімейство адрес: AF_INET (IPv4) або AF_INET6 (IPv6) */
    unsigned char rtm_dst_len;  /* Довжина маски префіксу призначення (0..32 для IPv4) */
    unsigned char rtm_src_len;  /* Довжина маски префіксу джерела (зазвичай 0) */
    unsigned char rtm_tos;      /* Type of Service (ToS) / DSCP */
    unsigned char rtm_table;    /* ID таблиці маршрутизації (RT_TABLE_MAIN, RT_TABLE_LOCAL тощо) */
    unsigned char rtm_protocol; /* Протокол, що створив маршрут (RTPROT_STATIC, BGP тощо) */
    unsigned char rtm_scope;    /* Область видимості маршруту (RT_SCOPE_UNIVERSE тощо) */
    unsigned char rtm_type;     /* Тип маршруту (RTN_UNICAST, RTN_LOCAL тощо) */
    unsigned unsigned rtm_flags;/* Допоміжні прапорці (RTM_F_CLONED, RTM_F_FIB_MATCH) */
};
