/* POSIX, є всюди — навіть у Winsock і lwIP */
struct ip_mreq {
    struct in_addr imr_multiaddr;   /* адреса групи */
    struct in_addr imr_interface;   /* АДРЕСА локального інтерфейсу */
};

/* Linux 2.2+, FreeBSD, macOS */
struct ip_mreqn {
    struct in_addr imr_multiaddr;   /* адреса групи */
    struct in_addr imr_address;     /* адреса інтерфейсу; можна 0.0.0.0 */
    int            imr_ifindex;     /* ІНДЕКС інтерфейсу — має перевагу */
};

/* фільтр за джерелом; Linux 2.4.22+, BSD, Windows */
struct ip_mreq_source {
    struct in_addr imr_multiaddr;   /* адреса групи */
    struct in_addr imr_interface;   /* адреса локального інтерфейсу */
    struct in_addr imr_sourceaddr;  /* дозволене (чи заглушене) джерело */
};
