union nf_inet_addr {
    __be32          ip;
    __be32          ip6[4];
    struct in_addr  in;
    struct in6_addr in6;
};

struct nf_conntrack_man {
    union nf_inet_addr u3;         /* IP-адреса хоста */
    union {
        __be16      all;           /* Універсальний порт / ID */
        __be16      tcp_offset;
        __be16      udp_offset;
        __be16      icmp_id;
    } u;
    u_int16_t       l3num;         /* AF_INET або AF_INET6 */
};

struct nf_conntrack_tuple {
    struct nf_conntrack_man src;  /* Джерело (IP + порт/ID) */
    struct {
        union nf_inet_addr u3;     /* Призначення (IP + порт/ID) */
        union {
            __be16  all;
            __be16  tcp_offset;
            __be16  udp_offset;
            u_int8_t type;         /* Тип ICMP */
            u_int8_t code;         /* Код ICMP */
        } u;
        u_int8_t    protonum;      /* Номер L4-протоколу (IPPROTO_TCP, IPPROTO_UDP тощо) */
        u_int8_t    dir;           /* Напрямок: IP_CT_DIR_ORIGINAL або IP_CT_DIR_REPLY */
    } dst;
};
