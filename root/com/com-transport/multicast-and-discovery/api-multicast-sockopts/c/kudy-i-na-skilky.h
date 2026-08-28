/* один намір — три різні типи аргументу */
#if defined(_WIN32)
    DWORD ttl = 4, loop = 1;
#elif defined(__linux__)
    int ttl = 4, loop = 1;
#else
    unsigned char ttl = 4, loop = 1;   /* історична форма BSD */
#endif
setsockopt(fd, IPPROTO_IP, IP_MULTICAST_TTL,  (const char *)&ttl,  sizeof ttl);
setsockopt(fd, IPPROTO_IP, IP_MULTICAST_LOOP, (const char *)&loop, sizeof loop);
