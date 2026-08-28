/* Опитування за іменем хоста та сімейством адрес (IPv4/IPv6) */
enum nss_status _nss_<module>_gethostbyname2_r(
    const char *name,
    int af,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop
);

/* Зворотне опитування за двійковою IP-адресою (Reverse DNS) */
enum nss_status _nss_<module>_gethostbyaddr_r(
    const char *addr,
    int len,
    int type,
    struct hostent *result,
    char *buffer,
    size_t buflen,
    int *errnop,
    int *h_errnop
);
