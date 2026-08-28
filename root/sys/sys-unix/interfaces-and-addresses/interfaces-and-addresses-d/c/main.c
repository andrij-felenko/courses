struct in_ifaddr {
    struct in_ifaddr   *ifa_next;      /* Вказівник на наступну адресу в списку */
    struct in_device   *ifa_dev;       /* Зворотний вказівник на пристрій */
    __be32             ifa_local;      /* Локальна IP-адреса хоста (Big-Endian) */
    __be32             ifa_address;    /* IP-адреса призначення (для P-t-P) */
    __be32             ifa_mask;       /* Маска підмережі у форматі Big-Endian */
    __be32             ifa_broadcast;  /* Wide-area широкомовна адреса */
    unsigned char      ifa_prefixlen;  /* Довжина CIDR-префікса (0..32) */
    unsigned char      ifa_flags;      /* Прапорці адреси (IFA_F_SECONDARY тощо) */
    unsigned char      ifa_scope;      /* Область видимості адреси */
    char               ifa_label[IFNAMSIZ]; /* Назва адреси чи псевдоніма */
};
