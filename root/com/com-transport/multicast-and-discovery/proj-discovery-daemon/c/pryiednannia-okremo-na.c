static int join_all(int s, struct iface *out, int max)
{
    struct ifaddrs *list, *p;
    int n = 0;
    if (getifaddrs(&list) < 0) return -1;

    for (p = list; p && n < max; p = p->ifa_next) {
        if (!p->ifa_addr || p->ifa_addr->sa_family != AF_INET) continue;
        if (!(p->ifa_flags & IFF_UP))        continue;   /* інтерфейс опущено */
        if (!(p->ifa_flags & IFF_MULTICAST)) continue;   /* груп не вміє */
        if (p->ifa_flags & IFF_LOOPBACK)     continue;   /* сам із собою не говоримо */

        unsigned idx = if_nametoindex(p->ifa_name);
        if (idx == 0) continue;

        int seen = 0;                                    /* на інтерфейсі буває кілька адрес */
        for (int i = 0; i < n; i++) if (out[i].index == idx) seen = 1;
        if (seen) continue;

        struct ip_mreqn mreq;
        memset(&mreq, 0, sizeof mreq);
        inet_pton(AF_INET, DISC_GROUP, &mreq.imr_multiaddr);
        mreq.imr_ifindex = (int)idx;                     /* ОСЬ головний рядок */

        if (setsockopt(s, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof mreq) < 0
            && errno != EADDRINUSE) {                    /* EADDRINUSE = вже в групі */
            fprintf(stderr, "приєднання на %s: %s\n", p->ifa_name, strerror(errno));
            continue;                                    /* один не вдався — решта живе */
        }
        out[n].index = idx;
        snprintf(out[n].name, sizeof out[n].name, "%s", p->ifa_name);
        out[n].addr = ((struct sockaddr_in *)p->ifa_addr)->sin_addr;
        n++;
    }
    freeifaddrs(list);
    return n;
}
