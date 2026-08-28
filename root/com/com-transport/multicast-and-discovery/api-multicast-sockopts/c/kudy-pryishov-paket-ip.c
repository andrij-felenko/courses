struct in_pktinfo {
    unsigned int   ipi_ifindex;    /* інтерфейс, на який прийшло */
    struct in_addr ipi_spec_dst;   /* локальна адреса маршруту */
    struct in_addr ipi_addr;       /* адреса призначення з заголовка — ГРУПА */
};

struct in6_pktinfo {
    struct in6_addr ipi6_addr;     /* адреса призначення */
    unsigned int    ipi6_ifindex;  /* інтерфейс */
};
