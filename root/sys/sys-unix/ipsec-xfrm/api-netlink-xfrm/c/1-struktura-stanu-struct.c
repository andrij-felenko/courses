struct xfrm_usersa_info {
    struct xfrm_selector sel;           /* Селектор трафіку для прив'язки SA */
    struct xfrm_id       id;            /* Ідентифікатор SA: daddr, spi, proto */
    xfrm_address_t       saddr;         /* IP-адреса джерела тунелю */
    struct xfrm_lifetime_cfg lft;       /* Межі часу життя (байтів, пакетів, секунд) */
    struct xfrm_lifetime_cur curlft;    /* Поточна статистика використання */
    __u64                stats_packets; /* Лічильник успішно оброблених пакетів */
    __u64                stats_bytes;   /* Лічильник успішно оброблених байтів */
    __u32                seq;           /* Поточний серійний номер пакета */
    __u32                reqid;         /* Ідентифікатор запиту (зв'язок із політикам SPD) */
    __u16                family;        /* Родина адрес: AF_INET (IPv4) або AF_INET6 (IPv6) */
    __u8                 mode;          /* Режим: XFRM_MODE_TRANSPORT або XFRM_MODE_TUNNEL */
    __u8                 replay_window; /* Розмір вікна захисту від повторів (Anti-Replay) */
    __u8                 flags;         /* Бітові прапорці конфігурації стану */
};
