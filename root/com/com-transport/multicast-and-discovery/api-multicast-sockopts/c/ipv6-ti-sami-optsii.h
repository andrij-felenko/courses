struct ipv6_mreq {
    struct in6_addr ipv6mr_multiaddr;   /* адреса групи */
    unsigned int    ipv6mr_interface;   /* ІНДЕКС; 0 = ядро обере само */
};

struct ipv6_mreq m6;
memset(&m6, 0, sizeof m6);
inet_pton(AF_INET6, "ff02::fb", &m6.ipv6mr_multiaddr);   /* mDNS в IPv6 */
m6.ipv6mr_interface = if_nametoindex("eth0");
setsockopt(fd6, IPPROTO_IPV6, IPV6_JOIN_GROUP, &m6, sizeof m6);
