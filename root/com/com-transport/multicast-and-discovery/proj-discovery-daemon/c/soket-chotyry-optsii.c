static int open_socket(void)
{
    int s = socket(AF_INET, SOCK_DGRAM, 0);
    if (s < 0) return -1;

    int yes = 1;
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof yes);
#ifdef SO_REUSEPORT
    setsockopt(s, SOL_SOCKET, SO_REUSEPORT, &yes, sizeof yes);   /* BSD, macOS */
#endif
    setsockopt(s, IPPROTO_IP, IP_PKTINFO, &yes, sizeof yes);     /* хочемо знати ifindex */

    unsigned char ttl = 1;                    /* ставимо явно, хоч типове те саме */
    setsockopt(s, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof ttl);
    unsigned char loop = 1;                   /* луну НЕ вимикаємо, і це навмисно */
    setsockopt(s, IPPROTO_IP, IP_MULTICAST_LOOP, &loop, sizeof loop);

    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family      = AF_INET;
    a.sin_port        = htons(DISC_PORT);
    a.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(s, (struct sockaddr *)&a, sizeof a) < 0) { close(s); return -1; }
    return s;
}
