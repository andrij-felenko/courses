struct xfrm_selector {
    xfrm_address_t daddr;       /* IP-адреса призначення */
    xfrm_address_t saddr;       /* IP-адреса джерела */
    __be16         dport;       /* Порт призначення у network byte order */
    __be16         dport_mask;  /* Бітова маска порту призначення */
    __be16         sport;       /* Порт джерела у network byte order */
    __be16         sport_mask;  /* Бітова маска порту джерела */
    __u16          family;      /* AF_INET / AF_INET6 */
    __u8           prefixlen_d; /* Довжина маски призначення (CIDR, наприклад 24) */
    __u8           prefixlen_s; /* Довжина маски джерела (CIDR, наприклад 24) */
    __u8           proto;       /* Протокол транспортного рівня (IPPROTO_TCP, UDP, ICMP або 0) */
    int            ifindex;     /* Індекс причіпленого мережевого інтерфейсу */
    __kernel_uid32_t user;      /* UID процесу-власника сокету */
};
