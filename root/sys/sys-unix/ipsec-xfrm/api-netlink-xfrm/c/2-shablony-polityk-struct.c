struct xfrm_user_tmpl {
    struct xfrm_id id;        /* Dst IP, SPI та протокол (IPPROTO_ESP/AH) */
    __u16          family;    /* AF_INET / AF_INET6 */
    xfrm_address_t saddr;     /* IP-адреса джерела тунелю */
    __u32          reqid;     /* reqid для зв'язування з SA */
    __u8           mode;      /* XFRM_MODE_TRANSPORT або XFRM_MODE_TUNNEL */
    __u8           share;     /* Спосіб поділу (XFRM_SHARE_ANY) */
    __u8           optional;  /* 0 = суворе використання IPsec, 1 = необов'язкове */
    __u32          aalgos;    /* Бітова маска дозволених алгоритмів аутентифікації */
    __u32          ealgos;    /* Бітова маска дозволених шифрів */
    __u32          calgos;    /* Бітова маска алгоритмів компресії */
};
